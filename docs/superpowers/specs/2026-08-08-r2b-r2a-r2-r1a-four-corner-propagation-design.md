# R2B-R2A-R2-R1A Four-Corner Propagation Design

## Goal

Execute the authorized physics preflight
`P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-FOUR-CORNER-BRANCH-AND-UNRESOLVED-OTS-ENERGY-PROPAGATION-PREFLIGHT`
without inventing a continuous source kernel, selecting a branch lane after seeing results, or promoting unresolved OTS energy to resolved heat.

## Fixed inputs

The following remain immutable: the 26-event registry, 46,080-node material state, owner law, canonical BDF forcing, MPRK22(1), Alexander L-stable SDIRK2, analytic safeguarded thermal root, exact He II Ly-alpha packet energy, and the separate photon/resolved-energy/unresolved-energy/escape ledgers.

## Branch lanes

For each node, let `f in [0.1,1]`.

- If `T < 10^4 K`, propagate the four strict source-safe corners `(v,f) in {0,1} x {0.1,1}`. No continuous `v(T)` adapter is permitted.
- If `10^4 K <= T <= 10^5 K`, find the bracketing Hummer-Seaton table cell and propagate the four endpoint corners `(v,f) in {v_left,v_right} x {0.1,1}`.
- In the table domain only, also propagate two explicitly noncanonical adapter lanes `(v_loglinear(T),0.1)` and `(v_loglinear(T),1)`.
- Preserve lane identities even when a node lies exactly on a table knot and numerical values coincide.

The four corners are load-bearing envelope lanes. The two log-linear lanes are named adapter auditors and cannot narrow the load-bearing envelope.

## Event-resolved population operator

The branch-aware population RHS is reconstructed from the locked event graph, not from the legacy sigmoid/exponential `v(T), f(x_HI)` functions. All photoionization, collisional ionization, recombination, and OTS cascade contributions are represented as nonnegative event fluxes and then supplied to the existing MPRK22 production-destruction update.

The event sum must reproduce the branch-parameterized population RHS at relative residual below `1e-13`; H and He nuclei residuals must remain below `1e-11`; no direct He I to He III event is allowed.

## Energy ownership

- He II Ly-alpha absorption uses exactly `40.813320 eV`; its H I and He I excess energies enter resolved heating exactly once.
- Two-photon and free-bound first moments remain in `E_OTS_unresolved`. The constructive spectra from the prior stage remain non-identifiability witnesses only and are not a dynamical thermal axis.
- Free-bound, Balmer, and case-B packet energy remains in `E_OTS_unresolved` unless a source-locked first moment exists.
- Escaped Ly-alpha energy enters the escaped-radiation ledger.
- Every event must have exactly one energy owner. Duplicate and unowned energy counts must both be zero.

## Numerical preflight

Run the first accepted microstep at the already validated partition `2048`. For each of the three shape lanes, compute one full step and two half steps for all eight branch policies: four load-bearing strict corners and four named adapter auditors. This is a 24-policy matrix; unidentified energy moments remain ledger-valued rather than duplicating trajectories.

Hard numerical gates:

- fixed-point/thermal roots converge;
- strict species positivity;
- H and He nuclei residuals `<=1e-11`;
- owner closure `<=1e-11`;
- photon closure `<=1e-8`;
- resolved thermal balance `<=1e-10`;
- total energy closure including unresolved and escaped ledgers `<=1e-10`;
- event reconstruction `<=1e-13`;
- full/two-half local error `<2e-4` for each lane.

## Predeclared uncertainty gate

At the end of the microstep, use only the load-bearing corners to form nodewise enclosures. The stage authorizes an uncertainty-qualified first canonical interval only if, in all three shape lanes,

- `max width(x_HII) < 2e-3`,
- `max width(x_HeII) < 2e-3`,
- `max width(x_HeIII) < 2e-3`,
- `max width(log T) < 2e-3`,
- and all hard numerical gates pass for every corner.

These thresholds preserve the earlier durable R1A uncertainty policy. They are deliberately separate from the stricter `2e-4` numerical local-error gate. Failure does not imply physical nonexistence; it routes to a source-extension/calibration stage for low-temperature `v`, `f`, or packet spectra.

## Transaction and evidence

A rejected branch lane must not mutate the parent state or accepted ledgers. The stage records per-lane certificates, nodewise enclosure summaries, exact/Wolfram identities, Decimal replay, research-harness phase documents, manifests, SHA-256 sums, and a compact immutable bundle. Production history remains unauthorized unless the predeclared uncertainty gate closes.
