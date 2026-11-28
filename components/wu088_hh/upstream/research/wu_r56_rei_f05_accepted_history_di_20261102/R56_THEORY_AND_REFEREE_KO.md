# WU R56 | Original REI F05: source-accepted H/He history and D memory from tick0 to161

2026-11-02. Science owner: cosmosapjw-quantum/WU088_HH. Research scope: original-source **H/He history** [0,64,128,160] drives an explicitly conditional D microphysics 46,080-cell simulation. REI original 26-event HHe owner, native photon/OTS/thermal and tick161 official admission are untouched.

## Primary sources and exact identity

WU parent Draft PR195 HEAD \`20a68553c15e89a2178e5f2ad0caaff5c889aba0\`. Original REI owner PR365 HEAD \`fab9429140038974a98f3ad3212036b0227e600e\` and immutable original 26-event source TAR \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\` used indirectly. REC PR195 HEAD \`0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235\`; original 184,320 H/He cell-tick rows SHA256 \`6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c\`. Three original REIADP1 state files confirmed exact immutable SHA256: tick64 \`aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425\`, tick128 \`bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6\`, tick160 \`74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6\`. Original tick0 material NPZ SHA256 \`7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d\`. Original native photon/temperature forcing 17 nodes SHA256 \`9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268\`. Original source Savin Table1 47-pair reaction data SHA256 \`ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8\`.

Scientific original literature: Savin (2002), *ApJ* 566, 599–603, DOI https://doi.org/10.1086/324218, for D(1s)+H+ ⇄ D+ +H(1s) charge exchange. Galli & Palla (2002), DOI https://doi.org/10.1016/S0032-0633(02)00083-1 for primordial deuterium astrochemistry context. The original source's HI-derived DI photo/RR/EII model is explicitly an approximation, not a new ab-initio DI quantum cross section.

## Derivation

Metric (-,+,+,+), physical proper time t in seconds; photon numbers native photons/cMpc³, original \(\eta_D=2.5\times10^{-5}\) only hypothetical. Four original energy groups: G1 13.60–24.59 eV, G2a 24.59–39.50, G2b 39.50–54.42, G3 54.42–100 (G3 original photon population identically zero). Source \(x_{\rm H^+}(t)\), \(n_e^0(t)\), \(T(t)\) are original accepted H/He interval *midpoints at ticks 0,64,128,160*; between accepted times piecewise-linear \(x,n_e\) and logarithmic \(T\), NOT a certified continuous native owner history. 160→161 endpoint uses explicitly unapproved preview. Original 17 knot photon field is PCHIP-interpolated, with native original \(\Gamma_{\rm HI}(t)\), group \(N_g^0(t),A_g^0(t)\), and original HI-group photo-energy weights. Proper first tick \(\Delta t=4871848749.16828\,\mathrm{s}\).

The per-cell evolving D+ fraction \(y\) and accumulated net CX events \(C\), cumulative photo-events \(P_g\), electron-impact ionizations \(I\), and recombinations \(R\) obey
\[
\dot y =
k_f n_H(x_H-\eta_D C)(1-y)-k_r n_H[1-x_H+\eta_D C]y
+\sum_g\Gamma_g(1-y)
+\beta_{\rm HI}(T)[n_e^0+\eta_D n_H(y-C)](1-y)
-\alpha_B(T)[n_e^0+\eta_D n_H(y-C)]y,
\]
\[
\dot C=k_f n_H(x_H-\eta_DC)(1-y)-k_r n_H[1-x_H+\eta_D C]y,\quad
\dot P_g=\Gamma_g(1-y), \quad
\dot I=\beta_{\rm HI}n_e^{\rm eff}(1-y),\quad
\dot R=\alpha_Bn_e^{\rm eff}y,
\]
with exact isotope ledger \(y-y_0=C+\sum_g P_g+I-R\) and electron creation since initial state \(\eta_D(\sum P_g+I-R)=\eta_D(y-y_0-C)\). Source group photo rates use original HI Verner gamma weights, \(\Gamma_g=\Gamma^0_{\rm HI}\,w_g(1-D_g/N_g^0)\), \(w_g=\sigma^0_{\rm HI,g}N_g^0/\sum_h\sigma^0_{\rm HI,h}N_h^0\). Four-group deficit/displaced absorption \(D_g,B_g\) evolve
\[
\dot D_g=\eta_D\sum_jN_{{\rm H},j}\dot P_{g,j}-(A_g^0/N_g^0)D_g,\qquad \dot B_g=(A_g^0/N_g^0)D_g,
\]
so \(\eta_D\sum_jN_{{\rm H},j}P_{g,j}=D_g+B_g\) from zero initial deficits. Original H/He owner and its optical opacity are frozen. This is not full photon current/energy repartition or new native accepted REI trajectory.

D initial states at **tick0**, not tick160: ALL_NEUTRAL \(y_0=0\), H_MATCHED \(y_0=x_{\rm HII}(0)\), CX_EQ \(y_0=k_fx_0/(k_fx_0+k_r(1-x_0))\), ALL_IONIZED \(y_0=1\). No initial state is claimed historically true; all are explicit cases in an unresolved initial-data family.

## Actually computed original-source physical results

- Four scenarios × 46,080 original physical material cells; accepted-source 4-point history 0→64→128→160, plus unaccepted preview 160→161; cumulative \(C,I,R,P_g,D_g,B_g\) persist through the whole interval, unlike treating tick160 as a fresh start.
- Tick160 D+ fraction medians: ALL_NEUTRAL **0.492280093009123**; H_MATCHED **0.9999498027039342**; CX_EQ **0.9999495655067969**; ALL_IONIZED **0.999971650926081**.
- Gross DI photoevents generated **only between native ticks 160→161** (photons/cMpc³): ALL_NEUTRAL \`6.18945928493661e58\` (1.953302628% of source first-tick emitted photons); H_MATCHED \`1.84403722739384e55\` (0.00058195112%); CX_EQ \`1.8453782643255828e55\`; ALL_IONIZED \`1.4776658885056147e55\`. Thus 0-start vs H-matched first-tick absorption differs by factor ~3356; the historical D initial state is materially unresolved.
- Candidate **gross** DI photoelectron energy / original |\(\Delta U_{\rm F05}\)| median ALL_NEUTRAL \`0.03552909580653901\`, >1% in **27024/46080** cells; H_MATCHED median \`5.431652586692549e-6\`, >1% in **0/46080** cells. These are *not* added net heat; source H/He/OTS displacement and latent/escape bookkeeping remain coupled owner tasks.
- Original group photon deficit fraction at tick161 max ALL_NEUTRAL \`7.716965033631982e-5\`, H_MATCHED \`1.2969849940615163e-8\`; G3 source exactly zero.
- H_MATCHED source-time donor LEFT_HOLD sensitivity first-tick photoevents \`1.7597085135239327e55\` versus LINEAR \`1.84403722739384e55\`, a 4.6% point difference. **This is neither a rigorous continuous-path error bar nor an acceptance criterion**, but it exposes the missing native H/He continuous stage history.
- RK 2 vs 4 substeps/tick H_MATCHED y160 max absolute difference \`1.63202784619898e-14\`; not the primary scientific uncertainty.
- Full archived model 46,080-row CSV SHA256 \`fd23177e302892373a6adba5ad5417c964c8f54535ea02967efbf3593cc13692\`. Independent standard library all-row 46k gross photon recount maximum relative error \`5.404529904446817e-16\`, original Savin CX source reconstruction \(2.22\times10^{-16}\), all four 46k per-cell histories positive. Separate scalar DOP853 diagnostic (12 real source cells) with original photon deficit *ignored* differs from coupled RK4 historic D+ by max \`6.3052834890497955e-6\` for neutral, \`1.5260015473472777e-11\` for H_MATCHED: different physical approximation, same author, not an exact independent code replication.

## Adversarial judgment and drift watchdog

The previous R55 assumption of instantaneous D steady state at tick160 is not a uniquely established original physical state. R56 specifically identifies history-induced D memory as a physical input dependency, not an argument to build more isotope rate atlases. The large >3-order-of-magnitude first-tick gross absorption variation under original accepted H/He backgrounds demonstrates scientific uncertainty from unconstrained D initial conditions. Original OTS/thermal/energy source channels cannot be interpreted as net heat, and valid ODE numerical convergence does not eliminate historical initial-condition and continuous-source uncertainty.

Source-authentic 184,320 REC H/He rows + 3 original native state f64 bodies + actual 17 photon knots reused; no original H/He source, worker, history, geometry, thresholds, main, or production mutated. Source interval-certified endpoints do **not** certify the linear/log-linear interpolation between them. Do not promote an invented historical D initial condition to native REI or treat a gross photoheating sensitivity as source-native energy gain.

Canonical WU **34/49 (+0)**; REI central **28/88 (+0)**; working **33/88 (+0)**; Physical Fast **4/7 (+0)**. Original accepted tick160/131072, tick161 HOLD, production HOLD. All-stage R1–R10/C1–C10 receipts refer to one source-conditional science unit, not 20 new DAG nodes.

**Next science**, if available: source-owning original 26-event accepted *continuous* H/He stage history or rigorously bounded donor trajectories, and a physically sourced D initial state at original z=6. Only then run original H/He/DI/4-group OTS/thermal owner to adjudicate first 160→161. Do not create more frozen-source initial-value scenarios absent new independent physical evidence.
