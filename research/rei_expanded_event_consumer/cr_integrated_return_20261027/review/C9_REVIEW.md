# C9 독립 code·원자료 검토

## 판정

**PASS_SCOPED_CODE_AND_RAW**. 한 번의 동결 실행이 반환한 실제 24개 대안의 conservative diagnostic projection, interface JVP, reference·clock·endpoint 대응이 동결된 수용 기준을 만족한다. 차단 finding은 0개다.

이번 검토는 코드 작성자와 다른 검토자가 수행했다. 검토자는 이론에 기여했지만 consumer/checker/runner를 구현하지 않았다. C5에서 닫은 source 검토를 재사용하고, C9에서는 실제 stdout, stderr, CHECKS, OBSERVATIONS, map table, resource receipt와 원래 CR24 source의 대응을 읽었다. Provider·consumer·checker를 재실행하거나 import하지 않았다.

최종 figure는 별도의 시각 검토에서 판정한다. 현재 판정은 physical rate/history/state update 또는 whole-network/L4 완료를 포함하지 않는다.

## 실제 실행 근거

- 한 번의 attempt01, exit0, stderr0 bytes.
- 저장된 CHECKS에는 이름이 서로 다른 5,264개 assertion이 있고 모두 자신의 원래 tolerance를 통과한다.
- OBSERVATIONS는 24개이며, 각 raw_event 객체는 원래 고정 CR export의 해당 event와 같다. Case/source 대안은 합산하지 않았다.
- 모든 실제 event의 rate, exposure, instantaneous RHS, emission history, spectrum, physical heating은 null이다. Native projection에 명시한 b=1.4e6m^-3는 consumer fixture다.
- Native25와 photon port의 false physical-update 상태, 원래 source qualification과 legacy source identity를 유지한다.

### 수치 범위

| 검사 집합 | 관측 최대 scaled residual | 동결 기준 |
|---|---:|---:|
| Source integrated energy | 1.2031443924538344e-16 | 2e-13 |
| 새 algebra/Decimal/reference/endpoint 등 FD 제외 | 1.681255923043035e-16 | 해당 새 algebra2e-14 |
| Native binding+fast+retained energy | 1.4992796638549268e-16 | 2e-14 |
| Mixed JVP 대 centered FD | 1.127517777594486e-10 | 2e-8 |

최대 FD는 `chi3_R80_N1024, z=2.316, h=2e-4, row22`에서 나왔다. 최대 non-FD 값은 `chi3_R80_N2048, z=2.649, reference tangent row22`다. 같은 analytic operand scale을 두 step에 사용했다. 두 step에서 확보한 판별을 universal convergence order나 모든 방향의 physical Jacobian 인증으로 바꾸지 않는다.

오차 scale은 row의 물리 단위를 유지한다. 예를 들어 \(\chi=1.5,R80,N2048,z=2.479\) 행의 count projection은 3.4078838351780594e-18/baryon, fast-energy projection은 -2.2607623708714063e-36J/baryon이다. 해당 FD 기준의 절대 허용량은 각각

\[
2\times10^{-8}(|A/b|+|d(A/b)|)
\simeq6.95\times10^{-26}\ {\rm baryon}^{-1},
\]

\[
2\times10^{-8}(|K/b|+|d(K/b)|)
\simeq5.43\times10^{-44}\ {\rm J/baryon}
\]

이다. 작은 입력을 무차원1로 덮는 floor는 없다. Zero 행은 정확한0을 요구한다.

## 5,264의 실제 의미

이 숫자는 독립적인5,264개 physical scenario가 아니라,24개 공급자 대안에 대한 row별·방향별·경계별 assertion 합계다.

