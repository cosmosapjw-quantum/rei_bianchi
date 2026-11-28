# BASS_HE E13C5 — 전체 finite 오차 예산과 두 OFF 정밀화의 효과

## 결론

이번 연구 노드는 `HE_E13C5_FULL_FINITE_BUDGET_AND_COMPLEMENT01`이다. 실제 독립 최종 판정은 **PASS_SCOPED**, 미해결 blocker는 **0개**다. PR20에 이미 저장된 OFF/KF/GM 각각 2,440개 node의 first-two-step 구간을 직접 합산하고, 같은 목표를 둘러싸는 OFF 0·700의 기존 N512 결과 두 항을 결합했다.

전체 OFF photon 구간 폭의 감소는 **1.430233307 ppm**, 종별 합 열 구간 폭의 감소는 **1.059316287 ppm**이다. 교체 뒤 남는 폭 중 선택 밖 2,436개 node의 비중은 각각 **99.9999829853%**, **99.9999701123%**다. 선택 네 경로에서 확인한 9.4059배·4.5443배의 축소가 전체 합에서도 같은 비율로 나타나는 것은 아니다.

다음 finite 정밀화의 후보는 photon/흡수량에 대해 OFF **101·102**, 종별 합 열에 대해 OFF **410·413**이다. 다만 상위 두 경로의 폭을 완전히 없애도 감소 가능한 비중은 photon **0.7871572984%**, 열 **0.2974840851%**에 그친다. 전역 폭은 여러 node에 분산되어 있다.

이번 실제 primary는 저장된 결과에 대한 정확한 유리수 합산 **1회**다. 새 계수 평가, ODE, native, gas, full-first2 및 N512 solver 실행은 **0회**다. NCP 전달 계약도 이 저장 결과 합산을 한 번 재현하는 작업으로 고정했다. 실제 NCP 호스트 실행은 이 Chat 작업에서 수행하지 않았다.

## 1. 입력 계보와 연구 목표의 갱신

이전 노드는 selected 네 node/mode 밖의 complement를 어떻게 제한할지 준비하고 있었다. 최신 계보를 확인하니 PR20의 원 계산이 전체 finite captured grid를 이미 처리한 상태였다.

| 근거 | 고정 identity와 의미 |
|---|---|
| PR20 원 계산 head | `0633ec2c9aed37593b9f1c05abc7156727408583` |
| PR20 head tree | `49d1a38d4243ea94190a6ad6cf607ed822d8c9c0` |
| PR20 원 evidence commit | `ba42c50aa4b92e69d1c7dc62e32c36d904401d8b` |
| PR19 두 OFF 정밀화 계보 | `b6c2d1468a63042d56b8cf4b3d13bc72dcff198a` |
| 전체 saved PATHS | 292,932,850 bytes; SHA `175d8aa96d50965127ac61840991fc69e348e1acbb21e21cfed5eb7947441c94` |
| N512 saved result | SHA `5a3b9f17c6d250afed0e4270e4cce71d22d930a482084bc12c3e7dcc66cb68d7` |

PR20은 이전 PR19의 `e25039b3…`에서 갈라져 나왔다. 따라서 두 OFF N512 결과가 PR20에 이미 반영되어 있다고 가정하지 않았다. PR20이 재사용한 12경로는 PR19의 해당 record와 `segment.origin` 이외 모든 필드가 동일함을 확인했고, N512의 동일 목표 대응은 고정된 이전 lineage reducer 결과와 연결했다.

PR20의 full cover는 **7,320경로 / 14,652segment**다. 특별 node 0·700·1620·2344만 경로당 3segment이고 나머지는 2segment다. 이 루프는 PR20의 원 3시간 54분 계산이나 원 구성요소의 물리 검토를 다시 수행하지 않았다. 원 계약의 `HARNESS_UNAVAILABLE=true` 및 당시 `PENDING` 기록은 역사 자료로 보존하고, 이후의 scoped independent review를 별도 연결했다. 현재 루프는 GPT-6 Astra 연구·코딩 하네스 4.0.0을 적용했다.

