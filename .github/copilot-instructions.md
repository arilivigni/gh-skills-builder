# Copilot instructions for this plugin

This repository contains a GitHub Copilot plugin for creating GitHub Skills exercises. Keep the plugin content focused on the exercise lifecycle: outline, bootstrap, review, and publish.

## Repository layout

- `.github/plugin/plugin.json` declares plugin metadata, custom agents, and Agent Skills.
- `agents/` contains custom agent definitions with `.agent.md` files.
- `skills/` contains Agent Skill folders. Each skill has a `SKILL.md` file with `name` and `description` frontmatter.
- `instructions/` contains companion Copilot instructions for exercise repositories. These are not listed in `plugin.json` because the referenced plugin spec declares only `agents`, `commands`, and `skills`.
- `evals/evals.json` contains skill-creator test prompts.

## Editing guidance

- Keep one thin orchestrator agent responsible for sequencing, approval gates, and publication authorization.
- Put stage-specific requirements in the corresponding lifecycle skills; load skills directly rather than adding specialist agents.
- Keep review report-only until the user approves a separate fix round. This is a behavioral rule, not restricted tool access or independent review.
- Prefer learner-centered language: objectives, scenario, practice loop, validation, feedback, and completion criteria.
- Preserve the GitHub Skills conventions of issue-driven steps, workflow-backed validation, clear learner feedback, and safe repository automation.
- Avoid destructive workflow guidance. Any generated workflow should use least-privilege permissions and explain what it changes.
- Update `README.md` and `plugin.json` whenever agents or skills are added, removed, or renamed.
