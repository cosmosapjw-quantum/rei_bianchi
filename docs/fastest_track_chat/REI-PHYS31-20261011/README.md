# REI-PHYS31-20261011

## 결과

같은 이차 모멘트의 고정 대칭 프로파일은 C3 커널에서 문턱의 삼차 전개까지 일치한다. C4에서는 첫 허용 차이가

\[
\Delta W=-\frac{\Delta\mu_4\,[p k^{(4)}(e)+q k^{(4)}(x)]}{24F_W}\delta^4+o(\delta^4)
\]

다. 현재 고정 source-real 커널은 해당 구간에서 해석적이며, 선택한 양의 다항식 밀도에서 균일 밀도를 뺀 저장점 계수는 상단 −0.00110495859229183348 eV⁻², 하단 −0.000619616589313442784 eV⁻²로 계산됐다. 같은 비영 A 수준을 보존했다. 유한 폭의 오차 상계와 정확 영점/J의 enclosure는 미해결이다.

## 읽는 순서

1. [한국어 보고서와 전체 증명](report/PHYS31_REPORT_KO.md)
2. [독립 최종 판정](independent/DECISION_REVIEW_KO.md) · [기계 판독 판정](independent/DECISION_REVIEW.json)
3. [실제 숫자 요약](report/PHYS31_RESULTS_SUMMARY.json) · [전체 원자료](contributions/numerics/QUARTIC_PROFILE_FIRST.json)
4. [물리 계약](PHYSICS_CONTRACT.json) · [고정 프로토콜](contributions/numerics/PROTOCOL.json) · [주장 목록](evidence/CLAIM_LEDGER.json)
5. [재현 기록](portability/REPLAY_RECEIPT.json) · [다음 PHYS32 인수문](next/PHYS32_NEXT_HANDOFF_KO.md)

최종 판정의 권위는 실제 reviewer 기록에 있다. 후보 파일의 과거 “판정 대기” 문구는 당시 역할·시점을 기록한 것이며 최종 판정 이후에도 원문을 보존한다. 게시 commit과 PR 상태는 별도 publication receipt에 기록한다.

## 실제 실행 범위

고정된 새 프로그램 첫 실행 1회와 ZIP을 다른 경로에 복원한 재현 1회를 완료했다. 각 실행에서 같은 79개 검사를 수행해 모두 통과했고, 원자료 69,411바이트가 완전히 일치했다. 두 표현에서 얻은 최대 정규화 차이는 4.6819296×10⁻⁷⁴, 고정 허용치는 10⁻⁶⁰이다. 두 실행의 총 물리 k⁽⁴⁾ 호출은 16회이며 전역 고유 보존 노드는 4개다. 새 에너지 노드·물리 근·하위 도함수 출력·과거 main/import/suite는 0이다.

재현 runtime ZIP은 `portability/PHYS31_RUNTIME.zip`이며 실제 복원·실행 명령, 입력 identity와 mode, 원 결과 및 비교 결과는 해당 디렉터리와 `execution/`에 있다. 이번 PHYS31 실행 예산은 모두 사용했다. 새 과학 실행은 다음 요청의 별도 계약에 속한다. 결과 조립과 그림 생성 코드는 저장 숫자·기호 정의의 표시용이며 추가 물리 평가를 수행하지 않는다.

같은 호스트·Python·입력 계보를 사용했으므로 독립 물리 데이터 credit은 0이다. 정확한 다항식 toy와 두 도함수 표현의 일치는 물리 데이터 또는 원자 fit의 오차 인증을 대신하지 않는다.

## 유지 상태

Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED. Production source/default/runtime 변경 0. PHYS32는 정량 나머지와 근의 조건을 연결하는 후속 제안이며 `PROPOSED_NOT_RUN`이다.
