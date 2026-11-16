# Radiation-stress consumer: definitions, equations and claim map

## 1. Fixed model and frames

Use the actual original proper-time histories with

    ds² = -c² dt² + a² e^(-2b)(dx²+dy²) + a² e^(4b) dz²,
    s = db/dt,   H² = H_F²+s²,
    H_F² = H0² (Omega_r a^-4 + Omega_m a^-3 + Omega_Lambda).

The orthonormal shear is diag(-s,-s,2s), sigma²=3s². For an axisymmetric
radiation field, DeltaP=P_parallel-P_perp has units J/m³. Its stress tensor
has traceless part diag(-DeltaP/3,-DeltaP/3,2DeltaP/3). Holding the originally prescribed H fixed, the trace-free Einstein equation
gives the forced-background diagnostic

    d(delta_s)/dt + 3H delta_s = (8 pi G / (3 c²)) DeltaP,
    delta_s(t_i)=0.

The coefficient has units m/kg and the right-hand side has units s^-2.
Here delta_s is a sourced first-order diagnostic on the original geometry.
Radiation and gas are not re-evolved on this corrected geometry. A fully
linearized coupled system would also contain 3 s delta_H in the shear equation
and the response of the radiation moments to delta_b. These terms are not
solved here. The subsequent algebraic delta_H calculation must therefore be
read as the first forced-background estimate, not a closed linear-response
solution or a rigorous feedback-error bound.

## 2. Two distinct radiation sources, with one owner each

The saved column `J2_photon_u_eV_per_H` is U2, already angle integrated:

    U2 = (1/nH) integral E J_2(E) dE,
    DeltaP_ion = nH_proper * U2 * epsilon_eV.

Convert nH from cm^-3 to m^-3 by 10^6 and epsilon_eV to
1.602176634e-19 J/eV. No extra 4 pi, angular weight, or a^-3 is applied.
These are actual saved primary-ionizing photons. Case-A recombination escape
has a separate owner and is not silently added as an isotropic or OTS source.

For the locked effective radiation fluid initially isotropic at b=0, conservation
of phase-space occupation along BASS/Bianchi-I photon characteristics gives,
in the **current local direction** mu,

    D²(mu,b)=e^(-2b)(1-mu²)+e^(4b)mu²,
    J_l(b)=(1/2) integral_-1^1 P_l(mu) D(mu,b)^(-4) dmu,
    epsilon_r(a,b)=epsilon_r0 a^-4 J_0(b),
    DeltaP_r(a,b)=epsilon_r0 a^-4 J_2(b),
    epsilon_r0 = 3 H0² c² Omega_r / (8 pi G).

The equivalent **initial-direction** representation follows from constant
covariant momenta:

    R(mu_i,b)=sqrt[e^(2b)(1-mu_i²)+e^(-4b)mu_i²],
    mu_local=mu_i e^(-2b)/R,
    J_l=(1/2) integral R(mu_i,b) P_l(mu_local) dmu_i.

This is the independent angular audit. It includes the angular Jacobian through
the change of variables and does not multiply a second angular measure.
The characteristic identity is literature-supported by Fleury, Pitrou & Uzan,
Phys. Rev. D 91, 043511 (2015), arXiv:1410.8473, Sec. IV, and directly derived
from g^(ij) p_i p_j. The identical metric follows the original AXBI contract.

The expansions independently checked with Wolfram are

    J0 = 1 + (8/5)b² - (16/21)b³ + (8/35)b⁴ + O(b⁵),
    J2 = -(8/5)b + (8/7)b² - (16/35)b³ - (40/231)b⁴ + O(b⁵).

In particular the stress opposes the sign of s for small b of the same sign.
Tr(sigma³)=6s³ permits scalar odd higher-order terms; exact +/- scalar parity
does not follow from axisymmetry. The numerical comparison uses actual signs.

## 3. Two independent time-integral forms

On the represented original history,

    delta_s(t) = [8 pi G/(3c²)] a(t)^(-3)
                 integral_ti^t a(t')³ [DeltaP_r+DeltaP_ion](t') dt'.

Let u=ln a, nH0=nH a³ and keep proper seconds. The same integral is

    delta_s_r(a) = H0² Omega_r a^-3 integral_ui^u J2(b)/(a H) du,
    delta_s_ion(a) = [8 pi G/(3c²)] nH0 epsilon_eV a^-3
                    integral_ui^u U2/H du.

The first implementation uses SI pressures and native-time trapezoids. The
audit uses these dimensionless-background expressions and ln(a) Simpson
quadrature. Differences assess postprocessing quadrature and clock consistency;
they are not errors of the original coupled evolution.

## 4. Consequences for the fixed-density clock

At fixed a and unchanged matter/radiation monopole densities, vary the shear term:

    delta_H_shear/H = (s/H)(delta_s/H),
    delta_t_shear(a) = -integral_ti^t (delta_H_shear/H) dt'.

This isolates the shear response to anisotropic stress. For completeness also
report the separate algebraic expansion diagnostic of the omitted radiation
monopole energy and extra gas/ionizing energy:

    Delta epsilon_r = epsilon_r0 a^-4 (J0-1),
    epsilon_extra = Delta epsilon_r + epsilon_ion + epsilon_gas,
    epsilon_ion = nH U0 epsilon_eV,
    epsilon_gas = (3/2) k_B T (nH+nHe+ne),
    epsilon_background = 3 c² H_F²/(8 pi G),
    delta_H_energy/H = (4 pi G/(3 c² H²)) epsilon_extra.

The locked original criterion uses epsilon_extra/epsilon_background < 1e-4.
Ionizing and gas energy are included exactly as its approximation diagnostic;
this is not a fully closed, double-count-free Friedmann re-solution of stellar
source and baryon rest-energy depletion. The shear-only and energy terms must
not be conflated or promoted to a coupled abundance correction.

For the gas term, electrons contribute thermal particles but not baryon nuclei.
Use nHe/nH=0.2454/[4(1-0.2454)] and verify ne from actual ionic fractions.
Chemical binding energy is not gas thermal energy.

## 5. Acceptance and uncertainty

| Claim | Required evidence | Status before execution |
|---|---|---|
| Four original histories and moment conventions are consumed | full SHA-256, native rows, charge, units and ordering | pending check |
| Radiation moment and shear diagnostic equations | characteristic mapping, Einstein difference equation, two integration forms | derived |
| Omitted-stress and energy diagnostics satisfy original 1e-4 ceilings | extrema over every saved row, separate terms, checked quadrature | unresolved |
| First-order expansion-clock effect | full saved-history integral with explicit boundary and scope | unresolved |
| Coupled abundance is accurate or insensitive to feedback | changed-geometry gas/radiation trajectory and AX11 controls | unresolved; not supplied by this postprocessor |
| Complete signed family/source robustness | +0.01 history, two refinement levels, source/IC variants | unresolved AX08/AX11/AX12 |

No general impossibility/no-go result is being admitted; NG1–NG7 are therefore
not applicable to a new no-go claim. Numerical ceilings are kept exactly as
originally declared. A result below a numerical floor is not a detected sign.
