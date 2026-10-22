# Physical interpretation and finite plotting contract

The executable specification is `PHYSICS_PLOT_CONTRACT.json`. This unit adds three independent initial-parameter plot sets and two explicitly multi-parameter galleries to the reionization dossier. It reuses the 82 admitted atomic histories and the separately admitted conditional nuclear postprocessing. One new intermediate positive matter-stress case is allowed; no old trajectory is rerun.

## R1 — Observable and question

Display the evolution of all eight retained nuclear species and all 21 census entries against redshift and elapsed proper time. Independently vary the initial shear norm, radiation-stress norm, or matter-stress norm while holding the other two initial physical quantities at zero. The three primary comparisons keep the varied component's signed orientation nonnegative. Additional comparisons expose orientation reversal, cancellation, and strong shear.

The plotted abundances are numbers per baryon, `Y=n_species/n_B`, and ionic entries are the absolute saved census `Y_Aq`. This common-rest-frame pilot should not be confused with the original dossier's more general tilted multi-current abundance definitions.

## R2 — Data and finite scope

The old grid contains 75 L16 product-grid cases, two initial-cancellation cases, two negative-shear cases, and three L24 numerical controls. The old reference18-state trajectory is outside that 82-case registry. Every old trajectory has 257 saved samples from z=20 to z=2. The new case is `quotient_L16_S0_Am0.8_Ar0`, with the same numerical settings as matching L16 cases, stored only in this new unit. Its nuclear postprocessing uses the admitted existing rate/closure implementation and processes only this case.

The new case supplies a third positive-orientation matter-norm point. Choosing S=.2 for that point would change the supposedly fixed shear and is therefore excluded. The initial parameter table must come from saved diagnostics rather than rounded filenames.

## R3 — Definitions and physical matching

The saved diagnostics define

- `Sigma_F=abs(signed_Sigma)`;
- `Pi_m=abs(P_m)`;
- `P_r=P_gamma+P_nu`, `Pi_r=abs(P_r)`;
- `Pi_total=abs(P_m+P_r)`.

In particular, `Pi_total` is not `Pi_m+Pi_r`. The same norm can correspond to two different signed orientations. Holding raw amplitudes Am and Ar nonzero while changing shear would not hold the physical stress norms fixed because their normalization contains the initial Hubble rate. Zero-stress anchors avoid this ambiguity.

Measured existing initial matter stresses for Am=(-.8,0,1.6) at S=Ar=0 are approximately (-5.468874345897007e-4, 0, 1.0937748691794015e-3). Radiation stresses for Ar=(-.8,-.4,0,.4,1.6) at S=Am=0 are (-2.388555339655477e-3,-1.1942776698277385e-3,0,1.1942776698277385e-3,4.777110679310954e-3). Apparent zero matter stresses of order 2e-19 are floating-point roundoff. The fixed-zero-axis gate is absolute 1e-15; actual values remain recorded.

## R4 — Model separation

Six bulk isotope totals are sums of the inherited charge census. Those isotope abundances are constant in that atomic model. The admitted nuclear calculation treats them as passive reservoirs; its negligible consumption does not justify plotting fabricated changes obtained by adding increments far below floating-point resolution.

T and n totals come from the canonical conditional nuclear history, joined by exact case name. `log_T_n` stores natural logarithms in order T,n. Its all-bare, instantaneous-thermalization closure is a conditional comparator, not a prediction of the charge-state history or stopping of fast nuclear products. The T neutral/ionized partition remains unresolved. Its two entries must be visibly annotated as unresolved, not plotted as the old structural zeros. A free neutron has no atomic charge partition; its panel can show the separately labelled conditional total n.

These displays do not merge the atomic and nuclear lanes into a solved coupled ion/nuclear system. The observed nuclear consumption justifies the passive comparison within the stated conditional model; it does not validate its microphysical closure empirically.

## R5 — Time, redshift and fixed inputs

Redshift decreases from 20 to 2 left to right. Proper elapsed time is measured separately along each trajectory from z=20, with one displayed Gyr defined as 1e9 Julian years (365.25 days each). This is not the cosmic age. A universal secondary time axis over the redshift plots would be incorrect because H changes between cases.

The physical baryon-density, prescribed gas-temperature and UV histories as functions of redshift are shared. The expansion rate, elapsed time, shear and stress histories respond dynamically. “Held fixed” applies to the stated initial parameters, not their entire evolved histories.

## R6 — Positive and limiting examples

The isotropic initial anchor is `quotient_L16_S0_Am0_Ar0`. The shear slice uses initial norms 0,.01,.05,.2,.6. The radiation slice uses Ar=0,.4,1.6. The matter slice uses Am=0,.8,1.6. These amplitude values are registry keys; plots and tables use physical diagnostic values.

The two cancellation examples have equal and opposite initial P_m and P_r to roundoff but retain nonzero component stresses. Cancellation does not persist automatically. Positive and negative shear at the same norm are distinct solutions. The context plots separate photon and neutrino stress, whose subsequent interactions differ, without introducing a new neutrino experiment.

## R7 — Numerical interpretation

At common saved redshift, the observed largest ionic conditional-fraction difference from the isotropic L16 reference is approximately 2.542e-3 for the strong-shear zero-stress example, 2.1083e-8 for the positive radiation endpoint, and 4.1618e-10 for the positive matter endpoint. Existing L16/L24/tighter-tolerance control discrepancies reach 3.3929270504273745e-9. These control discrepancies are diagnostic scales, not certified global error bars or a confidence interval.

The matter-only ionic response is therefore unresolved relative to the saved numerical-control discrepancy. Its raw differences may be shown, with that label; they must not be sold as an established physical effect. No discrepancy is subtracted from a curve. No fresh convergence campaign is implied. Difference plots compare conditional fractions at the same z, only; plotting a same-z subtraction against case-dependent time would not make it a same-time difference.

## R8 — Finite execution and files

Each primary group has totals and ionic-group figures on both axes, a common-z conditional-fraction difference figure, and a signed-stress/context figure: 18 figures. Each additional gallery has totals and ionic-group figures on both axes and a signed-stress/context figure: 10 figures. Total: 28 figures, each in PNG and PDF. Eight isotope facets/grouped panels account for all eight nuclei; the ionic manifest accounts for all 21 census entries, including explicit unresolved T entries.

Use logarithmic abundance values directly for tiny nuclear inventories. Do not turn underflow into a structural zero or replace exact zeros with a chosen positive plotting floor. Initial zero T/n can be omitted from the logarithmic ordinate with a clear annotation.

## R9 — Acceptance and independent interpretation

Check exact case-name joins, matching grids, initial fixed physical axes, positive ordering of primary norm values, finite atomic histories and inherited conservation/positivity gates. Record actual case parameters and end times. Verify every selected case is shown on both axes, all species are accounted for, and every requested visual exists. Inspect representative and crowded panels for label legibility. Fresh scientific review judges claim scope and source/observable consistency; it does not authorize a broader physics claim merely because rendering succeeds.

## R10 — Stop and next result

The executable next step is rendering and the one new bounded case. Stop after that case, its nuclear postprocess, figure inspection, and one scoped independent review/targeted repair if needed. No repeated old82 runs, extra nuclear source search, unconstrained parameter search, or iterative accuracy campaign is authorized by this contract. The parent controller integrates the figures into the seven-chapter dossier while preserving the distinction between its general theoretical construction and this restricted numerical experiment.
