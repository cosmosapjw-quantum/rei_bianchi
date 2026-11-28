# BASS_HE E13C5 — 전송 파일명 복구 후 재개

`NCP_RESUME_HANDOFF_KO.md`를 local Codex에 전달한다. 보존된 `.part002.bin`의 실제 SHA를 확인한 뒤 원 manifest basename으로 배치하고, 새 출력·receipt로 원 ZIP restorer를 한 번 호출한다. 그 뒤 기존 고정 source/lock의 saved-budget 작업을 이어간다.

이 패키지는 작은 복구 보완본이다. 대형 조각은 이미 NCP의 원 intake/parts에 보존되어 있고, 원 백업 위치는 `original_kit/`에 들어 있다. 추가 사용자 첨부는 필요하지 않다. 최초 실패 archive와 영수증을 그대로 포함했고 scientific core와 원 restorer는 바꾸지 않았다.

실제 NCP 파일명 배치, ZIP 복구, 합산은 아직 NOT_RUN이다. 코드의 작은 파일 대조 6개와 범위를 한정한 독립 코드 검토를 완료했다. 이 상태를 실제 호스트 재현 완료로 해석하지 않는다.
