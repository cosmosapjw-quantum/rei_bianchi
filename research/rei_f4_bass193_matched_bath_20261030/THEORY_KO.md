# REI/BASS frozen-bath H/He source discrepancy, exact five-species derivation

At each of the original BASS21 193 saved epochs, let (Y_i=n_i/n_b), (X=(Y_{H1^0},Y_{H1^+},Y_{He4^0},Y_{He4^+},Y_{He4^{2+}})^T), (q_5=(0,1,0,1,2)^T), (e_o=\sum_{i\notin H1,He4}q_iY_i\ge0). Then (n_e^B=n_b(q_5^TX+e_o)), (n_e^5=n_bq_5^TX), so their difference (n_o=n_be_o) is exactly the omitted-isotope electron pool, not a fitted correction. The source-owned BASS T, nb, photon UV and H are fixed external coordinates; (Y_i\) is per *baryon*, not per Href.

For H/He original BASS photo generator (G_B\), native RR/DR source matrix (M_B(T)\), and selected REI Grackle-3.4.1 k1...k6 rate-law matrix (M_R(T)\), after converting the latter's cm³/s to m³/s by 1e-6:

\[
F_B=G_B X+n_e^B M_BX,\quad
F_{R|B}=G_BX+n_e^BM_RX,\quad
F_{R|5}=G_BX+n_e^5M_RX.
\]

The first is a block of the original BASS21 model (its original n/T pilot is zero); the second is a REI-rate **counterfactual** under *the exact same BASS electron pool*; the third additionally restricts electrons to H/He-only. In particular neither REI lane is the full original REI17 native chemical/thermal/photon model. With \(\Delta M=M_R-M_B\),
\[
\boxed{F_{R|5}-F_B=\underbrace{n_e^B\Delta M X}_{\Delta F_{rates}}-\underbrace{n_oM_RX}_{\Delta F_{pool}}.}
\]

For the five-state **fixed-T, fixed-nb, fixed-other-isotopes partial Jacobian**,
\[
J_B=G_B+n_e^BM_B+n_b(M_BX)q_5^T,\qquad
J_{R|5}=G_B+n_e^5M_R+n_b(M_RX)q_5^T,
\]
\[
\boxed{J_{R|5}-J_B=n_e^B\Delta M+n_b(\Delta MX)q_5^T-n_oM_R.}
\]
The middle term is rank≤1 but the entire correction need not be. With additional dynamic isotope or EOS/thermal/photon variables, omitted derivative columns and (\partial T/\partial Y\) must be restored; do not call this a full J21↔J17 intertwining theorem. The seven stoichiometric columns (S_e=e_{dst}-e_{src}\) obey \(\mathbf1^TS=0\), charge (q_5^TS_e=+1\) CI or −1 RR/DR. Thus both the five-state chemical F and J conserve H1+He4 nuclei (not general reaction-network total without omitted channels).

The actual source `rust/rei_microphysics/src/igm_rates.rs` is pinned at Git blob `dc3cc028a41ac852d94835372ce13545389d1c3a` (upstream Grackle commit `af7939494ce65007887ada7b98d1813df6843346`). The operational low-T branch (T/11605\le0.8\) retains Grackle's nonphysical-as-data CI coefficient floor (10^{-20}\,cm^3/s), and switches HeII DR off. 102/193 BASS saved samples are on this branch. They are source-literal rates, not measured 100K collisional ionization. Cross-owner actual temperature and electron-pool coupling is not demonstrated.

**Source evaluation:** BASS numerical coefficients projected 129/129 from Git blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7` via pre-existing donor, not a new raw-byte verification of original coefficient JSON. Actual BASS native `AtomicNetwork.evaluate` matched its H1/He4 F and J block to (1.23e{-32},6.16e{-33}\,s^{-1}). REI Grackle Rust was not compiled; the Python translation with explicit literal coefficients passed 36 scoped tests. A Wolfram independent symbolic *tool* check (not a distinct human/model author) returned exact zero for F/J decomposition and conservation.

Historical Grackle network: https://grackle.readthedocs.io/en/grackle-3.4.1/Network.html ; Verner-Ferland RR: https://www.pa.uky.edu/~verner/rec.html . Physical model scope and all original negative CI/budget gates remain unchanged.
