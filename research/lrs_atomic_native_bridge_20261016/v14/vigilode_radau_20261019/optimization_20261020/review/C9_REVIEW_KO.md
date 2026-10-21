# C9 독립 구현·과학 검토 — 2026-10-20

**판정: 검토한 유한 범위에서 PASS 권고. 현재 게시를 막을 코드·과학 결함은 발견하지 않았다. 최종 과학적 admission과 게시·백업은 root 소유다.**

검토자는 실제 child /root/opt20_intake_theory (Astra)다. 이 child는 C3 수학 구조를 조사했지만 신규 Rust/Python/C 구현을 작성하지 않았다. 이번 C9는 신규 diff와 실행 증거에 대한 한 회의 독립 구현 검토다. 새 build, native history, benchmark, Git write 또는 upload를 수행하지 않았으며 기존 원시 자료만 읽고 비교했다.

기준 계약은 optimization_20261020/OPTIMIZATION_CONTRACT.md다.
physmath-research-loop v1.3.0 SKILL/STAGE_SELECTION/CODING_LOOP C9,
SUBAGENT_MODE/POLICY_INTEGRATION 및 resume_20261020/github/AGENTS.md의
유한 검토·물리 기준 동결·결과와 provenance 구분을 적용했다.

## 1. 검토 대상과 소스 연결

coder/patch_files의 src/lib.rs, src/main.rs, native_additions/axbi_native_rhs.rs,
native_additions/transport_hook.txt, prepare_and_run.py, src/bin/lrs_batch.rs,
optimization_20261020/{batch_experiment.py,batch_interleaved.py,memory_probe.py,wait4_probe.c}와
coder/experiment.py, adapter.diff, 실제 baseline/compiled source tree를 읽었다.

- Case binary: 24f9d38e56d3380e830478b8afe7760b2f44fff7ab60167ed14aa668ae7f4ac0.
- 보존된 unchanged baseline binary: 28dfc8dbfe627acd7c7d2f77c08746db6d5f67f620b6e6a38a1b658c52eebc2d.
- Batch binary: b0a2f47e58d0b5d94804ac919c257be81503f55874ece5e82901349a6533b096.
- 최종 delivery runner: 75c56fe1418df437b9ccb3ce35daa63f47190b207d83e3112ce14aede078bbe6.

