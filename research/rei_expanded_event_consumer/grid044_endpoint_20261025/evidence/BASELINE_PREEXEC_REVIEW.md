# Independent baseline and scope pre-execution review

Reviewer: `/root/rei_baseline_intake`, separate from the frozen-contract author and implementation agent. Date: 2026-10-25. Reviewed the actual `/workspace/scratch/9d364a030876/REI_BINDING_IMPLEMENTATION_CONTRACT.md`, restored GRID044 source contract/payload/module, and saved donor NPZ metadata/final row. No provider quadrature, target_response execution, ODE, old test suite, fresh83 or NCP was run by this review.

## Decision

The selected instantaneous photo-only counterfactual at the actual saved z=2 state has a coherent scientific contract. **No model/normalization/baseline blocker was found.** Before the first numerical acceptance run, define the stated row-scaled error denominators explicitly, because the physical rates are very small. This is a narrow acceptance-definition clarification; the numerical tolerance and model need not change. Root and implementer were notified.

## Direct evidence

1. The restored `grid044_history.npz` byte SHA256 is exactly `ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b`.
2. Actual final row: eta=1.9459101490553132; a=0.33333333333333326; z=2.000000000000001; nHref=5.151254745827817e-6 cm^-3, hence5.151254745827817 m^-3; H=6.6227883620909854e-18 s^-1; s=8.642688723850055e-20 s^-1; b=0.1573743367974665; donor proper elapsed=9.742841244666013e16 s.
3. The immutable opacity payload uses eta=1.9459101490553132, redshift2 and nHref=5.151254745827818 m^-3. These differences are rounding-scale and below the frozen relative1e-14 binding tolerance.
4. The actual NPZ has21 species labels, Li7 before Li6. Its `atomic_abundance_per_Href` final column is the correct abundance input; `atomic_scaled` is isotope-conditional and must not be mistaken for the same quantity. Actual n,T_0,T_1 are exactly zero. Li6/7 trace values remain positive and must not be floored.
5. Actual donor endpoint T=14994.847774798709 K. This is the earlier grid044 background donor, not the subsequently integrated ANGTHERM01 thermal state. PHOTO-only rates do not consume T, so the scalar RR100–10000 K range is not an additional dependency. Record T as inherited context only; do not claim that a thermal provider was evaluated here.
6. GRID044 opacity `theory/IMPLEMENTATION_CONTRACT.json` explicitly uses normal-tetrad comoving ground-state targets, SI cross sections, proper seconds, n_i/nHref, unchanged stellar/external_IGM emission templates, birth support5–150eV, continuous free-streaming integration, and amplitudes(1,1). LiI64.39eV is a formula-branch split, not an upper valence cutoff. The root contract preserves all of these.
7. Existing `target_response` returns25 outputs and25x23 derivatives. Its first21 outputs are species rates, row21 is freed-electron number, rows22–24 are radiation loss/binding/primary-electron energy. The last two columns differentiate the two source amplitudes. It is not a25-state solver model.

## Equation and ownership audit

For physical number sources S and reference source R, the quotient rule is

`F=(S-x*R)/r`,
`dF=(dS-R*dx-x*dR)/r-F*dr/r`.

These equations correctly cancel homogeneous volume dilution when the same clock/frame/reference is used. For frozen comoving reference at fixed endpoint and abundance tangents, R=dR=dr=0. Existing REC f,J are already normalized; setting physical S=r*f and its x derivative r*J and passing through the quotient once recovers them. Dividing the REC outputs by r again would be an implementation error.

The root's distinction between the actual fixed-reference scenario and manufactured changing-reference derivative tests is adequate. Manufactured source/reference tests do not qualify an astrophysical injection history. No physical `partial_t` or geometry derivative certificate follows from them.

Thirteen isotope charge transitions with two additive spectral contributions are a consistent incidence construction. Event owner identity must be independent of arbitrary domain labels. The extra physical-key owner guard is needed because the inherited WU registry's exact key alone cannot rule out overlapping owners with different strings. Photon loss, binding gain and primary kinetic gain are complementary outputs of one photo event. The energy identity uses independently retained K; reconstructing K=P-chiGamma would make this particular check circular.

Primary electron energy remains nonthermal. HE degradation/stopping is unqualified, so thermal heat must remain null rather than zero. Generic CR event-ledger arithmetic is reusable at the new event inputs; CR C23B's physical spectrum has a different redshift/support and cannot be relabelled as GRID044. A scalar Gamma/P/K set supplies no angular absorption measure or four-force. Therefore BASS new absorption stress/feedback remains open.

## V6/D5 callback boundary

An actual21-component F=A*x callback with full-write J=A is valid for the frozen epoch and prescribed rates. Its isolated time box[t*,t*] is a point-evaluation contract, not an executable trajectory domain. The per-isotope component box is an outer domain; it does not enforce isotope-simplex sums by itself. The callback may be tested there as a mathematical linear extension, while full physical domain certification remains open. Tests must not silently substitute stored f for actual A*x evaluation.

A wrong finite J may pass the gateway; the separate derivative comparison must reject it. This is the correct distinction between callback protocol and derivative accuracy. Native physical norm and old D1–D5 verification must stay reused without replay or replacement implementation.

## Narrow acceptance clarification

`row-scaled` is not numerically defined in the frozen text. For source comparisons, use a row scale based on the absolute sum of expected contributing event terms (or an equivalently justified component scale). For Jacobian comparisons, use the maximum absolute reference coefficient in that row, with exact zero-row assertions. Rust/Python comparison should use corresponding row scales. Do not use `max(1, abs(reference))`: a wrong rate of order1e-14 would otherwise pass a1e-13-level test. Source conservation residuals should use event contribution scales, not absolute rate1. The exact chosen formulas must be recorded before execution. This review does not prescribe a new tolerance.

## Baseline and resource preservation

The30CPU/120wall new-unit allowance and separately measured compiler preparation are new bounded work, not residual old GRID044/83/ANGTHERM budgets. The requested no-IVP/no-old-test path preserves all historical spent/unknown/reserved records. Current central and sibling refs, backup receipts and native-offline limitations are handled by root at node entry. No full-network, L4 or empirical-spectrum claim is admitted by this review. Final independent decision requires the actual changed code, raw outputs, timing receipt and a viewed plot; there is no need to repeat the retained trajectory review.
