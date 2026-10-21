# v10 이후 native time 유한 격자 진단 — 2026-10-21

## 최신 반환 intake

현재 공개 PR199의 실제 head는 `dd24a9f89e847ae7e97c017ffededd4aa53790d8`이며, v10 배송 head `652a7e03b844a145d6c6cbb401ab81f4a8429aff` 이후 캠페인/백업 게시 커밋이 추가되어 있다. 해당 HEAD의 task tree는 `bbe0079939ad642a4d38e443950f37926432dd70` (2,412 files)다. 현재 PR status checks는 root `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check` 실패, workspace tests skipped로 보고된다. `rust/`와 `.github/`는 이 연구 변경의 범위가 아니다.

이번 확인 범위는 PR199 최신 HEAD/commit/checks, 관련 age/source-age 검색 결과가 포함된 첫 100 branch 응답, 직접 Drive backup folder 138개, Dropbox backup folder 36개, v10 NCP return bundle과 receipt/분석이다. 이 범위에 v10 이후의 추가 native 실행·반환은 없었다. 다른 대화 전체 검색은 현재 노출된 connector에서 사용할 수 없어 미확인으로 남긴다. 전체 branch 목록이나 모든 과거 대화를 감사했다고 주장하지 않는다.

## 저장 endpoint와 identity

읽기 전용 Astra 검토는 `FINITE_GRID_ONLY_THREE_LEVEL_DIFFERENCE_DIAGNOSTIC`을 **분석 전용으로 허용**했다. 입력은 이미 반환된 NCP bundle 안의 세 raw endpoint다. 저장된 결과를 다시 계산했으며 NCP/native solver는 실행하지 않았다.

| Case | Native steps | endpoint SHA256 | N | U |
|---|---:|---|---:|---:|
| time8 | 968 | `519d67265330e471ef609f4de049b08c98407a7cc28a28f5b8c40ba3343bcf49` | 3.944104471334758e-10 | 2.02942961474498e-8 |
| time16 | 1,936 | `7f99f0d4e02c74540ca6816e094468ca3197ec45cf72c6cab0ea3053078f21eb` | 2.984041448074298e-10 | 1.593397342102259e-8 |
| time32 | 3,872 | `a0e78399b5455423420821fdd04cf7bd9160b1dea46028194398ebfe704e8a77` | 2.5968162478970445e-10 | 1.4115091425757936e-8 |

모든 endpoint의 proper time은 `16924302009133.814 s`이고 birth-time 배열은 같다. 공통 mesh는 968→1,936→3,872개이며 저장된 coarse point는 각 fine mesh의 odd zero-based index에 정확히 일치한다 (`fine[1::2] == coarse`). Refinement config에서 q0, birth32, n_mu8, source8, transport16, common birth levels 8/16/32/64는 고정되고 time factor만 8/16/32로 변한다. 세 run은 모두 같은 V10 prepared identity `ca09947a4a460d3643430547688da8f7c8e0d8bd2e7f4b79e66d3fd0bc17cb1c`, 별도 BE binary `2d5d95371df4c4cf882a4563edc4becdf965c76fdbbf9b9dfaa97fe083fd57fd`, source `campaign.py` SHA `271fb71e25efddbd492d1fe96e1557ca31abf999e2f62e6fad0a0dbd0ed8fe2f`를 사용했다. 원 positive B1 `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`와 동일 binary가 아니다.

## 방법과 결과

원 비교 구현의 상대지표는 `|z_a-z_b|/|z_b|`라 각 쌍의 분모가 달라진다. 따라서 기존 N/U 상대거리 두 개의 비로 차수를 구하지 않았다. 각 저장 scalar observable에 대해 binary64 저장값을 exact rational로 바꾸어 아래 차이를 계산했다.

`d1 = z8 - z16`, `d2 = z16 - z32`, `cΔ = |d2|/|d1|`, `p3 = -log2(cΔ)`.

`p3`는 `h ∝ 1/time_factor`라는 단일 간격 proxy와 공통 선도오차 형태 `e(h)=C h^p + higher-order terms`를 가정했을 때의 이 세 점에 대한 경험적 기울기다. 검증된 BE 차수, 점근 오차 상계, solver 수축 성질 또는 이후 격자 보장은 아니다. 모든 12개의 원 target scalar 성분에서 인접 차이 크기가 감소했고 두 `p3` 값은 다음과 같다.

| Observable | d8-16 | d16-32 | cΔ | p3 (finite-grid only) |
|---|---:|---:|---:|---:|
| N | 9.600630232604602e-11 | 3.872252001772535e-11 | 0.4033331050 | 1.3099562699 |
| U | 4.360322726427209e-9 | 1.818881995264654e-9 | 0.4171438926 | 1.2613829717 |
| temperature_K | 0.001596819683982176 | 0.001388377053444856 | 0.8694638896 | 0.2018019838 |

