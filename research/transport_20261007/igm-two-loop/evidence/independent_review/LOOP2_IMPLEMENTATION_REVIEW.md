# Independent second-loop implementation review

2026-10-07. This review covers the additive, transparent prescribed-stage control. It does not interpret the control as a completed production exporter or a coupled IGM history.

## Source and mathematical findings

The stock sweep continuously clips the actual parent measure at the stored boundary, obtains a positive exact-two-moment restriction, and uses the ephemeral moment-rule site. For transparent stock, all relevant owners are linear combinations of 1 and exp(eta): active count/energy, exported count/cutoff energy, and integrated redshift work. The one-site rule therefore integrates these owners exactly in real arithmetic for each restricted piece. No indivisible persistent photon node is held until crossing.

The source sweep separately integrates continuous geometric eta weights and follows source-bearing then source-free characteristic segments. It preserves the distinction between stock weights and geometric source weights. Exported cohorts transfer surviving count and energy before clearing active stock. The source is transparent; the optional fixed-opacity panel experiment was not executed. First-loop absorbing single-characteristic controls cannot be promoted into an absorbing continuous-panel sweep result.

The cutoff-specific characteristic selects one exact listed cutoff, derives its segment length from log1p((E_start-E_cut)/E_cut), and explicitly records the unanchored energy roundtrip. Its endpoint energy uses the declared physical cutoff; other owners keep their analytic integral definitions. This is an explicit event API and leaves the generic unsplit-cutoff rejection intact. Its small roundtrip defect must remain in the independent budget comparison rather than being assigned to a compensating owner.

The source oracle correctly separates exact supplied stored-log-coordinate outflow from its independent continuous birth-energy stock/energy/redshift integrals. Geometry differences are recorded. The source redshift expression integrates photon histories; it is not obtained by subtracting other ledger terms. The original number and energy floors remain unchanged, and source-free denominators do not use initial stock.

The LeftFront restriction implements y exp(beta y) on the parent support and retains the parent factor under interior restriction. The E^-3 observable interval is the correct Jensen/secant interval for fixed positive number and energy moments. Summing child bounds uses additional child moments and measures genuine spectral-resolution information. It is not a validated Verner enclosure or a directed-rounding interval certificate.

## Initial integrated evidence inspected

`work/integrated_loop2_first/loop2_oracle.json` reports 1794 owner checks across 138 budget cases, with 1258 exact-zero reference owners. It reports maximum positive owner relative error 4.45703527405077e-13 against 3e-12, number-budget ratio 0.00043403855945108223 and energy-budget ratio 0.0008156718138233969. All 18 envelope cases contain the independent density integral and shrink on refinement. These figures describe that particular executed source and oracle; the corrections below require updated final evidence.

## Concrete corrections requested before final acceptance

1. `anchor_relative` accumulates max(signed roundtrip) from zero, so negative roundtrip defects disappear. Report the maximum absolute discrepancy.
2. Source band-exit continuation replaces the outgoing energy convention with explicit Emin after clearing `first.u`. Record the actual discrepancy between the first segment terminal energy and epsilon Emin times its terminal count, separately from the final cutoff roundtrip. An integrated budget pass alone does not constitute the claimed transition audit.
3. `inverse_cubic` accepts arbitrarily large positive finite energies, while `powi(-3)` can underflow to zero and silently turn a positive mathematical bound into empty inventory. Restrict its numerical domain, retain log-positive factors, or fail closed. This does not affect the existing 13.7 to 20 eV fixture but matters to honest API admission.
4. The initial oracle's scalar ledger reconstructs a correctly rounded high-precision exp(log_hi+log_lo). The actual Rust readout instead computes exp(fl(log_hi+log_lo)). To claim a candidate readout ledger, emit the actual Rust scalar readout for every owner and use those values for budget checks. Keep the independent authoritative-log owner comparison separate.

These are numerical/reporting issues, not evidence that the underlying continuous-export or moment-envelope derivations are incorrect. Final gate remains pending artifact-bound corrections and updated execution evidence.

## Final corrected artifact-bound acceptance

All four requested corrections are present in the actual final source. The cutoff summary takes absolute roundtrip values, the source-band energy transition has an explicit 2e-12 continuity guard and exported diagnostic, positive E^-3 factors remain logarithmic, and budget checks consume the actual Rust scalar CSV readouts. The initial reconstructed-ledger result remains historical and is not relabelled.

Final execution reports 32 native tests, 903 panel oracle cases/3612 component comparisons, 86 tail cases/1118 owners, 48 anchored-cutoff cases/1248 owners, and 1794 continuous-sweep owner checks. The maximum sweep physical relative owner error is 4.45703527405077e-13. Across 138 actual-readout ledger cases, maximum number and energy budget ratios are 0.001976601154891768 and 0.001561103661235051. Maximum source-band exit relative discrepancy is 1.776356839400252e-15; maximum reported cutoff roundtrip magnitude is 1.306144734853125e-16. All 18 observable intervals contain the independent density integral and narrow under the prescribed refinement.

The reviewer compared every final source/input identity with `INPUT_SOURCE_SHA256.json`; all match. All recorded final-run process exit codes are zero. Decision: **ACCEPTED_BOUNDED_LOOP2** for exactly the finite scope in `LOOP2_INDEPENDENT_DECISION.json`. The production exporter, physical H/He feedback, inverse closure, repeated projection, and original 37-field long-window certificate remain open. No further optional campaign is needed to publish this bounded result.
