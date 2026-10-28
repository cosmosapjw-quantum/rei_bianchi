# Current pilot cases, initial conditions and shear input: C2 code trace

Baseline PR248 HEAD `022f2ed85595364f05834d8eb1573434efce92d0`, as supplied by
the controller. Repository AGENTS.md was read; PhysMath Research Loop1.3.0
SKILL/POLICY/CODING definitions are reused from the unchanged preceding unit.
This audit reads existing code and stored arrays only. No RHS, coefficient,
test, figure or IVP was executed or repeated. The extracted values and useful
source SHA256 identities are in `CURRENT_INITIAL_VALUES.json`.

## Actual case definitions

The producer is `rei_source_history_20261028/implementation/coupled.py`.
Its CLI maps the case prefix to `mode` and the suffix `refined` to the solver
tolerance choice. All three cases use the same copied first baseline row,
same prescribed old bath, same output times, and same variable scaling.

| Item | OFF_base | ON_base | ON_refined |
|---|---|---|---|
| New-source amplitude alpha | 0 | 1 | 1 |
| Replenished external photon bins and CR flux | Disabled | Frozen illustrative values | Same as ON_base |
| Direct thermal/fast injection | Disabled | Frozen illustrative values | Same as ON_base |
| Thermal escape kesc | 0 | 1e-18/s | 1e-18/s |
| Fast escape ke_n,ke_T | Both0 | 1e-3/s,2e-9/s | Same as ON_base |
| Fast slowing ks_n,ks_T | 1e-2/s,1e-8/s | Same | Same |
| Intrinsic beta, n+HI/HII capture | Retained | Retained | Retained |
| New TI photoionization | Gamma=0 | Frozen external-bin Gamma | Same as ON_base |
| New TII recombination | 1e-14/s retained | Same | Same |
| Old stable-isotope photo/RR bath | Retained | Same prescribed bath | Same prescribed bath |
| Solver | Radau | Radau | Radau |
| Relative tolerance | 1e-7 | 1e-7 | 2e-8 |
| Absolute tolerance, scaled variables | 1e-11 | 1e-11 | 2e-12 |
| max_step / first_step arguments | Not set / not set | Not set / not set | Not set / not set |

The unset `max_step` uses the backend's default unbounded step maximum;
`first_step` is selected by the backend. Output times are not imposed step
boundaries. `jac_sparsity` is the compiled conservative23x23 sparse dependency
mask; no analytic Jacobian is passed. Signed Newton trial states use the smooth
polynomial RHS without clipping. Physical output positivity is checked later.

OFF means new external sources and escape are off. It does not turn off the
inherited photon/RR bath or every physical process. Since its initial n/T and
fast stocks are zero and there is no new production, those stocks stay zero in
the stored OFF trajectory. The old bath is a fixed reconstruction, so OFF is
not defined as exact reproduction of the original nonlinear donor trajectory.

## Initial populations, fast stocks and ledgers

All populations below are particles/Href, with Href the conserved comoving
reference whose physical density evolves as nHref. This is not an evolving
total-baryon normalization in the open source model.

| Displayed state | Initial value |
|---|---:|
| n | 0 |
| H1 I | 0.9998 |
| H1 II | 0.00019999999999999998 |
| D I | 2.4995e-5 |
| D II | 5e-9 |
| T I, T II | 0,0 |
| He3 I,II,III | 1e-5,0,0 |
| He4 I,II,III | 0.082,0,0 |
| Li7 I,II,III,IV | 0,5e-10,0,0 |
| Hidden Li6 I,II,III,IV | 0,1e-14,0,0 |

The isotope totals are exactly the declared rounded donor-model totals, not a
newly calibrated BBN calculation. The inherited electronic isotope-equality
approximation sets both HII/H and DII/D to approximately2e-4. Their physical
interpretation and any charge-exchange correction belong to the new authority
contract; this audit does not alter those fractions.

The evolved physical state order is
`[the17visible states, Bn,BT,Un,UT, accumulated_external_baryons, accumulated_free_electrons]`.
The last six entries initially vanish. Bn/BT are particles/Href; Un/UT are
eV/Href. The last two entries are accumulated changes, not the initial physical
electron density. Initial algebraic heavy-plus-hidden charge is
0.00020000550001 electrons/Href; the stored initial electron bath has that same
value. The bath and the evolved electron ledger are separate objects thereafter.
The original complete21-state baryon/Href ratio is1.32808000350006.

