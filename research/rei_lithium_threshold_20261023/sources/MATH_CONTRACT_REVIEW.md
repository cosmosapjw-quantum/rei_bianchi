# Independent assessment of the proposed ANGTHERM02 contract

Status: **MATHEMATICAL DESIGN ADMISSIBLE, NUMERICAL EXECUTION PENDING**.

The controller's late-time frozen-bath Li calculation, threshold-partitioned
GL8/16/32 rate integration, same-finite-M16 reconstruction control, and global
attenuation envelope at delta=2e-8 form a discriminating finite experiment.
The experiment should report conditional trace-Li accuracy, separately from
the old fully coupled ANGTHERM01 trajectory and from bath interpolation error.

## Approved mathematical elements

1. The fixed-q measure remains dmu0. Rescaling a quadrature interval to the
   known active domain introduces its ordinary interval-width factor, not
   a second physical-angle Jacobian.
2. The four-state late Li Markov system is triangular in its upper two charge
   states. The neutral scalar equation has a common source r1 cLi in every
   angular/attenuation variant, with 0<=cLi<=1.
3. With a uniform optical-depth bound delta, attenuation changes each of the
   LiI/LiII fractions by at most expm1(delta) for the same seeded Li state and
   fixed bath. The proof does not require cLi=1.
4. The full-prehistory scalar upper equation with source r1(1-F) is valid:
   extra LiI photoionization only lowers fI, while fII<=1-fI. Its integrated
   optical envelope closes the initial depth bound if it remains below delta.
5. The source-specific sigma maximum can be bounded by 1.66e-18 cm^2 on the
   relevant 5.392..10 eV interval using its single positive stationary root.

## Required finite checks before numerical admission

- Keep PCHIP logT/logv accepted-history interpolation an explicit prescribed
  model; do not equate it with the unsaved original continuous solution.
- Use the saved log counts to bound the omitted higher-energy photon tail;
  reconstructed count underflow is not exact physical zero.
- Verify the saved eta_star LiI value lies below the global comparison
  solution at eta_star. If needed, reset only the comparison upper bound
  upward and recompute its remaining envelope; report the change.
- Include numerical error margin in the B<delta decision. A generous gap
  and a tighter independent envelope run are useful observed evidence; a
  formal interval certificate would require interval or equivalent bounds.
- Keep same-finite-rule reconstruction error separate from GL8/16/32
  differences and attenuation error. Use raw native Li fractions.
- Split the continuum rate calculation at all-on/partially-on/all-off
  endpoints. Although the partial-support rate is continuous at the last
  crossing, its derivative generally has a square-root endpoint behavior.
- Do not claim new exact whole-system photon/energy conservation by combining
  the corrected Li fraction with old photon/gas/work ledgers.

## Independence and performed work

The reviewer read the source model and existing results and performed only
finite array inspection, a cubic stationary-root evaluation, and saved-array
trapezoid diagnostics. No new IVP, code implementation, Git mutation, or
publication was performed. See MATH_CANDIDATES.md for the derivations.

## Audit of the actual frozen THEORY_CONTRACT.md

The controller's final contract was read in full at
`rei_isotope/research/rei_lithium_threshold_20261023/THEORY_CONTRACT.md`.
Decision: **READY FOR BOUNDED EXECUTION**. No blocking mathematical correction
was found. This review applies to the actual Hermite-primary/PCHIP-secondary
bath definition, ten-case table, delta=2e-8, sigma_max=1.66e-18 cm^2, and
the declared numerical comparison margins in that document.

The new actual-absorption-energy ledger is mathematically consistent:
`I-I_star+Qgas+Eesc-Eabs=0` follows event by event for the prescribed bath.
It neither updates T nor silently joins the old photon/gas/shear-work ledgers.
The derivative formula for the Hermite log-temperature bath,
`(log T)'=U'/U-v'/(N_nuc+v)`, is also correct.

One norm clarification is useful for downstream reporting. The remaining
high-energy count `Ntail/YLi` bounds each Li-fraction component's change from
those omitted future primary photoabsorption events; the full four-component
L1 norm is bounded by **2 Ntail/YLi**. Each absorption transfers one population
unit between two adjacent charge states, hence has L1 norm two, while
subsequent common Markov evolution is L1 contractive. With zero sum, any one
component is bounded by half that L1 total. This statement is conditional on
the fixed bath and no additional photon births, exactly as in the contract.

The global F envelope and the explicit seeded-state inequality suffice for
the stated family of late optical profiles bounded by B(eta_star). They do
not identify an unknown earlier continuum Li state with the saved M16 state;
the final contract correctly treats the latter as the late initial-value
definition. No extra gate or process layer is required by this clarification.
