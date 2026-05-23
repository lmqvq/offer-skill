# offer-skill PRD

Product name: `offer-skill`  
Subtitle: `A dual-perspective interview and hiring skill`

## Summary

`offer-skill` helps candidates and interviewers analyze resumes, project experience, and hiring materials from candidate, interviewer, or dual perspectives.

Its core model is case-based:

- store inputs once
- reuse them across workflows
- preserve outputs as assets
- support backup and rollback

## Primary Audiences

- Candidates
- Interviewers
- Hiring managers

## Core Workflows

- `project-highlight`
- `resume-eval`
- `mock-interview`
- `interview-retro`

## v0.1 Release Scope

### Shipping in `v0.1`

- `project-highlight`
- `resume-eval`
- local input handling only
- case persistence
- version backup and rollback

### Deferred After `v0.1`

These items are planned and must remain visible:

- `mock-interview`
- `interview-retro`
- `web-assisted` research
- `deep-research`

Do not delete or silently collapse these planned capabilities when evolving the repo.

## Core Principles

- Perspective changes emphasis, not facts
- Evidence must be stronger than vibes
- Outputs must be structured and actionable
- Local-only scope must be explicit in `v0.1`
- Deferred capabilities must remain on the roadmap
