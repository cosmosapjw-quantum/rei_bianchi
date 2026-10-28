# 임시 작업 공간 복구와 보존 범위

## 판정

최종 포장 전 기존 임시 작업 디렉터리가 사라진 것을 실제 파일 조회로 확인했다. 원인은 **NOT_ESTABLISHED**다. tool catalog 변경과 시간상 인접했다는 관측만으로 인과관계를 주장하지 않는다.

과학 source, 실제 child raw, 계약, 독립 심사, admission을 포함한 게시47파일은 모두 복구됐다. 과학 실행을 다시 하지 않았다. 일부 조사 작업물과 문헌 도구의 전체 반환값은 보존되지 않아 그 한계를 아래에 명시한다. 복구 작업은 기존 과학 판정의 범위를 넓히지 않는다.

## 원격 패키지의 실제 byte 복구

Dropbox에서 이미 저장된 A/B/parent C를 읽고 다음 고정 SHA256과 일치함을 확인했다. 실제 수신 bytes를 사용했으며 새 ZIP으로 재생성해 같은 패키지라고 주장하지 않았다.

| 패키지 | Bytes | SHA256 |
|---|---:|---|
|A preexecution|50,988|cbaef6567202ed31b65a9bb0d7ca0104a40da01e5efbd45359132cb792ccc3e4|
|B reviewed|143,551|d650f075bf9e80da47d2f6c3069b5453dc2936583674395ccd4ba9fa00305341|
|parent C|3,670,130|50ce6fd5ffd38fef75cabe6dd25c8495e2347d5c817277a5aefa1fa08b8cb266|

근거는 recovery/DOWNLOAD_RECEIPT.json이다. Drive는 기존 upload/metadata ACK를 유지하며 이번에 bytes를 별도 재다운로드하지 않았다.

47파일은 남아 있던 실제 게시 payload의 UTF-8 content로 복구한 뒤 원래 B의 member manifest와 각 size/SHA256을 한 번 비교했다. 전부 일치했다. A는 PREFLIGHT.json, STAGE_A_MANIFEST.json, parent_backups/FINAL_DELIVERY.json도 복구했다. 과거 준비의 NOT_AUTHORIZED, 실행 당시 PENDING 같은 epoch별 기록을 현재 상태로 덮어쓰지 않았다.

recovery/PAYLOAD_RECOVERY.json은 실제 비교 결과다. recovery/RECOVERY_COVERAGE.md/json은 **A/B/payload만 사용한 첫 복구 단계**의 결손 목록이며, 아래 원래 도구 반환값 복구 이전의 관측이다. 그 목록을 최종 미복구 목록으로 해석하지 않는다.

## 원래 조사 반환값 복구

별도 조사 agent의 retained store에 원래 반환 객체가 남아 있어 recovery/recovered_survey/에 저장한다. 새로운 조회로 옛 관측을 대체하거나 요약에서 원시 payload를 재구성하지 않는다. 이 경로의 복구 manifest/status가 저장된 응답의 실제 범위를 기록한다.

복구 대상은7repos/1,323heads의 raw pages,53기존PR+4head질의+10source reads의67응답,3compare와D3commit,Drive/Dropbox목록·metadata·text 응답,실제PersonalContext error다. 원래 SURVEY_SUMMARY도 보존한다. 원래 wire JSON의 공백·키순서와 새 serialization의 byte identity를 주장하지 않으며, 보존된 원래 구조화 반환값이라는 의미다. 이 구별은 과학 source/raw의 byte identity 검증과 별개다.

## 남은 결손

20개 원래 첨부 payload,7개 전체 archive member inventory,별도 member-read mapping/추출본문/PDF 추출물은 현재 복구되지 않았다. 원래 ATTACHMENTS_MANIFEST.json과 ATTACHMENTS_REVIEW.md는 B/payload에서 복구됐고 독립 reviewer가 다시 읽었다. 원래 관측된 목록·읽기 범위·해석은 보존하지만 manifest를 첨부 원본 bytes로 대신하지 않는다. 상세는 recovery/recovered_attachments/REVIEWER_RECOVERY_STATUS.md/json이다.

현재 research/SCISPACE_RAW.json, WOLFRAM_CONTEXT_RAW.json 및 일부 primary-page 전체 반환값도 미복구다. 원래 research/SOURCE_READS.json과 primary URL/read scope는 보존됐다. 보고된 SciSpace 검색1회·Wolfram context1회·evaluator0은 원래 기록을 따른다. 도구를 재호출해 과거 raw인 것처럼 기록하지 않았다.

원래 STAGE_A_LOCAL.json/STAGE_B_LOCAL.json은 자기 ZIP 밖에 있던 파일로 byte 복구되지 않았다. 실제 dual-provider ACK와 이번 remote byte 복구 영수증은 남아 있다. parent C는 원래 bytes로 포함하고, 과거 조사 응답을 현재 epoch의 응답으로 다시 표시하지 않는다.

## 비용·후속 게시

과학 재실행0, pressure 실행0, old22/66/83·ANGTHERM01/02·NCP 재생0이다. 다운로드·해시·복구·포장 비용은 별도 미측정 **UNKNOWN_NOT_ZERO**이며 scientific child CPU0.036647s에 추가 측정된 것처럼 합산하지 않는다. 과거 cap 초과·unknown과 현재 one-child 소진을 그대로 보존한다.

게시 전 live HEAD가 e69b01457f1f27e11806ad724a925a1f723d0c24로 이동했음을 확인했다. actual compare와 직접 source read로 HE-ANG TDCS54 관련 assembly3파일의 병렬 변경을 확인했다. 새 base tree를 사용해 이를 보존하고, 소유한 HI leaf의 마감 기록만 expected-SHA/non-force로 추가한다. science fca9a31…의 source/raw와 보호 ANGTHERM02는 수정하지 않는다.
