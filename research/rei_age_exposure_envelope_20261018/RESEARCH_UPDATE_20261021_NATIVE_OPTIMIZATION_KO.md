# V10 연구 업데이트: subnormal 표현 수정과 미완료 native time 캠페인

## 결과와 현재 위치

**기존 N2·N3·N4의 subnormal moment 실패를 원래 count/energy 허용오차를 바꾸지 않고 해결하는 제한된 지지점 완화를 구현했다. 독립 cohort 흡수 평가를 병렬화하고, 쓰이지 않는 전체 상태 복제를 줄였으며, accepted chemistry 단계의 이산 BE kernel을 관측하는 코드를 연결했다.** 남은 이 lane의 native 실행은 time8·time16·time32다. 새 캠페인은 이 세 case만 묶어 실행한다.

V9 최종 배송 HEAD `abbf71caf4bd45af5bdf8bc7744690d10b8715e7`에서 이어졌다. 이번 새 intake에서 PR199는 이 HEAD 그대로였고 draft/open이었다. 완료된 native age32·age64·spectral128, v7 benchmark, v8 고정 모형 계산, v9 저장 자료 분석을 재실행하지 않았다. 새 NCP native 결과는 현재 확인 범위에서 발견되지 않았다.

새 단위는 [native_optimization_20261021](native_optimization_20261021/README.md)다. 이론·코드·원자료·독립 검토를 한곳에 보존했다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`. Native age/time 수렴 판정은 HOLD이고 실제 nonlinear Grackle response bound는 NOT_ESTABLISHED다. 새로운 실행 READY는 이 수렴 판정과 별개인 탐색 실행 권한이다.

## 먼저 확인한 새 근거

GitHub에서는 REI 253 branches·최근 updated PR100, VigilODE 161 branches·PR78·최근 workflow25를 확인했다. 선택한 실제 source/raw/report25개를 읽었고, 그중18개는 별도의 원격 Git blob identity도 대조했다. Drive 직접 파일133개와 Dropbox 직접 파일31개를 확인했다. Root의 다른 대화 검색도 이번에는 실제 성공했다. 모든 대화·모든 과거 archive를 읽었다는 뜻은 아니다. 반환 excerpt 범위, global cloud 검색의 누락, 재검산하지 않은 큰 raw archives를 [intake](native_optimization_20261021/intake/README.md)에 구분했다.

LRS PR198의 새 HEAD `82364d3d2548a1e864468cb781336f825fc18c29`는 기존 반환의 admission/handoff 수정이었다. 실행 source5248822의19 settings·38840 RHS·mismatch0은 재사용 근거이며 새로운 실행으로 중복 계산하지 않았다. BRPERF PR210의 실제 photon worker 코드는 persistent worker와 worker-local 입력, index 회수·직렬 합산의 설계 근거로 사용했다. RUN19의 current-temperature exact cache는 읽었지만, evolving gas에서 opacity를 고정하는 cache나 다른 lane의 근사 rate provider는 가져오지 않았다. VigilODE W-filtered/lagged-LU의 일부 gate 실패도 그대로 기록했다.

SciSpace·Exa 검색은 성공했다. Wolfram context 호출은 internal error였으나 evaluator는 실제 성공해 두 모멘트 구성·분산식·BE 단조성·log 식을 확인했다. Binary64 성공이나 nonlinear native 해의 인증은 CAS 결과에서 추론하지 않았다. 참고 문헌과 실제 사용 범위는 [literature receipt](native_optimization_20261021/literature/LITERATURE_RECEIPT.json)에 있다.

## 구성적 수치 수정

원래 fixed-support 실패는 양성 photon 분포 자체가 존재하지 않는다는 결론이 아니다. 양성 질량 `N>0`, 일차 모멘트 `U`, support `[a,b]`에서 정확한 평균 `m=U/N`이 support 안에 있으면 `N delta_m`은 두 모멘트를 보존한다. N4의 `N=10 eta`, `U=245 eta`, `eta=2^-1074`에는 `q=24.5`가 직접적인 구성이다.

구현은 원래 moment gate가 실패한 경우 중 finite `0<N<f64::MIN_POSITIVE`에만 적용한다. `U/N`과 support 안의 인접 표현 가능 후보를 제한적으로 검사하고 원래 compensated count gate와 energy gate를 모두 통과해야 받아들인다. Normal 질량은 원 quadrature를 유지하며, 후보가 모두 실패하면 원 실패를 보존한다. 모든 subnormal 문제의 완전한 해결법으로 주장하지 않는다. Repair count·최대 질량 bits·첫 cell의 입력/후보 bits와 전후 defect를 기록한다.

같은 질량 N의 양성 측도 두 개가 `[a,b]`에 지지되면 유계 관측량 f의 로컬 차이는 `N*(sup f-inf f)` 이하이다. C2 조건에서는 평균 주위 Taylor 전개와 분산 상한 `(b-m)*(m-a)`로 더 작은 조건부 상한을 얻는다. 실제 first-moment residual을 포함해야 하며 machine energy defect가0이라고 실수 residual까지0인 것은 아니다. 실패한 rounded vector의 질량이 N과 다르면 동일 질량 가정을 확인하지 않고 이 식을 적용할 수 없다. 자세한 유도와 범위는 [THEORY_KO.md](native_optimization_20261021/THEORY_KO.md)에 있다.

## 실제 native 적분기와 관측량 연결

미완료 native time 경로의 chemistry는 준비한 노드에 `w/(1+dt*c*opacity)`의 backward-Euler 감쇠를 적용한 후 공유 gas Newton 식을 푼다. 완료된 age32·age64 positive 기준해의 logarithmic DOP853 경로, v8 고정 exponential 계산과 적분 연산자가 다르다. 따라서 time case와 age32의 비교는 동일 입력 계보를 갖는 유한 차이 진단이며 같은 적분기 내 time 수렴 인증으로 쓰지 않는다. Time8↔16, time16↔32는 별도로 비교한다.

새 observer는 Newton trial이 아닌 accepted chemistry 뒤에서 실행된다. Cohort별 입력 N, 준비 질량 Q, 출력 N, dt, 실제 저장 분모의 min/max, 양성 노드 수, outward Q/S 구간을 streaming JSONL로 기록한다. 원 분모 연산 결합 `1.0 + dt_s * c * opacity`를 유지한다. `1+dt*(c*opacity)`로 재결합하면 실제로1ULP 차이가 날 수 있다.

저장된 양성 weight와 저장된 denominator를 정확한 유리수로 해석하면 `Q_lo/d_max <= sum(w_i/d_i) <= Q_hi/d_min`이다. 인증 이름은 `STORED_DENOMINATOR_DISCRETE_BE`다. 연속 물리 hazard의 전 구간 supremum, unrounded 물리 계수, nonlinear gas response를 감싸는 상한은 아니다. 동일 cohort의 검증된 전달에 한해서 `N_after/N_before = kappa*rho*exp(-E)`로 재구성 질량·출력 집계·이산 유효 exposure를 구분할 수 있다. 현재 구현 인증은 per-step kernel 범위다. 실패 전체 실행의 accepted prefix는 INCOMPLETE로 보존한다.

## 병렬화와 실제 가벼운 측정

기존 persistent OrderedWorkerPool을 재사용해 각 cohort의 `PreparedAbsorption.evaluate`를 병렬 처리한다. 결과를 원 index로 회수한 뒤 photo Gamma·heat를 원 cohort 순서로 합산한다. 물리 연산의 합 순서는 worker 완료 순서에 따라 바뀌지 않는다. Worker pool의 중첩 제출이나 새 Rust dependency는 없다.

Native trace는 최종 출력에서 쓰는 common8 관측의 pre/post 상태와 final state를 유지한다. Time8·16·32에서 기존1000·1968·3904개의 전체 상태 snapshot 대신 필요한9개의 저장 시각으로 줄이는 설계다. 출력 관측은 기존18 pre/post records를 유지하고, 실제 physics stepping은 동일하다. Accepted-step scalar observer는 별도 streaming이다. Snapshot 수 감소를 전체 RSS 또는 wall speedup으로 환산하지 않았다.

Source8/n_mu8/transport16의 실제 native 준비 입력으로32 cohort jobs를 만들고, sample당20회 평가·구성별5회로 새 흡수 커널만 측정했다. Shared-gas RHS·IVP·시간 이력은 실행하지 않았다.

| 구성 | 5회 wall 중앙값 | 원 직렬 대비 비율 | 과학 출력 |
|---|---:|---:|---|
| 원 직렬 cohort loop | 0.009680326 s | 1.0000 | 기준 |
| Ordered pool 1 | 0.009681998 s | 0.9998 | 모든 fields bit-identical |
| Ordered pool 2 | 0.006849993 s | 1.4132 | 모든 fields bit-identical |
| Ordered pool 4 | 0.004608712 s | 2.1004 | 모든 fields bit-identical |

이것은 cgroup8 CPU·8GiB sandbox의 해당 kernel 측정이다. NCP64코어 속도향상이나 전체 native campaign wall 측정은 아니다. 모든20 raw samples와 입력·출력 parity는 [MICROBENCH.json](native_optimization_20261021/verification/MICROBENCH.json)에 있고 [timing plot](native_optimization_20261021/verification/KERNEL_TIMINGS.png)으로도 보존했다. 기존 v7 benchmark를 다시 돌린 것이 아니다.

## 검증과 검토

Original native153에서 생성한 task-only overlay를 Rust1.94.1로 실제 컴파일했다. N2·N3·N4 captured failures가 원 gate를 통과했고, normal-path 보존·잘못된 입력 거부·worker1/2/4 동일성을 확인했다. 작은 실제 native 실행 네 개에서 serial/parallel, observer OFF/ON, full/compact trace의 endpoint·observations·native_return 파일 bytes가 모두 일치했다.

처음 설정한 transport4, n_mu2, source1 제어 입력은 기존 domain/normalization gate에서 trajectory 시작 전에 거부됐다. 실패 stdout/stderr/receipt를 보존한 뒤 유효한 최소 domain인2birth/n_mu8/source8/transport8로 검증했다. 원 gate를 완화하지 않았다. Local light cap240s와 별도 build cap120s를 구분하며, 구현 누적 light는9.371467903998564/240s, 별도 build는10.375765744000091/120s다. 독립 R6 algebra controls7개는0.023791467989212833s이며 별도 기록했다. Python changed-risk tests10개와 captured Rust controls가 PASS다. R6/C9는 모두 PASS_SCOPED, 열린 지적0개다. C9의 네 항목(timeout 출력, 중단 child 재개, 부적격 결과 분석 차단, B1/new BE 분리)을 수정했고, 두 namespace 회귀 실패도 debit/raw에 포함했다. 전체 historical suite는 반복하지 않는다.

## 64코어·128GB NCP 실행 계획

실제 가용 자원이 확인된 유휴64코어 host에서는 **time8·16·32 세 case × transport workers20 + 각 main lane1 = 최대63 CPU slots**로 실행한다. BLAS/OpenMP는1이다. Case당 address-space cap24GiB, 큰 host의 메모리 reserve16GiB로 설계했다. Affinity·cgroup quota·현재 available memory를 관측하고 공유 host에서는 명시된 실제 가용량 아래로 줄인다. 다른 lane 실행을 중단하거나 죽이지 않는다.

Case당1800s, aggregate child wall5400s, three-way elapsed2000s, 별도 build300s다. 동시 job 수가 줄면 elapsed cap은 `ceil(3/jobs)*1800+200`으로 최대5600s다. 이전 attempt의 wall debit을 유지하고 완료된 동일 identity 결과는 hash를 확인해 재사용한다. 실패·중단·손상 결과는 보존하고 같은 attempt를 자동 재실행하지 않는다. 독립적인 나머지 case는 남은 budget 안에서 계속할 수 있다.

`campaign.py`는 frozen native153 복원, 생성 source 확인, 컴파일, 작은 preflight, 세 case 실행, 저장 age32 자동 복원, time8↔16·16↔32 및 age32 진단 비교를 연결한다. B1과 computational base는 원래 기준해의 immutable identity로 유지한다. 새 BE binary의 SHA는 새 source/prepared/runtime과 별도로 기록하며 B1 binary와 같다고 쓰지 않는다.

이번 대화의 실제 device listing은 성공했고 장치는 online이었다. 이어진 config 조회가 **현재 Desktop Commander 월 사용량 한도**로 중단되면서 “do not retry or reconnect”를 반환했다. 재접속·재시도를 하지 않았다. NCP64코어/128GB와 현재 작업 상태는 관측되지 않았고 새 NCP 제출은0이다. 이는 이전 대화 blocker를 상속한 결과가 아니다. [복사 가능한 Codex 인계](HANDOFF_CODEX_CURRENT_KO.md)에 필요한 모든 실행을 남겼다.

## 배송과 다음 연구

Publication·C8/C10·confirmation은 [CURRENT delivery receipt](DELIVERY_RECEIPT_CURRENT.json), 실행/연구 상태는 [CURRENT DAG](contracts/NEXT_DAG_CURRENT.json)가 권위다. C8/C10은 science source snapshot이며 별도 confirmation의 exact UTF-8 delta가 최종 배송 tree를 복원한다. 사용자가 ZIP을 옮기거나 풀 필요가 없도록 다음 assistant가 자동 처리한다.

새 native 반환을 확보하면 먼저 원 게이트·실제 repair mass/count·accepted-prefix/완료 구분·원0.005 finite differences를 분석한다. Age/time 수렴 HOLD를 성공 exit0만으로 해제하지 않는다. Root native cargo fmt와 workspace CI는 scoped 연구 검증과 분리한다. PR199 draft 유지, no merge/no force-push, 실제 부모를 잇는 expected-head fast-forward만 허용한다.
