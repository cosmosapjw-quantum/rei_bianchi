# BASS_HE HE17 R9: warm P01 ì²« ì ì¸ì¦ì ê³µë³ ì ë¥Â·ê´ì¸¡ë ìë¹ ê³ì½ê³¼ REI ê°ë° ë³´ì¡°

**ì¼ì:** 2026-10-14 (Asia/Seoul). **ì í ë¨ê³:** `R9` (ì ì ê²°ê³¼Â·ì½ë© ì°ê²°)ë§ ìí. **ë¶ëª¨:** `BASS_HE` draft PR53, commit `a9220de96339fa08ece6251aeb4ac2c47f0f13c5`. `HE17 R5âR8`ì ê³¼í ê³ì°ì ë°ë³µíì§ ììê³ , R10 ì¢ë£ ëë 15ê° íì ìì fine ì¸ì¦ì ì´ë² ê²°ê³¼ë¡ íìíì§ ìëë¤.

## ìì½ ë° ê·¼ê±° ìí

ì´ë² ê²°ê³¼ë ì´ë¯¸ ì±íë **ê°ì warm P01ì ì²« ì** `0â¤tâ¤6.25Ã10^9 s`ì íì íì¬ R7ì ì ì columnÂ·ì¤ì°¨ carryì R8ì ì¬ì°¨/ì¤ì°¨ íë¥  êµ¬ê°ì íëì **ì¤í ê°ë¥í ì½ê¸° ì ì© source-bound ë°í ê°ì²´**ë¡ ê²°í©íë¤. ì ìë¹ê¸° `src/he17_consumer.py`ë ì¤ì¡´íë R8 ZIPì ì ì²´ hashÂ·57ê° payload identityÂ·CRCÂ·R7 ìë³¸ ZIPÂ·R5 `CONTRACT.json`/`SOURCE_LINEAGE.json`Â·receiver commitÂ·NPZÂ·Hermiteë¥¼ ëì¡°í ë¤ ê°ì ë°ííë¤. ì´ë¤ chemistry/photon ODEë ì¬ì¤ííì§ ìëë¤. ê³µê°ë ê³¼í êµ¬ê°ì **inherited certified**ì´ë©°, source ìë¹Â·ì ì ê²½ í©ì±ìì **directly derived / implementation tested / WolframâxAct checked**ë¤. ì¸ë¶ ëë¦½ ê³¼íì¬ì¬, ì¤ì  native íµí©, ì ì²´ ì°ì£¼ë¡ ì ê´ì¸¡ ì¤ì°¨Â·foregroundë **NOT_RUN / unresolved**ë¤.

## 1. ê¸°í, IC, ë¨ìì ì ì© ìì­

ìê·¸ëì² `(-,+,+,+)`, `x^0=ct`, `u^a u_a=-1`, `dx^a=c k^a ds`, `k^2=0`, ê´ì  ë§¤ê°ë³ì `s`ë ì´ë¤. `Î¸`ë ë¬¼ì§ ì¸ê³ì ìì ì´ ë¨ìë¡ ì¦ê°íë age scalarì´ë©° `q_a=câ_a Î¸`, `u^a q_a=1`ë¡ ëë¤. `D=-uÂ·k>0`, `A=qÂ·k=dÎ¸/ds>0`ë¥¼ **ë°ë¡** ì ì§íë¤. ì¼ë°ì  ì ìì ë¥ë `J_e^a=c n_e u^a+j_e^a`ì´ê³  `uÂ·j_e=0`ì´ë¤. ê´íê¹ì´ë

\[
 d\tau_T=-\frac{\sigma_T}{c}J_{e,a}\,dx^a,
 \qquad
 \mathcal C_{[t_0,t_1]}
 =\int_{t_0}^{t_1}\left(\frac{cD}{A}n_e-\frac{k_a j_e^a}{A}\right)d\theta,
 \qquad \tau_T=\sigma_T\mathcal C.
\]

`n_e`ì SI ë¨ìë `m^-3`, columnì `m^-2`, `Ï_T`ë `mÂ²`, `Ï`ë ë¬´ì°¨ìì´ë¤. íì¬ ì sourceë prescribed normal-comoving non-tilted LRS Bianchi Ië¡ **ê·¸ source-age/normal-clockìì** `D/A=1, j_e=0`ì ì ì©íë¤. `c=299792458 m/s`, `k_B=1.380649Ã10^-23 J/K`, `1eV=1.602176634Ã10^-19 J`ë¥¼ ì ì§íê³  `Ä§=1`ì ê°ì íì§ ìëë¤.

