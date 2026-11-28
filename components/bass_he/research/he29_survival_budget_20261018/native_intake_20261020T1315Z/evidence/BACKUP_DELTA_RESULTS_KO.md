# HE29 백업 변경분 intake — 2026-10-20

기존 `BACKUP_DELTA_INTAKE.json`과 `FINAL_BACKUP_RECEIPT.json`을 먼저 읽고, 이전 탐색 종료 시각 06:08:55 UTC 이후의 변경분을 조사했다. Dropbox 검색 3회(HE29, canonical dossier의 20261020/native), canonical Drive 직접 목록 1회(100개 상한), 원래 DATA archive의 Drive metadata 1회, 새 Drive parts manifest 읽기 1회를 수행했다.

새 반환 `BASS_HE_HE29_NATIVE_RETURN_20261020_c1c4c061.tar.gz`가 12:42:38 UTC에 Dropbox에 게시되어 있었다. 276206340 bytes를 실제 GET으로 내려받아 SHA256 `c1c4c06149bf9561141bc0f6b6f39c280bd554a5e1252ed0825f0e950f1c10c6` 및 Dropbox content_hash를 검증했다. 293 regular member 중 manifest 제외 292 payload의 크기/SHA가 모두 맞았다. archive source는 실행하지 않았다. `execution/build/he29_owner_server` 실제 4691224 bytes의 SHA256은 `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9`이고 build receipt와 일치한다. rlib SHA도 일치했다.

네 pair의 TABLE.json 파일 bytes와 runtime `source_table_sha256`은 별도 identity다. 후자는 각 RESULT.table_sha256과 4/4 일치했다. archive에 독립적으로 직렬화된 생성 table 배열은 없으며, 본 intake는 table을 재생성하지 않았다. 과학 admission 및 residual 해석은 부모의 Git source 분석에 맡겼다.

Drive에서는 동일 archive의 parts manifest 및 세 part metadata를 읽었다. Dropbox archive bytes를 해당 offset/길이로 나누면 manifest의 3개 part SHA와 모두 일치한다. Drive part raw bytes는 다시 내려받지 않았으므로 독립적인 dual raw verification으로 기록하지 않는다.

기존 통합7a86d5bb와 closeout d0a76860도 원래 크기/SHA에 맞게 복원했다. 과거 Drive upload UNKNOWN은 그대로 보존하며 재업로드하지 않았다. 첫 sandbox GET 세 건은 socket Operation not permitted였고, 승인된 네트워크 escalation 뒤 세 건 모두 HTTP200으로 완료했다. 이 실패는 native 실행 실패가 아니다.

Dropbox date filter는 이번에도 이전 날짜를 반환하여 실제 반환 timestamp로 다시 필터링했다. native 검색은 100개와 has_more=false를 반환했지만 이전 recall 공백에 따라 완전한 변경 피드라고 간주하지 않는다. 정확한 HE29 반환을 발견한 뒤 관련 프로젝트 전체 백업 재귀 조사는 확대하지 않았다. NCP 제출·과학 재실행·Remote Desktop Commander 호출·원격 mutation은 모두 0이다.
