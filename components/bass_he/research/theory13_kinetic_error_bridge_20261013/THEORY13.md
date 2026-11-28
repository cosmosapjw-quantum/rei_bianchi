# THEORY13: finite-history kinetic optical-depth error bridge

Unit: `HERE_RUX03_KINETIC_OBSERVABLE_ERROR_BRIDGE_13`. Date: 2026-10-13.
Status: **derived and symbolically checked; independent scientific review pending**.

## 1. Question and retained model

THEORY12 supplied a same-history Klein–Nishina model remainder, while THEORY11 certified a Thomson functional. This unit constructs the missing numerical-error transfer for the new kinetic observable, retaining the old precise Thomson estimator rather than assigning its error bound to a different functional.

Parent12: `53cc1bfce3a9c0a386e1f9e10d516973c78dd499`; parent11: `a0a3ba4ecb17c779a713705a45ee3fa3a9638c94`; receiver PR114: `a5c958c414dea41216b445c05f58df837f05cacb`. PR38 and receiver heads were read live. Keep the full fixed-tetrad FT03 CI3/RR3/DR2/photo source, Case-A kinetic/binding escape, common gas velocity, D=gamma*n_H=10^-3 cm^-3, f=2/25 and the parent input family. Geometry, external births and CR/RCT/HH are zero in this selected source problem. Two exact BE steps satisfy h_j<=H=5e8 s and T<=1e9 s. Conservative gas coordinates and lab photon inventories are reconstructed linearly between the same endpoints.

The passive diagnostic assumes isotropic nondegenerate Maxwell–Jüttner electrons at the same density, velocity and temperature. It does not replace the total-gas EOS or add scattering-in, redistribution or feedback. Fix the lab diagnostic energy,0<=E_lab<=70eV, and a unit lab ray throughout the history. With gamma<=1.002 and1-beta.ell<=1.05, E_gas<=73.647eV<74eV.

Use metric(-,+,+,+), unit timelike n,u, physical four-velocity c*u, k=n+ell, k.k=0,n.k=-1. E_lab=hbar*omega, epsilon=E_lab/(m_e*c^2),theta=k_B*T_e/(m_e*c^2),kappa=c*sigma_T*D. Optical depth is dimensionless.

The inherited cube Q=[-1,1]^7 contains both true and reconstructed histories. On it:

    e=e_H in[139/250,141/250], Le=1/250,
    |beta|<1/20, gamma<=501/500,
    ||D_X beta||<=3e-6, ||D_X gamma||<=2e-7,
    ||D_X T_e||<=1400K, ||DeltaX_j||<=h_j*mX,
    mX=162307/10^14 s^-1,
    I_X=integral ||X-Xhat||dt <=136178669878425125/5721699348 s.

Q11^(16) denotes the parent's signed electron-residual-corrected Thomson estimator with16 midpoint panels per original stage. Its exact reference radius is3.83037199569464061905e-14. Its32 actual source samples are a retained execution requirement; they were not run here.

## 2. Separate and integrate the small recoil functional

Let H1=1+5theta/2 and b=1-beta.ell. The parent12 adapter is

    chi_app=chi_T-r_epsilon,
    chi_T=kappa*e*b,
    r_epsilon=2*kappa*epsilon*e*gamma*H1*b^2.

Define the rank2 kernel

    S^{ab}=H1*u^a*u^b/gamma
          =gamma*H1*(n^a+beta^a)*(n^b+beta^b).

Then g_ell=k_a*k_b*S^{ab}=gamma*H1*b^2. The electron-stress metric term proportional to theta*g^{ab} vanishes exactly in this null contraction; it is not discarded from a claimed full stress tensor.

Electron abundance is affine on each conservative segment. With endpoint weights

    w0=(2e0+e1)/6, w1=(e0+2e1)/6,

construct

    M_Q^{ab}=sum_j h_j*(w0*S0^{ab}+w1*S1^{ab}),
    Q_R=2*kappa*epsilon*k_a*k_b*M_Q^{ab},
    Q13=Q11^(16)-Q_R.

All weights are positive. This integrates affine e times the endpoint-linear interpolation of the entire kernel S. The true nonlinear primitive path is unchanged, and its difference is bounded below. Once the original three endpoint primitives are known, recoil needs no new source call or interior primitive evaluation.

