---
name: github-skills-outline
description: "Create learner-centered GitHub Skills exercise outlines from a topic, demo, workshop, or rough idea. Use this whenever the user wants to design a GitHub Skills exercise, convert training material into a self-paced GitHub exercise, name the exercise or its repository, define learning objectives and steps, or plan validation before building repository files."
---

# Create GitHub Skills outline

Use this skill to design a self-paced GitHub Skills-style exercise before implementation begins. The outline
is a build contract: `github-skills-bootstrap` should be able to generate the repository from it
without guessing.

Start from the learner outcome, not the tool list. Prefer concrete GitHub actions such as editing a file,
opening a pull request, resolving feedback, running a workflow, or inspecting a result. Keep the exercise
small enough for one focused sitting and surface prerequisites and assumptions early.

## Workflow

1. Clarify the topic, target learner, prerequisites, time box, and desired outcome.
2. Narrow broad ideas to one primary learner outcome.
3. Design a scenario that gives the learner a reason to complete the task.
4. Propose the exercise identity: a title, repository name candidates, and a recommended pick. See
   [Exercise identity](#exercise-identity).
5. Break the exercise into 3 to 5 steps with one learner action per step.
6. Write a Theory block and one or more activities for every step. Split a step into numbered activities when
   the learner switches tools or produces a separate result.
7. Define validation signals and feedback for each step.
8. Name the repository files, workflows, and assets needed for implementation.
9. Call out open questions instead of inventing domain details that affect correctness.
10. Present the outline, take feedback, and revise. Repeat until the user explicitly approves.

## Approval gate

The outline is not finished until the user approves it. On each revision, state what changed and what still
needs a decision. When approved:

- confirm the exercise title and the chosen repository name explicitly; they are reused downstream for the
  README title, the Copy Exercise badge, and the default publish target,
- record where the approved outline is stored so the bootstrap step can consume it (bootstrap saves it to
  `.github/exercise-outline.md` in the exercise repository),
- confirm the step count, graded steps, and file map one final time,
- hand off to `github-skills-bootstrap`.

Do not generate repository files from this skill.

## Exercise identity

Propose the title and repository name with the first outline draft so the user can react to them early.
Naming is part of the outline, not a publish-time decision: bootstrap writes it into the README and badge,
and publish uses it as the default target.

- **Title** — eye-catching and outcome-focused. A short hook plus the concrete outcome works well, for
  example `Cleared for Takeoff: Ship a Feature with the GitHub Copilot App`.
- **Derive both from the exercise abstract.** Base the title and every name candidate on the exercise
  abstract prompt the user gave (its topic, learner outcome, and scenario), not on generic product names.
  If the abstract changes during revision, re-check that the title and names still fit.
- **Repository name candidates** — offer 3 to 5. Each must be lowercase, hyphen-separated, use only
  letters, digits, and hyphens, start with a letter, and stay under about 40 characters. Lead with the
  product or topic so the name sorts and searches well, then add the hook, for example
  `copilot-app-cleared-for-takeoff`.
- **Never include a `skills-` prefix** in the title or any candidate name. The Copy Exercise badge adds it
  when naming the learner's copy (`skills-<repository>`), so a prefixed name would produce `skills-skills-...`.
- **Recommended pick** — name one candidate and say why in a sentence.
- **Learner copy name** — show the resulting `skills-<repository>` name.

Do not check name availability or create anything from this skill. Availability is confirmed when the
target owner is chosen during publish.

## Step design requirements

Every step must include all of the following. A step missing a Theory block or an Activity block is an
incomplete outline: fill the gap, or ask the user for the missing detail. Never emit a step with a Theory
heading and no content.

| Element | Requirement |
| --- | --- |
| `📖 Theory` | Exactly one per step. Real awareness-level content, two to five sentences, directly tied to the step's activities. Not a placeholder. |
| `⌨️ Activity` | At least one per step, each with concrete numbered actions a learner performs. Name a lone activity `Activity`; name several `Activity 1`, `Activity 2`, and so on. The final activity ends with the action that triggers validation. |
| Action types | Tag each action as chat prompt, CLI prompt, terminal, or GitHub UI so bootstrap emits the right badge block. |
| Troubleshooting | Recovery hints for the likely mistakes in each activity. Bootstrap places them in a `Having trouble? 🤷` block after that activity. |
| `Actions Trigger` | The GitHub event that advances the exercise (`pull_request`, `push` with `paths`, `issues`, `issue_comment`, `workflow_dispatch`). |
| `Grading-Check` | Whether the step is graded, and the concrete check: `skills/exercise-toolkit/actions/file-exists`, `skills/action-keyphrase-checker`, or a custom script. |
| Learner artifact | What exists in the repository after the step succeeds. |

Keep the exercise scoped to the requested topic. If a concept is useful but out of scope, list it as a
follow-up exercise instead of adding it to the current outline.

## Activity action types

When an activity action is a Copilot prompt or a terminal command, write the exact text in the outline and
tag its type by where the learner types it. Bootstrap renders it as a badge-led blockquote:

- **chat prompt** — Copilot Chat, the Copilot app, or an IDE: purple `Prompt` badge, `prompt` fence.
- **CLI prompt** — inside a Copilot CLI session, including slash commands such as `/login`: `CLI-Prompt`
  badge, `prompt` fence.
- **terminal** — a shell command, including the one that starts Copilot CLI: blue `Terminal` badge, `bash`
  fence.
- **GitHub UI** — plain numbered instruction, no badge.

## Reference guidance

- Prefer official references (GitHub Docs, GitHub Learn, GitHub Blog/Changelog, and official VS Code docs).
- Keep references relevant to the exact step content; do not add generic links that are not used.

## Formatting conventions

- Any image added for the exercise should be stored in `.github/images` and referenced with a relative path.
- Keep GitHub callouts left-justified (no indentation) when using `[!NOTE]`, `[!IMPORTANT]`, or `[!TIP]`
  outside a list. Inside an activity's numbered list, indent a callout three spaces under its item.
- Use this exact style:

> [!NOTE]
> This is a note

> [!IMPORTANT]
> This is an important item to be aware of for this exercise

> [!TIP]
> It is a good idea and recommended to do this tip

## Outline template

Return this structure by default:

```markdown
# [Exercise title]

## Summary

One-line description of the exercise.

## Exercise identity

- **Title**: [Eye-catching, outcome-focused title]
- **Repository name candidates** (derived from the exercise abstract, no `skills-` prefix):
  1. `[lowercase-hyphenated-name]` — [why]
  1. `[lowercase-hyphenated-name]` — [why]
  1. `[lowercase-hyphenated-name]` — [why]
- **Recommended repository name**: `[name]` — [one-sentence rationale]
- **Learner copy name**: `skills-[name]`
- **Target owner (if known)**: [account or organization, or "decide at publish"]
- **Copyright holder**: [name for `LICENSE` and the README footer, or "decide at publish"]

## Welcome block

- **Who is this for**:
- **What you'll learn**:
- **What you'll build**:
- **Prerequisites**:
- **How long**:

## Learning objectives

## Scenario

## Learner journey

### Step 1: [Step name]

**📖 Theory: [Theory title]**

[Two to five sentences of awareness-level context tied to the activity below.]

**⌨️ Activity: [Activity title]**

1. [Action] — _(type: chat prompt | CLI prompt | terminal | GitHub UI)_
1. [Action that triggers validation] — _(type: ...)_

**Troubleshooting**

- [Likely mistake and recovery]

**Transition**

- Actions Trigger: [event]
- Grading-Check: [graded? which check and what it asserts]
- Learner artifact: [what exists after this step]

### Step 2: [Step name]

**📖 Theory: [Theory title]**

[Two to five sentences of awareness-level context tied to the activities below.]

**⌨️ Activity 1: [Activity title]**

1. [Action] — _(type: chat prompt | CLI prompt | terminal | GitHub UI)_

**Troubleshooting (Activity 1)**

- [Likely mistake and recovery]

**⌨️ Activity 2: [Activity title]**

1. [Action] — _(type: ...)_
1. [Action that triggers validation] — _(type: ...)_

**Troubleshooting (Activity 2)**

- [Likely mistake and recovery]

**Transition**

- Actions Trigger: [event]
- Grading-Check: [graded? which check and what it asserts]
- Learner artifact: [what exists after this step]

### Step 3: [Step name]

[Same structure as step 1 for one activity, or step 2 for several. Repeat for every step.]

## Review recap

Feeds `.github/steps/x-review.md`.

- Accomplishments:
- What's next:

## File map

| File | Purpose |
| --- | --- |
| `.github/exercise-outline.md` | Approved outline, saved verbatim by bootstrap |
| `README.md` | |
| `LICENSE` | MIT license; its copyright line feeds the README footer |
| `.github/steps/1-step.md` | |
| `.github/steps/x-review.md` | |
| `.github/workflows/0-start-exercise.yml` | |
| `.github/workflows/1-step.yml` | |
| `.github/workflows/N-step.yml` | Final step, named `Step N # Last step of the exercise`; posts the review |

## Success criteria

## Risks and open questions
```

## Quality bar

- The title and repository name are approved, and the name follows the naming rules above.
- Objectives should be observable: the learner can demonstrate them through repository activity.
- Every step has a Theory block with real content and at least one activity, and every activity has its own
  troubleshooting hints.
- Steps should be small enough that validation can give targeted feedback.
- Validation should check intent, not only file existence.
- The file map should name real files, aligned by number, with every step workflow as `N-step.yml`, the final
  one named `Step N # Last step of the exercise`, and the review content as `x-review.md`.
- The outline should be implementable as GitHub issues, comments, workflows, and Markdown content.
