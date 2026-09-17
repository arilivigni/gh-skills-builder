# GitHub Skills exercise template contract

This is the concrete contract implemented by [`skills/exercise-template`](https://github.com/skills/exercise-template)
and [`skills/exercise-toolkit`](https://github.com/skills/exercise-toolkit). Treat it as the default shape for
a new exercise. Follow an existing repository's conventions instead only when that repository intentionally
diverges, and say so when you do.

## Canonical file set

```text
README.md
LICENSE
.gitignore
.github/images/                      # exercise images, referenced relatively from steps
.github/steps/1-step.md
.github/steps/2-step.md
.github/steps/3-step.md
.github/steps/x-review.md            # note: "x-", not a number
.github/workflows/0-start-exercise.yml
.github/workflows/1-step.yml
.github/workflows/2-step.yml
.github/workflows/3-last-step.yml    # note: "-last-step", not "-step"
```

## Naming invariants

| Concept | Rule |
| --- | --- |
| Step content | `.github/steps/N-step.md` |
| Step workflow | `.github/workflows/N-step.yml` |
| Workflow name | `name: Step N` |
| Start workflow | `.github/workflows/0-start-exercise.yml` with `name: Step 0` |
| Final workflow | `.github/workflows/N-last-step.yml`, still named `Step N` |
| Review content | `.github/steps/x-review.md` (no number) |

Additional invariants:

- Workflow `Step N` posts the content for step `N+1`. `Step 0` posts step 1.
- The final step workflow posts `x-review.md` and finishes the exercise. It does not enable another step.
- Every `gh workflow enable "Step N"` must name a workflow that exists.
- Every `STEP_N_FILE` / `REVIEW_FILE` env value must point at a file that exists.

## exercise-toolkit version

**Default: `v0.9.3`.** This is the latest published release and the version used in every skeleton below.

At exercise creation time, check whether a newer release exists and ask the user whether to adopt it. Do not
silently upgrade, and do not silently stay behind.

> ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
>
> ```bash
> # Latest PUBLISHED release (excludes drafts and prereleases)
> gh api repos/skills/exercise-toolkit/releases/latest --jq .tag_name
>
> # Confirm the tag actually exists before pinning it
> gh api repos/skills/exercise-toolkit/git/ref/tags/TAG --jq .ref
> ```

If the latest published release is newer than the default, ask the user:

> The exercise-toolkit default is `v0.9.3`, but `<newer tag>` is now available.
> Do you want to build this exercise against `<newer tag>` instead?

Apply the user's answer to every toolkit reference in the repository.

> [!WARNING]
> Never pin a draft or prerelease. A draft release is visible through the releases API to users with
> repository access, but **its git tag does not exist**, so `uses: ...@<tag>` fails to resolve and every
> workflow in the exercise breaks. `v0.9.4` is currently a draft with no tag, which is why the default is
> `v0.9.3`. Always confirm a tag resolves before pinning it.

Rules:

- `v0.9.x` is the known-good line. `skills/exercise-template` itself still pins `v0.9.1`.
- Never mix refs. The same tag must appear in every `uses: skills/exercise-toolkit/...@<ref>` and in every
  `actions/checkout` of `skills/exercise-toolkit`.
- Always pin a tag that exists. Never use `@main`.

## Reusable workflows

| Workflow | Inputs | Outputs |
| --- | --- | --- |
| `skills/exercise-toolkit/.github/workflows/start-exercise.yml` | `exercise-title` (required), `intro-message` (required), `issue-title-prefix` (optional) | `issue-number`, `issue-url` |
| `skills/exercise-toolkit/.github/workflows/find-exercise-issue.yml` | `issue-title-text` (optional) | `issue-number`, `issue-url` |
| `skills/exercise-toolkit/.github/workflows/finish-exercise.yml` | `issue-url` (required), `exercise-title` (optional), `update-readme-with-congratulations` (optional, boolean) | none |

Verified against `v0.9.3`. If you pin a different tag, re-read the `workflow_call` block of each workflow
rather than assuming these signatures still hold.

## Toolkit actions

| Action | Use |
| --- | --- |
| `skills/exercise-toolkit/actions/file-exists` | assert a learner created or kept a file |
| `skills/exercise-toolkit/actions/wait-for-workflow` | wait for a learner-triggered workflow to settle |
| `skills/exercise-toolkit/actions/repository-elapsed-time` | time-based checks |
| `skills/action-keyphrase-checker@v1` | assert a file contains expected content |

## Toolkit markdown templates

These live in the toolkit and are consumed by checking the toolkit out into the workspace. Do **not** copy
them into the exercise repository.

| Template | Use |
| --- | --- |
| `markdown-templates/step-feedback/watching-for-progress.md` | posted after step content so the learner knows automation is watching |
| `markdown-templates/step-feedback/checking-work.md` | replaces the last comment while a grading job runs |
| `markdown-templates/step-feedback/step-results-table.md` | replaces the checking comment with pass/fail results |
| `markdown-templates/step-feedback/step-finished-prepare-next-step.md` | transition message before the next step content |
| `markdown-templates/step-feedback/step-mistake.md` | targeted recovery feedback |
| `markdown-templates/step-feedback/lesson-review.md` | transition message before the review content |
| `markdown-templates/step-feedback/welcome.md` | exercise welcome copy |
| `markdown-templates/step-feedback/exercise-finished.md` | completion copy |
| `markdown-templates/readme/exercise-started.md` | README state when the exercise is running |
| `markdown-templates/readme/exercise-finished.md` | README state when the exercise is complete |

Create a local `.github/markdown-templates/` directory only for exercise-specific copy that has no toolkit
equivalent.

## Third-party action pins

| Action | Pin | Use |
| --- | --- | --- |
| `actions/checkout` | `v6` | checkout repo and toolkit |
| `GrantBirki/comment` | `v2.1.1` | create or replace issue comments from a Markdown file, with `vars` |
| `peter-evans/find-comment` | `v4` | locate the comment a grading job should replace |

## Permissions matrix

Grant permissions **per job**, not workflow-wide. A workflow-level `permissions:` block applies to every job
in the file, so a single `actions: write` there hands workflow-mutation authority to the learner-triggered
grading job as well. Set `permissions: {}` at the workflow level and grant each job only what it uses.

| Workflow | Job | `contents` | `actions` | `issues` | Why |
| --- | --- | --- | --- | --- | --- |
| `0-start-exercise.yml` | `start_exercise` | `write` | `write` | `write` | `start-exercise.yml` commits the README and disables workflows |
| | `post_next_step_content` | `read` | `write` | `write` | checkout, comment, enable `Step 1` |
| `N-step.yml` | `find_exercise` | — | — | `read` | locate the exercise issue |
| | `check_step_work` | `read` | **none** | `write` | reads files and posts comments; never toggles workflows |
| | `post_next_step_content` | `read` | `write` | `write` | checkout, comment, disable self and enable next |
| `N-last-step.yml` | `find_exercise` | — | — | `read` | locate the exercise issue |
| | `post_review_content` | `read` | `write` | `write` | checkout, comment, disable self |
| | `finish_exercise` | `write` | — | `write` | `finish-exercise.yml` commits the congratulations update |

> [!IMPORTANT]
> The grading job is the one to watch. It runs on learner-controlled triggers, so it must not hold
> `actions: write` (it would be able to enable or disable any workflow, including skipping ahead) and it must
> not hold `contents: write` unless that specific grader actually commits. Reading files and posting issue
> comments needs neither.

## Workflow chaining rules

- On a fresh copy, only `Step 0` is enabled. Every other step workflow ships disabled.
- Each intermediate step workflow ends by disabling itself and enabling the next one:

  ```yaml
  - name: Disable current workflow and enable next one
    run: |
      gh workflow disable "${{github.workflow}}"
      gh workflow enable "Step 2"
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

- The final step workflow only disables itself.
- `Step 0` is guarded so it does not run in the template itself:

  ```yaml
  jobs:
    start_exercise:
      if: |
        !github.event.repository.is_template
  ```

  That guard is separate from how `Step 0` gets disabled. `Step 0` contains no `gh workflow disable` of its
  own; the disabling happens inside the reusable workflow. `start-exercise.yml@v0.9.3` runs a
  `disable_workflows` job that disables **every** workflow whose filename begins with a digit, including
  `0-start-exercise.yml` itself, before `post_next_step_content` enables `Step 1`.

  So the state after a learner copies the exercise is: all numbered workflows disabled by the reusable
  workflow, then `Step 1` re-enabled by the start workflow's own final step. The exercise does not rely on
  the copied repository shipping with a particular enabled/disabled state for steps 1 and later.

- Step workflows default to `workflow_dispatch` with the real learner trigger left commented out for the
  author to choose. Uncomment and scope the trigger to the step's actual learner action. Prefer `paths`
  filters on `push` triggers so unrelated commits do not advance the exercise.

> [!IMPORTANT]
> The start workflow is the exception: it must have a real first-run trigger enabled before publishing.
> The README tells the learner to copy the repository and wait about 20 seconds for the first lesson. If
> `0-start-exercise.yml` ships with only `workflow_dispatch`, nothing creates the welcome issue and the
> learner is stuck on a repository that appears broken. Either enable the `push` trigger (with the repository
> marked as a template, plus the `is_template` job guard), or change the README to tell the learner to run
> the workflow manually. Do not ship the advertised automatic start with no event behind it.

## Workflow skeletons

### `0-start-exercise.yml`

```yaml
name: Step 0 # Start Exercise

on:
  workflow_dispatch:
  # Required for the advertised "copy the repo and wait ~20 seconds" start path.
  # Uncomment before publishing, and make the repository a template first so the
  # workflow does not run in the template itself. The `start_exercise` job is
  # additionally guarded with `!github.event.repository.is_template` below.
  push:
    branches:
      - main

# Least privilege: grant permissions per job, not workflow-wide, so a job only
# holds the scopes it uses. `permissions: {}` here means "no default".
permissions: {}

env:
  STEP_1_FILE: ".github/steps/1-step.md"

jobs:
  start_exercise:
    if: |
      !github.event.repository.is_template
    name: Start Exercise
    permissions:
      contents: write # start-exercise.yml commits the README update
      actions: write # start-exercise.yml disables workflows
      issues: write # create the exercise issue
    uses: skills/exercise-toolkit/.github/workflows/start-exercise.yml@v0.9.3
    with:
      exercise-title: "(replace-me: Exercise title)"
      intro-message: "(replace-me: One line introduction message for the exercise)"

  post_next_step_content:
    name: Post next step content
    runs-on: ubuntu-latest
    needs: [start_exercise]
    permissions:
      contents: read # checkout step content
      actions: write # enable the next step workflow
      issues: write # post step content and progress comments
    env:
      ISSUE_NUMBER: ${{ needs.start_exercise.outputs.issue-number }}
      ISSUE_REPOSITORY: ${{ github.repository }}
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          ref: main

      - name: Get response templates
        uses: actions/checkout@v6
        with:
          repository: skills/exercise-toolkit
          path: exercise-toolkit
          ref: v0.9.3

      - name: Create comment - add step content
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: ${{ env.STEP_1_FILE }}
          vars: |
            login: ${{ github.actor }}
            full_repo_name: ${{ github.repository }}

      - name: Create comment - watching for progress
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: exercise-toolkit/markdown-templates/step-feedback/watching-for-progress.md

      - name: Enable next step workflow
        run: gh workflow enable "Step 1"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### `N-step.yml` with a grading job

```yaml
name: Step 2

on:
  workflow_dispatch:
  # Choose the trigger that matches this step's learner action.
  # pull_request:
  #   branches:
  #     - main
  #   types:
  #     - closed

# Least privilege: grant permissions per job, not workflow-wide. Only the job
# that toggles workflows gets `actions: write`; the learner-triggered grading
# job must not be able to mutate workflow state.
permissions: {}

env:
  STEP_3_FILE: ".github/steps/3-step.md"

jobs:
  find_exercise:
    name: Find Exercise Issue
    permissions:
      issues: read # locate the exercise issue
    uses: skills/exercise-toolkit/.github/workflows/find-exercise-issue.yml@v0.9.3

  # Optional "grading job". Remove it if this step is not graded.
  check_step_work:
    name: Check step work
    runs-on: ubuntu-latest
    needs: [find_exercise]
    permissions:
      contents: read # read the learner's files; raise to write only if your grader commits
      issues: write # post and update the feedback comment
      # No actions: write. Grading must not be able to enable or disable workflows.
    env:
      ISSUE_REPOSITORY: ${{ github.repository }}
      ISSUE_NUMBER: ${{ needs.find_exercise.outputs.issue-number }}
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Get response templates
        uses: actions/checkout@v6
        with:
          repository: skills/exercise-toolkit
          path: exercise-toolkit
          ref: v0.9.3

      - name: Find last comment
        id: find-last-comment
        uses: peter-evans/find-comment@v4
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          # Never replace a comment that is not our own feedback comment.
          # Without these filters `direction: last` returns whatever was posted
          # most recently, which may be the learner, and `edit-mode: replace`
          # would then overwrite it.
          comment-author: "github-actions[bot]"
          body-includes: "watch your progress in the background"
          direction: last

      - name: Update comment - checking work
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          comment-id: ${{ steps.find-last-comment.outputs.comment-id }}
          file: exercise-toolkit/markdown-templates/step-feedback/checking-work.md
          edit-mode: replace

      # START: Check practical exercise

      - name: Check if README file exists
        id: check-file-exists
        continue-on-error: true
        uses: skills/exercise-toolkit/actions/file-exists@v0.9.3
        with:
          file: README.md

      - name: Check for keyphrase in README.md
        id: check-for-keyphrase
        continue-on-error: true
        uses: skills/action-keyphrase-checker@v1
        with:
          text-file: README.md
          keyphrase: Installation guide

      - name: Update comment - step results
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          comment-id: ${{ steps.find-last-comment.outputs.comment-id }}
          edit-mode: replace
          file: exercise-toolkit/markdown-templates/step-feedback/step-results-table.md
          vars: |
            step_number: 2
            results_table:
              - description: "Checked if README.md file exists"
                passed: ${{ steps.check-file-exists.outcome == 'success' }}
              - description: "Checked for Installation guide in README.md"
                passed: ${{ steps.check-for-keyphrase.outcome == 'success' }}

      # END: Check practical exercise

      - name: Fail job if not all checks passed
        if: contains(steps.*.outcome, 'failure')
        run: exit 1

  post_next_step_content:
    name: Post next step content
    needs: [find_exercise, check_step_work]
    runs-on: ubuntu-latest
    permissions:
      contents: read # checkout step content
      actions: write # disable this step and enable the next one
      issues: write # post step content and progress comments
    env:
      ISSUE_REPOSITORY: ${{ github.repository }}
      ISSUE_NUMBER: ${{ needs.find_exercise.outputs.issue-number }}
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Get response templates
        uses: actions/checkout@v6
        with:
          repository: skills/exercise-toolkit
          path: exercise-toolkit
          ref: v0.9.3

      - name: Create comment - step finished
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: exercise-toolkit/markdown-templates/step-feedback/step-finished-prepare-next-step.md
          vars: |
            next_step_number: 3

      - name: Create comment - add step content
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: ${{ env.STEP_3_FILE }}

      - name: Create comment - watching for progress
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: exercise-toolkit/markdown-templates/step-feedback/watching-for-progress.md

      - name: Disable current workflow and enable next one
        run: |
          gh workflow disable "${{github.workflow}}"
          gh workflow enable "Step 3"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Grading job rules:

- Every check step sets `continue-on-error: true` and a stable `id`.
- Every check `id` appears as a row in the `results_table` with a learner-readable `description`.
- The job ends with `Fail job if not all checks passed` using `contains(steps.*.outcome, 'failure')`.
- When `check_step_work` exists, `post_next_step_content.needs` must include it. When it is removed, the
  `needs` list must be reduced back to `[find_exercise]`.

> [!WARNING]
> Getting this wrong silently disables grading. If `check_step_work` runs but is not in
> `post_next_step_content.needs`, the two jobs run in parallel and the learner is advanced to the next step
> even when the grading job fails. The exercise looks like it validates work but does not. The upstream
> `skills/exercise-template` ships `2-step.yml` in exactly this state, with the correct wiring left as a
> comment for the author to apply, so it is easy to inherit by accident. The pre-handoff checks below
> detect it.

### `N-last-step.yml`

```yaml
name: Step 3 # Last step of the exercise

on:
  workflow_dispatch:

# Least privilege: grant permissions per job, not workflow-wide.
permissions: {}

env:
  REVIEW_FILE: ".github/steps/x-review.md"

jobs:
  find_exercise:
    name: Find Exercise Issue
    permissions:
      issues: read # locate the exercise issue
    uses: skills/exercise-toolkit/.github/workflows/find-exercise-issue.yml@v0.9.3

  post_review_content:
    name: Post review content
    needs: [find_exercise]
    runs-on: ubuntu-latest
    permissions:
      contents: read # checkout review content
      actions: write # disable this final workflow
      issues: write # post the review comments
    env:
      ISSUE_REPOSITORY: ${{ github.repository }}
      ISSUE_NUMBER: ${{ needs.find_exercise.outputs.issue-number }}
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Get response templates
        uses: actions/checkout@v6
        with:
          repository: skills/exercise-toolkit
          path: exercise-toolkit
          ref: v0.9.3

      - name: Create comment - step finished - final review next
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: exercise-toolkit/markdown-templates/step-feedback/lesson-review.md

      - name: Create comment - add review content
        uses: GrantBirki/comment@v2.1.1
        with:
          repository: ${{ env.ISSUE_REPOSITORY }}
          issue-number: ${{ env.ISSUE_NUMBER }}
          file: ${{ env.REVIEW_FILE }}

      - name: Disable current workflow
        run: gh workflow disable "${{github.workflow}}"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  finish_exercise:
    name: Finish Exercise
    needs: [find_exercise, post_review_content]
    permissions:
      contents: write # finish-exercise.yml commits the README congratulations update
      issues: write # close out the exercise issue
    uses: skills/exercise-toolkit/.github/workflows/finish-exercise.yml@v0.9.3
    with:
      issue-url: ${{ needs.find_exercise.outputs.issue-url }}
      exercise-title: "(replace-me: Exercise title)"
```

## README skeleton

```markdown
# (replace-me: Exercise title)

_(replace-me: One-line description of the exercise)_

## Welcome

- **Who is this for**: (replace-me: Target audience description)
- **What you'll learn**: (replace-me: Learning objectives)
- **What you'll build**: (replace-me: Description of what the learner will create)
- **Prerequisites**:
  - (replace-me: Prerequisite skill or exercise)
  - (replace-me: Other prerequisites)

- **How long**: This exercise takes less than (replace-me: 30) minutes to complete.

In this exercise, you will:

1. (replace-me: Learning objective step #1)
1. (replace-me: Learning objective step #2)
1. (replace-me: Learning objective step #N)

### How to start this exercise

Simply copy the exercise to your account, then give your favorite Octocat (Mona) **about 20 seconds** to prepare the first lesson, then **refresh the page**.

[![](https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/new?template_owner=OWNER&template_name=REPO&owner=%40me&name=skills-REPO&description=Exercise:+TITLE&visibility=public)

<details>
<summary>Having trouble? 🤷</summary><br/>

When copying the exercise, we recommend the following settings:

- For owner, choose your personal account or an organization to host the repository.

- We recommend creating a public repository, since private repositories will use Actions minutes.

If the exercise isn't ready in 20 seconds, please check the [Actions](../../actions) tab.

- Check to see if a job is running. Sometimes it simply takes a bit longer.

- If the page shows a failed job, please submit an issue. Nice, you found a bug! 🐛

</details>
```

The Copy Exercise badge URL must use the real `template_owner` and `template_name` of the published
repository. Re-check it after any repository transfer.

## Template slots

Every slot an author must fill is marked with the `(replace-me: ...)` sentinel, matching the convention in
`skills/exercise-template`. Keep it that way when you edit these skeletons.

A bare descriptive phrase such as `Exercise title` or `First instruction` reads as real content, so a
skeleton copied verbatim would sail past the no-placeholder gate and ship unusable learner content. One
sentinel keeps a single token sufficient to catch every unfilled slot.

## Step skeleton (`N-step.md`)

Every step file must contain exactly one `### 📖 Theory:` heading with real content and at least one
`### ⌨️ Activity:` heading with numbered instructions.

```markdown
## Step 1: (replace-me: Step name)

(replace-me: Brief story or scenario to introduce the step)

### 📖 Theory: (replace-me: Theory title)

(replace-me: Awareness-level background that directly supports the activity below. Two to five sentences.)

> [!NOTE]
> (replace-me: Optional note relevant to this section)

### ⌨️ Activity: (replace-me: Activity title)

1. (replace-me: First instruction)

   Indent any multiline instruction content so the ordered list keeps numbering.

1. (replace-me: Second instruction)

1. (replace-me: Additional instructions as needed)

<details>
<summary>Having trouble? 🤷</summary><br/>

- (replace-me: Troubleshooting tip or hint)
- (replace-me: Additional troubleshooting tips as needed)

</details>
```

## Activity block conventions

Inside an `⌨️ Activity`, every Copilot prompt and every terminal command uses a badge-led blockquote. The
badge line comes first, then a bare `>` line, then the fenced block inside the same blockquote. Indent the
whole blockquote to align under its numbered list item.

Use the badge URLs verbatim. Do not restyle, recolor, or rename them. Keep the alt text `Static Badge`.

### Copilot Chat / IDE prompt

```markdown
1. Ask Copilot Chat to summarize the change.

   > ![Static Badge](https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple)
   >
   > ```text
   > Summarize the changes in this pull request.
   > ```
```

### Copilot CLI prompt

```markdown
1. Run the prompt with Copilot CLI.

   > ![Static Badge](https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff)
   >
   > ```text
   > Explain what this workflow does.
   > ```
```

### Terminal command

```markdown
1. Run the command.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > gh repo view
   > ```
```

## Review skeleton (`x-review.md`)

```markdown
## Review

_Congratulations, you've completed this exercise and learned a lot about (replace-me: FEATURE)._

<img src="https://octodex.github.com/images/jetpacktocat.png" alt="celebrate" width=200 align=right>

Here's a recap of your accomplishments:

- (replace-me: Accomplishment #1)
- (replace-me: Accomplishment #N)

### What's next?

- (replace-me: Natural follow-up Skills exercise, if there is one)
- (replace-me: Documentation link to learn more about the feature)
- (replace-me: Other resources or calls to action)
```

## Images and callouts

- Store exercise images in `.github/images/` and reference them relatively from step files, for example
  `<img width="200" alt="descriptive alt text" src="../images/inspectocat.png" />`.
- Always provide meaningful alt text.
- Keep `[!NOTE]`, `[!IMPORTANT]`, `[!TIP]`, `[!WARNING]`, and `[!CAUTION]` callouts left-justified when they
  are not nested inside a list item.

## Pre-handoff checks

Run these before reporting the bootstrap complete:

> ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
>
> ```bash
> set -euo pipefail
> # No placeholder text left behind. The skeletons in this reference use
> # `replace-me` plus bare tokens (OWNER, REPO, TITLE, FEATURE, ORG) and
> # bracketed slots such as [Step name], so check the whole set, not just one.
> python3 - <<'PY'
> import re, sys
> from pathlib import Path
>
> TOKENS = [
>     r"replace-me",
>     r"\bOWNER\b", r"\bREPO\b", r"\bORG\b", r"\bTITLE\b", r"\bFEATURE\b",
>     r"\bVISIBILITY\b", r"\bSOURCE_ORG\b", r"\bDEST_ORG\b",
>     r"\[(?:Step name|Action|Exercise title|Theory title|Activity title)\]",
>     r"Accomplishment #\d", r"Learning objective step #",
> ]
> pattern = re.compile("|".join(TOKENS))
>
> targets = [Path("README.md")] + [p for p in Path(".github").rglob("*")
>                                  if p.is_file() and p.suffix in {".md", ".yml", ".yaml"}]
> problems = []
> for path in sorted(targets):
>     if not path.exists():
>         continue
>     for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
>         found = pattern.search(line)
>         if found:
>             problems.append(f"{path}:{number}: placeholder {found.group(0)!r}")
>
> if problems:
>     sys.exit("\n".join(problems))
> print("no placeholders")
> PY
>
> # Structural audit: required files exist, at least one step exists, step files
> # and step workflows line up by number, each workflow's declared name matches
> # its filename number, the last step is an N-last-step.yml that posts the
> # review, referenced content files exist, enable targets exist, and grading
> # jobs are wired into needs in both directions.
> python3 - <<'PY'
> import re, sys, yaml
> from pathlib import Path
>
> problems = []
> steps = Path(".github/steps")
> flows = Path(".github/workflows")
>
> for required in (Path("README.md"), steps / "x-review.md", flows / "0-start-exercise.yml"):
>     if not required.exists():
>         problems.append(f"missing required file: {required}")
>
> step_numbers = {int(m.group(1)) for p in steps.glob("*-step.md")
>                 if (m := re.fullmatch(r"(\d+)-step\.md", p.name))}
> if not step_numbers:
>     problems.append("no numbered step files found in .github/steps")
>
> workflow_numbers, names, last_steps, enables = {}, {}, [], []
>
> for path in sorted(flows.glob("*.yml")):
>     text = path.read_text(encoding="utf-8")
>     document = yaml.safe_load(text) or {}
>
>     declared = str(document.get("name", "")).strip()
>     if declared:
>         # Duplicate names make `gh workflow enable "Step N"` ambiguous, so the
>         # chain can select the wrong file and skip the review.
>         if declared in names:
>             problems.append(f"{path}: declares name {declared!r}, already declared by {names[declared]}")
>         names[declared] = path
>
>     number = re.match(r"(\d+)-", path.name)
>     if number:
>         value = int(number.group(1))
>         if declared != f"Step {value}":
>             problems.append(f"{path}: declares name {declared!r}, expected 'Step {value}'")
>         if value > 0:
>             if value in workflow_numbers:
>                 problems.append(f"{path}: duplicates step number {value} with {workflow_numbers[value]}")
>             workflow_numbers[value] = path
>     if re.fullmatch(r"\d+-last-step\.yml", path.name):
>         last_steps.append(path)
>
>     # A referenced file that merely exists is not enough: STEP_N_FILE must be
>     # step N's own content, and REVIEW_FILE must be the review page.
>     for key, target in re.findall(r"^\s*(STEP_\d+_FILE|REVIEW_FILE):\s*[\"\']?([^\"\'\n]+)", text, re.MULTILINE):
>         target = target.strip()
>         if not Path(target).exists():
>             problems.append(f"{path}: references missing file {target}")
>             continue
>         if key == "REVIEW_FILE":
>             if target != ".github/steps/x-review.md":
>                 problems.append(f"{path}: REVIEW_FILE is {target}, expected .github/steps/x-review.md")
>         else:
>             expected = ".github/steps/" + key.split("_")[1] + "-step.md"
>             if target != expected:
>                 problems.append(f"{path}: {key} is {target}, expected {expected}")
>
>     enables += [(path, name) for name in re.findall(r'gh workflow enable\s+"([^"]+)"', text)]
>
>     jobs = document.get("jobs") or {}
>     has_grading = "check_step_work" in jobs
>     for job_name, job in jobs.items():
>         if job_name in {"find_exercise", "check_step_work"}:
>             continue
>         needs = (job or {}).get("needs") or []
>         needs = [needs] if isinstance(needs, str) else list(needs)
>         if has_grading and "check_step_work" not in needs:
>             problems.append(f"{path}: job '{job_name}' does not need check_step_work, so grading cannot gate it")
>         if not has_grading and "check_step_work" in needs:
>             problems.append(f"{path}: job '{job_name}' needs check_step_work, but no such job exists")
>
>     # Least privilege: a workflow-level grant reaches every job, and the
>     # learner-triggered grading job must not be able to toggle workflows.
>     # Require the explicit empty mapping: an absent key inherits the
>     # repository default token scopes rather than granting nothing.
>     if document.get("permissions") != {}:
>         problems.append(f"{path}: must set workflow-level 'permissions: {{}}' and grant per job")
>     for job_name, job in jobs.items():
>         if (job or {}).get("permissions") is None:
>             problems.append(f"{path}: job '{job_name}' has no permissions block")
>     grading = jobs.get("check_step_work") or {}
>     if grading:
>         granted = grading.get("permissions") or {}
>         if granted.get("actions") in {"write"}:
>             problems.append(f"{path}: check_step_work has actions: write; grading must not toggle workflows")
>         if granted.get("contents") == "write":
>             problems.append(f"{path}: check_step_work has contents: write; only grant it if the grader commits")
>
> for path, target in enables:
>     if target not in names:
>         problems.append(f"{path}: enables '{target}', which no workflow declares")
>
> missing_workflow = step_numbers - set(workflow_numbers)
> missing_step = set(workflow_numbers) - step_numbers
> if missing_workflow:
>     problems.append(f"step files with no matching workflow: {sorted(missing_workflow)}")
> if missing_step:
>     problems.append(f"step workflows with no matching step file: {sorted(missing_step)}")
>
> if len(last_steps) != 1:
>     problems.append(f"expected exactly one N-last-step.yml, found {[str(p) for p in last_steps]}")
> elif step_numbers:
>     final = max(step_numbers)
>     if not re.fullmatch(rf"{final}-last-step\.yml", last_steps[0].name):
>         problems.append(f"last step should be {final}-last-step.yml, found {last_steps[0].name}")
>     text = last_steps[0].read_text(encoding="utf-8")
>     if "REVIEW_FILE" not in text:
>         problems.append(f"{last_steps[0]}: final workflow does not reference REVIEW_FILE")
>     if re.search(r'gh workflow enable\s+"', text):
>         problems.append(f"{last_steps[0]}: final workflow should not enable another step")
>
> if problems:
>     sys.exit("\n".join(problems))
> print(f"structure OK: steps {sorted(step_numbers)}, workflows {sorted(workflow_numbers)}, last {last_steps[0].name}")
> PY
>
> # Every toolkit reference is the same release tag.
> # Covers both forms: `uses: skills/exercise-toolkit/...@<ref>` and the toolkit
> # `actions/checkout` `ref:` value. Any ref that is not vX.Y.Z (for example
> # `main` or a SHA) is reported as a failure. The detected tag is captured so
> # the next check does not need a hand-substituted value.
> TOOLKIT_REF="$(python3 - <<'PY'
> import pathlib, re, sys, yaml
>
> refs = {}
> def walk(node):
>     if isinstance(node, dict):
>         yield node
>         for value in node.values():
>             yield from walk(value)
>     elif isinstance(node, list):
>         for value in node:
>             yield from walk(value)
>
> for path in sorted(pathlib.Path(".github/workflows").glob("*.yml")):
>     for mapping in walk(yaml.safe_load(path.read_text(encoding="utf-8"))):
>         uses = mapping.get("uses")
>         if isinstance(uses, str) and uses.startswith("skills/exercise-toolkit"):
>             # A `uses:` with no `@ref` follows the toolkit default branch.
>             ref = uses.rsplit("@", 1)[1].strip() if "@" in uses else ""
>             refs.setdefault(ref or "(unpinned)", set()).add(str(path))
>         if mapping.get("repository") == "skills/exercise-toolkit":
>             # A checkout with no ref follows the toolkit default branch.
>             ref = mapping.get("ref")
>             ref = str(ref).strip() if ref is not None and str(ref).strip() else "(unpinned)"
>             refs.setdefault(ref, set()).add(str(path))
>
> bad = {r: f for r, f in refs.items() if not re.fullmatch(r"v\d+\.\d+\.\d+", r)}
> if bad:
>     sys.exit(f"non-tag toolkit refs: { {r: sorted(f) for r, f in bad.items()} }")
> if len(refs) > 1:
>     sys.exit(f"mixed toolkit refs: { {r: sorted(f) for r, f in refs.items()} }")
> if not refs:
>     sys.exit("no exercise-toolkit references found")
> # Print only the tag so the caller can reuse it.
> print(next(iter(refs)))
> PY
> )"
> echo "toolkit ref: $TOOLKIT_REF"
>
> # That tag actually exists. A draft release appears in the releases API but
> # has no git tag, so every `uses:` pinned to it fails to resolve.
> gh api "repos/skills/exercise-toolkit/git/ref/tags/$TOOLKIT_REF" --jq .ref
>
> # Every step file has exactly one non-empty Theory block and at least one
> # Activity block containing numbered instructions. Counting headings is not
> # enough: an empty Theory section or an Activity with no steps must fail.
> python3 - <<'PY'
> import re, sys
> from pathlib import Path
>
> THEORY = "### 📖 Theory:"
> ACTIVITY = "### ⌨️ Activity:"
> problems = []
>
> def sections(text, marker):
>     """Body text following each occurrence of marker, up to the next heading."""
>     bodies = []
>     for match in re.finditer(re.escape(marker) + r"[^\n]*\n", text):
>         rest = text[match.end():]
>         end = re.search(r"^#{1,3} ", rest, re.MULTILINE)
>         bodies.append(rest[: end.start()] if end else rest)
>     return bodies
>
> def meaningful(body):
>     """Strip HTML comments, standalone images and blank lines."""
>     body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
>     body = re.sub(r"^\s*<img[^>]*>\s*$", "", body, flags=re.MULTILINE)
>     return [line for line in (l.strip() for l in body.splitlines()) if line]
>
> for path in sorted(Path(".github/steps").glob("*-step.md")):
>     text = path.read_text(encoding="utf-8")
>
>     theory_bodies = sections(text, THEORY)
>     if len(theory_bodies) != 1:
>         problems.append(f"{path}: expected exactly 1 Theory block, found {len(theory_bodies)}")
>     elif not meaningful(theory_bodies[0]):
>         problems.append(f"{path}: Theory block has no content")
>
>     activity_bodies = sections(text, ACTIVITY)
>     if not activity_bodies:
>         problems.append(f"{path}: no Activity block")
>     else:
>         for index, body in enumerate(activity_bodies, 1):
>             if not re.search(r"^\s*\d+\.\s+\S", body, re.MULTILINE):
>                 problems.append(f"{path}: Activity block {index} has no numbered instructions")
>
> if problems:
>     sys.exit("\n".join(problems))
> print("step content OK")
> PY
>
> # Workflows parse
> if command -v actionlint >/dev/null 2>&1; then
>   actionlint
> else
>   python3 -c "import sys,yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"
> fi
> ```
