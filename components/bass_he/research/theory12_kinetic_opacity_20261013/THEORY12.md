# THEORY12: kinetic scattering-out opacity and a global recoil envelope

Unit: `HERE_RUX03_KINETIC_SCATTERING_OPACITY_12`. Date: 2026-10-13.
Status: **derived / symbolically checked; independent scientific review pending**.

## 1. Scope and provenance

Parent THEORY11 is `a0a3ba4ecb17c779a713705a45ee3fa3a9638c94`; receiver PR114 is `a5c958c414dea41216b445c05f58df837f05cacb`. Both heads were read live. The parent FT03 CI3/RR3/DR2/photo, Case-A escape, common gas velocity, fixed-tetrad source, conservative reconstruction and passive Thomson diagnostic are unchanged.

This unit quantifies a separate physical cross-section approximation error. The additional diagnostic closure is classical isotropic Maxwell–Juttner electrons at the same number current and kinetic temperature. The parent total-gas EOS is not replaced. General moment results below also apply to positive nonthermal distributions with the required finite moments. Electron stress is electron-only, not the parent total gas stress.

We treat linear independent free-electron scattering-out with the unpolarized Klein–Nishina total cross section. Induced/degenerate factors, scattering-in, polarization/frequency redistribution and Compton feedback are separate collision-operator tasks. Photoabsorption stays a separate retained source process.

Use signature(-,+,+,+). Unit observer n and gas/electron velocities u,w satisfy n.n=u.u=w.w=-1; physical four-velocities contain c. A lab ray k=n+ell satisfies k.k=0,n.k=-1. Photon momentum is (E_lab/c)k, E_lab=hbar*omega. Define delta=-u.k=gamma(1-beta.ell), epsilon=E_lab/(m_e*c^2), eta=delta*epsilon and theta=k_B*T_e/(m_e*c^2). The rate chi is per lab time; length opacity is chi/c.

## 2. Exact current-only Thomson rate

Normalize a positive invariant electron measure dmu=F(p)d^3p/w^0 so that

    I1^a=integral w^a dmu=N_e^a/c,
    I2^ab=integral w^a*w^b dmu=T_e^ab/(m_e*c^2),
    I3^abc=integral w^a*w^b*w^c dmu.

With q=-w.k>0, the kinetic scattering-out rate is

    chi_KN=c*integral q*sigma_KN(epsilon*q) dmu.

For constant sigma_T this reduces exactly to

    chi_T=-sigma_T*k.N_e=c*sigma_T*n'_e*delta.

At fixed electron number current, a thermal velocity spread therefore produces no separate pure-temperature term in the Thomson total rate. This statement does not require isotropy. In the parent normalization D=gamma*n_H and n'_e=n_H*e_H,

    chi_T=kappa*e_H*(1-beta.ell), kappa=c*sigma_T*D.

This is a total event-rate statement; energy exchange and the redistributed spectrum are different moments.

## 3. A global single-electron Klein–Nishina bound

For photon energy x>=0 in the individual electron rest frame, let mu be the scattering cosine, A=1+mu^2 and y=x*(1-mu). The normalized total cross section is

    S(x)=(3/8)*integral_{-1}^1 f(A,y) dmu,
    f(A,y)=A/(1+y)^2+y^2/(1+y)^3.

This is exactly the usual unpolarized KN integrand r^3+r-(1-mu^2)r^2, r=(1+y)^-1. The identities

    R1=f-A*(1-2y)
      =y^2*[A*(3+2y)/(1+y)^2+1/(1+y)^3],

    (3A+1)*y^2-R1
      =y^3*[(4A+3)+(7A+3)*y+(3A+1)*y^2]/(1+y)^3,

    A-f=y*[2A+(3A-1)*y+A*y^2]/(1+y)^3

have nonnegative right sides for A>=1,y>=0. The angular integrals of A,2*(1-mu)*A,(1-mu)^2*(3A+1), multiplied by3/8, are1,2,26/5. Consequently

    0<S(x)<=1,
    0<=S(x)-1+2x<=(26/5)*x^2       for every x>=0.

The bound is global, so it can be integrated over an unbounded electron momentum distribution without truncating a high-energy thermal tail.

## 4. Covariant moment remainder

