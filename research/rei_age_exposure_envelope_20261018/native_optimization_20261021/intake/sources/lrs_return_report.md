# 현재 상태 — NCP 반환 완료, 2026-10-20T110800Z

상태 갱신: 2026-10-20T17:20:33Z. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**, VigilODE pin **8a8bd409b1d96c7b7421f496d229e119fd3d284e**의 실제 NCP 결과를 회수했다. metadata intake HEAD는 **90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec**이며 실행 source와 구분한다.

Locked release build exit 0 (345.147809 s), Rust 4 unit + 6 integration = **10 PASS**, 기존 **cell-cache 19설정(10 Radau + 9 SSPRK 대조) 모두 완료**다. 누적 RHS 시도 38,840, raw 내부 경과시간 합계 4.937230308 s다. `cell-borrowed` fixed Radau N2의 exit 0과 유한 물리값 일치가 반환됐다. 이 대화의 새 native 실행·build는 각각 **0**이며 저장된 반환 증거를 분석한다.

NCP binary SHA256은 **c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992**다. 이전 C10 sandbox binary `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`와 다른 실행 산출물이다. borrowed 개별 argv·inputs receipt·outcome receipt·binary hash는 archive에 없다. 동일 binary 연결은 delivery의 진술이며 독립 borrowed receipt로 복원되지 않는다. 명령을 추정하지 않으며 이 제한만으로 native 재실행을 의무화하지 않는다.

N2의 RHS 395·cell preparations 2,680·node visits 252,800은 같고 지정 상태/node clone은 cache 338/216,320 대 borrowed 0/0이다. raw wall은 cache 0.041180299 s, borrowed 0.061808789 s이며 stderr 마지막 0.091509 s는 측정 경계가 다르다. **speedup·memory reduction은 NOT_ESTABLISHED**, default legacy·성능 경로와 batch cell-cache는 유지한다. source-on 일반2차·uniform stiff·일반 양수성·Case B/full EoR/signed Bianchi·넓은 positive-CMB/비영 boundary·continuous global certificate는 HOLD, production은 NOT_ISSUED다.

archive `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`: 47,372,583 bytes, SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`. 이전에 게시된 이 archive의 양쪽 full readback receipt와 이번 회수 증거를 구분한다. 저장소 CI 두 job의 cargo fmt 실패·cargo test skipped도 NCP 표적시험 PASS와 별개다.

다음 행동은 반환 결과를 사용하고, 실제 profile이 병목을 보일 때 후속 optimizer 하나만 선택하는 것이다. 완료된 build·19설정·N2 smoke를 강제로 반복하지 않는다. 이번의 승인 범위는 ADMIT_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT이며, 독립 판정 PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT와 함께 반환 분석 STATE와 review/에 기록했다.

## 반환 분석과 현재 판정 상태

19설정의 4.937230308 s는 각 raw `wall_s`의 **내부 경과시간 합계**다. raw 측정은 초기화 전에 시작하고 JSON serialization 전에 끝난다. 따라서 native RHS나 rate evaluation의 독점 CPU 시간으로 해석하지 않는다.

기존 NCP 결과와 현재 source의 연결을 실제 저장 증거로 읽은 뒤 상위 인계 포인터를 수정했다. 과거 C10 source hash·root admission·backup receipt·publication ACK·CI 기록과 기존 NCP 원문은 수정하지 않았다. 이번 root acceptance는 **ACCEPTED_SCOPED**, 구현하지 않은 독립 Astra의 최종 판정은 **PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT**다. 실제 판정 원문은 `review/ROOT_ADMISSION.json`, `review/INDEPENDENT_REVIEW.json`, `review/REVIEW_KO.md`에 보존했다. 기존 `ncp_20261020T110800Z/INDEPENDENT_REVIEW.json`의 PASS_SCOPED는 이전 metadata HEAD의 판정으로 구분한다.

## 저장 출력의 유한 비교

이전 C10 v2의 **실제 cell-borrowed 19설정**을 새 NCP cell-cache 19설정과 비교했다. 이전 full19를 cell-cache라고 쓰지 않는다. 유한 numeric leaves 316,559개·기타 leaves114개·containers24,346개에서 수치 차이0·구조 차이0·공통 work-counter 차이0이다. 별도의 같은 source cell-cache N16 fixed/birth/disabled 세 대조에서는 유한 numeric leaves154,411개·기타18개·containers11,864개 모두 차이0이다. 세 대조는 기존19설정의 일부를 다시 비교한 것이며 총22 unique 설정이 아니다.

비교는 physical config/initial/records/실제 dt_s와 RHS를 포함하고 timing과 native-evaluation mode/clone 계수를 명시적으로 분류했다. 허용오차를 바꾸지 않았다. 두 host의 출력/invariant diagnostics는 이 유한 자료에서 일치했다. 이는 일반 차수·강성·양수성 정리가 아니다. 저장 JSON의 signed-zero difference0도 과거 C10을 전면 bitwise 검증했다고 소급하는 근거로 쓰지 않는다.

상위 Astra의 최종 결정은 **ADMIT_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT**, 상태는 ACCEPTED_SCOPED다. 독립 Astra의 최종 판정도 PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT이며 과거 C10 판정과 구분한다. 실제 inspector·결과·실행 outcome은 `analysis/`에 보존했다. 원본19 raw를 Git에 복사하지 않고 기존 archive의 정확한 입력 경로·hash를 결과에 기록한다. 이 대화는 native19matrix+borrowed1의 반환을 가져왔으며 native 실행을 새로 한 수는0, 새 unique 과학 설정도0이다.

## intake 범위와 실행 수단

PR198 comments timeline의 실제 응답은 비어 있었다. metadata base91a65b3에서 HEAD90c46b까지 2 commits ahead이고 `ncp_20261020T110800Z/`의 5개 metadata 파일만 추가됐다. evidence publication은 `301297a2cd34346d666ec74e12831697db9a6f01`, 이후 HEAD message는 “Record independent scoped review of LRS V14 result”, 작성 시각은 2026-10-20T11:34:41Z다.

branch API는 100/100/53 항목의 3페이지 metadata를 읽었다. 내용과 delta를 확인한 것은 PR198과 직접 관련 LRS v6–v14 branch identities다. owner 전체나 모든 관련 repo 내용을 완전하게 검색했다고 주장하지 않는다. PersonalContext query는 07:48/11:15의 이전 assistant NOT_RUN과 더 오래된 d87 문서만 반환했고 새 receipt는 없었다. 다른 모든 대화의 완전 검색은 아니다.

Desktop Commander list_devices는 cosmosapjw device online (`edd1b263-56a0-4391-8a2a-677dd00eabf5`)을 반환했지만 실제 start_process는 monthly usage cap으로 거절됐다. 도구가 retry/reconnect를 금지했으므로 SERVICE_ERROR로 분류한다. 성공한 SSH·원격 read command는 없다. 로컬 Python 3.12.14 probe는 PASS이며 C++는 요청·probe하지 않았다.

tool catalog 갱신 뒤 transient local workspace evidence의 소실을 관측했고 원본 agent archive가 없어 동일 provider archive를 회수했다. 원인은 확인되지 않았다. 분류는 RUNTIME_INTERRUPTION_RECOVERY이며 native 재실행은 없다. 기존 결과의 validity와 packaging/provenance 문제를 구분한다. archive 안 일부 historical delivery JSON의 terminal literal backslash-n은 packaging 한계이며 원본 bytes를 고치지 않았다. 이번 생성 JSON은 실제 newline을 사용한다.
