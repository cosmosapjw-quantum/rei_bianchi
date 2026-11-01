# REI Bianchi IGM: original F05 tick [160,161] physical H/He/T preview

Date: 2026-11-01; repository cosmosapjw-quantum/rei_bianchi. ONE central F05 scientific unit, 0 new canonical nodes. Status: ORIGINAL_SOURCE_PHYSICAL_PREVIEW_GENERATED / ORIGINAL_OWNER_ADMISSION_HOLD.

## Source authority and objective

The original central REI IGM seeks a physically consistent inhomogeneous H/He photoionization and thermal history, with photon-group source closure, coupled in a later stage to Bianchi geometry and Thomson/LoS observables. The original 26-event 46,080-cell adaptive run stopped at accepted tick 160/131072. This new unit solves exactly the next original microstep [160,161] with the unchanged native MPRK22(1)+Alexander SDIRK2 physics, and publishes genuine spatial state and energy, NOT another optical-depth or source atlas.

Source TAR SHA256: a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b
Accepted parent numerical state SHA256: cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01
Native kernel SHA256: 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644
Frozen parent PR350 HEAD: 38e32c7b23683930e788696bb65e923819678aac
Earlier common-parent PR348 HEAD: fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120
Original independent-output full/twohalf logT upper = 2.1245050576368385e-4, FAIL against strict 2e-4, preserved.

## Equations and computational meaning

The original conservative MPRK H(2) / He(3) corrector A p_out = p_in with A=I+B implies exact A Δp = −B p_in. Nonnegative original physical transition rates yield an inverse-positive conservative M-matrix, with ||A^−1||_1=1. We reuse the existing PR350 outward interval residual enclosure ||Δp−z||_1 ≤ ||b−Az||_1 for arbitrary numerical trial z and b=−B p_in. There is no new estimator.

For gas U=(3/2) k_B T (N_H+N_He+n_e), original fixed nuclei and native Alexander-SDIRK2 thermal roots imply Δ ln T = log1p(ΔU/U_in) − log1p(Δn_e/Npart,in), with ΔU=h[(1−γ)Rγ+γRfinal] and γ=1−1/sqrt(2). Exact full-step minus two-half-step defects are enclosed by shared-source increments. This is a DISCRETE MAP comparison; it is NOT by itself certified error against the exact continuous ODE flow.

## Actual physical data produced

All three original shape lanes ran exact native full/half1/half2 source maps on the connected Linux computer with exit code 0. One 46,080 spatial-cell dataset was generated; the three lanes share the same physical parent and are not independent astrophysical histories. Each lane has 46,080 rows by 27 columns of H/He nuclei, ion fractions, source-normal gas temperature, free-electron number, gas thermal U, and correlated Δ lnT / Δne intervals. Each lane additionally writes PREVIEW_NONAUTHORITATIVE_TICK161.npz containing the actual computed five-population native endpoint intervals and log temperature, explicitly NOT an accepted REIADP1 state.

Source physical CSV SHA256 (all three identical): 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d
Unapproved state NPZ SHA256 (all three identical): 2919b8a506c98911c5c4bffeb56327d3c8e45e8ba2abfa41dc11ec1b01f534a4

Physical source-domain totals, all using original input/model units:
- Source H nuclei 5.523438018661131e66; He nuclei 4.363516034742294e65.
- Tick161 free electron total N_e between 5.960306646847429e66 and 5.960306998498221e66.
- Tick161 gas thermal U between 3.372024144255893e55 and 3.3720305043537067e55 erg.
- Spatial Tgas between 2096.669317523477 and 66261.73002470825 Kelvin.
- Spatial xHII 0.9927160103598534 to 0.9999970269227849.
- Spatial xHeII 0.9828386604579787 to 0.9996056173279568.
- Spatial xHeIII 0.0003829672930191433 to 0.015960243553536497.
- Original one-tick correlated total free-electron change between −1.5661331419664924e60 and −1.5534971180107392e60. This is a SOURCE-DOMAIN, one-step net decrease, NOT observed universal IGM evolution.
- One-tick ΔlnT absolute max upper 7.696852786234425e−5.

