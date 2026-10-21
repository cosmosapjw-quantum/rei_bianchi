# 2026-10-19 연구 갱신: 정확한 subnormal pair 탐색과 age32 수동적 진단

## 결론과 연구 범위

이번 intake의 실제 PR199 HEAD는 `ee3b6c8014bcb21e6d4c9ef3a3560dc40df61309`였다. 최신 Drive·Dropbox 목록을 읽고 B1 NCP 결과 ZIP과 B2 배송 ZIP을 양쪽에서 각각 전체 다운로드했다. 네 readback의 SHA256·크기·ZIP CRC가 모두 일치했다. B1의 161개 payload와 실행 receipt의 131개 output hash도 검증했다. 따라서 이미 완료된 q0 age64 block-max와 spectral128 실행을 새 캠페인으로 반복하지 않았다.

완료된 age64 block-max는 photon normalized 2.002711130429069e-10, energy normalized 1.929660553608937e-13으로 기존 1e-8 gate를 통과한다. 이것은 단일 사례의 보존 검사 결과다. age32→64 수렴성, nonlinear Grackle의 전역 응답 상계, RMS dimension dilution의 인과 판정은 여전히 성립하지 않는다. 기존 block-max 결과에 birth snapshot이 없다는 이유만으로 age64를 다시 실행하지 않는다.

이번에 완료한 것은 (1) 정확 입력 디렉터리 준비, (2) 잃었던 energy 실패 셀 원자료 회복, (3) 고정 노드·양의 지지 안에서 count와 저장 energy를 동시에 검사하는 정수 pair 탐색, (4) 같은 계산 소스의 age32 실행·비교 및 수동적 진단, (5) 작은 실제 native off/on 대조다. 다음 NCP READY는 **단일 q0 age32 block-max reference, 진단 ON**이다. native time8/16/32 정확도는 HOLD다.

## 1. 새 증거와 기존 결과의 재사용

| 결과 | 현재 판정 |
|---|---|
| NCP q0 age64 block-max | 기존 완료를 재사용: exit0, 19,756 RHS, case 782.730985318005 s, 48 transport threads |
| q+0.1 age8 transport64→128 | 기존 완료를 재사용: He I 누적 photoevent 차이 0.2660778682%; 유한 이웃 목표만 충족 |
| 기존 RMS q0 age64 | 기존 실패 유지: photon 1.0081783527976493e-8 > 1e-8 |
| 기존 age64 관측 | 18개 기록, 9개 고유 상태. 실제 birth paired snapshots는 MISSING_DATA |
| 새 NCP 실행 | 이 대화에서는 NOT_RUN. 실제 원격 도구 호출이 월 사용량 중지 응답을 반환했으며 재접속 반복 안 함 |
| 샌드박스 native | Rust 1.94.1 실제 컴파일 및 아래의 명시적 짧은 실행 완료 |

현재 compiler와 네트워크를 실제로 확인했다. 과거 compiler 부재와 백업 다운로드 실패는 이번 blocker로 상속하지 않았다. NCP 원격 명령은 도구의 사용량 중지 응답 전에 실행되지 않았다. 이 사유는 과거 NCP 성공 기록과 구분한다.

원자료: `evidence/fresh_intake_20261019/`, `evidence/ncp_blockmax_20261019T084150Z/`.

## 2. 저장 수치의 정수 격자와 구성적 보정

최소 양의 binary64 subnormal을 \(\eta=2^{-1074}\)라 쓰면, 저장 가중치는 \(z_i=t_i\eta\)이고 \(t_i\)는 비음 정수다. 이번 opt-in 수정은 원래 moment 검사가 실패한 분기에만 들어간다. 정상·원래 통과한 입력, 원래 노드 \(q_i\), source schedule, rtol/atol, 원래 count/energy 허용식을 유지한다.

먼저 기존 first-largest count helper로 정확한 count base를 만든다. 그 뒤 donor \(a\)에서 receiver \(b\)로 \(k\eta\)를 옮긴다:

\[
t_a'=t_a-k,\qquad t_b'=t_b+k,\qquad 1\le k\le t_a-1.
\]

기존 양의 가중치를 양수로, 기존 0을 0으로 유지한다. count base로부터의 \(L^1\) 변화는 \(2k\eta\)다. 비영 총량 보존 정수 변화는 \(L^1\ge2\eta\)이므로 k=1 성공은 이 범위에서 전역 최소다. k>1 결과는 **고정 count base에서 단일 pair를 쓰는 최소 k**만 의미한다. 여러 pair와 다른 count base까지 포함한 전역 최적화는 아니다.

### 정확한 유한 필요 구간

양의 가중치 수가 m, 총량이 \(T=\sum_i t_i\)일 때

\[
q_{\max}T+\frac m2<2^{52}
\]

이면 개별 에너지 곱과 양의 누적합이 subnormal 정수 격자에 남는다. 원래 Kahan energy는 이 영역에서 정확히

\[
E=\sum_i \operatorname{round}_{\mathrm{even}}(q_it_i)
\]

quantum이다. 두 변경 항을 뺀 정수합을 C, 목표 energy tick을 U, 원래 energy 허용치를 \(\tau\) tick이라 쓰면 모든 성공 후보는

\[
|C+q_at_a+q_bt_b+k(q_b-q_a)-U|\le\tau+1
\]

을 만족해야 한다. 두 곱의 ties-to-even 반올림 오차 절댓값 합이 1 이하이기 때문이다. 이 선형 구간을 양의 지지·저장 용량 구간과 교차한다.

구현은 binary64 bit에서 공통 dyadic 분모를 정확히 만들고 checked i128 연산을 사용한다. 양·음 기울기와 같은 q를 모두 다룬다. heap의 (k, donor, receiver) 순서로 후보를 평가하며 실제 원래 Kahan count/energy 검사를 다시 통과해야만 채택한다. 기울기 부호만으로 방향을 버리지 않는다.

65,536회 candidate evaluation은 고정된 계산 자원 예산이다. 물리 허용치가 아니다. 예산 소진, 표현 범위 미지원, 완전한 단일 pair 탐색의 실패를 서로 다른 상태로 남긴다. 앞 두 상태를 수학적 비존재로 해석하지 않는다.

### 실제 셀과 실행

| 단계 | 저장 셀 또는 실행 결과 |
|---|---|
| N2 원자료 회복 | 동일 count-only 코드를 한 번 실행하여 잃었던 128-node 벡터를 회복. exit1, 6.3377 s. count 0/tol0, energy -2η/tol1η |
| N3 k=1 교정 | N2 셀: donor24→receiver0, k=1, energy -2η→-1η, L1=2η. 한 번의 변경된 time8은 다음 셀에서 exit1, 7.0382 s |
| N3 새 실패 셀 | count -1η, energy -15η, 두 허용치 0. count base 후 energy +2η. donor0→receiver14, k=3이면 두 원래 gate 정확히 통과 |
| N4 정확 구간 탐색 | compiled Rust와 독립 Fraction 일치: N2 k1, 625 evaluations; N3 k3, 164 evaluations |
| N4 실제 time8 | Rust build exit0, 9.001 s. 단일 time8 exit1, 22.150563978 s. 120 s cap 또는 탐색 예산에 걸린 것이 아님 |

N3 k3 결과의 L1은 count base에서 6η, 최초 벡터에서 7η다. N2 k1의 실제 선형 energy 변화는 약 0.14900032258072216η이다. 저장 에너지 변화가 1η인 것과 구분한다.

