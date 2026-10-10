# Spectral quadrature: bounded next implementation

Status: **source-inspection design, not an implemented or validated repair**. This note does not use lost EVENT003 numbers and does not decide the recovered EVENT003 spectral gate. No ODE, RUN002 verification, grid-doubling campaign, or remote write was performed for this note. The actual model identity is UNKNOWN; no harness/model switch is claimed.

## What the code establishes

- `n2/characteristics.py::make_grid` uses one logarithmic midpoint per uniform q panel and Gauss-Legendre angle nodes. Its weights are positive and fixed. The state already includes these weights.
- `geometry_nodes` transports **fixed initial-frame covectors**. At fixed initial angle, E = R(t, mu0) q and R is independent of q. The physical direction is also independent of q at fixed mu0.
- `source_reference` uses the current physical source band 10–50000 eV, the exact pinned HM12 interpolation, and R^-3. `initial_photons` uses only the initial HM12 UVB, with its own native rows.
- HM12 interpolation is linear in the native ordinate and log(E), then linear in z. `HM12Table.moment` already integrates powers of E exactly for **that interpolation**, preserving native jumps. It does not integrate the native atomic cross sections.
- The event wrapper stops on atomic thresholds, physical source band edges, native emissivity jumps, and redshift knots. This controls temporal crossings. It does **not** replace midpoint spectral quadrature with threshold-split spectral integration. All ordinary HM12 energy knots are not temporal stops.
- The native RHS uses the same absorption events to update photon loss, species production, excess heat, and counters. This shared operator is a property to preserve. The native threshold cutoffs and chemical binding energies are distinct existing constants; do not merge them as a numerical repair.

These are inspected implementation facts. A threshold or source-quadrature contribution to a measured spectral discrepancy is a **hypothesis**, not a causal result. A source-only quadrature error, an initial-UVB quadrature error, opacity-weighted evolved-spectrum error, and coupled gas feedback must be separated before choosing the replacement.

## First action: attribution without another ODE

Create a new read-only `n2/diagnose_quadrature.py` and immutable output. At the saved 129 epochs (and the original 65-epoch subset), calculate exact source number and source energy moments of the pinned interpolation over 10–50000 eV and compare them with the actual as-run q/weight sums. Perform the analogous initial-UVB checks, including threshold-split source/IC band moments. Keep species-specific native-sigma weighted moments numerical; do not substitute an E^-3 cross section merely because the HM12 helper supports power=-3.

For one angular ordinate with normalized angle weight w_mu, define A_p(z) = integral E^p s_log(E,z) d ln E over the current physical band. Then

    source N_ref = w_mu R^-3 A_0,
    source Q_ref = w_mu R^-4 A_1,   Q = integral q dN_ref,
    source U_ref = R source Q_ref = w_mu R^-3 A_1.

For the current FLRW case R=1/a_rel, these angle-summed references are a_rel^3 A_0 and a_rel^3 A_1. For anisotropic runs the angular sum must be checked separately; in the continuum solid-angle map, the normalized integral of R^-3 equals a_rel^3. This angular identity is not a certificate for a finite n_mu rule.

Store signed errors, absolute errors, reference amplitudes, and maxima. Use the existing full-history normalization where a comparison is gated. Source moments alone do not certify the evolved radiation or gas. Reconstruction-based integration of saved photon samples is useful for sensitivity diagnosis, but its interpolation is an extra approximation and must be labeled; it cannot become a reference truth by declaration. No change to acceptance tolerances follows from this diagnostic.

## Minimal implementation candidate: fixed-q composite quadrature

The smallest patch compatible with the current packet state and Jacobian is a **fixed**, nonuniform q grid with positive composite Gauss nodes. Add an explicit grid factory or injected immutable grid to `Coupled`; do not silently reinterpret the existing `--energy` count. Save panel edges, Gauss order, q, mu, weights, construction policy, and a grid hash. Existing uniform-midpoint runs and their identities remain unchanged.

Use the diagnostic to choose a bounded panel budget, with static panel boundaries informed by initial UVB knots, opacity/source thresholds, source jumps and selected threshold trajectories q_star(t,mu0)=E_star/R(t,mu0). Freeze the construction epochs and panel budget before a new whole-history run. A knot placed at one time cannot align that threshold at every later time. Thus this is **threshold-informed fixed quadrature**, not exact time-dependent threshold integration and not guaranteed to meet 1e-3.

Feed precisely the same q, mu, weights to the UVB IC, source, native RHS, Jacobian, output, event generator, and counter accumulation. Positivity of weights and unchanged pointwise cross sections retain the existing packet-level algebraic number/energy cancellation. Every node remains a fixed covector; no remap term is needed. Each quadrature node, including multiple nodes per panel, receives ordinary event crossings. Keep below-10-eV retained photons, late 50-keV entries, empty dormant support, and source-only band restrictions as currently defined.

Validate one chosen rule against one prospectively frozen enriched rule over the full mean-redshift 15.9→4 interval; this is a bounded candidate pair, not indefinite grid doubling. If the point-packet rule cannot economically achieve the frozen gate, stop and report that limit before adopting a larger representation change.

## Exact moving threshold splits require a representation change

