# Saved-history scientific figure contract

2026-10-29 unit; prepared 2026-10-28 UTC. Baseline publication identity supplied by controller: PR251 HEAD c5ab42c8673db614e7fb16695ad071c65becb81b. This local recovered checkout has no .git. Authority lane read AGENTS.md and exact user physmath-research-loop version1.0.0, including research policy, theory loop, evidence/handoff and REI execution overlay. This is a constructive rendering contract for existing results; no IVP or new physical closure is authorized.

## Scientific object and identities

Use only saved OFF_base, ON_base, ON_refined in rei_source_history_20261028/outputs. The canonical population table is pilot17_populations.csv; NPZ physical/scales and saved validation provide independent schema/normalization checks. There are361 common time samples, including201 matched background epochs and early transients. The17 visible states in order are n, H I, H II, D I, D II, T I, T II, 3He I, 3He II, 3He III, 4He I, 4He II, 4He III, 7Li I, 7Li II, 7Li III, 7Li IV. Display number abundance particles/Href, including rare states without flooring. The actual initial bath is300K. The optional8K profile is unexecuted and does not enter these figures.

## Clock derivation and dual axes

The original saved clock is built in history.py from matched H(eta)>0:

    eta = ln(a/a0),  eta0=0,  z_mean=21 exp(-eta)-1,
    t_k = integral_0^eta_k exp[-PCHIP(log H)(u)] du,
    elapsed_Myr = elapsed_proper_s /31557600000000.

The original integral used interval GL8 and comparison GL16. Reuse those computed t_k; do not regenerate a cosmological age. At t=0 the source-onset epoch is z=20. No absolute cosmic-age offset is supplied. In the existing population table eta at transient times is linear interpolation in the saved t_k. For a plotting tick at t, piecewise-linearly interpolate saved (t,eta) and compute z=21 exp(-eta)-1. For a chosen redshift tick z*, invert eta*=ln[21/(1+z*)] against ordered (eta,t). Because all matched knots are present, interpolating the361 table rows reproduces the same piecewise-linear map up to roundoff. Do not interpolate z itself linearly, extrapolate outside the saved interval, or substitute LCDM cosmic age.

Every evolution panel has elapsed time in Myr on the bottom and mean redshift on top. Full-range panels may use linear time to expose late evolution; abundance panels may use logarithmic positive elapsed time to expose the initial evolution, provided t=0 is separately stated/marked and not relocated to an invented positive time. Any zero-inclusive nonlinear axis must print its exact transform. A standalone all17 log-time overview plus linear-time grouped views is a useful complementary choice. z20 to z2 maps to the saved finite interval ending at9.742841241346858e16s.

Early transient redshift is degenerate at display precision: the first positive row has t=.08238295318127252s, eta=9.978766240739514e-18 and stored z=20.0. The many-to-one floating-point z plateau does not invalidate increasing t/eta. On such panels retain the upper axis with a single explicit annotation 'mean z approximately20 over this interval'; do not fabricate separated inverse-redshift ticks or claim temporal degeneracy. When useful, a separately labeled delta-z=21[-expm1(-eta)] inset can reveal the small change; it is not a replacement for labeling mean z. Tick validation tests eta rather than strict monotonicity of rounded z.

## Finite figure inventory and grouping

1. One axis containing all17 ON_refined abundance curves, each distinctly identified. State the case in the title. Provide a three-case companion or controls in the grouped plots; all17 means one shared abundance panel, not17 isolated panels.
2. Grouped abundance panels containing all17 states exactly once, with OFF_base dashed, ON_base dotted and ON_refined solid. Group by abundance scale, not isotope alone: compute each state's peak positive abundance across the three saved cases; assign bands peak>=1e-3, [1e-6,1e-3), [1e-12,1e-6), and <1e-12. Empty bands may be omitted, dense bands split at a documented abundance boundary. Record actual membership and peak ranges. This makes abundance proximity reproducible while curves reveal evolution timescales. Early-transient n/T grouping is additionally physically motivated by their source-onset relaxation.
   Chosen display refinement: split the final peak<1e-12 band at1e-16 into [1e-16,1e-12) and <1e-16, separating the Li IV scale from the n/T scale; Li I belongs to group 3 with Li II and Li III. The actual inventory therefore has five abundance groups when all five are nonempty; the same exact-once coverage and recorded-membership requirements apply.
