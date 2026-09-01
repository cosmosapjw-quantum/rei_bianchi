# Tri-repository formula synchronization — REI lane

This directory is the REI-side manifest for the BASS/REC/REI control plane.

Canonical owner registry and compiler live in `cosmosapjw-quantum/bass` under `coordination/tri_repo_sync/`. This repository remains the unique authority owner for:

- late-time H/He thermochemistry;
- full-OTS event topology and conservation ledgers;
- the complete first canonical interval;
- reionization/opacity provider export.

REI consumes BASS conventions/background contracts and the REC recombination provider by exact commit pins. It does not copy or replace those formulas.

The current manifest preserves Draft PR #32's fail-closed boundary:

```text
STOP_INVALID
UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION
UNDECLARED_IMPORT: ntpath
NO_PASS_FIRST_CANONICAL_INTERVAL
NO_PROVIDER_EXPORT
```

The only admitted positive scope is the constrained FLRW thermochemistry microstep substrate already recorded by the project. This synchronization branch changes no production physics, runtime bridge, tests, or scientific claims. Scientific promotion, PR readiness, merge, and Jira completion remain manual.