나머지 Gamma 3개, heat 3개, photo-event ledger 3개도 `FINITE_DIFFERENCE_DECREASE`이며 각 raw exact difference, 비율, 기울기는 [DIAGNOSTIC.json](native_optimization_20261021/evidence/native_time_refinement_20261021/DIAGNOSTIC.json)에 저장했다. 원 0.005 acceptance는 이전 방식 그대로 유지했고 time8↔16 및 time16↔32 모두 12성분 전체 기준 미달이다. 해당 12성분 중 최댓값은 각각 0.5214024677 및 0.2258134630으로, 0.005보다 크다. age32는 positive DOP853이므로 네 번째 native-BE refinement로 합치지 않았다. BE↔DOP853 cross-operator finite comparison은 기존 분석과 동일하다.

따라서 새 관측의 표현은 다음으로 제한한다: **이 세 저장 native-BE 격자에서 이 12개 endpoint 성분의 인접 차이 크기가 감소했다.** `p3`는 유한 격자 산술 진단이다. native age/time convergence는 계속 `HOLD`; nonlinear Grackle response bound는 `NOT_ESTABLISHED`; `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다.

## 연구 문헌 점검

- Iserles, *A First Course in the Numerical Analysis of Differential Equations* (Cambridge 저자 발췌본)는 Euler 방법에서 local truncation과 global convergence를 구분하고, 안정성 조건 없이 local 차수만으로 global order를 결론내릴 수 없다고 설명한다. 여기서는 경험 기울기가 정리의 대체물이 될 수 없다는 일반 맥락에만 인용한다: [Cambridge excerpt PDF](https://assets.cambridge.org/97805215/56552/excerpt/9780521556552_excerpt.pdf).
- Weirs, *Solution Verification Using the Robust Multi-Regression Approach*, Sandia SAND2017-4811C는 3 mesh Richardson 기울기를 차이 비로 계산하는 예를 제시하는 동시에, 일부 점의 3-mesh rate가 설계 차수 범위를 크게 벗어나거나 noisy할 수 있음을 보여준다: [OSTI/Sandia PDF](https://www.osti.gov/servlets/purl/1457898).
- Love & Rider (2013), DOI `10.1016/J.CAMWA.2013.04.019`는 시간만 refine하고 공간 이산화를 고정하는 상황의 관측 차수가 결합 이산화 구조에 따라 formal order와 달라질 수 있음을 논한다. 현재 실험의 직접 모델 분석은 아니며 refinement 해석이 discretization identity에 의존한다는 주의 근거다: [publisher paper](https://www.sciencedirect.com/science/article/pii/S0898122113002265).

SciSpace 검색은 Shampine & Zhang (1990), DOI `10.1137/0727087` 등 ODE convergence/asymptotic behavior literature를 찾았고, primary source 요지를 위 범위에 한정했다. Wolfram 산술은 N/U `p3`를 각각 1.309956269916857 및 1.2613829716768823으로 독립 재계산했고 Python Decimal/Fraction 결과와 일치했다. 이전의 상대거리 비 로그값은 N/U에서 1.1094326270 / 1.0865153715이며, raw-difference 지수와 다르므로 잘못된 proxy로 기록하고 수렴 차수로 사용하지 않는다.

## 실행, 검토, 전달

- Astra 읽기 전용 계약: `ADMISSIBLE_ANALYSIS_ONLY`; 첫 진단 실패 후 mesh `[1::2]` 인덱스 수정을 한 번 승인했다. 결과의 독립 검토는 `PASS`로 사실 게시를 허용했으며 scientific convergence/admission은 `HOLD`다. 요청 역할은 gpt-6-astra/high였지만 agent runtime identity는 독립 관측되지 않았다.
- `DIAGNOSTIC_ATTEMPT001`는 분석 script가 coarse mesh를 잘못된 fine index `[::2]`와 비교해 exit1로 종료됐다. stdout/stderr와 정확한 오류를 보존했다. raw source/data 오류가 아닌 진단 구현의 인덱싱 결함이다. 해당 attempt elapsed와 누적 60초 accounting은 기록되지 않아 `NOT_RECORDED` / `NOT_ESTABLISHED`로 공개한다; 이는 과학 결과 판단을 바꾸지 않는다.
- 승인된 한정 수정 후 `DIAGNOSTIC_ATTEMPT002` exit0, 0.0343s. 입력은 hash-bound saved output뿐이며 solver 실행 0회.
- 코드·물리 모델·solver·허용오차는 수정하지 않았다. 의무 CI를 실행하지 않았다. 최신 PR check의 root fmt 실패와 workspace tests skipped를 scoped 연구 판정과 혼합하지 않는다.
- 실행 receipt, stdout/stderr, raw endpoint/mesh/config 복사본, 해시, 계산 스크립트, DAG 및 현재 handoff는 같은 evidence 폴더와 task state에 보존한다.
- Native time8/16/32 campaign은 완료 상태다. 이 lane에서 새 NCP 실행은 남지 않았다. 새 NCP campaign prompt는 필요 없다.

## 다음 단계

세 저장 격자 진단은 종료했다. 새 solver case를 실행하기 전에, 남은 다음 연구 질문과 새로운 independent contract를 먼저 정의해야 한다. time64 재실행·저장 age32 재적분·모델/finite-cap/허용오차 변경은 이 결과에서 승인되지 않았다. PR199 draft는 유지하며 no merge/no force-push를 따른다.