ìì¹ sourceì `n_H`ë *proper* `cm^-3`ì´ë©°, `Ï_e=n_e/n_H=x_HII+(3/38)(x_HeII+2x_HeIII)`ì´ë¤. ê·¸ë¬ë¯ë¡ `\mathcal C=cÂ·10^6â«n_H^{cm^-3} Ï_e dt`. ì´ sourceì photon stockì ë³ëì *reference-volume* `cm^-3` ì¢íì´ë©°, ì´ë¯¸ properì¸ ì ìë°ëë¥¼ photon stockì ë¶í¼ë¹ë¡ ë ëëì§ ìëë¤. `w`ë `eV/H`, warm ì´ê¸° gas ì½ `50000K`, FT03/HuiâGnedin/Verner + HM12 emissivity, Case-A escape, CR/RCT/HH OFF, ì NPZ ë°ì´í¸ `3cbf35cf...2be`, receiver commit `a5c958c4...`, fixed Hermite `7a201539...`ê° ìë ¥ ê²½ê³ë¥¼ ê²°ì íë¤. ê³¼ê±° R4 ë¤ë¥¸ slopeë ìê¸ ì ì©íì§ ìëë¤.

**ëê°ë AXBI ì¤íê³¼ êµ¬ë³:** AXBIë `Y_He=0.2454`, `f_He=1227/15092`, `Grackle/IGM+MD14`, initial gas ì½ `8.1K`, `w`ë `erg/H`ë¤. ê·¸ ëª¨ë¸ì **stellar spectrum** `50000K`ë¥¼ warm gas `50000K`ì ëì¼í ê¸°ì²´ ì¨ëë¡ ì·¨ê¸íì§ ìëë¤. ì´ cold sourceë¥¼ R9ì warm ìì¹ ìë¹ê¸°ì ë£ì¼ë©´ typed `SOURCE_FAMILY_MISMATCH`ë¥¼ ë°ííëë¡ íë¤.

## 2. ì¬ì¬ì©í  ì ë¦¬: ì í bin ì¸ì¦ì ê³µë³ ìë¹ì foreground í©ì±

**ì ë¦¬ (source-bound optical-current return).** (i) ëì¼í ì í ììÂ·ê´ì IVP, clock, ìì ì ìë°ëì ë¶í¼, ëì¼í ê´ì /ë¨ë©´ì ì ëí ì¸ì¦ë ì ì column êµ¬ê° `C_-â¤Câ¤C_+`ì´ ìê³ , (ii) ê´íê¹ì´ `B_Â±=Ï_T C_Â±`ê° `0â¤B_-â¤B_+â¤1`ì´ë¼ íì. ê·¸ë¬ë©´

\[
 B\in[B_-,B_+],\qquad
 P_{\rm cond}=1-e^{-B}\in[S_4(B_-),S_5(B_+)],
 \quad S_n(x)=\sum_{k=1}^n\frac{(-1)^{k+1}x^k}{k!}.
\]

ì¶ê°ë¡ **ë³ëë¡ íê°í** ê°ì ê´ì Â·ê´ì¸¡ì ì¸ê·¼ì foregroundê° `0â¤T_-â¤Tâ¤T_+â¤1`ë¡ ì£¼ì´ì§ë©´,

\[
 \boxed{\,
 [1-S_{25}(T_+)]S_4(B_-)
 \le P_{\rm obs}\le
 [1-S_{24}(T_-)]S_5(B_+)\,},
 \qquad P_{\rm obs}=e^{-T}(1-e^{-B}).
\]

**ì¦ëª:** ì§ìí¨ìì êµë ê¸ì/ì ë¶ remainderìì `S_{2m}(x)â¤1-e^{-x}â¤S_{2m+1}(x)` (`0â¤xâ¤1`)ì´ê³  `1-e^{-x}`ë ì¦ê°í¨ì, `e^{-T}`ë ê°ìí¨ìë¤. êµ¬ê° ê³±ì ë¹ììì´ë¯ë¡ ìì ë°ê¹¥ í¬í¨êµ¬ê°ì´ ì±ë¦½íë¤. Tì Bì ì¤ì  ìê´ê´ê³ê° ìì¼ë©´ ì´ êµ¬ê°ì ë ë³´ìì ì¼ ì ìë¤. `T`ê° ì ìëì§ ììì¼ë©´ `P_obs=null`ì´ì§ `T=0`ì´ë¼ë ë»ì´ ìëë¤. ì´ ì ë¦¬ë **ì í´ì§ ê´íì  pathì scattering-out/ì²« ì¶©ëë¥  ê´ì¸¡ë**ì¼ë¡, ì ì²´ polarized Thomson ìì±Â·ì°ë ì¬ë¶ë°° ë°©ì ìì´ë source photon-feedback ê³ì°ì ëì íì§ ìëë¤.

