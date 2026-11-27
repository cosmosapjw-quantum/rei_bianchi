# MOVING_GAS_STAGE_05 구현 계약

Unit: HERE_RUX03_MOVING_GAS_SOURCE_05. 작성 상태: **author_complete_pending_independent_decision**. Independent adoption: see review/DECISION.md.

이 문서는 현재 저자 유도를 다음 CODING 단위로 연결한다. 독립 최종 채택은 별도 review/DECISION.md의 판정으로 확정한다. 이 계약 작성에서 native build, chemical RHS, ODE 또는 새 과학 계산을 실행하지 않았다.

주 근거는 [moving-source 유도](../derivations/MOVING_SOURCE_AND_THERMAL_BALANCE.md)의 S1–S31, [primitive/fixture 유도](../derivations/PRIMITIVE_RECOVERY_AND_EXAMPLES.md)의 P1–P56, [primitive 실행 결과](../derivations/PRIMITIVE_RESULTS.json), [현재 source map](../source_map/SOURCE_MAP.md)이다. 아래 S/P 번호는 이 두 유도의 식 번호다.

## 1. 구현 단위와 기존 경로

새 구현 단위는 **HERE_RUX03_MOVING_GAS_STAGE_05**다. 고정 local Eulerian tetrad와 고정 lab 체적의 homogeneous source substep에서 한 common gas velocity가 변한다. 이 substep 동안 lab photon energy와 방향을 고정한다. Geometry·공간 수송은 기존 바깥 substep이 소유한다.

선행 CODING 의무인 **HERE_RUX03_PRIMARY_PROVIDER_03**와 **HERE_RUX03_COVARIANT_MOMENTS_04**는 pending이다. 실제 production 연결은 이들의 공통 event provider와 angular/momentum ledger를 재사용한다. 현재 source-bound conditional 구현은 PR114 commit a5c958c414dea41216b445c05f58df837f05cacb이며 gas velocity나 conservative gas momentum state를 아직 갖지 않는다.

권장 새 API의 역할은 다음 네 가지다. 이름은 구현 시 확정할 제안이다.

| 역할 | 입출력 계약 |
|---|---|
| recover_moving_primitive | D, composition, gas E와 M → 유일 primitive, scalar bracket, root/domain diagnostics |
| evaluate_moving_endpoint | 같은 candidate Y → primitive, eliminated photons, owned events, escape, 7변수 residual과 ledger |
| try_moving_source_step | old state와 h → 검증된 endpoint 또는 원인별 실패; 성공한 endpoint만 호출자 상태에 반영 |
| adapt_axisymmetric_source | 고정 reference-volume 데이터 → Eulerian photon/source 입력; axial ring 또는 resolved-azimuth 표현을 명시 |

이는 제안 인터페이스이며 현재 source에 이미 존재하는 API 목록이 아니다.

## 2. 변수·단위·불변 입력

Signature는 (-,+,+,+), x⁰=ct다. 구현 내부에서 아래 단위를 섞지 않는다.

| 기호 | 저장 의미와 단위 |
|---|---|
| D | 고정 Eulerian H 핵수 밀도, cm⁻³; D=γ n_H |
| f | n_He/n_H, 고정 무차원 핵수 비 |
| ζ | (x, f a, f b), 무차원; a=x_HeII, b=x_HeIII |
| E | rest+binding+thermal+bulk를 포함한 gas lab energy density, erg cm⁻³ |
| M | c×physical gas momentum density의 3성분, 각각 erg cm⁻³ |
| β, γ | v/c와 Lorentz factor; gas proper density는 n_H=D/γ |
| w, B | thermal 및 binding energy, eV per H |
| E_q, ε E_q | photon lab energy, 각각 eV와 erg |
| N_q, S_q | weights를 포함한 lab photon density와 lab-time source, cm⁻³ 및 cm⁻³ s⁻¹ |
| h | lab source timestep, s |
| Q′_esc, Q′_th | proper gas-frame power, erg cm⁻³ s⁻¹ |

