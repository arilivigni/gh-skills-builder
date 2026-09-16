#!/usr/bin/env python3
"""Validate plugin content consistency.

Deterministic, offline checks that protect the conventions this plugin teaches.
Run locally with:

    python3 scripts/validate-content.py

Use --online to additionally verify that the pinned exercise-toolkit tag
resolves on GitHub. That check needs network access and is not run in the
pull request gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CANONICAL_BADGES = {
    "chat-prompt": "https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple",
    "cli-prompt": "https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff",
    "terminal": "https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff",
}

CONTRACT = Path("skills/bootstrap-github-skills-exercise/references/exercise-template-contract.md")

failures: list[str] = []


def fail(check: str, message: str) -> None:
    failures.append(f"[{check}] {message}")


def markdown_files() -> list[Path]:
    return sorted(
        p
        for p in ROOT.glob("**/*.md")
        if ".git/" not in str(p.relative_to(ROOT)) and "node_modules" not in str(p)
    )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str | None:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.DOTALL)
    return match.group(1) if match else None


def frontmatter_keys(block: str) -> dict[str, str]:
    values = {}
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def check_agents() -> None:
    """Agent files are referenced only as a directory by plugin.json, so nothing
    else validates their frontmatter. A malformed agent name has broken this
    plugin before."""
    agents = sorted(ROOT.glob("agents/*.agent.md"))
    if not agents:
        fail("agents", "no agent files found in agents/")
        return

    for path in agents:
        rel = path.relative_to(ROOT)
        block = frontmatter(read(path))
        if block is None:
            fail("agents", f"{rel}: missing frontmatter block")
            continue

        keys = frontmatter_keys(block)
        for required in ("name", "description"):
            if required not in keys:
                fail("agents", f"{rel}: missing required frontmatter field '{required}'")

        name = keys.get("name")
        if name is None:
            continue

        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            fail("agents", f"{rel}: agent name '{name}' must be lowercase kebab-case")

        expected = path.name[: -len(".agent.md")]
        if name != expected:
            fail("agents", f"{rel}: agent name '{name}' does not match filename stem '{expected}'")


def check_skill_registration() -> None:
    """plugin.json referencing a missing skill is already covered by CI. The
    reverse -- adding a skill and forgetting the manifest -- is not."""
    manifest = json.loads(read(ROOT / ".github/plugin/plugin.json"))
    registered = {Path(entry).name for entry in manifest.get("skills", [])}
    on_disk = {p.parent.name for p in ROOT.glob("skills/*/SKILL.md")}

    for name in sorted(on_disk - registered):
        fail("skills", f"skills/{name} has a SKILL.md but is not registered in plugin.json")


def check_fence_balance() -> None:
    """An unbalanced code fence silently swallows the rest of a document."""
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        depth = 0
        opened_at = 0
        opener = 0
        for number, line in enumerate(read(path).splitlines(), 1):
            match = re.match(r"^ {0,3}(`{3,})(.*)$", line)
            if not match:
                continue
            ticks, info = len(match.group(1)), match.group(2).strip()
            if depth == 0:
                depth, opened_at, opener = 1, number, ticks
            elif not info and ticks >= opener:
                depth = 0
        if depth != 0:
            fail("fences", f"{rel}: unclosed code fence opened at line {opened_at}")


def check_yaml_blocks() -> None:
    """Workflow skeletons get copy-pasted into real exercises, so a skeleton
    that does not parse ships a broken exercise."""
    try:
        import yaml
    except ImportError:
        fail("yaml", "PyYAML is not installed; cannot validate YAML snippets")
        return

    total = 0
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        text = read(path)
        for match in re.finditer(r"^([ ]*)```yaml\n(.*?)^\1```$", text, flags=re.DOTALL | re.MULTILINE):
            total += 1
            line = text[: match.start()].count("\n") + 1
            try:
                yaml.safe_load(textwrap.dedent(match.group(2)))
            except Exception as error:  # noqa: BLE001 - surface any parse problem
                fail("yaml", f"{rel}:{line}: YAML block does not parse: {error}")

    if total == 0:
        fail("yaml", "no YAML blocks found; the contract reference should contain workflow skeletons")


def check_toolkit_refs() -> tuple[str | None, set[str]]:
    """The contract tells authors never to mix toolkit refs. The contract itself
    must not mix them either."""
    refs: set[str] = set()
    for path in markdown_files():
        text = read(path)
        refs |= set(re.findall(r"exercise-toolkit[^\s`\"']*@(v[0-9]+\.[0-9]+\.[0-9]+)", text))
        refs |= set(re.findall(r"^\s*ref:\s*(v[0-9]+\.[0-9]+\.[0-9]+)", text, flags=re.MULTILINE))

    # v0.9.1 is referenced once as prose describing what skills/exercise-template
    # itself pins. Only pinned refs in skeletons must agree.
    pinned = {r for r in refs if r != "v0.9.1"} or refs

    if len(pinned) > 1:
        fail("toolkit-ref", f"mixed exercise-toolkit refs in documentation: {sorted(pinned)}")
        return None, pinned

    return (next(iter(pinned)) if pinned else None), pinned


def check_contract_self_consistency() -> None:
    """The contract imposes a Theory + Activity rule. Its own step skeleton must
    satisfy that rule, or the plugin contradicts itself."""
    path = ROOT / CONTRACT
    if not path.exists():
        fail("contract", f"{CONTRACT} is missing")
        return

    text = read(path)
    match = re.search(r"## Step skeleton.*?^```markdown\n(.*?)^```$", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        fail("contract", "step skeleton block not found in the contract reference")
        return

    skeleton = match.group(1)
    if skeleton.count("### 📖 Theory:") != 1:
        fail("contract", "step skeleton must contain exactly one '### 📖 Theory:' heading")
    if "### ⌨️ Activity:" not in skeleton:
        fail("contract", "step skeleton must contain a '### ⌨️ Activity:' heading")
    if "Having trouble" not in skeleton:
        fail("contract", "step skeleton must contain a 'Having trouble' recovery block")

    for section in ("## Activity block conventions", "## Workflow chaining rules", "## Permissions matrix"):
        if section not in text:
            fail("contract", f"contract reference is missing section '{section}'")


def check_badges() -> None:
    """Badge drift means exercises stop looking consistent, which is the whole
    point of standardizing them."""
    seen: set[str] = set()
    known = set(CANONICAL_BADGES.values())

    for path in markdown_files():
        rel = path.relative_to(ROOT)
        for url in re.findall(r"https://img\.shields\.io/badge/[^)\s`]+", read(path)):
            if "Copy%20Exercise" in url:
                continue
            if url in known:
                seen.add(url)
            else:
                fail("badges", f"{rel}: non-canonical shields.io badge: {url}")

    for kind, url in CANONICAL_BADGES.items():
        if url not in seen:
            fail("badges", f"canonical '{kind}' badge is not documented anywhere")


def check_toolkit_tag_online(ref: str | None) -> None:
    """A draft release appears in the releases API but has no git tag, so
    pinning it breaks every generated workflow."""
    if ref is None:
        fail("toolkit-tag", "no toolkit ref found to verify")
        return

    import urllib.error
    import urllib.request

    url = f"https://api.github.com/repos/skills/exercise-toolkit/git/ref/tags/{ref}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:  # noqa: S310 - fixed https host
            json.load(response)
        print(f"  toolkit tag {ref} resolves")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            fail("toolkit-tag", f"pinned toolkit ref {ref} has no git tag (draft release?)")
        else:
            print(f"  warning: could not verify {ref}: HTTP {error.code}")
    except Exception as error:  # noqa: BLE001 - network issues should not fail the gate
        print(f"  warning: could not verify {ref}: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true", help="also verify the pinned toolkit tag resolves")
    args = parser.parse_args()

    check_agents()
    check_skill_registration()
    check_fence_balance()
    check_yaml_blocks()
    ref, _ = check_toolkit_refs()
    check_contract_self_consistency()
    check_badges()

    if args.online:
        check_toolkit_tag_online(ref)

    if failures:
        print("Content validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Content validation passed (toolkit ref: {ref}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
