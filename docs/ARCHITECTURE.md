# offer-skill Architecture

## Core Shape

```text
user intent
  -> perspective preset
  -> workflow preset
  -> local materials
  -> case artifacts
  -> structured outputs
  -> version backup / rollback
```

## Active v0.1 Modules

- `scripts/create_case.py`
- `scripts/version_manager.py`
- `presets/perspectives.json`
- `presets/workflows.json`

## Deferred Modules After v0.1

- mock interview generation
- interview retrospective builder
- web-assisted research pipeline

These are deferred, not removed.

## Case Contract

Each case lives under:

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

See [../references/schema-reference.md](../references/schema-reference.md) for details.
