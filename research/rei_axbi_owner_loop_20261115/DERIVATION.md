# R5 — characteristic, clock and electron consumer derivation

The clock equations and exact coordinate decomposition are in
`CLAIMS_AND_NUMERICS.md`. They follow directly from the original frozen
metric/background; no source fit is re-estimated here.

For a photon emitted with local direction cosine mu_e at (a_e,b_e), the
spatial covariant momenta are constants along a Bianchi-I null geodesic.
The tetrad energy obeys E^2=c^2 sum_i p_i^2/a_i^2. Therefore

    E/E_e = (a_e/a) sqrt[exp(2 Delta b)(1-mu_e^2)
                         + exp(-4 Delta b) mu_e^2],
    mu(a) = mu_e exp(-2 Delta b)/sqrt[...].

Here a_1=a_2=a exp(-b), a_3=a exp(2b); E_e is a physical energy,
not a comoving spectral label. The isotropic limit is E/E_e=a_e/a.
Differentiating gives d ln E/dt=-H+s(1-3mu(a)^2). The angular map has
Jacobian dOmega/dOmega_e=(a_e/a)^3/(E/E_e)^3. These relations underlie
the admitted BASS characteristic result and are derived here for the
original variable-H high-z geometry. See Fleury, Pitrou & Uzan,
[arXiv:1410.8473](https://arxiv.org/abs/1410.8473).

An initially isotropic unit photon distribution has

    (1/2) integral_{-1}^1 sqrt[exp(2b)(1-mu^2)+exp(-4b)mu^2] dmu
        = 1 + (8/5)b^2 - (16/21)b^3 + O(b^4).

Thus a scalar first-order response is absent for this particular isotropic
test distribution, while a cubic odd term is allowed. This is not a
prediction of the coupled ionization response. It demonstrates why an
exact even-in-shear assumption would be unjustified. The original source
uses positive Gauss-Legendre angular weights, which integrate the relevant
isotropic low moments exactly; REC's positive midpoint-grid correction
is tied to its own grid and must not be blindly transplanted.

For cold Thomson scattering on comoving, non-tilted electrons, the proper
collision rate is Gamma_T(t)=c sigma_T n_e(t), with dimensions s^-1. The
restored history supplies n_e in cm^-3 and t in seconds. The H/He identity
n_e=n_H x_HII+n_He(x_HeII+2x_HeIII) fixes the electron normalization. REC's
pinned values are c=29979245800 cm/s and sigma_T=6.6524587051e-25 cm^2.

On each consecutive native interval use the explicitly declared linear
n_e(t) representation. Then its optical-depth increment is exactly
Delta tau_j=c sigma_T (n_e,j+n_e,j+1) Delta t_j/2 for that representation.
The conditional receiver is the end of the supplied history, zbar=4:

    tau(t,4) = integral_t^{t4} Gamma_T(t') dt',
    g_cond(t) = Gamma_T(t) exp[-tau(t,4)],
    P_j = exp[-tau(t_{j+1},4)] [-expm1(-Delta tau_j)].

Summing P_j telescopes to 1-exp[-tau(t20,4)] and is nonnegative. At fixed
time boundaries this optical depth is direction-independent in the stated
non-tilted homogeneous model. Directional redshift surfaces or tilted gas
would change the mapping and are not supplied here. The tail from zbar4
to an observer at z=0 is unknown, not zero. This output is not the Planck
total optical depth or a full sky calculation.

The underlying source remains the pre-existing conditional model based
on the MD14 fit ([arXiv:1403.0007](https://arxiv.org/abs/1403.0007)) and
Plancklike parameters ([arXiv:1807.06209](https://arxiv.org/abs/1807.06209)).
The z>8 source extrapolation and homogeneous closure remain model
assumptions. No new empirical emissivity data are introduced by this loop.
