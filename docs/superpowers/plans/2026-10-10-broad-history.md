# Broad Reionization History Implementation Plan

> For agentic workers: execute the native plan with superpowers:executing-plans; keep a fresh final independent reviewer.

**Goal:** Obtain a source-pinned20→4 filling-factor history and scientifically bounded shear/sensitivity results now.

**Architecture:** Add an opt-in research module, importing existing Bianchi background constants and density normalization. Integrate the scalar filling factor and photon counters by an exact local reaction step; compare with an independent adaptive solver. Preserve native receiver and all original atomic gates.

**Tech Stack:** Python3, NumPy, SciPy, pytest, matplotlib; existing repository sources.

**Spec:** `research/broad_history_20261010/SCIENTIFIC_CONTRACT.md`.

## Global Constraints

All scientific constants, domain, closure and numerical budgets are fixed in the spec. No forced branch merge, production default change, CR/RCT promotion or old-suite replay. The user's explicit request to plan and execute supplies execution authorization; no redundant plan-approval pause. A new linked worktree isolates the code.

## Review Focus

- Distinguish volume filling factor from local ion fraction and He/thermal closure.
- Post-overlap photons must remain visible in the budget and must not imply radiation transport.
- Match baryon/source normalization, initial shear and mean-redshift labels across paired runs.
- Resume must reject mismatched config/code and incomplete evidence.
- Refinement must separate numerical error from physical model uncertainty; tau is a segment.

### Task1: exact reaction and broad history

Files: `research/broad_history_20261010/{model.py,tests/test_history.py}`.
Consumes: pinned background constructor and published R15/HG97 constants.
Produces: `advance_constant(q,A,B,h)` -> Q, integrated_Q, Nrec,Nemit,Nexcess; `history(config,nsteps)` -> arrays and metadata.

- [x] Write and observe failing analytic reaction/domain tests.
- [x] Implement exact reaction+overlap and source/background closure.
- [x] Run focused tests including conservation, input guard and FLRW background comparison.
- [x] Commit implementation milestone.

### Task2: whole-interval campaign and checkpoints

Files: `run_campaign.py`, `reference.py`, `evidence/`, `figures/`.
Consumes: history interface. Produces per-caseCSV+summary, exact identity checkpoint, convergence decision, adaptive reference, scientific plot and BASS six-column history.

- [x] Run complete20→4 paired campaign and nuisance scenarios at declared resolutions.
- [x] Check whole-history convergence and independent reference; retain first failures if any.
- [x] Check pointwise shear parity and photon budget; record actual runtimes.
- [x] Save checkpoint and commit.

### Task3: integrate research program and publish

Files: `REPORT_KO.md`, `DAG.json`, `BLOCKERS.json`, `RESUME.json`, `START_CODEX_KO.md`, per-repo sync return.

- [x] Map every latest blocker to baseline-resolved, external-input-required, numerical repair or preserved extension; do not erase old failures.
- [x] Fresh independent decision review with exact producer/source/evidence pins.
- [ ] Publish additive REI branch+draftPR and five repo-specific sync branches. No owner branch overwrite.
- [ ] Create durable evidence archive+Drive/Dropbox receipts and exact next prompt.
