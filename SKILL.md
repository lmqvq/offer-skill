---
name: offer-skill
description: Analyze resumes, project experience, and interview notes from candidate, interviewer, or dual perspectives. Use when Codex needs to help with project highlight extraction, resume-vs-JD evaluation, interview preparation planning, or interview retrospectives. In v0.1, actively support only `resume-eval` and `project-highlight` with local materials; keep `mock-interview` and `interview-retro` marked as planned workflows for later releases.
---

# Offer Skill

Offer Skill is a dual-perspective interview and hiring skill. Use it to turn local resume, JD, project, and interview materials into reusable case artifacts instead of one-off answers.

## User-Facing Model

The user should normally interact with this Skill through the host AI tool, not by manually running repository scripts.

The scripts in this repository exist to support the Skill internally:

- create cases
- import local materials
- run workflows
- back up and restore artifacts

When this Skill is invoked, the AI host should do the orchestration and prefer the unified entrypoint:

```bash
python scripts/offer_skill.py --workflow <resume-eval|project-highlight> --perspective <candidate|interviewer|dual> ...
```

Use the lower-level scripts only when debugging or testing.

## Operating Rules

- Start by identifying the active perspective: `candidate`, `interviewer`, or `dual`.
- Start by identifying the active workflow: `project-highlight`, `resume-eval`, `mock-interview`, or `interview-retro`.
- In `v0.1`, execute only `project-highlight` and `resume-eval`.
- In `v0.1`, use only local materials. Do not claim web research, live interview-trend coverage, or sourced high-frequency question discovery.
- Preserve the roadmap: keep `mock-interview` and `interview-retro` visible as planned workflows, and keep web-assisted research visible as a planned capability.
- Preserve the research profile roadmap: keep `web-assisted` and `deep-research` visible as planned research profiles.
- Treat all outputs as case assets. Prefer writing or updating files under `cases/{case_slug}/` rather than leaving analysis only in chat.

## Workflow Decision Tree

1. If the user wants to understand how to present a project, use `project-highlight`.
2. If the user wants to compare a resume against a target role or JD, use `resume-eval`.
3. If the user asks for a realistic mock interview flow, explain that `mock-interview` is planned after `v0.1`.
4. If the user asks to review past interview performance, explain that `interview-retro` is planned after `v0.1`.

## Typical Requests

- `Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.`
- `Use $offer-skill to extract project highlights from this project note from the candidate perspective.`
- `Use $offer-skill to compare candidate and interviewer views of this project.`

## v0.1 Scope

Read [references/v0-1-scope.md](references/v0-1-scope.md) before creating or updating repo assets.

Current `v0.1` commitments:

- `project-highlight`
- `resume-eval`
- local-material parsing
- case creation and persistence
- version backup and rollback

Explicitly deferred after `v0.1`:

- `mock-interview`
- `interview-retro`
- web-assisted and deep research

## Case Workflow

1. Read the user's local materials.
2. Prefer the unified entrypoint for normal Skill execution:

```bash
python scripts/offer_skill.py \
  --workflow <resume-eval|project-highlight> \
  --perspective <candidate|interviewer|dual> \
  --display-name "<name>" \
  --resume-file <path> \
  --jd-file <path> \
  --projects-file <path>
```

3. Let the unified entrypoint automatically:

- create or reuse the case
- import the provided materials
- run the selected workflow
- write outputs under `cases/{case_slug}/`

4. Use the lower-level scripts only when needed for debugging:

```bash
python scripts/create_case.py --case-slug <slug> --display-name "<name>" --perspective <candidate|interviewer|dual>
python scripts/import_material.py --case-slug <slug> --material-type <resume|jd|projects> --from-file <path>
python scripts/run_workflow.py --case-slug <slug> --workflow <resume-eval|project-highlight>
```

5. Generate normalized or derived artifacts as they become available.
6. Write the final Markdown output under `analyses/`.
7. Before risky updates, run:

```bash
python scripts/version_manager.py --action backup --case-slug <slug>
```

8. If needed, list or restore versions:

```bash
python scripts/version_manager.py --action list --case-slug <slug>
python scripts/version_manager.py --action rollback --case-slug <slug> --version <version>
```

## Shared Interpretation Rules

- Use perspective to change emphasis, not facts.
- Distinguish strong evidence from weak claims.
- Prefer structured findings over generic encouragement.
- When materials are thin, say exactly what is missing.
- When a planned workflow is requested in `v0.1`, say it is deferred and preserve the request as roadmap context if appropriate.

## References

- Read [references/schema-reference.md](references/schema-reference.md) for case structure and file contracts.
- Read [references/workflow-status.md](references/workflow-status.md) for enabled and deferred workflow states.
- Read [references/research-status.md](references/research-status.md) for enabled and deferred research profiles.
