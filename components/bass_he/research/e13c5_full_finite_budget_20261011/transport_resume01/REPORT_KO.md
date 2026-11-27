# BASS_HE E13C5 — 최초 전송 실패의 판정과 최소 재개

## 판정

반환 archive를 실제 내려받아 22,851 bytes 및 SHA-256 `98571ce22e2eb2c2246a432960a67d51fa55356edfa4e1ee295ab256d818d09f`를 확인했다. 실패는 `TRANSPORT_FILENAME_BINDING`이다. NCP의 실제 전체 ZIP 복구와 저장 결과 재현은 계속 `NOT_RUN`이다.

수신 측 inventory의 파일명은 `.zip.part002.bin`이고, 원 manifest가 요구하는 이름은 `.zip.part002`다. 원 restorer는 모든 part의 정확한 이름을 먼저 확인한다. 따라서 `FileNotFoundError`, `verified_parts=[]`, 부분 출력 없음, exit 1은 코드의 실행 순서와 일치한다. 수치 계산의 호출은 발생하지 않았다.

## 증거의 범위

| 항목 | 확인 상태 |
|---|---|
| 반환 ZIP 전체 bytes/SHA | 이번 Chat에서 실제 파일을 직접 검증 |
| 반환된 kit payload 12개 | 동봉 manifest와 실제 bytes/SHA 일치 |
| 원 manifest/restorer | 실제 반환 파일과 고정 Git blob의 일치를 독립 확인 |
| 대형 part001/part002의 SHA | 수신 영수증의 기록이 manifest와 일치; 이 작은 반환본에는 대형 조각이 없으므로 이번 Chat에서 재해시하지 않음 |
| 실제 NCP core/source/lock/입력 검사 | NOT_RUN |
| 실제 NCP semantic/CSV parity | NOT_RUN |
| budget/physics/full-first2/N512 | 모두 0 |

호스트 `s1a0e5abed09`, CPython 3.12.3, Linux 6.8.0-124-generic, affinity 0–63은 수신 보고다. Ubuntu 24.04.1이라는 배포판 표기는 사용자 반환 메시지에서 제공되었다. 별도 cloud provider attestation은 없다.

## 최소 수정

기존 전달 절차에 다운로드된 물리 파일명과 manifest basename을 명시적으로 대응시키는 단계를 보완했다. 새 `code/place_verified_part002.py`는 정확히 명시한 `.part002.bin`만 읽는다. 원본의 40,580,022 bytes/SHA를 확인하고 canonical basename의 새 파일을 만든다. 복사한 실제 파일의 SHA를 확인한 뒤 원 restorer의 atomic no-replace 함수로 게시한다.

원 `.bin`과 첫 실패 영수증을 보존한다. Canonical 파일이 이미 있으면 exact bytes/SHA가 같은 경우에만 확인 후 그대로 사용하며, 다른 파일은 덮어쓰지 않는다. 광범위한 glob, 무조건 suffix 삭제, manifest 수정은 하지 않는다. 기존 scientific core, 원 ZIP, 원 restorer, budget source, RUN_LOCK 및 정밀도는 변경하지 않았다.

6개 작은 byte 대조가 통과했다: 정상 `.bin` 복사, 잘못된 해시 거부, 동일한 기존 canonical 확인, 다른 기존 canonical 보존, source symlink 거부, 게시 직전 다른 파일이 생기는 경합에서 기존 파일과 partial 보존. 이 대조는 generic 파일 배치 함수에 대한 것이며 실제 NCP 대형 조각 배치나 production CLI 실행을 뜻하지 않는다.

독립 검토는 원 실패의 증거 대조와 새 코드 읽기·기록된 대조 확인을 수행했고 concrete blocker 0으로 판정했다. 독립 추가 실행은 하지 않았다. 자세한 범위는 `review/`에 고정했다.

## 재개 조건

이름 배치 성공은 `PASS_SCOPED_PART002_FILENAME_BINDING`으로만 기록한다. 이후 새 ZIP 출력과 새 명시적 receipt를 지정하여 원 restorer를 한 번 호출한다. `PASS_LOCAL_TRANSPORT_RESTORE`가 확인되어야 내부 core/source/lock/입력 검증으로 넘어간다. 그 뒤 기존 NCP wrapper의 저장 결과 합산 1회를 실행한다.

첫 실패는 과학 invocation을 소비하지 않았다. 단계가 실패하면 자동 재시도하지 않고 새 실패의 원인과 로그·partial을 보존한다. 원격 업로드 ACK, 로컬 파일명 배치, ZIP 복구, 실제 호스트 합산 결과를 서로 구별한다.

원 과학 연구의 PASS_SCOPED 결과는 보존된 상태다. 이 전송 보완에서 새 물리 연구, 새 solver, continuum·physical·production·receiver 승격은 수행하지 않는다.
