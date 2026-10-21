# VigilODE를 이용한 native-derived source-age 연구 | 2026-10-19

## 이번 결과

실제 native source packet을 보존한 고정 opacity 모형에서, **출생 시각을 32개로 묶으면 원래 64개 시각에 비해 전체 survivor number는 약 0.815145% 작아지지만, 흡수가 있는 node의 survivor는 약 82.574593% 작아진다.** 흡수율이 0인 공통 population이 전체 수치의 대부분이어서 첫 정규화만으로는 age 차이가 가려진다. 같은 비교의 전체 energy 차이는 약 −2.607765%다. 이는 고정 gas·endpoint geometry·node 조건의 새 계산이며, 실제 nonlinear native age32→64 수렴 결과를 대신하지 않는다.

VigilODE의 원래 affine error-prefix 코드를 이 모형에 연결했다. 전역 최소 absorption hazard를 사용하는 첫 경계가 넓다는 실제 결과를 확인한 뒤, 동일 hazard tuple끼리 1,112개 sensitive group을 만들어 다시 계산했다. 이 보완으로 number-error 상한이 약 1,356–1,437배 좁아졌다. node별 직접 해와 그룹별 prefix가 같은 정확한 실수 오차 합을 감싼다는 것을 유도하고, 전체 57,344개 node를 독립적인 Decimal 100자리 계산으로 확인했다.

원래 age32 block-max NCP 실행은 READY다. native time8/16/32의 저장 표현 문제는 HOLD다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 1. 연구 전에 실제로 읽은 GitHub와 백업

REI draft PR199의 실제 HEAD는 `0ae749e9fdb179729c018706dbd59c4f61732b6a`였고 게시 준비 중 재조회에서도 같았다. 사용자가 처음 제시한 `604c228…`보다 뒤의 배송 상태를 읽어 이어갔다. CURRENT5와 AGENTS를 해당 실제 HEAD에서 읽었으며, 이미 완료된 age64 block-max와 spectral128을 반복하지 않았다.

| 조사 범위 | 실제 수행과 발견 |
|---|---|
| REI GitHub | branch 247개, PR metadata 205개 전체 페이지; PR199 최신 commits 30개·comments·Actions 최신 100개; 관련 PR150/151/171/198/199/205/206 확인 |
| Google Drive | 연관 폴더 52회 목록, 반환 entry 1,659개; age backup 폴더 112개; 최신 관련 실행 ZIP/TAR의 실제 내용 확인 |
| Dropbox | 연관 폴더 18회 목록, 반환 entry 1,171개, cursor 종료; age 전용 폴더 18개 |
| 새 관련 원자료 | BR05, LRS, RUN16 archive 전체 다운로드·SHA/크기/CRC 또는 TAR 구조 확인; manifest payload 합계 1,204개 모두 size/SHA 일치 |
| 새 PR199 age32 결과 | 이번 관찰 범위에서 발견되지 않음 |

목록 entry 수는 중복을 제거한 파일 수가 아니다. Drive 공용 research dossier의 최신 1,000개는 2026-10-19부터 9월26일까지의 새 결과 창을 덮지만 오래된 전체 계정 이력을 끝까지 읽었다고 주장하지 않는다. 알려진 전용 경로와 발견된 연관 폴더를 조사했다. VigilODE PR71이 언급하는 약 184MB 원본 종합 backup은 이번 검색에서 찾지 못했으며, GitHub에 게시된 실제 CSV를 읽었다. 이 한계는 `vigilode_age_transport_20261019/intake/`에 보존한다.

다른 REI lane의 새 실행은 아래와 같이 구분해 반영했다.

| 관련 lane | 새로 읽은 실행 근거 | age-exposure 연구에 미치는 의미 |
|---|---|---|
| PR198, LRS SSPRK2 | N512/5,952 segments에서 proper-clock 누적 defect가 +112.286124136 s에서 −4.88281e−7 s로 줄어든 `ln1p` 교정 자료; 같은 16설정의 전후 비교 | source clock의 차분 계산이 실제 영향을 줄 수 있다는 근거. REI 원 physics를 임의 수정하지 않음 |
| PR205, RUN16 | frozen path survivor 1.1803145305707004e−10 comoving m^-3, HI elasticity 0.9972065222179413, 첫 gap의 sensitivity 기여 75.895% | opacity/path 상관관계가 중요하다는 조건부 진단. 전체 gas trajectory enclosure 아님 |
| PR206, BR05 | Nt16/r8 실제 birth-monitor history, 41.91796 s; 유한 time–birth rectangle 검토 | 해당 BASS lane의 실제 결과로 보존. native age32 비교나 joint continuum convergence를 대신하지 않음 |

## 2. VigilODE에서 실제로 재사용한 부분

