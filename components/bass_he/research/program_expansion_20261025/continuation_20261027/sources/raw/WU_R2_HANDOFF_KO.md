# WU088_HH: 원 target19와 실제 공급자 registry R2 인계

## 현재 결과

고정 인계 `34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad`에서 이어, R1 source `18a6804d7cbe4879701e83631f7e908bbb84cef1`의 과학 결과와 실제 양쪽 백업을 보존했다. 원 PNG와 원 19개 반응식을 연결된 기존 자료에서 실제로 회수했다. **원래 19개 ID와 28개 명시 방향을 모두 유지하며, 27개 방향에는 실제 primary-source 참조가 있다.** `He4+γ→D+D`의 정방향 수치 행은 명시적 입력 의존성이다.

`SCIENTIFIC_ADMISSION.json`의 판정은 `ACCEPT_SCOPED_TARGET19_SOURCE_BINDINGS_AND_NUMBER_PROJECTIONS`이다. 독립 C9는 `reviews/C9_FINAL.json`, SHA256 `de646cc00802a2744518f19396c008f572bd49386414f956b24b4cc784a174d5`이다. 이 판정은 source 전사·정체성·관측량 구분·선언된 정수 사건 열에 적용된다.

| 항목 | 현재 확보 범위 |
|---|---|
| 원 target identity | 19개 ID, 28개 방향, 원 PNG 1,856,861 bytes |
| 새 실제 source variant | 26개: 핵 공급자 19개 + NNDC 3개 + He4 측정 4개 |
| native NACRE-II | 10개 표, 598개 T9 행 |
| native ENDF | MF3 246 knots, MF6 16 product의 1,777 yield knots |
| He4 실제 측정 | 두 원문의 두 채널, 합계 20개 값·통계/계통 오차 |
| 조건부 모형 | 원 대상 13개 계열 + 별도 closure 5개 = 18개 |
| 새 finite projection | 조건부 정방향 18개 + 선언 광핵 정방향 6개 = 24개 |
| 재사용 | R1 species 9개와 event 근거 24개; R1 125개 열은 재컴파일하지 않음 |
| 주 검증 | 13/13 그룹, 첫 실행 PASS |
| 독립 수용 | 원 실행의 9개 PASS 그룹 + 교정한 공개 metadata 그룹 = 10/10 |

R1의 102 source variant·125 candidate 열·92 species identity, 기존 249-check, PHYS91 결과와 REI18의 82개 저장 배경에 대한 완료 계산은 그대로 재사용한다. 원 PNG의 SHA256은 `472ba6be633d2b5fc05fc1e0e88f965ff3c0311b0697e3c35c05bbca1629e6f9`이다. R1 문서의 “원 network locator 미회수”는 당시 관찰이며 이 R2에서 그 입력 공백이 실제로 해소됐다.

## 물리적 의미와 남은 의무

광핵 source 관계는 네 종류로 분리되어 있다.

- Target 8, D(γ,n)p: 공식 ENDF/B-VIII.1 MF3/MT50의 배타 native channel.
- Target 7, He3(γ,p)D: MF3/MT5와 MF6 deuteron yield를 보존한 인수 형태 후보. 곱셈·보간은 수행하지 않았다.
- Target 11, Li7(γ,t)He4: 실제 total/inclusive source가 있으나 해당 배타 가지의 연결은 미해결이다.
- Targets 4·5, He4(γ,n)He3와 He4(γ,p)T: Shima/Murata의 실제 응답 평균 측정. efficiency·acceptance·모형 의존·각도 보정을 보존한다.

Target 6은 `sources/he4_photon/TARGET6_DEPENDENCY.json`의 직접 문헌/EXFOR 의무를 따른다. 현재 무관측 진술을 단면적 0이나 수치 상한으로 바꾸지 않았다. 모든 새 rate/Q/state/consumer admission과 activation은 false이며, 24개 열 모두 에너지는 `UNQUALIFIED:ENERGY`이다. source의 인쇄 Q, MT5의 0 필드, 임계값과 실제 에너지 침적을 구분한다.

NACRE-II native T9 표는 과거 100 K/10000 K constant-S 모형의 유효성을 검증하지 않는다. NIST total absorption의 partial-channel 할당, Li7의 ground/first-excited inclusive capture, 약붕괴의 bound spectator electron과 딸 상태, 원자–bare 질량·결합 에너지·공분산, named consumer는 각각 독립 의무다. 다음 실제 입력과 사상은 `NEXT_SOURCE_INTAKE_KO.md`에 있다.

## 반드시 재사용할 근거

1. `REUSED_CALCULATIONS.json`에 고정한 compiler·R1·PHYS91·REI18 출력과 원 검증 결과를 사용한다.
2. R2 `registry/`의 11개 JSON과 C9의 SHA를 사용한다. 같은 identity의 builder·parser·검증을 완료 확인 목적으로 다시 실행하지 않는다.
3. 독립 검토의 두 checker-only 실패를 삭제하지 않는다. 최초 독립 결과는 9/10이었다. 공개판의 의미 보존 문구와 source-supported 상태 annotation을 허용하도록 한 항목만 교정했고, 그 교정의 LF/form-feed locator 오류도 별도 v2에서 수정했다. 이미 통과한 source/24-column 검사는 재실행하지 않았다.
4. 비CC 논문 전문은 공개 묶음에 포함하지 않았다. 수치 사실, 원문의 URL/SHA와 정확한 표·수식·행 위치는 보존했다. 원문이 없는 행은 명시적으로 `original_bytes_bundled=false`이다. 독립 검토는 회수했던 실제 원문과 대조했다.

