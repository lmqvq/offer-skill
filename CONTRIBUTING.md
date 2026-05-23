# Contributing

Thanks for contributing to `offer-skill`.

## Development Notes

- Keep case structure stable.
- Keep perspective separate from workflow.
- Keep local materials as the grounding layer, even when using research profiles.
- Add tests for scripts and schema-affecting changes.

## Areas Where Contributions Help Most

- resume and JD parsing quality
- mock interview realism
- interview retrospective heuristics
- research source ranking and trend extraction
- better workflow chaining

## Test Command

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```
