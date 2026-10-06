# Independent review: low-temperature H/He point provider and RHS

Review date: 2026-10-06. Scope is the source-bound phenomenological point evaluator, not an integrator, radiation transport, empirical fit validation, interval certificate or cosmological prediction.

## Verdict

Contract: **confirmed for the bounded point slice**, with the explicitly approved strict recovered-EOS temperature admission policy below.
Quality: **confirmed for reviewed source state**, after one reproduced helium-simplex boundary defect was fixed. No remaining blocking finding was found. This does not authorize publication by itself.

This review was read-only for repository files. Scratch probes and independently rebuilt binaries were written under `/workspace/shared/igm-thermal-review`. Source identifiers and hashes below bind this verdict; changing those files requires another check.

## Independent evidence

1. Read the approved physics contract, implementation plan, complete provider/RHS, tests, C harness, and source density mapping. Selected source is Grackle 3.4.1 commit `af7939494ce65007887ada7b98d1813df6843346`.
2. Independently recalculated git blob SHA1 for upstream `rate_functions.c`: `e8e8a38148c8a6c8029eab6663c718b38b30b8ff`. Independently delimited all 14 C function bodies by brace depth and verified their SHA256 hashes against the manifest and exact presence in the C harness. This is a literal C reference independent of Rust provider execution, not a replay of provider outputs. An initial line-slicing hash check failed because extraction ends at the closing brace rather than all trailing line bytes; precise body delimitation then passed.
3. Recompiled the reference from repository-only bundled files: `gcc -std=c99 -O0 -Wall -Wextra -Wno-unused-parameter grackle_literal_reference.c -lm -o /workspace/shared/igm-thermal-review/repository_c_reference`; generated CSV and `cmp` against the bundled CSV exited 0. The source headers initially missing from the bundle were added before the final check.
4. `source /workspace/shared/rei-build-feasibility/env.sh; export CARGO_TARGET_DIR=/workspace/shared/igm-thermal-review/target; cargo test --locked --offline` exited 0: **166 tests passed, zero failed**. Fresh final log: `full-test-final.log`. Rate tests compare 17 values over 96 temperatures against independent C with relative tolerance 3e-13 and exact zeros; logarithmic domain grid and adjacent-representable branch/cap neighborhoods are included.
5. `rustfmt --edition 2021 --check src/igm_rates.rs src/igm_thermal.rs tests/igm_rates.rs tests/igm_thermal.rs` exited 0.
6. Independent scratch Rust grid `independent.rs`: 51 by 51 fraction combinations and four nominal temperatures, nH=1e-4 and nHe=1e-5 cm^-3. **8,836 admitted states** pass absolute CMB normalization against separately supplied coefficient `1.0178101728574782e-37`, binding-energy derivative reconstructed from species derivatives, and scale-aware material/escape/CMB ledger closure. The other 1,568 cases are explicitly diagnosed endpoint round-trip rejections, not silently skipped numerical failures; see approved policy. Log `independent-final.log`. An initial closure probe normalized to the tiny residual CMB term, an ill-conditioned choice; it was replaced by normalization to the sum of absolute ledger components, without changing production code.
7. Independent scratch `probe.rs` reproduced the mixed-He boundary bug before correction and succeeds after correction; `boundary-final.log` records final results.
8. Existing tracked `atomic_provider.rs`, `hhe_events.rs`, and `thermal.rs` have no git diff. The old raw 100 K guard and FT03 admission are not weakened by this additive provider. Existing suite remains passing. Foundation code is consumed through its unchanged checked EOS.

9. `cargo clippy --locked --offline --all-targets` exited 0. `clippy-final.log` contains existing repository warnings, with no diagnostics against `igm_rates` or `igm_thermal` sources/tests. This is not a repository-wide warning-free claim.

## Physics and API checks