## 2. 합산 대상과 수학적 계약

Mode \(m\), 관측량 \(X\)에서 고정 captured grid의 목표는

\[
Q_{m,X}=\sum_{p=0}^{2439}w_{m,p}x_{m,p,X},\qquad w_{m,p}>0
\]

이다. \(S=\{0,700,1620,2344\}\), \(R=G\setminus S\)로 두고 각 경로 interval의 끝점을 정확한 Fraction으로 읽었다. 이미 weight가 포함된 `weighted_reduction`에는 weight를 다시 곱하지 않았다.

\[
I^{\rm full}_{m,X}=I^S_{m,X}\oplus I^R_{m,X}.
\]

Complement는 저장된 2,436개 항의 **직접 합**으로 계산했다. 전체 interval에서 selected interval을 일반적인 interval subtraction으로 빼면 폭이 \(W_R+2W_S\)로 부풀 수 있다. 반올림된 전체 합의 끝점에서 기존 항의 끝점을 임의로 공제하는 방식도 사용하지 않았다.

교체 집합은 \(K_{\rm OFF}=\{0,700\}\), \(K_{\rm KF}=K_{\rm GM}=\varnothing\)이다.

\[
I^{\rm hybrid}_{m,X}
=\bigoplus_{p\notin K_m}w_p I_p^{\rm old}
\oplus\bigoplus_{p\in K_m}w_p I_p^{512}.
\]

모든 OFF 34개 전체 지표, 즉 절대량 17개와 보정량 17개에서 hybrid는 기존 전체 interval 안에 들어간다. KF와 GM은 각 exact per-path 합이 그대로 유지된다. Mode는 서로 다른 captured gas history이므로 세 mode를 하나의 물리량으로 더하지 않았다.

보정량은 별도의 목표다.

\[
\Delta_{m,X}=\sum_p w_{m,p}(x_{m,p,X}-c_{m,p,X}).
\]

누적 moment의 \(c\)는 captured segment 값의 exact-lift 합이다. Photon은 마지막 segment의 `DP`, energy stock은 마지막 `energy_endpoint_minus_captured_erg`를 쓴다. Energy 변환에는 입력 규약의 binary64 `1.602176634e-12`를 정확히 lift한 \(\epsilon\)을 한 번 적용했다. 이 보정은 native 전체 AGGREGATE 또는 continuum integral과의 차이가 아니다.

A/B/H total은 양쪽 모두 **세 종의 interval 합**으로 정의했다. 더 좁은 전용 total certificate를 한쪽에만 섞지 않았다. Signed whole-path anchor는 inter-step seam을 포함하며, `anchored=false` 기록만으로 seam을 제거하지 않았다.

## 3. 전체 폭, selected 효과, 남는 폭

아래는 정확한 결과를 반올림하여 표시한 값이다. 폭은 \(U-L\)이며, energy/heat는 저장된 captured 정규화와 spectral weight를 유지한 eV 지표다. 원 exact endpoint는 `BUDGET_EXCERPT.json` 및 `evidence/budget_control/EXEC01/RESULTS.json`에 있다.

| OFF 지표 | 기존 전체 폭 | 교체 후 전체 폭 | 감소율 |
|---|---:|---:|---:|
| 최종 photon | \(6.210370822609\times10^{-17}\) | \(6.210361940330\times10^{-17}\) | 1.430233307 ppm |
| 종별 합 흡수량 | \(7.614520380689\times10^{-17}\) | \(7.614501107383\times10^{-17}\) | 2.531125413 ppm |
| 종별 합 흡수 에너지 | \(1.468942901079\times10^{-15}\) | \(1.468939874990\times10^{-15}\) | 2.060045104 ppm |
| 종별 합 열 | \(3.911161582128\times10^{-16}\) | \(3.911157438971\times10^{-16}\) | 1.059316287 ppm |
| Signed whole-path anchor | \(5.758034876685\times10^{-32}\) | \(5.758011891788\times10^{-32}\) | 3.991795371 ppm |