## 3. ì¤ì  ìë¹ë êµ¬ê°ê³¼ ì íí ì°ì  ëì¡°

R7ì ì ì²´ photon 2904ì±ë¶ error vectorë¥¼ ë³´ì¡´íê³ , ê°ì ì²« ì 64ë¶í ì `\mathcal C` êµ¬ê°ì **ì¬ê³ì°íì§ ìê³ ** ì¬ì©íë¤. ììí ì¶©ë¶ ë°ê²½ì `R_C<1585.727990634604 m^-2`ë¤. ë¨ë©´ì ì ì¤ì§ í ë² `Ï_T=6.6524587051Ã10^-29 mÂ²`ì´ë¤. Python exact Fraction ê²ì¬ìì `C_Â±Ï_T=B_Â±`ê° ë ëì  ëª¨ë **ì íí ê°ìë¤**.

\[
 \boxed{B\in[7.99991934859042930820094,\;7.99991934859042951918074]\times10^{-9}},
\]

\[
 \boxed{P_{\rm cond}\in[7.99991931659107460155593,\;7.99991931659107481253574]\times10^{-9}}.
\]

êµ¬ê° ëì ì íììì ë°ê¹¥ ë°ì¬ë¦¼íì¼ë©°, raw ê²°ê³¼ JSONì ì íí ì ë¦¬ìë¥¼ ë£ìë¤. ì´ë ìë¡ì´ ì¤ì  ì¤ì°¨ ê°ìê° ìëë¼ R8ìì ì´ë¯¸ ëìí íë¥  readoutì ììì´ë¤. ì¤ì  ì°ì£¼ë¡ ì  foregroundë **ë¯¸ì§ì **ì´ë¯ë¡ ê¸°ë³¸ ë°íì `observer_probability=null`ì´ë¤.

**ì ì¡°ë ì¡°ê±´ë¶ ì§ë¨**ì¼ë¡ ì¸ë¶ìì `T_-=T_+=1/4`ë¥¼ ê³µê¸íì ë, ì´ë² ìë¡ì´ 24/25ì°¨ foreground ê³ì°ì

\[
 P_{\rm obs}\in[6.23034342826918697527635,\;6.23034342826918713958759]\times10^{-9}
\]

ë¥¼ ë°ííë¤. ì´ë **ì ì¡°ë foreground**ì´ê³  P01 ì°ì£¼ë¡ ì ì¤ì  ê´ì¸¡ ê²°ê³¼ê° ìëë¤. 25ì°¨ ë¤ì í­ì `Tâ¤1`ììë ìì exact rationalë¡ ì¶©ë¶í ê³ì°ëë¤. `T>1`ì ì´ ìì-domain ê²½ë¡ê° ê±°ë¶íë¤. ë í° Tìë ë³ëì ê²ì¦ë exponential range reduction ëë ëë¦½ foreground solverê° íìíë¤.

## 4. Code/API / evidence identity

`python src/he17_consumer.py --archive inputs/BASS_HE_HE17_R8_ADOPTION_INTEGRATION_20261014_v1.zip --out results/NEW_RETURN.json`ë¥¼ ì¤ííë¤. ê¸°ì¡´ ì¶ë ¥ì ë®ì´ì°ì§ ìëë¤. ë©ìëë `read_source_certificate`, `make_result`, `foreground_probability`. ìµì ê³ì½ìë **ìë³¸ SHA256+57 manifest payload+CRC**, nested R7 ZIP, R7 result, R7 endpoint, ì R5 `CONTRACT`ì `SOURCE_LINEAGE`, receiver commit/NPZ/reference identity, ìê° `[0,6250000000]s`, `3/38`, sigma, exact column/tau/probability, 4gas+2904photon error, missing subsequent-cell majorant=nullì í¬í¨íë¤. ì¦ê±° íì¼ì ê·¸ë¥ ì´ë¦ì¼ë¡ë§ ì°¸ì¡°íë ëì  **ìë ¥ ìë³¸ì ì½ì´ ê²ì¦**íë¤.

