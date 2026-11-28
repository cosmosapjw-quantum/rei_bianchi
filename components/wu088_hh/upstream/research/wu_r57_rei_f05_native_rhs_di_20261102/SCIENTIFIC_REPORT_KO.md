# WU R57 | Original REI F05 26-event native RHS manifold → source-conditional D history

2026-11-02. Physics-first WU088_HH research unit serving original REI Bianchi IGM. This is NOT an original REI source-owner continuous solution, actual D historical initialization, or accepted tick161.

## Authority and science contract

- WU immutable parent Draft PR #196 HEAD \`2d52baa98bd97b513a2cdad2f2c1fe1b5e9917b0\`.
- Original REI source PR #367 HEAD \`b9cd64afee16dc4c0e74aa39b00c831df626c777\`, sealed original 26-event H/He/OTS/thermal RHS, original accepted material ticks 0,64,128,160; original four-epoch RHS 20-field 184320-row private CSV SHA256 \`5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913\`. Original REI kernel SHA256 \`579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644\`; source tar SHA256 \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\`.
- Original REC #195 full 184320 accepted H/He state CSV SHA256 \`6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c\`.
- Original physical H/He source state from the original REI 26-event model: source proper time \(\Delta t_{\rm tick}=4871848749.16828\) s, 46080 native material cells, 17 original group-photon forcing knots; native 4 photon groups, last G3 exactly zero.
- Savin (2002), ApJ 566, 599–603, DOI https://doi.org/10.1086/324218, original D/H charge exchange 47-pair table. Stancil, Lepp & Dalgarno (1998), ApJ 509, 1, DOI https://doi.org/10.1086/306473, primordial nonequilibrium D chemistry z≈4000–10, NOT a measured REI z=6 D initial condition. The R54–R56 HI-cloned DI photo/RR/EII approximations and hypothetical \(\eta_D=2.5\times10^{-5}\) are retained and labeled.

## R5 constructive derivation: source-cone C1 with exact endpoint tangent

The original REI #367 source code was reused as a byte-locked *read-only* four-epoch replay, with exactly seven additional per-cell output columns: source \(N_{\rm HII},N_{\rm HeII},N_{\rm HeIII}\), derivatives \(\dot N_{\rm HII},\dot N_{\rm HeII},\dot N_{\rm HeIII}\), and \(\dot{\log T}\). All 184320 original 20-field records remain byte-for-byte *text-identical* in source column values, zero mismatches. New 184320×27 private RHS gzip SHA256 \`d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e\`.

Original source mechanical identities:
\[
N_e=N_{\rm HII}+N_{\rm HeII}+2N_{\rm HeIII},\qquad
\dot N_e=\dot N_{\rm HII}+\dot N_{\rm HeII}+2\dot N_{\rm HeIII},
\]
\[
U=\frac32 k_B (N_H+N_{He}+N_e)T,\quad
\frac{d\log T}{dt}=\frac{\dot U}{U}-\frac{\dot N_e}{N_H+N_{He}+N_e}.
\]
Original derivative electron identity max rel \(2.23\times10^{-14}\); thermal temperature identity max rel \(1.49\times10^{-13}\). This uses original total-U thermal RHS, NOT extra double-counted \((3/2)k_BT\dot N_e\).

A direct untransformed cubic Hermite HII fraction on [0,64] violates the physical upper bound in 150/46080 original cells at the midpoint, with max \(x_{\rm HII}=1.0000566889968443\). This negative finding was preserved. A naive clamp changes the source derivative and is not employed.

Instead define source-positive coordinates at each accepted endpoint \(t_i\):
\[
x=N_{\rm HII}/N_H,\ h=\log[x/(1-x)],\qquad
u=\log(N_{\rm HeII}/N_{\rm HeI}),\quad
v=\log(N_{\rm HeIII}/N_{\rm HeI}),\quad \theta=\log T
\]
where \(N_{\rm HeI}=N_{He}-N_{\rm HeII}-N_{\rm HeIII}>0\). The original 26-event source slopes, e.g. \(\dot h=\dot x/[x(1-x)]\), \(\dot u=\dot N_{\rm HeII}/N_{\rm HeII}-\dot N_{\rm HeI}/N_{\rm HeI}\) and analogous \(\dot v,\dot\theta\), are exact algebraic consequences of original source point RHS.

For \(\tau=(t-t_i)/(t_{i+1}-t_i)\), reconstruct \(q(t)=H_{00}q_i+H_{10}\Delta t\dot q_i+H_{01}q_{i+1}+H_{11}\Delta t\dot q_{i+1}\), with cubic Hermite polynomials \(H_{00}=2\tau^3-3\tau^2+1\), \(H_{10}=\tau^3-2\tau^2+\tau\), \(H_{01}=-2\tau^3+3\tau^2\), \(H_{11}=\tau^3-\tau^2\).

