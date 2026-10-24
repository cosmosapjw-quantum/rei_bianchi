# L1 실제 실행 결과

## 선택 단위

ELEMENTAL_HI_PW19_Z2_479_FINITE_PI_WITH_EXPLICIT_NONTHERMAL_RESERVOIR.
동결 source summary를 소비하는 proper-time, per-Href source와 fixed-moment JVP이다.

입력은 bath-frame 정지 ground-state elemental HI, z=2.479, threshold13.6eV, photon support13.6–50000eV이다. isotope-specific H1/D/T 대응을 추가하지 않는다. 채택 amplitude는1이고 target 정규화 m=aX_HI는 정확히 한 번 적용된다.

여섯 에너지 소유자 순서:
gas_thermal, binding, UV, dynamic_escape, source_reservoir, primary_nonthermal.

\[
q=m(0,B,-P,0,0,K),\qquad
Dq=\delta m(0,B,-P,0,0,K),\qquad
\delta m=a\delta X+X\delta a.
\]

입자 소유자 HI, HII, e_nt, e_th, absorbed_photon에는
m(-A,+A,+A,0,-A)
를 전달한다. 전하에 e_nt+e_th를 한 번 더하며 e_all은 별도 세 번째 pool이 아니다.

## 동결 identity

| 대상 | SHA256 |
|---|---|
| source_pair.py | ee5fb4d009945da7d4f3233f5624870095090404d015524c3abe0de3955653f4 |
| source_card.json | 1b4077f58752b2112ebdac1661d19c7942612adcf65fa5e98a41bb9bdb3707dd |
| focused_check.py | 8222a8f66bea1ecf6da1df1344a638a89c4654ae7d61e494165096ee23b5addb |
| run_focused_once.py | dd95849ac3bdbef4ac498bbaef643e006a0ba15119757f3f6dc3e18629124242 |
| raw/stdout.jsonl | 166f293d9eeb435e3b7b453b9d0f69601003f9171e71438afc5d83f1ba706809 |

원 공급자 read commit b8882d026887f375acf90768d4e3740eb03da226, original science54477b285e0c712610453bca1408a076af43521d, CASES blob61bcbc0b44206f496534da6bdffcdfe1731ad063을 재사용한다. source_card는 그 선택 row의 동일 바이트다. 이번에 source/fixture를 수정하지 않았다.

## 관측 결과

준비한 parent runner를 정확히 한 번 호출했다. 실제 child command와 환경, hashes, exit, timeout, CPU, wall은 raw/resource_receipt.json에 있다.

| 관측 | 값 |
|---|---:|
| scientific child attempts | 1 |
| fixture groups | 1 |
| return code | 0 |
| timeout | false |
| launch error | null |
| user CPU | 0.024463s |
| system CPU | 0.012183999999999999s |
| total child CPU | 0.036647s |
| launch-inclusive wall | 0.03701553899736609s |
| automatic retries | 0 |
| stderr bytes | 0 |

각 source component와 fixed-moment JVP component는 정확한 Fraction 참조의 최종 float 반올림과 일치했다. mixed cancellation 방향의 정확한 dm=2^-54가 보존되었다. HI+HII, HII−(e_nt+e_th), absorbed_photon+HII의 event accounting과 null 보존이 fixture에서 확인되었다. 지원하지 않는 redshift3은 거절되었다.

## 세 종류의 잔차를 분리한다

공급자 summary의 표현된 입력 잔차:
\[
r_B=B-\chi A
 =\frac{2526731116588545}
 {2787593149816327892691964784081045188247552},
\]
\[
r_E=B+K-P
 =\frac1{618970019642690137449562112}=2^{-89}.
\]
양수 r_E는 저장된 binary64 입력의 정확한 관계이며, 원 donor의 별도 floating residual −1.6155871338926322e−27은 원래 부호 그대로 source_card에 있다.

정확한 source/JVP 합은 각각 mr_E, δm r_E이다. fixture가 저장한 출력 component 반올림 이후의 추가 차이는 다음과 같다.

| 출력 | 정확한 component-rounding residual |
|---|---|
| source, X=3/7,a=1.0 | 1/8665580274997661924293869568 |
| JVP, dX=2/9,da=−1/5 | 257/3119608898999158292745793044480 |
| mixed cancellation, dm=2^-54 | 0/1 |

이 값들은 물리 공급자 오차 또는 열화 오차가 아니다. gross_B와 gross_E도 raw에 정확한 분수로 보존했다. B→χA, P→B+K, K→P−χA 같은 보정과 임의 소유자 residual 흡수는 수행하지 않았다.

fixture의 ledger_tolerance_acceptance는 NOT_EVALUATED_NO_FROZEN_CRITERION이다. 새 source-consistency tolerance를 결과를 본 뒤 설정하지 않았다. 고정 L0 gate2e-12는 과거 L0 범위에서 그대로 유지한다.

## 물리적 해석

q_thermal=0은 선택 NO_DEPOSITION 모델의 source 규칙이다. 공급자 physical_secondary_heat=null은 그대로 null이다. primary kinetic energy K를 실제 deposited heat로 간주하지 않는다.

이 구별은 Furlanetto–Stoever(2009/2010)의 에너지·ionized fraction 의존적 deposition 분할, Pawlik–Schaye(2010)의 excess-weighted rate와 complete-thermalization 가정과 일치한다. 본 여섯 소유자 구현 자체는 여기서 구성한 adapter이다.
https://arxiv.org/abs/0910.4410
https://arxiv.org/html/1008.1071v2

현재 결과는 instantaneous prescribed spectrum snapshot에 대한 충실한 summary 소비를 지지한다. 유한 photon energy support와 유한 radiation stock 진화는 별도다. 원자별 source 재적분, physical uncertainty certificate, nonthermal pressure state, stopping, RR, cosmological/Einstein trajectory는 이번 child의 산출물이 아니다.

독립 review와 root의 admission은 review/L1_EXECUTION_REVIEW.* 및 ADMISSION.json에서 별도로 결정한다.

## 자원 연속성

새 L1 increment는 CPU1s/wall5s, 1child만 승인되었고 한 번 사용했다. 남은 child 호출 허용량은0이다. 미사용 CPU를 다음 압력 모듈로 이전하지 않는다.

과거 L0 known measured exploration10.156695CPU초는 그대로이며, 이번 L1을 포함한 알려진 두 단위의 산술합은10.193342CPU초다. 이 합이 전체 연구 비용을 뜻하지 않는다. 기존10초 cap 초과0.110448의 FAIL, historical wholeL0 UNKNOWN_NOT_ZERO, original cumulative cap NOT_FROZEN을 보존한다. Parent/IO/model review/remote context 비용은 별도 미측정이며0으로 보고하지 않는다.

과거22/66/83전구간, ANGTHERM01/02, NCP, cosmological IVP, 과학 그림/render 재실행은 모두0이다.
