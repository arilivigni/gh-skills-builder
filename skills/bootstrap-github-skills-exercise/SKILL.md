---
name: bootstrap-github-skills-exercise
description: "Bootstrap a GitHub Skills exercise repository from an approved outline, following the skills/exercise-template layout: a README with the Copy Exercise badge, .github/workflows/0-start-exercise.yml, numbered .github/steps/N-step.md files with matching N-step.yml workflows, and .github/steps/x-review.md. Use this when the user asks to create exercise files, step Markdown, issue templates, GitHub Actions workflows, validation scripts, starter content, or repository structure for a GitHub Skills-style learning experience."
---

# Bootstrap GitHub Skills exercise

Use this skill when an outline is approved and the user wants repository content or automation.

> [!IMPORTANT]
> Read `references/exercise-template-contract.md` before writing files. It holds the exact file names,
> workflow skeletons, reusable workflow inputs and outputs, action pins, chaining rules, and Markdown
> skeletons implemented by `skills/exercise-template` and `skills/exercise-toolkit`. Follow it unless the
> target repository intentionally diverges, and say so when you diverge.

## Preconditions

Do not start until you have:

1. An approved outline. If none exists, run `create-github-skills-outline` first.
2. A step-by-step journey where **every step has exactly one Theory block and one or more Activity blocks**,
   with each activity's troubleshooting tips planned.
3. A decision for each step on whether it is graded and what the grading check asserts.
4. An approved exercise title and repository name from the outline's Exercise identity section.

If the outline is missing a Theory or an Activity for any step, or has no approved title and repository
name, stop and resolve it with the user. Do not invent filler content or pick a name on the user's behalf.

## First inspect the repo

Before editing, identify existing conventions:

- Where learner steps live.
- How workflows create issues, post comments, and validate progress.
- Which `skills/exercise-toolkit` ref the repository already pins.
- Whether reusable local actions or scripts already render Markdown templates.
- Existing test commands or workflow harnesses.

Reuse established patterns. Keep learner-facing copy concise, encouraging, and action-oriented, and
maintainer-facing logic explicit and testable. Prefer shared local actions or scripts for repeated rendering
or validation. When a test harness exists, add appropriate tests, fixtures, or a maintainer validation script.
Do not overwrite learner or maintainer edits after bootstrap unless the user explicitly requests regeneration.

## Repository shell (first action)

Before writing any step or workflow, create the repository shell. It locks in the approved identity and
gives later rounds and resumption a durable record of the outline:

1. Save the approved outline verbatim to `.github/exercise-outline.md`. If the target repository already
   stores its outline elsewhere, reuse that location and say so.
2. Write `README.md` from the contract's README skeleton, filling the title, one-line summary, and Welcome
   block from the outline.
3. Fill the Copy Exercise badge from the Exercise identity, following the contract's Copy Exercise badge
   rules. Keep the badge markup and image exactly as the skeleton has them and change only the link:
   `template_name` is the approved repository name, `name` is `skills-<repository name>`, and `description`
   is `Exercise:+` followed by the approved title with words joined by `+`. Use the target owner for
   `template_owner` when the outline names one; otherwise ask the user. If the owner is still undecided,
   leave the `OWNER` token in place and report it, so the no-placeholder gate catches it before publish.
4. End the README with the skeleton's footer, using the year and copyright holder from the `LICENSE`
   copyright line, or the current year when that line has none. For a new standalone repository without a
   `LICENSE`, first create the MIT `LICENSE` with the copyright holder named in the outline's Exercise
   identity, or one the user confirms. If the holder is still undecided, do not create `LICENSE`; leave the
   footer's `(replace-me: copyright holder)` slot and report it.

Do not create, rename, or push a GitHub repository from this skill. Repository creation belongs to
`publish-github-skills-exercise` behind explicit authorization.

## Build order

Work in this order so each file can reference something that already exists:

