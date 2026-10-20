# v10 GitHub 선별 intake — 2026-10-21 KST

## 결론과 범위

이 문서는 GitHub에서 실제로 읽은 원격 목록, 고정 commit의 코드, 저장된 raw timing 및 비교 영수증에 근거한다. REI 253 branches / 최근 갱신 PR 100개, VigilODE 161 branches / PR 78개 / 최신 workflow 25개를 읽었다. age-exposure PR199 HEAD와 CURRENT5 전체 검토는 root 담당이다. 이 intake의 목록에 보인 PR199 HEAD는 `abbf71caf4bd45af5bdf8bc7744690d10b8715e7`였다.

v9 최종 commit의 실제 시각은 **2026-10-20T20:46:58Z**다. 그 이후 갱신된 REI PR은 이 목록에서 #199와 #198뿐이다. #198의 `82364d3d2548a1e864468cb781336f825fc18c29`는 **기존 NCP 반환을 수용하고 stale handoff를 교정한 새 publication**이다. 여기서 별도 native age32 신규 완료 결과는 찾지 못했다. 이는 선별 범위의 발견 결과이며 모든 branch history, 이전 대화, Drive/Dropbox 또는 모든 raw archive를 읽었다는 뜻이 아니다.

VigilODE의 production 7개 branch는 이전 intake 이후 새로 보이지만 모두 v9 최종 commit보다 이른 시각에 작성되었다. 이 차이를 post-v9 실행과 혼동하지 않는다. GitHub connector의 현재 읽기는 성공했다. 과거 connector 장애를 상속하지 않았다. 원격 변경, Git 편집, native 실행, science campaign 또는 benchmark 재실행은 **0건**이다.

## 원격 범위 및 시각

| 대상 | 실제 조회 | 범위 한계 |
|---|---:|---|
| REI branch 목록 | 100 + 100 + 53 = 253 | 이름과 HEAD 전체; 모든 HEAD의 전체 history/contents를 읽은 것은 아님 |
| REI PR 목록 | 최신 갱신 100개, state=all | 이 페이지에 있는 PR의 갱신시각과 HEAD; 모든 과거 PR 아님 |
| VigilODE branch 목록 | 100 + 61 = 161 | 이름과 HEAD 전체 |
| VigilODE PR 목록 | 78개, state=all | 첫 page가 100개 미만; 목록 시점 전체 |
| VigilODE workflow | 최신 25개 | created_at 2026-10-20T02:17:35Z–12:54:59Z, total_count 1027 |
| PR210/211 changed-files | 각각 첫 100개 | 전체 변경 파일 수로 해석하지 않음 |
| 세부 Git tree | BRPERF photon/native_rates, RUN19 native/rate_cubic, LRS coder | 모두 truncated=false, 아래 manifest의 subtree 범위 |
| source-age 관련 추가 HEAD | 5개 commit 시각 실제 조회 | optical hazard, positive age, sandbox, owner-bind, positive-native-intake 모두 10월16–18일 |

## 1. LRS 완료 반환: 반복하지 않을 근거

**원격 head:** `82364d3d2548a1e864468cb781336f825fc18c29`, 20:49:50Z. 부모 `90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec`. 이 publication은 이전 `301297a2cd34346d666ec74e12831697db9a6f01`의 반환 증거를 현재 source 기준으로 수용했다. 실제 실행 source는 `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`, VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`이다.

읽은 근거는 `sources/lrs_return_report.md`, `lrs_return_state.json`, `lrs_return_admission.json`, 실제 비교 구현 `lrs_return_compare.py`, 저장된 비교 출력 `lrs_compare_result.json`이다. RUN archive 전체 47 MB와 native 19개 raw 본문을 이번 intake에서 다시 취득한 것은 아니다. 따라서 아래 수치는 실제 comparator source와 저장 결과/receipt를 읽은 범위로 한정한다.

- NCP run `20261020T110800Z`, binary SHA256 `c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992`; 이전 sandbox C10 binary `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`.
- 19 settings = Radau 10 + SSPRK 9; RHS 38,840; source hash mismatch 0. 비교 baseline은 실제 **cell-borrowed** 19개다.
- finite numeric leaves 316,559개와 그 외 leaves 114개, containers 24,346개에서 mismatch 0. 별도 same-source cache N16 control 3개는 이 19개와 겹치므로 고유 실행 수를 22개로 늘리지 않는다.
- borrowed N2는 RHS 395 / cell preparation 2,680 / node visit 252,800. 캐시 방식의 clone 338 states / 216,320 nodes가 borrowed 방식에서 0 / 0이 된다.
- raw wall cache 0.041180299 s / borrowed 0.061808789 s. 이 실행으로 속도 향상 또는 memory 감소가 성립했다고 주장하지 않는다. 내부 elapsed 합 4.937230308 s는 초기화 포함·JSON 직렬화 제외이며 exclusive RHS CPU가 아니다.
- archive `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`, 47,372,583 bytes, SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`.
- admission은 ACCEPTED_SCOPED이고 root escalation은 false다. STATE의 PREPARED_NOT_PUBLISHED는 source-time 필드다. 현재 실제 원격 publication을 읽었으므로 이를 blocker로 상속하지 않는다.
- borrowed 개별 argv/input/outcome/binary-hash 링크는 archive에 없고 same-binary 연결 일부는 delivery assertion이다. 이 한계를 기록하되 provenance 보강만을 위해 완료된 protected LRS 캠페인을 반복하지 않는다.