For alpha_i=h*w_i*gamma_i*H1_i, accumulate A=sum alpha, B=sum alpha*beta, C=sum alpha*(beta outer beta). The angular kernel is A-2B.ell+C:ell*ell. Its STF form uses9 independent coefficients: A+trC/3, -2B and C_STF. Quadrupole and antipodal sum2(A+C:ell*ell) are retained. Different lab energies reuse the same moments through epsilon. Averaging beta before squaring drops the nonnegative weighted variance.

## 3. First-derivative temporal error

For fixed ray,

    dg=H1*b^2*d(gamma)+(5/2)*gamma*b^2*d(theta)
       -2*gamma*H1*b*ell.d(beta).

Set thetaU=k_B*110000K/(m_e*c^2), HU=1+5thetaU/2, gammaU=501/500,bU=21/20,Ltheta=(k_B/(m_e*c^2))*1400K. Uniform constants are

    GU=gammaU*HU*bU^2,
    Lg=(HU*Lgamma+(5/2)*gammaU*Ltheta)*bU^2
       +2*gammaU*HU*bU*Lbeta,
    Lr=2*kappa*epsilon*(Le*GU+emax*Lg).

They retain all temperature/velocity feedback in the primitive inverse. Therefore

    |integral r_epsilon(X)-integral r_epsilon(Xhat)|<=Lr*I_X.

Actual values: GU=1.10475623088922861, Lg=7.18543247293804559e-6, Le*GU+emax*Lg=0.00442307750747165149. At lab70eV the temporal radius is5.75200853296266184e-16.

## 4. Recoil quadrature with no Hessian

On one normalized segment g is K-Lipschitz with K=Lg*||DeltaX||. Let S=e0+e1,de=e1-e0,d=g1-g0. For K>0, r=d/K lies in[-1,1]. The compatible endpoint cones are min(g0+Ks,g1+K(1-s)) and max(g0-Ks,g1-K(1-s)). Integrating their products with affine positive e gives center and radius

    Ic=S*(g0+g1)/4+de*d*(3-r^2)/24,
    RI=S*K*(1-r^2)/8.

The endpoint rule IL=w0*g0+w1*g1 has Ic-IL=de*d*(1-r^2)/24. Thus

    |integral e*g-IL|<=K*(1-r^2)*(S/8+|de|*|r|/24)
                    <=K*(S/8+de^2/(288*S)).

The final inequality follows from
`a+b^2/(4a)-(1-t^2)(a+b*t)=a*(t-b/(2a))^2+b*t^3>=0` for a=S/8,b=|de|/24,t=|r|. K=0 is an exact constant-kernel branch. An inconsistent endpoint/bound enclosure must be resolved, not clipped. Direction-specific cone centers are certificates, not substituted global angular fields.

Summing over the two steps,

    E_R,quad<=2*kappa*epsilon*Lg*
       [emax*mX*H^2/2+Le^2*mX^3*H^4/(288*emin)].

At lab70eV this is4.49252289292838611e-18. Electron abundance is integrated exactly, which removes its large variation from the leading quadrature term.

## 5. Add the model remainder on the true history

Parent12 establishes, with eta=E_gas/(m_e*c^2),

    -6eta*theta^2 <=(chi_KN-chi_app)/chi_T
      <=(26/5)*eta^2*[1+6theta*(1+5theta/2+3theta^2)].

Use etaU=74eV/(m_e*c^2),thetaU above and tauT,U=kappa*emax*bU*2H. Let Mminus and Mplus be the corresponding positive magnitudes after multiplying by tauT,U. The exact total error identity is

    tau_KN-Q13=(tauT-Q11^(16))
      -(R[X]-R[Xhat])-(R[Xhat]-Q_R)+(tau_KN-tau_app).

Consequently, with Enum=E11+E_R,time+E_R,quad,

    Q13-Enum-Mminus <=tau_KN<=Q13+Enum+Mplus.

At the selected CODATA2022 central constants:

| term | exact rational displayed |
|---|---:|
| parent Thomson radius |3.83037199569464061905e-14|
| recoil temporal |5.75200853296266184003e-16|
| recoil quadrature |4.49252289292838611302e-18|
| Enum |3.88834133331356007606e-14|
| Mminus |3.53122496876690094959e-21|
| Mplus |1.28809055717302624392e-15|
| total negative radius |3.88834168643605695e-14|
| total positive radius |4.01715038903086270e-14|

An outward statement is `[Q13-3.889e-14,Q13+4.018e-14]`. This is a conditional estimator certificate, not an actual computed optical depth. Constant uncertainty and actual endpoint/evaluator errors are separate inputs. The table uses the conservative74eV gas cap; energy-specific73.647eV bounds are slightly tighter.

## 6. Positivity and finite evaluation errors

The parent bounds Q10>=kappa*T*emin*.95 and |R_e^(16)|/T<=a_e*H^2*(1+1/64), together with Q_R<=2*kappa*epsilon*emax*GU*T, imply

    Q13/(kappa*T)>=emin*.95
      -(1+41/841)*a_e*H^2*(1+1/64)-2epsilonU*emax*GU
      =0.52798303893414674...>0.527.

This holds for T>0; zero duration returns zero. Zero photon energy returns the original Thomson estimator.

For endpoint primitive uncertainties,

    delta_g<=HU*bU^2*delta_gamma+(5/2)*gammaU*bU^2*delta_theta
             +2*gammaU*HU*bU*delta_beta,
    delta_QR<=2*kappa*epsilon*sum_j h_j*
               [GU*delta_e+emax*delta_g]+roundoff.

For inexact BE roots use the actual source residual to update I_X and use actual segment increments in K. Do not add the same primal/source error twice. Keep Thomson residual, recoil temporal, recoil quadrature, model and evaluation contributions distinct. Nonthermal electrons require the parent12 general electron-moment contract rather than the MJ numbers.

## 7. Actual checks and provenance

Actual Wolfram evaluator calls:5. Four substantive calculations plus one compact exact-field recovery. Final distinct named groups:16 rational/algebraic,10 actual xAct,9 scalar/angular=35. The successful xAct run has13 zero tensor residuals. No independent reviewer, native source/BE/ODE run or actual32 electron residual samples was executed.

The first xAct run had two failures because squaring an unwrapped Einstein contraction produced duplicated dummy-index/Scalar expressions. Explicit scalar inner products and a separately indexed product check repaired the encoding; no physical equation or tolerance changed. Both versions and actual residuals are preserved.

A separate Fraction identity guard caught a manually copied long denominator with three extra zeros. Compact Wolfram capture resolved the transcription; eight selected exact fractions match the independent rational regeneration. Undefined-symbol warnings preceding fully numeric outputs are retained.

Runtime: Wolfram15.0.1, xTensor1.3.0, xPerm1.2.4, pure-Wolfram backend. Official archive SHA256 `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`; xTensor.m SHA256 `04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36`. Submitted code files were saved before calls with normalized LF; output records are selected normalized transcriptions, not raw connector transport bytes.

Primary context: Diethelm2014, arXiv1305.3465v4, positive quadrature definitions and regularity assumptions; Roumeliotis2002 DOI10.1007/978-94-017-2519-4_7, publisher abstract only; Sarkar–Chluba–Lee2019 arXiv1905.00868v2 Eq33a, previously attributed thermal coefficients. The required endpoint-cone inequality is proved above. One PDF screenshot failed; parsed primary text was available. Paper PDFs are not redistributed. Constants: https://physics.nist.gov/cuu/Constants/Table/allascii.txt . Actual runtime package: https://xact.es/download.html .

## 8. Next execution and retained obligations

Consume validated same-source Y0,Y1,Y2 and parent11's32 electron-event residual samples, recover the same endpoint primitives, accumulate the9 recoil angular coefficients and return Q11,Q_R,Q13 with their complete intervals. The recoil addition needs no new source call, nonlinear step or adjoint solve. Existing PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04, MOVING_GAS_STAGE_05, CERTIFICATE_ADAPTER_06, RUX and all-Bianchi/D2.3 obligations remain with their current owners. Independent reviews remain open. This optional bridge closes a theory-to-code error-transfer gap rather than adding a new mandatory theoretical gate.
