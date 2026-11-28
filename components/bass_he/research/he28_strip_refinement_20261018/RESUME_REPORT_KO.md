# HE28 중단 복구 및 native 실행 승인 경계 수정

2026-10-18. 재개 시 원격 HEAD `c83858025a28528b35d6f56d13c351273aec6a27`에 HE28 구현과 source-only 수치 증거가 이미 게시되어 있음을 확인했다. 초기 intake만 다시 만들거나 HE27 native 캠페인을 재실행하지 않았다.

## 복원과 실제 변경

Drive 단계2 아카이브 123,765 bytes, SHA256 `b50eced554dcdd7a210ef5ec0346e2b5cf9be5c1b8cdb018e200a5e718f527b1`를 다시 가져와 내부 50개 파일을 검증하고 27/27 테스트를 재실행했다. HE27 113,771,104-byte 백업도 기존 두 조각에서 복원해 SHA256 `0a08d9a505a1af9fb2f0452e2db4207789186ad7d1780b9fd5e8a522ccaf5faf`를 검증했다. Dropbox HE28 검색에는 단계2 백업만 반환되었다. 이번 조회에서 새 HE28 native 결과는 발견하지 못했다.

`he28_run.py campaign --stage study`는 이전 pilot의 Python 소스와 binary만 검사했으며, source-table 해상도와 관련 기록의 일치 여부는 검사하지 않았다. 해상도512에서 받은 pilot 승인을256 study에 재사용하거나 TABLE/RESULT의 table digest가 다른 경우에도 실행 요청이 진행됐다. 명시적인 가짜 process dispatch를 사용하는 두 회귀에서 RED를 재현했다. 이것은 기존 연구 결과가 오염됐다는 증거가 아니라 NCP 실행 전 발견한 승인 경계 결함이다.

수정은 pilot/study table resolution 일치, pilot q0/m4/r2/GL4/n16 설계, owner/parent identity, TABLE와 RESULT의 table digest 및 table metadata 일치를 필수로 하고 boolean True만 인정한다. table digest 상호 일치 검사는 table 배열을 새로 재계산한 byte 검증과 다르다. study의 m/r/n은 명시된 여섯 조합으로 변경 가능하다. 모든 물리 및 오차 허용치는 유지했다.

최종 **35/35 tests PASS**: 기존27개+추가8개. Bash 구문/compileall 통과. 원본 parent17개 source SHA256 동일. 소스 정제 모델과 inherited native physics/transport/reference는 변경하지 않았다. 회귀의 가짜 성공 영수증을 native 실험으로 세지 않는다. 신규 native 실행0회, 새 격자 pilot NOT_RUN, study0/6 NOT_RUN이다.

## 보존된 과학 결과의 범위

앞 단계에서 실행된 270개 frozen-source future-kernel 비교와420개 table sample을 재실행하지 않았다. q0,m16에서 생존확률 최대 오차는 r1=3.582992108563943e-8, r2=1.1850303294203002e-8, r4=6.884057879297245e-9, r8=1.3721871416905174e-9, r16=1.7226467474706908e-9 per emitted photon이다. r8에서 감소하지만 r16에서 다시 증가한다. 단조 및 연속 스펙트럼 수렴, 새 격자 온도 이력은 여전히 HOLD다.

8개 source 모멘트 일치는 비선형 미래 exp[-u lambda(E)] 적분의 일치를 보장하지 않는다. 국소 N/U와 지지집합을 공유하는 양의 분포의 width-squared Taylor bound를 전역 per-band moment fit의 인증으로 바꾸지 않는다.

## 다음 실행 및 파일

실제 코드 수정은 `2672002d4340a2bf6ac346bf5c39731463b5508a`, 테스트 포함 source revision은 `2e824c21d41c68f728f9630f2b219fa11f0c3b53`이다. 재현/실행은 `CODEX_HANDOFF_PROMPT_KO.md`와 기존 `ncp/BOOTSTRAP.sh`를 따른다. 원본 Rust `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`를 별도 clone에서 컴파일한다. 새 work root에서 pilot 후 같은 table512로 한정된6개 study만 실행한다. source table 또는 source가 바뀌면 기존 pilot 승인은 재사용하지 않는다.

단계0/1/2의 이전 백업 영수증은 보존한다. 이 복구 단계의 실제 게시·백업 결과는 별도 `results/resume/DELIVERY.json` 및 PR76 대화 영수증으로 기록한다. Dropbox URL raw download는 이번에도 도구 URL 경계에서 막혔으며 이를 원격 전체 SHA readback 성공으로 부르지 않는다. 독립 심사 도구가 없어 self-review만 수행했고 native_subagent NOT_RUN이다.