**age lane에 주는 정보:** FD Jacobian/동일 cell에서 준비물 재사용 및 clone 제거는 유용한 후보이나, LRS 물리·source·adapter를 age lane에 그대로 이식할 근거가 아니다. 이번 intake는 LRS adapter Rust body를 읽지 않았으므로 직접 port 승인으로 사용하지 않는다.

## 2. BRPERF01: photon path 준비와 지속 worker의 실제 구현

**pin:** PR210 `e4c8133288614638792888367ca10b2ded3138ff`. 실제 읽은 source는
`photon/src/batch.rs` (blob `b7d34aeb7ae15e76f21ecb68e6edeacb48cf20f2`)와
`photon/src/kernel.rs` (blob `3921f20abfc0df057421664cdba4846e6f0c66c5`)다.
로컬 대응은 `sources/brperf_batch.rs`, `sources/brperf_kernel.rs`.
전체 prefix는 `research/dossier_ssot_sandbox_20261016/bass_reactive_performance01_20261020/brperf01/`이다.

PreparedBatch는 모든 birth label을 보존하며 원래의 reflection-equivalence key만 deduplicate한다. birth-time bits, energy bits, absolute direction bits, birth geometry scale bits를 포함하고 ray를 먼저 검증한다. fixture pointer guard와 별도 identity가 clock·volume·source amplitude·thermal/geometry/threshold/density 의존성을 묶는다. kernel은 positive Gauss rule과 source-frozen path preparation을 재사용한다. 원 provider와 fit threshold **13.60 / 24.59 / 54.42 eV**를 바꾸지 않는다.

Persistent worker는 worker마다 native fixture를 새로 소유하여 geometry의 Rc/RefCell을 무리하게 Send/Sync로 만들지 않는다. 모든 결과를 받은 뒤 원래 index 순서를 복원하고 ledger 합산은 원래 template-major/node-minor 직렬 순서로 수행한다. 첫 오류도 원 index 기준으로 결정한다. 현재 코드의 worker 허용 범위는 **1–16**이다.

실제로 읽은 두 raw TIMINGS.csv는 각 40 rows(6 warmup + 28 paired + 6 A/A)다. 두 verification JSON도 읽었다. 각 부호 case는 384 templates / 3,648 births / 1,824 unique paths, **2 workers**이며 independent process는 case당 하나다.

| case | baseline/candidate raw byte parity | paired median speedup | 해석 |
|---|---|---:|---|
| signed minus | true | 1.8047291403760777 | 7 pairs, exploratory |
| signed plus | true | 1.7750685425916601 | 7 pairs, exploratory |

캐시 직렬은 minus 1.01848, plus 0.985805여서 일관된 wall 개선으로 수용하지 않았다. 6-session confirmatory gate는 수행하지 않았다. 이는 BRPERF의 frozen fixture 및 label 집합에서 완료된 관측이며 age lane의 57,344 labels나 evolving-gas native RHS에 대한 측정이 아니다. spectrum/opacity 준비를 native evolving gas에 사용하려면 해당 RHS 평가에서 변하는 density·temperature·source·geometry 의존성을 current identity로 묶어야 한다.

보고서의 native gas control 45 histories / 5,040 macrosteps와 frozen photon reference는 완료다. BASS의 `PERF05_BASS_NATIVE_COMBINED`는 별도 lane의 남은 과제다. age 작업 큐에 이를 자동 편입하지 않는다.

