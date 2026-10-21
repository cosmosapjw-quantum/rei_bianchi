# Cross-repository latest source intake

Read-only intake. No scientific integrations, tests, builds, production edits or publication performed.

Coverage: all **805 accessible branch refs** and their **805 HEAD commit metadata** were fetched (0 metadata failures), across paginated branch pages 1/2/2/3/2. There are **84 HEADs dated since October 17** and **81 all-state PRs updated since October 17**. PR lists were sorted newest update first and stopped only after reaching an older item. Commit dates are not branch-ref update timestamps. No October 22 commit was observed; latest observed head is October 21 15:16:49 UTC. Selected actual sources and receipts were read; this does not claim every file, all historical PRs, private conversations or host results were inspected.

| Repository | Refs | Latest PR | Actual branch HEAD |
|---|---:|---:|---|
| BASS_HE | 90 | 85 | `e8bb035d31f59e34734947b9082bdbd60128b799` |
| WU088_HH | 142 | 133 | `9a9f5c16ddf3c9fe98bfbcae6ee1f0cf1ae5ea15` |
| bass_cr | 172 | 95 | `8dc5031b3323d4be42a7444843294200aa8887f2` |
| BASS | 264 | 179 | `d14652646c1da77b6513e7f97725ff5dd5c1db4e` |
| rec_bianchi | 137 | 119 | `a949529872eb5ba0e20c7e206fe893e5d544e48c` |

The PR95 API still advertises content head `e7729092abc6edbe74f31d0ed82aa84d5506b8d5`, while the branch inventory and its commit metadata confirm document head `8dc5031b3323d4be42a7444843294200aa8887f2`. The body separately identifies NCP acceptance content `038aa0c8e5790f5c94e596035ea816fbca588a15`. Keep these roles distinct. Root AGENTS were read at the latest HE/HH/CR pins. BASS/REC root AGENTS returned 404 and complete recursive trees confirmed none; BASS's vendored C15 REI AGENTS was read. CR full recursive-tree retrieval failed, so selected paths were retrieved through directory and PR-file endpoints instead.

## Concrete reuse order

### 1. Adopt exact reflection-even four-tower compact23 representation for L8; one FV moments evaluation per RHS

Source: BASS_HE PR85 e8bb035d31f59e34734947b9082bdbd60128b799.

Read actual compact_transport.py and independent review. Prior 6 exact matrix checks, 12 RHS states, 4 full-window IVPs reported in source receipt. Max full-state differences 2.1252e-10 and 9.4475e-12 at unchanged DOP853 tolerances.

Compatibility: Compatible if odd multipoles remain zero, isotropic gas-energy placeholder excluded or separately supplied, photon-only Thomson damping retained; not HH75 collisionless 8→3 reduction. Compact initializer takes sigma norm + orientation, so preserve signed initial Sigma through orientation.

Claim ceiling: No new chemistry result; no speedup measured.

### 2. Prepare immutable canonical FV packet arrays once; bounded batched outputs; preserve all A-dependent weight/normalization bindings

Source: BASS_HE PR84 / REC119.

HE31 actual source confirms dot reductions differ from original sum order, so tolerance parity not byte parity. REC119 frozen81-state parity and finite coupled checks exist.

Compatibility: Portable to fixed finite canonical FV geometry z20→2, with same mass, cells, quadrature, normalization; no source extrapolation.

Claim ceiling: HE31 donor real support z>=4. Do not extrapolate donor to z2; use newly defined atomic network.

### 3. Prepare A-independent Gauss/mass-shell geometry; rebuild A weights, packet/cell populations, energy normalization and number for every case

Source: bass_cr PR93 0f45d0a422d79ccead565a8abaab860fcc230687.

Actual source read. Source claims constructor15/moments45 and saved375 states byte parity, source ODE replay prohibited.

Compatibility: PR147 canonical FV family; preserve A*numerator/2 evaluation order, not predivided P2.

Claim ceiling: No speedup/RSS measurement; CR95 only z20→4 offgrid4, completed129 guard.

### 4. Reuse implemented 21-state isotope/charge generator, per-isotope scaling and analytic rank-one electron-feedback Jacobian in 62-state coupled API

Source: rec_bianchi PR119 a949529872eb5ba0e20c7e206fe893e5d544e48c.

Actual atomic_network.py, coupled.py, atomic scope, StageB status and independent code review read. 21 atomic checks, 81 optimization states, 15 coupled JVP directions, 13 runner checks reported; actual125 pilot NOT_RUN.

Compatibility: n,H1,D,T,He3,He4,Li6,Li7 q0..Z, derived electron. Isotope-blind electronic rates explicit; photo+RR+DR, zero-inventory n/T, prescribed T>=100K and UV<=200eV, baryon test-fluid.

