# Case Schema Reference

## Required Files

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

## `meta.json` Core Fields

- `schema_version`
- `id`
- `kind`
- `case_slug`
- `display_name`
- `perspective`
- `workflow_history`
- `target_role`
- `inputs`
- `research`
- `artifacts`
- `lifecycle`
- `scope`

## `manifest.json` Core Fields

- `manifest_version`
- `id`
- `kind`
- `display_name`
- `entrypoints`
- `artifacts`
- `capabilities`
- `research_profiles`

## Research Note

`research/` directories remain part of every case because research can now be used directly by:

- `mock-interview`
- `interview-retro`

Research profiles available in the schema:

- `local-only`
- `web-assisted`
- `deep-research`
