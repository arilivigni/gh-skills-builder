---
name: create-github-skills-outline
description: "Create learner-centered GitHub Skills exercise outlines from a topic, demo, workshop, or rough idea. Use this whenever the user wants to design a GitHub Skills exercise, convert training material into a self-paced GitHub exercise, define learning objectives and steps, or plan validation before building repository files."
---

# Create GitHub Skills outline

Use this skill to design a self-paced GitHub Skills-style exercise before implementation begins.

## Workflow

1. Clarify the topic, target learner, prerequisites, time box, and desired outcome.
2. Narrow broad ideas to one primary learner outcome.
3. Design a scenario that gives the learner a reason to complete the task.
4. Break the exercise into small steps with one learner action per step.
5. Define validation signals and feedback for each step.
6. Identify repository files, workflows, and assets needed for implementation.
7. Call out open questions instead of inventing domain details that affect correctness.

## Step design requirements

For each step in the learner journey, include:

- `Theory`: awareness-level context only, directly tied to the activity.
- `Activity`: concrete numbered actions a learner can perform in GitHub.
- `Transition`: both an `Actions Trigger` and a `Grading-Check`.

Keep the exercise scoped to the requested topic. If a concept is useful but out of scope, list it as a follow-up exercise instead of adding it to the current outline.

## Reference guidance

- Prefer official references (GitHub Docs, GitHub Learn, GitHub Blog/Changelog, and official VS Code docs).
- Keep references relevant to the exact step content; do not add generic links that are not used.

## Formatting conventions

- Any image added for the exercise should be stored in `.github/images` and referenced with a relative path.
- Keep GitHub callouts left-justified (no indentation) when using `[!NOTE]`, `[!IMPORTANT]`, or `[!TIP]`.
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

## Target learner

## Prerequisites

## Learning objectives

## Scenario

## Learner journey

| Step | Learner action | Why it matters | Validation signal | Feedback |
| --- | --- | --- | --- | --- |

## Repository plan

## Success criteria

## Risks and open questions
```

## Quality bar

- Objectives should be observable: the learner can demonstrate them through repository activity.
- Steps should be small enough that validation can give targeted feedback.
- Validation should check intent, not only file existence.
- The outline should be implementable as GitHub issues, comments, workflows, and Markdown content.
