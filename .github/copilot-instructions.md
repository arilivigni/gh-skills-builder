# Copilot instructions for this plugin

This repository contains a GitHub Copilot plugin for creating GitHub Skills exercises. Keep the plugin content focused on the exercise lifecycle: outline, bootstrap, review, and publish.

## Repository layout

- Root `plugin.json` declares Agent Plugins v1.0.0 metadata and its canonical `$schema`. Do not add top-level component path arrays.
- `com.github.copilot/agents/` contains Copilot-specific custom agent definitions with `.agent.md` files.
- `skills/` contains Agent Skill folders. Each skill has a `SKILL.md` file with `name` and `description` frontmatter.
- `instructions/` contains optional companion Copilot instructions to copy into exercise repositories, not automatically loaded plugin components.
- `evals/evals.json` contains skill-creator test prompts.

## Editing guidance

- Keep one thin orchestrator agent responsible for sequencing, approval gates, and publication authorization.
- Put stage-specific requirements in the corresponding lifecycle skills; load skills directly rather than adding specialist agents.
- Keep review report-only until the user approves a separate fix round. This is a behavioral rule, not restricted tool access or independent review.
- Prefer learner-centered language: objectives, scenario, practice loop, validation, feedback, and completion criteria.
- Preserve the GitHub Skills conventions of issue-driven steps, workflow-backed validation, clear learner feedback, and safe repository automation.
- Avoid destructive workflow guidance. Any generated workflow should use least-privilege permissions and explain what it changes.
- Update `README.md`, the manifest version, and lifecycle validation whenever agents or skills are added, removed, or renamed. Components are discovered by their fixed directory layout.
