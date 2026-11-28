# NCP local Codex handoff — 2026-10-12 개발계획 개정

## 지금 적용할 상태

결정은 **SCIENTIFIC_FAST_TRACK_RESET**이다. 현재 NCP에 넘기는 새 과학 work unit은 **0개**다. 이 문서는 실행 대기 상태와 다음 이관 조건을 전달한다. 이미 완료된 E13C8 합산, E13C9/C10 국소 계산, 복구 helper, 성능 benchmark 또는 full native continuation을 새 이름으로 다시 실행하는 명령이 아니다.

현재 로컬에 저장소가 있으면 새로운 계획 revision의 `DEVELOPMENT_PLAN_KO.md`와 `research/scientific_priority_reset_20261012/ACTIVE_DAG.json`을 읽는다. 정확한 게시 commit은 이 작은 계획 packet의 `PUBLICATION.json` 또는 전달 영수증을 따른다. 파일이 없어도 아래 결정만으로 **현재 실행할 NCP 명령이 없다는 판단**은 가능하다. 이 결정을 위해 E13C10의 206 MB 전체 과학 archive를 내려받거나 복구할 필요는 없다.

```text
project: cosmosapjw-quantum/BASS_HE
plan: SCIENTIFIC_FAST_TRACK_RESET
NCP_action: NO_CURRENT_HEAVY_WORK
new_work_units: []
physics_invocations_to_run: 0
E13C11: PARKED_PENDING_OBSERVABLE_NEED
next_scientific_milestone: prescribed-history directional Liouville + polarized Thomson response
execution_location_for_design_code_and_short_pilots: HERE_CHATGPT
```

## 보존할 과학 상태

- BASS_HE 기준 PR26: `3c20b6e9dcd099a4f5ac23208445225f959fd1e5`.
- E13C8 전체 finite OFF: `PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF`. 2,440개 경로 전체 결과와 이미 완료된 2,331개 NCP 작업을 보존한다.
- E13C9 선택 경로의 signed Volterra 및 E13C10의 `PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST`를 보존한다.
- E13C10 새 full population은 `NOT_RUN`; 해당 E13 계보의 physical/continuum/production/receiver는 `HOLD`다.
- 기존 E13C10 `NEXT_DAG.json`의 E13C11 자동 후속 제안은 이번 계획이 대체한다. 과거 package 파일을 고치지 않는다.
- 현재 user는 짧은 실행을 ChatGPT에서 끝내고 길고 무거운 병렬 부분만 NCP로 넘기길 원한다. NCP에서 별도 재설계·전체 감사·문헌조사·원자 provider 재구현을 시작하지 않는다.

## 다음에 실제로 진행할 공동 과학 작업

REI PR104의 reduced history, BASS N4의 이미 완료된 proper-time 전자 이력 수신과 기존 native 편광 Thomson 코드를 재사용한다. 새 연결은 전자 이력의 `c*sigma_T*ne_eff*dt`를 실제 충돌 호출에 전달하고, 동일 mean-H 대조군을 포함한 방향 스펙트럼·편광 반응을 비교하는 것이다. Collisionless Liouville에 xe를 읽히는 것만으로 산란 반응이 계산되지는 않는다. F/M/B/B0 대조에 같은 geometry의 B_F/M_F를 더해 `[B−M](ne_B)−[B_F−M_F](ne_F)`로 전자 이력 민감도를 분리한다. 서로 다른 proper-time 셀 평균을 점밀도로 복사하지 않고 원 producer history와 같은 cell-integral 정의로 공통 a/B-clock에 재투영한다. 새 보간·재투영 오차도 paired 수치오차에 포함한다.

관련 source 기준:

- REI reduced: `f66929c23ea3fa6e39dd4808e5b27d136c568a03`, `research/broad_history_20261010/REPORT_KO.md`.
- REI characteristic: `17f8d0daa72e0f76a49cde01b110f650a6688c42`, `rust/rei_microphysics/src/bianchi_i.rs`.
- BASS receiver와 편광 Thomson: `2325a42c0954e949bb57f53976d0c9a9d9a9a362`, `research/accel02_n4_20261011/REPORT_KO.md`, `_rustcore/src/kinetic/pol_collide.rs`.

