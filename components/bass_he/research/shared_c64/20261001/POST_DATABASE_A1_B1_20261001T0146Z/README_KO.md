# BASS_HE 첫 A1/B1 연구 루프

먼저 `BASS_HE_POST_R10R_THEORY_CLOSURE_REPORT_KO.md`, `GATES.json`, `NEXT_HANDOFF_KO.md`를 읽는다. A1은 범위 내 형식적 유도와 독립 검토를 완료했으나 실제 finite-R ETF/채널 embedding은 열려 있다. B1은 1,131개 원문 값과 13행 메타데이터의 부분 권위 패키지다. 새 단면적 계산은 없다.

`A1`은 derivation·matrix helper·12개 algebra test 기록·CAS를, `B1`은 원문 수치 전사·출처 메타데이터·검증 코드를 담는다. `review`는 저자와 분리된 검토다. 실패 기록은 지우지 않았다. 각 node의 RESULT와 NOT_RUN이 적용 범위를 제한한다.

공개 Git 패키지는 논문 PDF·페이지 이미지·원문 전체·사용자 원문 계약·기존 Git 응답 덤프를 제외한다. `PUBLICATION_MANIFEST.json`이 정확한 공개 payload 목록을 정한다. 이미지 참조 중 공개판에서 빠진 항목은 private archive의 동일 경로에 있다.

전체 private archive에는 변경하지 않은 v3 source ZIP을 `private_sources/BASS_HE_PRIMARY_SOURCE_ARCHIVE_20261001_v3.zip`로 포함한다. B1 verifier는 이를 별도 디렉터리에 풀고 `python B1/code/verify_source_cells.py --source-root <v3_root>`로 실행할 수 있다. 검토된 증거를 재사용하되 환경이나 영향 의존성이 바뀐 경우에만 필요한 검사를 반복한다. A1 실행법과 범위는 `BASS_HE_NUMERICAL_ARCHITECTURE.md`에 있다. Historical B1 scripts는 저작 과정의 기록이며 portable 실행 계약이 아니다.

`MANIFEST.json`은 private payload의 SHA256/bytes를 기록하며 자신과 자신의 checksum sidecar는 제외한다. 외부 ZIP SHA256과 delivery receipt가 봉인된 전송 객체를 식별한다. ACK/remote metadata 확인과 실제 다운로드 복원은 구분한다. Publication identity는 private `provenance/PUBLICATION_RECEIPT.json`과 외부 receipt에 기록한다. 전체 프로그램은 미완료이고 다음 단일 node는 A1b다.
