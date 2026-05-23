# Install

## Local Use

Clone the repository:

```bash
git clone <your-repo-url> offer-skill
cd offer-skill
```

Create a case:

```bash
python scripts/create_case.py \
  --case-slug my-first-case \
  --display-name "My First Case" \
  --perspective candidate
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