이 source 존재와 과거 scoped 수신은 새로운 연결의 실행 완료가 아니다. B1은 현재 `PLANNED_NOT_RUN`이다. BASS_HE의 고정 첫 두 step P/H는 누적 photon stock·heat/H이며 Γ 또는 실제 RCT photon spectrum으로 바꿔 쓰지 않는다. 기존 scalar KF/GM 구현도 새로운 physical/production 채택을 뜻하지 않는다.

## 새 NCP packet을 받았을 때의 실행 경계

새 packet에 목표 observable·accuracy, 고정 source/input, 미실행 독립 work list, HERE pilot wall/CPU/RSS 및 병렬 이득의 근거, 실행 명령과 fresh output/반환 규칙이 함께 있을 때 해당 명령을 실행한다. 그러한 packet이 아직 없으므로 이 문서에는 실행할 MPI 명령을 넣지 않는다.

실제 host의 CPU topology·affinity/quota·NUMA·가용 RAM을 확인한다. 64 ranks 또는 임의 hybrid 배치를 추측으로 선택하지 않는다. MPI×OpenMP×BLAS 중첩을 막고 실가용 RAM의 최소20%를 남긴다. 시간 순서가 있는 trajectory step과 Thomson으로 결합된 각도를 독립 작업처럼 쪼개지 않는다. 독립 scenario/조건 집합이 우선 병렬 단위다. 기존 E13 P60과 다른 consumer의 binary64 근사를 구별한다.

완료 cache와 실패 증거를 보존하며 output을 덮어쓰거나 source/precision/physics/tolerance를 조용히 바꾸지 않는다. 첫 실패는 정확한 상태·카운터·stderr와 함께 반환한다. 현재 REI C12의 `NO_CURRENT_BUDGET`을 임의 초기화하거나 새 allocation으로 해석하지 않는다.

## 기존 과학 자료가 나중에 필요한 경우

현재 계획의 이해·대기 판정에는 추가 전달 파일이 필요 없다. 특정 후속 과학 작업이 원본 E13 bytes를 실제로 요구할 때만 다음 기존 백업을 이용한다.

- 기존 complete: `BASS_HE_E13C10_COMPLETE_20261012T005719Z_sha_70fe29c9556d.zip`, 206,346,675 bytes, SHA-256 `70fe29c9556d83e22c7e05fe281ccf243a9bed5cc032a3df695f7157e5f65ae1`.
- 기존 recovery kit: `BASS_HE_E13C10_RECOVERY_KIT_20261012T010300Z_sha_0893f7d0552d.zip`, 38,891 bytes, SHA-256 `0893f7d0552d786b27ebf1dacaad795d213abb025891f7ea7d34aca01b28032d`.
- [Recovery kit](https://drive.google.com/file/d/16YlWU-tsjJYowo3-bNYefbYVAfo-sbC6/view?usp=drivesdk), [승인된 백업 폴더](https://drive.google.com/drive/folders/1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI).
- 기존 Git [backup locations](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3c20b6e9dcd099a4f5ac23208445225f959fd1e5/research/e13c10_first_midpoint_bound_local_20261012/DELIVERY/BACKUP_LOCATIONS.json)에 실제 part/Dropbox 위치가 있다.

과거 part002의 `.bin` 접미사 복구 실패와 수정된 helper의 이후 복구 성공은 기존 영수증의 역사다. 이번 계획 변경에서 복구·재현을 다시 호출하지 않는다.

## 이번 handoff의 반환 기대

현재 추가 host 실행이나 upload receipt를 만들 필요가 없다. 상태를 보고해야 한다면 **“계획 반영: E13C11 대기, 새 NCP work 0, 다음 짧은 과학 작업은 HERE의 prescribed-history 수송 연결”**로 답한다. 새로운 수치 결과, host attestation 또는 NCP 실행 성공을 선언하지 않는다.
