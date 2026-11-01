# REI IGM F05 [160,161] owner V2 shadow: original source physical acceptance candidate
2026-11-01 | one science unit | parent PR352 HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c | research/rei-f05-owner-v2-shadow-admission-20261101

## Result and scientific object
Constructed an *explicit versioned* alternative source-owner F05 candidate, replaying the original 26-event 46,080 spatial-cell H/He/OTS/thermal full, half1 and half2 maps in the original native kernel, original source time, and all three frozen shape lanes. No new physical provider, rate atlas, tolerance, or fourth estimator. Reused PR350 M-matrix direct residual increment bounds. The frozen original independent-output historical FAIL is retained as a simultaneous diagnostic. The candidate step is **SCOPED_V2_NATIVE_HHE_TICK161_PASS**, and the original source-owner worker remains unchanged and OFFICIAL_TICK161_NOT_ACCEPTED.

Original source tar SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b
Original accepted state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01
Original kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644
Original source INPUT_LOCK SHA256 90137341a1a37344be762e82e6603cd5c6bf4db00164ab0ba98809f0e9d9f381
Upstream original M-matrix parent PR350 38e32c7b23683930e788696bb65e923819678aac.

## Mathematical and scientific justification
For original MPRK H(2) and He(3), A p_out=p_in, A=I+B, hence A Δp=−B p_in. A is inverse-positive conservative M-matrix under exact physical nonnegative transition rates. Therefore ||A^−1||_1=1 and, for any trial z and b=−B p_in, ||Δp−z||_1 ≤ ||b−Az||_1. Verified symbolically with Wolfram for a representative positive-rate conservative 3×3 A: nonnegative inverse, unit column sums, and strictly positive determinant. This corroborates the structural identity, not full implementation-wide formal rounding.

For thermal U=(3/2) k_B T (N_H+N_He+n_e), native original gamma/final SDIRK2 thermal root gives ΔU=h[(1−γ)Rγ+γRfinal], γ=1−1/√2, and ΔlnT=log1p(ΔU/U0)−log1p(Δne/(N_H+N_He+ne0)). Reusing PR350's actual source and native software, the full-vs-twohalf discrete defect is enclosed by shared-parent increments (not by separate endpoint boxes). This is the same mathematical discrete defect, not a proved continuous flow truncation error.

## Actual new source-owner physical acceptance evidence, local experiment
Three genuine original 46,080-cell native lanes ran to OS exit 0 and use the SAME physical source. The original native owner post-map validator code was called on each lane with all 14 *actual freshly computed raw intervals* (not labels from a preexisting pass). Every interval contained zero. Original native full/half1/half2 map, 3 final population solvers, 3 thermal roots per map, table windows, original 4-group photon/OTS/energy and width checks all passed.
- Original legacy output-box logT upper 2.1245050576368385e-4 > frozen 2e-4, remains FAIL.
- New direct M-matrix increment logT 5.387144148931529e-6 < frozen 2e-4.
- New x_HII 5.998277644160958e-6, x_HeII 4.55075870552145e-6, x_HeIII 4.550636330824591e-6, all below 2e-4.
- Original output max logT public width 2.257243260856967e-4 < frozen 2e-3.
- Raw nuclear ledger H_nuclei = [−4.425725319743481e56, 4.425725319743481e56] source-count units; He_nuclei = [−2.9711268467606964e56,2.9711268467606964e56].
- Raw final photon identity residual [−1.9002742808337572,2.1364458106978503] source-photon count units; raw final total-energy residual [−1.4785553253554954e36,+1.4785553253554954e36] erg. The photon-group residuals and every stage/final energy ledger are preserved in V2_RECEIPT.json and fully audited. These are interval inclusions of zero, not proof that full photon or energy model error is comparably small.

The isolated V2 candidate stores actual native five-population and T intervals for 46,080 nodes, plus original parent arrays, in SHADOW_V2_NONAUTHORITATIVE_TICK161.npz (local SHA256 eb13b86f86dfdd37ba17a7007640263b7210397be31ead24a05c5d2dbf62f90b). Standalone independent audit verified 3/3 lanes, local candidate SHA byte equality, zero relative discrepancy over all parent/endpoint population and T numerical arrays compared to earlier source-exact PR352 physical-state preview, immutable SHA, 14 native raw ledger, and no original REIADP1 accepted-state serialization. Normal 9/9 and Python -O 9/9 unit/negative tests PASS.

## Same-author hostile scientific judgment
- What passed: the native source owner post-map PHYSICAL gate under an explicitly versioned V2 alternative interval representation of the same discrete step-doubling defect. Original 14 raw physical ledger, clock, source, thermal domain and width are unchanged.
- What did NOT pass: official original 1.0 acceptance worker classification, original runtime contract SHA and environment fingerprint, and the entire first 131072-tick history. Original stage scientific contract locks predecessor parity; changing the estimator representation requires an explicitly adopted V2 source-owner contract, not a silent mutation.
- Local source experiment used NumPy 2.4.2 and pandas 3.0.0, unlike original pinned NumPy 2.3.5 and pandas 2.2.3. Optional numexpr/bottleneck NumPy ABI warnings occurred but native computations returned exit0; source-native numerical facts are locally checked, strict ORIGINAL runtime equivalence is NOT_CLAIMED. The GitHub CI pinned source runtime, if successful, is an independent clean-workflow source-scoped V2 validation, still not original runtime SHA due new Git HEAD/contract.
- M-matrix exact nonnegative structural rate proof relies on the physical production-destruction construction, not rounded interval lower entries which can be −minsubnormal for structural zeros. Formal fully rounded original source-native Krawczyk/BLAS and validated exact ODE truncation error are NOT_PROVEN. Two methods under the same native kernel are not independent astrophysical datasets.
- The raw ledger intervals include zero but may be wide; they certify original gate compliance under that native contract, not exact cosmic energy conservation over arbitrary physical histories.
- Same-author hostile review only, native subagent NOT_RUN because user explicitly requested without subagent.

## Release status, drift and next physical decision
Central 28/88_REPORTED; Working 33/88_REPORTED; Physical Fast 4/7_REPORTED; canonical delta=0; ORIGINAL_ACCEPTED_TICK=160/131072; CANDIDATE_V2_TICK161=PASS_SCOPED_ONLY; PRODUCTION=HOLD. No merge/force push/original worker or stage policies edit/tolerance or budget reset/auto tick162. Exactly one REI central F05 owner-gate enabling science unit, no additional source/optics atlas or estimator.

Next action is single specific source-owner decision on a versioned V2 change of the discrete local-defect ENCLOSURE EVALUATION, with new complete runtime contract and strict first-stage predecessor parity test, preserving original physical source and original 14 ledger/width/clock/event gates. Only upon explicit admission may tick161 become canonical. No production history mutation in this PR.

## Primary literature
Stefan Kopecz and Andreas Meister, On order conditions for modified Patankar–Runge–Kutta schemes, Applied Numerical Mathematics 123 (2018), 159–179, DOI https://doi.org/10.1016/j.apnum.2017.09.004. O. Mullier, A. Chapoutot and J. Alexandre Dit Sandretto, Validated computation of the local truncation error of Runge–Kutta methods with automatic differentiation, DOI https://doi.org/10.1080/10556788.2018.1459620. Neither independently verifies the REI code, nor do discrete step differences alone give continuum local truncation theorem.