Stable-species scales are max(initial isotope total,1e-25). n/T and fast stock
scales use the maximum predicted alpha1 frozen-QSS stock over the saved knots,
with floor1e-30; each thermal T charge shares the total-T scale. Fast energy
scales are1e6 times their corresponding fast-stock scales. These are solver
scales, not inserted population floors. The two ledger scales use initial
visible baryon and heavy-charge stock, respectively. The exact stored23-element
scales for each case are retained in the extraction JSON.

## Donor and prescribed background closure

Input CSV is `rei_fast_selected_20261028/outputs/grid044_M4_nominal_all21_populations.csv`.
The matching input NPZ is
`rei_fast_selected_20261028/inputs/angtherm_selected/research/rei_angular_thermochemistry_20261023/results/grid044_M4_nominal.npz`.
Both contain the same201 saved eta epochs, eta=ln(a/a_initial), z=21exp(-eta)-1,
from z20 to2. The current elapsed clock begins at this initial source-on epoch;
it is not cosmic age. Its prior finite reconstruction uses log-H PCHIP and
dt=deta/H, fixed GL8 checked againstGL16. No clock recomputation was done here.

The actual stored first-epoch temperature is **300K**. It comes from
`angular_model.Reduced`'s300K initial thermal-energy construction, not the
older `AtomicNetwork21` public8K prescribed-temperature scenario. Calling this
saved bath a physical standard8K postrecombination model would be incorrect.

The prepared pilot reconstructs old proper photo hazards as
`c*nHref*sum(sigma(E_j)*photon_groups_j)` and recombination hazards as
`nHref*electron_per_Href*alpha(T_saved)`. It reads actual24x201 M4 photon groups,
temperature and electron histories. Hazards are piecewise affine in elapsed
proper time; nHref is log-linear. Old stable H,D,He3,He4,Li7 transitions remain;
old n/T atomic terms and all old beta terms are excluded. The new beta/capture
ownership occurs once. Hidden Li6 follows its saved prescribed history and
enters charge/baryon bookkeeping; it is not advanced by the new17-state RHS.
Gas temperature, old photons, old electron rate bath, H and shear do not respond
to the new source populations or open-matter injection.

## Exact current shear input path

`old_bath()` imports the pinned `angular_model.py`, constructs `Reduced(M=4)`,
and obtains energies/cross sections from `coefficients(eta)` without rerunning
the donor. `angular_model.Background` reads
`inputs/background/grid044_history.npz`: eta,H,s,b,nH_ref_cm3. It constructs
`saved_bp=s/H`, `bfun=CubicHermiteSpline(eta,b-b[0],saved_bp)`,
`hfun=PCHIP(eta,logH)`. Sign is the default+1. The geometric model is the LRS
Bianchi-I metric `diag(a²exp(-2b),a²exp(-2b),a²exp(4b))`, with
`sigma=diag(-s,-s,2s)` and s=db/dt. The same map redshifts photon energies and
changes their angles. It is a prescribed geometry in the current pilot.

Stored initial background values are H0=1.2206975634162752e-16/s,
s0=2.990086160628583e-17/s, b0=0,
bprime0=0.24494897427831772, and nHref0=0.0017668803778189406/cm³.
The coupled23-state pilot has no evolved b, shear tensor, stress tensor, H,
Einstein constraint, or Einstein feedback variable. A new shear/IC helper must
therefore be an additive explicit construction; relabeling current prescribed
background interpolation as solved Bianchi dynamics would be incorrect.

## Time samples and current boundary

The output time constructor takes the201 matched proper-time knots and four
40-point log-spaced sequences from .001/L to30/L, where L is lambda_n,
lambda_T, Lfast_n or Lfast_T. Points outside the finite endpoint are discarded;
the union has361 stored times for each actual case, including t0. The sampled
interval ends at9.742841241346858e16 proper seconds. Figures later mask t0 only
on logarithmic axes, leaving the raw data unchanged.

Current work is C2 trace and later contract-bound helper authoring. Previous
pilot tests, trajectories and figures are not rerun. New non-IVP tests require
the controller's explicit bounded allocation; NO_MORE_IVPs remains in force.
