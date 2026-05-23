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

## `manifest.json` Core Fields

- `manifest_version`
- `id`
- `kind`
- `display_name`
- `entrypoints`
- `artifacts`
- `capabilities`

## v0.1 Note

`research` directories still exist in `v0.1` even though research workflows are deferred. Keep the folders to preserve forward compatibility.

Research profile presets must still preserve:

- `web-assisted`
- `deep-research`