- k4 is split directly into RR and DR, not by subtracting near-equal values. RR+DR reproduces original k4. DR events and matched cooling vanish when T/11605<=0.8. Raw reHeII2 remains visible as excluded cooling there. This is an explicit channel-consistency closure and differs from blindly summing all raw source cooling at low T.
- 1..1e6 K is documented as an operational phenomenological package domain, not empirical fit support. Source tiny CI floors and CE capped exponentials are retained. Diagnostics explicitly report entire floor-selected/cap-active channel contributions, not the difference from a hypothetical unclipped physical rate.
- ceHeI uses ne²*nHeII and erg cm6/s; other selected excitation terms use their correct binary density factors. Checked directly against upstream `cool1d_multi_g.F` lines 442–467. Free-free uses ne*(nHII+nHeII+4*nHeIII).
- H and He nuclei and charge follow a shared forward/capture event ledger. Absent helium has zero fraction derivatives. Species derivatives are chemical derivatives only, not expansion-diluted proper-density derivatives.
- CI transfers existing-owner binding energy from thermal to binding once and does not put threshold power into escape. RR/DR emit binding plus their selected source thermal cooling once. No approximate Grackle CI cooling or FT03 derivative moment is added. CE/free-free enter escape once. The binding derivative independently reconstructed from nHII, nHeII and nHeIII derivatives matches the supplied ledger.
- CMB is signed into the gas, zero at equal temperatures, scales ne*Tcmb^4*(Tcmb-T), and is not folded into nonnegative escape. Fundamental constants and exact blackbody expression reproduce the independent absolute coefficient. The equal/opposite CMB reservoir is documented.
- w RHS equals -2H*w+Q/nH. Temperature RHS includes changing-particle feedback, with a finite-difference EOS directional-derivative test. Proper-volume thermal equation recovers -5H*u+Q. No fraction dilution term or second particle correction appears.
- Publicly mutable state inputs are revalidated through EOS. Invalid fractions, NaNs/infinities, negative parameters, inconsistent zero-Gamma/nonzero-heat, arithmetic overflow and positive-product underflow are rejected without mutating the borrowed state. Outputs are not accepted as later trusted inputs. Zero electrons, zero/absent species, pure species and mixed fully ionized-He boundary are exercised.

## Findings and disposition

### F1: helium simplex arithmetic mismatch — fixed

Axis: contract and quality; category: boundary correctness; severity: medium; confidence: high.
Original `src/igm_thermal.rs` formed neutral He as `1.0-y-z`, whereas admission checks `y+z<=1`. With y=.8,z=.2, valid admission yields a negative sequential-subtraction residue, causing RHS error. Independent scratch reproduction used fractions [.5,.8,.2], nH=1,nHe=.1,T=100 K. Implementer changed to `1.0-(y+z)` and added `helium_simplex_boundary_uses_validated_sum_without_clipping`. Identical scratch call succeeds in final bytes; no clipping was introduced.

### F2: nominal endpoint temperature reconstruction — accepted explicit limitation

Axis: contract/API boundary; category: compatibility; severity: low after explicit policy; confidence: high.
General `IgmGasState::from_temperature` can round a nominal endpoint outside the provider envelope. Reproductions: fractions [0,.01,.01], nH=1e-4,nHe=1e-5, requested 1 K recover 0.999999999999999889 K; [0,.02,.02], requested 1e6 K recover 1000000.00000000012 K. Root explicitly chose strict recovered-EOS admission, without projecting thermal state, broadening the provider domain or modifying foundation. README, RHS API docs and `recovered_eos_temperature_is_strictly_admitted_without_endpoint_projection` agree. Scalar `igm_rates` accepts exact endpoints. Future integration must preflight actual recovered EOS temperature and use a representably interior IC where necessary; constructor success alone is not chemistry admission.

### F3: reference reproducibility bundle — fixed

Axis: quality; category: evidence reproducibility; severity: low; confidence: high.
The initially copied C harness referenced two absent headers. Exact pinned headers and license are now bundled, README gives offline reproduction, and reviewer independently compiled and byte-compared the repository-only reference successfully.

## Limits and next gate

No time integration, positivity-preserving stepping, cumulative floor/cap budgets, source history, photon transport, convergence history, observational calibration or remote deployment was verified. Those are separate later gates. This point slice must not be described as a complete reionization solver or as empirically accurate throughout 1..1e6 K. Existing source floors can control an extremely cold regime and must remain visible in later integrated budgets.

## Reviewed SHA256
310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf  src/igm_rates.rs
30515d96270ec73a37829ba298513a42112991168479d3cb40f33b67fd469ab2  src/igm_thermal.rs
b70e2817108ceb77f875a3ab522365186b09a97cadf2062decff1865f3d6ade8  tests/igm_rates.rs
043333afcdbf38df053e8eae7988e178825baeb7d8c98c16b7f760841ed9410c  tests/igm_thermal.rs
a085c6b50d804f73ee99e5ede3dd4390a49a0ff261d1c7cc145d6c029e6f80bb  tests/data/igm_grackle/LICENSE
2cea3c393da1d0ec55e8b2173b4226267a1f583e9625f530514c61a43469afc1  tests/data/igm_grackle/README.md
13a1b252a790dc32bdb765399841471a54765f1a390426ee5db821ce9589c594  tests/data/igm_grackle/grackle_literal_reference.c
50ece50b98792c6c0210d6b11e2aec29b4caa4acd96ff9e09a31274dcdff4565  tests/data/igm_grackle/grackle_literal_reference.csv
1e4e076f94f4e4e2b6cadaa830ffb628a4ca54143b27e843db7631372c2bdc63  tests/data/igm_grackle/manifest.json
716e17085df3fe3650dca47502739868a8851c8c11690310e74333fb97e30b5e  tests/data/igm_grackle/upstream_grackle_macros.h
8ec4d3bc1faf75106d568d6ac2c3d30055f9c89839715196a7d5241b7ed93737  tests/data/igm_grackle/upstream_phys_constants.h
