# E13C10 독립 최종 검토

## 판정과 적용 범위

**`PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST`**로 판정한다. 고정된 captured OFF 문제의 다섯 경로, 12개 직렬 segment에 한해 새 first-integral enclosure를 채택할 근거가 충족되었다. 최종 선택은 `runs/REFINED`의 실제 결과이며, 각 경로의 17개 absolute와 17개 correction metric이 모두 기존에 채택된 E13C9 구간에 포함되고 폭이 증가하지 않는다. 합계는 **170/170**이다. 선택 경로의 가중 P 폭은 **97.7836860203087%**, H 폭은 **98.0689999175101%** 감소했다. 원래의 50% 기준을 충족한다. [E1–E3]

검토자는 후보 코드, 이론 후보, 제조해 통제 설계를 작성하지 않았다. 고정된 코드와 실제 증거를 읽고, 별도의 Fraction 기반 saved-data 감사 코드를 작성·실행했다. 후보나 과학 커널을 import하거나 새로운 coefficient/경로 계산을 호출하지 않았다. 소스 검토에서 발견한 위치와 문서 해석 문제를 전달했으며, 수정안의 생성과 구현은 owner 및 다른 contributor가 수행했다. 이 검토의 해결되지 않은 blocking finding은 **없다**.

| node | first grid N | second grid M | segment 수 | raw 포함·폭 비증가 | 최종 RESULT SHA-256 |
|---:|---:|---:|---:|---:|---|
| 1 | 1024 | 128 | 2 | 34/34 | `4ab97ac2e81594ce0d11c9386e77254a8f162e94111bce0a16c7972db4bfe590` |
| 1162 | 1024 | 256 | 2 | 34/34 | `dd43bc096ab100bd7a080427e3c0ab9ccff896a3ffc8c92f17b786c652c83f7c` |
| 1976 | 1024 | 128 | 2 | 34/34 | `b71872c709de746457fc2fc96e21dd3a0a30ee37b9290689cd33d4854415ae11` |
| 1620 | 512 | 128 | 3 | 34/34 | `8db16d5f8d7be464e2011b8c47317049b60ec20383e7f2a993c0bd684795d6f4` |
| 2344 | 512 | 128 | 3 | 34/34 | `9ae31ce74841d6105e773978eef8697cb623461013127cc78fc468fb60ef3e6e` |

모든 선택 결과의 interval precision은 P60이다. 이 결정은 E13C8의 전체 finite admission 또는 E13C9의 기존 선택 경로 admission을 소급 변경하지 않는다. E13C10 전체 모집단은 `NOT_RUN`, physical·continuum·production·receiver는 `HOLD`다.

## 수학적 근거와 구현 연결

한 original cell `[a,b]`에서 길이를 Δ, midpoint를 m이라 하면, C² 함수의 midpoint 오차는 양의 Peano kernel K에 대해 `∫f − Δ f(m) = ∫K f''`이다. 왼쪽 반구간에서 K는 `(x−a)²/2`, 오른쪽에서 `(b−x)²/2`이며 각 반구간의 kernel 질량은 정확히 `Δ³/48`이다. 따라서 새 왼쪽 반구간 derivative enclosure를 D_left, 유효한 전체 cell enclosure를 D_whole이라 할 때

`h ∫cell f ∈ h Δ f(m) + h Δ³ (D_left + D_whole)/48`

가 성립한다. D_whole은 오른쪽 반구간에서도 유효하다. 실제 source의 `h*(left_d2+d2)/(48*N**3)`가 이 식과 일치한다. 원본 Jet2의 d2는 정규화 좌표 x의 실제 두 번째 도함수다. 배율에 별도의 h²를 다시 넣지 않는다. 네 번째 도함수, Simpson의 고차 remainder, 또는 상수 곡률 가정이 필요하지 않다. [E4]

