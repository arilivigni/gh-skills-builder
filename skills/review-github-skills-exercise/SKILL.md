---
name: review-github-skills-exercise
description: "Review GitHub Skills exercises for learner experience, step and activity consistency, parity with skills/exercise-template (0-start workflow, numbered steps, x-review.md, Copy Exercise badge), validation correctness, workflow safety, accessibility, and publish readiness. Use this whenever the user asks to audit, review, improve, QA, or validate a GitHub Skills-style exercise repository or draft."
---

# Review GitHub Skills exercise

Use this skill to review an exercise draft with a high signal-to-noise ratio.

## Report-only boundary

Do not edit exercise files, apply fixes, or change repository or remote state during review, even when edit
and command tools are available. Use inspection and validation that do not modify the exercise; if a check
requires changes or a live exercise run, report it as unverified rather than performing it during review.
After reporting findings and proposed fixes, stop and wait for the user to choose which fixes to apply.
Approved fixes belong to a separate bootstrap round, followed by another review.

This is a behavioral rule, not a tool-permission boundary. A review performed by the same agent that built
the exercise is not independent review.

## Review process

1. Read the README and identify the promised learner outcome.
2. Trace the learner journey from start through completion.
3. Verify every step has a Theory block with real content and at least one activity, and that every step
   follows the same step and activity anatomy.
4. Inspect workflows, local actions, scripts, and templates that drive validation or feedback.
5. Check template parity against the template contract, `references/exercise-template-contract.md` in the
   `bootstrap-github-skills-exercise` skill: file and workflow numbering, the final workflow, toolkit ref
   consistency, chaining, the README Copy Exercise badge and footer, and leftover placeholders.
6. Run the contract's Pre-handoff checks from the exercise repository root when the environment allows. They
   only read files and query whether the pinned toolkit tag exists. Run each check on its own so one failure
   does not hide the rest, and report each failure using the severity guide below. List any check you could
   not run under `Unverified checks`.
7. Check tests or validation docs.
8. Report only findings that affect learning, reliability, safety, accessibility, or publication.

## Rubric

### Step content completeness (blocking)

- Every `.github/steps/N-step.md` has exactly one `### 📖 Theory:` heading followed by real
  awareness-level content. A Theory heading with no content, or a step with no Theory block, is a blocking
  finding.
- Every step has at least one activity heading, `### ⌨️ Activity:` or `### ⌨️ Activity 1:`, with actionable
  numbered instructions. A step with no activity is a blocking finding.
- Theory content is tied to the activities in the same step, not generic background.

### Step and activity consistency

Every step follows the contract's Step and activity rules, so learners meet the same rhythm in every step:

- `## Step N: <title>` is the first heading, and `N` matches the filename number.
- The only `###` sections are the Theory and the activities. Supporting detail sits in `####` subsections,
  such as `#### References`.
- A step with one activity uses `### ⌨️ Activity: <title>`. A step with several uses `### ⌨️ Activity 1:`,
  `### ⌨️ Activity 2:`, and so on, numbered from 1 with no gaps. Every activity has a title and uses the ⌨️
  emoji, not the `:keyboard:` shortcode.
- Each activity is followed by its own `Having trouble? 🤷` block with hints for that activity. A stretch
  goal or other `<details>` block can follow it but does not replace it.
- Every instruction is numbered `1.`, and everything that belongs to an item is indented three spaces. A
  column-0 callout, blockquote, image, or code fence after a blank line ends the list and restarts the
  numbering.
- The step's final activity ends with the action that triggers validation, then
  `1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.`

### Learner experience

- The start path is obvious.
- Each step explains what to do and why it matters.
- Objectives match the tasks, which require meaningful practice with concise explanations.
- Feedback helps the learner recover from common mistakes.
- Completion is visible and satisfying.

### Template parity

- Step files and step workflows align by number (`N-step.md` ↔ `N-step.yml` ↔ `name: Step N`).
- The final workflow is `N-step.yml` for the highest step, declared as
  `name: Step N # Last step of the exercise`. It posts `.github/steps/x-review.md` and enables no other step.
  No other workflow carries the `# Last step of the exercise` marker.
- Every `gh workflow enable "Step N"` names a workflow that exists.
- Every `STEP_N_FILE` value points at step `N`'s own file, and every `REVIEW_FILE` value points at
  `.github/steps/x-review.md`.
- Every `skills/exercise-toolkit` reference uses the same pinned release tag, none use `@main`, and the
  pinned tag actually resolves (a draft release has no git tag and will break every workflow).
- If `check_step_work` exists, `post_next_step_content.needs` includes it; if it was removed, `needs` is back
  to `[find_exercise]`.
- The start workflow is guarded with `if: !github.event.repository.is_template`.
- The start workflow has a real first-run trigger, not only `workflow_dispatch`, unless the README explicitly
  tells the learner to start it manually. A README promising an automatic start with no event behind it
  leaves the learner on an apparently broken repository.
- No placeholder text remains in `README.md` or `.github/`: not only `replace-me`, but bare skeleton tokens
  (`OWNER`, `REPO`, `ORG`, `TITLE`, `FEATURE`, `VISIBILITY`) and bracketed slots such as `[Step name]`.
- `### How to start this exercise` contains exactly one Copy Exercise badge, copied from the
  `skills/exercise-template` README with its image unchanged:
  `https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935`.