ì R7ì 4ì±ë¶ `hB Îµ_N` ìì¶ì **ê°ì ì²« ììì Bê° ê³ ì ì¼ ë**ì íì ëë¤. ë¤ì ì ì¥ ìì ì B/Îº/reference/ìì°¨ë¡ full 2904ì±ë¶ ë²¡í°ë¥¼ ê³±í´ì¼ íë¯ë¡ R9 ë°íì ê·¸ ìì¹Â·hashë¥¼ ì§ì íê³  `subsequent_cell_error=null`ë¡ ì ì§íë¤. ì ì¥ë ì¨ëÂ·ì ìë°ëì ë³ë PL í¸í¥, ëª¨ë¸ calibration, baryon/atomic-fit/systematic, continuous spectral/angle error, ì ì²´ observer tailì ì¬ì í ë³ëë¤. ë¶ëª¨ì mpmath.iv primitive ì íì±ì ë³´ì¡´ë íì¤í¸ì ìì¡´íë©° ì ì²´ ëêµ¬íì ê²ì¦ì´ë¼ê³  ì£¼ì¥íì§ ìëë¤.

**ìë³¸ íì¤í¸/ì¤í ê²°ê³¼:** ì²ììë ë¯¸êµ¬í source ìë¹ê¸°ìì ììë red (`NotImplementedError`)ë¥¼ ê´ì°°íê³ , ê°ì 11ê¸°ë³¸ ê¸°ë¥ ê²ì¬ë êµ¬í ë¤ green, ì´í Decimal ëë¦½ numerical crosscheckÂ·T=1 ê²½ê³ 2ê°ë¥¼ ì¶ê°í´ ìµì¢ **13 unittest íµê³¼(exit0)**. í¨í¤ì§ 57 payloadÂ·nested ZIP CRCÂ·R5 lineage ì¼ì¹, source mismatchÂ·sigma mismatchÂ·íì¼ ì¤ì¼Â·T ë²ì ê±°ë¶, ì¨ë/ë¨ì/foregound null, ì íí sigma ê³±ì íì¤í¸íë¤. ì source RHSÂ·ODEÂ·native receiverÂ·HPC/ê¸°ì¡´ R5/R7 ì¤íì 0í.

Wolfram Language 15.0.1ìì  ì²« í¸ì¶ì scalar í­ë±ì **8ê° 0**, ì´ê¸° xTensorë package-name resolution ê²½ê³ ë¡ ëª¨ë FAILì´ìë¤. ì¤í¨ ì¶ë ¥ê³¼ ì½ëë¥¼ ë³´ì¡´íê³  `Needs` í ë³ëì `ToExpression` íì±ì¼ë¡ scopeë¥¼ ìì íì¬ ë ë²ì§¸ Wolfram í¸ì¶ìì **ì¤ì  xAct/xTensor1.3.0 tensor í­ë±ì 5ê° ëª¨ë 0**ì ì»ìë¤. ê³µì archive/extracted xTensor íì¼ SHAë¥¼ ê²ì¬íë¤. ì´ 2í í¸ì¶ì ëì¼ ìì±ì + CASì ìí ê²ì°ì´ë©° ì¸ë¶ ëë¦½ ì¬ì¬ ëë native subagentsë NOT_RUNì´ë¤.

## 5. ë³ë ¬ `rei_bianchi` ì¤ì  Codex ìíì ìµì ë¤ì ìë¹

ì¤ì  local worktreeë¥¼ **2026-10-14T12:58:19Z**ì ì½ìë¤. ìµì  HEAD `45f166adee36d57cabe712ff66209926d1aa1556`, tracked clean. AX07 FLRW ZERO scoped PASS, AX08 signed family IN_PROGRESS, ì HALF_MINUS ì½ accepted 81480 ì§í, AX11 refinement/T1Â·AX12 source/IC configë ì¤ë¹ëì§ë§ run not started, AX14/15 ë¯¸ìë£. `STATE.next_ready_ids=[]`. ì¤ì  ownerë ìµê·¼ ë³ëë¡ **ì¨ë rate tableê³¼ bounded component benchmark**ê¹ì§ ê²ìíë¤. ì´ ì±ë¥ ì¤ë¹ë¥¼ R9ê° êµ¬ííë¤ê³  ì£¼ì¥íì§ ìì¼ë©°, ìì§ ì¤ì  physical full signed result/empirical convergence certificateê° ìë¤.

