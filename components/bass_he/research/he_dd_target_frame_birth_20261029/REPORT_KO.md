# BASS_HE HE_DD_TARGET_FRAME_BIRTH_LEDGER, 2026-10-29

**Scope:** original PR107 HEAD `85e2faeebd777ab3e9b287a0dc1dfd38d9af723c`; standalone add-only theory→coding development. No PR105/106/107 original physics or IVPs re-executed. Source is frozen `IAEA-NDS/exfor_master@939a14d7... M0475.x4`, original SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`. No new source/full-text qualification.

## Scientific results

At alpha-target rest, the incident photon energy E and CM cosine mu give D kinetic energies `K±=(M+E)/2-m ± sqrt(E²(s-4m²)/(4s))*mu` where `s=M²+2ME`. The **correlated pair**, not an arbitrary one-particle event label, always obeys `K+ + K-=M+E-2m = E-23.8464782 MeV`. The one-D marginal counting both deuterons per event has mean `(E-23.8464782)/2` independently of angular distribution. At E=213/330 MeV pair energies 189.1535218/306.1535218 MeV; marginal means 94.5767609/153.0767609 MeV. The support and single-D variance remain angular-law dependent: `Var_marginal=Delta² E[mu²]` and labeled covariance `-Delta²(E[mu²]-E[mu]²)`. In a non-even angular law the pair-centered cross moment is NOT the labeled covariance. The external physics event rate R_event and deposited heat remain unavailable.

The kinematic target-frame conversion is `E'_gamma=gamma E_lab (1-beta dot n)`, with exact rational squared-energy function implemented. A formal local event rate with a measured target-normal cross section and actual normal-frame photon distribution is `n_alpha^rest c int n_gamma^normal gamma(1-beta dot n) sigma_event(E') dE dOmega`; **this rate kernel is not implemented or numerically populated**. A source spectrum birth operator would inject two correlated daughters at K±; no D_fast transport/stopping/Cv provider is present.

## Source survey
Actual GitHub updated PR lists and selected original reports read across BASS_HE#107, BASS#244, bass_cr#122, rei_bianchi#263, rec_bianchi#156, WU088_HH#158, vigilode#108; Drive and Dropbox searched for historical BASS_HE checkpoints. Current source-specific input still lacks Arends/Silverman full detector calibration/event definition, qualified inverse DA at exact matched s, 330MeV total event SIG, actual photon phase-space history, liquid-He or cosmological target distribution, D_fast slowing and thermal deposition. Cross-repository chemistry/HD/UVB/He-flow data are related interfaces, not replacements. Survey is bounded to updated PRs/reports; no complete absence theorem over all code.

## Actual numerical/coding results
- `src/birth_ledger.py` pure Python Fraction exact per-event ledger; Decimal non-directed four-vector samples; moving target E'^2; manufactured angular moments. 27/27 new scoped unit tests PASS, compileall PASS.
- Separate C++20 Boost cpp_dec_float_100 independent four-vector calculation: 8 cases, max observed residual `1.78277808761e-109`, compiled with `-O2 -Wall -Wextra -Werror`, exit0. Independent algorithm is NOT a distinct native researcher reviewer.
- 300/300 deterministic randomized Fraction angular weights pass mean, variance, Cauchy and covariance controls.
- Wolfram CAS four independent symbolic residuals `{0,0,0,0}`; warning about symbolic names is nonfatal; results exact.
- Figure `figures/daughter_kinematic_support.png` rendered and directly visually inspected. It shows only K± support vs target-frame photon energy, no measured DA or physical rate.
- Initial C++ initializer-list expression-template compilation error repaired to explicit array values. Initial plot near threshold had floating conversion below exact rational threshold; shifted diagnostic sampling start by 1e-8 MeV. No physics formula/tolerance modified.
- Old BASS_HE full science suite, completed IVP, source campaigns and prior closed research operations NOT_RUN; previous R6/C9 independently NOT_RUN.

## Review and decision
PHYS-MATH PASS for pair-energy identity, count distinction, sign/dimension checks; C++ and Wolfram give algorithmic external methods; PHYS-MATH-CODE PASS_SCOPED for 27 new Python tests and 8 C++ four-vector cases. R6/C9 distinct-author independent review NOT_RUN. New local kinematics completed **1/2**, physical rate/deposition interface **0 admitted**. Inherited central **28/88**, HE **14/18**, PR105 **2/2**, PR106 **1/2**, reciprocity **1/2**. New scoped R stages **9/10**, C stages **9/10** (R6,C9 held); no central/HE increments.

### Principal claim gates
`kappa=null`, `R_event=null`, `physical_activation=false`, `L4=false`, `production=HOLD`. To activate, obtain the original experimental DA event/particle efficiency and polarization with source hash/quotation; a source-qualified total event cross section, target-frame photon history, target proper density/velocity distribution, and nonthermal D stopping/deposition/Cv. Source-tagged exact-s inverse raw DA may independently test reciprocity, but it does not replace actual 330 MeV gamma field.

**Next action:** introduce a measured, source-qualified 330 MeV photon/He target state and angular event spectrum through an independent typed adapter; run only affected tests before considering any physical rate. If external inputs remain unavailable, keep this standalone kinodynamic birth-moment result as a complete scoped reference, not production heating.
