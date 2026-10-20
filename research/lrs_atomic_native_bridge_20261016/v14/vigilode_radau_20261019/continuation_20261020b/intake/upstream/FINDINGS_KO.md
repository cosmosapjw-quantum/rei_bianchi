# 새 실행 intake와 다음 최적화 후보

작성: 2026-10-20 06:52 UTC. 실제 child `/root/opt20_upstream`의 read-only R1/C2·보조 R2 결과다. 이 child는 코드 구현, 빌드, 수치 실행, Git 변경, 원격 업로드를 하지 않았다. 외부 작업은 이번 LRS 실행 수에 더하지 않는다. 이 child는 과거 physmath-research-loop v1.3.0의 C2/C3 자료를 보조 자료로 재사용했으며, 이번 실행 계약과 판정은 root가 읽은 사용자 제공 executor skill internal 1.0.0과 현재 프로젝트 AGENTS를 따른다.

## 1. 결론

다음 한정된 구현 후보는 **cached cell의 node와 PhotonState를 매 RHS마다 다시 복사하지 않고, 기존 native rate fold에 빌린 node 참조를 원래 순서로 전달하는 것**이다. 현재 과학 source는 `33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1`이고 VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다. 원격 source 원문을 다시 읽었다.

- [addon 원문](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/native_additions/axbi_native_rhs.rs), Git blob `42ce6a1aee49bf760bf7b627fe749490068a6d64`.
- [adapter 원문](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/src/lib.rs), Git blob `16be47fe18922210202b2d7101cea189c34b0896`.

`PreparedAbsorption::native_rates` 자체가 addon에 있다. 따라서 generic node fold를 같은 addon 안에 추출하면 원본 native 152개 파일을 바꿀 필요가 없다. 별도 opt-in `cell-borrowed` 경로를 기존 `cell-cache`와 같은 binary에서 비교하는 root의 선택에 맞는다. 아직 이 후보의 실제 속도 개선은 측정되지 않았다.

## 2. 새 외부 증거의 실제 확인 범위

이전 전달 HEAD `70a9ff3f…` 이후의 새 변경과, 이전에 존재했지만 이번에 처음 읽은 증거를 구분했다. PR 목록만으로 완료를 인정하지 않았다.