Multiply the global inequality by the positive measure c*sigma_T*q*dmu:

    chi_1=chi_T-2*c*sigma_T*epsilon*k_a*k_b*I2^ab,

    0<=chi_KN-chi_1
      <=(26/5)*c*sigma_T*epsilon^2*(-k_a*k_b*k_c*I3^abc).

The null-null electron stress projection is the first recoil correction. For the1+3 decomposition with electron energy flux q_e and anisotropic stress pi_e,

    k_a*k_b*T_e^ab
      =delta^2*(rho_e+p_e)-2*delta*(q_e.k)/c+pi_e^ab*k_a*k_b.

A positive counterexample to current-only recoil is two equal electron beams at velocities +/-3/5 along z. Their Thomson rate is isotropic, while the first recoil coefficient is17/10 parallel to the beams and5/4 perpendicular. No Maxwell–Juttner assumption is used in that discriminator.

## 5. Maxwell–Juttner moments

In the electron number frame use r=|p|/(m_e*c), gamma_e=sqrt(1+r^2), z=1/theta and radial partition Z(z)=K2(z)/z. Expectations here use the physical number weight F*d^3p, not dmu. Differentiating Z and using the vanishing boundary term in integral div_p[p*exp(-gamma_e/theta)] gives

    <gamma_e>=K1/K2+3theta,
    <1/gamma_e>=K1/K2,
    <gamma_e>-<1/gamma_e>=3theta.

With h_e=<gamma_e>+theta=K3/K2,

    <gamma_e^2>=1+3theta*h_e.

Let H^ab=g^ab+u^a*u^b. Isotropy then yields

    I2^ab=n'_e*(h_e*u^a*u^b+theta*g^ab),
    I3^abc=n'_e*[(1+3theta*h_e)*u^a*u^b*u^c
      +theta*h_e*(u^a*H^bc+u^b*H^ac+u^c*H^ab)].

Their traces give g_ab*I2^ab=-n'_e*(h_e-4theta), g_ab*I3^abc=-I1^c. Their null contractions are n'_e*h_e*delta^2 and -n'_e*(1+6theta*h_e)*delta^3. Thus

    0<=chi_KN/chi_T-(1-2eta*h_e)
      <=(26/5)*eta^2*(1+6theta*h_e).

## 6. Bessel-free enthalpy enclosure and adapter

The pressure identity can be written3theta=<(gamma_e-1)*(1+1/gamma_e)>. It implies1+5theta/2<=h_e<=1+4theta. Set d=h_e-1-5theta/2. The exact relation

    d=(1/2)*<(gamma_e-1)^2/gamma_e>>=0

and1/gamma_e<=1 give

    d <= (1/2)*<(gamma_e-1)^2>
      = -d+(3theta/2)*(h_e-1).

Therefore0<=d<=3theta^2. Define

    s_app=1-2eta*(1+5theta/2), chi_app=chi_T*s_app,
    h_U=1+5theta/2+3theta^2.

Then a global sufficient enclosure is

    -6eta*theta^2 <= chi_KN/chi_T-s_app
      <=(26/5)*eta^2*(1+6theta*h_U).

This requires neither a Bessel call nor a thermal momentum quadrature in the adapter. The positive practical branch is separately verified on the stated warm domain. The limit eta=0 is exactly the Thomson rate; the first temperature correction is -5eta*theta, not an isolated O(theta) rate term.

## 7. Angular structure at fixed lab energy

For an isotropic gas with mu=beta_hat.ell,

    chi_1/(kappa*e_H)=(1-beta*mu)-2epsilon*gamma*h_e*(1-beta*mu)^2.

Its Legendre coefficients are

    A0=1-2epsilon*gamma*h_e*(1+beta^2/3),
    A1=-beta+4epsilon*gamma*h_e*beta,
    A2=-(4/3)*epsilon*gamma*h_e*beta^2.

Use h_e=1+5theta/2 for the rational adapter. A recoil quadrupole is therefore retained even when the gas-frame electrons are isotropic. The original current-only monopole/dipole shortcut is preserved only for the original Thomson observable. The exact KN remainder may contain higher moments.

## 8. Quantitative warm-domain result

Use the specified CODATA2022 central model values m_e*c^2=510998.95069eV, sigma_T=6.6524587051e-25cm^2, exact c and k_B/eV=1380649/16021766340eV/K. Measured-constant uncertainty is separate.

