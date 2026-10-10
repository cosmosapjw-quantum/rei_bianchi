# SYNC03 independent theory gate

Decision: **ADMIT FOR FINITE-INTERVAL, SOURCE-CONDITIONAL RECEIVER DIAGNOSTICS**. This is a theory decision before the receiver results are reviewed. Numerical execution remains a separate gate.

The inspected source is the actual F08 proper-electron export at REI commit `84afbe7660ec79e5e43822e7aea49a0a9ee8daea`, with four T0/T1 FLRW/BI files named and hashed in `intake/rei/NE_INPUT_MANIFEST.json`. The BASS implementation inspected is `intake/bass_rec/bass/_rustcore/src/microphysics/{visibility,visibility_clock}.rs`. Input rows are proper densities in cm^-3 at accepted normal-time endpoints on [0, 10^13] s, with D=1. The source explicitly supplies **no observer tail**. A tail of zero is therefore a new, explicit truncated-interval diagnostic boundary, not recovered source data.

## Rate, clock and sign

Use increasing future normal time t. With the constants actually owned by the pinned BASS code,

    k = c sigma_T 10^6,
    q_i = k n_e,i,
    qbar_i = (q_i + q_(i+1))/2,
    d_i = qbar_i (t_(i+1)-t_i),
    A_j = sum_(i>=j) d_i,
    tau_j = h + A_j,
    S_j = exp(-tau_j).

Here n_e is the exported cm^-3 value, 10^6 converts it to m^-3, q has units s^-1, and h is the dimensionless observer-tail depth. No additional scale-factor dilution, clock conversion or Doppler multiplication is required for this D=1 normal-time source. The BASS constants are c=299792458 m/s and sigma_T=6.6524587e-29 m^2; this review binds to that implemented constant rather than silently replacing its authority or precision.

The continuous sign convention is d tau/dt=-q and d S/dt=qS>=0. The cell probability mass is

    M_i = S_(i+1)-S_i
        = exp(-tau_(i+1))[-expm1(-d_i)] >= 0.

The endpoint-mean rule is exactly the cell integral of the piecewise-linear interpolant through the supplied q endpoints. Consequently, edge optical depths, edge survival and complete cell masses are the same for that interpolant and its frozen endpoint-mean cell surrogate, apart from arithmetic. It does not make either interpolant the exact continuous source solution. Interior visibility q(t)S(t), peak height and peak location are not interchangeable between these two reconstructions.

For a linear cell with width H, coordinate s in [0,H] and endpoint difference Delta q, the exact interior depth difference is

    tau_PL(t)-tau_frozen(t) = Delta q s(H-s)/(2H),
    max |tau_PL-tau_frozen| = |Delta q| H/8.

This optional bound concerns reconstruction within one cell; it is not a global time-discretization estimate.

## Finite interval mass and the tail

The normalization identity is

    sum_i M_i + S_0 = exp(-h).

The omitted later-interval last-scattering probability is 1-exp(-h). Including that term restores unit total mass. For h=0, sum M+S_0=1. Do not normalize sum M to one, and do not describe M as a probability distribution conditioned on a scattering unless that additional conditioning is explicitly performed and named.

A common tail h multiplies every survival and every cell mass by exp(-h), while adding h to each depth. A h=0.1 stress therefore has a known exp(-0.1) scale factor. It is a boundary sensitivity experiment, not an empirical tail estimate.

If h is genuinely unknown with only h>=0, the finite-history optical-depth contribution A is still known in the selected reconstruction, but absolute observer survival/masses are not. They can range down to zero as h grows. A common unknown tail cancels exactly in a paired depth contrast and only supplies an unknown common attenuation to paired survival/mass contrasts. Distinct FLRW and BI tails need separate evidence; one may not assume cancellation for them.

## Conditional endpoint boxes

Let n_i^- <= n_i <= n_i^+ be the source's conditional endpoint bounds. Apply the same positive conversion and averaging to construct qbar_i^- and qbar_i^+. For a tail interval h in [h^-,h^+],

    d_i^- = qbar_i^- H_i,                 d_i^+ = qbar_i^+ H_i,
    tau_j^- = h^- + sum_(i>=j) d_i^-,     tau_j^+ = h^+ + sum_(i>=j) d_i^+,
    exp(-tau_j^+) <= S_j <= exp(-tau_j^-).

