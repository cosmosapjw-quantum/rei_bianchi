# Continuous-source H/He checkpoint

This additive opt-in continuous-emissivity implementation is accepted only for the manufactured homogeneous H/He fixture and tested grids. The original pulsed-source diagnostic FAIL remains unchanged. No claim of a continuum theorem, arbitrary-model robustness, Bianchi integration, observed EoR validation, new-path restart, or automatic LTE controller is made.

The reviewed final binary/source binding is in evidence/frozen-bin/provenance_masked_v1.json. Independently executed Rust tests: 223 PASS. Python suite: 22 PASS. The final candidate/reference CSV comparison has 81 rows, all frozen field criteria and dimensional ledgers PASS; worst allowance ratio 0.9212590357 (Gamma_heii). The earlier dense-output comparison FAIL is retained separately. Off-phase spectral refinement passes narrowly at 0.980896. The final run took 100583 accepted steps and uses fixed maximum timestep and fixed threshold-band quadrature.

The full 3,035,151-byte package is maintained separately in private backup storage; SHA256 71df0aad1739ce561eda7b16f7a773058ec401c5a129ae1e3a0e60823fce02e9. Backup restoration status is reported separately; this page does not certify remote full-byte restore. Large raw exploratory artifacts and the executable are not duplicated in Git.

Publication is on the existing separate draft PR84, branch forward/rem-hhe-igm-20261006, based on 4567b91785dbba1964fd807ab9c6873f542c1030. All earlier diagnostic evidence is preserved. This is not a merge or release. Existing full cargo fmt failures affect 12 unchanged legacy paths; remote CI must be read on the exact new commit. Local scientific and test acceptance does not imply green CI.

If rollback is later authorized, revert this additive checkpoint commit; do not delete immutable historical evidence or private archives.
