# Fixed-state joint photon-moment receiver: a bounded correlation bridge

Date: 2026-10-08. Scope: exact readout algebra and receiver admission only.
Model identity: UNKNOWN; no model-family inference or performance claim. The
physmath skill and the recovered research harness's common instructions and
phase 6 were read. The harness's bundled state is an unrun template, not evidence.

Evidence read directly: `bridge/vendor/source_transfer.py` (R11),
`inputs/CONSUMER_CONTRACT.json`, and `inputs/receiver_record.rs` from rei_bianchi commit
`8477bae16accaf3de168669aafd2f31eac2ca811`. Source identities are recorded by the
parent handoff. This note derives a new conditional adapter; it does not certify
the producer's physical moment errors, solve chemistry, or advance R11/R12's
continuous-state programme. Status: **DERIVED; exact toy vectors calculated;
production admission HOLD**. Independent decision review is owned by the parent.

## 1. Same fixed state and physical clock

Use R11 coordinates `h=xHII`, `y=xHeII`, `z=xHeIII`, `w=erg/H`. Write

\[
f=n_{He}/n_H,\quad X_e=h+f(y+2z),\quad D=1+f+X_e,\quad
T=\frac{2w}{3k_BD},\qquad
a=(1-h,\ f(1-y-z),\ fy).
\]

Here `a_i` is the number of absorbing atoms/ions of species i per hydrogen
nucleus; species order is `(HI,HeI,HeII)`. The three entries of `a` must not be
confused with the cosmological scale factor. Require `0<=h<=1`, `y,z>=0`,
`y+z<=1`, `w,nH,H,kB,epsilon_eV>0`, `nHe>=0`. All state, constants, background,
provider semantics, evaluation time, and unit declarations are identical across
the compared moment alternatives. Density is **proper** `cm^-3`.

Let `Gamma_i` have units `absorber^-1 s^-1`, and let `Ecal_i` be its
incident-energy moment in `eV absorber^-1 s^-1`, not excess heating per absorber.
With physical time t, the photo source alone is

\[
\dot h=(1-h)\Gamma_H,\qquad
\dot y=(1-y-z)\Gamma_{HeI}-y\Gamma_{HeII},\qquad
\dot z=y\Gamma_{HeII},
\]
\[
\dot X_e=\sum_i a_i\Gamma_i=\dot h+f(\dot y+2\dot z),\quad
\dot B=\epsilon_{eV}\sum_i a_i\chi_i\Gamma_i,\quad
\dot U_{abs}=\epsilon_{eV}\sum_i a_i\mathcal E_i,\quad
\dot Q=\dot U_{abs}-\dot B.
\]

`dot X_e` is `electrons/H/s`; the last three quantities are `erg/H/s`.
Each ionization adds one free electron, while the nuclei count per H is fixed, so
`dot D = dot X_e` for this contribution. Differentiating `T=2w/(3kB D)` gives

\[
\boxed{\dot T_{photo}=\frac{2}{3k_BD}
\left(\dot Q-\frac{w}{D}\dot X_e\right)
=\frac{2\dot Q}{3k_BD}-\frac{T}{D}\dot X_e.}
\]

Dropping the second term changes the observable: nonnegative photoheat does
**not** imply a nonnegative temperature source. If `dot Xe>0`, its sign changes
at `dot Q/dot Xe = w/D = (3/2)kB T`. Equality is an exact cancellation. This is
the photo contribution, not the complete thermal RHS; expansion, Compton,
collisional, recombination, and other material contributions remain separate.

For `s=ln a_cosmo`, `d/ds=H^-1 d/dt`; therefore all physical-time source
components above must be divided by the same positive fixed `H` when the
receiver requests derivatives per `dln a`. The R11 optical **source action** is
`C_T nH dotXe / H^2`, where `C_T=c sigma_T` has units `cm^3/s`. This dimensionless
partial source action is not an observed temporal jump or the derivative of an
arbitrarily prescribed gas interpolant. An already per-dln-a quantity must not
be divided by H a second time.

## 2. Shared affine generators preserve the declared correlations

At that single fixed state define the six-dimensional moment vector

\[
m=(\Gamma_H,\Gamma_{HeI},\Gamma_{HeII},
\mathcal E_H,\mathcal E_{HeI},\mathcal E_{HeII})^T
=m_0+\sum_{j=1}^k g_j u_j,\quad -1\le u_j\le1,\quad 0\le k\le6.
\]

