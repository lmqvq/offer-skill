# offer-skill

**A dual-perspective interview and hiring skill**

`offer-skill` is an open-source Skill for analyzing resumes, project experience, and hiring materials from both candidate and interviewer perspectives.

It is designed around one core idea:

> turn interview-related materials into reusable case artifacts, not one-off answers

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

Create a new case:

```bash
python scripts/create_case.py \
  --case-slug backend-java-social \
  --display-name "Backend Java Social App Prep" \
  --perspective candidate \
  --role-title "Backend Engineer"
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
