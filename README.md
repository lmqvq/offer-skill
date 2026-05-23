# offer-skill

**A dual-perspective interview and hiring skill**

`offer-skill` is an open-source Skill for analyzing resumes, project experience, and hiring materials from both candidate and interviewer perspectives.

It is designed around one core idea:

> turn interview-related materials into reusable case artifacts, not one-off answers

## How Users Should Actually Use It

The normal usage model is:

1. install `offer-skill` into your AI tool's skill directory
2. ask the AI tool to use `offer-skill`
3. let the AI read your local resume / JD / project files
4. let the AI call the internal scripts for case creation, import, and workflow execution

In other words:

- end users should mainly talk to the AI tool
- the scripts in this repo are internal implementation details
- those scripts exist so the Skill can persist cases, version artifacts, and produce deterministic outputs

### Typical user requests

Candidate-side:

- `Use $offer-skill to evaluate my resume against this JD from the candidate perspective.`
- `Use $offer-skill to extract project highlights from my backend project notes.`

Interviewer-side:

- `Use $offer-skill to review this resume against the JD from the interviewer perspective.`
- `Use $offer-skill to identify weak evidence and generate follow-up questions for this candidate's project experience.`

Dual perspective:

- `Use $offer-skill to compare how a candidate would present this project and how an interviewer would challenge it.`

## Why This Exists

Most interview helpers only solve one slice of the problem:

- resume polishing
- project storytelling
- mock questions
- interview review

`offer-skill` is built to unify those slices behind:

- shared input parsing
- shared evidence and competency reasoning
- dual-perspective output
- case persistence
- version backup and rollback

## Product Positioning

`offer-skill` serves two primary audiences:

- Candidates: explain projects better, prepare for interviews, understand gaps
- Interviewers and hiring teams: evaluate resumes faster, identify risks, ask sharper follow-up questions

## v0.1 Scope

`v0.1` is intentionally narrow.

### Enabled in `v0.1`

- `project-highlight`
- `resume-eval`
- local material parsing
- case creation and persistence
- version backup and rollback

### Explicitly Deferred After `v0.1`

These are intentionally **not** implemented yet and must remain visible in docs and presets:

- `mock-interview`
- `interview-retro`
- `web-assisted` research
- `deep-research` interview trend analysis

This warning is repeated on purpose so later contributors do not accidentally erase planned capabilities from the roadmap.

## Repository Layout

```text
offer-skill/
├── SKILL.md
├── README.md
├── INSTALL.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
├── presets/
├── references/
├── scripts/
├── cases/
└── tests/
```

## Quick Start

## AI-First Usage

If your host supports Skills, the preferred experience is to install `offer-skill` and invoke it through the AI tool.

Examples:

```text
Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.

Use $offer-skill to extract project highlights from this project description for a backend engineer role.
```

The AI should then:

- create or reuse a case
- import the local materials
- run the right workflow
- save outputs under `cases/{case_slug}/`

Internally, the preferred entrypoint is:

```bash
python scripts/offer_skill.py --workflow <resume-eval|project-highlight> ...
```

## Developer / Internal Usage

Run the full `v0.1` flow in one call:

```bash
python scripts/offer_skill.py \
  --workflow resume-eval \
  --perspective interviewer \
  --display-name "Backend Resume Review" \
  --resume-file ./resume.md \
  --jd-file ./jd.md \
  --projects-file ./projects.md
```

If you need lower-level debugging, you can still call the internal scripts separately.

Create a new case:

```bash
python scripts/create_case.py \
  --case-slug backend-java-social \
  --display-name "Backend Java Social App Prep" \
  --perspective candidate \
  --role-title "Backend Engineer"
```

Import local materials:

```bash
python scripts/import_material.py \
  --case-slug backend-java-social \
  --material-type resume \
  --from-file ./resume.md

python scripts/import_material.py \
  --case-slug backend-java-social \
  --material-type jd \
  --from-file ./jd.md

python scripts/import_material.py \
  --case-slug backend-java-social \
  --material-type projects \
  --from-file ./projects.md
```

Run a v0.1 workflow:

```bash
python scripts/run_workflow.py \
  --case-slug backend-java-social \
  --workflow resume-eval

python scripts/run_workflow.py \
  --case-slug backend-java-social \
  --workflow project-highlight
```

Back up the case before changes:

```bash
python scripts/version_manager.py --action backup --case-slug backend-java-social
```

List backups:

```bash
python scripts/version_manager.py --action list --case-slug backend-java-social
```

Rollback:

```bash
python scripts/version_manager.py --action rollback --case-slug backend-java-social --version v1
```

## Documentation

- [PRD](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Deferred Capabilities](docs/DEFERRED_CAPABILITIES.md)

## Safety and Boundaries

`offer-skill` is an analysis aid, not an automated hiring decision maker.

It should not be used to:

- fabricate project experience
- generate deceptive claims
- replace human hiring decisions
- imply live web research in `v0.1`

## Open Source Direction

This repository is being prepared as a public starting point. The current goal is to make the first release:

- understandable
- extensible
- testable
- explicit about deferred capabilities

## License

MIT