원래 midpoint 합의 enclosure는 동일 source·input·N·P·segment에 귀속되어 있다. 새 규칙은 이 이미 유효한 합을 유지하며 곡률의 부호와 범위를 더 정밀하게 보존한다. 두 pilot 경로에서는 앞서 계산한 SAME_N 결과의 whole-cell d2를 재사용하고 왼쪽 반구간만 새로 평가했다. 나머지 세 경로는 whole/left 범위를 각각 한 번 계산했다. 실패했던 경로 admission과 그 안의 유효한 derivative enclosure는 별도의 증거다. source·input·cell identity 및 포함 정리에 의거하여 후자를 재사용할 수 있다. 최종 경로 구간은 새 식에서 직접 만들어졌다.

전체 original cell은 9,216개다. 독립 감사는 각 cell의 정확한 dyadic 좌표, D_left의 D_whole 포함, 두 범위의 양의 kernel 가중 합을 Fraction으로 확인했다. 저장된 midpoint 합과 fine-grid local.bounds의 동일성, 두 pilot의 parent d2 항별 동일성도 확인했다. raw interval intersection, 이전 최종 구간으로의 fallback, clipping, 새로운 작은 오차 허용 규칙은 없다. [E1]

원본 17개 source/input lock member의 bytes와 SHA가 유지되었다. 고정 source/mask, gas interpolation, exact binary64 lift, eV 변환, species heat 정의, 양의 경로 가중치 1회 적용, signed seam과 기존 branch discrepancy를 유지한다. 기본 elementary composition의 정의역과 C² 조건은 원래 source 계약에 따른다. 이것으로 물리 계수 모델 자체의 독립적 실험 검증을 주장하지 않는다.

## 새 carry와 유한 remainder

첫 forcing 적분은 incoming correction과 무관한 동일 수학적 대상이다. 새 incoming center c에 대해 기존 gain `G_k*c`를 더하고, 현재 c에서 E13C9 prefix 및 signed second correction을 다시 계산한다. incoming radius η와 새 center를 사용하여 `S = |c| + η + B_r`를 재구성한다. D는 원래 fine-grid D_L bound다. 그때 기존 finite Volterra bound인 `(|G_k|+T_k)η + T_k D S`를 적용한다. [E1, E4]

독립 감사는 실제 outgoing 중심·반경, gain 적용, 새 S와 각 incoming/coupling/tail 항, 현재 prefix의 시작값과 cell 간 연결, source 입력과 signed energy seam, 경로 누적을 확인했다. 원본 input-dependent norm bound를 재사용했으며 예전 incoming center/radius나 old signed second integral을 새 candidate에 대입하지 않았다. 재중심화 표현은 정확한 저장 center±radius를 의미하고, 별도 출력 endpoint의 outward 표시 여유는 구분해 검토했다.

frozen·first·second 각 계층의 number/energy/species heat 식과 전역 식을 원시 항에서 직접 조립한 **205개 ledger**가 모두 0을 포함했다. 후보가 저장한 ledger Boolean만 읽어 이 결론을 내리지 않았다. 저장된 169개 ledger enclosure의 0 포함도 별도로 확인했다. [E1]

## 실제 통제와 최초 실패의 보존

| 증거 | 실제 실행과 결과 | 검토상 의미 |
|---|---|---|
| Exact polynomial control | 40개 행, 207개 확인, 실패 0 | 상수·일차·양/음 이차·부호 변화, Peano identity와 kernel mass, 다른 grid의 비포함 반례 |
| EXEC01 | 24개 manufactured integrator 호출, 2,290개 확인, 실패 0 | 원래 signed C² 규칙과 별도 P140 closed-form 17-output target |
| EXEC02_CACHED | 12개 호출, 941개 확인, 실패 0 | 동일 midpoint aggregate 보존, 96개 새 whole-cell 평가, 새 midpoint 0 |
| EXEC03_HALF_CELL | 12개 호출, 993개 확인, 실패 0 | fresh/cached parent 양쪽 branch, 48 whole+96 left 평가, midpoint 0 |
| 독립 saved-data 감사 | 첫 실행 exit 0, 413,507개 확인, 실패 0 | source·cache·cell·carry·ledger·raw admission·가중 aggregate·bound allocation의 실제 산술 확인 |

