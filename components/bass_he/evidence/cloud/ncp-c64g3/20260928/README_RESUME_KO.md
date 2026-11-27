# c64-g3 root-backed storage 검증 재개

이 디렉터리의 기존 `RUN_RETURN.json` 및 blocker 파일은 최초 `BLOCKED_DATA_MOUNT` 기록이다. 삭제하거나 덮어쓰지 않았다. 새 최종 색인은 [resume-002/RUN_RETURN.json](resume-002/RUN_RETURN.json)이며, `MOUNT_BLOCKER_RESOLUTION.json`이 H2의 `RESOLVED_AS_ROOT_BACKED_HOST_STORAGE` 전이를 설명한다.

실제 NAVER Cloud c64-g3에서 `/dev/vda2` ext4 root(`/`)의 일반 디렉터리 `/srv/bass-he`를 사용했다. format, partition 변경, mount/unmount, 새 volume 생성은 하지 않았다. 최초 free-space 90,323,353,600 bytes(85.57%)는 20 GiB 및 20% 기준을 넘었다. 실행 중 새 dispatch는 15 GiB 및 15% 미만에서 멈추도록 테스트했다.

검증 계산의 exact source는 `8307e3dc32f7bfb60af04ee7a2375b49f8bf854f` / tree `245e6013cc6476f7c48d2bec414ca599e6bf3ed1`이다. 이 커밋의 실행 binding은 `4930dd9b8c95186450c44b6cae866d2efd4bbedfa01369e52541b0c215322451`, scientific source ID는 `bd1acfb4ba6685ddd2cd1207023d5f7fadf9d37bfd1bee73f9d02a20713c8ae3`이다. 이후 evidence/docs 커밋의 최종 hash는 PR #14 metadata와 최종 응답에 있다. 커밋이 자기 hash를 내포할 수 없기 때문이다.

`MEMORY_CALIBRATION_RESUME_002.json`은 112개 실제 표본의 worker RSS p95 83,689,472 bytes를 기록한다. `WORKER_SWEEP_RESUME_002.json`은 1/8/16/24/32 workers × 3회, 15/15 arm telemetry, 동일 scientific digest와 16-worker 선택 근거를 담는다. `SCIENCE_TRACER_RESUME_002.json`은 fresh wrong-pair/control/endpoint/D0 32·64 경계를 기록한다.

`REPLAY_CLOSEOUT_RESUME_002.json`과 `REPLAY_ACTIONS_RESUME_002.json`은 별도 fresh run의 controls 2, endpoints 7, geometry actions 56, imported evidence 0 및 각 action 수치를 공개한다. `RUN_BINDING_RESUME_002.json`, `RUN_PROFILE_RESUME_002.json`, `EVENTS_RESUME_002.jsonl`로 실행 provenance를 검수할 수 있다. `FAULT_INJECTION_RESUME_002.json`과 `FAULT_TESTS_RESUME_002.xml`은 corrected scratch 52/52 PASS를 기록한다. 첫 scratch 실패 2개는 `/srv` basetemp가 `local_sandbox`의 `/tmp` 계약과 충돌한 `TEST_ENVIRONMENT` 결과로 보존했다. production 결과 65개 SHA256는 fault run 후에도 불변이었다.

`CHECKPOINT_RESTORE_RESUME_002.json`과 `CHECKPOINT_MANIFEST_RESUME_002.json`은 실제 새 디렉터리 추출, MANIFEST 69개 hash, SQLite/결과 65개, restored `status` readback을 기록한다. `BACKUP_RECEIPTS_RESUME_002.json`은 Google Drive와 Dropbox의 create-only upload ACK 및 metadata readback을 기록한다. 원격 바이트 재다운로드/restore는 `NOT_RUN`이다.

호스트 계산은 비루트 `bass-he` 계정의 현재 user-session cgroup에서 실행했다. 전용 systemd service 설치·시작이나 reboot 검증은 수행하지 않았다. 과학 solver와 tolerance는 변경하지 않았으며 `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`이다. 이 PASS는 runner/environment migration 검증이며 과학적 독립 승격이 아니다.
