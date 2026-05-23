# Install

## Important Usage Note

`offer-skill` is designed to be used primarily through an AI tool that supports Skills.

That means the intended flow is:

- install the skill
- tell the AI to use `offer-skill`
- let the AI call the internal scripts

The scripts in this repository are mainly for:

- deterministic case management
- testing
- development
- CI

They are not meant to be the main end-user interface.

For normal Skill execution, prefer the unified internal entrypoint:

```bash
python scripts/offer_skill.py --workflow <resume-eval|project-highlight> ...
```

## Local Use

Clone the repository:

```bash
git clone <your-repo-url> offer-skill
cd offer-skill
```

Run the full `v0.1` flow in one call:

```bash
python scripts/offer_skill.py \
  --workflow resume-eval \
  --perspective candidate \
  --display-name "My First Case" \
  --resume-file ./resume.md \
  --jd-file ./jd.md \
  --projects-file ./projects.md
```

Use the lower-level scripts only when you need step-by-step debugging.

Create a case:

```bash
python scripts/create_case.py \
  --case-slug my-first-case \
  --display-name "My First Case" \
  --perspective candidate
```

Import local files into the case:

```bash
python scripts/import_material.py --case-slug my-first-case --material-type resume --from-file ./resume.md
python scripts/import_material.py --case-slug my-first-case --material-type jd --from-file ./jd.md
python scripts/import_material.py --case-slug my-first-case --material-type projects --from-file ./projects.md
```

Run a supported workflow:

```bash
python scripts/run_workflow.py --case-slug my-first-case --workflow resume-eval
python scripts/run_workflow.py --case-slug my-first-case --workflow project-highlight
```

## AI-Tool Usage

After the Skill is installed, users should normally say things like:

```text
Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

Use $offer-skill to extract project highlights from this project note from the dual perspective.
```

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```

## v0.1 Scope Reminder

Only these workflows are active:

- `project-highlight`
- `resume-eval`

These are deferred:

- `mock-interview`
- `interview-retro`
- `web-assisted` research
- `deep-research`

Keep them visible in:

- `presets/workflows.json`
- `presets/research-profiles.json`