Moving q nodes or changing packet weights at every RHS call is **not** a safe drop-in patch. Current N_i is a weighted packet and U_i=R q_i N_i. Changing q_i or its weight adds transport/remapping terms that are absent from the implemented equation. Likewise, one packet at one E cannot generally represent both the exact source photon number and exact source energy of a finite band. Correcting only Gamma, a displayed plot, or accumulated counters is inadmissible.

A compatible, larger alternative keeps fixed q-cell boundaries and evolves two moments for each angle and cell:

    N_c = integral_c f(q) d ln q,
    Q_c = integral_c q f(q) d ln q,     U_c = R Q_c.

Since q is conserved and R is q-independent for each angular ordinate,

    dN_c/dt = S_0,c - sum_a A_0,a,c,
    dQ_c/dt = S_1,c - sum_a A_1,a,c,
    dU_c/dt = R dQ_c/dt - lambda U_c,
    lambda = H + s (3 mu(t)^2 - 1).

Here A_p,a,c = integral_c q^p [c n_a sigma_a(Rq)] f(q) d ln q. Use the *same* A_0 and A_1 for photon sinks, species production, absorbed-number counters, and energy transfer. Chemical gain per event is chi_a; excess heat is R A_1,a,c - chi_a A_0,a,c (times the eV-to-erg factor). The two terms therefore sum to absorbed energy R A_1,a,c. Total radiation expansion work is sum_c lambda U_c. Existing gas cooling/Case-A escape and signed CMB exchange remain unchanged.

At each RHS evaluation, split the integration **within each fixed cell** at physical atomic thresholds divided by R, band edges divided by R, and current source-table knots/jumps divided by R. These quadrature nodes are integration scratch points, not newly transported state packets. Keep the same native sigma provider and native gas response. `HM12Table.moment` can supply exact S_0,c and S_1,c for the declared source interpolation, while opacity-weighted photon moments require converged numerical quadrature.

This requires an explicit positive, moment-realizable within-cell reconstruction and its derivatives. A declared positive two-parameter density (for example, a normalized power law in q) can represent interior admissible N,Q pairs; it is a **new numerical closure**, not an exact spectrum. Zero cells must remain exactly zero. Enforce N>=0 and q_left N <= Q <= q_right N, with the upper bound narrowed to currently active support for cells straddling the 50-keV entry boundary. Do not populate the out-of-band dormant portion or clip failed moments back into the cone. Preserve initial-UVB discontinuities and report finite-cell reconstruction error. An implementation must explicitly handle cells partially entering support and endpoint/singular realizability cases.

The current native ABI accepts weighted evaluation packets, but a straightforward dynamic quadrature reuse does not by itself preserve the independently stored cell moments or exact source moments. Prefer a reviewed cell-moment adapter or a versioned moment input that passes the common integrated photo-rates/heat and moment sinks together. Do not force an exact source moment into counters while the gas/photon RHS uses a different sampled source. The present diagonal photon Jacobian cannot be reused unchanged: the reconstruction couples N_c and Q_c and its derivative must be included. This path is a larger patch and needs its own algebraic/local review before a whole-history solve.

## Gate and scope preservation

Keep time-field target 2e-6, initial-energy-normalized energy ledger 1e-9, initial-nH-normalized number ledger 1e-9, geometry identity 1e-11, and empirical spectral/angular target 1e-3. Evaluate the nine history fields and declared source/radiation-energy/heat moments at common whole-history epochs, plus accepted-domain and ledger checks at the existing prescribed locations. A finite pair passing 1e-3 remains an empirical refinement result, not a continuum certificate. Never substitute a source-budget normalization for the fixed initial-energy criterion.

The fixed physical scope remains conditional initial gas (T=20 K, xHII=2e-4, helium initially neutral), pinned HM12 IC/emissivity, finite 10–50000 eV source, H/He primary photoionization, imported Case-A atomic subset, prescribed geometry and isotropic CMB bath. No CR/RCT/secondary cascade, diffuse reabsorption, stress backreaction, high-energy extension, or observational EoR admission is introduced.

## Concrete bounded DAG and parallel work

1. Q0: source/IC moment attribution from pinned tables and saved states; no ODE. Output determines whether a minimal fixed-q patch is justified.
2. Q1A: immutable composite fixed-q grid injection and common operator use. Independent review checks packet accounting and event coverage. No new physical provider.
3. Q1B, alternative only if Q1A is inadequate: explicit fixed-cell two-moment closure, shared moment operator, realizability, support handling and new Jacobian. Do not implement both solvers simultaneously without the Q0 decision.
4. Q2: one full 15.9→4 candidate/enriched comparison, unchanged gates, immediate raw-output durable checkpoint before report generation.
5. Q3: independent scientific decision, then BASS export binding to the accepted native history and its exact source/commit hashes. Existing reduced-history N4 adoption does not validate a new native history automatically.

Parallel tasks that do not depend on choosing Q1A/Q1B: a real checkpoint-resume CLI with solver/state/source/grid identities and an interruption-recovery test; read-only profiling of saved execution logs and bounded native serialization costs; BASS consumer schema and provenance binding; raw-completion archival automation. Existing `RESTART.npz` alone is not a supported resume interface. None of these tasks should repeat RUN002 or upgrade its scope.

## Provenance

This source inspection was written during recovery of the missing 256-grid run. It does not consume that run's numerical outcome. Exact inspected source hashes are in the companion JSON.
