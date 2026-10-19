# BR04 independent numerical review

## Decision

The frozen/source-fixed age certificate and its stated composition formulas are verified at the bounded scope of this unit. Actual Rust nodes were read back and compared with a Decimal90 reference using analytic quantile integration. The original-source study also separates label-weight error from conditional age shape error. These results do not certify the full evolving H/He/D time integration, its universal order, or longspan convergence.

The mathematical assumptions and proofs are in AGE_CERTIFICATE_THEORY.md. Machine-readable results, exact reference values, input hashes, and the actual execution log are in evidence/theory.

## Independent checks actually executed

The recorded initial local command used the first four arguments and both inclusion flags. The reproducible command additionally allows an explicit original-source path:

    python3 scripts/verify_age_certificate.py <generated_age_study> <output_directory> --include-source --include-edges --source-inputs <unit_root>/inputs/AP_FROZEN_SOURCE_INPUTS.csv

The generated study and verifier output directories are caller selected. The verifier reads the original evidence and checks that its SHA-256 values remain unchanged. It does not overwrite those inputs. The recorded initial complete local execution took 11.94 seconds. The optional source path defaults to the verifier's unit input directory, independently of either output directory.

| Check | Actual scope | Result |
| --- | --- | --- |
| Scalar and timestep-composed actual nodes | 84 cases, 168 emitted/survivor measures, 16,370 input node rows, 2,016 scalar comparisons | PASS_SCOPED |
| Reference self-checks | Six named analytic checks, including uniform one-atom and GL2 radical results, exponential youngest-atom limits, and composite midpoint transport costs | PASS |
| Original-source actual-node subset | Twelve of 288 unique rules; 5,888 of 137,152 actual node rows; 24 measures and 264 scalar comparisons | PASS_SCOPED |
| Source identity and mixture arithmetic | All 4,608 exported label rows retain the original energy, birth weight and summed species opacity; all twelve mixture rows, 168 scalar comparisons | PASS_SCOPED |
| Edge contracts | Ten cases: empty and zero source, zero opacity, positive survival underflow, extreme-opacity atoms, and invalid inputs | PASS_SCOPED |
| Existing rule representation limit | Five exported AP-rule failures at optical depth 10^300, one per tested refinement | Correctly classified |

The source subset was declared before reading its comparison results: choose the smallest and largest total optical depth in each of AP refinements 1, 2, 4, 8 and GL2/GL4. Its rule IDs are 0, 47, 48, 95, 96, 143, 144, 191, 192, 239, 240, 287. Direct independent age-distribution integration therefore covers twelve source rules. The remaining per-label certificate values enter the independent mixture-arithmetic check as input; they are not represented as independently reintegrated from every source node.

The largest absolute W1 discrepancy was 4.477×10^-17 in the main matrix and 6.588×10^-18 in the source subset. Corresponding CDFsup discrepancies were 2.151×10^-16 and 2.733×10^-16. All declared comparison tolerances passed.

At optical depth 10^12, the old GL log-survival can have magnitude about 10^11. Its largest absolute log-mass discrepancy, 7.395×10^-6, is within the declared relative tolerance on that large logarithm. It is not a claim of a 10^-6 absolute log tolerance.

The reference uses 90-digit Decimal arithmetic on the exact real values represented by the exported binary64 nodes. It integrates the absolute quantile difference using a logarithmic primitive; Rust instead sums nonnegative CDF plateau integrals. Terms with exponent below -1800 are omitted by the reference, with a separately documented tail bound in its main optical-depth domain. Decimal arithmetic still rounds, and extremely small negative primitive differences below 10^-75 are treated as cancellation. These numerical checks are not directed-rounding interval enclosures.

## Original-source quantitative results

The frozen inventory contains 384 source labels, duration 8×10^12 seconds and 32 emission intervals. The exact survivor number density is 1.0011168643620165×10^-8 reference-comoving m^-3; the exact mean age is 1.510948967737823×10^10 seconds.

All distances in the following table use age divided by the total duration. W1 in seconds is obtained by multiplying by 8×10^12 seconds. The distances shown are conservative scalar-mixture upper bounds, derived from the per-label distances and label-weight total variation.

