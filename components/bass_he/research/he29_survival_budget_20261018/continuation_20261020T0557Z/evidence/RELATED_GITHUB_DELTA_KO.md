# HE29 관련 GitHub 새 게시 조사 — 2026-10-20 05:57Z continuation

**조회한 관련 GitHub 게시 표면에서 새 HE29 기준해 반환은 0/4다.** 새로 게시된 일반 ODE·LRS·HH·BASS·REC 결과는 원래 게시 source와 binary identity를 읽고 각각의 연구 범위로 분류했다. 이 intake에서는 코드 변경, 문헌 검색, benchmark·기존 과학 실행·tests 재실행을 하지 않았다.

- 변경 기준: **2026-10-20T02:32:00Z 이후**.
- 마지막 GitHub 읽기 이후 시계 확인: **2026-10-20T06:06:42Z**.
- 상세 응답 요약·28개 읽은 source 문서의 URL/commit/UTF-8 SHA256: [RELATED_GITHUB_DELTA.json](RELATED_GITHUB_DELTA.json).
- 활성 절차는 standalone **physmath-research-loop 1.0.0**이며, 과거 1.3.0 작업은 재사용 근거다.

## 1. HE29 계약과 새 결과 분류

원래 코드·테스트 revision은 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, Rust owner는 `f7830e2f55e7a1938bc3c98f61b60651f8dae474`, VigilODE 실행 pin은 `a21d573980f66fe02891bd216153443b5352f921`이다. 실제 [owner ref](https://api.github.com/repos/cosmosapjw-quantum/rei_bianchi/git/ref/heads/research/bass-he-optical-depth-transfer-20261015)는 바뀌지 않았다. 필요한 반환은 m8/GL4/q0의 (r2,512), (r4,512), (r8,512), (r4,1024), 각각 Radau+DOP853와 같은 model/table의 source·binary binding이다.

| 새 게시 | 읽은 실행 identity·결과 | HE29 분류 |
|---|---|---|
| [VigilODE PR76](https://github.com/cosmosapjw-quantum/vigilode/pull/76), `6972f28a…` | run39360536475: source `aaa8116c…`, binary `5495f7a9…`; 312 timing cells, 26 matched+4 diagnostic pairs. 더 뒤의 저장 run39361183318은 source `df2f4fb1…`, binary `d42ee2e0…` | 기존 stiff benchmark와 자율 few-mode-96 Riccati 모형. HE29 기준해 아님 |
| VigilODE hybrid 활동 branch, `2b828f81…` | 새 generated reflecting-grid 모형 및 structured-AD API. 관측한 run39377432935의 bounded-research step은 failure, evidence 보존 step은 success | 현재 HE29 source/binary/table binding 없음. 이 조회에서 새 numerical completion을 수용하지 않음 |
| [REI PR198](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198) LRS | 최초 `d07c3266…` 뒤 조회 중 `33ae18c3…`가 새 게시됨. baseline source `d87ba9ca…`, VigilODE `8a8bd409…`, candidate binary `24f9d38e…`, batch binary `b0a2f47e…` | 같은 19 LRS 설정의 새 국소 최적화 검증. HE29 아님; 이번 NCP 최적화는 NOT_RUN |
| [REI PR199](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199), `cf006847…` | 57,344-node 고정 opacity/gas 모형의 정확 산술·cache·oracle 측정. 새 nonlinear native history와 age32 실행 0 | 고정 연산자 연구; HE29 기준해 아님 |
| REI RUN19 Unit A, `f2996d02…` | original source `99e07bcf…`; RHS server `b59383e6…`, bench binary `4bfdf468…`. source-off T 계수 공유·순간 RHS·IPC/batch 측정; 새 gas/transport IVP 0 | 별도 HHeD owner의 RHS 구현 측정; HE29 기준해 아님 |
| [HH PR120](https://github.com/cosmosapjw-quantum/WU088_HH/pull/120), `31745376…` | HH m0/D2, L28의 저장 work-precision 18개; binary `303efb12…`, 원 고정 certificate 사용 | 다른 HH 모형·입력. HE29 기준해 아님 |
| [bass PR174](https://github.com/cosmosapjw-quantum/bass/pull/174), `8138a014…` | S9 source `4b30957c…`, binary `69de3e87…`; manufactured donor/collisionless cohort의 새 8/8 이력 | 실제 새 실행이지만 HE29 thermochemistry/table 기준해 아님 |
| [REC PR110](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/110), `e2b39e33…` | audit library `7e6f4bde…`, ABI smoke binary `38edba45…`; 보존된 R3M stream의 differential audit 15회, new_physical_steps=0 | 원 HyRec2012/R3M 결과 감사 최적화. HE29 기준해 아님 |

원래 물리식·reaction rate·허용치·절대 fraction 1e-11 gate를 바꾸지 않았다. 관련 lane의 다른 table이나 certificate를 HE29 table512/1024 identity로 대신하지 않았다.

## 2. 이전 census와 실제 차이

VigilODE는 152→153 refs이며 **새 hybrid branch 1개**, 기존 midcheck branch의 HEAD 변경 1개가 있었다. 다른 refs는 이전 저장 목록과 같았다. default **main은 `8d0c79184e09efb5bdadc24a6315c60a71a44264`**, 별도 활동 branch `claude/nice-dijkstra-208xq0`는 **`c03ca90f19a9e64ba7751c069325a48b54b39c2e`**로 유지됐다. PR71/73/74/75 HEAD도 이전 검토와 같아 연구를 반복하지 않았다.

REI는 250→251 refs이며 RUN19 branch 1개가 새로 생겼고 LRS·age branch 2개가 변경됐다. PR207 RUN17, PR208 BR06, PR209 RUN18은 기존 HEAD·게시 근거를 재사용했다. LRS는 이번 읽기 도중 추가 push가 있었으므로 최초의 C5 IN_PROGRESS 기록을 최종 상태로 남기지 않았다. [최신 ROOT_ADMISSION](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/optimization_20261020/ROOT_ADMISSION.json)과 [SOURCE_IDENTITIES](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/optimization_20261020/coder/experiments/SOURCE_IDENTITIES.json)를 추가로 읽었다. 이 새 등가성 비교는 signed-zero bit equality까지 시험한 것으로 기록하지 않는다.

bass_cr의 pushed_at은 2026-10-19T09:24:31Z로 기준 시각 전이고 새 PR/Actions는 발견되지 않았다. HH·bass·REC에는 각각 위의 새 PR 또는 HEAD 변경이 있었다. 이 세 저장소의 오래된 전체 branch census는 반복하지 않았고 최근 PR·Actions·push metadata와 변경 파일/source를 조사했다.

처음의 `cosmosapjw-quantum/recagent` 조회는 repository·PR·Actions 모두 HTTP404였다. 부모가 기존 기록의 canonical을 `rec_bianchi`로 확인한 뒤 그 저장소를 실제 조회했다. 이 별칭 오류는 보존했으며 canonical 접근 차단으로 분류하지 않는다.

## 3. Actions·새 문헌/API의 범위

기준 시각 이후 생성된 Actions는 첫 관측에서 VigilODE 7개, REI 11개, REC 9개였고 나머지 세 저장소는 0개였다. 모든 해당 응답의 total_count와 반환 행 수가 일치했다. REC 한 run은 그 응답에서 in_progress였으므로 완료라고 바꾸지 않았다. 이전 VigilODE census에서 진행 중이던 ignored-long-tests 3개는 별도 GET에서 success로 확인했지만 HE29 실행 결과로 세지 않았다. run39360536475의 artifact 목록은 0개였고 결과는 Git에 게시된 파일에서 읽었다.

[PR76 SUMMARY](https://github.com/cosmosapjw-quantum/vigilode/blob/6972f28aa4bcbe4c68dbba92e44ff58884545bca/research/midcheck_20261020/runs/39360536475/SUMMARY.json)와 [REPORT](https://github.com/cosmosapjw-quantum/vigilode/blob/6972f28aa4bcbe4c68dbba92e44ff58884545bca/research/midcheck_20261020/REPORT_KO.md)는 실제 달성 오차의 정합 여부를 구분한다. 네 diagnostic pair를 공정한 외부 solver 속도 순위로 승격하지 않는다. 비교 source·binary는 HE29가 아니며 그 속도를 HE29 예상값으로 옮기지 않았다.

새 hybrid의 [PLAN](https://github.com/cosmosapjw-quantum/vigilode/blob/2b828f81512a11cc35229bc77453f305df33d268/research/hybrid_20261020/PLAN.md), [구조 수정 계약](https://github.com/cosmosapjw-quantum/vigilode/blob/2b828f81512a11cc35229bc77453f305df33d268/research/hybrid_20261020/AMENDMENT_01.md), [공개 module](https://github.com/cosmosapjw-quantum/vigilode/blob/2b828f81512a11cc35229bc77453f305df33d268/crates/vigilode-hybrid/src/lib.rs)은 생성된 grid/reaction 식을 전제로 한다. feature-native의 NativeRun/solve_trajectory와 kernel API가 있지만 임의 callback·mesh·PDE 오류로 certificate를 확장하지 않는다고 source 자체가 명시한다. HE29의 frozen f64 owner용 일반 Schur hook을 새로 확보했다거나 a21을 교체했다고 주장하지 않는다.

## 4. 재사용·새 실행·남은 의무

[기존 VigilODE intake](../../optimization_20261020/evidence/VIGILODE_GITHUB_INTAKE.json), [기존 REI intake](../../optimization_20261020/evidence/REI_GITHUB_INTAKE.json), [관련 저장소 intake](../../optimization_20261020/evidence/RELATED_GITHUB_INTAKE.json)를 재사용했다. HE28 pilot/study, HE29 source 검증과 기존 transport6, 기존 Schur·callback/FFI 검사 및 이미 완료된 mixed-difference 분석을 반복하지 않았다.

이번 28개 문서의 source hash 계산은 저장 근거를 식별하기 위한 작업이다. 첫 묶음은 shell argument 길이 제한으로 process 생성 전에 거절되어 작은 묶음 13개로 계산했으며, 과학 실행이나 benchmark 실패가 아니다. 원본 GitHub 문서에 있던 local 경로·실행 환경 문자열은 공개 요약 JSON에 복사하지 않았다.

GitHub 읽기는 하나의 원자적 시점이 아니다. 반환된 commit·run timestamp를 유지하며 조회 도중 발견된 LRS 추가 게시를 반영했다. 게시되지 않은 NCP process의 상태는 이 조사에서 관측하지 못했다. 결과는 부모의 BASS_HE·백업 intake와 합쳐 다음 연구 착수 여부를 판정하는 근거이며, 네 HE29 native pair의 완료나 제출을 뜻하지 않는다. 연속 스펙트럼·기체온도 전역 오차상한·전체 EoR·upstream Grackle 전체 동등성·관측 Bianchi/CMB의 HOLD를 유지한다.

