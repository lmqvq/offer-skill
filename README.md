<div align="center">

# offer-skill

### *A dual-perspective interview and hiring skill*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Workflows: 4](https://img.shields.io/badge/Workflows-4-success.svg)](references/workflow-status.md)
[![Research Profiles: 3](https://img.shields.io/badge/Research-3%20profiles-blue.svg)](references/research-status.md)
[![Codex Skill](https://img.shields.io/badge/Skill-Codex-black.svg)](SKILL.md)
[![Stars](https://img.shields.io/github/stars/lmqvq/offer-skill?style=social)](https://github.com/lmqvq/offer-skill/stargazers)

</div>

---

`offer-skill` helps candidates and interviewers work from the same materials, but with different goals.

- Candidates want to explain projects better, discover weak points, prepare for interviews, and review past performance.
- Interviewers want to judge depth, detect weak evidence, ask sharper follow-up questions, and review interview quality.
- Most AI helpers answer once and disappear. `offer-skill` turns resume, JD, project, and interview materials into reusable **case artifacts**.

In one line:

> Resume + JD + project notes + interview notes -> structured case -> reusable hiring analysis

## What This Project Is

`offer-skill` is not just a prompt collection.

It is a Skill repo built around:

- dual perspectives: `candidate`, `interviewer`, `dual`
- four workflows:
  - `project-highlight`
  - `resume-eval`
  - `mock-interview`
  - `interview-retro`
- three research modes:
  - `local-only`
  - `web-assisted`
  - `deep-research`
- case persistence: keep materials and outputs under `cases/{case_slug}/`
- deterministic helpers: internal scripts for case creation, import, workflow execution, backup, rollback, and research capture

## What Problem It Solves

### Candidate side

- "My project sounds flat in interviews even though I did real work."
- "I don't know which parts of my resume actually match this JD."
- "I want mock interviews tied to my real materials, not generic interview lists."
- "After an interview, I want to know whether I lacked knowledge or just explained it badly."

### Interviewer side

- "This resume sounds good, but where is the hard evidence?"
- "I need follow-up questions that separate shallow familiarity from real ownership."
- "I want to review interview performance in a structured way."
- "I want optional external trend signals, but I still want the analysis grounded in the candidate's actual materials."

## Current Capabilities

| Workflow | What it does | Typical inputs | Output |
|---|---|---|---|
| `project-highlight` | Extract project value, ownership, risk points, and deep-dive prompts | project notes, optional resume/JD | project highlight analysis |
| `resume-eval` | Compare a resume against a JD, detect weak evidence, and generate validation questions | resume, JD, optional projects | resume-vs-JD evaluation |
| `mock-interview` | Generate interview flows and practice questions from local materials and optional research signals | JD, optional resume/projects/research | mock interview plan |
| `interview-retro` | Review real or mock interview notes and turn them into an improvement plan | interview notes, optional answers/JD/projects/research | interview retrospective |

## Research Profiles

`offer-skill` supports three research profiles:

| Profile | Best for | Input style |
|---|---|---|
| `local-only` | privacy-first, grounded local analysis | only user-provided files |
| `web-assisted` | stronger realism from external signals | local files + external notes or live search |
| `deep-research` | broader interview trend analysis | local files + deeper external search/synthesis |

See:

- [Workflow Status](references/workflow-status.md)
- [Research Status](references/research-status.md)

## How Users Should Actually Use It

The normal user should **talk to the AI tool**, not manually orchestrate multiple scripts.

Typical requests:

```text
Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

Use $offer-skill to extract project highlights from this backend project note from the interviewer perspective.

Use $offer-skill to run a mock interview for this JD using my resume and project notes.

Use $offer-skill to review these interview notes and tell me what broke down.
```

The AI should then:

- create or reuse a case
- import the provided local materials
- apply the requested workflow
- save the result under `cases/{case_slug}/`

## Install

If your host discovers skills from a folder containing `SKILL.md`, clone this repo into that host's skills directory.

Example:

```bash
git clone https://github.com/lmqvq/offer-skill.git <YOUR_SKILLS_DIR>/offer-skill
```

Then invoke it from your AI tool by name.

### AI-first invocation

Examples:

```text
Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.

Use $offer-skill to extract project highlights from this project description for a backend engineer role.

Use $offer-skill to create a mock interview from this JD with deep-research enabled.
```

## One-Call Internal Entrypoint

Internally, the preferred execution path is a single script:

```bash
python scripts/offer_skill.py --workflow <project-highlight|resume-eval|mock-interview|interview-retro> ...
```

That unified entrypoint can:

- create or reuse a case
- import local materials
- run the selected workflow
- write outputs back to the case
- optionally use external research text or live research queries

Example:

```bash
python scripts/offer_skill.py \
  --workflow mock-interview \
  --perspective candidate \
  --display-name "Backend Mock Interview" \
  --jd-file ./jd.md \
  --resume-file ./resume.md \
  --projects-file ./projects.md \
  --research-profile web-assisted \
  --research-file ./market_notes.md
```

## Lower-Level Developer Flow

If you want to debug the system step by step, the lower-level scripts are still available.

### 1. Create a case

```bash
python scripts/create_case.py \
  --case-slug backend-java-social \
  --display-name "Backend Java Social App Prep" \
  --perspective candidate \
  --role-title "Backend Engineer"
```

### 2. Import local materials

```bash
python scripts/import_material.py --case-slug backend-java-social --material-type resume --from-file ./resume.md
python scripts/import_material.py --case-slug backend-java-social --material-type jd --from-file ./jd.md
python scripts/import_material.py --case-slug backend-java-social --material-type projects --from-file ./projects.md
python scripts/import_material.py --case-slug backend-java-social --material-type interview_notes --from-file ./interview_notes.md
python scripts/import_material.py --case-slug backend-java-social --material-type candidate_answers --from-file ./candidate_answers.md
```

### 3. Run a workflow

```bash
python scripts/run_workflow.py --case-slug backend-java-social --workflow resume-eval
python scripts/run_workflow.py --case-slug backend-java-social --workflow project-highlight
python scripts/run_workflow.py --case-slug backend-java-social --workflow mock-interview --research-profile web-assisted --research-file ./market_notes.md
python scripts/run_workflow.py --case-slug backend-java-social --workflow interview-retro
```

### 4. Back up or restore

```bash
python scripts/version_manager.py --action backup --case-slug backend-java-social
python scripts/version_manager.py --action list --case-slug backend-java-social
python scripts/version_manager.py --action rollback --case-slug backend-java-social --version v1
```

## What Gets Written

Each analysis is stored as a reusable case:

```text
cases/{case_slug}/
├── meta.json
├── manifest.json
├── inputs/
├── normalized/
├── derived/
├── analyses/
├── research/
└── versions/
```

This means the repo is built for repeated iteration, not one-shot prompting.

## Example Outputs

### `resume-eval`

Produces a Markdown artifact with:

- overall match
- strong matches
- weak matches
- missing evidence
- candidate suggestions
- interviewer questions

### `project-highlight`

Produces a Markdown artifact with:

- summary
- candidate view
- interviewer view
- evidence
- risk flags
- suggested questions
- action items

### `mock-interview`

Produces a Markdown artifact with:

- interview setup
- categorized question list
- expected signals
- common failure modes
- follow-up paths
- practice plan
- research signals

### `interview-retro`

Produces a Markdown artifact with:

- summary
- what went well
- what broke down
- interviewer interpretation
- candidate improvement plan
- next practice questions

## Why The Case Model Matters

The project is built around `case` artifacts because interview preparation and hiring review are iterative.

Without a case model, you get:

- repeated parsing
- repeated context loss
- chat-only outputs

With a case model, you get:

- reusable materials
- persistent outputs
- version backup and rollback
- room for workflow chaining

## Project Structure

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

Important directories:

- `presets/`: workflow, perspective, and research-profile presets
- `references/`: scope notes and schema notes
- `scripts/`: internal deterministic helpers
- `tests/`: regression tests for workflows, case scaffolding, and research-enabled execution

## Documentation

- [PRD](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)

## Safety and Boundaries

`offer-skill` is an analysis aid, not an automated hiring decision system.

It should not be used to:

- fabricate project experience
- generate deceptive claims
- replace human hiring decisions
- present external trend signals as if they were guaranteed truth

## Tests

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```

## Contributing

Contributions are welcome, especially around:

- richer parsers
- better interview trend synthesis
- stronger validators
- more realistic workflow chaining

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Acknowledgment

The repo presentation here was improved by studying how [`titanwings/colleague-skill`](https://github.com/titanwings/colleague-skill) explains scope, install, usage, and roadmap on GitHub.

## License

MIT
