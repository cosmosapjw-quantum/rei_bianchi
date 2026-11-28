# HE29 백업 변경분 입력 확인 — 2026-10-20

## 판정과 재사용

**새 HE29 native 반환 0건, 요청한 네 기준해 쌍의 새 인정 결과 0/4 observed**이다. m8/GL4/q0의 `(r2,512)`, `(r4,512)`, `(r8,512)`, `(r4,1024)`에서 각각 Radau와 DOP853, source·binary·table identity, 실제 실행 출력이 함께 있어야 인정한다. 이번 확인에서는 그 조합을 갖춘 반환을 찾지 못했다. 미게시·미반환 원격 프로세스는 관측하지 않았다.

이전 완료 HEAD `1765522318438e966e61d8a72f12084550da399d`, 실행 코드 `a5d4711460c09b310b78c9692aa62534b7a843d3`, COMPLETE77f와 CLOSEOUT3380의 양쪽 raw readback PASS를 재사용했다. 두 기존 archive를 다시 다운로드하지 않았다. 과거 HE28/HE29 테스트·benchmark·native 실행은 모두 재실행 0회다.

조회는 2026-10-20 05:58:47 UTC에 시작했고, 보수적 변경 기준은 **2026-10-20 02:32 UTC**다. 변경 기준이 이전 게시 완료보다 이르므로, 새로 보이는 우리 자신의 완료 보존본은 기존 완료 근거로 분류했다.

## 실제 조회 범위

| 경계 | 실제 확인 | 해석 |
|---|---:|---|
| Drive canonical 최신 직접 목록 | 100개; 최저 수정 시각 2026-10-15 18:35 UTC | 실제 수정 내림차순이 cutoff 이전까지 닿았다. 이후 항목은 기존 COMPLETE77f·CLOSEOUT3380 두 개다. |
| Drive 관련 publication 표면 | 직접 최근 목록 총 11회 / 296개 항목 | 이전 폴더 목록에서 선택한 10개 경계와 새 REC R3P 폴더 1개다. 예전 264폴더 전체 재귀를 반복하지 않았다. |
| Drive 검색 진단 | keyword/raw filter 4회, exact metadata anchor 1회 | 검색이 알려진 새 보존본도 회수하지 못해, 검색의 0건은 부재 근거로 쓰지 않았다. |
| Dropbox 변경 후보 검색 | HE29·HE30·VigilODE·REI·20261020·native·reference 7회 | 반환 페이지는 모두 `has_more=false`였지만, 날짜 필터와 검색 회수 누락을 별도로 기록했다. |
| 실제 새 내용 읽기 | raw 객체 5개, extracted JSON receipt 1개 | archive 4개는 231개 regular member를 열거하고 선택 identity 문서를 읽었다. payload 추출·실행은 하지 않았다. |

Drive recent-documents 도구도 archive anchor를 회수하지 못해 archive 부재 근거에서 제외했다. Dropbox의 `last_modified_after`는 cutoff 이전 항목을 함께 반환하여 반환된 실제 수정 시각으로 다시 걸렀다. REI 검색은 오래된 100개를 반환하면서 끝났지만, 다른 조회가 새로운 REI 파일을 보여 주었으므로 전체 change feed로 표현하지 않는다.

## 새 후보의 source·실행 범위

| 후보 | 실제로 읽은 근거 | HE29 분류 |
|---|---|---|
| REI LRS recovery | 새 REMOTE_ACK JSON; source `d87ba9ca…`, recovery publication `8f8dd2ea…`, `native_recovery_runs=0`, `builds=0` | 기존 LRS 19개 설정의 문서·환경 복구. HE29 네 쌍이 아니다. |
| REI LRS optimization C1–C4 | 93,202-byte archive; 19개 member; DAG·optimization contract·source intake | LRS cell-cache 최적화 설계/부분 구현과 unchanged-source build. C5 진행 중, C6 candidate pending이며 이 snapshot에는 native history 완료 결과가 없다. |
| REI age-envelope v7 | 110,415-byte delivery confirmation; source `354823050e6da98e64dde40596be061ce22e71f2`, delivery `cf00684741eb612e35f987713c28937513d44d57` | PR199의 별도 age-envelope source·보존 receipt. 기존 native inputs 153개와 v6 runtime을 재사용한다. |
| BASS_CR C21H resume | 302,813-byte ZIP; 75개 member; PAYLOAD_MANIFEST·current Git intake·DAG | `runtime_source_changes=0`, `native=NOT_RUN`. bass_cr의 복원·게시·제조 검증 근거다. |
| BASS_CR C21H/C21I handoff | 320,523-byte ZIP; 49개 member; recovery receipt와 handoff | C21H native chemistry/NCP NOT_RUN. C21I는 이 보존본 시점에서 intake 상태다. |
| REC R3P stage2 | 1,106,797-byte ZIP; 88개 member; stage manifest·DAG·보고서·build receipt | 기존 R3M prefix/spectral stream 감사의 가속. U5의 h/h2 HOLD를 유지하고, 이 snapshot에서 실제 U5 16-step smoke는 아직 대기 중이다. |

