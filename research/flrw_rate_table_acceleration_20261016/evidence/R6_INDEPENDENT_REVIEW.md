# R6 independent decision

**PASS_SCOPED_LI6_LI7_CONDITIONAL_COEFFICIENT_IMPLEMENTATION.** No blocking finding. Active added-species scope is 6Li and 7Li, each q=0..3. Carbon remains historical and unselected.

The generic log-linear error/slope derivation, prepared-temperature identity, source-branch handling, and event conservation reasoning from the preceding review are reused. The Li delta was checked against ten exact original coefficient lines. CI lower bounds [1,4,5] eV and per-charge RR/DR tabulation intervals give the complete-chain intersection [5/8.617385e-5,1e7] K. Li+ DR's negative fit amplitude is retained; its total is analytically positive because the larger positive amplitude also has the lower excitation energy. Binary64 underflow remains a separate numerical condition.

The explicit required `ElementalElectronicEquality` policy is a conditional electronic approximation. It retains separate (Z,A,q) identities and independently conserves 6Li and 7Li nuclei; their A-weighted sum conserves baryons. The returned electron source balances ionic charge. `IsotopeResolved` must return `MissingSource`. There is no default abundance, isotope threshold/mass correction, isotope accuracy bound, or added thermal/photo ledger. Li8/Li9 remain distinct upstream reservoirs pending nuclear closure.

Prior PR151 was checked at full head `9f455d98e2dd655412b561defff9e41e31dbb50a`; seven exact source pins are retained in `intake/LI_PRIOR_PR.json`. Its research inventory tracks Li7, omits Li6 explicitly, and does not supply isotope-resolved thermal rates. Existing native bookkeeping has thirteen species through He4.

Read-only R7 inspection accepts the recorded **sampled H/He coefficient** result: the initial 8193-node grid failed 1e-5, the authorized 65537-node grid reached 3.8387697880837957e-7 over 421431 tested temperatures, with zero reported mask/zero/invalid-input discrepancies. The direct reference is the unchanged source included by the probe. This is not a continuous curvature certificate, Li numerical result, batch/parallel admission, trajectory result, or measured full-driver speedup.

Implementation may proceed under the remaining root cumulative budget. C9 must inspect actual code and outcomes, including separate-isotope conservation, explicit policy failures, scalar/batch agreement, source-domain/fallback boundaries and point-RHS behavior. This reviewer ran no tests or scientific calculations. Full reviewed hashes and obligations are in `R6_INDEPENDENT_REVIEW.json`.