ì¤ì  comparator `research/axbi_goal_20261014/convergence/compare_histories.py` SHA256 `35e1499ef9a69180e5df442c198d3b4c28ea1090c9f6829aad1a68eba8c69cc9`ìë HE floor ìì ì´ **ì´ë¯¸ ë°ì**ëì§ë§, HH source-pair guard ë° CR exact PL normì ìì§ ì ì©ëì§ ììë¤. R8ìì íì¤í¸Â·ê²ìí **ì¦ë¶ í¨ì¹**ì ë ê³µê¸ helperë¥¼ ì´ë² ìì Codex handoffì ì íí ì¬í¬í¨í´ ìë¹ ì§ì ë§ ê°±ì íë¤. Source relationì baseline `d7676b93...`ì T1 prepared `4de69c1e...` ê° HH69ì ì¤ì  ì¸ output-resource í¸ì§ì íì íê³ , numerical target/resource ì°¨ì´ì T1 ìì§ ë¯¸ì¤íì´ë¼ë ì¬ì¤ì ë³´ì¡´íë¤. CR62 exact union-knot PL reconstruction normì ë°ì´í°ê° ë¤ì´ìì ëë§ opt-inì¼ë¡ ì°ë©° true-IVP errorê° ìëë¤.

**READY_FROM_BASS_HE:** `HE_REI_R9_REDUCER_SUPPLIER_RETURN`ì tested patch+source identity+handoffì `HE17_FIRST_CELL_CURRENT_RETURN`ì runnable consumer. **NOT_READY:** owner AX08/11/12 ì ì²´ DAG, actual source-matched completed T1 pair, native warm photon/current call site, signed shear claim admission. ê¸°ì¡´ recovery adapters/process/queueë ownerë§ ê´ë¦¬íë©° ì´ë²ìë ì¸ë¶ ì ì¥ìì ê¸°ë¡/í¨ì¹/launchíì§ ììë¤. Reionizationì BBN-style species/temperature abundance goalì warm HE optical certificateë¥¼ ì ì íì¡°ê±´ì¼ë¡ ë£ì§ ìëë¤.

## 6. ë¬¸í ë²ì ë° ë¤ì ë¨ê³

ë¬¸íì ê³µë³ RTEììë ê´íê¹ì´Â·ë§¤ì§ rest frame absorptionì ë¶ë³ì±ì Younsi, Wu & Fuerst (2012), A&A, https://www.aanda.org/articles/aa/full_html/2012/09/aa19599-12/aa19599-12.html ìì ëì¡°íë¤. ì¤ì°¨ì data/discretization/roundoffÂ·goal-functional êµ¬ë³ì KehletâLogg, *Numerical Algorithms* (2017), doi:10.1007/s11075-016-0250-4 ë° SciSpaceìì ì°¾ì Han (2015), doi:10.1080/00036811.2014.992423ì ë²ìë¥¼ ì°¸ê³ íë¤. ì ì column ë° foreground êµ¬ê°ì ì´ ë¬¸íì ìì¹ë¥¼ ê°ì ¸ì¨ ê²ì´ ìëë¼ ë³¸ë¬¸ìì ì§ì  ì ëí source-bound í¨ìë¤. ë¬¸í ì ì²´ ë¼ë¬¸ì ëë¦½ novelty claimì ìë¤.

**ë¤ì ì í ë¨ê³ R10:** íì¬ ìë³¸ ì¸ì¦/ì¤í ì½ë/ì¤ë³µ ìë REI Codex ì¸ê³ì ì¢ë£Â·ì¬ê°. **ë³ëì ì¤ì  ì°êµ¬ ë¤ì ê³¼ì :** source R5âR9ì ì°ê²°ë ë¤ì ë ë²ì§¸ ì ì¥ ìì fixed referenceÂ·ì A/B/CÂ·ìì°¨Â·raw photon incoming 2904ì±ë¶ì¼ë¡ whole-cell ì¸ì¦ì êµ¬ì±íë ê²; ì¤ì  native warm provider call siteê° íìíë©´ ì receiver commitìì ë¶ë¦¬ ê²ì¦. R9ë¥¼ ì ì²´ 16ì ëë ì¤ì  cold AXBI convergence ìë£ë¡ ìê¸ ê²©ìíì§ ìëë¤.
