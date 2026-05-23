---
name: offer-skill
description: Analyze resumes, project experience, interview notes, and optional external interview signals from candidate, interviewer, or dual perspectives. Use when Codex needs to help with project highlight extraction, resume-vs-JD evaluation, mock interview generation, or interview retrospectives. Prefer the unified entrypoint so the host AI can automatically create or reuse cases, import local files, apply optional research profiles, and write structured outputs back to the repository.
---

# Offer Skill

Offer Skill is a dual-perspective interview and hiring skill. Use it to turn local resume, JD, project, interview, and research materials into reusable case artifacts instead of one-off answers.

## User-Facing Model

The user should normally interact with this Skill through the host AI tool, not by manually running repository scripts.

The scripts in this repository exist to support the Skill internally:

- create cases
- import local materials
- run workflows
- capture optional research
- back up and restore artifacts

When this Skill is invoked, the AI host should do the orchestration and prefer the unified entrypoint:

```bash
python scripts/offer_skill.py --workflow <project-highlight|resume-eval|mock-interview|interview-retro> --perspective <candidate|interviewer|dual> ...
```

Use the lower-level scripts only when debugging or testing.

## Operating Rules

- Start by identifying the active perspective: `candidate`, `interviewer`, or `dual`.
- Start by identifying the active workflow: `project-highlight`, `resume-eval`, `mock-interview`, or `interview-retro`.
- Start by identifying the active research profile: `local-only`, `web-assisted`, or `deep-research`.
- Use local materials as the grounding layer even when external research signals are added.
- Treat all outputs as case assets. Prefer writing or updating files under `cases/{case_slug}/` rather than leaving analysis only in chat.

## Workflow Decision Tree

1. If the user wants to understand how to present a project, use `project-highlight`.
2. If the user wants to compare a resume against a target role or JD, use `resume-eval`.
3. If the user wants a realistic question flow tied to a role, use `mock-interview`.
4. If the user wants to review interview performance and build an improvement plan, use `interview-retro`.

## Typical Requests

- `Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.`
- `Use $offer-skill to extract project highlights from this project note from the candidate perspective.`
- `Use $offer-skill to create a mock interview from this JD with web-assisted research.`
- `Use $offer-skill to review these interview notes and compare knowledge gaps versus expression gaps.`

## Case Workflow

1. Read the user's local materials.
2. Prefer the unified entrypoint for normal Skill execution:

```bash
python scripts/offer_skill.py \
  --workflow <project-highlight|resume-eval|mock-interview|interview-retro> \
  --perspective <candidate|interviewer|dual> \
  --research-profile <local-only|web-assisted|deep-research> \
  --display-name "<name>" \
  --resume-file <path> \
  --jd-file <path> \
  --projects-file <path> \
  --interview-notes-file <path> \
  --candidate-answers-file <path> \
  --research-file <path>
```

3. Let the unified entrypoint automatically:

- create or reuse the case
- import the provided materials
- apply the selected workflow
- use optional research signals when requested
- write outputs under `cases/{case_slug}/`

4. Use the lower-level scripts only when needed for debugging:

```bash
python scripts/create_case.py --case-slug <slug> --display-name "<name>" --perspective <candidate|interviewer|dual>
python scripts/import_material.py --case-slug <slug> --material-type <resume|jd|projects|interview_notes|candidate_answers> --from-file <path>
python scripts/run_workflow.py --case-slug <slug> --workflow <project-highlight|resume-eval|mock-interview|interview-retro>
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
- When using research profiles, keep the final analysis grounded in the candidate's actual materials instead of substituting internet summaries for real evidence.

## References

- Read [references/schema-reference.md](references/schema-reference.md) for case structure and file contracts.
- Read [references/workflow-status.md](references/workflow-status.md) for workflow coverage.
- Read [references/research-status.md](references/research-status.md) for research profile usage.
