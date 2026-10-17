# Cloud Phi birth clock and fixed-geometry cohorts

Additive research snapshot from local source commit `f520b29146a1975c82baf8b7a8698d97f75c3fb1`, on the PR183 source base `b0382198564c7e85e479d48011e880ef7c2c4d46`. Existing repository lanes, native defaults and the original 12 owner modules are preserved. No binary or build output is included.

## Read this chronology first

1. `docs/RESULT_KO.md` and `docs/INDEPENDENT_REVIEW.md` describe the first low-level stage: 21 new tests plus 68 existing tests (89 PASS), and 1,890 Rust scalar outputs checked against 450-digit mpmath.
2. `docs/COHORT_RESULT_KO.md` and `docs/COHORT_REVIEW.md` describe the final cohort stage: 9 new cohort tests plus 12 selected prior tests (21 PASS). The full 89-test suite was not rerun after the cohort changes. SymPy checks the constant-source ODE and semigroup residuals at zero.
3. `evidence/COMMAND_LEDGER.json` contains all 20 measured commands, including original failing attempts. Sums are 19.669065 seconds wall and 19.814236 seconds child CPU within the existing 300/600-second bounded cap. These are command-only costs, not total project costs or a fresh execution allowance.

Historical `NOT_POSTED` and `external_publication=false` fields are retained execution-time statements. This additive repository copy is the later publication step. No tests, oracle, build or scientific run were repeated during publication.

## Scope and HOLDs

The opt-in `PositiveAgeBridge::advance_fixed_geometry_phi` treats pre-existing photon cohorts with full-step exponential survival and constant-emission newborn cohorts with the Phi integral. It requires H=0, shear=0 and fixed geometry. Gas opacity is frozen at each step's initial state, so coupled evolution remains first order. The midpoint birth label represents an interval; it is not an exact birth-age distribution. Mixed legacy/Phi continuation outside the documented method contract is not certified.

Variable Bianchi source-on evolution, coupled second order, global age/angle/energy convergence and full native reionization histories remain HOLD. No merge or production adoption is implied. Clippy was not run. No Wolfram, user-computer or NCP execution occurred in this cloud phase. The unexecuted local/Wolfram handoff scripts were omitted; historical Wolfram assertions are not independently verified by this publication.

## Publication provenance

`PUBLICATION_PROVENANCE.json` maps original and published hashes. Absolute executor path prefixes in stderr were redacted; original outcomes remain intact. The bounded runner's executor-specific toolchain path was replaced with optional `RUST_TOOLCHAIN_BIN` (otherwise normal PATH); this portability-only copy was not executed. Original command-log output hashes therefore refer to pre-redaction bytes. `SOURCE_FILE_MANIFEST.json` records every published file except itself.