default `main`만 읽지 않았다. branch 147개와 PR metadata 71개, 관련 tree와 DAG를 조사하고, 최신 benchmark branch와 all-DAG 연구 branch가 갈라져 있음을 확인했다.

재사용 기준은 `research/all-dag-completion-20261018`의 `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406`이다. 아래 원본 두 파일을 변경 없이 포함하고 license와 SHA256을 기록했다.

| 원본 | 사용한 기능 |
|---|---|
| `crates/rodas5p-core/src/directed.rs` | 양성 interval 계산의 outward addition/multiplication |
| `crates/rodas5p-integrators/src/affine_transport.rs` | `AffineErrorMap`, `parallel_error_prefix`, `AffinePrefixWorkspace` |

원본 코드의 model premise는 호출자가 입증해야 한다. 이번에는 동일 packet의 두 출생 시각 이후 photon 차이가 지수 감쇠한다는 정확한 식으로 그 premise를 제공한다. 필요한 세 가지 error variant만 공급하는 작은 compatibility layer를 두었고, 전체 nonlinear RODAS5P solver를 교체하지 않았다.

이미 게시된 154행 endpoint CSV와 2,700행 continuous-time CSV는 실제로 읽고 기존 검증기를 실행했다. 두 번째 CSV는 2,639개 완료, 54개 거부, 7개 solver failure다. 완료 행 중에서도 requested-grid 정확도 기준을 넘는 경우가 있다. 예를 들어 nonlinear Prothero–Robinson의 한 uniform101 설정에서 직접 요청 시각으로 진행한 행은 작은 normalized error를 보였지만, dense-off 행은 약 1,751.99였다. 따라서 완료 상태와 요청한 관측 시각의 정확도 판정을 분리했다.

게시 전 PR71이 `9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858`까지 갱신된 것도 발견했다. 이전 `ac1cd2a…` 이후 5 commits/82개 변경 파일은 모두 별도 strict-solver-comparison 연구 경로였다. 이 고정 cutoff에서 34개 파일의 Git blob을 검증하고 새 실행 aggregate를 독립 재집계했다. 실패 run39255702592는 NumPy int32 JSON 직렬화 오류였고, 뒤의 run39257390707은 756개 고유 accuracy cell, 1,152개 유효 timing process, 96개 paired comparison을 남겼다. R_up≤1은 VigilODE-fast 207/252, Diffsol 39/252, Netlib DVODE 16/252였다. 96개 timing comparison 중 achieved-accuracy factor2가 맞는 것은 12개이고 84개는 같은 target 비교이므로 이를 일괄 성능 순위로 해석하지 않는다.

실행 metadata HEAD와 실제 컴파일된 교정 source SHA가 다른 점을 별도 receipt로 확인했다. SciPy1.17 VODE를 원 Fortran VODE와 같다고 취급하던 해석도 철회되어 있으며, 새 비교는 genuine Netlib DVODE를 사용한다. raw accuracy/timing JSONL gzip은 Git에서 제외되어 있고 Actions artifact API는 0개를 반환했으므로 aggregate 재집계를 전체 raw trajectory 검증으로 부르지 않는다. 자세한 근거는 `intake/SECOND_VIGILODE_INTAKE.json`에 있다. 새 자료는 production promotion이나 global error guarantee를 발급하지 않으며, 이번 affine source pin의 변경을 요구하지 않는다.

## 3. 현재 작업에 적용한 Rust package

| Package | 정확한 version | 실제 역할 |
|---|---|---|
| num-rational | 0.4.2 | 내보낸 binary64를 exact dyadic rational로 해석; optical depth와 Taylor 항의 정확한 연산 |
| num-bigint | 0.4.6 | 위 유리수의 분자·분모 정수. num-rational의 사용 version과 연결 |
| num-traits | 0.2.19 | 변환과 수치 trait |
| rayon | 1.12.0 | 원래 VigilODE parallel prefix의 실행과 thread 1/2/4 일치 확인 |
| serde / serde_json | 1.0.228 / 1.0.145 | 명시적 입력·출력; JSON float roundtrip |

Cargo.lock과 22개 dependency source/license를 함께 넣고 빈 registry cache에서도 `--offline --locked` 검증을 수행했다. 초기 registry→vendor 전환 때 생긴 stale Rust artifact 오류는 task build cache만 정리해 해결했으며, 실패 로그도 보존했다. 별도 외부 crate를 추가하지 않아도 충분한 기능은 추가하지 않았다.

## 4. 수학과 실제 데이터의 연결

packet i의 고정 source weight w_i, 총 hazard Λ_i, 출생 b_i에 대해 n_i(T)=w_i exp[−Λ_i(T−b_i)]다. A/B의 packet과 rate가 같으면 t_i*=max(b_Ai,b_Bi) 이후 차이는

