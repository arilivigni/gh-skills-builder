---
description: "Guidance for building and maintaining GitHub Skills-style exercise repositories."
---

# GitHub Skills exercise repository guidance

Use these instructions when working in a repository that implements a self-paced GitHub Skills-style exercise.

## Exercise model

- Design for one clear learner outcome per exercise.
- Keep the learner journey issue-driven whenever possible: start issue, step comments, validation feedback, and completion.
- Every learner action should have visible feedback and a recoverable next step.
- Prefer small, verifiable steps over long open-ended tasks.
- Validation should check behavior or repository state, not merely whether files changed.

## Repository conventions

- Keep learner-facing Markdown in predictable locations such as `.github/steps/`, `.github/markdown-templates/`, or `docs/`.
- Keep automation in `.github/workflows/` and reusable local actions in `.github/actions/`.
- Document the exercise goal, audience, estimated duration, prerequisites, and reset/retry behavior in `README.md`.
- Include a maintainer-facing test or validation guide for checking the exercise before release.
- Keep step and workflow naming aligned (`N-step.md`, `N-step.yml`, workflow name `Step N`) unless the repository already uses a different consistent convention.
- Every step workflow, including the last, is `N-step.yml`. Mark only the final one, as
  `name: Step N # Last step of the exercise`. The review content is `.github/steps/x-review.md` with no
  number.
- The README's `### How to start this exercise` section has exactly one Copy Exercise badge, copied unchanged
  from the [`skills/exercise-template` README](https://github.com/skills/exercise-template/blob/main/README.md)
  except for its link parameters: `template_owner`, `template_name`, `name=skills-<template_name>`, and
  `description=Exercise:+<Title>`. Keep `visibility=public` unless the exercise itself is private.
- The README ends with a `---` rule and a footer line:
  `&copy; <year> <holder> &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)`,
  with the year and holder from `LICENSE`.
- Feedback templates come from `skills/exercise-toolkit` and are consumed by checking the toolkit out into the
  workspace. Do not copy them into the exercise repository. Create local `.github/markdown-templates/` files
  only for exercise-specific copy with no toolkit equivalent.
- Pin every action and reusable workflow. Use one `skills/exercise-toolkit` release tag across the whole
  repository; the current default is `v0.9.3`. Never use `@main`, and never pin a draft or prerelease, whose
  git tag does not exist.

## Step and workflow patterns

- Every step file opens with `## Step N: <title>`, then has exactly one `### 📖 Theory:` heading with real
  awareness-level content and at least one activity heading with numbered instructions. A step missing
  either is incomplete.
- Keep `Theory` concise and directly tied to the activities in the same step. Put supporting detail in
  `####` subsections, such as `#### References`, instead of more `###` sections.
- Use `### ⌨️ Activity: <title>` for a lone activity. When a step has several, number them
  `### ⌨️ Activity 1: <title>`, `### ⌨️ Activity 2: <title>`, and so on. Never mix the two forms, and use the
  ⌨️ emoji, not `:keyboard:`.
- Activity instructions should be numbered, action-oriented, and resilient to common mistakes. Number every
  item `1.` and indent everything that belongs to an item three spaces, so callouts, images, and code blocks
  do not restart the list.
- Follow each activity with its own `Having trouble? 🤷` details block with recovery hints for that activity.
- End the step's final activity with the action that triggers validation, then
  `1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.`
- Use `{{ name }}` template variables only in step files whose posting workflow step passes `name` in
  `vars:`. In those files, wrap literal `${{ ... }}` snippets in `{% raw %}` and `{% endraw %}`.
- For transitions, define both the GitHub event trigger and the grading/feedback check.
- Prefer step workflow shape: `find_exercise`, optional `check_step_work`, then `post_next_step_content`.
- If a grading job exists, gate transition on it and return actionable feedback on failure. Every check uses
  `continue-on-error: true` with a matching `results_table` row, and the job closes with
  `if: contains(steps.*.outcome, 'failure')`.
- Only `Step 0` is enabled on a fresh copy. Each intermediate step disables itself and enables the next; the
  final step only disables itself.

## Activity block conventions

Inside an activity, every Copilot prompt and every terminal command uses a badge-led blockquote: the badge
line, a bare `>` line, then the fenced block, all inside one blockquote with no blank line, indented three
spaces under its numbered list item. Use the badge URLs verbatim and keep the alt text `Static Badge`.

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

## Workflow safety

- Use least-privilege `permissions` in every workflow.
- Keep template/copy bootstrap workflows from overwriting learner or maintainer edits after the first setup run.
- Avoid hardcoded repository-owner URLs in source content; render repository-specific links at runtime where possible.
- If a workflow posts issue comments, keep comment markers stable so feedback can be updated instead of duplicated.

## Review mindset

Before considering an exercise ready, verify:

- The start path works in a newly created repository.
- Every step has a Theory block with real content and at least one activity, and every activity has its own
  `Having trouble? 🤷` block.
- Each step tells the learner what to do, why it matters, and how to recover from common mistakes.
- Validation fails helpfully before it passes.
- Completion closes or marks the learning loop clearly.
- No placeholder text remains anywhere in `README.md` or `.github/`: not only `replace-me`, but bare
  skeleton tokens (`OWNER`, `REPO`, `ORG`, `TITLE`, `FEATURE`, `VISIBILITY`) and bracketed slots such as
  `[Step name]`.
- Images, links, and code snippets render correctly in GitHub.
- The README Copy Exercise badge uses the correct `template_owner` and `template_name`, and the README ends
  with the `&copy;` footer.