- The badge links to `https://github.com/new` with the correct `template_owner` and `template_name`, plus
  `owner=%40me`, `name=skills-<template_name>`, `description=Exercise:+<Title+words>`, and
  `visibility=public`, or `visibility=private` for a privately published exercise.
- The README ends with a `---` rule and the footer
  `&copy; <year> <holder> &bull; [Code of Conduct](...) &bull; [MIT License](https://gh.io/mit)`, whose year
  matches the `LICENSE` copyright line.

### Activity block conventions

- Every Copilot prompt and terminal command inside an activity uses a badge-led blockquote: the badge line,
  a bare `>` line, then the fence, all in one blockquote with no blank line, indented three spaces under its
  numbered list item.
- The badge matches where the learner types: the purple `Prompt` badge for Copilot Chat, the Copilot app, or
  an IDE; the `CLI-Prompt` badge inside a Copilot CLI session, including slash commands such as `/login`; and
  the blue `Terminal` badge for shell commands, including the one that starts Copilot CLI.
- Prompt and CLI Prompt blocks use a `prompt` fence. Terminal blocks use a `bash` fence.
- Badge URLs are unmodified and alt text is `Static Badge`.

### Validation reliability

- Checks verify the intended behavior.
- Failing states produce actionable messages.
- Success criteria are neither too loose nor too brittle.
- Re-running the exercise does not create confusing duplicate state.
- Template variables render as intended. `GrantBirki/comment` renders a step file only when the step that
  posts it passes `vars:`. Without `vars:`, `{{ name }}` reaches the learner literally. With `vars:`, a name
  that was not passed renders empty, and a `${{ ... }}` snippet outside `{% raw %}` tags is mangled.
- Every grading check uses `continue-on-error: true` with a matching `results_table` row, and the job closes
  with `if: contains(steps.*.outcome, 'failure')`.

### Workflow safety

- Workflow permissions are least-privilege and granted per job, not workflow-wide. A workflow-level grant
  applies to every job, so check that the learner-triggered grading job does not inherit `actions: write`
  from the job that toggles workflows, and does not hold `contents: write` unless it actually commits.
- Automation does not overwrite learner or maintainer work unexpectedly.
- Issue comments use stable markers if they are updated. Any `find-comment` feeding an `edit-mode: replace`
  is scoped by `comment-author` and `body-includes`, so it cannot overwrite a learner's comment.
- Repository-specific links are rendered safely.
- Step 0/start behavior does not require manual workflow disabling and leaves expected step workflows off.
- Exercise workflows are disabled by default before publication and only run as the learner progresses.

### Accessibility and maintainability

- Images have useful alt text.
- Images are stored in `.github/images` and referenced with relative paths.
- Links are descriptive.
- Markdown is readable in GitHub.
- Repeated logic is shared or documented.
- Reset behavior and maintainer test instructions are clear.
- Ordered activity steps render with correct numbering (no broken lists caused by mixed blocks).
- `[!NOTE]`, `[!IMPORTANT]`, and `[!TIP]` callouts are left-justified (no indentation) when they are not
  part of a list. Inside an activity's numbered list, a callout is indented three spaces under its item.

Expected callout formatting:

> [!NOTE]
> This is a note

> [!IMPORTANT]
> This is an important item to be aware of for this exercise

> [!TIP]
> It is a good idea and recommended to do this tip

## Severity guide

Report these template and consistency findings under the section shown, so every review ranks them the same
way. Rank other findings by their effect on learning, reliability, safety, accessibility, and publication.

| Finding | Report under |
| --- | --- |
| A step without a Theory block that has content, or without an activity | Blocking findings |
| A missing Copy Exercise badge, or one whose `template_owner` or `template_name` does not name the published repository | Blocking findings |
| Inconsistent activity headings: a numbered lone activity, mixed or skipped numbers, a missing title, or `:keyboard:` | Important findings |
| An activity without its own `Having trouble? 🤷` block | Important findings |
| Explicit list numbers such as `2.`, or a column-0 line that splits an activity's list | Important findings |
| A final activity that does not end with the Mona instruction | Important findings |
| A badge separated from its block, a wrong fence language, or a restyled prompt or terminal badge | Important findings |
| A template variable that shows literally, renders empty, or mangles a `${{ ... }}` snippet | Important findings |
| A restyled Copy Exercise image, a second copy button, a link that lacks `owner=%40me`, `name=skills-<template_name>`, or `description=Exercise:+<Title>`, or a `visibility` that differs from the exercise's own | Important findings |
| A final workflow named `N-last-step.yml`, or a missing or misplaced `# Last step of the exercise` marker | Nice to improve |
| A `template_name` that differs from the repository name only in case | Nice to improve |
| A missing README footer, or a footer year that does not match `LICENSE` | Nice to improve |
| Extra `###` sections besides the Theory and activities, or a reworded Mona instruction | Nice to improve |

## Output format

```markdown
## Overall readiness

## Blocking findings

## Important findings

## Nice to improve

## Suggested validation

## Unverified checks
```

If no issues are found in a category, say `None`.

For each finding, include the file/location, why it matters, and a concrete fix. Order findings by priority.
If the exercise is ready, say so plainly and list the final checks already covered. Disclose anything that
could not be verified without running the exercise. Report findings and stop; do not implement fixes.