Each generator has a stable identity and is shared across all six coordinates;
its first three entries and last three entries carry different declared units.
The cap of six (at most 64 vertices) is a bounded implementation choice, not a
physical limit. The set may be a conditional enclosure or a sensitivity family;
the upstream premise must say which. A sensitivity family is not an error bound.

For every scalar R11 readout q there is a row `L_q` with `q=L_q m`, because the
gas state and constants are held fixed. In particular,

\[
L_T^{\Gamma_i}=-a_i\left(\frac{2\epsilon_{eV}\chi_i}{3k_BD}
 +\frac{T}{D}\right),\qquad
L_T^{\mathcal E_i}=\frac{2\epsilon_{eV}a_i}{3k_BD}.
\]

Thus with exact rational input arithmetic,

\[
q_0=L_qm_0,\quad c_{qj}=L_qg_j,\quad
q_{min}=q_0-\sum_j|c_{qj}|,\quad q_{max}=q_0+\sum_j|c_{qj}|.
\]

These are attained scalar extrema over the **supplied full cube**: choose
`u_j=sign(c_qj)` for the upper extremum and its negative for the lower. Different
outputs can require different vertices, so the Cartesian product of scalar
output intervals is an outer box, not the exact joint output set. Preserve
`q0` and shared `c_qj` if downstream combinations need the correlations.

If one first discards correlation, the input-coordinate radii become
`r_i=sum_j |g_ij|`. The corresponding scalar box radius is

\[
r_q^{box}=\sum_i|L_{qi}|\sum_j|g_{ij}|\ \ge\
\sum_j\left|\sum_iL_{qi}g_{ij}\right|=r_q^{joint}.
\]

The triangle inequality proves the comparison. A decorrelated box may include
unphysical moments even if every member of the original family is admissible;
its wider image remains a conservative algebraic comparison, not an admissible
physical family. For a signed difference use the same linear map, but do not
impose physical positivity on a signed difference vector. Check the two actual
moment families first.

The exact robust condition for nonnegative `Tdot` over the full cube is
`Tdot_center >= sum_j abs(Tdot_generator_j)`; strict inequality proves strict
positivity. The analogous upper-end condition proves nonpositivity. This is a
conditional fixed-state sign certificate, not a time-evolved thermal statement.

## 3. Necessary domain checks and their limits

Enumerate every vertex `u_j in {-1,+1}` (one empty-tuple vertex for k=0) and
require for each species

\[
\Gamma_i\ge0,\qquad \mathcal E_i-\chi_i\Gamma_i\ge0.
\]

Affine inequalities achieve their minima on vertices, so this checks the whole
cube. Equivalently, their center must dominate the sum of absolute generator
coefficients. Do not clip a failed vertex or replace its negative value by zero.

These inequalities are necessary, **not sufficient**, for spectral
realizability. In particular, `Gamma_i=0, Ecal_i>0` cannot arise from one
nonnegative finite measure using the same energy, cross-section and weights.
Require `Gamma_i=0 => Ecal_i=0` at vertices when labelling inputs physical;
nonnegative Gamma and convexity then give the same implication throughout the
cube. If finite support with an independently justified `Emax` is supplied,
also require `Ecal_i<=Emax Gamma_i`. Even these separate-species checks do not
prove that all three pairs come from a **common** radiation spectrum and the
declared provider. Common-spectrum provenance remains an upstream premise.

Exact arithmetic certifies the algebra of supplied rational numbers only. It
does not certify binary64 provider evaluations, quadrature errors, state errors,
time interpolation, a continuum spectral integral, or the correctness of the
generator enclosure. Missing scientific enclosure premises must stay UNKNOWN,
not become zero-width errors.

## 4. Why current accepted midpoint records fail rate admission

The pinned `record.rs` labels its authority
`OBSERVED_BINARY64_OWNER_OPERANDS__KERNEL_PROVIDER_STATE_ERROR_UNRESOLVED__NOT_FULL_WIDE_ADMISSION`.
`Accepted.total[7:10]` holds `(A_HI,A_HeI,A_HeII)` and `[10:13]` holds
`(B_HI,B_HeI,B_HeII)`. These are integrated absorption owners (photons/H and
incident erg/H after eta aggregation), not per-absorber instantaneous moments.
Per-segment provenance explicitly uses `photons/H/unit_eta` or `erg/H/unit_eta`
and carries a separate quadrature weight. Its 45-value midpoint RHS is a
nonphoto stage: replay **requires** `photo_events_cm3_s == [0,0,0]` and
`photo_input_erg_cm3_s == 0`. Those zeros cannot be reinterpreted as observations
of a zero physical photo source. `Segment.rates` are checked as observed opacity;
they are not declared instantaneous per-absorber photoionization moments.

