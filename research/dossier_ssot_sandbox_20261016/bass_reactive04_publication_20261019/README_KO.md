# BR04 게시·복구 receipt

[Draft PR #203](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/203)의 과학 소스 commit은 `1b5acc89cfbcfa7b42b87255e604f8f86c6a3a01`입니다. 이 디렉터리는 그 소스를 변경하지 않고 이후 게시·백업·복구 사실을 추가합니다.

전체 ZIP `REI_BASS_REACTIVE04_TIME_AGE_20261019_ae69c7c9_FULL.zip`은 18,943,104 bytes이며 SHA-256은 `ae69c7c912cb918112b96b471a5494a3dea6cc24e265d6a3604af6bed5c103da`입니다. 두 cloud에서 실제 GET·별도 폴더 복원을 실행했고 각각399 entries와398 payload hashes를 검증했습니다. [Drive 파일](https://drive.google.com/file/d/1oh_aSpB0Ab-2ewdQJ1UGH3iFFSdO1izN/view)과 Dropbox의 정확한 경로·provider hash는 `PUBLICATION_RECEIPT.json`에 있습니다. Drive 별도 provider checksum은 connector가 노출하지 않았으며 raw SHA 검증은 완료했습니다.

## 복구 범위

게시 중 실행 환경이 교체돼 원격 commit에서326개 파일과125개 source-input 계약을 복구했습니다. Cargo의 잘린 설치 파일은 원 공식 payload 크기·SHA를 확인해 복구했습니다. 이 runtime 실패는 연구 코드나 물리 해의 실패가 아닙니다.

실제 추가 light 재현은 Rust15·Python7 PASS, study CSV7개와 독립 기준CSV3개의 원본 byte identity, 보존 native9개 이력의 동일한 재분석을 확인했습니다. 새 native 계산은 하지 않았습니다. 원래 전체224 및 strictClippy 실행 기록은 같은 소스의 과거 실제 실행으로 유지합니다.

독립 Decimal JSON 한 개는 이전 UTC/Python 문자열을 복원하지 못했습니다. 그 원본 기대SHA는 동결 계약에 그대로 두고, 새 실제 실행 provenance를 갖는 파일로 전체ZIP에 포함했습니다. `DECIMAL_PROVENANCE_REPLACEMENT.json`에 이전/현재 bytes와SHA 및 재검산 범위를 구분했습니다. 이 한 파일에 원본바이트 복구를 주장하지 않습니다. 과학CSV 및 native분석JSON의 원래 바이트는 검증했습니다.

## 판정

`BASS-REACTIVE-04_TIME_AGE=COMPLETE_VERIFIED_SCOPED_DIAGNOSTIC_CONTROL`; 긴 구간의 joint time–age 수렴은 여전히 `NOT_ADMITTED`입니다. 다음 DAG는 실제 retained cohort에 대한 read-only birth-width/error monitor와 r4–8 비교입니다. 기존 source/물리owner/CX/four-corner controller와 이전 branch·PR은 수정하거나 merge하지 않았습니다.

ZIP의 해시는 이 사후 receipt와 순환하지 않도록 source/복구 payload를 먼저 동결한 뒤 계산했습니다. 해당 source patch와 부모를 요구하는 증분bundle은 ZIP 안에 함께 있습니다.
