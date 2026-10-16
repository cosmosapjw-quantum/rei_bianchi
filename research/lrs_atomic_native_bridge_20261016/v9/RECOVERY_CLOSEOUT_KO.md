# V9 중단 복구와 최종 전달

- 시작점: PR168 `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b` 고정. 원본 PR150, NCP, 다른 연구 브랜치 변경하지 않음.
- 직전 중단: 클라우드 container_session_expired, 이후 연결 복구에 성공.
- 실제 연구: 매끄러운 고정-energy photon birth/HI absorption/neutral opacity 문제에서 R5의 4개 주요 시간배치 오차계수 유도. 양의 정확 반응쌍 및 중점 Strang 업데이트 구현. 독립 SciPy Radau와 5문제×6알고리즘×6해상도=180개 결과. Python 61/61 PASS.
- 원본 `src/birth_opacity_clock.py`, `tests/test_birth_opacity_clock.py` Git blob과 샌드박스 원본 바이트 일치. R5 원문, C8 결과 JSON/CSV, 실행로그, handoff, 무결성 ZIP을 GitHub PR169로 게시.
- Google Drive 단계별 raw R5/C5/C6/C8/C10 업로드 완료. 최종 ZIP 원격 whole readback SHA-256 일치; CRC와 manifest15/15, 새로 압축해제한 환경에서 61 테스트 및 180행 재실행 PASS.
- ChatGPT Library 별도 아카이브 ACK. 신규 Dropbox 백업 미실시 (사용가능 connector는 파일 parameter 주입 필요), 원격 바이트 검증이라고 주장하지 않음.
- 과학적 주장은 smooth 0D 조건부: `N′=S(X)-k(X)NM`, 총 H 핵수 정규화, 80 eV/13.6 eV 고정광자, prescribed H/chemistry. Native PR150 source-on 전체계의 1차 오차원인, moving Verner 문턱, full EoR, Case B, signed Bianchi는 미검증.
- 다음: PR169의 handoff를 읽은 Codex가 사용자 다운로드 없이 GitHub checkout에서 원본 PR150의 동일 상태·동일 구간 native source-on clock-factor 실험을 수행. 독립 Draft PR와 양쪽 클라우드 백업을 NCP에서 실시.
