<div align="center">

# offer-skill

### *A dual-perspective interview and hiring skill*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stage: v0.1](https://img.shields.io/badge/Stage-v0.1-blue.svg)](docs/ROADMAP.md)
[![Mode: Local Only](https://img.shields.io/badge/Research-local--only-orange.svg)](references/v0-1-scope.md)
[![Codex Skill](https://img.shields.io/badge/Skill-Codex-black.svg)](SKILL.md)
[![Stars](https://img.shields.io/github/stars/lmqvq/offer-skill?style=social)](https://github.com/lmqvq/offer-skill/stargazers)

</div>

---

`offer-skill` helps candidates and interviewers work from the same materials, but with different goals.

- Candidates want to explain projects better, find weak points in their resume, and prepare more precisely.
- Interviewers want to judge depth, detect weak evidence, and ask sharper follow-up questions.
- Most AI helpers answer once and disappear. `offer-skill` turns those materials into reusable **case artifacts**.

In one line:

> Resume + JD + project notes -> structured case -> reusable hiring analysis

## What This Project Is

`offer-skill` is not a generic chat prompt pack.

It is a Skill repo built around:

- dual perspectives: `candidate`, `interviewer`, `dual`
- workflow presets: `project-highlight`, `resume-eval`, `mock-interview`, `interview-retro`
- case persistence: keep materials and outputs under `cases/{case_slug}/`
- deterministic helpers: internal scripts for case creation, import, workflow execution, backup, and rollback

The intended usage model is AI-first:

1. install `offer-skill` into a host that supports Skills
2. ask the AI tool to use `offer-skill`
3. let the AI read your local files
4. let the AI call the internal scripts for you

## What Problem It Solves

### Candidate side

- "My project sounds flat in interviews even though I did real work."
- "I don't know which parts of my resume actually match this JD."
- "I need stronger, more evidence-based preparation than generic interview tips."

### Interviewer side

- "This resume sounds good, but where is the hard evidence?"
- "I need follow-up questions that actually separate shallow familiarity from real ownership."
- "I want a reusable evaluation artifact, not just chat history."

## v0.1 Status

`offer-skill` is intentionally shipping a narrow `v0.1`.

### Available now

| Workflow | Status | Perspective support | Input style | Output |
|---|---|---|---|---|
| `project-highlight` | `enabled` | `candidate` / `interviewer` / `dual` | local files only | project highlight analysis |
| `resume-eval` | `enabled` | `candidate` / `interviewer` / `dual` | local files only | resume-vs-JD evaluation |

### Explicitly deferred, but intentionally preserved

These are **not implemented yet**, and must remain visible in docs and presets:

| Capability | Status | Why it stays visible |
|---|---|---|
| `mock-interview` | `planned` | future interview simulation workflow |
| `interview-retro` | `planned` | future interview retrospective workflow |
| `web-assisted` research | `planned` | future sourced external interview material support |
| `deep-research` interview trend analysis | `planned` | future deeper role/stack/company interview analysis |

See:

- [Deferred Capabilities](docs/DEFERRED_CAPABILITIES.md)
- [Workflow Status](references/workflow-status.md)
- [Research Status](references/research-status.md)

## How Users Should Actually Use It

The normal user should **talk to the AI tool**, not manually orchestrate multiple scripts.

Typical requests:

```text
Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

Use $offer-skill to extract project highlights from this backend project note from the interviewer perspective.

Use $offer-skill to compare candidate and interviewer views of this project.
```

The AI should then:

- create or reuse a case
- import the provided local materials
- run the requested workflow
- save the result under `cases/{case_slug}/`

## Install

If your host discovers skills from a folder containing `SKILL.md`, clone this repo into that host's skills directory.

Example idea:

```bash
git clone https://github.com/lmqvq/offer-skill.git <YOUR_SKILLS_DIR>/offer-skill
```

Then invoke it from your AI tool by name.

### AI-first invocation

Examples:

```text
Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.

Use $offer-skill to extract project highlights from this project description for a backend engineer role.
```

## One-Call Internal Entrypoint

Internally, the preferred execution path is now a single script:

```bash
python scripts/offer_skill.py --workflow <resume-eval|project-highlight> ...
```

That unified entrypoint can:

- create or reuse a case
- import local materials
- run the selected workflow
- write outputs back to the case

Example:

```bash
python scripts/offer_skill.py \
  --workflow resume-eval \
  --perspective interviewer \
  --display-name "Backend Resume Review" \
  --resume-file ./resume.md \
  --jd-file ./jd.md \
  --projects-file ./projects.md
```

## Lower-Level Developer Flow

If you want to debug the system step by step, the lower-level scripts are still available:

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
```

### 3. Run a workflow

```bash
python scripts/run_workflow.py --case-slug backend-java-social --workflow resume-eval
python scripts/run_workflow.py --case-slug backend-java-social --workflow project-highlight
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
- room for future workflow chaining

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
- `references/`: scope guards and schema notes
- `scripts/`: internal deterministic helpers
- `tests/`: regression tests, including deferred-capability guards

## Documentation

- [PRD](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Deferred Capabilities](docs/DEFERRED_CAPABILITIES.md)

## Safety and Boundaries

`offer-skill` is an analysis aid, not an automated hiring decision system.

It should not be used to:

- fabricate project experience
- generate deceptive claims
- replace human hiring decisions
- imply live web research in `v0.1`

## Tests

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```

## Contributing

Before changing scope, keep these truths intact:

- `v0.1` only enables `project-highlight` and `resume-eval`
- `mock-interview` and `interview-retro` are deferred, not removed
- `web-assisted` and `deep-research` remain planned research profiles

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Acknowledgment

The presentation and repo-landing-page thinking here was improved by studying how [`titanwings/colleague-skill`](https://github.com/titanwings/colleague-skill) explains scope, install, usage, status, and roadmap on GitHub.

## License

MIT