## 3. RUN19: T-only preparation의 정확한 범위와 비효과 사례

**pin:** PR211 `c9deb933761a8d2593d1176aee028cd423bdbc05`.
`native/src/gas_reference_rhs.rs`의 blob은 `b1b1be09524203f8a116d57bf47199061701b3d0`,
`rate_cubic/src/lib.rs`는 `99e0a1f5a4b0fef7d28775ae59e37b3da7c21a9e`.
두 source 본문을 읽었다. 전체 prefix는 `research/atomic_nuclear_ssot_20261017/run19/`이다.

- gas_rhs는 EOS를 각 입력에서 확인하고 동일 prepared T coefficient bundle을 H/He 및 D 조립에서 공유한다. density·opacity·photoheating은 T-only cache에 넣지 않는다.
- GasRateWorkspace는 backend lifetime에 묶인 bounded 1-entry cache다. 재사용 조건은 EOS T의 **정확한 f64 bits 동일성**이며 근사 tolerance cache가 아니다.
- gas batch는 caller-owned outputs와 worker별 workspace를 사용한다. cap은 **1–4 workers / 최대 65,536 states**다. scoped thread startup/join이 매 호출에 포함된다.
- cubic table은 source-certified branch에 맞는 4-node stencil, tag/floor/structural-zero guard, out-of-domain/blocked/nonpositive/non-normal fallback을 가진다. source+algorithm identity digest, bounded allocation, exact cache metadata 확인이 있다. 다만 이 보존 조건이 보간 오차 인증을 대신하지 않는다. 원 direct provider를 유지하는 첫 최적화와 구분한다.

실제 `execution/unit_b/core_measure01/stdout.txt`와 COMMAND.json을 취득했다. stdout 21,528 bytes, SHA256 `940c2c444c9e7c0a7c5f23d337ff557a6f8bc16bc8c80aa251f66a97e786b758`가 COMMAND에 선언된 값과 같다. 아래 수치는 그 raw JSON이다.

| input pattern | shared direct ns/RHS | exact-T cached ns/RHS | batch4 direct ns/RHS |
|---|---:|---:|---:|
| 4,096 states, EOS T bits 1개 | 737.0384521484 | 286.6945800781 | 171.0136718750 |
| 4,096 states, EOS T bits 4,096개 | 669.4470214844 | 787.3057861328 | 308.6135253906 |

측정은 affinity 0–3, 한 process, fixed-mode order, 5 repetitions, steady RHS이며 IVP는 0개다. varying-T의 cache hit가 0인 실제 반례가 있으므로 current native path에서 T cache를 켜기 전에 hit 기회를 구별해야 한다. H/He/D source-off gas 벤치마크를 photo-coupled age history wall speedup으로 바꾸어 말할 수 없다. 기존 RUN19 A/B/C 실행은 반복 대상으로 삼지 않는다.

## 4. VigilODE 새 branch-only code: 자체 gate 결과를 함께 재사용

| branch suffix | HEAD | UTC commit |
|---|---|---|
| a1-api | a605573e2cb4bcbb17c21db7866d4b22ab747011 | 18:09:24Z |
| a1-defects | a8ec412affef1333ccb83b0137f50cf8cecc490e | 19:08:52Z |
| a2-wfiltered | 7bea78c213df502aa8c21b38c925c467fdec660e | 17:58:50Z |
| b1-lagged | 16f66319f32085f13663f71be69a947d02100d54 | 17:57:19Z |
| t-verify | f2250b75ff3638974a88fc0f82c835b2f00ded6f | 17:43:43Z |
| vigilode-plan-20261021 | 9b5d0836c6a6fb59f4ec054b17fcd3c7b64cb323 | 17:35:39Z |
| wave1-integration | 148b515f137a46b663fff75b5c6a93e933c945a3 | 20:37:41Z |

시각은 모두 2026-10-20이다. PR78 `ebb5b81ebe77314b6fee941096fd6cba6d8597fc`, PR77 `9bb05bed4cd7df720f2b429c2b47e97ed76712d5`, PR76 `6972f28aa4bcbe4c68dbba92e44ff58884545bca`는 기존 pin 그대로다. 새 branch의 실행은 조회한 workflow25로 뒷받침되지 않으므로 committed node report의 실행 범위를 사용했다.

