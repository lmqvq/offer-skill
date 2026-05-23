# Contributing

Thanks for contributing to `offer-skill`.

## Scope Guard

Before changing presets, docs, or code, keep these two rules intact:

1. `v0.1` only enables `project-highlight` and `resume-eval`.
2. `mock-interview`, `interview-retro`, and web-assisted research are deferred, not removed.

If you change docs or presets, preserve that status explicitly.

## Development Notes

- Keep case structure stable.
- Keep perspective separate from workflow.
- Prefer local-material support before adding research complexity.
- Add tests for scripts and schema-affecting changes.

## Test Command

Run tests from the repository parent directory on this machine:

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```