\[
|n_{Ai}(T)-n_{Bi}(T)|
=w_i(1-e^{-\Lambda_i|b_{Ai}-b_{Bi}|})e^{-\Lambda_i(T-t_i^*)}.
\]

이 양성 항의 합 D(T)가 total survivor 차이의 상한이다. 동일 rate tuple 그룹에서는 각 birth mismatch가 생기는 시점에 defect를 더하고 그 사이를 같은 hazard로 감쇠시키는 affine recurrence가 정확히 D를 재현한다. 경계의 실제 구현은 그 연산을 위쪽으로 반올림한다.

exponential은 정확한 유리수 optical depth, 이진 range reduction, 19차/18차 교대 Taylor 하한·상한, directed squaring으로 감싼다. 깊은 감쇠에서는 최소 양의 subnormal 상한을 남긴다. exp(-752)<2^-1074의 유리수 증명과 독립 CAS 검산을 포함했다.

같은 age marginal만으로 response가 정해지지는 않는다. weights (1,1), hazards (0,1), T=1, births (0,1)과 (1,0)은 age와 hazard marginal이 같지만 survivors가 2와 1+e^-1이다. source label 또는 joint age–hazard coupling을 보존해야 한다. passive zero-hazard node는 number 차이가 없어도 age moment가 달라지므로 N의 bound를 age-moment bound로 해석하지 않는다. 별도의 moment 경계와 평균 age의 양의 denominator 조건은 `THEORY_KO.md`에서 유도했다.

## 5. 실제 새 계산 결과

원본 age64의 64 source packet을 endpoint geometry에서 준비하여 **57,344개 node(각 896개)**를 추출했다. 출생·physical birth·encoded birth·inventory는 원래 보관 setup과 같았다. native transformed RHS 평가와 새 ODE history는 각각 0회다. 원 native 입력 153개와 준비 출력의 원래 부분도 독립 재검증했다.

각 설정은 동일한 packet/spectrum/opacity를 사용한다. 8/16/32는 출생 시각만 인접 cohort 묶음의 native proper-time midpoint로 바꾸고, 64는 원래 시각을 사용한다.

| 출생 시각 수 | survivor N [photons/H] | N의 64 대비 차이 | energy의 64 대비 차이 | 그룹 affine number-error 상한 [photons/H] |
|---:|---:|---:|---:|---:|
| 8 | 1.2963971200896042e−7 | −0.9863225862% | −3.2864403695% | 1.292312768972707e−9 |
| 16 | 1.2966075430685719e−7 | −0.9702513125% | −3.2108404228% | 1.2882258655815744e−9 |
| 32 | 1.2986383732570632e−7 | −0.8151445462% | −2.6077646955% | 1.25025157367156e−9 |
| 64 | 1.3093111517030134e−7 | 기준 | 기준 | 0 |

표의 survivor/energy는 central values이며 `STUDY.json`에 각각의 enclosure가 있다. 경계 열은 total number 차이의 절댓값을 감싸고, energy 차이를 감싼다고 표시한 값이 아니다. 32 대비의 central |ΔN|=1.0672778445950189e−9보다 bound가 약 17.14% 넓은 것은 label별 양의 차이를 합하기 때문에 전체 합에서의 상쇄를 사용하지 않기 때문이다.

### Passive population을 분리해야 보이는 차이

독립 C9에서 4,096개 zero-hazard node의 공통 mass가 결과 대부분을 차지함을 확인했다. 원래 CSV의 exact dyadic 합은

\[
P=\frac{2567757288181244159093}{19807040628566084398385987584}
 \simeq1.2963861367952044\times10^{-7}\;\text{photons/H}.
\]

N_sensitive = N − P를 정확한 유리수 interval 연산으로 재합산했다. 64의 sensitive survivor interval은 엄격히 양수여서 상대 차이의 분모 조건도 확인된다.

| 출생 시각 수 | 흡수가 있는 node의 survivor interval [photons/H] | 64 대비 signed 상대 차이 interval |
|---:|---:|---:|
| 8 | [1.0983293258238907e−12, 1.0983301709774838e−12] | [−99.9150230395%, −99.9150228434%] |
| 16 | [2.2140627217826137e−11, 2.2140628063006203e−11] | [−98.2869941325%, −98.2869939374%] |
| 32 | [2.2522364606161115e−10, 2.2522364690676477e−10] | [−82.5745930009%, −82.5745928161%] |
| 64 | [1.2925014906580857e−9, 1.2925014915032395e−9] | [0, 0] |

이 보완은 보관된 STUDY와 CSV의 가벼운 재합산이며 Rust model 실행을 다시 하지 않았다. 전체 N에 가까운 백분율이 나온다는 사실만으로 age accuracy를 수용해서는 안 된다는 직접 진단이다. 다만 native controller에서의 RMS dilution 인과관계를 증명한 것은 아니다.