Invert the coordinates:
\[
x=1/(1+e^{-h}),\quad
(N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII})=
N_{He}(1,e^u,e^v)/(1+e^u+e^v),\quad
T=e^\theta,
\]
\[
n_e=(N_Hx+N_{\rm HeII}+2N_{\rm HeIII})/V.
\]
This provides nonnegative chemical populations and H/He nuclear conservation, exact H/He electron accounting and source endpoint values and one-sided source instantaneous derivatives. It is C1 at the original accepted knots 64,128,160. Symbolic Wolfram logistic/softmax identities reduce to \(\{0,0,0\}\). The source only certifies the four endpoints and their RHS: the *interior interpolation itself is not the true original accepted continuous 26-event orbit*, nor a global error enclosure.

For 160→161, the model retains the **unaccepted preview** donor from R56 by explicit straight interpolation. The native source derivative construction has no authority to promote tick161.

## R57 original physical calculation and scientific decision

The WU R56 original 46k-cell D+ / Savin charge exchange, H-cloned DI photo/RR/EII and group photon-conservative deficit equations were rerun with two initial D scenarios from tick0 (ALL_NEUTRAL, H_MATCHED). For each, separately run *original source point linear* and *native source derivative C1 Hermite*. These are distinct donor hypotheses on the **same actual original H/He source epochs**; no new original H/He owner simulation or new D initial scientific state is claimed.

- Original native RHS Hermite H_MATCHED tick160 median \(y_{\rm D^+}=0.9999498027354448\), source-point linear \(0.9999498027039342\). Gross D photon absorptions in native 160→161 are \(\mathbf{1.844039025653054\times10^{55}}\) vs \(\mathbf{1.84403722739384\times10^{55}}\) photons/cMpc³, a source-path model difference \(\simeq 9.75\times10^{-7}\) relative.
- Original native RHS Hermite ALL_NEUTRAL tick160 median \(y_{\rm D^+}=0.492280093742615\), source-point linear \(0.492280093009123\). Gross first-tick D photon absorptions \(\mathbf{6.189459284155781\times10^{58}}\) vs \(\mathbf{6.18945928493661\times10^{58}}\) photons/cMpc³.
- Across source-accepted interior times, native source-cone and linear original-point HII curves differ by at most \(\mathbf{9.95594665691435\times10^{-5}}\) absolute over the tested 33 temporal sampling knots. The two D IC hypotheses remain very strongly separated even with source-native RHS temporal tangency.
- H_MATCHED source-cone gross photoelectron energy / |original native F05 \(\Delta U\)| median \(\mathbf{5.431630253011116\times10^{-6}}\), 0/46080 cells >1%; ALL_NEUTRAL median \(\mathbf{0.0355290970779811}\), 27024/46080 cells >1%. These are GROSS conditional energy candidates, **NOT NET physical heat**, and source HHe/OTS thermal/photon energy is not repartitioned.
- Full WU 46k-cell numeric physical result gzip SHA256 \`d6c7068ef6b07319a8c7b4715a0c681941d6a2c3dbb068ccceb53e5b98b3100e\`. Original source native charge/thermal audit and independent all 46k photon row-recount max rel \(\mathbf{3.6031\times10^{-16}}\); 0 invalid D fraction; four-group number balance max source scenario <\(4\times10^{-14}\), 5-flux population ledger <\(5\times10^{-15}\). Same-author disjoint stdlib audit PASS, normal unittest 9/9, optimized \`-O\` 9/9 PASS.

The result is **DERIVED / SOURCE-NATIVE ENDPOINT RHS IMPLEMENTATION-VERIFIED / SOURCE-CONDITIONAL NUMERICALLY CHECKED**, without a physical D initial condition or original continuous donor error enclosure. The history initial state remains the dominant open physical input; do NOT turn this one result into another family of adjacent approximate-source PRs. The next useful source-owner research is the true versioned V2 [160,161] 3-lane tick and 14-ledger acceptance with original continuous source time or an actual cosmological D initial state from high-z chemistry modeling, not source interpolation tuning.

## DAG, provenance and preservation

Exactly one new scoped WU science unit, not 20 DAG nodes. Original WU **34/49 (+0)**, REI central **28/88 (+0)**, working **33/88 (+0)**, Physical Fast **4/7 (+0)**. \`REI_L4=false\`, \`HH_R10=OFF\`, original V1 tick161 remains FAIL, original V2 tick161 unaccepted, \`PRODUCTION=HOLD\`, \`NO_MAIN_MERGE\`, \`NO_FORCE_PUSH\`, \`AUTO_NEXT_NODE=false\`. Native subagents unavailable, \`native_subagent=NOT_RUN\`; distinct-author blind referee NOT_RUN; same-author independent R57 audit actually executed. No original REI source/worker/history/main mutation.

Protected R57 folder: \`/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102\`. Reproduce using \`python3 r57_native_rhs_history_di.py --out results\`, \`python3 audit_r57.py\`, \`python3 -m unittest -v test_r57\`, \`python3 -O -m unittest -v test_r57\`. To regenerate native 26-event derivative file use isolated \`r57_derive_native_source_derivatives.py\` with original, precisely SHA-locked REI/REC/BASS_HE source and private native state paths from \`CHECKPOINT.json\`, not by modifying original repository.
