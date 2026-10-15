# AX03 independent initial anisotropic stress, opt-in REI research intake

The code introduces an independently specified initial tensor stress pi^i_j=diag(-pi_s,-pi_s,2pi_s) in physical J/m3, alongside original source-locked q_ref=s_ref/H_FLRW,ref.

Input initial radiation angular phase-space distribution:
W(mu_ref) = 1+kappa P2(mu_ref), |kappa|<=0.5, W>=0.5, pi_s_ref/epsilon_rad_ref=kappa/15.

This is an actual **Einstein–massless collisionless Vlasov** extension with radiation energy conservation, not ad-hoc pi(t):
R²=e^(2b)(1-u²)+e^(-4b)u²,
M=<W R>, P=<W R P2(mu_late)>/3, dM/db=-6P.
H²=H0²[Omega_m/a³+OmegaLambda+Omega_r M/a⁴]+s²;
dot s+3Hs=3H0² Omega_r P/a⁴.
Kinetic quadrupole generates shear even for q_ref=0.

Rust native module axbi_stress_background.rs is EXPORTED but NOT CALLED by the existing AX03 native driver. It has its own new source q/kappa initial conditions and refuses unknown q or |kappa|>0.5; reference sqrt(H_FRW²+s²) and initial source cosmology remain unchanged. Existing rust axbi_background.rs, original source normalization and checkpoint data are not replaced.

**Inputs and scientific evidence:** evidence/TABLES/AXBI_INITIAL_STRESS_BACKGROUND.csv 10 cases x501 rows, SI pi_x/y/z J/m3 and H,s,b,t; evidence/TABLES/AXBI_INITIAL_STRESS_MANIFEST.json sources and SHA. Native Rust GL32 RK4 endpoint x10 parity to independent Python DOP853: max delta b1.4584e-14, max delta s/H2.1040e-14, max proper time rel7.5562e-13; 7/7 Rust tests PASS. New Python source18/18 tests PASS, mpmath75 12 angular double integral checks PASS, local Wolfram15/xTensor8 exact zeros. Hamiltonian relative equation residual max6.66e-16 on 5010 recorded rows. Parallel 2/4 workers slower than one, 10-case NumPy vector GL16 RK4-128 median about0.038s versus separately solved DOP853 ~.146s; no claim of native coupled chemical solver acceleration.

Separate original REI experimental C9 short-clock source remains in parent commit edddcd6ea9a135fcf18c7be8357b5e11fea87407, and 35 selected original/native tests passed with the new module exported. **No legacy/full chemistry history was restarted or altered.** The compiled source identity changes with the new lib.rs module, so previous source-bound AX08 checkpoints and source history are not automatically compatible with newly compiled binaries. Do not resume the old checkpoint with this physics.

New scientific lane still needs the actual CMB/reionization ionizing radiation collision operator and coupled anisotropic stress, a dedicated scenario/source identity and source-clock, AX11/12 error budgets and a fresh HII/HeII/HeIII/temperature evolution. Treat the present all-Omega_r collisionless model as a conditional explicitly labelled test, not physical inference from EoR data.