고정 모형의 전체 N64≈1.30931e−7/H와 실제 보관된 nonlinear age64 endpoint N≈1.2909104481275381e−9/H는 약 101배 다르다. 고정 endpoint geometry에서 passive가 된 node가 많은 것이 이 모형과 원 trajectory의 차이를 드러낸다. sensitive 부분이 원 endpoint 수치와 가깝다는 관찰도 trajectory error bound나 검증된 작은 perturbation으로 해석하지 않는다.

전역 최소 hazard를 사용한 첫 upper는 8/16/32 순서로 1.752630145924156e−6, 1.8517261640991709e−6, 1.7926975551157504e−6이었다. grouping 후의 upper는 정확한 Decimal label-defect 합과 상대적으로 약 10^-14 이내에서 일치한다. 서로 독립적으로 반올림한 direct upper와 grouped upper의 endpoint 순서를 강요하지 않는다.

| 실행·검증 | 실제 범위 |
|---|---|
| Native coefficient export | 1회, 약 11.8 s, 64 packet·57,344 node; 새 native trajectory 0회 |
| Fixed-model 계산 | 4개의 고유 설정. 전역 경계 분석 후 grouping을 추가한 변경 분석 1회; 같은 사례를 8개로 중복 계산하지 않음 |
| 최종 grouped 계산 | kernel 51.048 s, cargo 명령 전체 53.733 s; cached exp 평가 53,408개 |
| Rust tests | 고유 4개: 새 task 3개 + 원본 upstream 1개. 반복 검증 명령 수를 고유 test 수로 세지 않음 |
| 독립 수치 검산 | exp fixture 17개, 모든 node의 labelled D를 Decimal 100자리로 재합산; photon ledger, passive node, source/vendor SHA 확인 |
| Parallel reproducibility | group final vector 및 원 prefix의 thread 1/2/4 bit parity |
| R6 / C9 | 별도 검토자의 수학·source/units·actual-data 독립 검토. 최종 source/output hash를 각 receipt에 연결 |

기존 83-test/24-case 연구와 뒤의 pair-search/tiny-native 검증은 관련 identity를 유지하여 재사용했다. 전체 과거 suite 또는 완료 NCP 캠페인을 반복하지 않았다.

## 6. 도구·보호 범위·다음 실행

SciSpace로 관련 positive-transport 문헌 후보를 찾고, Exa로 공식 Rust package/source를 확인했으며, Wolfram으로 cutoff 부등식·pair identity·photon ledger를 실제 검산했다. primary paper 전문을 확인하지 않은 항목은 초록 탐색으로만 기록한다. 이 연구의 증명은 명시된 scalar 모형의 직접 유도와 실제 version-pinned source에 의존한다.

현재 local Rust 1.94.1에서 컴파일과 계산이 실제로 작동했다. NCP connector는 새 호출에서 월 사용량 중지 상태를 반환하여 이번 대화의 NCP 실행은 NOT_RUN이다. 과거 compiler·백업 접근 blocker를 자동 상속하지 않았다. 현재 PR199의 이전 top-level CI는 owned task 밖의 `cargo fmt` 차이로 실패한 상태였으며 이를 새 코드의 과학 검증 PASS와 섞지 않는다.

남은 외부 실행은 이미 준비된 **q0 age32 block-max/binary64, source8/n_mu8/transport16/time1, passive diagnostics ON, transport48, case/total 1800 s cap** 한 사례다. 완료된 age64의 binary·computational base·runtime에 binding하여 비교한다. 현재 고정-opacity 계산 때문에 age64나 spectral128을 다시 돌릴 이유는 없다. 복사 가능한 전체 프롬프트는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다.

owner checkout, PR150/R9, LRS 및 BASS HHeD lane은 수정하지 않는다. PR199만 expected-head fast-forward로 배송하고 draft 상태를 유지한다. C8/C10 v6의 실제 provider identity와 readback 상태는 `DELIVERY_RECEIPT_CURRENT.json`에서 확인한다. archive 생성 이후 작성되는 final receipt는 그 archive 안의 pending receipt를 대체하며 자기 자신의 commit/hash를 재귀적으로 포함한다고 주장하지 않는다.

## 주요 근거

- [REI PR199](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199)
- [VigilODE PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)
- [고정 affine source](https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-integrators/src/affine_transport.rs)
- `vigilode_age_transport_20261019/THEORY_KO.md`, `IMPLEMENTATION.json`, `inputs/`, `results/`, `intake/`, `reviews/`
- 기존 원본/실행/배송 근거: `RESEARCH_UPDATE_20261019_PAIRSEARCH_KO.md` 및 `evidence/current_entries_before_vigilode_20261019/`
