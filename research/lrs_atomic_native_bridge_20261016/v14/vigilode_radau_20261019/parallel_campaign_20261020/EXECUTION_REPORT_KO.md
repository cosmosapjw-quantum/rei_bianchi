# 독립 이력 병렬 실행 — 구현과 실제 bounded 검증

## 구현 결과

기존 source를 복원하고 variant별로 한 번 빌드한 뒤, 서로 독립인 이력을 자원 제한 queue로 배정하는 실행 경로를 완성했다. V12/V13은 원본 example의 정확한 SHA에 묶인 selector-only 사본을 사용한다. SSPRK2는 원래 세 native 명령과 기존 audit를 재사용한다. 현재 Radau의19설정·borrowed N2·원래 V14 84는 기본 backlog에서 제외한다.

NCP 한 명령 경로는 `README_KO.md`에 있다. 전체 계획은 V12 144이력, V13 84이력, SSPRK2 transport52행/coupled16이력을 처리하는246 jobs다. 현재 sandbox에서 전체 backlog를 실행했다고 주장하지 않는다. 실제 NCP 연결의 quota/key 제한은 그대로이며, 실행 가능한 NCP의 후속 유한 작업이다.

기존 파일 변경은 `prepare_and_run.py`의 양수 `--build-jobs`(default1), `--build-only`, 선택적 `--run-focused-tests`, 외부 CARGO_TARGET_DIR 제거뿐이다. 원래 --all/--case/--prepare-only, default legacy, native evaluation/profile 전달은 유지했다. 추가 실행 코드는 `parallel_campaign_20261020/`에만 있다. native 원본, 기존 append hook, VigilODE source/pin/lock, provider/EoS/FD/GL2 birth/허용오차/기본 수치 동작을 수정하지 않았다.

## 실제 compile과 대표 shard

복구된 Rust/cargo1.94.1, offline/locked/release, CPU0와 build jobs1을 사용했다. 첫 V12 derived example은 exit0,11.700944882초였다. 공유 target에서 시도한 V13은 exit101,0.114367888초로 SourceClockConfig/PhotonAttenuation 등의 unresolved-import 오류를 반환했다. 정상 복원 source에 그 정의와 정확한 output SHA가 있음을 확인하고 source를 바꾸지 않은 채 V13 전용 target으로 한 번 재시도했다. **exit0,12.105879507초**였다. 세 compile 시도의 process wall 합은 **23.921192277초**이며 원래240초/시도·480초 전체 cap 안이다. 최초 실패와 수정 후 원문을 모두 보존했다. 최종 실행 recipe는 variant별 private target을 강제한다.

V12 대표는 D1_X1E5/owner_like_be/N8/cells8, V13 대표는 X1e-4/be_control/N8/cells32/tol1e-15다. 각각 실제 native shard를 한 번 실행해 exit0과8행 완료를 확인했다. 기존 saved CSV의 같은 설정을 필터링해 비교한 결과는 다음과 같다.

| 대표 shard | 유한 수치 비교 | 기타 비교 | 차이 |
|---|---:|---:|---:|
| V12 | 344 | 16 | 0 |
| V13 | 232 | 8 | 0 |

제외한 것은 V12 elapsed_wall_s / V13 wall_s뿐이다. dt_s와 나머지 물리·진단 열은 포함했다. 새 tolerance를 만들지 않았다. V13 과거 cells8의 X1e-5 CSV를 cells32의 동일 설정이라고 비교하지 않았다. 원본 example의 SHA와 derived source/selector diff, 실제 argv·binary hash·stdout/stderr·exit·CSV가 `native_validation/`에 있다.

## Scheduler의 실제 native 경로

검증된 NCP binary SHA256 `c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992`를 그대로 사용했다. 기존 fixed/birth/disabled RadauN16을 profile-off, cell-cache, 동일 thread 환경에서 serial/parallel로3쌍 실행했다. 순서는 AB/BA/AB다. serial은 CPU0, parallel은 서로 겹치지 않는 CPU0/1/2이며 현재 sandbox의 affinity9/cgroup CPU quota8 안이다.

**실제 native18회 모두 exit0**,9개 case-pair의 모든 non-timing JSON 내용이 같았다. 각 case의 cap10초, 전체 charged native process wall cap60초를 적용했다. 실제 charged process wall 합은 **9.626661057초**다. 마지막 완료 phase를 실제 resume하여3개를 REUSED_COMPLETED로 재사용했고 추가 native 실행은0이었다.

| Pair | Serial 전체 phase s | Parallel 전체 phase s | Serial/parallel |
|---|---:|---:|---:|
| 0 | 1.656947672 | 0.753377051 | 2.199360426 |
| 1 | 1.618014477 | 0.702647920 | 2.302738585 |
| 2 | 1.666196855 | 0.775281123 | 2.149151844 |

