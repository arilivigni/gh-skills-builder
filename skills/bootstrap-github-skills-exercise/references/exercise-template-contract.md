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

| Workflow | `contents` | `actions` | `issues` |
| --- | --- | --- | --- |
| `0-start-exercise.yml` | `write` | `write` | `write` |
| `N-step.yml` without grading | `read` | `write` | `write` |
| `N-step.yml` with grading that needs repo state | `write` | `write` | `write` |
| `N-last-step.yml` | `write` | `write` | `write` |

`actions: write` is required because every step workflow enables and disables sibling workflows.

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
- `Step 0` does not disable itself; it is guarded instead:

  ```yaml
  jobs:
    start_exercise:
      if: |
        !github.event.repository.is_template
  ```

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

permissions:
  contents: write
  actions: write
  issues: write

env:
  STEP_1_FILE: ".github/steps/1-step.md"

jobs:
  start_exercise:
    if: |
      !github.event.repository.is_template
    name: Start Exercise
    uses: skills/exercise-toolkit/.github/workflows/start-exercise.yml@v0.9.3
    with:
      exercise-title: "Exercise title"
      intro-message: "One line introduction message for the exercise"

  post_next_step_content:
    name: Post next step content
    runs-on: ubuntu-latest
    needs: [start_exercise]
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

permissions:
  contents: write
  actions: write
  issues: write

env:
  STEP_3_FILE: ".github/steps/3-step.md"

jobs:
  find_exercise:
    name: Find Exercise Issue
    uses: skills/exercise-toolkit/.github/workflows/find-exercise-issue.yml@v0.9.3

  # Optional "grading job". Remove it if this step is not graded.
  check_step_work:
    name: Check step work
    runs-on: ubuntu-latest
    needs: [find_exercise]
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

### `N-last-step.yml`

```yaml
name: Step 3 # Last step of the exercise

on:
  workflow_dispatch:

permissions:
  contents: write
  actions: write
  issues: write

env:
  REVIEW_FILE: ".github/steps/x-review.md"

jobs:
  find_exercise:
    name: Find Exercise Issue
    uses: skills/exercise-toolkit/.github/workflows/find-exercise-issue.yml@v0.9.3

  post_review_content:
    name: Post review content
    needs: [find_exercise]
    runs-on: ubuntu-latest
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
    uses: skills/exercise-toolkit/.github/workflows/finish-exercise.yml@v0.9.3
    with:
      issue-url: ${{ needs.find_exercise.outputs.issue-url }}
      exercise-title: "Exercise title"
```

## README skeleton

```markdown
# Exercise title

_One-line description of the exercise_

## Welcome

- **Who is this for**: Target audience description
- **What you'll learn**: Learning objectives
- **What you'll build**: Description of what the learner will create
- **Prerequisites**:
  - Prerequisite skill or exercise
  - Other prerequisites

- **How long**: This exercise takes less than 30 minutes to complete.

In this exercise, you will:

1. Learning objective step #1
1. Learning objective step #2
1. Learning objective step #N

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

## Step skeleton (`N-step.md`)

Every step file must contain exactly one `### 📖 Theory:` heading with real content and at least one
`### ⌨️ Activity:` heading with numbered instructions.

```markdown
## Step 1: Step name

Brief story or scenario to introduce the step.

### 📖 Theory: Theory title

Awareness-level background that directly supports the activity below. Two to five sentences.

> [!NOTE]
> Optional note relevant to this section.

### ⌨️ Activity: Activity title

1. First instruction.

   Indent any multiline instruction content so the ordered list keeps numbering.

1. Second instruction.

1. Additional instructions as needed.

<details>
<summary>Having trouble? 🤷</summary><br/>

- Troubleshooting tip or hint
- Additional troubleshooting tips as needed

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

_Congratulations, you've completed this exercise and learned a lot about FEATURE._

<img src="https://octodex.github.com/images/jetpacktocat.png" alt="celebrate" width=200 align=right>

Here's a recap of your accomplishments:

- Accomplishment #1
- Accomplishment #N

### What's next?

- Natural follow-up Skills exercise, if there is one
- Documentation link to learn more about the feature
- Other resources or calls to action
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
> # No placeholder text left behind
> if grep -Rni "replace-me" README.md .github/; then
>   echo "placeholder text found" >&2
>   exit 1
> else
>   status=$?
>   if [ "$status" -ne 1 ]; then exit "$status"; fi
>   echo "no placeholders"
> fi
>
> # Step content and step workflows line up
> ls .github/steps/ .github/workflows/
>
> # Every toolkit reference is the same release tag.
> # Covers both forms: `uses: skills/exercise-toolkit/...@<ref>` and the toolkit
> # `actions/checkout` `ref:` value. Any ref that is not vX.Y.Z (for example
> # `main` or a SHA) is reported as a failure.
> python3 - <<'PY'
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
>         if isinstance(uses, str) and uses.startswith("skills/exercise-toolkit") and "@" in uses:
>             refs.setdefault(uses.rsplit("@", 1)[1], set()).add(str(path))
>         if mapping.get("repository") == "skills/exercise-toolkit" and "ref" in mapping:
>             refs.setdefault(str(mapping["ref"]), set()).add(str(path))
>
> bad = {r: f for r, f in refs.items() if not re.fullmatch(r"v\d+\.\d+\.\d+", r)}
> if bad:
>     sys.exit(f"non-tag toolkit refs: { {r: sorted(f) for r, f in bad.items()} }")
> if len(refs) > 1:
>     sys.exit(f"mixed toolkit refs: { {r: sorted(f) for r, f in refs.items()} }")
> print("toolkit ref:", next(iter(refs), "none found"))
> PY
>
> # The pinned tag actually exists (drafts have no tag)
> gh api repos/skills/exercise-toolkit/git/ref/tags/TAG --jq .ref  # replace TAG with the selected repo-wide tag
>
> # Every step file has exactly one Theory block and at least one Activity block
> python3 - <<'PY'
> from pathlib import Path
> for path in sorted(Path(".github/steps").glob("*-step.md")):
>     text = path.read_text(encoding="utf-8")
>     theory = text.count("### 📖 Theory:")
>     activity = text.count("### ⌨️ Activity:")
>     if theory != 1 or activity < 1:
>         raise SystemExit(f"{path}: Theory={theory}, Activity={activity}")
> PY
>
> # Workflows parse
> if command -v actionlint >/dev/null 2>&1; then
>   actionlint
> else
>   python3 -c "import sys,yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"
> fi
> ```