## 최신 권한·병렬 작업·예산

빌드 직전 실제 WU HEAD는 `18a6804d7cbe4879701e83631f7e908bbb84cef1`, expansion HEAD는 `34dd7d1…`, PHYS91 owner HEAD는 `2912a315aa39e7293000b7b2b8c7cc7a706fea9e`였다. 당시 최신 root AGENTS와 동결 snapshot이 정확히 일치했다. `authority/PRE_BUILD_REMOTE.json`, `PRE_BUILD_LOCAL.json`, `PRE_PRIMARY.json`에 실제 관찰을 보존했다. 게시 이후 HEAD는 `delivery/`의 실제 Git 영수증을 읽는다.

중앙 branch의 병렬 HE·GRID044·CR·BASS 갱신을 확인했다. 관찰한 최신 중앙 HEAD `a5db4bac9dafadae29685bbea3cec7f43ab990b2`의 DAG는 88개 노드이며, 그 14개 WU 노드는 앞선 science pin과 의미가 같았다. 원 중앙 DAG를 압축 원본으로 보존했고 WU overlay에는 14개 원 노드를 모두 유지했다. `DAG_DELTA.json`은 중앙 owner가 취합할 수 있는 WU 변경 기록이며 중앙 반영 ACK를 가정하지 않는다.

PHYS91 primary/reference/Wolfram remaining은 모두 **0**이다. global historical CPU·money·remaining은 **null**이다. 이 R2의 측정된 8개 경량 child 합은 CPU 약 **0.737753 s**, wall 약 **0.861847 s**이며 전체 세션 비용이 아니다. 검색·준비·검토·wrapper의 미측정 비용을 0으로 간주하지 않는다. 수치 rate/Q·IVP와 완료 과학 계산 재실행은 0이다. HH_R10=OFF, L4_ready=false, production=NOT_ISSUED를 유지한다.

## 게시·백업과 재개

사용자는 필요한 자동 게시와 Dropbox/Drive 백업을 명시적으로 승인했다. 추가 확인 없이 현재 source와 검증 결과를 보존하고 expected-SHA non-force로 기존 draft PR150 branch에 더한다. main을 merge하지 않는다. 이 문단은 source snapshot 작성 당시의 이전 관측이다. 그 시점에는 새 source 게시와 ZIP/백업이 진행 중이었으며, 현재 완료 상태는 `delivery/PUBLICATION_AND_BACKUP.json`과 아래 실제 전달 완료 기록에 반영되어 있다.

R1 source ZIP은 이미 양쪽 백업에서 실제로 내려받아 SHA256 `c1ced1cdeb7382064e64d11abd38d52466802a699edf99bd78aa355c0ce17863`과 일치했다. 새 R2 ZIP은 실제 게시된 source commit의 root AGENTS, 고정 expansion 인계, R1/R2 leaf 및 unchanged compiler를 포함한다. 현재 단위의 source ZIP은 후속 metadata commit과 구별한다.

새 노드에서는 최신 AGENTS·HEAD·병렬 작업·실제 backup receipt를 다시 확인하고, 현재 `NEXT_SOURCE_INTAKE_KO.md`에서 변경된 입력이 처음 필요한 단계로 이어간다. 다음 의무는 target6 직접 수치 자료 또는 선택한 기존 source의 state/branch/domain/consumer 연결이다. 원 19개 target ID를 지우거나 기존 synthetic 249-check를 물리 rate/핵 Q 승인으로 확대하지 않는다.

## 실제 전달 완료 기록

- Source commit: **71019bb469c92d1ea665155ed98c472b362d6706**, tree **d91c82fece682b12d34a01db8ae12b4dc55f4c66**.
- 기대 부모 SHA **18a6804d7cbe4879701e83631f7e908bbb84cef1**에 대한 non-force 게시와 원격 readback이 성공했다. [PR150](https://github.com/cosmosapjw-quantum/WU088_HH/pull/150)은 draft 상태다.
- Source ZIP: **WU_PROVIDER_REGISTRY_R2_TARGET19_SOURCE_20261025_71019bb469c9.zip**, 7,084,911 bytes, 380개 Git 파일 + manifest = 381 members.
- ZIP SHA256: **43845ea085797a6d628b722d58197a64a0af6f0a34a708f3dc981a5274faa906**.
- Dropbox **id:BSpOijBcT10AAAAAAEAfFg**, Drive **1C4NE14swNXTL4GXb-ol8HE8cm57sHaIe**의 완료 ACK 뒤 양쪽 실제 다운로드가 같은 바이트 수와 SHA256으로 확인됐다.
- 최신 전달 권위: delivery/PUBLICATION_AND_BACKUP.json, FINAL_BACKUP_ACK.json, CLOUD_READBACK.json, GIT_READBACK.json.
- 이 완료 기록을 담는 metadata child의 정체성은 containing Git commit으로 읽는다. ZIP의 source commit과 혼동하지 않는다.
- R10/C10의 이번 source 단위 전달은 완료됐다. 27/28 source 참조, target6 입력 공백, 물리 rate/Q/consumer 미승인 상태와 기존 예산은 바뀌지 않았다.