\(1\) ppm은 상대비 \(10^{-6}\)다. 따라서 photon의 감소율은 약 **0.0001430233%**다. 물리량 자체의 크기가 이 비율만큼 변했다는 뜻이 아니라, 해당 finite enclosure의 **폭**이 줄었다는 뜻이다.

| 지표 | 선택 네 경로의 old/hybrid 폭비 | hybrid 전체 폭 중 complement 비중 | 현재 두 OFF만 더 정밀화할 때 가능한 추가 감소 상한 |
|---|---:|---:|---:|
| Photon | 9.40586548355 | 99.9999829853% | 0.112876147 ppm |
| 흡수량 | 11.0377770294 | 99.9999747839% | 0.184654910 ppm |
| 흡수 에너지 | 6.87887264467 | 99.9999649584% | 0.150288943 ppm |
| 열 | 4.54432801714 | 99.9999701123% | 0.075458651 ppm |
| Anchor | 12.1198953196 | 99.9999641021% | 0.270600022 ppm |

이 상한은 현재 두 항의 폭을 0으로 만들고 모든 다른 항을 고정하는 가정에서 나온다.

\[
W^{\rm new}=F_K+B^{\rm new}_K,\qquad
F_K=\sum_{p\notin K}w_p(U_p-L_p).
\]

따라서 현재 두 경로에만 계산을 계속 투입하는 선택의 한계를 수치로 확인했다. \(F_K\)는 고정한 per-path Minkowski 합의 floor다. 경로 간 상관성, 보존식 또는 새로운 direct-total certificate로 표현을 바꾸는 모든 방법에 대한 보편적인 하한은 아니다.

## 4. 다음 finite 정밀화의 후보

교체 뒤 weighted width의 순위를 관측량별로 계산했다. 서로 단위가 다른 photon/energy/heat의 폭을 합친 임의 점수나 사후 tolerance는 만들지 않았다.

| OFF 목표 | 상위 두 node | 상위 2개 비중 | 상위 10개 | 상위 100개 |
|---|---|---:|---:|---:|
| Photon | 101, 102 | 0.7871572984% | 3.8541169753% | 30.6391918477% |
| 흡수량 | 101, 102 | 0.8814078231% | 4.3037049313% | 32.7068737179% |
| 흡수 에너지 | 101, 102 | 0.6295980743% | 3.0901264657% | 25.3505528995% |
| 열 | 410, 413 | 0.2974840851% | 1.4871859625% | 14.6334776265% |
| Anchor | 109, 329 | 1.7363404473% | 7.3670477465% | 32.0141424396% |

Photon/열의 후보 네 경로는 모두 일반 2segment, `source_on=true`, HI만 활성인 mask다. 저장된 에너지 영역은 node 101/102에서 약 13.7709/13.7891 eV, node 410/413에서 약 18.5942/18.6420 eV다. 정확한 segment별 domain은 구현 요약과 전체 결과의 `character`에 남겼다.

다음 연구 노드는 이 네 후보의 same-target 입력, incoming carry 및 signed seam을 고정한 **관측량별 정밀화 계약**으로 잡을 수 있다. 상위 기여 비중은 가능한 개선의 상한이고, 아직 시행하지 않은 N512 계산의 실제 개선율이나 실행시간 예측이 아니다. 이번 NCP 전달에는 이 후속 solver 작업을 포함하지 않았다.

## 5. Full finite 보정량의 부호

각 mode의 17개 보정량, 총 51개에서 strict sign이 확정되었다. 부호는 hybrid 전에도 같았으며, 이번 두 항의 정밀화가 부호를 새롭게 결정한 것은 아니다.

