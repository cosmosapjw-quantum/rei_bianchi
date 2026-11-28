# Independent C9 — HE-ANG-FINITEMASS-SHELL

Date: 2026-10-24. Separate `independent_review` Astra role requested by the user; runtime model identity is not independently observable.

**Final verdict: PASS_SCOPED_KINEMATICS.** The actual implementation, independent controls, three completed execution records, and saved-output figure satisfy this frozen finite-fixture contract. No blocking finding, repair, additional execution, or optional audit is requested. Physical-provider admission remains `SOURCE_INPUT_PENDING`.

## Evidence and identities

R6 is reused unchanged. I read all five code files, MAPPING_DESIGN, PREPARATION_MANIFEST, the actual three START/FINISH pairs, raw unittest and analysis/plot logs, TEST_REPORT, ANALYSIS, RESOURCE_LEDGER, and the actual PNG. Reviewer activity was static reading, hashing, and image inspection only: no scientific imports, calculations, tests, quadrature, renderer, or old suite execution.

| Object | SHA256 |
|---|---|
| THEORY_KO.md | `9a2d927f5a04bbac6e0e6db759dad39fe950c08aae31fa948d2ca9ea47343a7b` |
| FROZEN_CONTRACT.json | `1e19f1f91f7003f60427f616c0be4473f8d0e97867bc92f81cc6667fcfc6a2b1` |
| shell.py | `53ad5f77d3cc5322719e4f6ef2748839662a3cc0ed532b85efb06be1811231c3` |
| test_shell.py | `374905f9b53cfe95bffba90016609968666e7994267bea4875323dcd547ee01e` |
| run_analysis.py | `27f36c03182c1d7fb4befc2f0ab81f89733f1ab81aff51e6eb075552472bf6ac` |
| plot_results.py | `736a3c2405a9a4264f87020065861680c8ff4e45bdeaca43485bd5aac5e0b3bd` |
| run_bounded.py | `7e5f4fe6221a12972eb72eed57b5fb300322f44ac6701639fc2e410672850676` |
| results/ANALYSIS.json | `711d8dd054e3d74e0d0c0da15ee352114b7a94b2d44e84504cc0e79f649e4243` |
| FINITEMASS_SHELL.png | `acb6c8f1bce35380272826296b6db6c62ba41afee363975095e0a7a9210b98bc` |
| FINITEMASS_SHELL.svg | `b5a94af45153ed6eb6fa77ee412d388eefb7faf82b941e4b13c78115d3bd11ae` |

The prepared code identities agree with the reviewed files. The runner checks frozen-input identities and the existing pinned mpmath wheel before child launch, records actual identities and costs, enforces sequential planned children, and has no automatic repair route. Dependency reuse is the same pure-Python mpmath 1.3.0 wheel on PYTHONPATH, not a fallback in precision or a new scientific method.

## Algorithm and input assessment

The lab/Jacobi inverse, COM subtraction, conditional sphere, phase volume, and constant-weight moments implement the reviewed formulas with the stated A-spectator convention. The positive-node code stores the first three coordinates as q and the last three as k, explicitly documented and consistently used; this naming choice does not change the isotropic S5 rule.

The radial solver forms the stated quadratic and preserves its raw discriminant, coefficient scale, and unresolved-band threshold. Within the guard it returns `NEAR_CAUSTIC_UNRESOLVED` and no finite radial/coarea weight. It does not clip a negative discriminant, merge nearby roots, or silently choose one branch. Away from the guard, the stable large root and product-derived companion are classified individually; positive roots, algebraic roots, and zero endpoints remain separate. The density includes the required pA factor, and branch-specific pB vectors and weights are available.

Direction normalization is explicit and reports the input norm. Invalid M/B/E0, nonfinite inputs, zero direction, and wrong vector dimensions are rejected by the relevant APIs. These finite controls do not establish total arithmetic robustness for every extreme binary64 magnitude. The discriminant guard is not an enclosure of all upstream coefficient error, and neither the documentation nor this receipt certifies it as such. The declared finite-fixture scope is the admission boundary.

The source-derived internal Hamiltonian is kept distinct from the newly derived lab maps and measures. All outputs continue to describe labelled kinematic measure with W=1 for volume/moment fixtures. No amplitude, incident flux, Fourier normalization, physical spin average, extra event-count factor, or absolute cross section has been introduced. Fixed B and reduced-mass binding remain distinct inputs. Existing fixed-center dynamics are not imported into a purported finite-mass physical amplitude.

## Independence and coverage of the controls

The actual **14/14 methods PASS** log covers inverse mapping, determinant through independent basis perturbations, direct lab momentum/energy, empty/collapsed support, completed-square identity, ordinary positive/negative/zero/complex root classes, exact two-root hand fixtures, raw-D nextafter guards, normalization errors, hand coarea factors, swap, every monomial through degree four, direct-node lab moments, volume scaling/binding modes/mass limit, and invalid inputs.

