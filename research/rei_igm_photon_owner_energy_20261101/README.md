# REI IGM | Source-owned cumulative absorbed photon, chemical, thermal and escaping-energy ledger

**Science unit:** \`REI_IGM_SOURCE_OWNER_EVENT_ENERGY_20261101\`. **Status:** \`DERIVED + NUMERICALLY_CHECKED + EXPLORATORY_SOURCE_CONDITIONAL\`, not canonical/admitted native REI first canonical interval, not Bianchi I photon transport. This is a **new physical calculation** from previously source-locked published UVB and Grackle H/He chemistry, **not another administrative/DAG audit**.

**Immutable base** Draft [PR #319](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/319) HEAD \`a51cf20df6afa5d98bd96be01a5e68c3cfe72785\`. Independent sibling [PR #320](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/320) source-own 46,080-node first-interval tick160/131072 analysis remains read-only and **BLOCKED** at frozen error threshold \`2e-4\`; no attempt to conflate these models.

## Original physical source and exact event owners

- Puchwein, Haardt, Haehnelt & Madau 2019, [MNRAS 485 47–68](https://doi.org/10.1093/mnras/stz222); [fiducial non-equilibrium UVB original ASCII](https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt), source 59-row REI Git blob \`218d81f68447da438228a7b102e1cec96a8e8a1a\`, 21 high-redshift original knot subset SHA256 \`faf3f87d94eefba71a781e1ae62ebf202760a56fb6c42afaceeba6ca8ffe235e\`. These six HI, HeI, HeII **photoionization rates [s^-1] and heating [eV/absorber/s]** are published model rates, not measured events. No extra \`4π\` or \`c\`.
- Original source-locked Grackle 3.4.1 \`af7939494ce65007887ada7b98d1813df6843346\`; REI owner \`igm_rates.rs\` blob \`dc3cc028a41ac852d94835372ce13545389d1c3a\`, \`igm_thermal.rs\` \`0648618d9822e169e9672ac3c556f86595c3b0b6\`. Preserve **Case-A escape** and uniquely owned photo excess / binding / collisional ionization / recombination / kinetic escape / CMB / adiabatic terms.
- Byte-locked PR319 six-state source Python SHA256 \`b1ad782557b9101b226edd8d9a203eacfbaa18dcd67cccbf03f020850b4a579e\`, never a claim that Rust was executed this time. Same source rate and gas fraction equations on FLRW redshift with two **chosen synthetic** IC variants: reset z10 almost neutral/T30K versus original-rate source prehistory evolved from z15.1. UVB-off as null control.

**New 26-component physical ODE:** original six FLRW H/He fractions/kinetic energy/proper time/Thomson τ plus 10 integrated per-H photo/CI/RR/DR event counts and 10 per-H thermal/binding/radiative energy source ledgers. \`dt=d ln(a/a_i)/H\`; no Bianchi shear, source RT or free escape-fraction calculation. Photon absorption from the imposed external field is **not** stellar photon production.

### Main computed original-source model data, z10→5.81

| Source/IC scenario | HI photon absorption [events/H] | HII recombinations [events/H] | Total absorbed photon [erg/H] | Photo excess heat [erg/H] | Escape/cooling [erg/H] | Thomson Δτ |
|---|---:|---:|---:|---:|---:|---:|
| Same UVB, true-model prehistory since z15.1 | 1.082135635795 | .268267288762 | 3.9078896681384e-11 | 1.1846418918652e-11 | 9.1100665630738e-12 | .02124628211791 |
| Same UVB, nearly neutral artificial reset at z10 | 1.216903200953 | .217793994506 | 4.4108151329395e-11 | 1.3372044616675e-11 | 8.4555612369939e-12 | .01738941655263 |
| Identical z10 IC, external UVB OFF | 0 | 1.757004115e-6 | 0 | 0 | 3.857007509e-17 | 7.680127696e-6 |

Prehistory needs **11.07463314% fewer absorbed H-ionizing photons** yet yields **22.17938453% more optical depth**, despite essentially equal final xHII≈1. This **does not constrain observed cosmic CMB τ**: the source and starting ionization/thermal history are *model choices*, an optically thin homogeneous EoR model, not 3D patchy reionization, not original Puchwein authors' full simulation.

The directly checked equation, with all quantities per physical H-nucleus reference, is
\[
\dot w = Q_{\rm th}/n_{\rm H}-2Hw,\qquad
\dot e_{\rm ion}=Q_{\rm bind}/n_{\rm H},\qquad
\Delta(w+e_{\rm ion})=\int[(Q_{\gamma,\rm abs}-Q_{\rm esc}+Q_{\rm CMB})/n_{\rm H}-2Hw]dt.
\]
\[
Q_{\rm th}=Q_{\gamma,\rm excess}-Q_{\rm CI}-Q_{\rm radkin}+Q_{\rm CMB},~~
Q_{\rm bind}=Q_{\gamma,\rm bind}+Q_{\rm CI}-Q_{\rm RR,bind},~~
Q_{\rm esc}=Q_{\rm RR,bind}+Q_{\rm radkin}.
\]
Wolfram independently simplified **two algebraic identities exactly to zero** (NOT a fresh different-model physical referee). Numerical integrated residual at tight method ≈2.3e-26 erg/H. [Three exact locally executed physics witness rows](PHYSICAL_EVENT_ENERGY_3_CASES.csv), Git blob \`a8722e194b3d4b10e2432b8d2143c573a1133b50\`, source CSV SHA256 \`d9a9986b893114802cdf2a15a3478a0c9388dc9d8e5903a03cbd57b44482f06f\`. [Standalone source-CSV balance verifier](verify_published_budget.py) is runnable via \`python verify_published_budget.py\` next to the CSV. It validates **published rows, not new solver rerun**.

## Execution and preservation

- New source-owned calculated **1,227 conditional-model rows** (1,203 time points, 24 epoch extracts), **4 PNG +4 SVG** scientific figures. REI PR319 prior baseline **24/24** tests passed; new cumulative ledger tests **17/17 normal and 17/17 optimized**. Source-included clean replay of 3 science CSV/JSON + 4 PNG **7/7 byte-exact**, independent knotwise quadrature, BDF/Radau same-author solver checks and zero-source negative control. Original rate and source identities checked.
- [All 20 R1–R10/C1–C10 stage ZIP SHA/CRC receipts](STAGE_SHA_RECEIPTS.md), each **REI central 28/88**, working **33/88**, WU **34/49**. The local backups also contain **four phase ZIPs** and master; the staged files are *not* 20 new scientific nodes.
- Full source master ZIP \`REI_IGM_SOURCE_OWNER_EVENT_ENERGY_SOURCE_MASTER_20261101.zip\` **1,019,627 B** SHA256 \`83963955eda36c84a3758afae5aaa0a49712b88275683ff308a6f94053f9ea64\`; all-stage nested archive ZIP \`REI_IGM_SOURCE_OWNER_EVENT_ENERGY_ALL_STAGES_20261101.zip\` **2,024,531 B** SHA256 \`cba8f73f2c9eea3310c26663d6e4f014cd6a8d34a528c7dce78eb5428a3d2b50\`. Master 54 entries CRC PASS, aggregate 25 entries CRC PASS incl. nested archives. Full Python ODE, 1,227 rows, 8 figures, tests and scripts are in **separate user-downloadable local ZIP**, not in this *thin* Git subtree. ChatGPT Library/Drive/Dropbox complete-binary remote readback **NOT_VERIFIED**, do not claim dual remote backup from GitHub.
- Native Rust REI \`RUX05\`, 46,080-node 26-event canonical first interval and live Bianchi source match **NOT_RUN**, Rust/Cargo unavailable here, linked research device OFFLINE. Browser connector inaccessible in this chat context. Native subagent NOT_RUN, same-author R6/C9 (not distinct author).
- **DAG:** REI central **28/88**, working **33/88**, WU **34/49**, canonical delta **0**. This directly constructs a source/thermal photon-owner ledger for *existing* \`REI-EXP-SCENARIO\`, \`RUX03\`, \`RUX05\`; owner/physics native admission still pending.

## Actual next scientific step

Consume the original immutable real **tick160** 46,080-node accepted state from [REI PR320](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/320) under original 26-event full model; implement *source- and parent-correlation-preserving* full-minus-two-half error map at [160,161] while keeping strict **2e-4** gate and no budget reset. In parallel match this conditional Puchwein EoR photon/energy source with original REI Rust rates, clock and photon owner, then source-match BASS Bianchi geometry and observed directional τ without importing unrelated REC/VigilODE anisotropic pilot as though equivalent. Do not launch a new audit loop or unbounded atomic source census.

**HOLD, NO_MAIN_MERGE, AUTO_NEXT_NODE=false, REI_L4=false, PRODUCTION=NOT_ISSUED.**
