# HE27 External Codex Handoff: integrate HE26 positive true-child donor into native HE25

Read and use (do not ask user to download files manually):
- HE25 immutable BASS_HE PR72 head `eb4952af1f3d9ca99aad300ddf6db6f2b2fe1233`, source path `research/he25_proper_birth_20261016/`.
- HE26 research branch `research/he26-moving-cutoff-positive-source-20261016`: `stages/R5_DERIVATION.md`, `src/portable_cut_core.py`, `tests/test_portable_core.py`, `results/RESULT_STATUS.json`.
- Original pinned Rust micro owner `cosmosapjw-quantum/rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`, keep unchanged.
- Compare only scientifically compatible constructions in rei_bianchi PR164/165, bass_cr PR75/76. Do not mix provider/source eras or zero/plus states at different cosmological epochs.

## Physical implementation work, not another process-only audit

Implement an opt-in HE27 adapter for the fixed conserved-momentum HE25 source `Model.source` and `BirthCell`. Resolve moving H I, He I, He II source/fit boundaries `chi_i/G(x,nu)` at **actual birth proper time**. Preserve `dN/dt=H dN/dln a`, physical birth-frame BB50K and exact total source budget, true positive child N and U, species cross section and heat kernels, original birth age/direction, proper nH,total and charge/number/energy normalization. Never reconstruct child spectrum from an arbitrary parent's first two moments. Do not blindly convert the source donor to global point photons, overwrite future opacity state, or reapply Jacobian/direction weight. Source attachment must be a conservative transaction with one injection owner.

First measured validation: q 0 and signed ±0.005, m4/8/16, angle4/8, x/X_END={0,.1,.37,.9,1}; compare the corrected source moments to **independent birth-frame physical (E,mu) quadrature**, preserve original HE25 GL4 negative controls as proof of bias. Source number N and U plus three photoevent and photoheat channels must be checked independently with sensible tiny-cgs integrand scaling (10^18 before SciPy QUAD, restoring cm² afterwards). The exact near-threshold angular shell with nu_cut=±0.47 should be used as a negative global GL test and positive split-Gauss test, but it must NOT become an EoR error claim.

Then integrate into the original native Case-A photon+gas step, only after fixing source injection compatibility, in an independent worktree. Preserve original Rust `igm_point_rhs` CI/RR/DR/thermal/escape/CMB owner; outer transport alone handles photon redshift/shear and gas adiabatic work. Run one pilot first, with saved exact input and source/binary SHA, then a bounded energy×time×angle refinement using actual identical source and cosmic clock. Compare with Radau/DOP853 on exactly the same *modified* semi-discrete physical RHS; do not compare changed source laws as if only integrators differed.

Retain original HE25 and HE26 untouched, new Draft PR and append-only evidence. After each completed R/C phase update `DAG_STATUS.json`, commit/push source/tests/results, create immutable full source+raw archive and source manifest. Perform create-only Dropbox + Google Drive uploads and authenticate full-byte readback; if unavailable state the exact cause and preserve GitHub. Final status must separate: (i) source-only exact cut quadrature LOCAL_PASS; (ii) native gas/photon integration; (iii) independent spectral/angle/time convergence; (iv) full EoR/CMB HOLD.

Current HE26 machine data: 108 source cases, 24 manufactured angular cases; 27/27 sandbox tests. Global HE25 original source rawN error 2.19e-5 vs exact positive cut 1.11e-15; largest photoevent kernel 1.43e-4 vs 4.22e-15. These are source-only errors and must not be described as cosmological ionic or temperature errors.