네 archive의 전체 member 이름에 HE29/HE30 경로는 없었다. 분류는 그 사실만으로 결정하지 않고 위 model/source/실행 상태와 함께 확인했다. REI LRS unchanged-source build의 기록된 executable SHA256은 `28dfc8dbfe627acd7c7d2f77c08746db6d5f67f620b6e6a38a1b658c52eebc2d`다. 이 build가 HE29 native 실행을 제공하지는 않는다.

REI age-envelope의 큰 execution-ready ZIP과 LRS recovery 원본 archive는 재다운로드하지 않았다. 직접 읽은 delivery/recovery receipt를 근거로 별도 프로젝트의 보존 범위를 기록했고, 그 producer의 raw 검증 주장을 이번 담당자가 다시 수행한 것으로 표시하지 않았다.

## 새로 읽은 raw identity

| 객체 | Bytes | 이번 GET에서 관찰한 SHA256 |
|---|---:|---|
| REI_LRS_OPTIMIZATION_C1_C4_20261020.tar.gz | 93202 | `ec610f486be6c99c367d8be0ae9b500fa9e884c90d946d6ef1704d9ccdb1514b` |
| REI_AGE_ENVELOPE_DELIVERY_CONFIRMATION_20261020_v7.json | 110415 | `4423349eec92b70265b3720c2ee857853926388cfa0a77fe201269901fd3981c` |
| BASS_CR_C21H_RESUME_EVIDENCE_20261020T053224Z.zip | 302813 | `db25e7c07edd8ff4b0296164f9904a0d9173b5c3a7ee09060b05f6fa01a93339` |
| BASS_CR_C21H_C21I_THREAD_HANDOFF_20261020T030354Z.zip | 320523 | `74a366d38f53753123913daa7fde074771da427b2036f1ad86fe39138d1e992a` |
| REC_R3P_STAGE2_VALIDATED_CODE_20261020.zip | 1106797 | `2f130036af177764b34e3d3438812adf9693f2368a1100f9d9f42e276146e250` |

첫 네 객체의 합쳐진 inspection 출력이 도구 출력 한도를 초과해 잘렸다. 이 오류를 보존하고 같은 네 객체에서 **한 차례만 출력 크기를 제한한 identity 요약**을 다시 읽었다. 총 HTTP GET 시도는 9회다. 완전한 구조화 receipt로 확인한 최종 5개 raw 객체는 합계 1,933,750 bytes이다. 첫 4개 시도의 합쳐진 반환이 잘렸으므로 그 첫 묶음 전체의 개별 성공·전송 합계를 별도로 확정하지 않았다. 이는 새 후보의 내용 조회였으며 과학 코드·기존 검증·benchmark 재실행은 아니다. 최종 bounded 요약은 모두 파싱됐고 남은 content-read 오류나 pending 요청은 없다.

## 남은 관측 한계

이 결과는 변경분 후보에 대한 범위가 정해진 확인이다. 검색 색인 지연, 날짜 필터의 미적용, 선택하지 않은 더 깊은 폴더의 새 쓰기·이동·metadata 보존 변경을 완전히 배제하지 않는다. 기존 넓은 census를 반복하지 말라는 작업 범위를 지켰으므로, 예전 264개 Drive 폴더를 이번 시점에 다시 모두 조회했다고 쓰지 않는다.

NCP·RemoteDesktopCommander·다른 원격 실행 도구는 호출하지 않았다. **0/4 observed는 확인 가능한 반환의 상태이며, 미반환 프로세스가 한 번도 실행되지 않았다는 판정이 아니다.** 업로드·원격 쓰기·소스 변경은 없으며, 이번 담당자의 로컬 산출물은 이 파일과 [상세 JSON](BACKUP_DELTA_INTAKE.json) 두 개다.

연속 스펙트럼, 온도 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB의 승인 범위는 이 intake로 확대되지 않는다.

## 병렬 Git 조사에서 알려온 후속 변화

이 백업 후보를 읽은 뒤 root는 rei_bianchi의 `33ae18c3…` 새 LRS native addition push를 발견하여 exact identity를 확인 중이라고 알렸다. 이 정보는 root의 별도 Git 조사이며, 이번에 실제 읽은 05:47 UTC C1–C4 archive의 snapshot 판정을 소급 변경하지 않는다. 관련 연구의 새 실행·감사·구현 결과가 있다는 사실과 새 HE29 기준해 인정 0/4는 구분한다. 후속 LRS 결과의 인정은 별도 source·binary·model identity 검토에 따른다.

이번 continuation의 활성 연구 규약은 root가 main/references에서 확인한 `physmath-research-loop1.0.0`이다. 이전 census에 사용한 규약 버전을 이번 기록의 활성 버전으로 이월하지 않았다.
