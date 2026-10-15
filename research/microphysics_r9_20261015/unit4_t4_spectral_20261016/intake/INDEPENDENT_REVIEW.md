# Independent C10 scientific review

Decision: `PASS_C10_FINITE_MODEL_RECOVERY`, restricted to the fixed-nucleus, point-nucleus, nonrelativistic three-electron Li to Be+ common-space sudden ground projection and unresolved complement. The reviewer was read-only and did not implement the collection tool or run the solver.

The reviewer checked the recovered source, contract, input, receipt and NPZ identities, 18/18 manifest entries, and 86/86 collector gates. The terminal attempt ended 2026-10-15T15:50:09.842211Z with `finite_model_computed`, exit 0, wall 4932.148 s and supervisor peak 8.8232 GiB. At 23:03 UTC, no matching process or access gap was observed. The NPZ is 9,130,341 bytes, SHA256 `7aa230b66d500e7637161589533eef4f3f4efdc13f4beafb7e28fd275ab82c5d`.

| Gate | Li parent | Be+ daughter | Limit |
|---|---:|---:|---:|
| Original-H residual (Eh) | 4.308654214e-8 | 3.189816242e-8 | 1e-7 |
| Stored orbital metric | 1.017023749e-10 | 1.017023749e-10 | 1e-8 |
| Independent norm error | 2.220446049e-16 | 5.551115123e-16 | 1e-10 |
| Independent RDM trace error | 8.881784197e-16 | 8.881784197e-16 | 1e-8 |
| Stored spin error | 2.220446049e-15 | 4.773959006e-15 | 1e-6 |

Both FCI convergence flags are true. The retained space has 92 orbitals; CI arrays have shape `(4186,92)`, and required arrays are finite. Energies are −7.454809366923839 and −14.294193208284327 Eh. The independent NPZ calculation gave P_ground=0.5756391820077922, complement norm squared=0.42436081799220776, closure error 0, vector identity error 1.766984918e-16, and ground/complement overlap 6.284834886e-16. This check used Python 3.12.3 and NumPy 2.4.2; the NCP solver used NumPy 2.5.4, SciPy 1.18.1 and PySCF 2.14.0. The small last-bit difference is within the frozen tolerance.

The original-H residual, orbital metric and S² are solver-reported gates; the archive does not carry integrals to recompute them independently. The complement includes bound excitation and cannot be called an ionization probability. The reviewer identified a narrower executable next T4 diagnostic: projected Lanczos spectral measure starting from the saved complement under the same Be+ Hamiltonian, with ground removal, normalization, moment and Krylov refinement checks. That diagnostic needs a separately frozen execution contract and integrals. Exclusive physical continuum decomposition remains blocked on T2 outgoing Coulomb/exchange channels, thresholds and energy normalization. Electron capture requires a distinct contact/annihilation operator.