In an ideal continuous interpretation of integrated owners,

\[
A_i=\int_{s_0}^{s_1} a_i(s)\Gamma_i(s)\,\frac{ds}{H(s)},\qquad
B_i=\epsilon_{eV}\int_{s_0}^{s_1}a_i(s)\mathcal E_i(s)\,\frac{ds}{H(s)}.
\]

Consequently even `A_i/dt` is an interval-averaged rate **per H**, not Gamma_i.
With constant, positive `a_i`, constant H, and a separately justified constant
moment closure only, inversion would be `Gamma_i=H A_i/(a_i Delta s)` and
`Ecal_i=H B_i/(epsilon_eV a_i Delta s)`. Current records have affine gas and
piecewise radiative segments; this constancy is not supplied. If `a_i=0`, no
such inversion exists. Changing the time distribution or gas targets can keep
the same integrated owner and change any proposed instantaneous rate.

The A/B owners can support their own integrated-budget identities when their
owner semantics are established. They do not justify an instantaneous Tdot, a
global optical-depth enclosure, a temporal jump, or a continuous rate jet.

Required receiver gates before an actual record may enter the affine adapter:

1. Pin producer repo/commit/schema, accepted transaction/node/segment identity,
   and record hash; preserve accepted-vs-rejected-trial distinction.
2. Declare semantic kind: `instantaneous_per_absorber_moment_rates`; reject
   `integrated_absorption_owner`, `opacity`, and nonphoto placeholder fields.
3. Supply all six moments, generator IDs and common-spectrum/provider premises,
   with species order, proper-density normalization, incident-vs-excess energy,
   eV-to-erg conversion, physical clock and derivative clock explicitly typed.
4. Supply the identical fixed `(h,y,z,w,nH,nHe,H,kB,epsilon_eV,C_T)` context and
   evaluation time for center and every generator. A point state cannot stand
   for a time interval. Check `dt/dln a=1/H` under the producer's declared
   arithmetic/tolerance; do not silently force equality between rounded data.
5. Bind the exact `chi_ev` threshold tuple to the same FixedContext; reject threshold mismatch. Preserve one unique generator ID per ordered shared generator.
   Require exact input decoding policy, finite-domain checks and every vertex's
   necessary threshold/zero-rate conditions; reject missing premises instead
   of inventing generator magnitudes.
6. Keep the output labelled `conditional_fixed_state_photo_source`; never
   promote to total RHS, accepted step error, continuous history, or an atomic
   provider certificate without the missing evidence.

Current admission result: **REJECT / INTEGRATED_OWNERS_AND_NONPHOTO_RHS**, not a
failure of the accepted record's intended replay contract. The blocker is the
missing instantaneous joint-moment receiver payload and its error premises.

## 5. Counterexamples and exact toy vectors

`TOY_VECTORS.json` is an independent rational oracle computed directly from the
equations above, without importing R11 or the new adapter. Energy constants and
thresholds in these toys are deliberately rescaled synthetic values, not an
H/He atomic benchmark. All fractions are exact strings. Cases include:

- a three-generator family with cross-species and rate/energy correlations;
- monochromatic threshold photons with identically zero heat but negative
  temperature source from particle dilution; its decorrelated heat box admits
  spurious positive and negative heat;
- a zero-source limit with every photo readout exactly zero;
- a family whose positive Gamma vertices violate the excess-energy condition;
- a zero-Gamma positive-energy family that passes threshold inequalities but
  fails the additional necessary realizability condition.

Other explicit limitations: a Gamma-only enclosure cannot bound arbitrary heat
(`Ecal/Gamma` can increase without an upper spectral support premise); allowing
the gas state to depend on u destroys the fixed linear map; spectral quadrature
alternatives are not left/right temporal traces. These counterexamples forbid
promotion of this local affine receiver to a full state-error or history-error
propagator.