비선형 unknown은 정확히 7개인 \(Y=(\zeta_1,\zeta_2,\zeta_3,E,M_x,M_y,M_z)\)다. Photon nodes는 제거하고, w와 β는 primitive recovery에서 구한다.

\[
e=\zeta_1+\zeta_2+2\zeta_3,\quad d=1+f+e,\quad
B=\chi_0\zeta_1+\chi_1\zeta_2+(\chi_1+\chi_2)\zeta_3,
\]
\[
r=m_{\rm ref}c^2+\epsilon B,\qquad
\rho=n_H(r+\epsilon w),\quad p=\frac23n_H\epsilon w,\quad
T=\frac{2\epsilon w}{3k_Bd}.
\]

중성 원자 reference mass m_ref는 bound electrons를 포함한다. 별도 free-electron rest mass를 다시 더하지 않는다. 매 candidate의 r, d, n_H, n_He=f n_H, n_e=e n_H를 함께 갱신한다. 배열 ζ와 primitive fixture §7의 scalar rapidity parameter는 코드 이름을 구별한다.

## 3. Positive-gap primitive inverse

각 candidate composition에서 \(a_r=Dr>0\), \(s=M\cdot M\), \(E_0=\sqrt{a_r^2+s}\)를 만든다. 양의 thermal primitive의 정확한 조건은

\[
\delta_E=E-E_0>0.
\]

Cold equality는 algebraic EOS 경계이며 warm FT03 입력이 아니다. E₀는 공통 energy-density scale과 hypot 계열 계산으로 평가한다. θ, γ 또는 pressure를 임의로 clipping해서 admissibility를 만들지 않는다.

Root unknown은 \(z_{\rm th}=C-a_r=\frac53D\epsilon w\)다. \(W=\sqrt{(a_r+z_{\rm th})^2+s}\)에서

\[
g(z)=\frac{z(6a_r+z)}{5(W+E_0)}
+\frac{2z^2(a_r+z)(2a_r+z)}{5W(W+E_0)^2}
=\delta_E,
\]
\[
\frac53\delta_E\le z_*\le\frac{5E_0}{3a_r}\delta_E,\qquad
\frac{3a_r}{5E_0}\le g'(z)\le\frac35.
\]

P16–P19의 양의 항 식과 deterministic bracket을 그대로 사용한다. Safeguarded Newton을 bracket 내부에서 수행하거나 bisection을 사용한다. Residual/interval 폭과 P18의 derivative lower bound를 연결해 root 오차를 보고한다. M=0에서는 \(z_*=5(E-a_r)/3\)인 닫힌 극한을 처리한다.

회복식은

\[
C=a_r+z,\quad \gamma=W/C,\quad \beta=M/W,\quad n_H=DC/W,
\quad w=\frac{3z}{5D\epsilon},\quad p=\frac{2Cz}{5W}.
\]

이미 구한 z를 사용해 thermal energy를 평가한다. 큰 C에서 a_r를 다시 빼는 계산을 반복하지 않는다. 선택적으로 \(u_{\rm sp}=M/C\), \(\gamma=\sqrt{1+|u_{\rm sp}|^2}\)를 사용하되 같은 normalized state를 반환한다.

Warm domain은 별도로 검사한다. 현재 composition에서

\[
\theta_{\min,\max}=\tfrac32k_BdT_{\min,\max},\qquad
z_{\min,\max}=\tfrac53D\theta_{\min,\max}
\]

를 만들면 P13은 \(g(z_{\min})\le\delta_E\le g(z_{\max})\)와 동치다. T_min=30000 K, T_max=110000 K를 유지한다. 로컬 branch 정리에 사용할 box는 이 부등식의 strict interior다.

Inverse derivative/JVP에는 P21을 사용하거나 그 식과 일치하는 AD를 사용한다. M=0에서 |M|로 나누지 않고 s=M·M로 미분한다. ζ 변화에 따른 \(a_r=D r(\zeta)\)와 d의 변화도 chain rule에 포함한다.

## 4. 한 endpoint의 실행 순서

각 residual 평가에서 하나의 immutable candidate evaluation을 구성한다.