| Mode | 최종 photon 보정 | Energy stock 보정 [eV] | 종별 합 열 보정 [eV] |
|---|---|---|---|
| OFF | \([4.827055209445,4.827676245639]\times10^{-13}\) | \([8.847799613141,8.849003863531]\times10^{-12}\) | \([-2.603095871717,-2.602704755973]\times10^{-12}\) |
| KF | \([4.832458647426,4.833080484185]\times10^{-13}\) | \([8.855990705579,8.857196739393]\times10^{-12}\) | \([-2.605868273986,-2.605476580139]\times10^{-12}\) |
| GM | \([4.918913639490,4.919548274862]\times10^{-13}\) | \([8.987048132813,8.988282686926]\times10^{-12}\) | \([-2.650226717760,-2.649825777999]\times10^{-12}\) |

표는 표시용 반올림이며 certification에는 exact JSON endpoint를 사용했다. Photon, energy stock, QN, QE, HeII의 A/B/H 보정은 양수이고, HI·HeI의 A/B/H, 종별 합 A/B/H, Z 보정은 음수다. Midpoint 부호나 zero-containing ledger만으로 부호를 판정하지 않았다.

## 6. 실제 실행과 독립 확인

Primary saved-result processor는 **34.757663469초**, 최대 RSS **171,196 KiB**, exit **0**으로 끝났다. Raw stream 1회에서 7,320경로/14,652segment와 raw SHA를 확인했다. 범위 한정 확인 **279,451개**, 합성 대조 **29개**가 통과했다. 별도의 이론 기여는 elementary exact identity와 반례 **25개**를 확인했다.

독립 검토자는 후보 코드를 import하지 않는 Fraction 프로그램으로 저장된 raw를 한 번 합산했다. 이 계산은 **20.1575초**, 최대 RSS **110,264 KiB**, **235,912 checks / 실패 0**이었다. 후보와 독립 결과의 정확 대조 **6,063개**가 통과했다. 그 안에는 1,020개 partition interval, 918개 폭 예산 값, 204개 전체 부호, 204개 top10 순서, 2,040개 top10 폭, 1,020개 top-k 비중이 포함된다.

새 NCP transport 조건에 대해서는 CSV를 한 번 풀어 **248,880행 / 102그룹**, rank permutation, 동률 node 순서, 폭 합, 상위 100개를 독립 원자료 합산 결과와 대조했다. CSV의 정확한 압축 해제 identity는 **51,718,536 bytes**, SHA `ce053b71a6b9aeb8bc5c8d1d9e9be3911c4a7aeba60779151a8af9d5bad3f8f4`다.

이 독립성은 **입력 동일성과 saved interval의 합산·순위·전달 검증**에 관한 것이다. 원 구성요소의 interval certificate와 고정 captured 모델 자체의 타당성은 기존 검토에 조건부로 의존한다. 기존 full physics 검토를 새로 수행했다고 표현하지 않는다.

최종 독립 판정과 정확한 reviewed hashes는 `INDEPENDENT_REVIEW.json` 및 `evidence/independent_review/`에 있다.

## 7. 보존한 두 실제 문제와 수정

첫 복구에서는 archive에서 읽어낸 stream의 해시만 확인했고, 실제 출력 파일의 마지막 **118,002 bytes**가 없는 것을 뒤늦게 확인했다. Primary와 독립 raw 합산은 아직 시작하지 않은 상태였다. 원본 archive는 온전했으며 새 경로에서 쓰기 길이 확인, flush/fsync, atomic rename, 실제 persisted SHA readback을 거쳐 46개 member를 복구했다. 최초 receipt와 잘못된 성공 해석, 후속 원인 조사와 정정은 `evidence/intake/`에 남겼다. 파일을 자른 주체는 확인되지 않았다.

독립 NCP 검토에서는 `dict.get`을 쓰면 필수 `null` 필드가 누락되어도 통과할 수 있음을 실제 재현했다. `key not in result or result[key] != value`로 수정했다. 최초 source와 반례를 보존했고, 누락 거부/명시적 null 허용의 두 집중 대조를 수행했다. 이 수정은 scientific reducer나 수치 결과를 변경하지 않았다.

초기 NCP 경계 대조는 21/21 통과했다. 이후 위 null 문제만 집중 확인했으며 21개 전체 suite를 반복했다고 주장하지 않는다. 최종 source의 verify-only도 수행했지만, 실제 saved-budget child 또는 NCP 과학 job은 실행하지 않았다.