| Birth rule | Relative survivor-mass defect | Scalar-mixture W1 upper bound | Scalar-mixture CDF upper bound | Relative mean-age error |
| --- | ---: | ---: | ---: | ---: |
| AP r1 | 0 at exported binary64 aggregate precision | 3.51967494×10^-4 | 0.21523544 | +5.99455774×10^-3 |
| AP r2 | 0 at exported binary64 aggregate precision | 1.99474719×10^-4 | 0.12477298 | +7.62223983×10^-4 |
| AP r4 | 0 at exported binary64 aggregate precision | 1.08402215×10^-4 | 0.06712097 | +7.21641093×10^-5 |
| AP r8 | 0 at exported binary64 aggregate precision | 5.69834501×10^-5 | 0.03480249 | +5.66708356×10^-6 |
| GL2 | -0.7450568024 | 0.37048236 | 1 after the trivial probability-distance cap | +2.53638683 |
| GL4 | -0.1628240889 | 0.08773831 | 0.79595870 | +0.36785903 |

The raw GL2 CDF upper bound in the CSV is 1.322968788. A CDF distance itself cannot exceed one. The uncapped bound is valid but uninformative at that size; the table applies the separate trivial cap without changing the exported evidence.

For GL2 and GL4 the normalized label-weight total variations are 0.36552959 and 0.08632309. Their weight errors contribute strongly to these conservative mixture bounds. The bounds are not the exact unlabelled-mixture W1 values and should not be used as numerical estimates of those distances.

AP r8 has a mean-age error of 85,626.74 seconds but a W1 upper bound of 455,867,600.82 seconds. This difference is consistent: a single moment can cancel much more effectively than the full age distribution. Exact survivor mass and a small mean-age error do not identify that distribution.

## What fixed time refinement does and does not show

For total frozen optical depth 93 and fixed AP r2, the exact continuous reference is independent of the number of emission intervals. From one to 64 intervals the measured W1 falls from 1.137444219×10^-3 to 7.861858265×10^-4. The CDFsup remains about 0.124772979 across those grids. The signed second-moment error becomes negative between 16 and 32 intervals. These are direct birth-approximation effects in a reference problem with no gas time-integration error.

The persistence of CDF error at these fixed-refinement grids explains why timestep refinement alone cannot be assumed to certify age accuracy. It does not assert that CDF error remains nonzero for arbitrarily many intervals at fixed refinement; once the local optical depth and physical panel widths shrink sufficiently, a separate asymptotic analysis applies.

At single-step optical depth 10^12, AP r1 has fractional-age W1 of 1.869170193×10^-13. Multiplication by optical depth gives an optical-age W1 of 0.1869170193, while CDFsup is 0.2152354382. AP r8 improves these quantities to 0.03020051248 and 0.03480249216. A tiny error measured in total-step age units is therefore not by itself uniform accuracy in the survival-layer scale.

The full native crossed time–birth study must be interpreted separately. The certificate in this unit supplies a computable error for the frozen/source-fixed measure. To convert it into a birth-error bound for a coupled evolving history, the change in the gas/opacity response must also be controlled. The crossed-comparison identity and its conditional bound in the theory report state precisely where that missing term enters.

## Failure and scope classification

The first fresh run passed the scalar comparison but then exposed an input-location bug: the verifier inferred the source input path from the generated age-study directory. It raised FileNotFoundError before source verification could run. The actual traceback is preserved in DECIMAL_FRESH_PATH_FAILURE.log. The implementation was corrected to accept the explicit source path shown above, with a default relative to the verifier's own unit root. This is classified as REPRODUCTION_INPUT_PATH_BUG, separate from a numerical or physical failure. The second fresh attempt passed all three independent verification groups, reproduced the three Decimal reference CSVs byte for byte, and verified the final script hash. The failure ledger therefore records CORRECTED_VERIFIED; detailed fresh execution remains in evidence/FRESH_RESTORE_VERIFICATION.json.

The existing BR03 AP rule returns NoForwardProgress at optical depth 10^300 for all five tested refinements. The certificate itself handles independently supplied positive atoms at that depth. This is a finite-representation limitation of the existing rule construction. It is neither a Cx(WorkLimit) result nor evidence that a physical solution does not exist.

For a positive source with absolutely underflowed survivor mass, a normalized shape can remain computable by log-scaled weights. For exactly zero source or an empty positive-node list, the corresponding conditional shape is undefined. These states are kept separate in the exports and independent audit.

The new module is a read-only certificate for retained cohorts. It changes no photon event, source owner, thermal/chemical energy ledger, geometry work, competing-species absorption, CX half-flow, or timestep controller. Native conservation residuals, source threshold crossings, and the remaining physical assumptions belong to their source-native evidence and are not replaced by this distribution certificate.
