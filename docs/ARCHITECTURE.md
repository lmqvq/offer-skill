# offer-skill Architecture

## Core Shape

```text
user intent
  -> perspective preset
  -> workflow preset
  -> local materials
  -> optional research profile
  -> case artifacts
  -> structured outputs
  -> version backup / rollback
```

## Active Modules

- `scripts/create_case.py`
- `scripts/import_material.py`
- `scripts/run_workflow.py`
- `scripts/offer_skill.py`
- `scripts/version_manager.py`
- `scripts/research_engine.py`
- `presets/perspectives.json`
- `presets/workflows.json`
- `presets/research-profiles.json`

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