1. Repository shell — `.github/exercise-outline.md` and the `README.md` stub described above.
2. `README.md` — complete the objectives, start path, and troubleshooting details.
3. `.github/steps/N-step.md` for every step.
4. `.github/steps/x-review.md`.
5. `.github/workflows/0-start-exercise.yml`.
6. `.github/workflows/N-step.yml` for each intermediate step.
7. The final `.github/workflows/N-step.yml`, named `Step N # Last step of the exercise`, which posts the
   review.
8. Grading jobs, local actions, or scripts.
9. Maintainer validation notes.

## Required file set

| File | Required |
| --- | --- |
| `.github/exercise-outline.md` | always, unless the repository already records the outline elsewhere |
| `README.md` | always |
| `.github/steps/N-step.md` | one per step |
| `.github/steps/x-review.md` | always |
| `.github/workflows/0-start-exercise.yml` | always |
| `.github/workflows/N-step.yml` | one per step; the final one is named `Step N # Last step of the exercise` |
| `.github/images/` | when the exercise uses images |
| `LICENSE`, `.gitignore` | for a new standalone exercise repository |

## Markdown templates

Feedback templates come from `skills/exercise-toolkit` and are consumed by checking the toolkit out into the
workspace:

```yaml
- name: Get response templates
  uses: actions/checkout@v6
  with:
    repository: skills/exercise-toolkit
    path: exercise-toolkit
    ref: v0.9.3
```

Do not copy toolkit templates into the exercise repository. Create a local `.github/markdown-templates/`
directory only for exercise-specific copy that has no toolkit equivalent.

## Toolkit version check

The default toolkit ref is `v0.9.3`. When creating a new exercise, check whether a newer release exists and
ask the user whether to adopt it:

> ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
>
> ```bash
> gh api repos/skills/exercise-toolkit/releases/latest --jq .tag_name
> ```

If the latest published release is newer than `v0.9.3`, ask the user before changing anything, then apply
their answer to every toolkit reference in the repository.

> [!WARNING]
> Never pin a draft or prerelease. A draft release appears in the releases API but **its git tag does not
> exist**, so `uses: ...@<tag>` fails to resolve and every workflow breaks. Use `releases/latest`, which
> excludes drafts, and confirm the tag resolves with
> `gh api repos/skills/exercise-toolkit/git/ref/tags/TAG` before pinning it.

## Workflow structure expectations

Follow the standard job shape from the contract reference:

- `find_exercise` to locate the learner issue and its number/URL.
- optional `check_step_work` for grading and targeted feedback.
- `post_next_step_content` for transition behavior.

If `check_step_work` is present, include it in `post_next_step_content.needs`. If you remove it, reduce
`needs` back to `[find_exercise]`.

## Workflow design guidance

- Use least-privilege `permissions` per the contract reference matrix. Grant them per job, not workflow-wide:
  set `permissions: {}` at the workflow level so the learner-triggered grading job does not inherit
  `actions: write` from the job that toggles workflows.
- Pin every action and reusable workflow. Use one `skills/exercise-toolkit` ref across the whole repository;
  the default is `v0.9.3`. Never pin a draft release, whose tag does not exist.
- Only `Step 0` is enabled on a fresh copy. Every other step workflow ships disabled and is enabled by the
  previous step.
- Guard the start workflow with `if: !github.event.repository.is_template`.
- Make check workflows fail helpfully before they pass. Every check uses `continue-on-error: true` and a row
  in the `step-results-table.md` `results_table`, with a stable `id` and a closing
  `if: contains(steps.*.outcome, 'failure')` failure step.
- Update the existing feedback comment via `peter-evans/find-comment` rather than posting duplicates. Always
  scope the lookup with `comment-author` and `body-includes`: a bare `direction: last` returns whatever was
  posted most recently, so `edit-mode: replace` can overwrite a learner's own comment.
- Avoid hardcoded repository-specific URLs in source Markdown; render them at runtime.
- Prevent one-shot bootstrap workflows from overwriting legitimate later edits.
- Use `paths` filters on push-based triggers where practical to avoid accidental transitions from unrelated
  commits.
