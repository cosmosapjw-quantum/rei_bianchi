# BASS_HE -> rei_bianchi conditional ionization-error goal gate (2026-10-15)

Source: rei_bianchi isolated research commit d2c64e7dca1127200fa0758275b27320815d8291 (branch research/bass-he-optical-depth-transfer-20261015), file research/bass_he16_transfer_20261015/goal_error_budget.py and source-bound GOAL_ION_FRACTION_BUDGET.json.

## Conditional derived bound
With nH(t) and the proper-time clock fixed to their native cold model histories and with |δ x_HII(t)|, |δ x_HeII(t)|, |δ x_HeIII(t)| <= epsilon uniformly for each q-history:
|δE_tau(q)| <= (I_plus/2 + I_minus/2 + I_ZERO) (1+3 f_He) epsilon,
I_case = sigma_T c * int nH_case(t) dt, f_He = 1227/15092, nH in proper cm^-3, t in seconds with 1e6 unit conversion.

The ZERO original source prefix nH a^3 consistency was checked on all 200001 saved rows: maximum relative deviation 3.3306690738754696e-16.

For the q=.005 even tau response E=-2.76081465256e-8 at mean scale factor a=.08873654701704167, the conditional sensitivity coefficient is 0.2983152804358213742 and a sufficient uniform ionization-fraction absolute-error ceiling for <10% source-fraction contribution is 9.254687351351414e-9. At q=.01, the corresponding sufficient ceiling is 3.701786007074857e-8. For the common-proper-time residual component Et of q=.005, sufficient epsilon ceiling is 8.870205669004635e-10.

**Status:** Constructive conditional bound only. No native source-ODE global bound or independently certified error was produced; H(t), clock, non-equilibrium photo-source, photon numerics, interpolation and physical observability need their own error terms. These sufficient criteria are NOT necessary tolerances, and native local_target/last_error are not bounded |δx| unless proven separately.

Ubuntu end-to-end regressions: 33/33 PASS; this version includes direct tests of the conditional bound and matched t truncation. Do not replace warm HE18 16-cell certified source values with cold tau numerical values. Next minimal science gate: independent native convergence/tighter time stepping on q=0,±0.005 over the shared mean-a prefix, propagate into goal functional E and Et, and bound clock errors.