## 8. NCP 재현 계약

동봉된 `code/ncp_budget_continue.py`가 단일 진입점이다. 기본값은 verify-only이고 `--execute`일 때만 **저장 결과 합산 child 1회**를 시작한다. CPython 3.12.x/Linux, 표준 라이브러리, serial worker, 1 GiB 주소 공간, reducer 내부 300초/child 330초 제한이다. 시작 전에 빈 출력 경로, 여유 disk 2 GiB, 가용 memory 최소 1.2 GiB와 14개 고정 payload를 확인한다.

PR20 원 archive와 PR19 정밀화 archive가 모두 들어 있다. 실행기는 두 archive의 해시를 확인하고 각 member를 안전하게 복구한다. 9개 실제 입력, source, 계약, lock의 실제 bytes를 실행 전후에 확인한다. 실패 시 로그, checkpoint, 복구 파일, partial 결과를 보존하고 자동 재시도하지 않는다.

원 scientific projection은 그대로 보존했다. 그 안의 gzip bytes/SHA는 zlib 버전에 따라 달라질 수 있으므로 전달 adapter는 **압축 표현의 두 필드만 제외한 정확한 의미 projection**과 **압축 해제 CSV의 exact bytes/SHA**를 함께 비교한다. Fresh gzip 자체 identity와 fresh RESULTS의 모든 필드도 확인한다. 다른 gzip 표현의 같은 CSV는 허용하고, CSV 한 글자 변경 또는 필수 null 항목 누락은 거부하는 대조가 있다.

성공 상태는 `PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY`다. 이 상태는 기록된 호스트의 저장 결과 재현을 뜻한다. 호스트 이름이나 `/home/cosmosapjw` 같은 경로를 근거로 cloud provider가 NCP라고 단정하지 않는다.

## 9. 계속 남는 연구 범위

전체 finite node를 모두 둘러싼 사실은 node 사이 연속 spectral integral의 오차를 제한하지 않는다. 예를 들어 두 node 0과 1에서

\[
f_A(\eta)=A\eta^2(1-\eta)^2
\]

는 모든 nodal 값이 0이지만 적분은 \(A/30\)이다. 따라서 nodal interval을 임의로 좁혀도 continuum bound가 따라오지 않는다. Actual coordinate/measure/domain/tail, quadrature rule, node 사이 입력의 정의, branch partition과 quantitative derivative 또는 cell-range bound가 필요하다.

현재 closeout은 full finite 예산 분석과 두 OFF hybrid에 한정한다. Continuum spectral quadrature, cosmological 시간 수렴, 새 gas evolution, 실제 photon/heat/recoil 전달, physical/global/production admission 및 receiver adoption은 HOLD다. 두 OFF 경로의 추가 정밀도만 높이는 선택의 한계와, 관측량마다 다른 complement 후보를 이번 루프의 새 연구 결과로 남겼다.

## 재현 자료 안내

- `THEORY_KO.md`: 수학적 유도, sign·floor·continuum 반례.
- `SCIENTIFIC_CONTRACT.json`, `RESEARCH_CONTRACT.json`: 목표·입력·범위·resource 계약.
- `BUDGET_EXCERPT.json`: 대표 관측량의 exact interval과 예산.
- `evidence/budget_control/EXEC01/`: 원 실행 결과, projection, 전체 CSV 순위와 resource receipt.
- `evidence/independent_review/`: 독립 arithmetic, 대조, CSV 및 runtime 심사.
- `NCP_EXECUTION_CONTRACT.json`, `RUN_LOCK.json`, `NCP_PARITY_BASELINE.json`: NCP 실행·해시·수용 조건.
- `NCP_LOCAL_CODEX_HANDOFF_KO.md`: 복사해 사용할 실행 프롬프트.
- `dependencies/`: 별도 전달 파일 없이 복구할 수 있는 두 원 scientific archive.