- Ensure the last step finishes the exercise instead of enabling a non-existent next step. Name its
  workflow `N-step.yml` like every other step, not `N-last-step.yml`, and mark only its name line:
  `name: Step N # Last step of the exercise`.

Confirm the first-run path works from a fresh repository copy and each grading workflow fails with useful
feedback before it passes. Make completion behavior explicit: close the issue, comment success, open the
next issue, or show the final result as appropriate.

## Step and activity requirements

Build every step from the contract's step skeletons and its Step and activity rules, so learners meet the
same rhythm in every step. Every `.github/steps/N-step.md` contains, in this order:

1. One `## Step N: <title>` heading, where `N` matches the filename number.
1. Optionally, a short story, scenario, or image that sets up the step.
1. Exactly one `### 📖 Theory: <title>` heading followed by real awareness-level content. Put supporting
   detail in `####` subsections, such as `#### References`, instead of adding more `###` sections.
1. The activities the outline lists for the step, each with numbered instructions:
   - one activity: `### ⌨️ Activity: <title>`,
   - two or more: `### ⌨️ Activity 1: <title>`, `### ⌨️ Activity 2: <title>`, and so on, numbered from 1
     with no gaps.
1. A `Having trouble? 🤷` `<details>` block directly after **each** activity, with hints for that activity.

Write every activity the same way:

- Use the ⌨️ emoji, never `:keyboard:`. Never number a lone activity or mix the two heading forms in a step.
- Start a new activity when the learner switches tools or produces a separate result.
- Number every instruction `1.` and indent everything that belongs to it three spaces: extra paragraphs,
  images, callouts, code blocks, and badge-led blockquotes. A line at column 0 ends the list.
- End the step's final activity with the action that triggers validation, then this instruction:
  `1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.`
- A stretch goal or other `<details>` block can follow an activity's `Having trouble? 🤷` block, but never
  replaces it.

Write `.github/steps/x-review.md` from the contract's review skeleton: a `## Review` heading, a recap of what
the learner accomplished, and `### What's next?` as the last section.

## Activity block conventions

Inside an activity, every Copilot prompt and every terminal command uses a badge-led blockquote: the badge
line, a bare `>` line, then the fenced block, all inside one blockquote with no blank line, indented three
spaces under its numbered list item. Put only what the learner sends or runs inside the fence. Use the badge
URLs verbatim and keep the alt text `Static Badge`.

Choose the badge by where the learner types the text:

| The learner types it into | Badge | Fence language |
| --- | --- | --- |
| Copilot Chat, the Copilot app, or an IDE | Prompt | `prompt` |
| A Copilot CLI session, including slash commands such as `/login` | CLI Prompt | `prompt` |
| A shell, including the command that starts a Copilot CLI session | Terminal | `bash` |

Copilot Chat, app, or IDE prompt:

```markdown
1. Ask Copilot Chat to summarize the change.

   > ![Static Badge](https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple)
   >
   > ```prompt
   > Summarize the changes in this pull request.
   > ```
```

Copilot CLI prompt:

```markdown
1. Run the prompt with Copilot CLI.

   > ![Static Badge](https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff)
   >
   > ```prompt
   > Explain what this workflow does.
   > ```
```

Terminal command:

```markdown
1. Run the command.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > gh repo view
   > ```
