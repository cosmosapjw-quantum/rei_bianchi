# Independent theory and code review

Decision: **PASS_SCOPED**. No blocking or open actionable defect was found. The kernel is accepted as a finite frozen-bath mathematical reference with ordinary floating-point evaluation. This decision does not certify a physical RUN19 trajectory or a nonlinear gas/radiation tube.

Reviewer: `/root/orch_rei`, assigned the independent Astra-tier authority role under the current REI AGENTS routing. Actual runtime model identity was not exposed and is recorded as UNKNOWN. The reviewer did not write the contract or implementation. The reviewed hashes and individual decisions are in `INDEPENDENT_REVIEW.json`.

## Theory and implementation

The column convention is consistent. A pair `(i,j)` means forward i→j and backward j→i. Its approximate-minus-exact flux difference contributes −d to i and +d to j. The independent dense test assembles each directed transition into the destination row and origin column. With e=p−p_hat and r=p_hat′−Kp_hat−b, the error equation is e′=Ke−r, so the residual-integral sign and l1 bound are correct.

For a bounded piecewise-continuous finite Markov generator, nonnegative off-diagonal entries and zero column sums give a nonnegative column-stochastic propagator. Its l1 contraction supports the frozen-bath residual inequality. The helper accepts signed hazard differences; it does not itself validate or construct a physical generator. That separation is appropriate for this scope.

Pairwise cancellation and the independent absolute-rate majorant are correct in real arithmetic. Negative reconstructed populations are reported and retained, with absolute populations used for the independent majorant. Source differences are not treated as mass-conserving automatically. The mixed observable formula uses both l1 error E and a separately justified mass-error M; the test with constant weights correctly exposes the failure of assuming M=0 for mismatched mass.

The common-relative-error API requires an explicit shared epsilon for the two directions of a pair. Equal uncertainty bounds, a common temperature and detailed balance do not silently activate cancellation. The approximately 10^9 gross-to-net ratio in the receipt is a manufactured near-balance control under that declared identity. It is not an actual physical rate-table improvement.

Clock conversion and event accounting are explicit. The caller must convert hazards and source terms to the stated clock, with dt/dx included once, and separately supply initial error, solver residual and event/source defects. The kernel does not infer Hubble or density units. The contract correctly leaves state-dependent temperature, electron density, opacity and radiation/source feedback in the separate nonlinear tube problem.

## Certificate boundary

The samples-only certificate request returns unresolved and no total. Sampled trapezoid values use a different API and status. The hidden-bump control demonstrates why endpoint samples cannot certify a continuous residual integral.

The status `conditional_certificate` is acceptable only with the documented meaning: a floating evaluation of an exact-real bound assuming caller-proved continuous suprema. A provenance string records that premise; it does not verify it. Products and sums are not outward rounded and may round or underflow. Accordingly these outputs are **not machine-checked enclosures**, even when the caller supplies valid real-valued suprema. The README and receipt state this limitation; no additional implementation repair is needed for the present reference-kernel scope. A future certified adapter must add the actual continuous and arithmetic enclosure, rather than reuse this status as a production certificate.

## Evidence reviewed

The existing executor receipt records 11 tests, zero failures/errors, exit0 and 0.003195261s test time. Current kernel, test and runner hashes match that receipt. The independent review did not rerun the test suite, native histories, physical providers or NCP work.

The analytic two-state case records final l1 error 0.08626629747, analytic residual-integral bound 0.54894471383 and panel-supremum evaluation 0.55429352344. Its positive decreasing residual justifies left-endpoint panel maxima for this manufactured case. Dense controls cover2,4,17states with orientation changes; event/source mass, invalid inputs and negative reconstruction are covered independently of the dense construction.

The next action is to preserve and publish this scoped kernel with the review. Applying it to RUN19 requires original-owner hazard/source identities, real coefficient uncertainties, initial/event contributions and the continuous gas/depth admissible-tube work. No physical Li/Be/EC, full EoR, continuum or production admission is issued by this review.