1. Composition simplex, D와 r, conservative gap을 검사하고 primitive를 회복한다.
2. 모든 proper collider/absorber density와 T를 그 primitive에서 계산한다.
3. 각 directional photon의 Doppler factor, energy, opacity를 계산한다.
4. Photon unknown을 S10으로 제거하고 species별 integrated absorption을 만든다.
5. 같은 T·proper densities에서 공통 provider의 CI/RR/두 DR, captured kinetic powers를 평가한다.
6. Owned event bundle에서 chemistry, escape, rest heat 및 lab energy/momentum source를 함께 만든다.
7. 7변수 residual과 독립적으로 기록할 photon/species/energy/momentum/thermal ledger를 반환한다.
8. Solver가 endpoint를 수용한 뒤에만 photon state와 escape accumulators를 반영한다.

Photon 방향 \(e_q\)는 unit 3-vector다. Lower abundances per H는

\[
y=(1-\zeta_1,\;f-\zeta_2-\zeta_3,\;\zeta_2).
\]

\[
\delta_q=\gamma(1-\beta\cdot e_q),\quad E'_q=\delta_q E_q,\quad
N'_q=\delta_q N_q,
\]
\[
\lambda_{iq}
=cD y_i(1-\beta\cdot e_q)\sigma_i(E'_q),\qquad
N_q^+=\frac{N_q^-+hS_q}{1+h\sum_i\lambda_{iq}},
\quad A_{iq}=h\lambda_{iq}N_q^+.
\]

Shifted energy와 상대 유입 factor \(1-\beta\cdot e_q\)를 모두 사용한다. 모든 실제 atomic evaluation에 \(0\le E'_q\le50000\) eV를 적용한다. Fit cutoff (13.60,24.59,54.42)eV와 binding/heat χ=(13.598434599702,24.587389011,54.41776)eV는 구별한다. Photon numerator와 denominator는 nonnegative/positive 조건을 명시해 overflow와 잘못된 source 값을 판별한다.

CI/RR/DR의 proper rates \(R'_c\)는 같은 endpoint에서 평가한다. Integrated events는 \(A_c=hR'_c\)다. 이는 invariant four-volume normalization이므로 lab event increment에 γ를 한 번 더 곱하거나 나누지 않는다.

\[
D\Delta\zeta=\sum_c\nu_cA_c.
\]

Ionization stoichiometry는 H: (1,0,0), HeI: (0,1,0), HeII: (0,-1,1)이며 reverse reactions는 반대 부호다. Two DR terms는 모두 HeII→HeI다. 원래 fraction 형식으로 반환할 때 a=ζ₂/f, b=ζ₃/f를 사용한다.

## 5. Conservative source residual와 escape

\(Q'_{\rm esc}\)는 기존 RR/DR의 binding+captured kinetic power다. \(L=hQ'_{\rm esc}\)로 두고 gas-frame isotropic Case A escape의 lab increments를

\[
\Delta E_{\rm esc}=\gamma_+L,\qquad
\Delta M_{\rm esc}=\gamma_+L\beta_+
\]

로 기록한다. 현재 scalar escape counter에 없는 scaled momentum accumulator를 새 출력에 명시한다. Escaped photon number/spectrum을 이 energy moment로부터 만들어내지 않는다.

Gas residual은 다음 식이다.

\[
r_\zeta=\Delta\zeta-D^{-1}\sum_c\nu_cA_c,
\]
\[
r_E=\Delta E-\sum_{iq}\epsilon E_q A_{iq}+\gamma_+L,
\]
\[
r_M=\Delta M-\sum_{iq}\epsilon E_q A_{iq}e_q+\gamma_+L\beta_+.
\]

CI binding transfer는 r(ζ)의 변화에 포함된다. CI energy를 gas total energy source에 별도로 다시 더하지 않는다. Photo momentum에는 full lab photon energy를 사용하고, rest photoheat에는 \(\epsilon(E'_q-\chi_i)\)를 사용한다.

외부 source \(S_q\)는 lab number density per lab time이며 photon caller가 소유한다. 그 source가 Y에 의존하는 확장에서는 numerator와 source Jacobian까지 같은 stage에서 평가해야 한다. 선택된 fixed input source는 그대로 유지한다.

## 6. 로컬 full-channel solve

Photon elimination 뒤

\[
F(Y,h)=Y-Y_- -h\mathcal S_h(Y)=0,\qquad
D_YF(Y_-,0)=I.
\]

Strict simplex, positive primitive cone, strict warm domain, active Doppler energies의 strict allowed range 및 piecewise cutoff로부터의 여유가 로컬 정리의 가정이다. 이 neighborhood의 provider/source는 C¹이어야 한다. Primitive inverse가 전역 유일하다는 결과와 full rate-dependent source endpoint의 로컬 branch 결과는 서로 다른 계약이다.

고정 positive coordinate scales \(S_Y=\mathrm{diag}(1,f,f,s_E,s_M,s_M,s_M)\)와 dimensionless norm을 solver 입력에 기록한다. Chosen convex physical ball에서 actual bounds M₀,L₀를 확보하면

\[
hM_0\le r,\quad hL_0<1
\]

인 범위에서 \(Y_{k+1}=Y_-+h\mathcal S_h(Y_k)\)가 S21의 오차 bound를 갖는다. 다른 damped Newton/trust-region 구현도 같은 residual과 domain을 사용하고, h=0에서 이어지는 로컬 branch를 추적한다. 자동 step reduction은 구체적인 domain/iteration 진단에 근거해야 한다.

수치 M₀,L₀나 positive certified h는 현재 문서의 실행 결과로 제공되지 않았다. Future JVP는 primitive inverse → Doppler/atomic rates → eliminated photons → event residual의 전체 chain을 포함한다. Frozen initial opacities로 endpoint Jacobian을 대체하지 않는다.

## 7. Finite thermal correction

w는 primitive output이다. Seven-equation conservative solve의 equivalent thermal diagnostic으로 S26–S28을 평가한다.

\[
\gamma_{\rm rel}=\gamma_+\gamma_-(1-\beta_+\cdot\beta_-),
\]
\[
\mathcal K_\gamma=D\left[
(r_-+\tfrac53\epsilon w_-)(\gamma_{\rm rel}-1)
-\tfrac23\epsilon w_-\left(\frac{\gamma_+}{\gamma_-}-1\right)\right],
\]
\[
D\epsilon\Delta w=hQ'_{\rm th}+\mathcal K_\gamma
=\frac{hD\epsilon}{\gamma_+}Q_{\rm th}^{(H)}+\mathcal K_\gamma.
\]

Old r,w and both endpoint velocities occur exactly as displayed. The same event ledger supplies \(Q'_{\rm th}\), including current E′ photoheat, CI threshold transfer, RR kinetic losses and both DR kinetic losses. Thermal projection is checked alongside the conservative equations; it does not add an eighth independent equation to Y.

For a stationary matched pair, Kγ=0. For changing velocity it is evaluated without dropping its finite terms or presuming its sign. The continuous limit includes \(-\frac23w\,\partial_t\log\gamma\). The fixed Eulerian volume therefore does not imply zero gas pressure work. Isotropic gas-frame heating alone also does not justify fixing lab β.

Kγ belongs to the velocity-changing source step. The inherited Bianchi expansion/shear work remains in the geometry substep; those terms are not added again to this fixed-volume source residual.

## 8. Angular/reference adapters

For the retained representation, fix the substep geometry and convert \(N_q=N_{{\rm ref},q}/V_0\), \(S_q=S_{{\rm ref},q}/V_0\), \(V_0=a_{\rm rel}^3\). Map the resulting counts back with the same V₀. Supply lab-normalized external source and explicitly identify the tetrad. An old rest state starts with D=n_H; a supplied moving state starts with D=γ n_H.

For arbitrary directional nodes, use actual unit directions. For an azimuth-averaged ring:

- Axial β gives δ=γ(1−β_z μ), independent of φ. The inherited positive ring weight and correct first/second moments may be retained.
- Transverse β requires resolved positive φ quadrature or the integral of the pointwise update \(N_+(\phi)=[N_-(\phi)+hS(\phi)]/[1+h\Lambda(\phi)]\).
- Evaluate σ at each actual E′(φ), and then integrate photon counts and lab energy/momentum. Normalize positive azimuth weights to the original ring measure.
- A ring mean direction is not an individual unit photon direction. Applying a single opacity or nonlinear denominator to an average direction does not implement S31.

A finite resolved-φ calculation records its quadrature and refinement evidence separately from the exact angular-integral construction.

## 9. Ledger residual normalization and returned evidence

Return unscaled physical residuals and scaled residuals together. Use the actual terms in each balance, so a large unchanged rest-energy baseline does not dilute a source defect.

For a balance \(\sum_k t_k=0\), define
\[
R(t)=\frac{|\sum_k t_k|}{\sum_k|t_k|}
\]
when the denominator is positive, and R=0 when all its terms are exactly zero. A numerical implementation may additionally use a documented fixed absolute scale, chosen before the run; record it and the tolerance with the result. Compensated sums are appropriate for signed channels and angular pairs.

| Balance | Physical residual / terms to normalize |
|---|---|
| Photon q | \(N_q^+-N_q^- -hS_q+\sum_iA_{iq}\) |
| Chemistry component j | \(D\Delta\zeta_j-\sum_c\nu_{cj}A_c\); scale individual channel contributions |
| Gas E and each M component | r_E and r_M above, using actual absorption and escape increments |
| Total lab energy | \(\Delta E+\sum_q\epsilon E_q\Delta N_q+\Delta E_{\rm esc}-h\sum_q\epsilon E_qS_q\) |
| Total scaled momentum | \(\Delta M+\sum_q\epsilon E_q\Delta N_qe_q+\Delta M_{\rm esc}-h\sum_q\epsilon E_qS_qe_q\) |
| Thermal projection | \(D\epsilon\Delta w-hQ'_{\rm th}-K_\gamma\) |
| Primitive/domain | EOS forward residuals, D−γn_H, u·u+1, primitive bracket/error, warm and E′ margins |

Use the increment as one normalization term. For photon q the scale is \(|\Delta N_q|+hS_q+\sum_iA_{iq}\), not the sum of the two large endpoint inventories; for chemistry j it is \(D|\Delta\zeta_j|+\sum_c|\nu_{cj}A_c|\). Preserve or accurately reconstruct increments when direct endpoint subtraction loses them.

Zero-momentum fixtures normalize against the sum of the absolute directional contributions, rather than dividing by a net momentum that cancels. Compute a direct endpoint/EOS ledger as well as the event-assembled balance, so an internal bookkeeping identity is not the only check.

The existing project acceptance tolerances remain identifiable. New primitive/7D solver tolerances and precision choices must be specified before numerical execution; this theory contract does not manufacture a passing numerical threshold. Diagnostics must identify actual inputs, source/provider commit, precision, solver method, h, branch/domain margins, event counts, residual scales and actual exit state.

## 10. Cancellation and failure classification

Two distinct cancellation issues require explicit handling.

1. E and E₀ may have been rounded to the same value while the physical thermal gap is small. P16 stabilizes evaluation of g, but it cannot restore lost conservative input information. Preserve higher-precision/compensated input or establish an outward-bounded gap before deciding its sign. An unresolved gap remains a numerical/input-domain diagnostic.
2. γ_rel−1, γ₊/γ₋−1, direct ΔE/ΔN, and Kγ can be much smaller than the quantities being subtracted. Use a precision/error budget that resolves the requested correction, preserve both velocity states and the event increments, and compare to exact or higher-precision fixtures. A rounded zero is not evidence that the finite correction vanishes.

Separate a proven out-of-domain candidate, unresolved floating-point sign, overflow, solver nonconvergence, provider cutoff crossing and missing angular resolution. Do not extrapolate FT03/Verner fits or alter the incoming state to erase such a diagnostic. A cold algebraic inverse test does not invoke the warm provider.

## 11. Discriminating implementation sequence

These are future CODING checks, not executions completed by this dossier.

| Step | Fixture or path | Required distinction |
|---|---|---|
| 1 | Primitive forward→inverse data in the exact cone, including M=0 and near-gap data | Unique root/bracket, EOS, D=γn_H, domain and sign-resolution behavior |
| 2 | h=0 and rest-frame source adapter | Exact identity step; old scalar normalization and photon elimination recovered |
| 3 | Isolated 23 eV HI single beam, P33–P49 | Nonzero recoil, current proper-density dilution, changed binding/electron count, endpoint opacity and full energy/momentum |
| 4 | Isolated equal opposite 23 eV beams, P50–P53 | Zero M, Kγ=0 and exact warm weighted-average temperature |
| 5 | Small pair imbalance / resolved directions | Smooth M→0 limit and correct even thermal response |
| 6 | Same endpoint with CI/RR/two DR/photo all present | Actual full seven-variable local branch and escape/thermal ledger; retain nonzero native channels |
| 7 | Axial ring against its resolved-φ counterpart; transverse resolved-φ input | Correct ring measure/moments and Doppler-dependent nonlinear update |
| 8 | Domain and finite Kγ discriminants | Transformed energy guard, separate binding thresholds, nonzero correction resolved at declared precision |

For the isolated single-beam fixture, rename the scalar rapidity parameter to q_rap in code. Use the exact rational endpoint P38–P39 with \(1<q_{\rm rap}<23/13.60\), and intersect its explicit warm/simplex inequalities P44. Given h>0 and the actual endpoint λ>0, construct \(N^-=D\xi(1+h\lambda)/(h\lambda)\), \(N^+=D\xi/(h\lambda)\). This makes the specified event \(D\xi\) an exact BE reference.

For the isolated pair use Dξ/2 per direction. The temperature reference is
\[
T_+=\frac{d_0T_0+T_{\rm exc}\xi}{d_0+\xi},\quad T_0=50000\,{\rm K},
\quad T_{\rm exc}=72733.757372464264931\ldots\,{\rm K}.
\]
The exact rational constants are in PRIMITIVE_RESULTS.json. CI/RR/DR have zero integrated increments only in these explicitly isolated fixtures. The adopted full FT03 Case A path keeps them active. These analytical fixtures do not replace the retained production initial condition.

## 12. Completion and next obligations

MOVING_GAS_STAGE_05 is complete only when the selected source implements the common conservative stage and actual path evidence shows primitive recovery, photon elimination, current-stage provider ownership, escape energy/momentum, finite Kγ, domain handling and angular adapters working together. State, source and input identity must bind the executable checks. The current THEORY05 author evidence does not supply those future native results.

The next THEORY unit is proposed as **HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06**: on an explicit physical box, derive/evaluate quantitative M₀,L₀ or residual-Jacobian bounds, a certified positive step interval and continuation rules up to warm, photon-cutoff, simplex or primitive-cone boundaries. Identify branch boundary or invertibility loss from actual bounds. This theorem task can proceed from the accepted equations independently of completion of a production implementation.

The original owner DAG \(RUX02+RUX03\to RUX04\to RUX05\) and owner completion status remain unchanged. The separate all-Bianchi abundance-source/relative-species-tilt D2.3 work is outside this contract.

## 13. Preparation provenance

These are the actual author inputs read for this contract; the independent final decision remains pending.

| Input | SHA256 |
|---|---|
| MOVING_SOURCE_AND_THERMAL_BALANCE.md | b7b7200c31d261348f867444c58ef0c5ce1fbcc750f6ca9fb0b0a7febc673820 |
| PRIMITIVE_RECOVERY_AND_EXAMPLES.md | 78572d6417ca22f67efd0563aa248877c865b29e474ccf0de8df6db633e3dbe5 |
| PRIMITIVE_RESULTS.json | a01a4dc62c0c09613ef4f46a3fce69641050e80684553ccf08390ff4e7eaccc2 |
| SOURCE_MAP.md | 214e2f5072acf63792a1514650fd49aae9cd2b336d504086dafae8cd9d7c6775 |

The primitive author reports one actual Wolfram call and 18 passing named groups. Unit-wide symbolic accounting belongs to the final execution registry and deduplicates shared identities. Native/RHS/ODE counts from this contract preparation are all zero.