N4가 만난 다음 셀은 n=10η, u=245η, 16개 노드 중 양의 가중치 10개와 0인 가중치 6개다. count 오차/허용치=0/0, energy 오차/허용치=1η/0이다. 양의 항의 저장 에너지는 (22+23+23+24+24+25+26+26+26+27)η=246η다. 기존 양의 지지를 유지하는 정확 count 벡터는 모든 양의 가중치가 1η인 **유일한 벡터**다. 따라서 이 제한 아래서는 여러 pair를 허용해도 저장 energy를 바꿀 수 없다. 모든 16개 노드에 엄격한 양수를 주는 것도 총량 10η 때문에 불가능하다. 이는 저장된 해당 셀과 현재 표현 제약에 대한 명제이며, 다른 표현·지지·노드 또는 연속 실수 가중치의 비존재 정리가 아니다.

N4에서 추가 repair나 같은 실행을 반복하지 않았다. 다음 native 연구는 이 표현 제약을 명시적으로 바꾸는 정당화가 먼저 필요하다. 현재 코드는 원래 오류를 유지한다.

원자료·실행기 snapshot·완전한 node bits: `evidence/native_count_energy_20261019/`, `evidence/native_pair_search_20261019/`. 증명·독립 review: `evidence/exact_pair_theory_20261019/`.

## 3. 응답 정확도에서 이 결과가 의미하는 범위

고정된 선형 응답 계수 \(K_i\)에 대해서는 pair 보정의 응답 변화가

\[
\Delta R=k\eta(K_b-K_a)
\]

로 정확하다. 결합 count+pair 변화는 실제 총 L1과 \(\max_i|K_i|\)로 제한할 수 있다. response 계수 자체가 상태와 함께 바뀌는 nonlinear Grackle 흐름의 전역 오차 상계는 여기서 도출되지 않는다.

앞선 동일 age 분포·다른 opacity response의 W1=0 반례와 조건부 paired bound, 24 prescribed-opacity 사례는 완료 증거로 재사용한다. 지금의 정수 저장 보정이 그 반례를 없애거나 실제 nonlinear response bound를 제공한다고 주장하지 않는다.

문헌은 서로 다른 문제의 범위를 구분하는 데 사용했다:

