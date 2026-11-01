# REI IGM | Original 26-event finite photon-source nonlinearity

Date 2026-11-01. Immutable parent PR #332, HEAD 2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a.
Original frozen Aug29 46080-node accepted source archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.
Accepted state SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.
Science scope: close only the exact finite nonlinear source-competition term required by the full 26-event first canonical interval, not the entire nonlinear difference map.

## Definitions, assumptions, physical ownership

At one original source-clock time and each of four photon groups g, let J_g >= 0 be original group current, E_g>=0 external subgrid sink, c_sg>=0 original source-owned H/He cross-section coefficient INCLUDING original H vs He denominators/YHe, and n_is>=0 original neutral atoms (HI, HeI, HeII) at node i. Shared three moments S_s=sum_i n_is; original D_g=E_g+sum_s c_sg S_s >0.
Node photoionization rate phi_isg=J_g c_sg n_is/D_g [events/s per node]. Photon conservation: sum_is phi_isg + J_g E_g/D_g = J_g.
Original source photoheat = sum_isg phi_isg * original excess_energy_sg[eV] * 1.602176634e-12 erg/eV. This is NOT full chemical+radiative+escape+expansion energy closure.

Compare original initial material re-evaluated at accepted tick160 photon clock and a nuclei-conserving representative of actual accepted tick160 marginal state, keeping SAME J,E,c and clock. It is a same-clock material counterfactual, NOT the actual time-integrated trajectory.

## Exact finite identity, algebraically derived (Wolfram verified)

Set n1=n0+delta_n, D1=D0+delta_D where delta_D_g=sum_s c_sg sum_i delta_n_is.
Then
  delta_phi_isg = (J_g c_sg /D1_g) * (delta_n_is - n0_is delta_D_g/D0_g).
Define local first-order differential
  L_isg=(J_g c_sg/D0_g)*(delta_n_is-n0_is delta_D_g/D0_g).
The EXACT finite nonlinear remainder is
  R_isg= -(delta_D_g /D1_g) L_isg,
  delta_phi_isg=L_isg+R_isg.
For group absorption share p_sg=c_sg S_s/D_g, replace J_g c_sg n_is by c_sg S_s:
  L_p=(c_sg delta_S_s-p_sg0 delta_D_g)/D0_g,
  R_p=-(delta_D_g/D1_g)L_p.
The external group fraction changes with the same denominator. Together they conserve group photon current exactly. Wolfram exact rational residuals were {0,0,0} for global share and 0 for single-node quotient. Source energy linear/remainder use the SAME original photoelectron excess-energy weights, not an invented UVB rate.

## Analytic all-X bound restricted to the photon source and fixed forcing

For original accepted parent marginal neutral box [lo_is,hi_is], S1_low=sum_i lo_is and S1_high=sum_i hi_is; D1_min=E+sum_s c_s S1_s_low >0.
Define M_g=max(abs(D1_min-D0),abs(D1_max-D0)); m_is=max(abs(lo_is-n0_is),abs(hi_is-n0_is)).
Then every state in that entire rectangular population set satisfies
  |R_isg| <= (J_g c_sg/D0_g)*(M_g/D1_min)*(m_is+n0_is M_g/D0_g).
For the global group share similarly
  |R_p_sg| <= (M_g/(D1_min D0_g))*(c_sg m_s+p_sg0 M_g),
where m_s=max(abs(S1_low_s-S0_s),abs(S1_high_s-S0_s)).
All-X here describes the complete independent population rectangle at fixed J,E,c and one source evaluation site. The true reachable set may be narrower. The formula is analytically valid, but the implemented IEEE float bound (longdouble accumulated moments) is NUMERICALLY_CHECKED, not an outward-directed arbitrary-platform rigorous numerical certificate.

## Connection to remaining original central first-interval blocker

The original whole-parent full-vs-two-half logT upper at tick [160,161] is 2.1245050576368385e-4 > the UNCHANGED strict 2e-4. This source component is essential but not sufficient to evaluate joint D_h(X,Theta)=F_h(X,Theta)-G2(G1(X,Theta),Theta).
For an implicit population stage A(Y,Theta) Z=b(Y,Theta), its tangent solves A delta_Z=delta_b-delta_A Z. A thermal implicit root r(logT,Y,Theta)=0 has delta_logT=-(r_logT)^-1(delta_r_external). With correlated shared Y,Theta,
  J_D_Y = J_F_Y - J_G2_Y J_G1_Y
  J_D_Theta = J_F_Theta - J_G2_Theta - J_G2_Y J_G1_Theta.
Source nonlocal Jacobian has three shared neutral sums AT EACH SOURCE EVALUATION, not a global rank-3 theorem for the full multistage D_h. Four source evaluation sites, OTS event/branch, implicit thermal/matter maps and interval remainder must still be constructed. No tick161 acceptance or canonical promotion follows from this source identity.

## Primary literature (context, not code validation)

Neher, Jackson and Nedialkov (2007), On Taylor Model Based Integration of ODEs, SIAM Journal on Numerical Analysis 45:236-262, DOI 10.1137/050638448, explains dependency/wrapping and verified Taylor models. Pawlik & Schaye (2011), Multifrequence thermally coupled radiative transfer with TRAPHIC, DOI 10.1111/j.1365-2966.2010.18032.x, contextual photon conserving H/He astrophysics. Actual code authority is original frozen REI PR332 PR321 PR320 lineage.

## Same-author adversarial scope restrictions

1. Midpoint-selected forcing J,E,c may lie in original forcing boxes; bounds computed here are CONDITIONAL on that fixed forcing choice, NOT the whole original forcing uncertainty.
2. Real accepted-state representative is within original marginal physical box, not proven a single coherent source realization.
3. Analytic second-order R is EXACT for the one-group quotient; its enclosure is NOT the whole 26-event MPRK/SDIRK2 time-map remainder.
4. Original first interval stays BLOCKED_MINIMUM_STEP. No unapproved IVP, production chemistry, merge, force push, tolerance relaxation or budget reset.
5. Reported DAG: Central 28/88, Working 33/88, Physical Fast 4/7, canonical delta 0. Distinct-author blind referee and native subagents NOT_RUN.
