# B1 prescribed-history transport — execution contract

Date: 2026-10-12. Owner: root, host-declared GPT-6 Astra; research/coding harness v4.0.0.
Authority: user request “B1 연구 루프를 시행해줘”, following BASS_HE PR27 at
`c3e797e0998cececc7cb7d0a502fc4e66f33fafc`.

## Scope and success

Compute F/M/B/B0/B_F/M_F over mean-volume z20→4 using the existing frozen
REI RUN002 histories, prescribed radiation and cold elastic Thomson scattering.
Produce actual time/energy CSV, figures, convergence evidence and interpretation.
Primary q2=∫P2(mu)I/∫I; compare B−M and (B−M)−(B_F−M_F).
The history response may be unresolved; a claimed resolved response needs observed
paired numerical differences <=10% of its magnitude. Near-zero quantities get
absolute residuals, not relative acceptance or a forced detection.

Preserve original Q/closure/clock/cross sections. No reionization ODE rerun,
no R15 emissivity-to-spectrum inference, no atomic provider reimplementation,
no E13C11/NCP work. Backreaction, thermal redistribution, observer tail and
observational CMB multipoles are outside scope.

## Definitions and initial/source data

Metric (-,+,+,+). LRS a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt.
The common spectral coordinate is y=(a/a_i)E/(k_B T_i), **not** conserved
direction-dependent covariant momentum. At a fixed time, a y slice has the same
physical energy in all directions, as required by elastic Thomson scattering.
T_i remains an arbitrary positive benchmark scale within E << m_e c^2;
no observed CMB temperature is assigned. h=2*pi*hbar and c are not set to one.

Reuse bass `bianchi/q/modeb.py::planck_state(T_of=None)`:
initial trace of the screen coherency occupation is F=1/expm1(y), with
F_theta=F_phi=F/2, U=V=0. Subsequent emissivity is explicitly zero.
Dimensionless spectral intensity is y^3(F_theta+F_phi); physical I_E is
2 E^3/(h^3 c^2) times the coherency trace under this normalization.
This radiation is a test field; the producer's R15 source only determines Q.

At each target direction mu, the backward Liouville map over delta_b is
D=sqrt((1-mu^2)exp(-2 delta_b)+mu^2 exp(4 delta_b)),
mu_old=mu exp(2 delta_b)/D, y_old=y D. These are the existing diagonal
null-covector characteristics, specialized to the frozen LRS background.
The meridional (e_theta,e_phi) screen has zero screen rotation in this LRS model.
Transport F_theta/F_phi by pullback; do not multiply occupation by a solid-angle
Jacobian or an additional redshift factor. Use target solid-angle quadrature
when forming moments. Both interpolated diagonal occupations remain positive.

## Frozen histories and new projection

Source input acquisition/projection is recorded in source_notes and inputs.
The two original histories have the same 16384 fine ln(a/a_i) cells.
For FLRW history on the B clock, reuse the original cell integral with
depth_F_on_B=depth_F * H_F(mid)/H_B(mid). This preserves the original Q integral
and density-midpoint prescription. Apply the existing BASS/REI sigma_T ratio.
Use BASS sigma_T=6.6524587e-29 m^2, REI=6.6524587321e-29 m^2,
c=299792458 m/s. No extra a^-3, 1+z or Doppler factor is introduced.
Coarse collision depths are sums of original fine projected measures.
Time-splitting refinements examine the new ordering error, not the producer ODE.

## Explicit execution backend decision

The local host has no Rust compiler/prebuilt bass library. Compiler provisioning
failed before scientific execution; exact receipts are retained. Therefore the
current physics backend is explicitly `EXPLICIT_EXISTING_BASS_PYTHON`, calling
the unchanged upstream `polarization.py::collide` for every energy slice.
This is not an implicit fallback and is not counted as Rust execution.
The Rust C ABI and exact source are supplied but its build/integration remains
`BUILD_NOT_RUN/HOLD`. The PR27 requirement for actual Rust calls is not closed
by the Python result. Numerical scientific conclusions will be scoped to the
executed backend; no native parity or whole-B1 native promotion is claimed.

## Numerical method and affected validation

Second-order Liouville-half / exact collision-full / Liouville-half splitting,
using frozen b at actual half edges and integrated cell opacity. Gauss-Legendre
mu and 8 uniform azimuths. Axisymmetric diagonal screen representation is
expanded to the full Cartesian coherency tensor for every upstream collision.
Off-diagonal/azimuth deviations are measured before symmetry reduction.
Log-positive cubic interpolation in mu and log(y), with explicit polynomial
edge extrapolation; claims are restricted to the guarded y=0.1→10 window
inside log(y) domain [-8,5], reusing the explicit broad-domain choice in
upstream tests/test_q7b_modeb.py::_pair (line 35), not the planck_state default
domain [-6,4]. Refine time, angle and
frequency only to resolve remaining signal/numerical risks.

Check analytic B0 pullback and p_L=0; F/M/M_F q2=p_L=0; U=V=0;
collision intensity conservation, screen symmetry and positivity; actual
depth/call counters; independent collision oracle; paired refinement.
Record measured time/RSS. No stochastic seeds or statistical confidence claims.

Independent oracle/validation assistance is separate from the author.
A final decision reviewer who did not generate the candidate or design its
validation will decide any scoped promotion. No review-of-review recursion.