```

## Template variables

`GrantBirki/comment` renders a step file as a Nunjucks template only when the workflow step that posts it
passes `vars:`. `0-start-exercise.yml` passes `login` and `full_repo_name` with step 1, so step 1 can use
`{{ login }}` and `{{ full_repo_name }}`. Later steps and the review are posted without `vars:`, so double
braces there reach the learner literally.

- Add a `vars:` entry to the posting step wherever a step file uses a variable, and pass every name it uses.
- In a step file posted with `vars:`, wrap literal `${{ ... }}` expressions, such as workflow snippets, in
  `{% raw %}` and `{% endraw %}`.

## Content formatting conventions

- Store exercise images in `.github/images` and reference them with a relative path such as
  `../images/inspectocat.png`. Always provide meaningful alt text.
- Keep GitHub callouts left-justified (no indentation) when they are not nested in a list item. Inside an
  activity's numbered list, indent a callout three spaces under its item, because a left-justified callout
  ends the list.
- Use this exact style:

> [!NOTE]
> This is a note

> [!IMPORTANT]
> This is an important item to be aware of for this exercise

> [!TIP]
> It is a good idea and recommended to do this tip

## Completion gates

Do not report the bootstrap as done until all of these hold:

1. No placeholder text remains in `README.md` or `.github/` — not only `replace-me`, but also bare skeleton
   tokens (`OWNER`, `REPO`, `ORG`, `TITLE`, `FEATURE`, `VISIBILITY`) and bracketed slots such as
   `[Step name]` or `[Action]`.
2. Every step file follows the step anatomy: `## Step N:` comes first, then exactly one Theory heading with
   content and no other `###` sections besides activities. A step has either one `### ⌨️ Activity:` or
   activities numbered from `### ⌨️ Activity 1:` with no gaps. Each activity has `1.`-numbered instructions
   that no column-0 line splits, and its own `Having trouble? 🤷` block. The final activity ends with the Mona
   instruction.
3. Every prompt and command badge is one of the three canonical badges, with alt text `Static Badge`, and
   sits in a single blockquote with a bare `>` line and a `prompt` fence (Prompt, CLI Prompt) or a `bash`
   fence (Terminal).
4. Template variables render: step files posted without `vars:` contain no `{{ name }}` variables or
   `{% %}` tags, and step files posted with `vars:` use only the names passed and wrap literal `${{ }}`
   expressions in raw tags.
5. Required files exist (`README.md`, `.github/steps/x-review.md`, `.github/workflows/0-start-exercise.yml`),
   there is at least one numbered step, and step content and step workflows line up by number. Every step
   workflow is `N-step.yml` declaring `name: Step N`, and only the workflow for the highest step is marked
   `# Last step of the exercise`.
6. Every `gh workflow enable "Step N"` names a workflow that exists, and the final workflow enables nothing.
7. Every `STEP_N_FILE` value points at step `N`'s own file, every `REVIEW_FILE` value points at
   `.github/steps/x-review.md`, and the final workflow references `REVIEW_FILE`.
8. Every `skills/exercise-toolkit` reference uses the same pinned tag, that tag exists, and no toolkit
   checkout is unpinned.
9. Every workflow sets `permissions: {}` and grants permissions per job, and the grading job holds neither
   `actions: write` nor `contents: write`. `post_next_step_content.needs` includes `check_step_work` when
   that job exists, and does not reference it when it does not.
10. All workflow YAML parses.
11. The README has exactly one Copy Exercise badge, under `### How to start this exercise`. It uses the
    canonical image and links to `https://github.com/new` with `owner=%40me`, `name=skills-<template_name>`,
    `description=Exercise:+<Title>`, and `visibility=public` (`private` only for a privately published
    exercise). The README ends with a `---` rule and the `&copy;` footer, whose year matches the `LICENSE`
    copyright year.
12. The README title matches the approved exercise title, and the badge's `template_owner` and
    `template_name` are the publishing owner and the approved repository name.
13. The start workflow has a real first-run trigger enabled, not only `workflow_dispatch` — or the README
    explicitly tells the learner to start the exercise by running the workflow manually. The advertised
    "copy and wait" start path must have an event behind it.

The contract reference includes a copy-ready command block that mechanically verifies gates 1 through 11.
Gates 12 and 13 are judgement calls and need a human read.

## Report back

When the build round finishes, tell the user:

- the files created or changed,
- which steps are graded and what each grading check asserts,
- anything you had to decide on their behalf,
- what to review first,
- which completion gates pass and which do not.

Then stop and wait for approval or change requests before starting another round.