Original source M-matrix candidate four-channel full/half local-map difference upper bounds: logT 5.387144148931529e-6, xHII 5.998277644160958e-6, xHeII 4.55075870552145e-6, xHeIII 4.550636330824591e-6, each < 2e-4 over all 46080 cells. Original output max width 2.257243260856967e-4 < frozen 2e-3. All original 14/14 H/He/photon/OTS/energy ledger intervals contain zero; no native table events. Original native source and history unchanged.

## Independent data validation and hostile review

Standalone stdlib auditor read EVERY original 46,080-by-27 row, for all three lanes. Checks: original source state/kernel SHA references, per-node nuclei/fraction cones, free-electron charge identity from H/He ion fractions, thermal U=(3/2)kB Npart T, correlated electron/logT increments overlap actual native endpoint intervals, source area totals versus rowwise sums, original 14 ledger and table/width gates, all 3 lane exact local byte identity, NPZ six-array names and CRC, no REIADP1 accepted-state masquerading. PASS 3/3 original lanes, one physical dataset. Normal 7/7 and Python -O 7/7 synthetic/negative tests PASS, including impossible He fractions, electron charge failures, disjoint native increments, zero temperature, and bogus node order.

Self hostile review: (1) A numeric step doubling defect is not the full continuum ODE truncation error or a validated complete cosmological 131072 tick trajectory. (2) Original SOURCE OWNER scientific contract requires exact predecessor classification and endpoint parity. The newer incremental estimator changes acceptance behavior and cannot be silently substituted into that locked protocol even though it is a conservative bound for the *discrete* difference. (3) The original interval code uses IEEE754/nextafter and native Krawczyk/BLAS; no separately verified full MPFI/MPFR correct-rounding proof. (4) Source clock and electron/geometry frame are not a currently observed IGM likelihood or coevolved Bianchi radiation transfer. (5) The local optional NumPy extension mismatch warning is a runtime_environment issue and did not stop original native jobs; CI clean-room replay to be judged separately. (6) This is same-author adversarial verification, not a distinct-author blind referee.

Literature comparison: Kopecz and Meister, Applied Numerical Mathematics 123 (2018) 159–179, DOI 10.1016/j.apnum.2017.09.004, positivity/conservation of MPRK; Mullier, Chapoutot and Alexandre dit Sandretto, Optimization Methods & Software 33 (2018), DOI 10.1080/10556788.2018.1459620, validated local truncation error requires comparison with exact flow and additional bounded Taylor remainder. These papers do not formally certify original REI calculations.

## Authority and DAG/drift watchdog

ORIGINAL_ACCEPTED_TICK=160/131072. TICK161=NONAUTHORITATIVE_ORIGINAL_NATIVE_PHYSICAL_PREVIEW. CENTRAL=28/88_REPORTED; WORKING=33/88_REPORTED; PHYSICAL_FAST=4/7_REPORTED; CANONICAL_DELTA=0. PRODUCTION=HOLD. NO_MERGE, NO_FORCE_PUSH, NO_TOLERANCE_RELAXATION, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.

This is ONE science unit, not 20 independent DAG nodes. Original worker/source/main/production unchanged; the preview format purposely cannot be read as the old accepted state. Next exactly one source-owner acceptance protocol decision: determine whether new versioned common-parent local discrete defect can replace original independent-output estimator while preserving all 14 energy/photon/nucleus ledgers, source identity, table event, model clock, exact three-lane behavior, and separate continuum physical error obligations. If source-owner admission is not justified, retain this source-authentic physical preview without promotion. Do NOT produce a fourth/fifth error estimator or unrelated source atlas; do not auto-run tick162.

## Reproduction and storage

Source preview: research/rei_f05_original_tick161_preview_20261101/owner_tick161_preview.py
Source physical audit: research/rei_f05_original_tick161_preview_20261101/audit_preview.py
Tests: research/rei_f05_original_tick161_preview_20261101/tests/test_preview.py
Workflow: .github/workflows/rei-f05-original-tick161-preview.yml
Independent local science: /home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101
Original frozen source local checkout: /home/cosmosapjw/worktrees/rei-f05-mmatrix-residual-20261101
GitHub branch: research/rei-f05-original-tick161-preview-20261101
Final GitHub Actions source CI / artifact and binary backup status must use actual provider ACK; never infer success from scripts being present.
