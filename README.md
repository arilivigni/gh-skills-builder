Design, build, review, and publish GitHub Skills-style exercises with custom agents and Agent Skills for learner journeys, workflow-backed validation, and release readiness.

## Installation

### Copilot CLI

Install directly from this repository:

```shell
copilot plugin install arilivigni/gh-skills-builder
```

Or from within an interactive Copilot session:

```
/plugin install arilivigni/gh-skills-builder
```

> [!NOTE]
> Installing from `arilivigni/gh-skills-builder` performs a direct repository install. You can verify the install with:
> ```shell
> copilot plugin list
> ```
> After install, manage the plugin by name (`gh-skills-builder`) for update and uninstall commands.

To update to the latest version:

```shell
copilot plugin update gh-skills-builder
```

To remove the plugin:

```shell
copilot plugin uninstall gh-skills-builder
```

### Copilot App

1. Open the Copilot App and go to **Plugins**.
2. Select **Add plugin**, then provide `arilivigni/gh-skills-builder`.
3. Confirm install, then enable the plugin for your chat/session.

> [!TIP]
> If you prefer VS Code, open the Command Palette (`⌘⇧P` / `Ctrl+Shift+P`), run **Chat: Plugins**, then install **gh-skills-builder** from the plugin picker.

## What's Included

### Agents

| Agent | Mention | Role | Tool Access |
| --- | --- | --- | --- |
| **Outline Architect** | `@github-skills-outline-architect` | Converts an idea, workshop, or demo into a learner-centered exercise outline with objectives, scenario, steps, validation, and success criteria. | Read, search, fetch, and edit planning docs |
| **Exercise Builder** | `@github-skills-exercise-builder` | Converts an approved outline into repository structure, Markdown steps, issue flow, workflows, and validation scaffolding. | Full coding and test tools |
| **Quality Reviewer** | `@github-skills-quality-reviewer` | Reviews an exercise for learning value, validation reliability, workflow safety, accessibility, and publish readiness. | Read, search, run commands, and run tests |
| **Publisher** | `@github-skills-publisher` | Prepares release notes, PR descriptions, validation evidence, final checklist, and publication handoff guidance. | Read, edit docs, run commands, and run tests |

### Skills

The plugin provides four lifecycle skills:

- `/create-github-skills-outline` — design a new exercise or convert training material into a self-paced GitHub Skills outline.
- `/bootstrap-github-skills-exercise` — create repository files, step Markdown, workflow plans, validation scripts, and starter structure from an approved outline.
- `/review-github-skills-exercise` — audit an exercise for learner experience, validation correctness, workflow safety, accessibility, and readiness.
- `/publish-github-skills-exercise` — prepare final checklist, release notes, PR copy, validation evidence, and launch guidance.

## Quick Start

### 1. Create the exercise outline

```
@github-skills-outline-architect I want to teach [topic] as a 30-minute GitHub Skills exercise.
Use /create-github-skills-outline to define objectives, learner steps, and validation ideas.
```

### 2. Bootstrap the repository

```
@github-skills-exercise-builder Use the approved outline to scaffold the exercise.
Use /bootstrap-github-skills-exercise to create README content, steps, workflows, and validation guidance.
```

### 3. Review before launch

```
@github-skills-quality-reviewer Review this exercise for learner clarity, validation reliability, workflow safety, and accessibility.
Use /review-github-skills-exercise and prioritize release blockers.
```

### 4. Prepare for publication

```
@github-skills-publisher Prepare this exercise for release.
Use /publish-github-skills-exercise to produce validation evidence, PR description, release notes, and remaining risks.
```

## How It Works

The plugin splits exercise creation into four focused phases so the human can approve the learning design before repository automation is generated:

- **Outline first** — define the learner outcome, scenario, steps, and validation signals.
- **Bootstrap second** — create or update repository assets only after the outline is approved.
- **Review third** — catch weak validation, unsafe workflow behavior, unclear learner instructions, and accessibility issues.
- **Publish last** — assemble release evidence and handoff notes for contribution or rollout.

## Companion Instructions

The Awesome Copilot plugin spec declares plugin content with `agents`, `commands`, and `skills`. Copilot instructions are standalone resources, so this plugin includes `instructions/github-skills-exercises.instructions.md` as an optional companion file to copy into exercise repositories.

## Evaluation

Test prompts are in `evals/evals.json`. They cover outline creation, bootstrap planning, quality review, and publish readiness.

## Release process (SemVer)

This plugin follows strict semantic versioning:

| Change type | Version bump | Examples |
| --- | --- | --- |
| Breaking behavior or contract changes | **MAJOR** (`X.0.0`) | Renaming/removing expected capabilities or changing required usage patterns |
| New non-breaking capabilities | **MINOR** (`X.Y.0`) | Adding agents, skills, or non-breaking plugin features |
| Fixes and non-breaking maintenance | **PATCH** (`X.Y.Z`) | Bug fixes, docs updates, wording improvements |

### CI gate

`.github/workflows/plugin-ci.yml` runs on pull requests and pushes to `main` and validates:
- `.github/plugin/plugin.json` syntax
- referenced agent and skill paths from the plugin manifest
- required `name` and `description` metadata presence in each skill `SKILL.md`
- local markdown links in `README.md`

### Deployment plan

1. Merge to `main` only after CI is green.
2. Confirm `.github/plugin/plugin.json` has the intended release version.
3. Prepare and verify first-release metadata from `main`:

```shell
python3 -m json.tool .github/plugin/plugin.json >/dev/null
grep '"version"' .github/plugin/plugin.json
```

4. Validate install paths before tagging:

```shell
copilot plugin install arilivigni/gh-skills-builder
copilot plugin list
```

5. Tag and publish from `main`:

```shell
git tag vX.Y.Z
git push origin vX.Y.Z
```

6. Verify the tag points to the intended commit:

```shell
git rev-parse vX.Y.Z
```

Example first stable release:

```shell
git tag v1.0.0
git push origin v1.0.0
git rev-parse v1.0.0
```
