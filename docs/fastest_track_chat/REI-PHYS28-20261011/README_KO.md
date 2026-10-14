# REI PHYS28 — 작은 대역폭의 분산 문턱 민감도

평균18 eV, 광자 지원[13.61,24.58] eV, 고정 실제 분산 W에서 균일 대역 반폭 δ의 일차 문턱 이동을 구했다. 고정 source-real 상수와 직렬화 J 아래 c*>0,c0<0이며 수치 근사는 **5.71638089140 eV**, **−2.37494837006 eV**다. 일차항은 지원·중심·확률 이동에서 생기고 대칭 대역 평균화와 V=W−δ²/3 보정의 일차 기여는0이다.

시작은 [한국어 보고서](report/PHYS28_REPORT_KO.md), 상세 수식은 [유도문](contributions/theory/DERIVATION_KO.md), 정확 근거는 [첫 수치 원자료](contributions/numerics/SMALL_WIDTH_FIRST.json), [독립 판정](independent/DECISION_REVIEW_KO.md), [재현 기록](portability/REPLAY_RECEIPT.json)이다. 최종 판정 권위는 `independent/DECISION_REVIEW.json`이고 **Physical HOLD**를 유지한다.

첫 과학 main1회120/120 PASS, 별도 새 경로 replay1회 byte동일. 전체joint(k,k′)16회, 새 영점·old PHYS19–27 main/suite/root·native·gas IVP 모두0이다. 표시용 새 커널도0회다. 과학 실행 전 수식 구분자 수정의 최초 동결본, 도구 assertion과 그림 배치 수정의 원본을 보존했다.

재현은 [사용법](portability/USAGE_KO.md)을 따른다. 기본 확인은 `--verify-only`이고 `--replay`는 새 PHYS28 프로그램을 실제 실행한다. 원 자료와 현재 결과는 덮어쓰지 않는다. `inputs/`에는 이번 연구에서 선택한 선행 입력30개를 보존했으며, 이것이 PHYS19–27 전체 기록을 모두 복제한 묶음이라는 뜻은 아니다. PHYS27 원 아카이브의 identity와 현재 복구 대조는 `evidence/RECOVERY_INVENTORY.json`에 있다.

최종 산출물 ZIP 검증·Git 게시·파일 전달은 묶음과 분리된 **PHYS28_PUBLICATION_RECEIPT.json**을 따른다. 이 README는 후속 게시가 이미 이루어졌다고 선제 주장하지 않는다. 다음은 [PHYS29 이차항 분해](next/PHYS29_NEXT_HANDOFF_KO.md), **PROPOSED / NOT_RUN**이다.

[160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED, production source/default/runtime 변경0을 유지한다. 초기 ε²t⁴ 계수의 국소 구조이며 root/계수 interval enclosure, 정량 고차 나머지, J·원자·기체 불확실성, 실제 emitter·우주론 history 또는 novelty 승격은 아니다.