P140 oracle의 실제 별도 interval evaluator와 closed-form prefix/stock/weighted-moment 함수를 읽었다. 새 candidate integrands나 midpoint/Jet2 weights로 oracle 적분값을 만들지 않는다. 다만 exact input parameter와 Python Decimal exp primitive는 공유한다. 통제는 manufactured 수학적 문제에 대한 검증이며 물리 coefficient model을 별도로 검증한 결과가 아니다. independent audit의 assertion 수 역시 독립적인 물리 사례 수를 뜻하지 않는다. [E1, E5]

초기 N32에서는 node 1이 12/34, node 1976이 0/34만 raw nesting을 만족했다. 특히 QN/QE는 폭이 크게 감소해도 중심 이동 때문에 기존 상단 경계를 넘을 수 있었다. 이 첫 실패는 `INITIAL_N32_REVIEW.md`, 원시 결과, 첫 finding과 initial source snapshot에 남아 있다.

원래 N에서 midpoint를 재사용한 다음 pilot은 모든 폭이 감소했지만 node 1이 33/34, node 1976이 26/34에 머물렀다. source correction의 아주 작은 초과는 represented interval을 center/radius로 바꾼 뒤 발생했고, HeI의 후속 segment에는 incoming-dependent 항의 이동도 있었다. 원래 strict contract를 유지한 채 이 결과와 source snapshot을 보존했다. 후속 양의 kernel 분할은 유도와 targeted control을 갖춘 새로운 수정이었다.

최종 REFINED는 다섯 경로 모두 34/34를 충족했다. 이 비교는 original grid 선택과 kernel-range refinement의 실제 판별 증거다. N32→N1024에서 순수한 단일 quadrature 차수를 측정하거나 보편적인 N⁻³ 폭 법칙을 확인한 것으로 해석하지 않는다. 조건부 N64 실행과 나머지 coarse N32 실행은 `SUPERSEDED_NOT_RUN`으로 남는다. 추가 정밀도·해상도 sweep 없이도 현재의 포함·실용 개선 기준을 판정할 근거가 충분하다.

## 가중 폭과 남은 상계의 구조

| 선택 경로 가중량 | 채택된 E13C9 폭 | 최종 E13C10 폭 | 감소율 |
|---|---:|---:|---:|
| P | `1.83702702468600293091209453916e-22` | `4.07142867588229839073735549299e-24` | `97.7836860203087025981346276037%` |
| H, eV | `4.13086716341852351327605165585e-21` | `7.97670483331586145025232084074e-23` | `98.0689999175101306660941604406%` |

이 값들은 다섯 선택 경로의 유효 구간 폭이다. 오차의 실제 관측값이나 전체 모집단 결과를 뜻하지 않는다. 모든 가중 합과 gain fraction을 독립 Fraction 산술로 원시 경로에서 재구성했고 owner 분석과 정확히 일치했다. [E1–E3]

새 반폭을 비음수 성분으로 분해한 결과도 별도로 재구성했다. 현재 선택 경로의 분해는 다음과 같다.

| 상계 성분 | P 반폭에서 비중 | H 반폭에서 비중 |
|---|---:|---:|
| 첫 적분 curvature range와 그 carry | `1.17020581739%` | `1.16614776984%` |
| signed second-correction rectangle와 그 carry | `98.8297170695%` | `98.8338156793%` |
| finite Volterra tail | `0.0000771131081%` | `0.0000365508465%` |
| 첫 midpoint·기타 rounding | 위 성분들보다 작음 | 위 성분들보다 작음 |

각 성분은 음수가 아니며 정확한 합이 실제 반폭과 일치한다. 이는 규정된 상계의 bookkeeping이며 true error의 원인별 측정이나 유일한 분해가 아니다. 현재의 다음 국소 정밀화 문제를 선택할 때 signed rectangle 부분이 주요 근거가 된다. 본 결정은 그 후속 방법을 구현·실행·승격하지 않는다. [E2, E3]

## 실행 자원과 NCP 경계

captured path 호출은 진단 네 개를 포함하여 **9회**다. 새 first-integral coefficient 평가 18,688회와 현재 path assembly의 second-correction 평가 5,632회를 합해 **24,320회**다. 원래 완료된 전체 quadrature나 NCP batch work unit을 다시 실행하지 않았다. 동일한 incoming center를 가진 일부 low-level second-correction 계산은 새 path assembly 중 반복될 수 있으며, 이를 전체 work unit replay와 구분한다.

