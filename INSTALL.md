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
python scripts/offer_skill.py --workflow <project-highlight|resume-eval|mock-interview|interview-retro> ...
```

## Local Use

Clone the repository:

```bash
git clone <your-repo-url> offer-skill
cd offer-skill
```

Run the full flow in one call:

```bash
python scripts/offer_skill.py \
  --workflow mock-interview \
  --perspective candidate \
  --display-name "My First Case" \
  --jd-file ./jd.md \
  --resume-file ./resume.md \
  --projects-file ./projects.md \
  --research-profile web-assisted \
  --research-file ./market_notes.md
```

Use the lower-level scripts only when you need step-by-step debugging.

## AI-Tool Usage

After the Skill is installed, users should normally say things like:

```text
Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

Use $offer-skill to extract project highlights from this project note from the dual perspective.

Use $offer-skill to run a mock interview from this JD with deep-research.

Use $offer-skill to review these interview notes and tell me what broke down.
```

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```
