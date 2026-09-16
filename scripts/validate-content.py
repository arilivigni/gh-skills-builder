#!/usr/bin/env python3
"""Validate plugin content consistency.

Deterministic, offline checks that protect the conventions this plugin teaches.
Run locally with:

    python3 scripts/validate-content.py

Use --online to additionally verify that the pinned exercise-toolkit tag
resolves on GitHub. That check needs network access and is run in the pull
request gate, where it only fails on a definitive 404; other network errors
warn instead, so it does not make CI flaky.
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


def _walk(node):
    """Yield every mapping in a parsed YAML document."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def collect_toolkit_refs() -> dict[str, set[str]]:
    """Collect every exercise-toolkit ref, in both the `uses:` and the toolkit
    `actions/checkout` `ref:` form.

    Parsing the YAML rather than grepping matters here: `0-start-exercise.yml`
    contains `ref: main` for a checkout of the *exercise* repository, which a
    naive `ref:` grep would wrongly report as an unpinned toolkit ref.
    """
    try:
        import yaml
    except ImportError:
        return {}

    refs: dict[str, set[str]] = {}

    def record(ref: str, where: str) -> None:
        refs.setdefault(ref, set()).add(where)

    for path in markdown_files():
        rel = str(path.relative_to(ROOT))
        text = read(path)

        for match in re.finditer(r"^([ ]*)```yaml\n(.*?)^\1```$", text, flags=re.DOTALL | re.MULTILINE):
            try:
                document = yaml.safe_load(textwrap.dedent(match.group(2)))
            except Exception:  # noqa: BLE001 - reported by check_yaml_blocks
                continue

            for mapping in _walk(document):
                uses = mapping.get("uses")
                if isinstance(uses, str) and uses.startswith("skills/exercise-toolkit") and "@" in uses:
                    record(uses.rsplit("@", 1)[1], rel)

                if mapping.get("repository") == "skills/exercise-toolkit" and "ref" in mapping:
                    record(str(mapping["ref"]), rel)

        # Refs mentioned in prose, outside any YAML block. Placeholders such as
        # `@<ref>` are documentation, not real pins.
        for ref in re.findall(r"exercise-toolkit[^\s`\"']*@([^\s`\"')]+)", text):
            if "<" in ref or ">" in ref or ref in {"ref", "tag"}:
                continue
            record(ref, rel)

    return refs


def check_toolkit_refs() -> str | None:
    """The contract tells authors never to mix toolkit refs and never to use
    `@main`. The contract itself must obey both rules, and the check must be
    able to see a non-semver ref in order to reject it."""
    refs = collect_toolkit_refs()
    if not refs:
        fail("toolkit-ref", "no exercise-toolkit references found")
        return None

    tag_pattern = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")

    non_tags = {ref: where for ref, where in refs.items() if not tag_pattern.fullmatch(ref)}
    for ref, where in sorted(non_tags.items()):
        fail("toolkit-ref", f"exercise-toolkit ref '{ref}' is not a release tag (in {', '.join(sorted(where))})")

    tags = {ref for ref in refs if tag_pattern.fullmatch(ref)}
    if len(tags) > 1:
        fail("toolkit-ref", f"mixed exercise-toolkit refs: {sorted(tags)}")
        return None

    if non_tags:
        return None

    return next(iter(tags)) if tags else None


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

    # The skeleton must satisfy the rule it teaches: a Theory heading with real
    # content beneath it, and an Activity with numbered instructions.
    theory = re.search(r"### 📖 Theory:[^\n]*\n(.*?)(?=^#{1,3} )", skeleton, flags=re.DOTALL | re.MULTILINE)
    if theory is None or not [line for line in theory.group(1).splitlines() if line.strip()]:
        fail("contract", "step skeleton's Theory block has no content")

    activity = re.search(r"### ⌨️ Activity:[^\n]*\n(.*?)(?=^#{1,3} |\Z)", skeleton, flags=re.DOTALL | re.MULTILINE)
    if activity is None or not re.search(r"^\s*\d+\.\s+\S", activity.group(1), flags=re.MULTILINE):
        fail("contract", "step skeleton's Activity block has no numbered instructions")

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
    ref = check_toolkit_refs()
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
