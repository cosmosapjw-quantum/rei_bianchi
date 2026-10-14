# REI-F03 finite synthetic fixture reproduction

Scope: unchanged REI_SYNTHETIC_HHE_3GROUP_STATIC_V1, static proper CGS, Case-A instantaneous escaping recombination energy. Seven independent coordinates are fractions HII/HeII/HeIII, proper thermal u, proper primary photons N0/N1/N2. Electron density and T derive from neutrality and EOS; escape energy and event counts are auxiliary bookkeeping.

1. With Python/numpy/scipy available, run reference.py from repository root. It reads the original fixture and integrates independent coordinates five population densities plus lnT, photons, escape and event counters using DOP853 and Radau with fixed rtol2e-12 and component absolute tolerances. It compares the finite final reference points to1e-9 absolute and emits reference.json. This is numerical cross-check, not rigorous enclosure.
2. cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked. Frozen external hhe_events and hhe_fixture cover zero duration, charge/EOS, mixed and pure event and density limits, implicit residual/event/energy ownership, malformed inputs, transactional rejects and independent finite reference/refinement.
3. Python verify_candidate.py runs crate tests and the hhe_fixture example at dt1e9,5e8,2.5e8 through t1e12. It checks actual final endpoint data, energy/event residuals1e-12, strict local max absolute fraction/lnT full-vs-two-half discrepancy below2e-4, finite independent observable error below2e-4 and monotonic refinement.
4. hhe_fixture 1e12 separately exercises bounded rejection/bisection down to min1e3. This exploratory coarse-trial branch is distinguished from the three fixed refinement runs; it does not claim an accepted public width.
5. cargo fmt --check and strict library Clippy. Original excessive-precision decimal fixtures are retained; all-target Clippy may explicitly allow that lint only.

Wrap research entrypoints with CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project <repository-root> --task REI-F03 -- <exact argv>. Telemetry spools; export issues do not change numerical results.

Acceptance limitations: full BE and constituent two-half maps sample actual implicit endpoints. Returned full-vs-half differences estimate local error empirically. These point residual checks do not bound a whole state/site box, certify a uniform nonlinear remainder, root uniqueness, physical atomic accuracy, Peebles mechanism or a Bianchi history. F00 planned four-site contract is retained as historical design; F03 actual endpoint contract is separate.

Source-bound Peebles request: this Case-A ground-continuum toy has no retained excited n2 shell, thermal inverse n2 bath, Lyman-alpha escape, two-photon decay or QSS closure. PB01 selected model MODEL_SCOPE_MISMATCH remains, and PB02 should bind actual level/REC-owner source separately. Do not inject an external C-factor and label it derived recovery. Scientific admission HOLD.

Actual reproduction from a checkout without private working files:

```bash
mkdir -p .cuh/fastest-track/REI-F03
cp docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F03_reference/{reference.py,reference.json,verify_candidate.py,verify_boundaries.py,boundaries.rs} .cuh/fastest-track/REI-F03/
CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project "$PWD" --task REI-F03 -- /home/cosmosapjw/cosmo_lab/.venv/bin/python .cuh/fastest-track/REI-F03/reference.py
CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project "$PWD" --task REI-F03 -- python3 .cuh/fastest-track/REI-F03/verify_candidate.py
CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project "$PWD" --task REI-F03 -- python3 .cuh/fastest-track/REI-F03/verify_boundaries.py
```

On other environments use a Python with the NumPy/SciPy versions in environment.json and installed Rust. Telemetry unavailable: run the exact underlying argv, retain logs, and mark telemetry failure separately. Scripts assume repository root. Do not overwrite an unrelated private task directory; these fixed paths identify this logical task.

The one independent reviewer directly compiled and ran review-probe.rs against original candidate hashes in review-scope.json. It inspected nominal receipts. Three P2 findings were fixed by Host in one closeout: nonnegative helium production numerator, consistent neutral fraction parentheses, and rejection of nonfinite EOS intermediates. boundary-red.log records failed expected assertions before repair; boundary-green.log has seven assertions true afterward. Final repaired bytes were not sent for a second independent review. The example now observes state equality on every rejected candidate. No original fixture, frozen tests or acceptance tolerances changed.

Latest research Git receipt read6f264b14a5195dba8dc11150f0171c0377f4d7e1 adds FLRW01 after PB01. Source-bound information for FLRW02 is in runtime_inputs/hhe_solver_binding.json. Proper/static absorption and local species RHS are implemented; diffuse photon spectrum/count, cosmological threshold flux and filling geometry are outside this map. Peebles PB02 and physical FT07 remain deferred in research handoffs. No inference from escaped energy to ionizing recombination-photon count.
