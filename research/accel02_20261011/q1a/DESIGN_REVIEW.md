# Q1A fixed-q Gauss: prospective bounded design

Status: derived quadrature design with inspected source support and counted nodes; **not an ODE result or a spectral acceptance claim**. Model identity UNKNOWN. No RUN002, EVENT003 or Q0 calculation was repeated. The completed Q0 evidence was read as the authority for the measured source/IC discrepancy.

## Selected minimal candidate pair

Use the current FLRW geometry (shear parameter zero), with unchanged physical band 10–50000 eV, source/IC tables, gas closure and initial conditions. Keep two Gauss–Legendre angular ordinates. Let u=t/t_end and a_rel(0)=1. Build one immutable common set of log-q panel edges from:

1. 10 eV, 50000 eV and the provider's actual q_max = 168999.99999999997 eV.
2. Every distinct native UVB energy strictly between 10 and 50000 eV: 356 energies. Deduplicate only the *panel boundaries*, never the source table's duplicate-row jumps or values.
3. q_star=a_rel(u) E_star at u in {0,1/4,1/2,3/4,1} and E_star in {10,13.60,24.59,E_jump,54.42,50000} eV, clipped only as construction boundaries to the common q domain. E_jump is taken exactly from the duplicated native emissivity energy, 54.37903440052643 eV, rather than a shortened decimal.

For the pinned geometry these sets give **385 distinct edges, 384 panels**. Freeze Gauss order 1 on every panel as the candidate (384 energy nodes) and order 2 as the enriched rule (768 energy nodes). The resulting full packet counts are 768 and 1536 with the existing two angular ordinates. This is a prospective choice, made without any new evolved candidate results. The minimum log-panel width is 0.00016848071475683568, so there is no nearly zero-width panel from the literal construction.

The selected geometry epochs have (z,a_rel) = (15.9,1), (8.700190800825359,1.7422337711709786), (6.193258352434989,2.3494220799506222), (4.85362735846561,2.887098710777847), (4,3.3799999999999994). These are geometry evaluations, not new gas/radiation trajectories.

## Why this particular allocation

The UVB has 96 distinct native knots below 13.6 eV, 118 in 13.6–54.42 eV and 142 in 54.42–50000 eV. Its initial jumps and kinks matter: completed Q0 found a large 256-midpoint full-number error dominated by the sub-HI interval. The emissivity's initial native energy knots in this band are a subset of the UVB knots. Placing all these native knots at panel edges directly addresses that known initial-field pathology without smoothing, averaging jumps or fitting a replacement spectrum.

At u=0, the UVB number ordinate is affine in log q within each panel. A one-point Gauss rule is therefore exact for its panel number integral, up to floating arithmetic, including arbitrarily large zero-width jumps at boundaries. This is a derivation, **not a claim that the initial cross-section-weighted Gamma or heat is exact**. The order-2 rule also improves the initial energy moment, whose integrand multiplies the affine ordinate by exp(log q). No angular anisotropy is present in the initial field.

For a panel [l,r] in log(q/eV), use quadrature nodes l+(r-l)(1+x_j)/2 and weights (r-l)w_j/2. The packet weight includes the independent angular factor w_mu/2 exactly once. All weights are positive and time independent. The sum of all packet weights is log(q_max/10), because the normalized angular weights sum to one.

## Invariant use and implementation requirements

The same frozen q, mu_0 and weights must reach initial_photons, source_reference, native RHS, Jacobian, output moments and temporal event generation. Every node is still a fixed initial covector; E=q R(t,mu_0), and no remap or weight-derivative term is introduced. Keep native sigma/threshold/chemical-energy distinctions untouched. Temporal events remain necessary for each new quadrature node, including 50-keV entry, 10-eV source exit, atomic thresholds and the native emissivity jump. Keep dormant nodes exactly empty until their existing support-entry logic admits them.

Record all panel edges, Gauss orders, expanded q/mu/weight arrays, construction u values, native jump identity, all source/provider hashes and a grid content hash. Give this explicit grid selector semantics; do not silently reinterpret the old --energy midpoint count. Candidate and enriched results must have distinct output directories and immutable as-run source snapshots.

## Limits and cost before executing

This is *not* exact moving-threshold integration. Except at the selected geometry epochs, source edges/jumps and opacity thresholds cross the interiors of fixed panels. For an integrand with jump amplitude J inside a panel of log-width h, a fixed point rule can have error O(J h); the smooth-function Gauss order estimate does not apply uniformly as the discontinuity moves. Adding Gauss order helps sampling, but does not guarantee the frozen 1e-3 history target. In particular the propagated 10-eV source cutoff moves to q=33.8 eV, through panels whose ordinary UVB spacing is appreciably wider than the dense sub-HI native line spacing. Cross-section-weighted evolved radiation and coupled gas feedback remain additional error sources.

The q>50000 initially empty interval has only the selected entry-trajectory panel divisions. Its later high-energy source moments are therefore a specific risk to assess in the full moment comparison; exact initial number does not establish later source accuracy there. The initial scale used for the energy ledger changes only through the new legitimate UVB quadrature; the allowed normalized residual remains 1e-9.

No runtime guarantee is justified. Relative to the saved 256-energy run, storage and native packet loops grow by factors 1.5 and 3. Event count also grows, and each event restarts BDF. A linear node-cost forecast alone can therefore substantially underestimate runtime; roughly quadratic event-times-node growth is plausible but is not a measured scaling law. Stop after this prospectively selected pair if it fails; do not begin automatic grid doubling or an unbounded node search.

## Decision and follow-up

Execute the new candidate and enriched rule over the complete z=15.9→4 interval, preserve every first failure, and immediately checkpoint raw completed outputs before long postprocessing. Establish time refinement for the **new selected discretization** rather than inheriting the old midpoint-grid time decision. Apply unchanged domain, positivity, 1e-9 initial-energy and initial-nH ledgers, 2e-6 temporal fields, 1e-11 geometry and 1e-3 spectral targets. Compare the nine state/rate fields *and* source number/energy, radiation energy and species/total heat moments; report 129 and 65 epoch sets independently with their own fine-history amplitudes.

If the rule remains inadequate, retain the finite-grid result and classify the residual before changing representation. Q1B fixed-cell two-moment transport is a separate explicit decision with new realization/Jacobian requirements; it is not a hidden postprocessing correction to this trial. No Bianchi signal, new BASS native-cell adoption, CR/RCT physics, or continuum-error certificate follows from quadrature construction alone.

## Inspected evidence

- NEXT_DAG.json: Q1A/Q2 policy and frozen criteria.
- recovery/Q0_SOURCE_ATTRIBUTION.md and review/recovery/Q0_DECISION.json: completed source/IC attribution, read only.
- n2/characteristics.py, n2/run_event_coupled.py, integration/run_native_history.py: fixed covectors, weighted packet usage and event/ledger call sites.
- n1/provider.py and research/physical_provider_20261010/hm12_data.py: source identities, interpolation, actual geometry and table support.

No broad literature search is required for this bounded source-pinned numerical design. It relies on inspected implementation and elementary Gaussian quadrature, not an unverified external formula.