3. Signed source response ON_base minus OFF_base at identical saved times; optionally show ON_refined minus OFF_base as a refined sensitivity. Name which difference is plotted. Use per-Href differences or divide by the explicitly named frozen state scale. Signed linear or symmetric-log axes retain zero and negative values. An arbitrary relative difference divided by OFF is undefined at zero and is excluded.
4. Refinement evolution delta_i=(ON_base_i-ON_refined_i)/scale_i using the existing NPZ scale_i, not the instantaneous stock. Show all17 with signed values or label absolute values explicitly. Threshold is max_t|delta_i|<=1e-5; saved maximum is9.4756292130907e-8. This is a two-resolution agreement diagnostic, not an inferred convergence order or physical error bar. A summary bar chart is optional and needs no evolution dual axis.
5. Early transients using saved positive-time samples, with n,T I,T II and optionally Bn,BT in separate explicitly normalized panels. Log elapsed Myr and the degenerate upper-z annotation resolve causality from zero initial stocks. Do not treat connected sample lines as additional solver output.
6. Conservation evolution, with signed open baryon and heavy/free-electron residuals for all three cases, zero line and the original absolute threshold1.0820350005000101e-8. A normalized residual/threshold axis avoids mixing scales. Optionally show actual Btot separately to explain open-system depletion.
7. Optional analytic Bianchi response, explicitly titled 'analytic prescribed-background benchmark'. Keep it separate from the saved chemistry. If plotted against x=a/a0 it is a response curve, not an elapsed-time evolution figure and no fictitious t/z mapping is attached. No isotope response or shear-coupled new trajectory is inferred.

Use consistent state colors and case styles, readable labels, units, panel letters and concise captions. Distinguish trace species by labels as well as color. Avoid simultaneous unlabeled overlays of51 curves in the overview. Positive vertices outside a panel’s declared x/y window are omitted from its vector geometry; they remain available in raw tables and outputs/plot_data.json. Per-curve omission counts are recorded in figures/FIGURE_METADATA.json. The overview uses its stated isotope multipliers; grouped panels use raw abundances. Exact zero and negative numerical samples remain in tables; log-domain omissions are declared, never replaced with a plotting floor.

## Conservation formulas and interpretation

    Btot = sum_i A_i y_i + Bn +3 BT + hidden_Li6_baryons,
    R_B = Btot + accumulated_external_baryon_ledger - Btot_initial,
    Qheavy = sum_i q_i y_i + BT + sum_q q y_Li6,q,
    R_Q = Qheavy - accumulated_electron_ledger - Qheavy_initial.

The CSV already contains R_B and R_Q calculated from the physical23 state. The electron ledger is distinct from the prescribed electron bath used by recombination. Btot changes under injection/escape; plotting its decline as conservation failure is incorrect. Initial Btot=1.32808000350006/Href and ON_refined endpoint=1.2057192755038328/Href. Hidden Li6 is prescribed and included once. No instantaneous evolved total is forced to unity.

## Three scientific axes

Symmetry/gauge: t is proper elapsed time along the background normal congruence; eta and z_mean refer to mean expansion. A constant time-origin shift does not change elapsed differences. Mean redshift is not the directional photon redshift of an anisotropic geometry. The17 abundances are local scalar stocks and do not supply a shear tensor or angular photon multipoles.

Invariants: require exact common case grids, finite values, positive frozen scales, same initial stocks, raw signs retained, the original open baryon/charge tests and the existing two-resolution comparison. Angular rotations do not change scalar populations or tensor contractions. In a separate Bianchi benchmark use the inherited STF convention sigma=s diag(-1,-1,2), sigma²=3s², Frobenius norm²=6s²; never substitute the historical sqrt3 normalization for sqrt6.

Observables: these are illustrative prescribed-bath number histories and source-response diagnostics. The source switches also include external escape; ON−OFF therefore measures the configured full switch, not a single channel. Curves are not measured line strengths, cosmological abundance posteriors or a self-consistent radiative/thermal evolution. The optional Bianchi forced response is sigma=x^-3[sigma0+(kappa pi0/H0)F_(3+p-m)(x)] with F_n=(x^n-1)/n and F_0=ln x, inherited from prior completed derivation/checks. No new theorem or no-go is proposed.

## Validation and budget execution boundary

Before admission, mechanically verify table/NPZ agreement, all17 coverage, matching times, clock endpoint/tick roundtrips, exact group coverage, signed difference/scales, original residual thresholds, finite vector coordinates, declared zero omissions and labels. Reuse accepted raw scientific results; validate only changed plotting dependencies. Small source/table tick residual tolerance may be1e-12 relative with explicit absolute handling at zero; this numerical serialization tolerance does not replace any physical acceptance gate. A fresh independent reviewer inspects generated files and validation evidence once, authorizing a targeted repair only for an actual defect.

Main cumulative606.634374 versus original600 may support a genuinely new bounded scientific diagnostic under the existing temporary-increase policy, with ceiling strictly below900 and restoration to600. It cannot absorb presentation work. Presentation63.924256494 leaves1.075743506CPU seconds under the explicit approved65; original30 and planning20.819461885/original10 remain historically visible. No ledger transfer or allowance reset is authorized. A single standard-library CSV/vector SVG/PDF renderer can plausibly fit, but cost is not established until measured. Freeze a finite one-pass command, reserve tail cost inside1.075743506, bound the child, count actual child plus wrapper CPU and stop without automatic retries. No Matplotlib startup, trial render or conversion campaign is presumed free. If this cannot deliver the requested artifact honestly, return completed source/contract plus a concrete finite additional-presentation proposal; do not infer a >65 grant from the figure request. Report unknown overhead as UNKNOWN_NOT_ZERO.

Local figure completion preserves global working33/88, central28/88 and physical-fast4/7. Original manifest gates must genuinely close before those counts change. Prior failed attachments are retired by user direction and are not a new dependency.
