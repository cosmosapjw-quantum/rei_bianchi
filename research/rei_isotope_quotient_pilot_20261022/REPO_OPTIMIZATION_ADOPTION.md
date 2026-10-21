# Repository optimization adoption

This recovered map records seven source repositories. **Only the additive `rei_bianchi` pilot was implemented and executed here.** Its existing 83 IVPs and final scoped independent decision are unchanged. This document is reconstructed from durable source intake and actual portable code, not a new experiment or audit campaign.

## Exact selected source pins

| Repository | Selected branch | Exact HEAD | Pin meaning |
|---|---|---|---|
| rei_bianchi | research/rei-hheli-sandbox-pilot-20261021 | 0d795da7f9114f89353c72a5829e5efcb64dfa44 | frozen PR218 donor, not claim of current latest REI HEAD |
| BASS_HE | research/he32-sandbox-primordial-pilot-20261021 | e8bb035d31f59e34734947b9082bdbd60128b799 | durable prior intake selection |
| WU088_HH | research/hh-phys78-sandbox-nuclide-pilot-20261021 | 9a9f5c16ddf3c9fe98bfbcae6ee1f0cf1ae5ea15 | durable prior intake selection |
| bass_cr | research/cr-c21n-offgrid4-sandbox-20261021 | 8dc5031b3323d4be42a7444843294200aa8887f2 | durable prior intake selection |
| BASS | research/rei-sigma-pi-sweep-analysis-20261021 | d14652646c1da77b6513e7f97725ff5dd5c1db4e | durable prior intake selection |
| rec_bianchi | research/rec-rei-hheli-sandbox-20261021 | a949529872eb5ba0e20c7e206fe893e5d544e48c | durable prior intake selection |
| vigilode | research/bassrei-port-20261021 | c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9 | latest observed branch HEAD by committer date; separate solver/FV research |

CR95 PR metadata HEAD is `e7729092abc6edbe74f31d0ed82aa84d5506b8d5`; the observed branch HEAD is `8dc5031b3323d4be42a7444843294200aa8887f2`. Both are preserved, not silently equated. Earlier inventories cover 805 refs in five repositories and 259 REI refs; the new VigilODE inventory covers187 refs/177 distinct HEADs. The combined1,251 references are observations from different times, not an atomic seven-repository snapshot. Enumeration does not imply full content audit.

## Adopted implementation and compatibility

### rei_bianchi — IMPLEMENTED_HERE_ONLY

Exact isotope quotient evolves 9 conditional fractions and reconstructs 21 census outputs; L16 even transport 39 plus tau yields 49 states, compared with 58-state unreduced reference. Analytic atomic/common-electron cross blocks plus finite-difference geometry Jacobian; inherited Radau and model unchanged.

Source-backed 5–60 eV photo+total RR, prescribed 100–10000 K, atomic test-fluid; no DR/CI/CX/nuclear or closed gas/UV evolution.

Remaining: Existing 79 nominal+3 controls+1 reference=83 IVPs; existing final scoped C9 decision. Broader thermal/radiation/nuclear work remains separately scoped.

### BASS_HE — ADOPTED_COMPATIBLE_KERNELS

HE32 reflection-even compact four-tower transport and HE31 PreparedCanonicalMoments are present in pilot/code/compact_transport.py and pilot/vendor/prepared_moments.py; one prepared massive moment evaluation is shared through returned geometry.

Parity reduction removes odd zero modes and zero gas placeholder, retaining photon-only Thomson damping and separate photon/neutrino energy/number towers. Finite FV24x12 Gauss3 and A-dependent normalization stay fixed. HE31 chemistry donor support is not extrapolated to z2.

Remaining: This REI lane does not complete HE32 own atomic/coupled sweep. Prepared reductions use tolerance parity, not byte equality.

### WU088_HH — SIGNED_CONVENTIONS_ADOPTED_COLLISIONLESS_REDUCTION_REJECTED_FOR_THIS_LANE

Signed tensor stress addition before norms and Frobenius sqrt6 convention are retained.

HH75 collisionless8→3 exp(M delta b) reduction is invalid for this variable electron/Thomson photon damping when damping and transport do not commute. HH78 conservative-gray reservoir differs from external prescribed UV/thermal REI closure.

Remaining: HH78 source is contract/intake only; HH_R10 remains OFF. Full-window certification and isotope execution are not completed by this REI pilot.

### bass_cr — GEOMETRY_PREPARATION_PATTERN_ONLY

Separate A-independent Gauss/mass-shell geometry from A-dependent weights, populations, energy normalization and number. Current code constructs the pinned FV distribution per case and prepares its moments.

No claim that a cross-case CR cache was ported. Preserve A*numerator/2 order, actual canonical cells and normalization. CR95 branch/pr head mismatch remains explicit.

Remaining: CR offgrid4 source interval z20→4 and completed129 guard remain separate; no donor ODE replay or claim of z2 validation.

### BASS — OPERATIONAL_PATTERN_ONLY_NATIVE_KERNEL_DEFERRED

Reuse exact state identity and completed-science-ID/no-work principles; cached immutable geometry and full-cost accounting are relevant patterns.

Warm C15 native moments hardcode96 radial x32 angular (16 reflected pairs), unlike this canonical FV24x12 Gauss3. a=.1999→.2 warm validation does not validate z20→2. No C++ kernel swap.