For30000<=T_e<=110000K, theta lies between5.05911015111238e-6 and1.85500705540787e-5. The enthalpy lies between1.00001264777537778 and1.00004637620870055.

All table energies are gas-frame diagnostic energies, not untransformed source lab energies.

| E_gas/eV | Thomson relative deficit enclosure (outward display) | Adapter relative radius |
|---:|---:|---:|
|0.001|[3.91395e-9,3.91409e-9]|<1.992e-17|
|23|[9.00103e-5,9.00240e-5]|<1.054e-8|
|35|[1.36963e-4,1.36994e-4]|<2.440e-8|
|70|[2.73879e-4,2.73986e-4]|<9.760e-8|
|74|[2.89523e-4,2.89643e-4]|<1.091e-7|

For E_gas<=74eV and the entire warm interval, s_app>0.999. The maximum model-relative radius is1.09062413236167827e-7. With the inherited true-history Thomson upper bound1.18105818398108136e-8 over at most1e9s,

    |tau_KN-tau_app|<1.289e-15.

This is a same-history physical model remainder. It does not itself establish the numerical integration error of the new observable. Parent THEORY11's3.831e-14 certificate remains attached to the Thomson functional; a kinetic-adapter numerical calculation must account for its own primitive/temporal/quadrature errors.

For a74eV gas-frame ray over the full horizon, the Thomson recoil discrepancy lower bound exceeds70 times that parent numerical budget. For the illustrative0.001eV ray, the upper discrepancy is below1/700 of it. The sufficient all-history ceiling making the Thomson model error no larger than3.831e-14 is E_gas,max<=0.82872555436853729eV for these density/time bounds. These are conditional comparison statements, not computed source trajectories or a CMB spectrum.

A directly reusable interval transformation is: if tau_T in[L_T,U_T] and0<=dmin<=1-chi_KN/chi_T<=dmax<1 on the ray/history, then

    tau_KN in[(1-dmax)*L_T,(1-dmin)*U_T].

This keeps the existing Thomson certificate intact and adds a separate physical-model interval. If only an upper energy is known, dmin=0 is a safe choice.

## 9. Actual execution and remaining tasks

Four cloud Wolfram evaluator calls were made. The first microphysics batch returned18/19True because K18 used an unparenthesized replacement/equality expression. The second call repaired that exact residual without changing any equation or tolerance and added14 scientific domain checks. A literal True bookkeeping item was excluded from scientific totals. The oversized domain output was partially elided; the fourth call recovered the compact table and added two exact paired-beam checks and one direct scalar KN high-precision quadrature.

Actual xAct ran11 groups containing14zero tensor residuals. Wolfram15.0.1, xTensor1.3.0, pure-Wolfram xPerm backend. Archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Total distinct scientific check groups:47, including two explicitly numerical sanity checks. No independent reviewer, native chemistry, nonlinear source stage, actual optical depth or ODE trajectory was run.

Prior native provider/moments/moving-stage/certificate-adapter tasks and reviews08-12 remain open under their existing owners. Parent11's actual endpoint/residual application remains the next execution. This optional kinetic adapter is not a new mandatory theory gate. No production source or sharing permission is changed.

## Primary references

Poutanen & Vurm2010, ApJS189,286, DOI10.1088/0067-0049/189/2/286, https://arxiv.org/pdf/1006.2397 . Parsed primary Eq14/18/20/23 supports the invariant collision average and incidence factor.

Sarkar, Chluba & Lee2019, MNRAS490,3705-3726, DOI10.1093/mnras/stz2794, https://arxiv.org/pdf/1905.00868 . Eq4 and Eq33a support the MJ distribution and known low-energy coefficients. The coefficients are not claimed novel; the explicit moment and globally bounded adapter construction is supplied for the present program.

NIST CODATA2022 constants: https://physics.nist.gov/cuu/Constants/Table/allascii.txt . Runtime: https://xact.es/download.html . Two web PDF screenshot attempts failed; no rendered-page inspection is claimed. Equations were read in primary parsed text and independently derived/tested.

The full Korean proof, report, exact rational table, executed-result records and replay material are in the archived evidence linked from EVIDENCE_INDEX.json. Recorded online outputs are normalized transcriptions, not raw connector bytes.
