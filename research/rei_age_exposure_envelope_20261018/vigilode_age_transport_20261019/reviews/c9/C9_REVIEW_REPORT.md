# C9 independent source, implementation and numerical review

Date: 2026-10-19. Reviewer: independent Astra review lane.

**Decision: PASS_SCOPED_C9_INDEPENDENT_REVIEW.** The source export, exact-input exponential enclosure, original VigilODE affine-prefix integration, grouped bounds and final passive/sensitive reporting agree with the declared fixed-gas, fixed-geometry, labelled-source model. This decision does not admit the nonlinear native trajectory or change native time-grid HOLD. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.**

The review used independent Python source/identity checks, exact Fraction arithmetic and a separate Decimal calculation. It changed no exporter, native, Rust or summary implementation. The native exporter was executed once by the implementation lane; C9 executed no native dynamics and no Rust study. The final passive split was reviewed as a summary-only calculation on the unchanged completed STUDY and coefficient CSV.

## 1. What was reviewed

The owned implementation is `vigilode_age_transport_20261019/` under the REI age-exposure research directory. `C9_FINAL_RECEIPT.json` binds the final reviewed implementation, inputs, results and documentation by SHA256. `C9_CORE_RECEIPT.json` preserves the receipt before the final passive-summary enhancement.

The native physics source is pinned to `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. The reused VigilODE files are pinned to `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406`. This review concerns the actual exported coefficients and actual completed grouped run, not only source code or proposed test cases. Publication commit identity, remote backup readback and protected-lane change checks are separate delivery checks owned by the parent research lane.

## 2. Native source and actual export identity

`validate_export.py`, `EXPORT_NODE_AUDIT.json` and `EXPORT_PACKET_AUDIT.json` establish the following:

- All **153 original native input files** match the frozen manifest, and all **156 prepared outputs** were checked before the export-specific append. The original transport source prefix is unchanged. The new read-only accessor is appended exactly once in a separate prepared runtime copy.
- The original generated `positive_native.rs` is unchanged. The derived exporter retains that source, renames its unused original main and appends a separate export entry point. It queries prepared source nodes; it does not call the transformed native evolution loop.
- Every archived age64 setup field was compared, including births, proper clocks, encoded and physical source vectors, initial states, cells and source inventory. This check is wider than the small field subset listed in the export receipt.
- The actual exporter output has **64 source packets, 896 nodes per packet, 57,344 node rows and 4,608 nonempty source cells**. The node accessor returns the original birth templates, not the accepted endpoint survivor coordinates. Each row retains packet, cell and node ownership.
- Every exported mass is finite and positive. Exact dyadic sums have maximum relative source-cell number defect `1.6141976994809757e-16` and source-cell reference-energy defect `3.000594807172295e-16`. Packet number and source-energy defects are `1.2067358325111509e-16` and `1.4722694707857669e-16`. These satisfy the existing tolerances; no tolerance or support rule was relaxed.
- All **57,344 physical energy products** agree with the native endpoint-geometry conversion. All **172,032 species hazard products** agree with `c * absorber_density * sigma` in the native export order, with `c = 29979245800 cm/s`, density in `cm^-3` and cross section in `cm^2`. The resulting hazard has units `s^-1`. An independent transcription of the original Verner cross-section formula gives a maximum observed difference of **0 ULP** on these nodes.
- Source weights have units photons/H, photon energy is eV, and the reported energy sum is eV/H. Source birth clocks and observation clock match the archived native setup and endpoint. The endpoint isotropic energy factor is `0.9980019986673332`.

The actual coefficient export, including its native compile/query, completed with exit 0 in **11.802 seconds**. This is a coefficient export, not a new nonlinear NCP campaign. The coefficient CSV SHA256 is `b83f5c07d83d9a6a04ca8120e8fcbe11dab67efb41cbcdd000e4f7eb6a25c17a`.

## 3. Exact model and proof-to-code connection

The model interprets imported binary64 masses, energies, species hazards and clocks as exact dyadic real numbers. For a node, total hazard is the exact real sum of its three imported hazards, and optical depth is that exact sum times the exact difference of imported observation and birth clocks. This is a clear coefficient-level contract. It need not equal a differently associated native floating-point total-rate calculation bit for bit, and it does not enclose atomic-data uncertainty or coefficient-generation error.

For fixed nonnegative hazard, the implemented survival is `w exp[-Lambda (T-b)]`; species events use the exact imported hazard share times `w (1-exp[-Lambda (T-b)])`. A zero-hazard node keeps all its weight and generates zero events. The photon ledger is valid for this model. Energy uses the exported endpoint physical energy directly rather than assuming separately rounded excess energy plus threshold is bit-identical.

The exponential implementation was reviewed against its proof:

1. Exact zero optical depth returns `[1,1]`.
2. For smaller positive depths, exact binary halving reduces the argument to at most 1/2. The exact rational Taylor sums of odd degree 19 and even degree 18 enclose the reduced exponential by the alternating-series theorem.
3. Conversion to binary64 compares the candidate's exact dyadic value with the rational target and moves outward if required. The implementation does not assume `to_f64` provides directed rounding.
4. Original VigilODE directed multiplication squares the interval to recover the original argument. Restricting the result to `[0,1]` is justified by nonnegative optical depth.
5. At optical depth at least 752, `[0, 2^-1074]` is valid: `exp(0.7) > 12013/6000 > 2`, so `1074 ln(2) < 751.8 < 752`. A positive upper bound remains when the central float underflows to zero.

The generic upstream arithmetic has a near-maximum-float finite-to-infinite boundary that is outside this study's domain. Here gains are in `[0,1]`, total source mass is about `7.3e-5/H`, clocks are below `1.7e13 s`, and all actual outputs were independently checked finite. C9 does not generalize this scoped success to arbitrary overflowing affine inputs.

## 4. Actual VigilODE reuse and paired-bound scope

`affine_transport.rs` and `directed.rs` are unchanged upstream source bytes. A documented thin local `CoreError` compatibility layer supplies only the variants used by these files. The upstream MIT license is preserved. The implementation calls the actual `AffineErrorMap`, `parallel_error_prefix` and reusable `AffinePrefixWorkspace` APIs.

For a paired source label, later birth `t* = max(b_A,b_B)` and initial defect `d = w (1-exp[-Lambda |b_A-b_B|])` give the exact later difference `d exp[-Lambda (t-t*)]`. The prefix contains labels only after both paired births have occurred. Its intermediate value is not a bound on a population with unmatched births. At the observation time all pairs are included, so the sum bounds the absolute total surviving-number difference.

A global minimum sensitive hazard gives a valid loose bound. Grouping by each exact imported species-rate tuple gives a common exact total hazard inside each group. Its affine recurrence is then an exact real identity for that group's labelwise absolute difference. Summing group endpoints bounds the same final defect as the direct nodewise expression. Independently outward-rounded direct and grouped upper endpoints need not be ordered. Their minimum is valid after establishing each as an upper bound.

This reasoning preserves source labels and age-opacity correlation. Equal unlabelled age marginals alone do not imply equal photon response. The preserved counterexample with hazards `(0,1)` and swapped births is valid. The monotone transport/W1 statement in THEORY_KO is restricted to the actual order-preserving source-clock coarsening. Separate moment inequalities in THEORY_KO are mathematically consistent and explicitly not counted as executed outward moment-difference certificates.

Source identities:

| File | SHA256 |
|---|---|
| Original affine transport | `4d8687c8c536850d7f5616192a864c839c63ab8e0ddc778678ffd6eba1a9e178` |
| Original directed arithmetic | `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814` |
| Original MIT license | `bfb425597830af905d9b52262dc5fc56e436de05796f6638a78258adaa0b8760` |

## 5. Independent actual-data numerical checks

`compute_decimal_reference.py` separately evaluates the declared model at Decimal precision 100 using exact binary64 conversion and exact Fraction species-hazard sums. It reads all **57,344 nodes**, has **1,113 unique rate tuples**, and cached 14,776 exponential evaluations. It completed in **4.306 seconds**. This is an independent high-precision numerical cross-check, not a substitute for the enclosure proof.

`validate_final.py` then verifies:

- **28/28** reported observable intervals, covering N, energy, two age moments and three species event sums for four settings, contain the independent reference.
- **4,448/4,448** active-rate group endpoint bounds contain an independently reconstructed group defect: 1,112 groups for each of four settings, including the exact 64-versus-itself case.
- All **220 reported global prefixes** enclose the exact dyadic recurrence defined by their reported leaves.
- The checked source and successful completed run exercise Rayon thread counts 1, 2 and 4 with exact output equality, plus allocating/workspace API equality. C9 inspected these assertions and their successful execution evidence without rerunning the Rust study.
- All reported floating-point outputs are finite. All four photon-ledger intervals contain zero. Between **10,880 and 11,040** central underflowed node values retain positive upper bounds.

The final grouped kernel took **51.048 seconds**. These timings are from this model and are not a solver performance comparison. The completed initial global-minimum result is preserved. Its four physical settings are byte-identical to the final grouped replay's four observable cases. This is one coefficient export and one fixed-data scientific study with four settings; the grouped implementation replay is not counted as another four scientific cases or a native history campaign.

| Coarse clocks versus 64 | Independent signed N difference, photons/H | Grouped affine upper on absolute difference, photons/H |
|---|---:|---:|
| 8 | -1.2914031613385614e-9 | 1.292312768972707e-9 |
| 16 | -1.2703608634432689e-9 | 1.2882258655815744e-9 |
| 32 | -1.0672778445952270e-9 | 1.250251573671560e-9 |
| 64 | 0 | 0 |

The grouped upper exceeds the independent labelwise defect by about `6.0e-15` to `6.9e-15` in relative terms. The much looser global-minimum upper is retained as evidence of why grouping was needed. Raw 100-digit values and all group checks are in `DECIMAL_ACTUAL_DATA_REFERENCE.json`, `ACTUAL_OBSERVABLE_CHECKS.json` and `ACTUAL_GROUP_CHECKS.json`.

## 6. Material reporting finding: invariant passive mass

C9 identified that total surviving N is dominated by an invariant passive population, which could conceal substantial birth-clock sensitivity. The exact passive mass, independently summed from the **4,096 zero-hazard rows**, is

`P = 2567757288181244159093 / 19807040628566084398385987584 photons/H`.

Its decimal value is `1.296386136795204317112402510188244872091944720655931622133039127220399677753448486328125e-7/H`.

The final summary now subtracts this exact dyadic P from the existing certified N endpoints and rounds outward. It proves the sensitive reference denominator is strictly positive, forms signed differences with exact passive cancellation, evaluates all ratio-interval corners exactly and rounds outward. The 64-versus-identical-64 ratio is exactly zero. `validate_passive_summary.py` independently checked all four new sensitive and relative intervals against exact Fraction endpoint expressions and the previously computed Decimal100 model values. It ran no exponential evaluation, native code or Rust study.

| Clocks | Sensitive N interval, photons/H | Sensitive signed relative difference versus 64 |
|---|---:|---:|
| 8 | [1.0983293258238907e-12, 1.0983301709774838e-12] | [-0.9991502303953932, -0.9991502284342793] |
| 16 | [2.2140627217826137e-11, 2.2140628063006203e-11] | [-0.9828699413248649, -0.9828699393743761] |
| 32 | [2.2522364606161115e-10, 2.2522364690676477e-10] | [-0.8257459300091148, -0.8257459281613881] |
| 64 | [1.2925014906580857e-9, 1.2925014915032395e-9] | [0,0] |

For 32 versus 64, the independent total relative difference is about **-0.8151445462%**, while the sensitive relative difference is about **-82.5745929276%**. Passive mass supplies **99.0128385532%** of the frozen-model age64 total N. Both normalizations are needed to describe this result accurately.

The frozen-model age64 total N is about **101.4254 times** the separately archived evolving native endpoint N. Its sensitive subset happens numerically to be about **1.0012325 times** that archived scalar. Neither numerical comparison certifies trajectory closeness: the frozen and evolving histories have different coefficient paths and no bound connecting them was established. This scope restriction is explicit in README, THEORY_KO and ANALYSIS.

The original STUDY SHA256 remains `ec0a81875d0300dfebb5f7404563e1381dc95ac65c2b28b34e1bab5ae0740307`; all original summary case fields, paired bounds and BOUNDS.csv are unchanged. Prior summary files are preserved under `results/summary_before_passive_split/`. `PASSIVE_SUMMARY_AUDIT.json` binds the final fields and independent check values.

## 7. Dependencies and reproducible offline evidence

Actual Cargo.toml/Cargo.lock selection matches these direct pins: num-rational **0.4.2**, num-bigint **0.4.6**, num-traits **0.2.19**, Rayon **1.12.0**, serde **1.0.228**, serde_json **1.0.145** with `float_roundtrip`. Exact-rational arithmetic and original parallel prefix code use them directly. No full nonlinear solver, faer or Krylov stack was added.

C9 verified **22 vendored registry packages** against Cargo.lock and rehashed **865 source files** against their Cargo checksum manifests. The portable Cargo configuration selects bundled vendor sources. Existing successful evidence records `cargo test --release --offline --locked -j 2`, exit **0**, with an empty registry cache and wall time **0.064026 seconds** for the final verification invocation. The earlier source-switch failure is preserved separately.

Four Rust tests passed in the completed run, including the unchanged upstream arithmetic test. The reviewed fixtures cover exact rational conversion boundaries, zero and positive subnormal upper bounds, original prefix versus rational recurrence, workspace agreement and thread equality. The verifier also includes 17 independent exponential fixtures. These are specific implementation checks; old unrelated REI test totals are not recomputed or relabelled by this review.

## 8. Findings closed and remaining limits

1. **Stale offline receipt: CLOSED.** C9 found a canonical exit-101 receipt conflicting with already-existing successful evidence. The implementation lane corrected the canonical receipt using that existing exit-0 evidence and retained the failed attempt. No test or campaign replay was required.
2. **Passive-mass dominance disclosure: CLOSED.** Exact passive and sensitive populations and signed sensitive-relative intervals are now reported and independently verified. The small total relative difference is not presented as uniform age accuracy.
3. **Energy table unit: CLOSED.** The README table now labels U as eV/H, consistent with the declared per-hydrogen source weights and THEORY_KO.

No unresolved defect was found within the reviewed fixed-input contract. The result remains conditional on the imported coefficients. It establishes neither nonlinear Grackle response bounds nor a repair of the native subnormal mass/energy representation obstruction. It does not replace the native ODE solver, prove requested native time-grid accuracy or issue production admission.

## Review artifacts

- `C9_FINAL_RECEIPT.json`: final file hashes, review counts and scoped decision.
- `C9_CORE_RECEIPT.json`: preserved pre-summary receipt.
- `EXPORT_NODE_AUDIT.json`, `EXPORT_PACKET_AUDIT.json`, `validate_export.py`: original-source and actual export identity.
- `DECIMAL_ACTUAL_DATA_REFERENCE.json`, `compute_decimal_reference.py`: independent actual-model numerical reference.
- `ACTUAL_OBSERVABLE_CHECKS.json`, `ACTUAL_GROUP_CHECKS.json`, `validate_final.py`: independent observable, group and prefix validation.
- `PASSIVE_EXACT_IDENTITY.json`, `PASSIVE_SUMMARY_AUDIT.json`, `validate_passive_summary.py`: exact passive identity and final reporting validation.

These artifacts document computations actually performed in this review. They must be shipped with their source/result hashes and scoped status intact.
