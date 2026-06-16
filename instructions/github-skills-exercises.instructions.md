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

## Step and workflow patterns

- For each step, keep `Theory` concise and directly tied to the `Activity`.
- Activity instructions should be numbered, action-oriented, and resilient to common mistakes.
- For transitions, define both the GitHub event trigger and the grading/feedback check.
- Prefer step workflow shape: `find_exercise`, optional `check_step_work`, then `post_next_step_content`.
- If a grading job exists, gate transition on it and return actionable feedback on failure.

## Workflow safety

- Use least-privilege `permissions` in every workflow.
- Keep template/copy bootstrap workflows from overwriting learner or maintainer edits after the first setup run.
- Avoid hardcoded repository-owner URLs in source content; render repository-specific links at runtime where possible.
- If a workflow posts issue comments, keep comment markers stable so feedback can be updated instead of duplicated.

## Review mindset

Before considering an exercise ready, verify:

- The start path works in a newly created repository.
- Each step tells the learner what to do, why it matters, and how to recover from common mistakes.
- Validation fails helpfully before it passes.
- Completion closes or marks the learning loop clearly.
- Images, links, and code snippets render correctly in GitHub.