wave1 pin에서 a2/b1/t node report, lagged driver 실제 source의 refresh/iterate/attempt, 측정 test의 gate 구현을 읽었다.
W-filtered는 해당 step LU로 `(M-h gamma J0)^-1 (h/2)d(midpoint)`를 계산하는 관측자다. PR witness rtol 1e-6에서 interior error 0.350≤2는 PASS지만 accepted steps 15/7=2.143>1.3은 **FAIL**이다.
Lagged driver는 새 state에서 J0를 갱신하고 factorization만 lag한다. current JVP/matvec residual, θ=0.1, q_max=0.5, 최대 6 correction으로 refresh를 결정하며 abandoned work까지 센다. HIRES factorization/accepted 0.654>0.4, endpoint error ratio 1.587>1.5; Brusselator100은 0.854>0.4로 자체 성능 gate **FAIL**이다. 이는 방법의 모든 가능성을 배제하는 결과가 아니라 이 고정 후보와 witness에 대한 완료된 결과다.

현재 age native DOP853에는 해당 step LU가 없으므로 이 관측자나 RODAS5P 교체를 직접 붙이는 것은 같은 RHS 가속 문제가 아니다. current source/clock을 유지하는 v10 candidate에서는 준비/할당/배치 구조를 먼저 재사용할 수 있다. 양쪽 node report가 남긴 shared CARGO_TARGET_DIR의 다른 worktree artifact 혼합 사례는 source-specific target directory를 쓰는 구체적 빌드 근거가 된다. 이번 intake에서 이 테스트를 재실행하지 않았다.

## 5. v10 소유 작업에 적용할 구체적 선택

1. **물리 함수와 label 집합 유지:** 고정된 B1/source/clock/threshold/provider를 그대로 두고 Gauss nodes, immutable tables, exact argument preparation을 RHS 평가 단위로 재사용하는 후보를 우선한다. frozen-opacity cache의 lifetime을 evolving gas step까지 연장하지 않는다.
2. **입력·출력 순서 유지:** 같은 source context 내 독립 path 계산만 worker-local context로 병렬화하고 결과는 원 index에 저장한다. 최종 floating reduction은 기존 순서로 유지한다.
3. **NCP resource contract를 먼저 구체화:** 64 cores / 128 GB는 요청한 호스트 규모다. 이번 GitHub 증거는 그 host의 affinity, 실제 사용 가능 RAM 또는 64-worker 성능 측정이 아니다. scheduler는 실제 affinity와 허용 cap을 읽어 합계 worker budget을 정하고 case별 메모리 추정/관측을 기록한다. 기존16/4 cap을 조용히64로 치환하지 않는다.
4. **이미 완료된 캠페인을 큐에서 제외:** v9 age32/64, v7 benchmark, v8 certificates는 root의 현재 증거와 함께 재사용한다. 이번 intake에서 확인한 LRS19, BRPERF frozen photon/gas controls, RUN19 A/B/C 및 VigilODE 고정 gate 측정도 반복 큐에 넣지 않는다. 별도 LRS/BASS/owner lane의 미완료 항목은 이 작업의 owned workload가 아니다.
5. **scope를 유지한 검증:** 이식한 정확한 cache/pool variant에서 scientific result parity, original label order, error propagation, context invalidation을 확인할 수 있다. 외부 후보의 speedup 숫자는 자신의 native workload 완료를 대신하지 않는다. 실제 nonlinear Grackle response/path-exposure bound는 이 intake로 새로 성립하지 않는다.

## 원본·hash·보존

`INTAKE_RECEIPT.json`은 범위와 실행0을, `SOURCE_MANIFEST.json`은 각 retrieval의 repo/ref/path, byte count, SHA256, Git blob 및 실제 가능한 기대 blob 비교를 기록한다. `objects/*.retrieval.json`은 immutable GitHub URL에서 얻은 raw text를 보관하고 `sources/`는 그 UTF-8 bytes다. directory listing은 source blob으로 오인하지 않는다.

초기 파일-format 처리에서 raw Markdown을 metadata JSON으로 해석하려던 parsing attempt가 한 번 있었다. 그 중간 `objects/lrs_return_report.json`은 canonical source가 아니며 manifest/admission에서 제외한다. 정확한 재취득은 `objects/lrs_return_report.retrieval.json` 및 `sources/lrs_return_report.md`이고 실제 Git blob과 일치한다. 이 오류는 native 실행 실패나 현재 GitHub connector 장애가 아니다.

