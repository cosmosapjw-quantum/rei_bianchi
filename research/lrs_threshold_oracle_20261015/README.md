# REI LRS threshold-characteristic oracle (2026-10-15)

**Scope:** An isolated research lane, not the v3/rux execution DAG, original
production solver, PR150 coupled cold H/He chemistry or live NCP program.
Source parent: 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

## Definitions and assumptions

Metric (-,+,+,+), with
ds^2=-c^2 dt^2+a^2 exp(-2b)(dx^2+dy^2)+a^2 exp(4b)dz^2.
To distinguish coordinates, call the evolution variable X=ln(a/a0);
b=(s/H)X, b(0)=0, constant signed s/H.
sigma^i_j=diag(-s,-s,2s) and
Sigma=sqrt(sigma_ab sigma^ab/2)/H=sqrt(3)|s|/H.
No tilt, scattering, source emission, perturbations or gas feedback.

Label an initial photon ray by energy E0 (eV), direction mu0 and
photon weight N0 in an initial comoving volume. Along its exact
collisionless Bianchi-I characteristic:

F=(1-mu0^2) exp(2b)+mu0^2 exp(-4b),
E=E0 exp(-X) sqrt(F),
mu=mu0 exp(-2b)/sqrt(F),
d ln E/dX=-1-(s/H)(3mu^2-1),
d mu/dX=-3(s/H)mu(1-mu^2).

Each *prescribed* absorbing species has a fixed comoving neutral stock
n_i=n_i0 exp(-3X), and a conditional, approximate power-law cross section
sigma_i(E)=sigma_i0(E_i/E)^3 Theta(E-E_i).
Inputs kappa_i0=c n_i0 sigma_i0/H0 >=0 are dimensionless, with
h(X)=H(X)/H0>0 prescribed.

The species' per-log-scale-factor hazard factorizes:
d tau_i/dX = kappa_i0 (E_i/E0)^3
              F(X)^(-3/2)/h(X) Theta(E-E_i).

This result *requires* density a^-3 and the E^-3 cross section.
Exact atomic H/He Verner fits and evolving ionization fractions
do not obey this factorization exactly. Photoelectric threshold energies
in eV here are illustrative species labels, not a complete atomic provider.

On each threshold-active interval [A,B], let
T_AB=int_A^B F^-3/2/h dX and eta_i=kappa_i0(E_i/E0)^3.
Then exact positive competing-risk absorbed counts are:
Delta A_i=N_A[-expm1(-sum(eta)*T_AB)] eta_i/sum(eta).

Independent continuous-budget reference integrals:
heat_i=int N kappa_i (E-E_i) dX >=0,
W=int N E [1+(s/H)(3mu^2-1)] dX >=0
(for -1/2<s/H<1, all angles).
Thus number and energy equations independently read:
N0=N_end+sum A_i,
N0 E0=N_end E_end+sum(E_i A_i+heat_i)+W.

The algorithm isolates threshold events via bisection; updates
counts by a positive exponential; computes heat and cosmological
work using nested 8-node Gauss-Legendre quadrature; and subdivides
large optical depths. The residual is measured instead of set to zero.

A collisionless initially isotropic angular distribution has
Pi/U=(P_parallel-P_transverse)/U=-8b/5+O(b^2).
This is a *linear-response* result, not a nonperturbative closure.
Numerical quadrature tracks the exact evolved mu, not a frozen-angle P2.

## Run

Run inside this directory:

    python3 -m pytest -q tests/test_lrs_threshold_oracle.py
    python3 run_reference.py

Results: evidence/test_results.txt and evidence/results.json.
Reproducing the experiment needs only CPython's standard library;
pytest is needed for its tests.

## Scientific limits and provenance

- Derived + Wolfram exact symbolic check: three characteristic/hazard
  identities (zero symbolic residuals).
- Numerically checked: FLRW closed expressions for absorbed number,
  absorbed energy and redshift work, signed-shear stress and
  finite positive photon/multispecies budgets.
- NOT_ATTEMPTED: real H/He cross sections, redshift-dependent
  chemistry, feedback, native Rust adapter, full cosmological EoR,
  dark energy dynamics, Bianchi classes II-IX, fitted observables.
- This is a reference comparator for source-native Bianchi photon
  kernels and PR150 threshold/cut-cell calculations, NOT a replacement
  for those implementations or an admission of physical EoR predictions.

Literature:
Gnedin & Abel, cosmological photon-conserving multi-frequency transfer,
https://arxiv.org/abs/astro-ph/0106278 .
Pawlik & Schaye, multi-frequency H/He thermal RT,
https://arxiv.org/abs/1008.1071 .


## Independently executed verification and angular resolution finding

Local CPython 3, pytest 9.1.1, NumPy 2.4.2, SciPy 1.17.0.
The 35 real pytest cases pass. An independent DOP853 solver integrating
the *unfactorized* n_i(X)*sigma_i(E(X)) rates achieved a maximum absolute
difference 7.105427357601002e-15 among eight count/heat/work outputs
versus the factorized characteristic oracle (specified test case).
The direct solver uses the same exactly calculated threshold event times
and a separate ODE RHS, so the check is an independent rate/integration
implementation, not independently inferred crossing positions.

Near the HeII terminal threshold (X_end=0.61), the n_mu=8 vs n_mu=128
HeII-absorption relative discrepancy is 2.861752487847175e-4
for s/H=+0.03, whereas at X_end=0.8 it is 6.37e-14.
Near-threshold angular resolution therefore matters despite excellent
per-ray energy and count ledgers. This is a *measured conditional
quadrature defect*, not a real-universe forecast or full-grid convergence
proof. The n_mu=128 comparison is the local reference, not an exact
continuum limit.

Additional original literature:
Fleury, Pitrou and Uzan, Phys Rev D 91, 043511 (2015),
https://doi.org/10.1103/PhysRevD.91.043511 .
Verner et al., Astrophys J 465, 487 (1996),
https://doi.org/10.1086/177435 . The true photoionization fits differ
from the E^-3 toy cross sections used for the exact factorization.