These are valid positive-linear transfers of the exported conditional boxes. They remain conditional on the original binary stage densities and actual source-stage inputs. They do not enclose an independently re-evolved globally consistent uncertain trajectory, physical density uncertainties, continuum chemistry error, atomic-fit error or receiver floating-point rounding unless those terms are separately supplied. Float endpoint containment checks are useful validation but are not automatically outward-rounded interval proofs. High-precision recomputation controls arithmetic comparison separately.

A conservative cell-mass enclosure follows without assuming independence:

    exp(-tau_(i+1)^+) [1-exp(-d_i^-)] <= M_i
      <= exp(-tau_(i+1)^-) [1-exp(-d_i^+)].

For a complete interval use its monotone form directly:

    exp(-h^+) [1-exp(-A_0^-)] <= sum_i M_i
      <= exp(-h^-) [1-exp(-A_0^+)].

It is normally sharper than adding independent cell-mass interval widths. Correlations can tighten these enclosures but are not needed to make these conservative conditional transfers valid.

For a paired contrast Delta A=A_BI-A_FLRW, a conservative conditional interval is [A_BI^- - A_FLRW^+, A_BI^+ - A_FLRW^-]. A common tail cancels from Delta tau. If that interval lies above zero, the selected conditional reconstruction supports greater BI finite-interval depth, smaller BI survival and larger BI finite-interval scattering mass. A positive central value alone does not establish that conditional sign. It never establishes the sign of the physical continuum contrast.

## Perturbation bounds, including unequal finite tails

For two nonnegative rates q and r on a common clock and interval, let

    E(t) = |h_q-h_r| + integral_t^b |q-r| du.

Then |tau_q-tau_r|<=E and

    |S_q-S_r| = exp[-min(tau_q,tau_r)] [1-exp(-|tau_q-tau_r|)]
              <= 1-exp[-E(t)].

For a cell [t_i,t_(i+1)],

    |M_q,i-M_r,i| <= [1-exp(-E_i)] + [1-exp(-E_(i+1))].

For pointwise visibility g=qS, where pointwise rate values are actually supplied,

    |g_q-g_r| <= |q-r|S_q + r |S_q-S_r|
               <= |q-r| + r[1-exp(-E)].

An opacity-integral bound alone does not bound the height or location of a visibility peak. The inspected BASS `compare_opacity` API explicitly assumes common tails; for unequal tails the additional |Delta h| must be included outside that API, or its return must not be advertised as the complete bound. With uncertain tails in finite intervals, the largest admissible |Delta h| is the maximum absolute endpoint difference between the two tail intervals. If the same tail parameter is shared, Delta h=0 exactly, including when its common value is uncertain.

To compare T0 with T1, integrate the original piecewise-linear endpoint reconstruction of each on a common refinement, or sum each complete set of original cell depths directly for whole-interval depth. Interpolating only coarse frozen cell averages onto fine cells can change the compared reconstruction. A T1-T0 difference is a measured resolution sensitivity, not an a posteriori continuum certificate. Measured cancellation of a paired contrast is useful but does not remove the separate absolute-history errors.

## Scientific scope and four-thread separation

The old F08 S0 source explicitly uses HH/RCT/CR OFF. The new HE low-temperature IGM point has an operational RCT domain [1000,10000] K, no new history, no physical admission and baseline RCT OFF. Its existence does not invalidate old OFF S0 execution, and its point pass does not enable RCT for the old hot S0 or close the previous empty FT03 overlap. Likewise the new CR photon-to-IGM point bridge is a separate CR-OFF implementation/owner-import task; its point tests cannot be reused as old F08 history dispatcher evidence.

For fixed common normal-time endpoints and zero tilt, the proposed receiver compares the two supplied scalar electron histories. It is not a directional Bianchi sky observable, a fixed-observed-redshift comparison, a volume filling factor Q_V or an observational EoR prediction. Those require additional geometry, endpoint/observer choices, physical histories and source calibration.

The BASS cold-Thomson validity contract preserves a separate finite-temperature and spectral-support gate. An executed numerical Thomson-opacity diagnostic at positive gas temperature is not a certified physical Thomson collision operator, and the 13.7 eV source line is not automatically a complete scattered-observable photon-energy authority. The existing physical admission HOLD remains.

Numerical admission now requires source/hash checks; valid grids and nonnegative bounds; native execution of the pinned API; independent depth/mass arithmetic; explicit tail and reconstruction metadata; unchanged original failure records; and a claim ceiling matching this review.