Claim ceiling: Not self-consistent gas/UV energy closure; no CI/CX/molecules/fusion; neutral Li inner-shell single-charge yield assumption. Must not silently combine with HH78 conservative-gray closure.

### 5. Reuse exact binary64 (x,b) moment cache and completed-science-ID planner; optional reflected native kernel only within its own warm C15 family

Source: BASS PR177–179.

Read cache, C++ kernel and moment_response. PR179 reports NCP5x2 admitted, all40 gates; PR178 140 kernel points and 5 reference/native pairs; no new run here.

Compatibility: Operational patterns portable. C++ hardcodes 96 radial and16 paired angular nodes of original32, not canonical FV24x12 Gauss3. Warm interval a=.1999→.2 is not z20→2 validation.

Claim ceiling: No end-to-end speedup claim. 729 completed baseline must return no-work.

### 6. Use signed-sector tensor/norm conventions and first-exit cell enclosure method as optional later certification path; reuse HH75 collisionless reduction only for collisionless controls

Source: WU088_HH PR132–133.

Read PHYS78 contract, HH75 radiation_flow. PR132 reports one actual initial cell, three four-cell NCP requests READY_NOT_RUN; PHYS78 is intake/contract only.

Compatibility: HH75 exp(M delta b) invalid when time-dependent Thomson damping does not commute with transport. HH78 assumes conservative gray source reservoir, unlike REC119 external thermostat/UV.

Claim ceiling: HH_R10 remains OFF; no physical HH rate, all-window certificate or isotope campaign completion.

## Most important current-state distinctions

- CR95 PR metadata head e7729092 differs from actual branch 8dc5031b, both retained; PR files endpoint only reflects93 files at content head, not152 final documented files.
- REC119 PR body stale StageA; actual pinned source has StageB implementation, checks and audit, but no actual125 pilot/figures.
- HE85 compact optimization complete_scoped; atomic physics/coupled sweep still pending. HH133 contract only.
- No Oct22 commit observed in 805 head metadata; latest observed is Oct21 15:16:49Z.
- Tensor convention sigma=diag(-s,-s,2s), pi_A=diag(-p_A,-p_A,2p_A), signed sum before norm; full Frobenius sqrt6; half contraction sqrt3; stress energy-density conversion kappa_t=8piG/c².
- All-isotope registry completeness is not reaction completeness or all-charge occupancy. Preserve explicit reduced operators and unresolved processes.

REC119 is further ahead than its PR description: actual Stage B code includes photo/RR/DR, 21 nucleus/charge states and a full analytic Jacobian. Its 125-case full-window run and figures are still explicitly NOT_RUN. This is the strongest immediately reusable isotope implementation here, but its prescribed-temperature/external-UV, test-fluid closure differs from HH78's planned conservative gray reservoir. Choose one declared model; do not transfer numerical acceptance across those closures.

HE32's compact23 is the strongest direct transport optimization for the new pilot: all four even towers survive and photon Thomson coupling remains available. Its supported sigma input is a nonnegative norm plus orientation; a signed Sigma front end must preserve orientation explicitly. Its independent review records tolerance parity, not bitwise parity. HE31 prepared moments also changes reduction order. CR prepared geometry is the alternative for exact original constructor/reduction-order reuse. BASS native reflected quadrature is a different warm C15 quadrature and cannot be dropped into canonical FV without a new adapter and targeted parity checks.

The HH75 8-to-3 reduction assumes collisionless transport and cannot simply eliminate photon moments once ne-dependent Thomson damping is active. REC119's isotope-scaled abundances and rank-one electron derivative are portable into the intended pilot. All-ion support includes LiIV, but soft UV below the Li thresholds leaves some states unpopulated. A complete state registry does not establish a complete nuclear or chemical network.

## Completed work to consume, not repeat

- HE29 references4/canary1; HE30 saved237 and D8 brackets; HE31 donor pair/reference; HE32 original/compact four IVPs.
- CR125 plus offgrid4 =129 unique input cases; PR94 NCP4 duplicates the sandbox4 coordinates, so do not count133 or repeat them.
- BASS warm729 and native NCP5×2, admitted by ACCEL03; ACCEL03 has no remaining execution action.
- HH1231 collisionless histories, finite-memory analyses and the one accepted PHYS77 cell; HH_R10 stays OFF.
- REC175/237 saved trajectories, REC118 local tangent checks/tiny wiring; REC118 three full-window tangent jobs are separately READY_NOT_SUBMITTED.

All execution quantities above are attributed to retrieved source/receipt reports. This intake did not rerun or independently validate their numerical arrays. The companion JSON stores exact PR/head metadata, selected changed-file inventories, source contents, compatibility limits and the three recent branch-only heads. Full 805 head metadata is in CROSSREPO_HEAD_DATES.json; raw recent PR data is in CROSSREPO_RAW.json.