The analysis contains **six** proton-mass fixtures: nominal 20, 54.4, and 413.6 eV, each with fixed B=0.5 and B=mu/2. Independent 80-digit volume quadrature integrates the one-dimensional q representation with a sine substitution, rather than calling the production volume helper. Its comparison with the high-precision closed expression and the binary64 volume addresses normalization as well as arithmetic.

The **sixteen** ordinary radial cases reconstruct the lab quadratic from vector momenta in mpmath80 without production coefficient helpers. The high-precision route uses the direct quadratic formula; the primary route uses the cancellation-avoiding form. Their independent branch counts and Jacobians agree in all reported cases, including the synthetic two-positive-root and no-real-root cases. Input floats are converted through their decimal string representations for this reference, so the comparisons are tolerance-level controls, not a bit-exact audit of the same rational binary64 inputs.

The fold control independently sums both raw branches in the regular h coordinate and integrates them, comparing with the regular conditional-sphere volume. This tests an integral different from pointwise quadratic residuals. The 76-node tests check all monomials through degree four against the known isotropic moments; the analysis then forms lab energies directly from inverse-mapped momenta. It compares those node averages and recoil variance with the analytic moment API. The inverse map is shared by that latter construction, so independent mapping tests, direct energy/momentum residuals, and R6 provide the complementary checks. No general-amplitude cubature accuracy is inferred.

## Actual numerical outcomes

All three actual FINISH records are PASS with exit 0, no timeout, and no measured cap overshoot. ANALYSIS records `status: PASS` and an empty error list. Saved metrics are below the frozen ceilings:

| Observed metric | Maximum or recorded value |
|---|---:|
| Binary64 volume relative error against 80-digit quadrature | 4.3022484084710367e-16 |
| 80-digit volume quadrature versus closed expression | 2.582957358791492e-81 |
| Ordinary radial-root scaled error | 4.662849293818372e-16 |
| Ordinary radial Jacobian relative error | 2.5621855173149446e-15 |
| Node energy scaled residual | 3.0751266063160474e-16 |
| Node momentum scaled residual | 2.220446049250313e-16 |
| Energy/momentum/variance moment scaled error | 2.418474499767532e-16 |
| Fold angular integral and conditional sphere volume | 2.48364706644902530860838766758008778… |
| Fold relative difference at the working precision | 0.0 |

Zero displayed residuals mean agreement at the working arithmetic, not a new proof of exact equality or a directed-rounding certificate. The quadrature error is the observed disagreement with the independently derived closed expression; it is not a rigorous adaptive-integration error enclosure. Recoil moment checks use the frozen absolute-or-scaled convention, not a uniform relative-error assertion for arbitrarily small moments.

## Actual visual review

The PNG passes direct visual inspection. Both positive branches are labelled; the analytic fold boundary is visible. The finite display grid ends just before that boundary, so the drawn branches do not join exactly at the tangent. This is a visible sampling limitation consistent with the saved quarter-degree grid and unresolved/absent-support policy, not evidence of two distinct roots exactly at the fold. It does not require another render.

The right panel clearly labels the common infinite-mass B=0.5 denominator and distinguishes fixed-binding solid lines from reduced-mass-binding dashed lines at each nominal energy. All axes, legends, titles, and three qualification lines are readable. The caption explicitly identifies the synthetic M=1 fixture and the W=1 kinematic scope. Plotting reads the saved passing analysis only; it performs no shell or reference calculation. There is no clipping or misleading physical-amplitude claim to repair.

## Resources and disposition

| Child | Measured CPU s | Measured wall s |
|---|---:|---:|
| Tests | 0.064747 | 0.06918608200066956 |
| Analysis | 0.5463089999999999 | 0.5751221360005729 |
| Plot | 1.873395 | 1.8748732269996253 |
| Total | **2.484451** | **2.519181445000868** |

These measured child costs fit the unchanged 8 CPU / 30 wall allocation. The one diagnosed reserve remains unused and is not automatically authorized. Prior-unit costs and reserves are not reset or transferred. Host preparation, model/provider/IO, and total remote CPU unknowns remain distinct; no end-to-end CPU-cap certification follows from the child totals.

**Findings:** no current blocker and no required repair. The display-grid limitation above and finite numerical-domain qualifications are recorded evidence limits, not additional execution obligations. Admit the implemented kinematic support, branches, coarea map, and constant-weight fixture formulas within this frozen tested scope. Preserve SOURCE_INPUT_PENDING, false physical-provider/event-sigma/activation/merge gates, and all prior unresolved source and owner obligations. Stop optional checks for this completed review.