Prepared source tree와 patch의 Rust lib/main/native module/batch source가 일치했다.
C10의 pinned VigilODE source 477개 파일을 현재 compiled input tree와 직접
비교한 결과 byte mismatch가 없었다. 검사한 native src/*.rs에서 바뀐 것은
additive axbi_native_rhs.rs 및 export hook을 추가한 axbi_covariant_transport.rs뿐이다.
후자의 기존 파일 전체 prefix는 보존됐고 기존 prepared parent 뒤의 추가분은38bytes다.
이 source byte 확인과 아래 수치 비교는 서로 다른 identity 주장이다.

## 2. 핵심 cache의 정확성 판단

NativeCellCache는 immutable transport를 빌리고 base PhotonState, cell별
PreparedCell, 고정 ray_scales를 소유한다. NativeCellCache::prepare는 native
validate_state를 먼저 호출하며 shape/index 오류, support 변화, 지정한 cell
이외 N/U 변화, changed=None인 상태변화를 거부한다. Cache API에 새로운
geometry를 받지 않으므로 다른 geometry 입력으로 조용히 재사용하지 않는다.
실제 Context::jacobian이 매번 새 cache를 만들고 chemical_step마다 Context를
새로 생성하여 source birth/geometry 변화 이후 캐시가 넘어가지 않는다.

Base 준비와 photon ± 준비는 원래 prepare_cell/cell_quadrature/provider를
그대로 사용한다. threshold split, beta-dependent panel 수, steep node 위치,
endpoint/delta 처리도 이 원래 경로를 따른다. 변경되지 않은 cell 준비만
재사용한다. 노드는 cell index와 각 cell 내부 순서대로 이어 붙인다.
NativeAbsorptionRates의 photon compensated sums와 모든 gamma/event/binding/
heat ordinary sums의 산술식·연산순서는 변경되지 않았다. 전체 합에서
old-cell 값을 빼고 new-cell 값을 더하는 재결합도 없다.

Base cached Jacobian과 ± evaluate_cached 모두 budget charge를 admissibility보다
먼저 수행한다. Central/one-sided FD 수식과 eps는 원래 코드 그대로이고
Fatal을 domain fallback으로 바꾸지 않는다. Plus Fatal이면 minus를 계산하기
전에 중단한다. Cache는 immutable base여서 실패한 replacement가 다음
perturbation에 남지 않는다. 최종 candidate commit 전에는 원래 physical state와
ledgers를 교체하지 않는 transactional chemical_step도 유지됐다.

## 3. 실제 컴파일·focused 실패와 통과

실제 build_repair inputs의 명령은 locked/offline/release/jobs=2다.
Exit0 및 compiler Finished release를 읽었다. Focused repair는 exit0,
4 unit tests와6 integration tests가 실제 stdout에서 통과했다.
4 unit에는 기존 classification test1개와 신규 cache test3개가 포함되므로,
기존7개에 신규3개를 더한 총10개다.

Native seeded state의 모든84열 FD 비교는 수치 차이0이며 charged RHS169회가
두 경로에서 같았다. 준비 횟수는6760→200이다. Empty d=4는9 RHS와 준비0,
delta d=5는11 RHS와 준비11→3으로 실제 출력됐다. Cache stale support/index/
shape, changed-cell steep/threshold 준비 및 resource failure rollback도 검사됐다.

초기 focused 실행의 exit101과 AXBI_COVARIANT_SUPPORT_DOMAIN 실패를 읽었다.
잘못된 steep fixture의 지원구간 입력을 수정한 뒤 원래 domain 검사로 통과한
것이며 실패 증거가 보존됐다. 물리 허용오차를 완화하여 통과시킨 흔적은 없다.

## 4. 원시 출력의 독립 비교

Coder의 issues=[] 요약을 신뢰하는 데 그치지 않고 별도의 읽기 전용 flatten
비교로 actual raw/reference, exit, completed, 배열 길이와 scalar type/value를
대조했다. 제외한 것은 JSON 최상위 wall_s와 새 native_evaluation metadata뿐이다.

| 기존 실행 자료 | 직접 읽은 범위 | 결과 |
|---|---:|---|
| Cached correctness matrix | 19설정, scalar/shape329,983경로 | 차이0, exit0, completed=true |
| Profile-off paired samples | 3설정×5쌍=30개 출력 | 차이0, exit0, profile OFF, CPU0 |
| 초기 batch campaign | 12batches/36children | 차이0, 모든child/batch exit0 |
| 한정 interleaved correction | 9batches/27children | 차이0, 모든child/batch exit0 |
| Small-C memory observations | 4children | 차이0, helper/child exit0 |
| 최종 runner flag forwarding | fixed/radau/N2 | 실제 CellCache/profile ON, 차이0, exit0 |

수치 비교는 **finite numeric exact equality**다. Rust assert_eq와 Python
numeric equality는 signed zero의 IEEE bit 차이를 검사하지 않으므로
수치 출력의 bit-identical 또는 bitwise equality를 주장하지 않는다.

P/C/R/D, photo_binding/photo_heat, CE/RR/DR/FF/CMB/escape,
ci_floor/ce_cap/excluded_dr 및 endpoint/state/ledger/residual 자료가 포함됐다.
19설정의 원시 JSON에서 null은 $.failure뿐이었고 NaN/Inf가 없었다.
배열 길이, missing key, raw completion과 종료코드도 함께 확인했다.
이 비교를 과거19설정 이외의 새 unique physical histories로 세지 않는다.

근거 파일:
C9_INDEPENDENT_RAW_READ.json,
C9_BATCH_RAW_READ.json,
C9_MEMORY_RAW_READ.json,
C9_FINAL_RUNNER_AND_INTERLEAVED_RAW_READ.json.

## 5. 성능·profile·메모리 해석

Profile-off serial samples는 같은 candidate binary와 frozen setting을 사용하고,
각 process를 taskset CPU0에 고정하여 AB/BA를 교대로 실행했다.
Native wall과 process wall은 별도다. 이 유한 세 설정의 측정 speedup 주장을
허용할 근거가 있다. 모든 설정·machine·stiff regime으로 일반화하지 않는다.

Profile의 preparation/rates/provider/other는 evaluate_native 안의 배타 구간이고,
cache 생성 비용은 preparation에 별도로 더해진다. Budget/admissibility 및
전체 solver/setup 시간을 모두 포괄하는 분할은 아니다. Jacobian 시간은
이들과 중첩되는 inclusive 값이므로 합산하면 안 된다.
Profile OFF에서 then(Instant::now)는 실행되지 않으며 fine-grained timing은
꺼져 있다. 기존 wall cap을 위한 clock은 유지된다.

고정N16 전체의 준비수119680→14720과 한84차원 Jacobian의6760→200은
다른 단위다. 각각 약8.13배와33.8배의 준비 작업 감소이며 전체 wall 비율과
혼동하지 않는다. Charged RHS와 node replay 횟수는 변하지 않았다.

초기 serial runner의 RUSAGE_CHILDREN.ru_maxrss는 누적 child high-water이고,
batch에서 /usr/bin/time이 없는 경우 peak_rss_kb=null이다. 이를 개별 native
peak로 읽으면 안 된다. 큰 Python parent에서 fork한 이전 두 memory 값은
pre-exec RSS bias 가능성으로 NOT_ADMITTED 처리된 것이 타당하다.

새 small C fork→exec→wait4 helper의 source/hash/build exit와 네 child rusage를
직접 확인했다. Legacy6400/6396KiB, cell-cache6552/6456KiB다. Python은 child
helper가 모두 끝난 뒤 큰 JSON을 읽는다. 네 관측의 기술통계만 허용하며
메모리 감소를 주장하지 않는다.

## 6. 병렬 구현·실패 보존과 한정된 throughput

Pinned VigilODE ParallelExecution::rayon 및 map_ordered를 직접 읽었다.
Width1은 sequential, width>1은 local Rayon pool이다. 각 slot에 서로 다른
CPU를 할당하고 한 slot 내 history는 직렬이며 각 child는 기존 thread1
native binary다. Width4에서도 jobs가3개이므로 실제 useful concurrency는3이다.

Rust batch는 child마다 timeout30s/kill grace2s를 두고 stdout/stderr/inputs를
보존한다. 실패 child를 JSON report에 남기고 같은 slot의 남은 작업을 멈춘다.
Closure는 실패를 report로 수집하므로 다른 이미 시작된 slot 결과도 수집한다.
전체 batch는 failure일 때 nonzero로 반환한다. 초기에 /usr/bin/time 부재로
발생한 child127과 batch실패도 실제 보존되어 있다. Optional RSS fallback 뒤
성공한 출력에서는 RSS가 null로 정직하게 표시된다.

폭을 순차적으로 몰아서 실행한 초기 batch timing은 drift가 크다.
해당 결과를 과학 오류로 삭제할 이유는 없지만 최종 scaling 표의 근거로
과장해서는 안 된다. 하나의 구체적인 interleaved correction은
[1,2,4],[4,1,2],[2,4,1] 순서이며 큰 raw 비교는 측정 완료 뒤 수행한다.
실제 median batch wall은1.7144622,1.000238744,0.892771737s,
관측 median ratio는1.71405와1.92038이다. 여전히 drift가 있고 3job만 측정했으므로
이번 환경의 diagnostic batch throughput으로 한정한다. 이를 single-history
속도 향상, 4배 scaling 또는 일반 병렬효율 정리로 확대하지 않는다.

## 7. 최종 delivery runner

기존 prepare_and_run.py의 native source 복원/검사/빌드 경로는 유지됐다.
새 --native-eval과 --profile을 argparse로 받고 run_cases의 네 positional
argument 뒤에 전달한다. Default legacy도 유지된다. Src directory를 통째로
복사하므로 새 src/bin/lrs_batch.rs도 prepared adapter에 포함된다.

기존 Python runner4개 테스트의 실제 exit0/stdout을 읽었다.
별도의 native forwarding smoke는 inputs argv에 cell-cache/profile이 있고,
실제 raw mode=CellCache, timings_enabled=true, completed=true다.
Exit0/truncated=false와 기존 fixed/radau/N2 scientific output 차이0을 확인했다.
이 smoke는 기존 설정의 delivery 경로 확인이며 새 과학 이력으로 세지 않는다.

## 8. 판정의 경계와 종료

현재 수정이 필요한 scientific blocker는 없다. 처리된 fixture/optional-RSS
실패는 과거 실패 증거로 유지한다. 메모리·throughput·profile 해석 제한은
보고 문구의 경계이며 새 검증 campaign을 요구하는 gate가 아니다.

Source-on 전체2차, uniform stiffness, general positivity, CaseB/fullEoR,
signed Bianchi, positive CMB/nonzero boundary 및 global certificate는 모두
기존 HOLD를 유지한다. PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED다.

이 C9를 종료하고 root가 검토된 소스·유한 성능 결과를 게시·백업할 것을
권고한다. 이 child의 publication/backup 상태는 PARENT_OWNED_PENDING이다.

