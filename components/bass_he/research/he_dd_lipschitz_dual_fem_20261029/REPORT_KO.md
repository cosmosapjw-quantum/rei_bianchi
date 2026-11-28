# BASS_HE HE-DD dual finite-element continuum bracket: 연구 및 코딩 보고서

2026-10-29 · 기준 BASS_HE PR#109 `11b3cfdb987137323d8ebd220e74063b0ed6db22` · 별도 add-only 연구 노드.

## 결론

기존 PR109의 PR105 EXFOR source-conditional nonnegative L-Lipschitz family를 그대로 보존하되, sign-split outer의 비최적성을 보완하였다. Finite-grid LP와 **exact rational post-dual** + Lipschitz continuum interpolation + midpoint-derivative quadrature + Machin/Taylor trigonometric error를 결합하여 b=⟨cos²θ⟩의 두 극값을 각각 외측·내측으로 가두었다. 단순 HiGHS 최적값은 증명으로 사용하지 않았고, 원본 source ERR-S도 joint CI로 승격하지 않았다.

| L [nb/(sr degree)] | min b bracket | max b bracket | Var(K_D) outer [MeV²] |
|---|---|---|---|
| 1/700 | [0.2800766324,0.2803338733] | [0.3794460960,0.3797024351] | [1063.89950,1442.33822] |
| 1/200 | [0.1854121068,0.1866070873] | [0.4679082819,0.4691036321] | [704.30670,1781.93773] |
| 1/100 | [0.1301587544,0.1335489820] | [0.5634911669,0.5668850720] | [494.42123,2153.37045] |

격자 h=0.02°, 4501 knots. 숫자는 표시 반올림, 실제 Fraction 원장/쌍대 잔차와 계산식은 `evidence/EXTREMA_CERT_L_*.json`, `src/lipschitz_lp_certificate.py`, `THEORY_KO.md`에 있음. Source-frozen Δ²(330)=3798.60144551709 MeV². 특히 L=1/700에서 새 형식의 b 전체 외측 [0.2800766324,0.3797024351]은 이전 PR109 numerical outer [0.279238681235,0.386397436244]보다 양끝이 강하다. 다른 L에서는 새 위쪽 경계가 강하지만 아래쪽 경계가 모두 강하다고 과장하지 않는다.

## 수학적·수치적 자격

- T1: nodal Lipschitz finite-element subset와 원래 연속 f 사이의 O(Lh) 직접 부등식.
- T2: sin(z)cos²(z)=¼(sin z+sin 3z), degree-trigonometric second-derivative envelope, rational Taylor/Machin/Decimal enclosure.
- T3: numerical LP dual candidate를 exact Fraction으로 재구성하여 A^T dual 오차를 양의 부분으로 보정하는 우변 증명.
- T4: raw LP primal을 rational McShane L-hull과 EXFOR f±에 clamp하여 실제 feasible witness를 구성; certified quadrature interval로 extrema 내측 증명.
- 실제 테스트: Python3.13.5 17/17 PASS; SciPy HiGHS only proposal; Wolfram exact identities {0,0,0}; 차원·정규화·소스조건 검사. 이전 완료된 IVP/science suite 재실행 없음. Native distinct-author R6/C9는 현 기능에 없음(NOT_RUN). Numerics produced inside this current turn; exact Fraction certificate objects are preserved.

## 실험·물리적 한계

Arends1976과 Silverman1984의 원문 detector efficiency/acceptance, coincidence와 event/particle DA 정의, beam polarization, same-s measured inverse numerical DA는 수용되지 않았다. Source 330 MeV photon history/target proper frame, 실제 σ_event, nonthermal D_fast stopping/redistribution/deposition, C_V도 없다. 1/700, 1/200, 1/100은 실험적 각도-L 측정이 아니라 임의 선언한 함수족이다. Constant κ는 normalized b에서 소거되나 angular-dependent detector acceptance는 소거되지 않는다. 이 결과는 **수학적 조건부 바운드**이지 측정된 variance, 물질 가열 또는 event rate가 아니다.

`kappa=null`, `R_event=null`, `heat_rate=null`, `physical_activation=false`, `L4=false`, `production=HOLD`.

## DAG 및 작업 게이트

Central 28/88, HE14/18, PR105 2/2, PR106 1/2, reciprocity 1/2, birth ledger 1/2, PR109 angular 1/2 모두 변동 없음. 신규 mathematical dual-FE 국소 1/2 (scoped certificate only), 물리 증분 0. 연구 R1–R5,R7–R10은 완료 9/10이며 R6 독립 비저자 심사 미완료; 코딩 C1–C8,C10 완료 9/10, C9 독립 비저자 심사 미완료. 각 단계의 실제 Git SHA와 Drive/Dropbox ACK는 `STAGE_LEDGER.json`, 최종 원격 결과는 `DELIVERY_RECEIPT.md`가 SSOT이다.

## 후속 물리 단계

새 규칙을 생산 rate로 붙이지 말고 먼저 Arends/Silverman 원전의 detector/polarization source semantics를 확보한다. 같은 불변량의 measured inverse DA와 330-MeV exclusive event σ를 결속한 다음 고에너지 photon phase-space/He target frame, D_fast stopping/deposition/C_V를 source-qualify한다. 별개 이론 확장은 exact continuum optimal-control solution 또는 더 좁은 interval adaptive FE; 이번 노드의 물리 gate를 열었다는 주장은 하지 않는다.
