# GitHub Skills exercise template contract

This is the concrete contract implemented by [`skills/exercise-template`](https://github.com/skills/exercise-template)
and [`skills/exercise-toolkit`](https://github.com/skills/exercise-toolkit), refined by the published exercises
[`skills/idea-to-merge-with-the-copilot-app`](https://github.com/skills/idea-to-merge-with-the-copilot-app) and
[`skills/create-applications-with-the-copilot-CLI`](https://github.com/skills/create-applications-with-the-copilot-CLI).
Treat it as the default shape for a new exercise. Every place it differs from `exercise-template` is deliberate
and listed under [Deliberate divergences from exercise-template](#deliberate-divergences-from-exercise-template).
Follow an existing repository's conventions instead only when that repository intentionally diverges, and say
so when you do.

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
.github/workflows/3-step.yml         # final step: name "Step 3 # Last step of the exercise"
```

## Naming invariants

| Concept | Rule |
| --- | --- |
| Step content | `.github/steps/N-step.md`, opening with `## Step N: <title>` |
| Step workflow | `.github/workflows/N-step.yml` |
| Workflow name | `name: Step N` |
| Start workflow | `.github/workflows/0-start-exercise.yml` with `name: Step 0 # Start Exercise` |
| Final workflow | `.github/workflows/N-step.yml` for the highest `N`, with `name: Step N # Last step of the exercise` |
| Review content | `.github/steps/x-review.md` (no number) |

Additional invariants:

- Workflow `Step N` posts the content for step `N+1`. `Step 0` posts step 1.
- The final step workflow posts `x-review.md` and finishes the exercise. It does not enable another step.
- Only the final step workflow carries the `# Last step of the exercise` comment. YAML treats it as a comment,
  so the declared name is still `Step N` and `gh workflow enable "Step N"` resolves it like any other step.
- Do not use the `N-last-step.yml` filename from `exercise-template`. Every step workflow uses `N-step.yml`.
- Every `gh workflow enable "Step N"` must name a workflow that exists.
- Every `STEP_N_FILE` / `REVIEW_FILE` env value must point at a file that exists.

## Deliberate divergences from exercise-template

`skills/exercise-template` is the starting point, not a byte-for-byte target. Where the template is silent,
unsafe, or inconsistent with the published exercises, this contract follows the published exercises:

| Area | `exercise-template` | This contract | Why |
| --- | --- | --- | --- |
| Final workflow | `3-last-step.yml` | `N-step.yml` named `Step N # Last step of the exercise` | one filename pattern for every step, as in the published exercises |
| Permissions | workflow-level `permissions:` that include `actions: write` | `permissions: {}` plus per-job grants | the learner-triggered grading job must not hold `actions: write` |
| Start trigger | `push` commented out in `0-start-exercise.yml` | `push` enabled, guarded by `is_template` | the README promises an automatic start |
| Grading wiring | `post_next_step_content` ships `needs: [find_exercise]`, with the fix in a comment | `needs: [find_exercise, check_step_work]` whenever a grading job exists | otherwise grading never gates progress |
| Toolkit pin | `v0.9.1` | latest published tag, default `v0.9.3` | see [exercise-toolkit version](#exercise-toolkit-version) |
| Activities | one `### ⌨️ Activity:` per step | one unnumbered activity, or several numbered ones | see [Step and activity rules](#step-and-activity-rules) |
| Recovery hints | one `Having trouble? 🤷` block per step | one block after each activity | hints sit next to the work they support |
| Prompt and command blocks | none shown | badge-led blockquotes with `prompt` and `bash` fences | see [Activity block conventions](#activity-block-conventions) |
| README footer | none | `&copy;` line with Code of Conduct and license links | matches the published exercises |

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
| Intermediate `N-step.yml` | `find_exercise` | — | — | `read` | locate the exercise issue |
| | `check_step_work` | `read` | **none** | `write` | reads files and posts comments; never toggles workflows |
| | `post_next_step_content` | `read` | `write` | `write` | checkout, comment, disable self and enable next |
| Final `N-step.yml` | `find_exercise` | — | — | `read` | locate the exercise issue |
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
  # Required for the advertised "copy the repo and wait ~20 seconds" start path:
  # a learner's copy runs this workflow on its first push. exercise-template
  # ships this trigger commented out; exercises keep it enabled. Mark the
  # repository as a template before publishing so the `is_template` guard on
  # `start_exercise` stops the workflow from starting an exercise here.
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

### Intermediate `N-step.yml` with a grading job

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

### Final `N-step.yml`

The final step workflow keeps the `N-step.yml` filename. Only its `name:` line marks it as the last step: the
`# Last step of the exercise` comment is ignored by YAML, so the workflow is still `Step N` to the previous
step's `gh workflow enable "Step N"`.

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

---

&copy; (replace-me: year) (replace-me: copyright holder) &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)
```

### Copy Exercise badge rules

`### How to start this exercise` contains exactly one Copy Exercise badge. Copy it from
[`skills/exercise-template`'s README](https://github.com/skills/exercise-template/blob/main/README.md) and
change only the URL parameters:

| Part | Rule |
| --- | --- |
| Markup | `[![](IMAGE)](LINK)` on its own line, keeping the template's empty alt text |
| Image | `https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935`, unchanged |
| Link | `https://github.com/new?template_owner=OWNER&template_name=REPO&owner=%40me&name=skills-REPO&description=Exercise:+TITLE&visibility=public` |
| `template_owner` | the account that publishes the exercise, for example `skills` |
| `template_name` | the published repository name, spelled exactly as the repository spells it, including case |
| `owner` | `%40me`, so the learner's own account is preselected |
| `name` | `skills-` followed by the repository name |
| `description` | `Exercise:+` followed by the exercise title, with words joined by `+` |
| `visibility` | `public`, so the learner's copy does not use private Actions minutes. If the exercise itself is published as a private repository, publish switches this to `private`, so learners' copies do not expose its content |

Do not restyle the badge, add a second copy button, or keep the template's
`<!-- (replace-me: Make sure to edit the URL ...) -->` reminder comment. The placeholder scan in
[Pre-handoff checks](#pre-handoff-checks) fails while that comment or any `OWNER`, `REPO`, or `TITLE` token
remains.

The badge must use the real `template_owner` and `template_name` of the published repository. Re-check it
after any repository transfer.

`template_name` is the repository name approved in the outline's Exercise identity section, `name` is
`skills-` followed by that name, and `description` carries the approved title. Keep these aligned with
`.github/exercise-outline.md`; if the name changes at publish time, update the badge and the saved outline
together.

### README footer

End the README with a `---` rule and one footer line, as the published exercises do:

- `&copy;`, then the year and copyright holder from the repository's `LICENSE` copyright line. If that line
  has no year, use the year the exercise is first published.
- A [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md)
  link.
- A link that names the repository's actual license. Exercises ship the MIT license, linked as
  `[MIT License](https://gh.io/mit)`.
- `&bull;` between the parts. Exercise-specific credits, such as font attributions, can follow as extra
  `&bull;` parts.

## Template slots

Every slot an author must fill is marked with the `(replace-me: ...)` sentinel, matching the convention in
`skills/exercise-template`. Keep it that way when you edit these skeletons.

A bare descriptive phrase such as `Exercise title` or `First instruction` reads as real content, so a
skeleton copied verbatim would sail past the no-placeholder gate and ship unusable learner content. One
sentinel keeps a single token sufficient to catch every unfilled slot.

## Step and activity rules

Every `N-step.md` uses the same anatomy, in this order, so learners meet the same rhythm in every step of
every exercise:

1. `## Step N: <title>`, where `N` matches the filename number.
1. Optionally, a short story, scenario, or image that sets up the step.
1. Exactly one `### 📖 Theory: <title>` section with real content. Put supporting detail in `####`
   subsections under it, for example `#### References`, instead of adding more `###` sections.
1. One or more activities. Each is a `###` activity heading followed by numbered instructions.
1. A `Having trouble? 🤷` block directly after **each** activity, with hints for that activity only.

Activity headings:

| Activities in the step | Headings |
| --- | --- |
| One | `### ⌨️ Activity: <title>` |
| Two or more | `### ⌨️ Activity 1: <title>`, `### ⌨️ Activity 2: <title>`, and so on, numbered from 1 with no gaps |

- Never mix the two forms in one step, and never number a lone activity.
- Always use the ⌨️ emoji. Do not use the `:keyboard:` shortcode.
- Start a new activity when the learner switches tools or produces a separate result, for example prompting
  Copilot and then reviewing what it produced. Keep each activity a short sequence the learner can finish.
- Other `<details>` blocks, such as a stretch goal, can follow an activity's `Having trouble? 🤷` block. They
  never replace it.

Instructions:

- Number every list item `1.`. GitHub renders the sequence, so adding or removing an item never breaks it.
- Indent everything that belongs to an item by three spaces: extra paragraphs, images, callouts, code blocks,
  and badge-led blockquotes. A callout or blockquote at column 0 ends the list, and the next item restarts
  at 1.
- End the step's final activity with the action that triggers validation, such as committing a file or merging
  a pull request, followed by this instruction:

  ```text
  1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.
  ```

## Step skeleton (`N-step.md`)

Use this skeleton for a step with one activity. Every step file must contain exactly one `### 📖 Theory:`
heading with real content and at least one activity heading with numbered instructions.

```markdown
## Step 1: (replace-me: Step name)

(replace-me: Brief story or scenario to introduce the step)

### 📖 Theory: (replace-me: Theory title)

(replace-me: Awareness-level background that directly supports the activity below. Two to five sentences.)

> [!NOTE]
> (replace-me: Optional note relevant to this section)

### ⌨️ Activity: (replace-me: Activity title)

1. (replace-me: First instruction)

   (replace-me: Optional detail for this instruction, indented three spaces so the list keeps numbering)

1. (replace-me: Second instruction)

1. (replace-me: Additional instructions as needed)

1. (replace-me: Action that triggers validation, such as committing the file)

1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.

<details>
<summary>Having trouble? 🤷</summary><br/>

- (replace-me: Troubleshooting tip or hint)
- (replace-me: Additional troubleshooting tips as needed)

</details>
```

### Step with several activities

Number every activity and give each its own `Having trouble? 🤷` block. Only the final activity ends with the
validation trigger and the Mona instruction.

```markdown
## Step 2: (replace-me: Step name)

(replace-me: Brief story or scenario to introduce the step)

### 📖 Theory: (replace-me: Theory title)

(replace-me: Awareness-level background that directly supports the activities below. Two to five sentences.)

#### References

- (replace-me: Documentation link to learn more about the feature)

### ⌨️ Activity 1: (replace-me: Activity title)

1. (replace-me: First instruction)

   > ![Static Badge](https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple)
   >
   > ```prompt
   > (replace-me: Prompt the learner sends to Copilot)
   > ```

1. (replace-me: Second instruction)

<details>
<summary>Having trouble? 🤷</summary><br/>

- (replace-me: Troubleshooting tip or hint)

</details>

### ⌨️ Activity 2: (replace-me: Activity title)

1. (replace-me: First instruction)

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > (replace-me: Command the learner runs)
   > ```

1. (replace-me: Action that triggers validation, such as committing the file)

1. Wait a moment for Mona to check your work, provide feedback, and share the next lesson.

<details>
<summary>Having trouble? 🤷</summary><br/>

- (replace-me: Troubleshooting tip or hint)

</details>
```

## Activity block conventions

Inside an activity, every Copilot prompt and every terminal command uses a badge-led blockquote:

- The badge line comes first, then a bare `>` line, then the fenced block, all inside one blockquote. Never
  leave a blank line inside it: a blank line ends the blockquote and separates the badge from its block.
- Indent the whole blockquote three spaces so it sits under its numbered list item.
- Put exactly what the learner should send or run inside the fence. Explanations go in the list item, not
  in the fence.

Choose the badge by where the learner types the text:

| The learner types it into | Badge | Fence language |
| --- | --- | --- |
| Copilot Chat, the Copilot app, or an IDE | Prompt | `prompt` |
| A Copilot CLI session, including slash commands such as `/login` | CLI Prompt | `prompt` |
| A shell, including the command that starts a Copilot CLI session | Terminal | `bash` |

Use the badge URLs verbatim. Do not restyle, recolor, or rename them. Keep the alt text `Static Badge`.

### Copilot Chat, app, or IDE prompt

```markdown
1. Ask Copilot Chat to summarize the change.

   > ![Static Badge](https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple)
   >
   > ```prompt
   > Summarize the changes in this pull request.
   > ```
```

### Copilot CLI prompt

```markdown
1. Run the prompt with Copilot CLI.

   > ![Static Badge](https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff)
   >
   > ```prompt
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

## Template variables in step content

`GrantBirki/comment` renders a step file as a Nunjucks template **only** when the workflow step that posts it
passes `vars:`. That changes how double braces behave:

| Posting step | `{{ name }}` in the step file | Literal `{{ }}` or `{% %}` text, such as a `${{ secrets.TOKEN }}` snippet |
| --- | --- | --- |
| passes `vars:` | replaced by the value, or by nothing when `name` was not passed | read as template syntax, so it is mangled unless wrapped in `{% raw %}` and `{% endraw %}` |
| no `vars:` | shown literally, braces included | shown as written |

Rules:

- `0-start-exercise.yml` posts step 1 with `login` and `full_repo_name`, so step 1 can use `{{ login }}` and
  `{{ full_repo_name }}`.
- The step workflow skeletons post later steps without `vars:`. A step that uses a variable needs a matching
  `vars:` entry on the `Create comment - add step content` step of the workflow that posts it.
- Add `vars:` only where a step uses a variable.
- In every step file posted with `vars:`, wrap literal `${{ ... }}` expressions, such as workflow snippets, in
  `{% raw %}` and `{% endraw %}`.

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

The published exercises add a section, such as `### What you practiced`, between the recap and
`### What's next?`. Add one when it helps, and keep `### What's next?` last.

## Images and callouts

- Store exercise images in `.github/images/` and reference them relatively from step files, for example
  `<img width="200" alt="descriptive alt text" src="../images/inspectocat.png" />`.
- Always provide meaningful alt text.
- Keep `[!NOTE]`, `[!IMPORTANT]`, `[!TIP]`, `[!WARNING]`, and `[!CAUTION]` callouts left-justified when they
  are not part of a list. Inside an activity's numbered list, indent a callout three spaces under its item,
  because a left-justified callout ends the list.

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
> # Structural audit: required files exist, step files and step workflows line
> # up by number, every step workflow is N-step.yml declaring `name: Step N`,
> # only the final one is marked `# Last step of the exercise` and posts the
> # review, referenced content files and enable targets exist, grading jobs are
> # wired into needs, and permissions are granted per job.
> python3 - <<'PY'
> import re, sys, yaml
> from pathlib import Path
>
> problems = []
> steps = Path(".github/steps")
> flows = Path(".github/workflows")
> # `# Last step of the exercise` is a YAML comment, so read it from the raw text.
> LAST = re.compile(r"""^name:\s*["']?Step (\d+)["']?\s+#\s*Last step of the exercise\s*$""", re.MULTILINE)
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
> workflow_numbers, names, marked, enables = {}, {}, [], []
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
>     if LAST.search(text):
>         marked.append(path)
>
>     number = re.match(r"(\d+)-", path.name)
>     if number:
>         value = int(number.group(1))
>         if declared != f"Step {value}":
>             problems.append(f"{path}: declares name {declared!r}, expected 'Step {value}'")
>         if value == 0 and path.name != "0-start-exercise.yml":
>             problems.append(f"{path}: the start workflow must be 0-start-exercise.yml")
>         if value > 0:
>             if path.name != f"{value}-step.yml":
>                 problems.append(f"{path}: rename to {value}-step.yml; every step workflow, including the last, is N-step.yml")
>             if value in workflow_numbers:
>                 problems.append(f"{path}: duplicates step number {value} with {workflow_numbers[value]}")
>             workflow_numbers[value] = path
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
> final = workflow_numbers.get(max(step_numbers)) if step_numbers else None
> if final is not None:
>     text = final.read_text(encoding="utf-8")
>     if final not in marked:
>         problems.append(f"{final}: the final workflow must be 'name: Step {max(step_numbers)} # Last step of the exercise'")
>     if "REVIEW_FILE" not in text:
>         problems.append(f"{final}: final workflow does not reference REVIEW_FILE")
>     if re.search(r'gh workflow enable\s+"', text):
>         problems.append(f"{final}: final workflow should not enable another step")
> for path in marked:
>     if path != final:
>         problems.append(f"{path}: only the final step workflow is marked '# Last step of the exercise'")
>
> if problems:
>     sys.exit("\n".join(problems))
> print(f"structure OK: steps {sorted(step_numbers)}, workflows {sorted(workflow_numbers)}, final {final.name}")
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
> # Step anatomy: `## Step N:` comes first, then exactly one non-empty Theory and
> # either one `### ⌨️ Activity:` or `### ⌨️ Activity 1:`, `2:`, and so on. Each
> # activity has `1.` instructions and its own Having trouble block, the final
> # activity ends with the Mona line, no column-0 line splits a list, and every
> # badge sits in one blockquote with `>` and the fence language it requires.
> python3 - <<'PY'
> import re, sys
> from pathlib import Path
>
> ACTIVITY = re.compile(r"### (⌨️|⌨|:keyboard:) Activity( \d+)?:(.*)")
> TROUBLE = "<summary>Having trouble? 🤷</summary>"
> MONA = "Wait a moment for Mona to check your work, provide feedback, and share the next lesson."
> FENCE = "`" * 3
> # Canonical badge, then the fence language its blockquote must use.
> CANONICAL = """
> https://img.shields.io/badge/Prompt-text?style=for-the-badge&logo=github-copilot&logoColor=white&labelColor=purple&color=purple prompt
> https://img.shields.io/badge/CLI-Prompt-text?style=flat-square&logo=github-copilot&labelColor=8250df&color=fbefff prompt
> https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff bash
> """
> BADGES = dict(line.split() for line in CANONICAL.strip().splitlines())
> problems = []
>
> def visible(lines):
>     """Blank fenced code, so a `# comment` inside a fence is not read as a
>     heading. Keep each opening fence, because one at column 0 ends a list."""
>     out, fence = [], None
>     for line in lines:
>         bare = re.sub(r"^[ \t>]*", "", line)
>         if fence is None:
>             opener = re.match(r"`{3,}|~{3,}", bare)
>             if opener:
>                 fence = opener.group(0)
>                 line = line[: len(line) - len(bare)] + fence
>             out.append(line)
>         else:
>             if re.fullmatch(re.escape(fence[0]) + "{%d,}\\s*" % len(fence), bare):
>                 fence = None
>             out.append("")
>     return out
>
> def ends_list(line, previous):
>     """A column-0 line ends a numbered list unless it lazily continues a paragraph."""
>     if not line.strip() or line[0] in " \t" or re.match(r"\d+\.\s", line):
>         return False
>     return not previous.strip() or re.match(r"[>#`~]|[-*+]\s", line) is not None
>
> for path in sorted(Path(".github/steps").glob("*-step.md")):
>     number = int(path.name.split("-")[0])
>     raw = path.read_text(encoding="utf-8").splitlines()
>     lines = visible(raw)
>     heads = [i for i, line in enumerate(lines) if re.match(r"#{1,3} ", line)]
>
>     def body(start):
>         end = next((h for h in heads if h > start), len(lines))
>         return lines[start + 1 : end]
>
>     if not heads or not re.match(rf"## Step {number}: \S", lines[heads[0]]):
>         problems.append(f"{path}: the first heading must be '## Step {number}: <title>'")
>
>     theory = [i for i in heads if lines[i].startswith("### 📖 Theory:")]
>     activities = [(i, m) for i in heads if (m := ACTIVITY.fullmatch(lines[i].rstrip()))]
>     sections = set(theory) | {i for i, _ in activities}
>     for i in heads:
>         if lines[i].startswith("### ") and i not in sections:
>             problems.append(f"{path}:{i + 1}: '{lines[i]}' is neither Theory nor an Activity; make it a '####' subsection")
>
>     if len(theory) != 1:
>         problems.append(f"{path}: expected exactly 1 Theory block, found {len(theory)}")
>     elif not [l for l in body(theory[0]) if l.strip() and not re.fullmatch(r"\s*(<img[^>]*>|<!--.*-->)\s*", l)]:
>         problems.append(f"{path}: Theory block has no content")
>
>     numbers = [m.group(2) for _, m in activities]
>     if not activities:
>         problems.append(f"{path}: no Activity block")
>     elif len(activities) == 1 and numbers[0]:
>         problems.append(f"{path}: a single activity is '### ⌨️ Activity: <title>', without a number")
>     elif len(activities) > 1 and [n and int(n) for n in numbers] != list(range(1, len(activities) + 1)):
>         problems.append(f"{path}: number every activity in order, '### ⌨️ Activity 1:' to 'Activity {len(activities)}:'")
>
>     for i, match in activities:
>         chunk = body(i)
>         where = f"{path}:{i + 1}"
>         if match.group(1) != "⌨️":
>             problems.append(f"{where}: use the ⌨️ emoji, not {match.group(1)!r}")
>         if not match.group(3).strip():
>             problems.append(f"{where}: activity has no title")
>         items = [(n, re.match(r"(\s*)(\d+)\.\s+\S", l)) for n, l in enumerate(chunk)]
>         items = [(n, m) for n, m in items if m]
>         if not items:
>             problems.append(f"{where}: activity has no numbered instructions")
>         for n, m in items:
>             if m.group(2) != "1":
>                 problems.append(f"{path}:{i + n + 2}: number every list item '1.', found '{m.group(2)}.'")
>         top = [n for n, m in items if not m.group(1)]
>         for a, b in zip(top, top[1:]):
>             n = next((n for n in range(a + 1, b) if ends_list(chunk[n], chunk[n - 1])), None)
>             if n is not None:
>                 problems.append(f"{path}:{i + n + 2}: this column-0 line ends the numbered list; indent it three spaces")
>         if TROUBLE not in "\n".join(chunk):
>             problems.append(f"{where}: activity is not followed by its own 'Having trouble? 🤷' block")
>     if activities and MONA not in "\n".join(body(activities[-1][0])):
>         problems.append(f"{path}: the final activity does not end with '{MONA}'")
>
>     for n, line in enumerate(raw):
>         found = re.search(r"!\[([^\]]*)\]\((https://img\.shields\.io/badge/[^)\s]+)\)", line)
>         if not found:
>             continue
>         alt, url = found.groups()
>         if url not in BADGES:
>             problems.append(f"{path}:{n + 1}: non-canonical badge {url}")
>             continue
>         fence = FENCE + BADGES[url]
>         follow = raw[n + 1 : n + 3]
>         if not (alt == "Static Badge" and re.match(r"\s*> !\[", line) and len(follow) == 2
>                 and re.fullmatch(r"\s*>\s*", follow[0]) and follow[1].strip() == "> " + fence):
>             problems.append(f"{path}:{n + 1}: write '> ![Static Badge](...)', then '>', then '> {fence}' in one blockquote")
>
> if problems:
>     sys.exit("\n".join(problems))
> print("step content OK")
> PY
>
> # Template variables: a step file posted without `vars:` cannot use
> # `{{ name }}`, and one posted with `vars:` may use only the names passed and
> # must wrap literal `${{ }}` expressions in raw tags.
> python3 - <<'PY'
> import re, sys, yaml
> from pathlib import Path
>
> # GrantBirki/comment renders a file with Nunjucks only when the step passes
> # `vars:`. Without vars, {{ name }} reaches the learner as literal braces.
> # With vars, an unknown name renders empty and ${{ ... }} loses its body.
> problems = []
> posts = {}
>
> for path in sorted(Path(".github/workflows").glob("*.yml")):
>     document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
>     for job in (document.get("jobs") or {}).values():
>         env = {**(document.get("env") or {}), **((job or {}).get("env") or {})}
>         for step in (job or {}).get("steps") or []:
>             if not str(step.get("uses", "")).startswith("GrantBirki/comment"):
>                 continue
>             options = step.get("with") or {}
>             target = re.sub(r"\$\{\{\s*env\.(\w+)\s*\}\}",
>                             lambda m: str(env.get(m.group(1), m.group(0))), str(options.get("file", "")))
>             if not target.startswith(".github/steps/"):
>                 continue
>             given = options.get("vars")
>             if isinstance(given, str):
>                 given = yaml.safe_load(given)
>             names = set(given) if isinstance(given, dict) else None
>             posts.setdefault(target, []).append((path, names))
>
> RAW = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}", re.DOTALL)
> TAG = re.compile(r"\{%.*?%\}")
> VARIABLE = re.compile(r"(?<!\$)\{\{-?\s*([A-Za-z_]\w*)[^}]*\}\}")
> EXPRESSION = re.compile(r"\$\{\{.*?\}\}")
>
> for target, sources in sorted(posts.items()):
>     if not Path(target).exists():
>         continue
>     text = Path(target).read_text(encoding="utf-8")
>     for workflow, names in sources:
>         where = f"{target} (posted by {workflow})"
>         if names is None:
>             for match in VARIABLE.finditer(text):
>                 problems.append(f"{where}: '{match.group(0)}' shows literally; pass '{match.group(1)}' in the step's vars")
>             for match in TAG.finditer(text):
>                 problems.append(f"{where}: '{match.group(0)}' shows literally because the step passes no vars")
>             continue
>         rendered = RAW.sub("", text)
>         if "{#" in rendered:
>             problems.append(f"{where}: '{{#' starts a Nunjucks comment and hides text; wrap it in raw tags")
>         for match in EXPRESSION.finditer(rendered):
>             problems.append(f"{where}: wrap '{match.group(0)}' in raw tags; Nunjucks renders it as '$'")
>         for match in VARIABLE.finditer(rendered):
>             if match.group(1) not in names:
>                 problems.append(f"{where}: '{match.group(0)}' renders empty; vars pass only {sorted(names)}")
>
> if problems:
>     sys.exit("\n".join(problems))
> print(f"template variables OK in {len(posts)} posted files")
> PY
>
> # README: one canonical Copy Exercise button under `### How to start this
> # exercise` that opens github.com/new with owner=%40me, name=skills-<repo>,
> # description=Exercise:+Title, and visibility=public (private only for a
> # privately published exercise), then a `---` rule and the `&copy;` footer,
> # which carries the LICENSE year when LICENSE has one.
> python3 - <<'PY'
> import re, sys
> from pathlib import Path
> from urllib.parse import parse_qs, urlsplit
>
> IMAGE = "https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935"
> CONDUCT = "https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md"
> problems = []
> lines = Path("README.md").read_text(encoding="utf-8").splitlines()
>
> start = next((i for i, line in enumerate(lines) if line.strip() == "### How to start this exercise"), None)
> end = next((i for i in range(start + 1, len(lines)) if re.match(r"#{1,3} ", lines[i])), len(lines)) if start is not None else 0
> if start is None:
>     problems.append("README.md: missing '### How to start this exercise'")
>
> buttons = [(i, *m.groups()) for i, line in enumerate(lines)
>            for m in re.finditer(r"\[!\[[^\]]*\]\(([^)\s]*Copy%20Exercise[^)\s]*)\)\]\(([^)\s]+)\)", line)]
> if len(buttons) != 1:
>     problems.append(f"README.md: expected exactly one Copy Exercise button, found {len(buttons)}")
> for i, image, link in buttons:
>     where = f"README.md:{i + 1}"
>     if start is None or not start < i < end:
>         problems.append(f"{where}: put the Copy Exercise button under '### How to start this exercise'")
>     if image != IMAGE:
>         problems.append(f"{where}: use the canonical Copy Exercise image {IMAGE}")
>     parts = urlsplit(link)
>     query = {key: values[0] for key, values in parse_qs(parts.query).items()}
>     if f"{parts.scheme}://{parts.netloc}{parts.path}" != "https://github.com/new":
>         problems.append(f"{where}: the button must link to https://github.com/new")
>     if query.get("owner") != "@me":
>         problems.append(f"{where}: keep owner=%40me so the learner's own account is preselected")
>     if query.get("visibility") not in {"public", "private"}:
>         problems.append(f"{where}: set visibility=public, or visibility=private for a privately published exercise")
>     if not query.get("template_owner") or not query.get("template_name"):
>         problems.append(f"{where}: set template_owner and template_name")
>     elif query.get("name", "").lower() != "skills-" + query["template_name"].lower():
>         problems.append(f"{where}: name must be skills-{query['template_name']}")
>     if not re.search(r"(?:^|&)description=Exercise:\+[^&]", parts.query) or "%20" in parts.query:
>         problems.append(f"{where}: description must read 'Exercise:+Title+Words', with + between words")
>
> content = [line.strip() for line in lines if line.strip()]
> footer = content[-1] if content else ""
> if not footer.startswith("&copy;") or CONDUCT not in footer or "&bull;" not in footer:
>     problems.append("README.md: end with the footer '&copy; <year> <holder> &bull; [Code of Conduct](...) &bull; [license](...)'")
> elif len(content) < 2 or content[-2] != "---":
>     problems.append("README.md: put a '---' line before the footer")
> else:
>     license_text = Path("LICENSE").read_text(encoding="utf-8") if Path("LICENSE").exists() else ""
>     year = re.search(r"Copyright \(c\)\s+(\d{4})", license_text)
>     if year and year.group(1) not in footer:
>         problems.append(f"README.md: the footer year should match LICENSE ({year.group(1)})")
>
> if problems:
>     sys.exit("\n".join(problems))
> print("README OK")
> PY
>
> # Workflows parse
> if command -v actionlint >/dev/null 2>&1; then
>   actionlint
> else
>   python3 -c "import sys,yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"
> fi
> ```