paired ratio 중앙값은 **2.199360426**이다. 이 시간 경계는 input hash와 receipt를 포함한 동일한 전체 scheduler phase다. 이 관측은 이 local host에서 기존 세 이력을 병렬로 처리한 결과이며, NCP64 scaling·일반 가속·개별 RHS나 물리 kernel의 가속을 입증하지 않는다. 기존 borrowed 실험의 속도/메모리 입증 상태를 바꾸지 않는다.

## 자원 관측과 과거 비용 입력

초기 raw cgroup remaining만으로는 nominal512MiB admission이0이었다. 실제 memory.stat에서 file cache 약7.44GB와 inactive_file 약2.02GB를 관측했고, raw remaining 약0.60GB와 구분해 저장했다. 최종 planner는 host MemAvailable와 raw remaining+관측 inactive_file의 보수적 estimate, 사용자 cap 중 작은 값에서20%를 예약한다. active_file/kernel/slab를 추가하지 않는다. 초기 build의 nominal256MiB는 actual peak RSS가 아니며, private-target repair는 root가 확인한 cache 회수 estimate 하에서 nominal1GiB로 실행했다. 어떤 예약값도 측정 RSS로 보고하지 않는다. `/usr/bin/time`이 없어 per-case peak RSS는 미기록이며 이를 위해 native를 재실행하지 않았다.

저장된 CSV 마지막 행의 시간만 읽은 입력은 V12의144이력 W=5.906294903초/L=0.131985188초, V13 X1e-4/cells32의42이력 W=3.071033693초/L=0.297773501초다. V13 X1e-5/cells8/tol1e-15의42이력은 W=1.508194652초/L=0.148447870초지만 cells32 backlog의 같은 설정이 아니므로 그 예측 입력으로 사용하지 않는다. 해당 X의 같은 설정 자료가 없으면 N 큰 순서 heuristic으로 표시한다. 이 값은 NCP wall 예측이나 실제 병렬 speedup이 아니다. 이상적인 동일 processor·고정 job 시간의 W/L 경계와 실제 host 관측을 구분한다.

## 표적 process 검증과 한 번의 독립 검토

새17개 tests와 원래 runner의4개 process tests, **총21개가 실제 PASS**했다. 서로 겹치지 않는 affinity, child 실패의 dependent blocking, timeout/process-group 정리, 완료 reuse, source/input/output mismatch, active+완료 aggregate charging, 정확한 CSV merge coverage와 원래 key 순서, nominal/inactive-cache 구분, 전체 backlog/private targets, 최소 prepare flag 호환성을 검사했다. 가짜 child는 process plumbing 전용이며 과학 검증으로 세지 않았다.

독립 reviewer가 발견한 실제 복원 입력 closure 누락을 수정했다. V13 restore script/spec/patch, V14 restore/spec/payload, SSPRK restore/spec/native payload를 바인딩하고, 그 입력이 바뀌면 과거 completed dependent도 현재 DAG에서 reuse하지 않도록 했다. 해당 회귀는 native 재실행 없이 통과했다. V12 기존 analysis의 실제 하위 디렉터리도 탐색해 reference가 있는데 absent라고 잘못 표시하지 않도록 했다. 최종 독립 C9와 root 판정은 이 구현자가 발행하지 않는다.

## 수행 scope와 남은 유한 작업

이번 실제 native 호출은 profile3 + 대표 shard2 + scheduler검증18 = **23회**, 새 unique 과학 모델0이다. 전체144/84/SSPRK backlog나 과거19/원래84를 재실행하지 않았다. V12의 SciPy/numpy reference3 IVP는 재적분하지 않고 saved reference/분석과 새 stdlib summary를 분리했다. V13 stdlib analyzer와 SSPRK Decimal audit의 새 full-backlog 실행은 NCP 명령에 포함되며 여기서 수행한 것으로 세지 않는다. exit0과 과학적 PASS를 구분한다.

이 작업은 PhysMath Research Loop1.3.0의 C5–C8로 root가 지정했다. SKILL, POLICY_INTEGRATION, CODING_LOOP, SUBAGENT_MODE와 code-work 지침을 실제 읽었고, ROOT_CONTRACT의 source-bound 구현·bounded actual validation·typed identity·과거 전체 재시험 금지·한 독립 검토 경계를 적용했다. 새 child를 재귀 생성하지 않았다. 원본 수치 source와 과학 승인 범위는 root Astra의 고정 계약에 남아 있다.

원시 결과 위치·고정 identity·실행 수와 상한은 `EXECUTION_SUMMARY.json`을 참조한다. source-on 일반2차, uniform stiff, 일반 양수성, Case B/full EoR/signed Bianchi, 넓은 positive-CMB/비영 boundary, global certificate 및 CSV에 없는 완전 photon ledger는 HOLD다. production은 NOT_ISSUED다.
