# Constructive bounds for the angular, geometry and coupling blockers

Evidence: derived from the E1 conditional angular law in DERIVATION.md and the
already measured PR233 primary kinetic-power moment. No new scientific execution.

## A finite-moment input for signed geometry transport

Assume the unpolarized E1 heavy-ion model of DERIVATION.md and a positive event
measure. Let K = integral E dW be its kinetic-power density and, for K>0, define
M = integral E kk dW / K. Then M is positive semidefinite, tr(M)=1, and

    dot(pi) = -(2 K/5)(M-I/3).

This expresses the entire admissible stress set at the given energy moment.
For each eigenvalue 0<=m_i<=1, the stress eigenvalues lie in
[-4K/15, 2K/15], sum to zero, and

    ||dot(pi)||_F <= (2/5) sqrt(2/3) K.

Proof: tr(M^2)<=tr(M)^2=1, so ||M-I/3||_F^2=tr(M^2)-1/3<=2/3.
Equality is attained by a collimated photon direction. An isotropic direction
mixture gives M=I/3 and zero STF source. For K=0 the positive measure gives zero
stress directly, without dividing by K. The trace of the full kinetic stress
source remains 2K.

The previously computed finite-source total is
K=1.4625823043267652e-36 J m^-3 s^-1. Consequently the displayed coefficient
times this actual K is a rigorous angular-ambiguity radius within the stated
finite E1 model. It is not a measured astrophysical uncertainty or a certificate
for the continuum photon quadrature, nondipole terms, or finite recoil.

For two directional event measures with energy-weighted total variation
eta_E = integral E |dW_1-dW_2|,

    ||Delta dot(pi)||_F <= (2/5) sqrt(2/3) eta_E.

The inequality follows by integrating the pointwise tensor norm. It provides a
specific finite-moment input-error map for B3g. It does not require replacing an
unknown angular distribution by an arbitrary isotropic distribution. A chosen
isotropic approximation can instead carry this nonzero conditional radius.

For polarized photon inputs replace the bound by
(4/5)sqrt(2/3)K, since a PSD trace-one coherency matrix obeys the same eigenvalue
bound. Use the sharper unpolarized result only under that explicit source model.

## Geometry response with an explicit unresolved propagator

For a linearized declared background response dot(z)=A(t)z+B(t)dot(pi)(t),
variation of constants gives

    Delta z(t) = Phi(t,t0)Delta z(t0)
      + integral_[t0,t] Phi(t,s)B(s)Delta dot(pi)(s) ds.

If the named BASS propagator and source histories supply bounds g(t,s) on
||Phi(t,s)B(s)|| in the declared physical norm, the source contribution is bounded
by integral g(t,s) r_pi(s) ds. Here r_pi is the explicitly derived angular radius;
the time-history and propagator bounds are still required. Neither endpoint
agreement nor a geometric constraint residual supplies g. This separates a now
available source-to-stress bound from the still-missing BASS transport certificate.

No BASS trajectory, production restart, or full feedback node is closed by this
component bound. Signed sector stresses must be added before taking a norm.

## Native binding-energy mismatch in secondary coupling

The NIST BED provider uses B_native=13.6057eV, whereas the inherited H1 photon
event ledger uses chi=13.6eV. Native BED outputs obey

    E_in = B_native + E_primary_out + E_secondary.

If a consumer instead books only chi for the same event, its ledger deficit is
deltaB=B_native-chi=0.0057eV per event. For an actual event-count source R_CI,
the mismatch power is deltaB*(1.602176634e-19 J/eV)*R_CI. For a finite integrated
count N_CI, its cumulative magnitude is |deltaB|*(1.602176634e-19)*N_CI.

This quantity diagnoses model/source convention error. It is not a new physical
thermal reservoir. The present native BED wrapper must reject mismatched binding
inputs; adopting a common energy convention requires a separately explicit model
change and its affected PI/RR/state-energy updates. No hidden offset or heat
assignment is introduced. Warm-bath energy diffusion also prevents using initial
primary energy alone as a universal bound on the number of later CI events.

## Three axes and remaining gates

- Symmetry/gauge: stress is a tetrad tensor; Frobenius norm is rotation invariant.
  Per-reference and per-volume conversions remain the previously frozen ones.
- Invariants: PSD moment cone, trace2K, signed STF sum and per-event native energy.
- Observables: a geometry/shear error or temperature change needs the actual
  time-dependent propagator and admissible reservoir dynamics. Current results
  supply constructive component inputs and identify exact missing coefficients.

The CDF continuum error, full angular/recoil source, actual geometry propagator,
and live coupled history remain open. The existing 88-node denominator is kept;
these component lemmas add no whole-node completion by themselves.