| 근거 종류 | Assertion 수 |
|---|---:|
| Native species·binding identity | 2 |
| Decimal value / JVP | 648 / 648 |
| Exactzero rows | 504 |
| Source energy | 24 |
| 핵종·질량수·thermal count·energy·energy tangent | 144 |
| Mixed FD:24대안×2step×27행 | 1296 |
| Reference value / tangent | 144 / 144 |
| Clock identity / no-b production path | 24 / 24 |
| 제조 capacity boundary | 96 |
| Endpoint value / tangent | 648 / 648 |
| 8종 mutation signature×24대안 | 192 |
| Incompatible / negative energy derivative | 24 / 24 |
| 입력·null ownership·중복·zero 등 나머지 controls | 30 |

Decimal expected 값은 명시적인 quotient와 row mapping을 사용하며 consumer helper를 통해 생성하지 않는다. FD는 frozen code의 값 경로를 호출하는 실제 차분이다. Mutation은 count 누락, external photon 중복, 열 중복, db/dbeta 누락, H 분모, endpoint drplus 누락, logT rebase의 unit-specific 비영 signature를 구별한다.

## 선택한 실제 값과 해석

\(z=2.479,R80,N2048\)의 두 \(\chi\) 대안은 다음과 같다. 이 표의 값은 공급자 원래 proper-volume integrated 값이다.

| \(\chi\) | Capture count [m^-3] | Fast kinetic removal 크기 [Jm^-3] | Retained photon energy [Jm^-3] |
|---|---:|---:|---:|
| 1.5 | 4.771037369249283e-12 | 3.1650673192199686e-30 | 4.4763957994064925e-29 |
| 3 | 2.5685395097196222e-12 | 2.2109226306054705e-30 | 2.4606134822300983e-29 |

Retained energy는 fast kinetic loss와 binding release의 합이다. Thermal count와 selected thermal energy는 변화하지 않는다. Native w_ext로 radiation을 보내거나 조건부 mean photon energy를 단색 spectrum으로 해석하지 않는다.

Manufactured capacity에서 최대 amplitude의 active constraint는 관측한 fixture에서 fast-count capacity다. 1.01배에서는 그 margin이 음수가 되어 잘못된 후보를 구별한다. 이는 제조 fixture의 capacity 진단이며 실제 bath depletion/history의 승인으로 쓰지 않는다. Endpoint figure/data의 nonzero logT 값과 tangent는 rebase 후에도 그대로 유지된다.

## 비용과 검토 중 발견한 운영 사실

과학 실행 receipt의 비용은 child0.281091CPU s, wrapper0.045367678CPU s, tail0.05CPU s, charged0.376458678CPU s다. Wall0.305686018s, 최대 RSS12800KiB로 동결된 .75/.10/.90CPU s,8wall s,512MiB 경계 안에 있다.

C9의 저장 자료를 분류하는 metadata 읽기는0.195797414CPU s를 사용했다. O(n²) list-membership 분류 때문에 앞선 provenance 수정0.029369910, C5 metadata0.002737664, supplier refresh metadata0.001666732를 포함한 기존0.20CPU s reservation의 실제 subtotal은0.229571720CPU s이며,0.029571720CPU s 초과했다. Root에 즉시 보고했고, 초과를 그대로 보존했다. 이 비용은 과학 replay가 아니며 numerical PASS를 변경할 과학 실패도 아니다. 기존 reservation을 사후에 PASS로 고쳐 쓰지 않는다.

Root는 초과액을 별도로 계상하고, 최종 metadata를 위한 새 prospective0.25CPU s reservation을 승인했다. 이 문서/JSON 작성은 그 안의0.03CPU s 경계를 사용한다. 이미 읽은 raw scan을 반복하지 않는다. 원격·미측정 비용은 UNKNOWN_NOT_ZERO다.

## 닫힌 의무와 남은 gate

현재 코드와 실제 원자료의 범위에서 source-qualified integrated diagnostic consumer를 채택할 수 있다. 새로운 rate·history·spectrum·physical state·27-state ODE client·global error certification은 공급하지 않는다. 작업32/88, 중앙27/88, L4false, global physical completion null을 유지한다.

다음은 saved-data figure의 실제 시각 검토와 최종 source/DAG/delivery 범위 검토다. 코드·criteria의 변경이나 새 scientific run은 요구하지 않는다.

