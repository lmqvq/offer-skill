# Deferred Capabilities

This document exists to make planned-but-not-yet-implemented capabilities impossible to miss.

## Status

The following capabilities are intentionally **not implemented in v0.1**, but must remain visible in docs and presets:

- `mock-interview`
- `interview-retro`
- `web-assisted` research
- `deep-research` interview trend analysis

## Why This File Exists

`offer-skill` ships a smaller first release on purpose:

- local materials only
- case persistence
- `resume-eval`
- `project-highlight`

That narrower scope should not erase the broader product direction.

## Deferred Workflow Intent

### `mock-interview`

Planned purpose:

- generate interview flows tied to a target JD
- use resume and project evidence to shape question sets
- eventually incorporate sourced interview trend inputs

Current state:

- documented
- present in workflow presets
- blocked from execution in `v0.1`

### `interview-retro`

Planned purpose:

- review real or mock interview performance
- separate knowledge gaps from expression gaps
- compare candidate perspective and interviewer interpretation

Current state:

- documented
- present in workflow presets
- blocked from execution in `v0.1`

## Deferred Research Intent

### `web-assisted`

Planned purpose:

- support sourced external interview materials
- gather recent role-specific question patterns
- improve realism of later `mock-interview` outputs

Current state:

- documented
- present in research-profile presets
- disabled in `v0.1`

### `deep-research`

Planned purpose:

- perform deeper interview trend analysis by role, stack, and company type
- preserve source grounding and recency metadata
- support higher-confidence interview simulation and retrospectives

Current state:

- documented
- present in research-profile presets
- disabled in `v0.1`

## Contribution Guard

If you change presets, scope files, or roadmaps:

- keep all four capability names intact
- do not rename them away
- do not remove them just because they are not yet executable