| 대상 | 읽은 source·receipt·실제 결과 | 이번 판단 |
|---|---|---|
| [VigilODE PR77](https://github.com/cosmosapjw-quantum/vigilode/pull/77), 전달 HEAD `f738fb481bad3f086b568c8493105576851093f2` | run 39378576576의 dispatch `c453e2e558ed6237472719c1b885c6af120bb51c`와 실제 실행 source `49ca3150c68d527a275c855ecf814122ff9c533a`를 구분. EXEC_SOURCE_COMMIT, EXIT_STATUS exit 0, execution.log, 실제 workflow stdout, AUDIT, RESULTS.csv, structured PREFLIGHT 원문을 읽음. stdout에는 12/4/3 tests PASS가 있고 PREFLIGHT는 final_t 0.2, accepted 4, rejected 0, failure null, 실제 16성분 final state와 curve 자료를 포함. | 06:18 게시로 이전 종료보다 오래된 새 인지 증거. 별도 reaction–diffusion 모델이며 LRS 실행이 아님. 이번 child가 재실행하거나 전체 certificate를 독립 재검산한 것은 아님. |
| 같은 PR77의 실패 run 39377432935 | 실행 source `ca3be3535b4eb40ecfc237f8ff80255d367ffcf5`, native_tests exit 101, 실패 workflow log를 읽음. | 실패 증거도 유지. 후속 source 수정 후의 성공과 혼합하지 않음. |
| rei RUN19, source `f2996d02908e5a2e678fab0dc0efb3424fa86a99` | run 39374365605는 verify_repo job의 success임을 stdout에서 확인. 별도 RUN19 COMMAND.json exit 0, stdout 47,630 bytes, 실제 JSON 72조건×5반복, target_evaluations 8192, ivps 0을 읽음. | 유효한 instantaneous gas RHS benchmark이며 native LRS 시간 이력이 아님. 05:20 CI 성공 자체는 benchmark 실행 증거가 아님. |
| [rei PR199](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199), `02767dc5e6c4b47883f590834aee38530852568d` | 현재 DELIVERY_RECEIPT_CURRENT.json v8와 optimization 문서를 읽음. receipt는 source_parent `cf00684741eb612e35f987713c28937513d44d57`, source_commit null, publication/backups PENDING, NCP scientific EXECUTION_NOT_RUN. | 새 observable-certificate 작업의 부분 전달 상태. native age/time HOLD를 유지. 진행 중 workflow를 완료 실행으로 읽지 않음. |
| [rec_bianchi PR110](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/110), `888d56d72579d1e1fd30f66abe02d9f91809a767` | 실제 source `e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d`. supervision exit_code 0, worker stdout 14,667 bytes, native_run returncode 0, verification, 원시 final state를 읽음. 요청·반환 16 steps, checked causal links 5,008. stdout SHA256 `5e576ae56a9be2a1ab7a9075b02b27e40524e66d4339c41e9664b8b0b0ef630b`. | 06:27 최신 게시를 확인한 별도 native smoke 증거. SMOKE_ONLY / HOLD_CAP_BEFORE_RT_BOUNDARY / PASS_PENDING_REVIEW를 그대로 유지. REI_activation false이며 LRS 결과로 이전하지 않음. |
| [BASS_HE PR78](https://github.com/cosmosapjw-quantum/BASS_HE/pull/78), `3b125fc3cf80ce715353be17f640f2d9a5fb9f4a` | 새 continuation README와 기존 optimization DELIVERY를 읽음. new native owner 0, reference pairs 0/4, native NCP process unobserved. | 06:33 게시된 intake/설계 갱신. 새 HE29 native 반환 증거 없음. 기존 workers 2/4의 불리한 측정은 그 실험 범위에만 적용. |
| [WU088_HH PR120](https://github.com/cosmosapjw-quantum/WU088_HH/pull/120), `31745376ca751e7c925b3b1453ef292436cd30e8` | source `e73048e1399263eac3d40ffd3e700807bbc7c72e`를 밝힌 PR와 실제 sample EXECUTION/RESULT/빈 STDERR를 읽음. sample 03:02:31 시작, returncode 0, binary SHA256 `303efb12fb6c6169b97440a1224d30730e5194a6230c02d469a13a25b9270c13`, accepted 703, structured shifted solves 5,624, dense factorizations 0. | 이전 종료보다 오래된 별도 HH SIMD/구조 solve 증거. 해당 HH denominator 조건이나 성능을 LRS에 그대로 적용할 수 없음. |

VigilODE main은 조회 시 `8d0c79184e09efb5bdadc24a6315c60a71a44264`였고 PR73–76 HEAD는 이전 intake와 같았다. 읽은 최근 30개 Actions 목록에는 06:20 이후 새 run이 없었다. 이 문장은 조회 범위의 delta이며 모든 branch·비공개 실행의 부재를 뜻하지 않는다. bass_cr 최신 PR84는 이전 날짜였다. rei_flrw·rei_r9 endpoint는 404였고 owner repository search도 빈 결과였으므로 “모든 관련 저장소 접근 완료”라고 주장하지 않는다. root가 PR198, 다른 child가 Drive/Dropbox를 담당한다.

## 3. VigilODE와 RUN19의 구체적 재사용 범위

### VigilODE PR77

읽은 [model.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/f738fb481bad3f086b568c8493105576851093f2/crates/vigilode-hybrid/src/model.rs)의 `Model::shift_factor`는 reflecting path diffusion, mean coupling, local quadratic reaction의 tridiagonal-plus-rank-one 행렬을 푼다. local directional dual로 계수를 얻고, 양의 pivot을 요구하는 tridiagonal factorization 뒤 rank-one correction을 수행한다. correction denominator는 finite이며 `64*f64::EPSILON`보다 커야 한다.

이것은 현재 LRS의 임의의 6×6 cell block에 사용할 일반 Schur API가 아니다. 해당 모델의 positivity 조건을 LRS block에 이전할 수 없다. LRS에서는 전체 stage matrix가 가역이어도 특정 cell block이 singular일 수 있으므로 dense fallback과 기존 residual 계약이 필요하다. 현 프로파일에서 LU 비용을 독립적으로 분리하지 못했으므로 다음 1개 변경으로 solver 교체를 택할 근거가 부족하다.

새 `vigilode-hybrid` manifest는 MIT, edition 2024, MSRV 1.94.1, 별도 workspace다. 기본 native feature와 optional external `diffsol=0.16.1`을 갖는다. 현재 LRS의 고정 VigilODE pin을 자동 갱신할 이유는 없다. 기존 pin의 `ParallelExecution::rayon`/`map_ordered`와 faer 0.24.4는 이전 회차에서 이미 재사용·검토한 것이며 새 도입으로 다시 세지 않는다.

### RUN19

[RUN19 native 보고서](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f2996d02908e5a2e678fab0dc0efb3424fa86a99/research/atomic_nuclear_ssot_20261017/run19/execution/unit_a/UNIT_A_REPORT_KO.md)는 T-only direct coefficient 공유와 worker-local `GasRateWorkspace`를 구체화했다. 실제 stdout과 COMMAND도 함께 읽었다. immutable backend 및 정확히 같은 EOS temperature bits에서만 재사용하며 density, electron, opacity를 캐시하지 않고 온도를 양자화하지 않는다. 해당 source의 gas STEP 경로는 원래 direct owner를 유지한다.

이는 현재 LRS에 유용한 2순위 후보이나, 현재 N16 cache 프로파일은 preparation 0.078447 s, rate fold 0.016176 s, provider 0.007128 s였다. 이 수치는 기존 실행 증거 재사용이며 새 측정이 아니다. inclusive Jacobian 시간과 합산해 새로운 총시간이나 speedup을 만들지 않는다. 먼저 node 복사 경로의 비용을 줄이고 남은 provider 비용을 다시 보아야 한다. RUN19의 ivps=0 또는 작은 net-rate cancellation 조건의 table 정확도를 실제 LRS 시간 정확도로 승격하지 않는다.

## 4. borrowed cell iteration의 식–코드 계약

현재 `NativeCellCache::prepare`는 cache 유효성 검사 후 선택된 한 cell만 원본 `prepare_cell`로 다시 만들지만, 매번 `template: state.clone()`와 `prepared.nodes.extend(cell.nodes.iter().cloned())`를 수행한다. 그 뒤 `native_rates`가 모든 node를 원래 순서로 방문한다.

새 seam은 다음으로 충분하다.

1. addon의 기존 rate arithmetic을 private generic helper로 추출한다. 입력은 cell 수, `support_lo`의 slice, `IntoIterator<Item=&AbsorptionNode>`, absorber와 nH다.
2. legacy `PreparedAbsorption::native_rates`는 `self.nodes.iter()`를 전달한다. borrowed cache 경로는 원래 cell index 순서로 각 cell의 원래 node slice를 이어 전달한다. 변경 cell의 임시 `PreparedCell`은 helper가 끝날 때까지 같은 호출 안에서 소유한다.
3. state shape/domain, changed-cell 범위, unchanged cell N/U/support 검사와 원래 prepare_cell 오류 전파를 유지한다. diagnostic fold 순서와 node count도 유지한다.
4. species 0..3, global photo/binding/heat sums, cell compensated_add의 산술 순서를 유지한다. 각 cell의 global 기여를 빼고 다시 더하는 방식으로 바꾸지 않는다.
5. base cache 생성 자체의 복사, coordinate decode의 복사, 최종 owned rate 출력은 이 한정된 변경만으로 모두 제거되지 않는다. 이번 비용 측정은 이를 구분해야 한다.

같은 순서의 같은 node 값으로 동일 arithmetic loop를 실행한다는 것이 동일 RHS의 근거다. 새 적분법·FD 간격·허용오차·물리 source 변경은 없다. Borrowed slice의 비연속 cell 배치가 cache locality에 영향을 줄 수 있으므로 실제 wall 개선은 측정 대상이다.

최소 검증은 기존 cached/legacy focused native fixture와 실패 계약을 재사용하여 전체 RHS·direct channels·사건 회계·84-column Jacobian을 비교하고, 기존의 대표 이력을 동일 binary/options에서 paired 실행하는 것이다. 새 제조 시간차수 실험은 필요하지 않다. 기존 tests가 새 공통 helper 양쪽만 비교하게 되면 독립 기준이 약해지므로, 이전 동결 결과 또는 현재 변경되지 않은 cell-cache 경로와의 비교를 남기는 것이 좋다.

## 5. workspace와 Schur의 우선순위 비교

| 후보 | 구현면과 필요한 확인 | 우선순위 |
|---|---|---|
| Borrowed node fold | addon helper와 opt-in adapter 분기. 동일 node 순서·오류·진단·counter, 동일 입력 결과 및 paired wall 확인. 새 crate 없음. | 지금 선택 |
| Reusable native rate workspace | 현 rate fold의 output 3 Vec와 compensated scratch 3 Vec를 재사용할 수 있으나 매 호출 전체 reset 필요. Evaluation이 owned direct output을 보관하므로 output borrow/lifetime 또는 FD-only private API를 정해야 함. 실패 후 정상 호출·shape 변경·empty state 확인 필요. 공유 mutable Context에 억지로 넣지 않음. | 후속 profile 기반 |
| RUN19 T-only workspace | 동일 EOS T bits와 immutable backend 조건을 보존한 독립 coefficient cache. current provider 비용이 작은 편이며 adapter/native gas owner 연결 변경이 더 큼. | 후속 profile 기반 |
| Block-Schur Radau | gas 12×12 및 cell 최대 6×6 solve. local invertibility가 추가 조건이며 full dense fallback/residual 계약 필요. nonlinear iteration·FD·solver code surface를 함께 확인해야 함. | LU 비용 분리 후 별도 유한 연구 |

## 6. 외부 문헌·Rust 기본 API

이번 Exa 원문 회수는 [Rust Iterator::flat_map](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flat_map)과 [Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.clear) 공식 문서를 대상으로 했다. flat_map은 IntoIterator를 반환하는 closure를 받아 iterator를 연결하며, 빌린 slice iterator를 입력으로 쓸 수 있다. 기존 node를 clone/collect할 필요가 없다. Vec의 length와 capacity는 다르므로 workspace를 재사용할 때 `clear`만 호출해 indexed fold를 시작할 수는 없다. 길이를 복원하고 모든 누적 상태를 reset해야 한다. 새로운 Rust dependency·MSRV 상승은 이 seam에 필요하지 않다. 이 문서는 runtime speedup을 보증하지 않는다.

SciSpace 결과는 이전 회차의 실제 검색과 그 후 회수한 1차 원문을 재사용했다. 새 SciSpace 호출을 한 것으로 세지 않는다. van der Houwen–Sommeijer의 [CWI 최종 원문](https://ir.cwi.nl/pub/1390/1390D.pdf), ZAMM 76(7), 367–375 (1996)은 block-triangular Jacobian approximation의 convergence 변화와 stage similarity transformation을 구분한다. SciSpace의 1995 표시는 최종 원문 1996으로 교정했다. 이 논문은 exact borrowed iteration의 성립을 위해 필요한 문헌은 아니며, 후속 approximate Schur/Jacobian 방안을 원래 nonlinear 문제와 혼동하지 않게 한다. 기존 LLNL 원문 회수가 실패한 Brown–Woodward 검색 결과는 결론 근거로 쓰지 않았다.

이전 SciSpace 검색·CWI/패키지 원문 retrieval은 `optimization_20261020/upstream/RETRIEVAL.json`에 있고, 이번 Exa 원문은 `PRIMARY_DOCS_RAW.json`에 있다.

## 7. 보존·게시·DAG 상태

| 단계 | 실제 완료 | 백업·게시 |
|---|---|---|
| R1/C2 외부 실행 intake | PR/source/종료코드/stdout/원시 결과의 지정 범위 조회 완료. 원문 API 응답과 source readback을 이 디렉터리에 저장. | Git push 및 양쪽 백업은 parent 담당, 이 child 시점 PENDING_PARENT |
| 보조 R2 구현 후보 유도 | 현재 33ae18 source를 읽고 borrowed fold의 조건·오류·lifetime·후속 후보를 기록. | 본 문서와 원문 retrieval을 parent 전달 |
| C5–C8 구현·실행 | 이 child 수행 없음. | root가 별도 coder와 진행 |
| C9 새 코드 검토 | 이 child 수행 없음. 이 문서는 변경 전 intake이며 독립 새 diff review로 세지 않음. | PENDING_NEW_DIFF |

원문 파일은 `CURRENT_SOURCE_RAW.json`, `SOURCE_RAW.json`, `EXTRA_SOURCE_RAW.json`, `RELATED_SOURCE_RAW.json`, `FINISH_SOURCE_RAW.json`이다. PR/API/workflow 조회 원문은 `UPSTREAM_INDEX_RAW.json`, `RUN19_INDEX_RAW.json`, `RELATED_INDEX_RAW.json`에 보존했다. API의 같은 payload가 tool wrapper 안에서 중복된 부분만 제거했으며 실제 raw content 문자열은 보존했다. 새 native 실행·시간 정확도·uniform stiff·Case B·full EoR·signed Bianchi 승격은 없다.