- [Cont–Heidari, arXiv v3](https://arxiv.org/html/1501.00014v3), Props.3.1–3.2: 단일 합을 보존하는 정수 반올림. 두 저장 moment 제약의 성공 정리로 확대하지 않음.
- [Sommariva–Vianello, author PDF](https://www.math.unipd.it/~marcov/pdf/compresscub.pdf), 식(5),(6),(13),(15): 비음 실수 moment fitting과 residual 기반 응답 근사. subnormal 정수 격자의 엄격한 두 gate와 구분.
- [Wilhelmsen 1974](https://doi.org/10.1137/0711030): 주어진 노드의 비음 cubature 존재 충분조건. 이번 작은 셀의 정수 표현 문제와 구분.

SciSpace 검색, Exa 원문 읽기, Wolfram context/evaluator를 실제 사용했다. Wolfram은 정확한 보존 등식과 작은 정수 경우 33,696개를 확인했다. 성공 정수 1,803개가 유도 구간 안에 포함됐다. 일반 구간 명제의 증명은 별도로 제공하며, 유한 사례 계산만으로 일반 정리를 선언하지 않는다. 도구 기록은 `evidence/exact_pair_theory_20261019/TOOLS_RECEIPT.json`이다.

## 4. 같은 계산 소스의 age32와 수동적 진단

새 명시적 plan은 q0, age32, n_mu8, source8, transport16, time1, common birth levels [8,16,32,64]다. 기존 age64와 age axis만 다르다. 기본 캠페인의 다섯 사례는 그대로며 age32는 명시적으로 선택해야 한다.

진단용 solver는 원래 generated solver SHA를 고정해 변환한 별도 사본이다. computational base, 변환 소스, 실제 실행 소스의 identity를 분리했다. norm wrapper는 원래 super 호출의 float 결과를 그대로 반환한다. RK step, dense output, RHS, 초기 step, 원래 허용치를 바꾸지 않는다.

새 telemetry는 binding block, 구간 재시도에서 버려진 accepted estimates, 실제 birth 직전·직후 P 관측을 기록한다. 실패한 interval의 locally accepted estimate를 최종 trajectory의 accepted step으로 세지 않는다. source jump 진단은 저장된 binary64 항을 Fraction으로 읽고 coverage·시계·active count·중복·누락을 따로 검사한다. 새로운 과학 gate를 만들지 않는다.

완료된 age64의 binary와 계산 base를 재사용한다. compact B1만 남은 경우 153 frozen input에서 동일한 156 prepared output을 복원하고, 원본 PREPARED_IDENTITY 바이트·BUILD_RECEIPT·binary hash binding이 정확할 때만 binary를 재사용한다. 원래 build receipt의 연결을 꾸며 바꾸지 않는다. 비교기는 COMPLETE·원자료 hash·동일 binary/runtime·non-age config를 확인한 뒤 기존 finite-neighbor 비교기를 호출한다.

### 실제 tiny native 대조

q0, birth2, n_mu8, source8, transport8, block-max, binary64, transport thread1로 off/on 한 쌍만 실행했다. B1의 검증된 동일 binary를 복사해 사용했다.

| 항목 | 실제 결과 |
|---|---|
| exit / wall | off 0 / 2.376692179 s; on 0 / 2.525052964 s |
| RHS | 양쪽 1,302회, error 없음, interval 결과 동일 |
| 상태 | 저장된 accepted whole-state snapshot 3개, 구간 끝 x, endpoint, 기존 observations, ledgers, setup byte 동일 |
| telemetry | 87 estimates = retained accepted84 + rejected3, solver steps84와 일치 |
| source jumps | 실제 birth 2/2 coverage, nonbirth/gas/ledger 좌표 bits 보존 |
| 고정 ledger gate | photon 1.1929597340350156e-11, energy 1.279000990894289e-14, 양쪽 PASS |

원래 solver는 모든 내부 adaptive step의 x/y와 native RHS byte stream을 저장하지 않는다. 이 실제 실행에서 해당 전체 byte 대조를 했다고 주장하지 않는다. 별도의 deterministic RPC fixture가 scheduled RHS bytes, rejection 및 DomainError rollback을 검증했다. 실제 tiny case에서는 rollback이 없었다.

저장된 birth 불변량의 정확 유리수 차이는 +1.3552527156068805e-20, -1.371599384158768e-20이다. 이 값은 0이 아니며, 통과했다고 새 허용치를 도입하지 않았다. 실제 source addition의 저장 잔차로 기술한다.

## 5. 검증·배송 및 다음 DAG

독립 review는 N1/N3 5 tests, N4 3 tests, S 범위 14 tests를 대상으로 각각 PASS였다. S의 14에는 신규 5개와 기존 norm 9개가 포함된다. N1/N3/N4 신규 테스트 방법은 8개다. 구현자와 reviewer의 같은 테스트 실행을 새 unique test로 중복 합산하지 않는다. 전체 historical suite나 24-case prescribed-opacity campaign은 이번에 다시 실행하지 않았다.

현재 READY는 **R_AGE32_BLOCK_MAX_SAME_SOURCE_WITH_PASSIVE_DIAGNOSTICS** 하나다. 기존 NCP Python3.12.3/NumPy2.3.5/SciPy1.17.0, 동일 B1 binary, transport48에서 단일 age32를 1800 s cap으로 실행한다. 성공 시 기존 age64와 finite-neighbor 차이, source jumps, binding blocks를 분석한다. 비교 identity가 맞지 않거나 실행이 실패하면 원자료와 typed HOLD를 배송한다. 자동 age64 재실행은 없다.

owner checkout, PR150/R9, LRS task 외 repo, 별도 BASS HHeD lane을 보존한다. Git은 PR199 branch에 expected-head fast-forward만 사용한다. 게시·ZIP·remote readback의 실제 상태와 최종 HEAD는 `DELIVERY_RECEIPT_CURRENT.json`에 기록한다.

**PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.

