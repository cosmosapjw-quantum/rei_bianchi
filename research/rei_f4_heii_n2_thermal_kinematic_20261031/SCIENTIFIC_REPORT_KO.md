# REI F4: Original BASS193 He II n=2 thermal excitation and nonthermal threshold eligibility (2026-10-31)

## Authority / preservation
**Parent** Draft PR #313 HEAD `47f34ccb68f02262f40cd3dfd198aa97abd35183`; read-only sibling PR #312 HEAD `ddf0a55b2a5db74e4678aa684444e9d72d4986ab`. Original BASS21/REI source owners unchanged, NO_MERGE, NO_FORCE_PUSH, no new cosmic IVP, no photo RHS injection.

**Published numeric atomic primary source:** K. M. Aggarwal, A. Igarashi, F. P. Keenan, S. Nakazaki (2017), *Radiative Rates and Electron Impact Excitation Rates for Transitions in He II*, *Atoms* **5**, 19, DOI 10.3390/atoms5020019, Tables 1 and 4. 1s→2s/2p_{1/2}/2p_{3/2} effective collision strength Upsilon vs log10 T=3.6...5.4. Physical domain: locally Maxwellian electrons, He II in its 1s ground state, 3.6<=log10(T/K)<=5.4. No extrapolation. Source original BASS T and plasma history from immutable PR302/303/312 source, SHA in private manifest.

**Common production-code cross-check:** Grackle 2017, Smith et al., MNRAS 466 2217-2234, DOI 10.1093/mnras/stw3291, `grackle-project/grackle/src/clib/rate_functions.c`, pinned content Git blob `dfbab661e7c45981eed750baebff140849917152`, specific `ceHeII_rate` thermal cooling coefficient. CHIANTI v11.0.1 independently provides HeII collision data, public `wtbarnes/chianti-database` commit `ffe260b75c1db00df2834d70397d6ab575b8c925`, `he/he_2/he_2.scups` git blob `ad2c183bef70dbb6a708bc375da65dfa98207cf5`, **not numerically spliced** into Aggarwal rates. Nonthermal author CCC HeII zip `e-HeII_XSEC_LS.zip` offered at `https://atom.curtin.edu.au/ccc-db/index.html` but raw numeric ZIP NOT_FETCHED. No unpublished-data contact blocker.

## Original source states and mathematical operator
Original BASS193 uses `n_e=n_b (q21·Y21)` including HeIII and all other native ionic charges. `n_HeII=n_b (nHref/n_b) yHe x_HeII` preserves isotope and helium number owner. From Aggarwal Tables 1 and 4, `E_1a / Ry = [2.999707, 2.999702, 2.999756]`, and `g_1s=2`. For each of three channels:
[
q_{1a}(T)=\frac{8.629\times10^{-6}\Upsilon_{1a}(T)}{2\sqrt{T/\mathrm K}}\exp[-E_{1a}/(k_B T)]\quad [\mathrm{cm^3 s^{-1}}],
]
[
\dot N_a= n_e n_{\mathrm{HeII}} q_{1a}/n_b\quad[\mathrm{events/(original\ baryon\ s)}],
\qquad \dot\epsilon_a=E_{1a}\dot N_a\quad [\mathrm{eV/(original\ baryon\ s)}].
]
Time exposure `dotN_a*Delta_tau` is a frozen endpoint coefficient, NOT a dynamical IVP, total heating, line luminosity or self-consistent excitation rate. `k_B=8.617333262145e-5 eV/K`, `Ry=13.605693122994 eV`.

Independent *nonthermal kinematic* source retains for each of the 192 arrival intervals × 4 first absorbers × 5 energy bands × 3 HeII transition thresholds the original electron count N, first kinetic moment M, and upper support `E_max=min(band upper,Epair−chi_first_absorber)`. Exact two-point-moment extrema of the fraction with `E>=transition threshold` generate conditional eligibility minima and maxima. These are mathematically allowed electrons, **not actual HeII collision event probabilities**. Overlap across transitions means do not sum marginal maxima.

## New numerical physical results
- **579** thermal HeII n2 transition rows, **193** Grackle comparison rows, **11520** first-electron nonthermal eligibility records, **192** source arrival summaries; **3 PNG + 3 SVG** scientific figures in original-source-private ZIP. 193 states, only **101/193** within published Table4 T support, 92 outside (no extrapolation). Original saved T ranges 100...11999.96 K. Original 192 source first electrons `4.374110632809568e-12 /b`, source kinetic `6.749242464433259e-11 eV/b`.
- Supported Table4 frozen point energy-loss exposure `8.354217730686933e-16 eV/b`, supported endpoint excitation-event exposure `2.0469310247883547e-17/b` (**not full history integral**).
- Aggarwal 3-channel n2 thermal energy-loss coefficient / Grackle `ceHeII` ratio across 101 native supported temperatures: **1.336831101515216...1.371818542301215**, median `1.371776811363900`. Prescription difference only, not physical uncertainty bound or a validation of temperature evolution.
- For HeII 2s original photoelectron eligibility: `[6.979531299794241e-26,3.171257141996121e-13]` initial electrons/b. 2p1/2 `[6.979531299794241e-26,3.171270437977819e-13]`, 2p3/2 `[6.979531299794241e-26,3.1711268472753175e-13]`. Only H I-first and Li I-first absorbers can reach ~40.81 eV excitation; He I-first and He II-first are excluded by primary photon energy ceiling. This is a **kinematic** electron envelope, not positive lower event yield.

## Validation & blind-referee style audit
Full private source-inclusive unit `bash VERIFY.sh`: Python **32/32** targeted tests, manifest **23/23**, exact deterministic computed source/plots rerun **PASS**, random 900 two-point moment counterexamples PASS; Wolfram evaluator `q_2s(12000 K,Upsilon=.155)=4.4149617159141926e-26 cm3/s` matched. Same-author adversarial audit only, distinct-author R6/C9 and native subagents **NOT_RUN**. Public Git contains derived report, arithmetic/source contract and selected witnesses; full 579+11520+193+192 result CSV and tested scientific Python code are in private master, not claimed as public Git objects.

**Gate:** WORKING=33/88, CENTRAL=28/88, F4_FAST=4/7, CANONICAL_DELTA=0; this auxiliary unit 1/1 scoped, F4 PARTIAL, L4_READY false, PRODUCTION HOLD, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE false.

**Next actionable source-owned science**: replace the Grackle `ceHeII` thermal cooling channel with the Aggarwal n2 energy-loss coefficient only after confirming exact energy owner and avoiding double counting; obtain public CCC HeII monoenergetic cross sections or published alternate and insert into actual multi-channel first-to-second collision cascade with daughter energy sharing. No private Langer data requirement.
