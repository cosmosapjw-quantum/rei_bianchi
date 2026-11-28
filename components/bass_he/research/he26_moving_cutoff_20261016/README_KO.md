# BASS_HE HE26: positive source spectral-cut and angular threshold diagnostic

2026-10-16 KST. Parent immutable [HE25 PR #72](https://github.com/cosmosapjw-quantum/BASS_HE/pull/72) exact head `eb4952af1f3d9ca99aad300ddf6db6f2b2fe1233`. This is an independent **source-only local sandbox** research implementation, not a change to original native Grackle or production photon transport.

## Physical construction and verified code

The exact non-tilted LRS Bianchi-I Killing-energy factor, Jacobian and three Verner H/He threshold preimages are derived in [stages/R5_DERIVATION.md](stages/R5_DERIVATION.md). A real source-only [portable moving cut implementation](src/portable_cut_core.py) returns **true** positive child photon N/U, HI/HeI/HeII source-weighted photoevent and photoheat integrals on each original HE25 momentum panel. The code does not silently recover spectrum from arbitrary parent N/U or reapply source angular Jacobians.

[tests/test_portable_core.py](tests/test_portable_core.py) is the exact-byte verified focused test source. Original HE25 `physics.Model` uses 4-node GL per fixed momentum panel, with narrow endpoint panels kept at `parts=1` for `hi/lo<=1.01` independent of m. The original published HE25 baseline source mean and m4/a4 256 modes were reproduced before comparing to independent physical-birth-variable QUAD.

**Sandbox actual evidence**: 27/27 local Python tests PASS, 108 distinct source moment quadratures `q=-.005,0,+.005`, regular m4/8/16, angle4/8, 6 times, plus 24 manufactured angular near-cut quadratures (signed q × 3 Verner thresholds × 4 Gaussian orders). Source HE21 BB50K/Verner source SHA256 `3df86063f12e238ec41219343a016b3a5086d18ce973015c335ec8118d9a5b66`.

| Error versus independent physical-birth QUAD | Baseline HE25 fixed GL4 | Exact spectral-cut clipped |
|---|---:|---:|
| Raw emitted source N relative, interior | 2.189808942e-5 | 1.110223025e-15 |
| Mean E absolute eV, interior | 1.462107331e-4 | 4.618527782e-14 |
| Largest species photoevent kernel relative | 1.429737335e-4 | 4.218847494e-15 |
| Largest species photoheat relative | 2.386714005e-5 | 1.998401444e-15 |

For the source-only `q+.005,m4,angle4,x=.37X` child registry, 64 parent intervals yield 72 positive supported children, normalized N=1 and mean E=20.276595394910 eV. Each child has no interior H/He fit threshold crossing.

**Manufactured** exactly near-cut discrete photon shell test (not the stellar continuum): global GL32 worst absolute angular difference `0.0051503308985927365`; exact event-cut-panel GL8 worst `5.551115123125783e-17` against independent SciPy QUAD. Never interpret this shell's large relative angular contrast as a physical CMB or EoR error.

### Discovered independent-reference defect

The first 9/24 numerical tests failed because unscaled SciPy QUAD used default absolute tolerance large compared with sigma ≈10^-18 cm²; relative photoheat discrepancy ≈2.079e-10. Scale the cross-section integrand by 10^18 **before** QUAD and then restore cm². The original strict relative acceptance was **not widened**; after repair 24/24, then 27/27 tests pass.

### Progress and scientific ceiling

DAG: R2 source read PASS → R5 derivation DERIVED → C5 donor IMPLEMENTED → C6 27 tests PASS → C7 source moment PASS → C8 conditional quadrature tests PASS → C9 first-failure/reference scaling review resolved → C10 delivery. **HOLD:** source donor has NOT been wired into native original HE25 photon+H/He chemistry; full time/energy/angle solver convergence and observational/CMB EoR are not certified. Native Rust/NCP this turn NOT_RUN; native subagents NOT_RUN (host does not expose dispatch).

The exact original machine-readable 108+24 case CSV, full Python independent runner and restored original HE21 source are included in the immutable sandbox research archive, with source manifests, test logs and SHA; this Git research branch publishes source-scoped theory, tested portable ABI, exact associated scientific summary and handoff. Stage-cloud direct upload was blocked by a container-session-expired error; do not infer Dropbox or Google Drive create-only success from the GitHub publication.

Related separate lanes: [rei_bianchi PR164](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/164) source-age signed shear, [PR165](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/165) H/He RR/DR, [bass_cr PR75](https://github.com/cosmosapjw-quantum/bass_cr/pull/75) common-q adapter. Primary background: [Mirocha et al. (2012)](https://arxiv.org/abs/1204.1944); [Friedrich et al. (2012)](https://doi.org/10.1111/j.1365-2966.2012.20449.x).
