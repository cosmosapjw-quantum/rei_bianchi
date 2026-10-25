# 최근 파일 메타데이터 목록 — 복구본

**3페이지, 파일 498개**의 최근 메타데이터를 다시 보존했다. 파일 identity도 498개로 중복은 없으며, 생성 파일 464개와 업로드 파일 34개다. 마지막 페이지는 98개와 terminal `next_cursor=null`을 반환한다.

## 복구 출처

이 문서와 JSON 요약은 소실 전 파일의 byte-exact 복원본이 아니다. 실제로 남아 있던 증거와 아래 복구 경로로 재작성한 요약이다.

| 파일 | 복구 경로 | 정확히 주장할 수 있는 범위 |
|---|---|---|
| LIBRARY_RECENT_0_PRIVATE.json | 살아남은 로컬 mirror에서 복사 | mirror 원문과 byte-identical |
| LIBRARY_RECENT_1_PRIVATE.json | functions store에 남은 실제 도구 응답을 재직렬화 | 실제 응답 내용에서 복구; 소실 전 전체 파일 hash와 비교하지 못함 |
| LIBRARY_RECENT_2_PRIVATE.json | 원래 page 1의 실제 다음 커서로 승인된 단 1회 복구 요청 | **REFETCHED_FOR_RECOVERY**; 원본 전체 bytes와 비교 불가 |

Page 2 복구 요청은 원래 인수와 실제 저장된 커서를 그대로 사용했다. 반환한 **98개**, **terminal null**, **2026-10-23 03:15:12.954581 UTC → 2026-10-22 00:42:38.549362 UTC** 범위가 소실 전 관측 기록과 일치한다. 이 제한된 비교로 원본 전체 byte identity를 주장하지 않는다. 새 전체 freshness 조사나 추가 검색은 하지 않았다.

기존 survey 파일 중 없어진 119개를 mirror에서 복원했다. 이미 복원되어 있던 BACKUP_CONTEXT_SUMMARY.json, SOURCE_INTAKE_KO.md, SURVEY_KO.md, SURVEY_SUMMARY.json 네 파일은 보존했다. 각 복구 페이지의 현재 SHA256와 복구 출처는 LIBRARY_RECENT_SUMMARY.json의 recovery에 기록했다.

## 조회 범위

기존 조건은 `modified_after=2026-10-22T00:00:00Z`, 전체 경로 재귀 조회, 생성 파일 포함, 수정 시각 내림차순, 페이지당 최대 200개다. 이는 **해당 최근 메타데이터 창의 커서 열거**다. 모든 보관 파일의 본문·ZIP payload 또는 모든 대화를 읽었다는 뜻은 아니다.

| 페이지 | 파일 수 | 최신 수정 시각 UTC | 가장 이른 수정 시각 UTC |
|---|---:|---|---|
| 0 | 200 | 2026-10-24 22:13:03.276230 | 2026-10-24 03:39:20.371509 |
| 1 | 200 | 2026-10-24 03:39:20.368494 | 2026-10-23 03:15:18.982344 |
| 2 — recovery refetch | 98 | 2026-10-23 03:15:12.954581 | 2026-10-22 00:42:38.549362 |

이 커서열은 기존 첫 페이지에서 시작했다. 그 뒤 병렬로 생성된 파일까지 반영된 완료 시점의 원자적 목록이라고 주장하지 않는다. Root A2 생성 여부를 확인하는 새 검색도 수행하지 않았다.

## 이미 읽은 세 백업에서 재사용한 변화

아래 내용은 살아남은 BACKUP_DELTA_20261025.json과 library_recent_selected의 증거에서 재사용했다. 이번 복구에서 본문을 다시 가져오거나 archive를 다시 받지 않았다.

| 파일 | 생성·수정 시각 UTC | 크기 | 재사용한 관측 |
|---|---|---:|---|
| VIGILODE_D4_EFFECTS_S1_20261025.zip | 2026-10-24 22:13:03.276230 | 77,115 B | 기존 S0 4/20 뒤 archive S1 **12/20**. 과학 contract tests는 NOT_RUN. |
| BASS_CR_N5_NEUTRAL_DELIVERY_20261024T220158Z.zip | 2026-10-24 22:03:00.566447 | 26,886,833 B | CR science **18/20** 유지. Central M1 publication의 owner receipt가 추가되었다. |
| rei_bianchi_IGM_progress_20261024_2200_KO.pdf | 2026-10-24 22:06:46.885971 | 71,194 B | 명목 22:00 보고서이나 실제 audit은 21:42:33–21:49:34 UTC. 이전 scoped 상태를 재사용하며 새 physical HI history를 제공하지 않는다. |

Vigil archive의 source commit은 `555a93e5bffbed4b488ee0496e73d8095b08eab4`다. 현재 Git ref를 이번 복구에서 새로 확인한 값은 아니다. 기존 읽기는 ZIP 40개 member 중 문서/JSON 6개에 한정된다.

CR science commit은 `5eb895abbacce1642c451fd3fdfd2f776783871f`이며, 저장된 crossbinding은 CLAIM_GATE와 LOOP_LEDGER_SCIENCE가 앞선 pinned Git 원문과 byte-identical임을 기록한다. Central **`2354d6e995fde736fffbcad2d0e40473218cb8c4`**는 expected parent `fc159d2b15843bdfe81af0840bc07392a4977680`를 가진 **archive 내부 owner receipt**다. 이를 현재 ref의 새 관측으로 바꾸지 않는다. 기존 읽기는 ZIP 482개 member 중 문서/JSON 8개였고, archive 존재만으로 R10/C10/D/M2/terminal acknowledgement를 완료 처리하지 않는다.

PDF 전체 텍스트는 앞서 11페이지·589줄, `has_more=false`까지 읽었다. 보고서 자신이 새 remote reads/science/archive GET을 모두 0으로 기록한다. 과거 cutoff의 HE B3-pending 및 next-unit-NOT_FROZEN 문구는 이후 직접 관측이나 현재 root의 동결된 stress 계약을 덮어쓰지 않는다.

## 작업 경계

세 파일에서 새로 채택할 수 있는 실제 물리 HI history는 확인되지 않았다. **498개 전체 payload나 모든 대화에 해당 입력이 없다고 단정할 수는 없다.** 내용에 관한 위 결론은 이미 읽은 세 파일의 범위다.

현재 `HI_NATIVE_MASSIVE_STRESS_20261025` 계약은 이 복구로 바뀌지 않는다. 새 review/admission이나 다음 unit을 시작하지 않았고, 전체 물리 완료율은 `null`을 유지한다. 이번 복구의 원격 호출은 승인된 terminal-page 메타데이터 요청 1회다. 추가 검색·본문 조회·다운로드·branch/ref 조회·과학 실행·테스트·CAS·render·Git 변경·provider upload·Library 경유 사용자 첨부 읽기는 모두 0회다.
