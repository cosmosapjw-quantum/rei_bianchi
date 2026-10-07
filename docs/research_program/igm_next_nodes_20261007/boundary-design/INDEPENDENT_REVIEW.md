# Independent continuous-boundary design review

Design/math verdict: **confirmed**.

Empirical candidate status: **not established**. No candidate solver or coupled history was implemented or run. This verdict establishes the consistency of the stated research design and gates; it does not certify binary64 robustness, spectral convergence, completion, or speed. The existing p64/p128 pair still fails 8/37 fields.

## Reviewed state and evidence

- Frozen design SHA-256: `2bdc7a6744f42818256c90de07285f5a56c02a3b2a587140a4965e6579959709`.
- Independently recomputed all seven source/evidence hashes: all match. Inspected immutable Python source/grid/event ownership, Rust export, comparator, field summary, and relevant pilot audit/diagnostics. The pilot's recorded accepted-state maxima are inherited evidence, not newly recomputed accepted-state arrays.

## Contract axis

The research-only boundary is respected. No immutable production source, physical configuration, pilot history, comparator, or resource cap was changed by this review. The new prototype plan is bounded pure-radiation work and explicitly excludes coupled histories and automatic promotion. Original zero-initial production allowances remain unchanged; nonzero-initial analytic controls are correctly labeled separately.

## Quality axis: confirmed mathematical claims

1. **Continuum and units (sections 2–4).** The per-H, per-d-eta density has no additional dilution term. Proper-time rates divide by H when using s=ln(a). Reynolds transport gives -f(b+) in number, -epsilon*Ec*f(b+) in energy, and the additional redshift sink -U. M=integral exp(eta)f removes that energy-weight drift from the stored moment. The physical-log-energy finite-volume signs in option B are also correct.
2. **Source and closure (section 3).** Both stated E^-2 source integrals follow directly from q proportional to exp(-eta). The ordinary exponential closure has a unique finite beta for every interior realizable pair. The front-weighted closure retains this property: its derivative is a strictly positive covariance, its finite-order zero at R preserves endpoint concentration limits, and its interior limiting trace is genuinely zero. Empty, atomic-limit and underflowed states must remain distinct.
3. **Kernel and ownership (section 5).** The frozen-per-s q/rates formulas, lambda=0 limits, and number/energy identities are correct. Q_E integrates the characteristic's declining emission energy; it is not the fixed-energy source convention in the old helper. Nonnegative heat additionally depends on keeping each nonzero species rate inside its energy support, as required by event splitting. The small checks satisfy that condition.
4. **Smoothing rejection (section 6).** Altering only cumulative outflow changes the independent residual; compensating stock alone leaves the spectral owners and gas trajectory unchanged. Fractional node deletion at Ec generally incurs (E_node-Ec) times the removed number. A single assumed mean cannot reproduce arbitrary energy-weighted absorption. These arguments support the proposed change; they do not prove this is the only possible conservative discretization.
5. **Tests and limits (sections 8–9).** The proposed tests distinguish continuous densities from genuine atoms, retain source/threshold topology, require independent owner/invariant negative controls, and separate temporal, quadrature and reconstruction convergence. The revised T1 correctly uses the initial active interval.

## Review finding resolved before this verdict

**Causal-source-front leakage: medium severity, high confidence, design section 3/T4.** The initial full-panel exponential closure could assign photons to eta>s+ln(Emax), even while preserving N/M and every global budget. The final design adds occupied-support metadata, the general upper Reynolds terms, a zero-trace constraint, a positive front-vanishing reconstruction, and a source-front test. This resolves the missing design gate. Merely changing a sampled endpoint value would not have resolved it.

## Mandatory gates still open for implementation

- **Quadrature versus stored moments:** shared positive quadrature preserves identities for its represented initial inventory, not automatically for stored N0/M0. For f=exp(2*eta) on [0,1], ordinary Gauss2 misses N by 0.0032787 relative and M by 0.0144333. Section 5 correctly requires positive moment-exact quadrature or controlled initial-moment residuals within the original complete budget. No such robust implementation has yet been demonstrated.
- **Realizability and tiny supports:** prove/test the inverse closure, scaled/log arithmetic, endpoint measures, empty-cell limit and nonnegative frozen stage rates. Rejection is a valid admission rule, not a proof that the time integrator can advance. No clipping, tail deletion, or repaired mean is allowed.
- **Shape and source accuracy:** conservation does not bound Gamma, heat, causal-front shape error, or the bias introduced by switching/reconstructing closure families. T4/T7/T8 must exercise front entry and panel-edge transitions as well as separate panel and quadrature refinement. Frozen-q injection and its emitted ledger must remain paired.
- **Coupling and performance:** the common gas transaction, accepted-state budgets, all 37 fields, retightening, complete output schedule and resource semantics remain untested. The new source-front metadata does not establish that two stored moments have the cost of two old nodes.

No remaining blocking contradiction was found in the frozen design. The next justified step is the separately bounded analytic prototype, subject to its own frozen numerical/resource contract and independent review.

The cited [Vaytet et al.](https://arxiv.org/abs/1101.4955), [Jiang](https://arxiv.org/html/2209.06240v1), and [Clawpack advection chapter](https://www.clawpack.org/riemann_book/html/Advection.html) were opened independently. They support the stated general frequency/characteristic finite-volume context, not the proposed closure's empirical accuracy.
