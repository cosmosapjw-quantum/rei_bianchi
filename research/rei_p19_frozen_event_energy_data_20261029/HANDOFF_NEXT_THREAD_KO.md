# REI 물리 데이터 우선 연구 인수인계: PR266→Event-rate compat + frozen-energy port

$physmath-research-loop $scispace $exa $wolfram

PROGRAM=REI_BASS_FULL_EVENT_RATE_COMPAT_20261029
FOCUS=ACTUAL_SOURCE_DERIVED_PHYSICAL_DATA_NOT_PERFORMANCE
PARENT_PR=266
PARENT_HEAD=a3470c88b4bddb38a08623d37ff6aa61210e04ae
BRANCH=research/rei-bass-event-rate-compat-20261029

ORIGINAL_WORKING_DAG=33/88
ORIGINAL_CENTRAL_DAG=28/88
PHYSICAL_FAST_DAG=4/7
PHYSICAL_DELTA=0
F4=PARTIAL
L4_ready=false
NO_MORE_IVPs=true
NO_FORCE_PUSH=true
NO_MERGE=true
AUTO_NEXT_NODE=false
SCOPED_WORKFLOW=18/20_AFTER_GITHUB_FINAL_READBACK_IF_ACKED
DIFFERENT_AUTHOR_R6_C9=NOT_RUN

## Read before doing work

Current GitHub branch `research/rei-bass-event-rate-compat-20261029`, directory `research/rei_bass_full_event_rate_compat_20261029/`; inspect exact HEAD and stage ledgers and latest PR268, PR269, PR267, PR266 separately. Read `physical_frozen_data/REPORT_KO.md`, `physical_frozen_data/RESULT.json`, the five exact SHA-locked original PR261/PR262 files, source code and three images.

## What is new and closed in physical scope

- Puchwein 2019 fiducial **non-equilibrium D1** source model: 13 selected z knot rows ×6 moments, plus per-event mean excess energy and photoionization time scale.
- Frozen REI 7 selected z snapshots (stored from a different REI model) with P19_D1_fiducial and P19_D1_BB13_GLs_nominal: 14 epoch summaries, 98 original 17-state ion-event records and 14 charge/baryon/energy ledgers.
- Reference: `Q_heat=Σ y_j h_c`, `Q_ion=Σ I_j y_j Γ_c`, `Q_abs=Q_heat+Q_ion`, `d y_e/dt=Σ y_j Γ_c`.
- Actual Python 19/19, prior source17.run_saved 7/7 cross-check, independent mpmath85 56/56 ≤3e-14 relative, Wolfram energy residual zero, figures inspected. No new IVP.
- At z=3.6030195933, fiducial electron creation 3.8104562e-16 /Href/s, heat 1.7777718e-15 eV/Href/s. BB13 calibrated 3.4297745e-16 /Href/s and heat 1.6001644e-15 eV/Href/s.
- Conditional P19-frozen rate tables are not observational data, not source-consistent dynamical REI recomputation, and not a calibration of actual BASS radiation field. The 13 published rows are a source-pinned selected subset, not the complete 2019 catalog.

## Physical next-node suggestion with provenance gates

NAME=REI_PHYSICAL_COMMON_BATH_EVENT_COUPLING
PRECONDITIONS:
  - original REI photon spectrum, helium CR/photo-nuclear channels and P19 source D1 consistency
  - one source-matched 17-state+hidden Li6/T/fast-reservoir isotope inventory and rate/energy ledger
  - actual BASS native full21 rate coefficients and common clock + electron feedback
  - H(z), nHref/nb, K and distinct physical directional redshifts
  - genuine independent-author R6/C9 before physics promotion
METHOD:
  - finish the source-owner event-by-event coupling and mass/charge/energy budget, not a new ODE or optimization run
  - output actual source-consistent reference data, not synthetics or future hypothetical forecasts
  - only count canonical DAG nodes where their own input/acceptance gates actually pass
  - never transfer previous budgets or mark unknown overhead zero

Each stage must record scoped completed/20 and canonical working33/88, central28/88, physical-fast4/7 with physical_delta0 until an actual authorized node closes. Per-stage GitHub commits and Library/Drive/Dropbox ACK have distinct identity types. Preserve and report prior failure logs. If remote ZIP upload fails, deliver actual local ZIP, GitHub source and explicit backup-failure status.
