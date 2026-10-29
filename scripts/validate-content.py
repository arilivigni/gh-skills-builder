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
AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_DIRECTORY = Path("com.github.copilot/agents")

CANONICAL_BADGES = {
    "chat-prompt": "https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple",
    "cli-prompt": "https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff",
    "terminal": "https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff",
}

# Each badge introduces a blockquote whose fence language is fixed.
BADGE_FENCES = {
    CANONICAL_BADGES["chat-prompt"]: "prompt",
    CANONICAL_BADGES["cli-prompt"]: "prompt",
    CANONICAL_BADGES["terminal"]: "bash",
}

COPY_EXERCISE_IMAGE = "https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935"

MONA_LINE = "1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson."

CONTRACT = Path("skills/github-skills-bootstrap/references/exercise-template-contract.md")

# Skill names before 3.0, mapped to their replacements.
RENAMED_SKILLS = {
    "orchestrate-github-skills-exercise": "github-skills-orchestrate",
    "create-github-skills-outline": "github-skills-outline",
    "bootstrap-github-skills-exercise": "github-skills-bootstrap",
    "review-github-skills-exercise": "github-skills-review",
    "publish-github-skills-exercise": "github-skills-publish",
}

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


def contained_component(path: Path, check: str) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except (ValueError, OSError, RuntimeError) as error:
        fail(check, f"{path.relative_to(ROOT)}: path must resolve within the plugin root ({error})")
        return False
    return True


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


