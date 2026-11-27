# NAVER c64-g3 검증 증거 — BLOCKED_DATA_MOUNT

정확한 PR #13 repair head `ad12eec6023c41b7791eb3958fc00b0adcd5bc14`에서 검증했다. 현재 VM은 NAVERCloud c64-g3_HIGH_CPU, 사용 가능 CPU 64개, OpenBLAS 1 thread로 확인됐다. 전체 pytest는 193/193 PASS다.

`findmnt /srv/bass-he`는 exit 1이고 해당 경로가 존재하지 않는다. `lsblk -f`에는 `/`에 마운트된 루트 ext4 디스크만 보인다. 승인된 별도 데이터 mount가 없으므로 mounted-host 메모리 측정, fresh science tracer, worker sweep, 56-action replay, host scratch 장애 주입, checkpoint restore, provider backup은 실행하지 않았다. 로컬 RSS나 과거 결과를 cloud 측정값으로 대체하지 않았다.

첫 미완료 기준은 H2 HOST_PREFLIGHT다. 승인된 ext4 volume이 외부 운영자에 의해 `/srv/bass-he`에 마운트되면 H2를 다시 확인한 뒤 H3부터 진행한다. 이 작업은 disk/VM/service/firewall/credential을 변경하지 않았다. 과학 PROMOTE는 HOLD다.

`COMMAND_LOG.txt`는 실제 명령, UTC, exit code, 민감 host 필드를 제거한 결정적 출력, 원본 stdout SHA256을 포함한다. `FULL_TESTS.xml`은 새 전체 실행의 JUnit이며 hostname 필드만 hash로 바꿨다. `CLOUD_TESTS.xml`은 그 실행에서 추출한 61개 cloud testcase이며 별도 재실행이 아니다. 최종 evidence commit/tree는 Git commit이 자기 hash를 파일에 포함할 수 없으므로 draft PR 본문에 기록한다.

검증 draft PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/14
첫 evidence snapshot commit/tree: 486cbdaebbadd47876f4ae7504c97c8a56b52924 / 0d84722381e4b659528f586e6143e7a81317fc3c
