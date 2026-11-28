# Equation–data–code map

The equation numbers refer to theory/THEORY_KO.md. Units and source scope are in CONTRACT.json.

| Theory or data | Implementation | Verification / interpretation |
|---|---|---|
| Relative Maxwellian M_j; eq(1) derivative ladder | components/moments/maxwellian_moments.py: PreparedMaxwellianMoments.evaluate | Shared alpha,beta,gamma,delta; direct positive moments; derivative recurrence; independent SI integral/80-digit control |
| CCC87 rows, incident electron energy, sigma in a0² | components/diagnostic/data/CCC_TICS_1S.txt; run_diagnostic.py | Exact donor SHA, no pi multiplier; heavy fixed target only; partial13.6058–968.61eV |
| Moment feasibility alpha*gamma>=beta² | components/pair/reactive_moments.py: RawMoments | Scaled test preserves roundoff defect, no clipping; explicit zero reason |
| Heavy fixed-target STF eq(3) | RawMoments.coefficients | kappa2=4gamma/(15theta²); incoming-loss projection only |
| Finite-mass incoming eq(4–6) | reactive_moments.py: binary_loss | Stable mass fractions, signed C, parent Q, same2x2 block for each STF component; six independent6D raw-velocity controls |
| Conditional derivative construction eq(1) | moments_from_rate_derivatives | Caller acknowledges T-independent microscopic kernel and differentiation; empirical fit derivative labeled conditional |
| Reactive centralization eq(8) | centralize_reactive_source | Includes+m R_n uu^T; one-step identity, boost and omitted-number mutant |
| Resolved event number/charge/energy ownership | components/event_bridge/vendor/rei_resolved_local.py | Byte-identical donor; per-baryon event rates, explicit products and all nine reservoirs |
| Supplied net central tensor per event | components/event_bridge/event_bridge.py: attach_event_tensor | Explicit J/event and trace/2=dEth; volumetric n_b multiplication; no default J=0; thermal/charge inventory declarations |
| Finite source admission | components/event_bridge/finite_bridge.py: from_finite_evaluation | Requires partial-source acknowledgment, binds T/mass/mapping/identity; underflow and CCC finite-mass reinterpretation rejected |
| Isotope/source reduction | components/event_bridge/source_lift.py: validate_source_lift | Tests RHS_full(Lz)-L RHS_reduced(z) in supplied domain; no universal isotope-equivalence claim |
| Whole-goal B1–B5 dependencies | GLOBAL_GOAL_DAG.json; NEXT_DAG.json | B2 incoming projection progresses; gain, transport, closure, full gas and metric still have explicit dependencies |

## Error owners

Source support and cross-section interpolation are physical-input uncertainties. Finite quadrature error belongs to the selected piecewise-linear source model. Binary64 underflow belongs to representation and does not authorize a physical zero. The tiny conditional-mean failure was an arithmetic-order defect; only that path was corrected and retested. A missing optional SymPy dependency and an invalid Wolfram symbol are environment/tool failures, whose raw records are retained. A display-label overlap was corrected without recomputing scientific outputs.