최대 경로 계산 시간은 **24.3628667649973초**, 경로별 경과 시간 합은 **125.589533965998초**, process CPU 시간 합은 **125.543761798초**다. 경로 계산의 최대 개별 RSS는 **173,412 KiB**다. 네 batch 영수증은 2/2/2/3 workers와 실제 child exit 0을 기록한다. 경로별 경과 시간의 합은 병렬 batch wall time과 다르며 전체 연구·전달 시간도 아니다. 같은 작업의 serial speedup, CPU 이용률, provider attestation은 설정된 제한 그대로 미확립 상태다. [E6]

독립 감사 자체는 9.517208747995초, process CPU 9.516523263초, RSS 196,068 KiB였으며 scientific kernel import와 coefficient/path invocation은 0이었다. actual child exit는 0, stderr는 비어 있다. [E1]

이 루프의 신규 NCP job은 **0**이다. 여기에서 필요한 계산은 실제로 짧은 local 작업으로 완료되었다. 앞으로 NCP 64코어/128 GB에 넘길 작업은 구체적 full-population accuracy 목표, 미실행 독립 work unit, 고정된 source/input/work lock, 측정된 비용과 병렬화 이익이 마련된 뒤 정할 수 있다. 이미 완료된 E13C7 heavy batch를 이 결과 때문에 다시 실행할 근거는 없다.

## 증거 포인터와 claim ceiling

아래 경로는 이 E13C10 package를 기준으로 한다. SHA는 bytes identity를 고정하며 수학적 타당성을 대신하지 않는다.

| ID | 파일 | SHA-256 |
|---|---|---|
| E1 | `review/independent/EXEC01_FINAL/REVIEW_RESULTS.json` | `84665d71fa85a4b2279767dbbc6deed080df91d61ff481c3e3f0be8bd51348ab` |
| E1 실행 | `review/independent/EXEC01_FINAL_COMMAND_RECEIPT.json` | `8c381751cee2466835bd0a99b306785540ac7a2278d46cbc585c879a6094f3d7` |
| E1 코드 | `review/independent/review_saved_arithmetic.py` | `8c00c5b58ad96875604c088ea0bedbf426c976c722b781b547c5015fc93f55ce` |
| E2 | `analysis/ACTUAL/LOCAL_ANALYSIS.json` | `2b1c3effa08bdf135c48f69e4d29fb4da47f284f40708e3b48a0e8814354d871` |
| E3 | `analysis/ACTUAL/BOUND_ALLOCATION.json` | `9966fa89d60ccb16502bc9782bec28722333a4a76a7379ebea7cb3c545c1418e` |
| E4 lock | `SOURCE_LOCK.json` | `dab62d573a17d5333aa09369c1865b873a2c55d77efc3a88aeef872beeef4bbb` |
| E4 계약 | `SCIENTIFIC_CONTRACT.md` | `467333ed1123008aa2e43c81016269ad14e69bf4aef0f58804dbc1dc1a761459` |
| E4 방법 | `code/first_midpoint.py` | `574e797e563820fb669a9b8e5d10cad21e598d9a64f9a3f4b79af1737c48acfa` |
| E5 | `tests/MANUFACTURED/EXEC03_HALF_CELL/CONTROL_RESULTS.json` | `0a8fcfbde1d5c5cc1bdc49511847524032364ce239d626d6990b6e277437180c` |
| E6 | `evidence/*_COMMAND_RECEIPT.json`, 각 `runs/*/node_*/START.json`, `COMPLETE.json` | 최종 결정 JSON의 evidence index 참조 |

검토상 근거 상태는 C² 포함 유도에 `derived`, exact/closed-form 및 captured 산술에 `numerically_checked`와 `implementation_verified`다. 새로운 물리 모델, 전체 모집단 개선율, continuum limit, production readiness, 실제 NCP 실행·가속에 대한 승격은 없다. 현재 scoped scientific gate는 닫혔으며 새로운 근거 또는 새 목표 없이 같은 review나 완료된 science를 반복할 필요가 없다.
