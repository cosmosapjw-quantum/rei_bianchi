너는 NCP local Codex의 `NCP_LOCAL_CODEX_BASS_HE_BOUNDED_HEAVY_EXECUTOR`다.

GitHub 저장소 `cosmosapjw-quantum/BASS_HE`의 브랜치 `research/shared-c64-crossrepo-20260928`를 현재 HEAD로 fetch하고, 다음 경로를 반드시 읽은 뒤 지시대로 H0부터 진행하라.

`docs/atomic_reionization_handoff_20261004_v1/NCP_LOCAL_CODEX_HEAVY_20261008_v1/START_HERE_KO.md`

같은 폴더의 `BUNDLE_DELIVERY.json`에 실제 게시된 NCP 통합 실행 패키지의 Drive/Dropbox ID, SHA256, 정확한 크기가 있다. 기존 NCP의 rclone/CLI/mount/캐시를 활용하여 스스로 회수하라. 내가 파일을 수동으로 첨부하거나 업로드할 필요가 없도록 하라. 표준 Python `ncp_intake.py`에서 바깥 ZIP, 내부 E6/E7/E8 원본 ZIP의 SHA/CRC/매니페스트를 검증한 뒤 새 빈 작업공간에 안전하게 복원하라. 한 provider에서 받은 bytes가 검증되면 다른 provider의 같은 bytes를 다시 다운로드하지 마라.

`NCP_LOCAL_CODEX_BASS_HE_HEAVY_HANDOFF_20261008_KO.md` 및 `NCP_LOCAL_CODEX_BASS_HE_HEAVY_DAG_20261008.json`에 정의된 H0→H6를 source/authorization/gates에 맞게 수행하라. E7/E8/E6 완료 검증과 다른 owner 연구를 재실행하지 말고 E9 실제 owner 1~2 step 동등성에서 시작하라. 통과 뒤 명시된 최대 3×384 step만 조건부 진행하라. 초기 25행을 385행에 패딩·보간하지 마라. 모든 physical/default/source/owner reservation gate를 보존하라. 마지막에 실제 명령·종료코드·원시 로그·Gate·Git non-force push·Drive/Dropbox 백업 영수증 및 한국어 RETURN handoff를 제공하라.

호스트 인증 수단이 없어 cloud 접근에 실패하면 임의의 파일을 대체하지 말고 접근 방식·명령·오류·최소 추가 인증 조치를 명시해 `INPUT_RETRIEVAL_BLOCKED`를 반환하라. 비밀 값을 출력하지 마라.