Remaining: Preserve completed729 baseline; source-local admitted results remain source-local. Future finite-FV compatible kernel requires its own bounded contract, not a pilot rerun now.

### rec_bianchi — PATTERN_ADOPTED_CLOSURE_NOT_IMPORTED

REC119 shared-electron feedback/rank-one Jacobian structure informs Jff=(P+ne R+outer(Rf,w))/H; isotope quotient is derived under this REI contract.

Do not import REC119 different 5–200 eV support, RR+DR, neutral-Li inner-shell single-charge-yield assumptions or its full 21-state/62-state API. Current REI uses 5–60 eV and total RR only.

Remaining: REC119 reports implemented coupled checks but its actual125 pilot was NOT_RUN at intake. Its own execution remains separate.

### vigilode — AUDIT_LESSONS_ADOPTED_SOLVER_SWAP_DEFERRED

Count hidden derivative RHS and factorization/setup work; distinguish application error from internal tolerance and warmed solve from process wall. Latest report/result status is incorporated below.

No VigilODE solver, Schur/remap or photon-FV adapter enters the frozen Radau/isotope-quotient lane. Upstream scoped heat/FV evidence is not REI trajectory admission.

Remaining: P02 FAIL stands; P02b has preregistration only at exact HEAD. P03-P06 and broad production remain HOLD; followup heat size/arm/driver questions remain a separate upstream DAG.

## Latest VigilODE evidence

- **research/ncp-followup-fvm-20261021** (`5fd6e459a3f67cee90e002821b9b4b740c47475b`): One commit ahead of external-audit anchor; compare reports 104 changed files. Opt-in analytic heat Jacobian, band/border Schur preconditioner, conservative remap and LRS scalar cold-Thomson oracle are implemented upstream. Upstream report states 9/9 scoped commands, 19 Rust and 15 Python tests. These are read reports, not checks run here. Corrected archived rotation acceptance is 7/140, all seven at internal rtol=1e-10; this does not establish general production accuracy. Shared electron/rank structure and explicit operator-work accounting are compatible design lessons. Frozen REI finite Legendre transport, atomic closure, exact quadrature and Radau solver remain unchanged.

- **results/ncp-followup-fvm-5fd6e45** (`fbbc832fdf942396155c12b04c30e63dc67fefe9`): One commit after 5fd6e459; tree diff is additive audit evidence, with no modified or deleted blobs. README and report v2 describe periodic_heat n=128 with 41 outputs and original application rtol=1e-6/atol=1e-9; analytic-stencil and basis-JVP trajectories agree bitwise. Total RHS including derivative work drops 5712 to 336, removing 5376 derivative RHS calls. 489 paired blocks report descriptive median STEN/BASE warmed 0.586, process-wall 0.620, CPU 0.616; timing remains diagnostic_only/STATISTICAL_AUTHORITY_HOLD because simultaneous one-host blocks are not independent. No REI speed ratio follows. Manifest report records 102/102 matching source artifacts; not independently rehashed here. Broad production HOLD; manufactured Schur probe is not an ODE/BASS benchmark; multiple sizes, matrix-free/banded heat, allocation and tightened-tolerance arms remain unrun.

- **research/bassrei-port-20261021** (`c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9`): Six commits ahead of 5fd6e459; new fixed-grid LRS photon FV Rust adapter, analytic partial-time support, tests and P02/P02b materials. P02 stored full result and DAG say FAIL: C1-C5 and C7-C10 pass, C6 fails at gamma=1e6 because u_ref compares the method's own tight-tolerance result with Radau. Stored method-v-reference difference about 1.2e-11 is not solely reference uncertainty; Radau 1e-13 versus 1e-14 is about 3.59e-13. Post-verdict diagnosis does not rescore P02. P02b preregistration changes reference uncertainty to Radau self-comparison and records method floor separately; it discloses known prior outcomes and supplies no new blind evidence. Exact P02b tree contains only PREREGISTRATION.md and run_p02b.py, with no results.json/raw/DAG_STATUS.json. Hence no observed P02b PASS; P03-P06 remain blocked in available DAG and production HOLD. This fixed-grid photon-FV port is separate from the frozen REI isotope-quotient/Radau pilot. Do not infer validation of the latter from P02, or reject its existing 83 IVPs because P02 failed.

## Remaining work and existing claim

The existing `NEXT_DAG.json` remains authoritative for this REI unit. Publication/preservation closes the completed atomic lane. Thermal/UV closure,16 nuclear/capture/decay targets, repository-specific pilots, compatible native kernels and VigilODE integration are separate future work; none adds a new gate or rerun to this completed pilot. The19 total target channels comprise3 atomic and16 nuclear/capture/decay targets.

The claim remains `PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID`. In particular, source registry coverage is not a completed full reaction network, prescribed-temperature/UV trajectories are not a closed thermal/radiative solution, and a single quotient/reference pair is not a general speed theorem.

Sources: `intake/CROSSREPO_LATEST.json`, `intake/REI_HEAD_DATES.json`, `intake/VIGILODE_LATEST.json`, `intake/VIGILODE_BRANCH_COVERAGE.json`, `PHYSICS_CONTRACT.md`, `SOURCE_MANIFEST.json`, the four inspected code paths in the JSON, and the existing summary/final review. VigilODE exact HEAD/path/blob URLs are recorded in its branch-coverage JSON.
