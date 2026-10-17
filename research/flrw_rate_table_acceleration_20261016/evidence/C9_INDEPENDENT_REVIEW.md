# Independent C9 review — PASS_SCOPED

Fresh review of the actual H/He/D rate-table/prepared-point implementation and Li6/Li7 conditional number component found no blocking defect. No production code was changed and no scientific build, test or benchmark was rerun. The reviewer did not implement the reviewed code. Astra high was requested; runtime model identity was not exposed.

This decision does not inherit PR178 actor independence: that record explicitly says independent actor review was not run. It admits only the objects and claims described below, without upgrading the whole PR178 or later FLRW branches.

## Source and physical review

The eight owned source/test paths match the current integration receipt at `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`. All 67 focused-manifest entries were checked against current source and the frozen bundle with no mismatch. Current `igm_rates`, `rate_table` and `igm_thermal` Git blob identities also match the PR177/178 frozen H/He core.

The thermal diff against the retained baseline only adds prepared-bundle dispatch and exact recovered-EOS-temperature binding. Reaction number, binding, kinetic, escape, CMB and expansion owners are unchanged. Default Axbi point evaluation prepares Direct once; the table backend is explicit. Prepared fields are private, invalid preparation fails, and a different EOS temperature returns `IGM_PREPARED_TEMPERATURE_MISMATCH`. D reuses the selected H bundle with the correct cm³→m³ and erg cm³→J m³ factors under its existing H-equality approximation.

The table preserves the actual low-temperature predicate, CI floor masks, CE caps, raw/excluded DR and structural zeros. Known branch crossings, changed endpoint floor masks, uncertified zero, signed and subnormal cells fall back directly. Input/provider domains remain strict. The current grid already rejects a nonnormal or nonpositive logarithmic step; the withdrawn NaN-step concern is not a finding.

Li row parsing preserves q=3−N, the RR temperature-dependent exponent, historical Voronov kB, and the signed DR amplitude. The negative Li+ DR term is dominated by a larger positive term with lower exponential energy. CI support remains per-row [1,4,5] eV through 20 keV, and RR/DR uses the declared [10q²,10⁷q²] K tabulation support. The complete chain intersection is [5/8.617385e−5,10⁷] K. Individual cold RR does not authorize cold CI or the complete cold chain.

Li6/Li7 identities are distinct and require `ElementalElectronicEquality`; `IsotopeResolved` returns `MissingSource`. The equality is an explicit modelling approximation, not isotope-resolved source data. Li8/Li9 decay remains pending. Adjacent fluxes conserve each isotope's nuclei and A-weighted baryon number; charge changes equal the returned electron source. The external electron density and number-only scope are explicit. No abundance, photo, thermal or nuclear closure is introduced.

## Evidence admitted

The original local raw records contain 5 H/He and 4 Li PASS tests. The H/He 65,537-node sampled maximum is 3.8387697880837957e−7; the Li 8,193-node, 1,015-temperature maximum is 1.1733732758756332e−6. Both satisfy the unchanged 1e−5 value target in its declared scope. The initial 8,193-node H/He failure is retained. The 21 H/He fixtures are not a 21-species network.

PR177 source-pinned summary evidence at `2f4103968cc26061a62dc7931c27c2fe86d75cd8` records 20,510 H/He queries and 3.8172670147488274e−7 maximum error. Its raw inner timing samples were not part of this bounded intake; their spread is not inferred. PR178 at `1579a5e4b0c3093bfd6942cc4914e29a00a71978` supplies three preserved raw runs, each with the RHS, derivative diagnostic and matched-worker benchmark tests. The 36-state RHS ledger norm is 1.2272269344036022e−16 and reported state/energy/temperature deviations are below the retained value-scale gates. The imported summary's separate four-test count is not asserted from these three-test raw logs; local C6 already supports exact-temperature binding.

C8 correctly separates the local Rust 1.85.1 and upstream Rust 1.94.1 cohorts. Local table-point timing is slightly slower than prepared Direct, and random scalar table lookup can be slower than direct. For PR178's equal four-worker comparison at N=262,144, median run-level speedups are 1.607568396 ordered and 1.370923361 random; median amortization thresholds are approximately 1.84 million and 3.16 million queries. These are conditional coefficient microbenchmarks, without a full-solver or universal speedup claim.

The 0.0065711347474461945 derivative diagnostic is an **absolute finite-difference log-slope difference**. The contract's conditional 1e−3 derivative criterion is **scaled** and applies if a derivative API is implemented. They cannot be directly compared to declare failure. There is no derivative API, and value accuracy does not certify slopes or a Newton/Jacobian. Derivative and trajectory admission remain HOLD.

## Claim boundaries and next action

The dossier registry has 17 original entries plus four Li6 entries, with distinct native13 bookkeeping and separate8-state Li component. It is not an activated coupled21 solver. Its Oct17 overlay correctly recognizes later mixture EOS/CX reference work instead of demanding repetition of the historical pure-H/D stage. Those later branches are intake references, not scientifically reviewed by this C9 decision.

PR178's standalone Rust policy is externally reported tested and advisory. This reviewer read its policy JSON but did not inspect its Rust implementation or tests; no independent policy-code admission is issued. The local focused build limitation, inherited Clippy reports, historical compiler-label caveat, resource ledger and absence of new execution are disclosed in C8. Cloud backup/readback and publication remain separate completion records.

**PASS → root scoped admission and mechanical C9/C10 checkpoint/handoff completion.** No targeted repair or additional scientific test is required for this admitted scope. Preserve Direct default and HOLD on derivative/Jacobian use, full trajectories/global convergence, NCP64 or end-to-end speedup, isotope-native Li accuracy, cold/full Li photothermal-nuclear closure, coupled21 activation and automatic production selection.

Exact reviewed artifact identities and findings are recorded in `C9_INDEPENDENT_REVIEW.json`.