def check_manifest() -> None:
    """Validate the closed Agent Plugins v1.0.0 manifest without network access."""
    for legacy in (".github/plugin/plugin.json", ".plugin/plugin.json", ".claude-plugin/plugin.json"):
        if (ROOT / legacy).exists():
            fail("manifest", f"remove legacy manifest {legacy}; use root plugin.json")
    if not contained_component(ROOT / "plugin.json", "manifest"):
        return
    try:
        manifest = json.loads(read(ROOT / "plugin.json"))
    except (OSError, ValueError) as error:
        fail("manifest", f"cannot read root plugin.json: {error}")
        return
    if not isinstance(manifest, dict):
        fail("manifest", "plugin.json must contain an object")
        return

    allowed = {
        "$schema", "name", "version", "description", "author", "homepage",
        "repository", "license", "keywords", "extensions",
    }
    for key in sorted(manifest.keys() - allowed):
        fail("manifest", f"unknown top-level field '{key}'")
    if manifest.get("$schema") != AGENT_PLUGIN_SCHEMA:
        fail("manifest", f"$schema must be {AGENT_PLUGIN_SCHEMA}")
    name = manifest.get("name")
    if (not isinstance(name, str) or not 1 <= len(name) <= 64
            or not re.fullmatch(r"(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", name)):
        fail("manifest", "name must follow Agent Plugins naming constraints")
    for key in ("version", "description", "homepage", "repository", "license"):
        if key in manifest and not isinstance(manifest[key], str):
            fail("manifest", f"{key} must be a string")
    for key in ("version", "description"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            fail("manifest", f"{key} must be non-empty for the marketplace listing")
    if "author" in manifest:
        author = manifest["author"]
        if (not isinstance(author, dict) or set(author) - {"name", "email", "url"}
                or any(not isinstance(value, str) for value in author.values())):
            fail("manifest", "author may contain only name, email and url strings")
    if "keywords" in manifest:
        keywords = manifest["keywords"]
        if not isinstance(keywords, list) or any(not isinstance(value, str) for value in keywords):
            fail("manifest", "keywords must be an array of strings")
    if "extensions" in manifest:
        extensions = manifest["extensions"]
        if not isinstance(extensions, dict) or any(not isinstance(value, dict) for value in extensions.values()):
            fail("manifest", "extensions must map client namespaces to objects")


def check_agents() -> None:
    """Validate Copilot-specific agent discovery and frontmatter."""
    if not contained_component(ROOT / AGENT_DIRECTORY, "agents"):
        return
    agents = sorted((ROOT / AGENT_DIRECTORY).glob("*.agent.md"))
    if not agents:
        fail("agents", f"no agent files found in {AGENT_DIRECTORY}/")
        return

    for path in agents:
        rel = path.relative_to(ROOT)
        if not contained_component(path, "agents"):
            continue
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


def check_skill_discovery() -> None:
    """Skills are discovered from immediate children of skills/, not a manifest list."""
    if not contained_component(ROOT / "skills", "skills"):
        return
    if not (ROOT / "skills").is_dir():
        fail("skills", "missing skills/ directory")
        return
    for directory in sorted((ROOT / "skills").iterdir()):
        if not directory.is_dir():
            continue
        path = directory / "SKILL.md"
        if not contained_component(directory, "skills") or not contained_component(path, "skills"):
            continue
        if not path.is_file():
            fail("skills", f"{directory.relative_to(ROOT)}: missing SKILL.md")
            continue
        block = frontmatter(read(path))
        if block is None:
            fail("skills", f"{path.relative_to(ROOT)}: missing frontmatter block")
            continue
        keys = frontmatter_keys(block)
        for required in ("name", "description"):
            if not keys.get(required):
                fail("skills", f"{path.relative_to(ROOT)}: missing required field '{required}'")
        if keys.get("name") != directory.name:
            fail("skills", f"{path.relative_to(ROOT)}: name must match skill directory")


def check_lifecycle_topology() -> None:
    expected_agent = AGENT_DIRECTORY / "github-skills-orchestrator.agent.md"
    agents = {p.relative_to(ROOT) for p in (ROOT / AGENT_DIRECTORY).glob("*.agent.md")}
    if agents != {expected_agent}:
        fail("lifecycle", f"expected only {expected_agent}; found {sorted(str(p) for p in agents)}")
    if (ROOT / "agents").exists():
        fail("lifecycle", f"legacy agents/ is not discovered; use {AGENT_DIRECTORY}/")

    expected_skills = {
        "github-skills-orchestrate",
        "github-skills-outline",
        "github-skills-bootstrap",
        "github-skills-review",
        "github-skills-publish",
    }
    on_disk = {p.parent.name for p in ROOT.glob("skills/*/SKILL.md")}
    if on_disk != expected_skills:
        fail("lifecycle", "expected exactly the five lifecycle skills under skills/")

    paths = markdown_files() + [ROOT / "evals/evals.json"]
    agent_reference = re.compile(
        r"@github-skills-[a-z0-9]+(?:-[a-z0-9]+)*"
        r"|\bgithub-skills-(?:outline-architect|exercise-builder|quality-reviewer|publisher)\b"
    )
    for path in paths:
        for name in agent_reference.findall(read(path)):
            if name != "@github-skills-orchestrator":
                fail("lifecycle", f"{path.relative_to(ROOT)}: obsolete specialist-agent reference {name}")

    # A line may name a pre-3.0 skill only alongside its replacement, as in a migration table row.
    for path in paths:
        for lineno, line in enumerate(read(path).splitlines(), start=1):
            for old, new in RENAMED_SKILLS.items():
                if re.search(rf"\b{old}\b", line) and not re.search(rf"(?<![\w-]){new}(?![\w-])", line):
                    fail(
                        "lifecycle",
                        f"{path.relative_to(ROOT)}:{lineno}: obsolete skill name {old}; use {new}",
                    )


def check_fence_balance() -> None:
    """An unbalanced code fence silently swallows the rest of a document.

    Fences inside blockquotes count too: this repository documents workflow
    skeletons and activity blocks as `> ```yaml` inside blockquotes, and an
    unclosed one there breaks rendering exactly the same way.
    """
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        depth = 0
        opened_at = 0
        opener = 0
        opened_quoted = False
        for number, raw in enumerate(read(path).splitlines(), 1):
            # Normalize any blockquote prefix ("> ", ">> ", ">") before matching.
            stripped = re.sub(r"^(\s*>)+\s?", "", raw)
            quoted = stripped != raw
            match = re.match(r"^ {0,3}(`{3,})(.*)$", stripped)
            if not match:
                continue
            ticks, info = len(match.group(1)), match.group(2).strip()
            if depth == 0:
                depth, opened_at, opener, opened_quoted = 1, number, ticks, quoted
            elif not info and ticks >= opener and quoted == opened_quoted:
                # Only a fence at the same quote depth can close the opener.
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
                if isinstance(uses, str) and uses.startswith("skills/exercise-toolkit"):
                    # A `uses:` with no `@ref` follows the toolkit default
                    # branch, exactly like an unpinned checkout.
                    ref = uses.rsplit("@", 1)[1].strip() if "@" in uses else ""
                    record(ref or "(unpinned)", rel)

                if mapping.get("repository") == "skills/exercise-toolkit":
                    # A checkout with no `ref` follows the toolkit's default
                    # branch, which is the `@main` problem by another name.
                    ref = mapping.get("ref")
                    record(str(ref).strip() if ref is not None and str(ref).strip() else "(unpinned)", rel)

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


def _markdown_block(text: str, heading: str) -> str | None:
    """Return the first ```markdown block that follows `heading`."""
    match = re.search(re.escape(heading) + r".*?^```markdown\n(.*?)^```$", text, flags=re.DOTALL | re.MULTILINE)
    return match.group(1) if match else None


def _check_step_skeleton(name: str, skeleton: str, numbered: bool) -> None:
    """A step skeleton must obey the step anatomy the contract imposes: one
    Theory with content, then either one unnumbered activity or activities
    numbered from 1, each with lazy `1.` instructions and its own recovery
    block, and only the final activity ending with the Mona instruction."""
    if skeleton.count("### 📖 Theory:") != 1:
        fail("contract", f"{name} must contain exactly one '### 📖 Theory:' heading")

    theory = re.search(r"### 📖 Theory:[^\n]*\n(.*?)(?=^#{1,3} )", skeleton, flags=re.DOTALL | re.MULTILINE)
    if theory is None or not [line for line in theory.group(1).splitlines() if line.strip()]:
        fail("contract", f"{name}'s Theory block has no content")

    parts = re.split(r"^(### ⌨️ Activity[^\n]*)\n", skeleton, flags=re.MULTILINE)
    activities = list(zip(parts[1::2], parts[2::2]))
    if numbered:
        expected = [f"### ⌨️ Activity {index}:" for index in range(1, len(activities) + 1)]
        if len(activities) < 2 or any(not heading.startswith(want) for (heading, _), want in zip(activities, expected)):
            fail("contract", f"{name} must number two or more activities from '### ⌨️ Activity 1:' with no gaps")
    elif len(activities) != 1 or not activities[0][0].startswith("### ⌨️ Activity:"):
        fail("contract", f"{name} must contain exactly one '### ⌨️ Activity:' heading")

    for index, (heading, body) in enumerate(activities, 1):
        if not re.search(r"^1\.\s+\S", body, flags=re.MULTILINE):
            fail("contract", f"{name}: '{heading}' has no numbered instructions")
        if re.search(r"^(?:[2-9]|\d{2,})\.\s", body, flags=re.MULTILINE):
            fail("contract", f"{name}: '{heading}' must number every instruction '1.'")
        if "<summary>Having trouble? 🤷</summary>" not in body:
            fail("contract", f"{name}: '{heading}' has no 'Having trouble? 🤷' block")
        last = index == len(activities)
        if last and MONA_LINE not in body:
            fail("contract", f"{name}: the final activity must end with '{MONA_LINE}'")
        if not last and MONA_LINE in body:
            fail("contract", f"{name}: only the final activity ends with the Mona instruction")


def check_contract_self_consistency() -> None:
    """The contract imposes step, README, and workflow rules. Its own skeletons
    must satisfy those rules, or the plugin contradicts itself."""
    path = ROOT / CONTRACT
    if not path.exists():
        fail("contract", f"{CONTRACT} is missing")
        return

    text = read(path)
    single = _markdown_block(text, "## Step skeleton")
    if single is None:
        fail("contract", "step skeleton block not found in the contract reference")
    else:
        _check_step_skeleton("step skeleton", single, numbered=False)

    several = _markdown_block(text, "### Step with several activities")
    if several is None:
        fail("contract", "multi-activity step skeleton block not found in the contract reference")
    else:
        _check_step_skeleton("multi-activity step skeleton", several, numbered=True)

    readme = _markdown_block(text, "## README skeleton")
    if readme is None:
        fail("contract", "README skeleton block not found in the contract reference")
    else:
        start = readme.find("### How to start this exercise")
        if readme.count(COPY_EXERCISE_IMAGE) != 1 or start < 0 or readme.find(COPY_EXERCISE_IMAGE) < start:
            fail("contract", "README skeleton must have exactly one canonical Copy Exercise badge under '### How to start this exercise'")
        lines = [line.strip() for line in readme.splitlines() if line.strip()]
        if len(lines) < 2 or lines[-2] != "---" or not lines[-1].startswith("&copy;"):
            fail("contract", "README skeleton must end with a '---' rule and the '&copy;' footer")

    final = re.search(r"^### Final `N-step\.yml`\n.*?^```yaml\n(.*?)^```$", text, flags=re.DOTALL | re.MULTILINE)
    if final is None or not re.search(r"^name: Step \d+ # Last step of the exercise$", final.group(1), flags=re.MULTILINE):
        fail("contract", "final N-step.yml skeleton must declare 'name: Step N # Last step of the exercise'")

    for section in (
        "## Step and activity rules",
        "## Activity block conventions",
        "## Template variables in step content",
        "### Copy Exercise badge rules",
        "### README footer",
        "## Workflow chaining rules",
        "## Permissions matrix",
        "## Pre-handoff checks",
    ):
        if section not in text:
            fail("contract", f"contract reference is missing section '{section}'")


def check_badges() -> None:
    """Badge drift means exercises stop looking consistent, which is the whole
    point of standardizing them. The Copy Exercise button is held to the image
    in skills/exercise-template's README."""
    seen: set[str] = set()
    known = set(CANONICAL_BADGES.values()) | {COPY_EXERCISE_IMAGE}

    for path in markdown_files():
        rel = path.relative_to(ROOT)
        for url in re.findall(r"https://img\.shields\.io/badge/[^)\s`\"']+", read(path)):
            if url in known:
                seen.add(url)
            elif "Copy%20Exercise" in url:
                fail("badges", f"{rel}: non-canonical Copy Exercise badge: {url}")
            else:
                fail("badges", f"{rel}: non-canonical shields.io badge: {url}")

    for kind, url in {**CANONICAL_BADGES, "copy-exercise": COPY_EXERCISE_IMAGE}.items():
        if url not in seen:
            fail("badges", f"canonical '{kind}' badge is not documented anywhere")


def check_badge_blocks() -> None:
    """A prompt or command badge leads one blockquote: the badge, a bare `>`
    line, then the fence language the badge requires. A blank line between them
    splits the quote, and a wrong language changes how the block renders."""
    badge_line = re.compile(
        r"^(?P<prefix>[ \t]*)> !\[(?P<alt>[^\]]*)\]\((?P<url>https://img\.shields\.io/badge/[^)\s]+)\)\s*$"
    )
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        lines = read(path).splitlines()
        for index, line in enumerate(lines):
            match = badge_line.match(line)
            fence = BADGE_FENCES.get(match.group("url")) if match else None
            if fence is None:
                continue
            prefix = match.group("prefix")
            follow = [following.rstrip() for following in lines[index + 1 : index + 3]]
            if match.group("alt") != "Static Badge" or follow != [prefix + ">", prefix + "> ```" + fence]:
                fail(
                    "badge-blocks",
                    f"{rel}:{index + 1}: write '> ![Static Badge](...)', then '>', then '> ```{fence}' in one blockquote",
                )


def check_skeleton_slots() -> None:
    """Every template slot in the contract's skeletons must carry the
    `(replace-me: ...)` sentinel.

    A bare descriptive phrase such as `Exercise title` or `First instruction`
    reads as real content, so an author can copy a skeleton verbatim and pass
    the no-placeholder gate while shipping unusable learner content. One
    sentinel keeps the gate's single token sufficient.
    """
    path = ROOT / CONTRACT
    if not path.exists():
        return

    phrases = [
        "Exercise title", "One-line description of the exercise",
        "Target audience description", "Learning objectives",
        "Description of what the learner will create",
        "Prerequisite skill or exercise", "Other prerequisites",
        "Learning objective step", "Step name", "Theory title",
        "Activity title", "First instruction", "Second instruction",
        "Additional instructions as needed", "Troubleshooting tip or hint",
        "Additional troubleshooting tips as needed", "Accomplishment #",
        "Brief story or scenario to introduce the step",
        "One line introduction message for the exercise",
        "Natural follow-up Skills exercise",
        "Documentation link to learn more about the feature",
        "Other resources or calls to action",
        "Optional note relevant to this section",
    ]

    text = read(path)
    for match in re.finditer(r"^```(?:markdown|yaml)\n(.*?)^```$", text, flags=re.DOTALL | re.MULTILINE):
        block = match.group(1)
        base = text[: match.start()].count("\n") + 1
        for offset, line in enumerate(block.splitlines(), 1):
            for phrase in phrases:
                if phrase not in line:
                    continue
                # The phrase must appear inside a (replace-me: ...) wrapper.
                wrapped = re.search(r"\(replace-me:[^)]*" + re.escape(phrase), line)
                if not wrapped:
                    fail(
                        "skeleton-slots",
                        f"{CONTRACT}:{base + offset}: unmarked template slot {phrase!r}; "
                        f"wrap it as (replace-me: ...)",
                    )


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

    check_manifest()
    check_agents()
    check_skill_discovery()
    check_lifecycle_topology()
    check_fence_balance()
    check_yaml_blocks()
    ref = check_toolkit_refs()
    check_contract_self_consistency()
    check_skeleton_slots()
    check_badges()
    check_badge_blocks()

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
