# PHYS34 다음 물리 연구 루프 인계

## 정지점과 권위

현재 작업은 `REI-PHYS33-20261012`이다. 최종 완료 여부와 채택 범위는 `../state/FINAL_STATE.md`, `../state/CLOSEOUT.json`, `../independent/DECISION_REVIEW.json`을 함께 읽어 확인한다. 최종 판정 이전의 `RESEARCH_STATE.md`를 완료 판정으로 대체해서 읽지 않는다. 원격 identity는 `../publication/PUBLICATION_RECEIPT.json`의 실제 확인 기록을 따른다.

PHYS33의 고정 계약은 상단 분지 하나, 0≤δ≤0.001 eV, 정확한 A=−2.2748589×10⁻¹³⁷ s⁻⁴, 실제 분산 W, 저장 중심 ŵ의 ±0.25 eV² tube다. 새 수치 main 1회와 복원 replay 1회가 모두 29/29 PASS_SCOPED이고 raw SHA256이 같다. 이 두 슬롯은 **SPENT**다. PHYS29–PHYS32, ACCEL02/C13/PILOT02/COMMON18 등 다른 lane의 실행 예산도 되살리지 않는다.

## 다음 최소 연구 단위

제안 이름: `LOWER_BRANCH_PINNED_KERNEL_PACKET_AND_ROOT_TUBE_ENCLOSURE`.

목적은 동일한 source-real 커널의 **하단 분지 하나**에서 패킷 지지, 전체 기울기 경로, k″와 k⁽⁴⁾의 필요 경계, 정확한 공통 높이의 근 존재·tube 안 유일성·프로파일 순서를 별도로 인증하는 것이다. 이는 아직 **NOT_RUN / NOT_CERTIFIED**다. PHYS33의 상단 결과로 하단 결과를 대입하지 않는다.

다음 순서로 시작한다.

1. 최신 branch/PR 원본과 마지막 완료 상태를 다시 확인한다. source 변경이 있었다면 PHYS33 identity와 나란히 기록한다. 기억 요약의 작업 번호를 원본보다 우선하지 않는다.
2. PHYS29 보존 JSON에서 하단 분지의 정확한 A 키·저장 중심 문자열과 PHYS31/32의 하단 패킷 기하를 읽는다. PHYS33의 상단 A를 그대로 복사하지 않는다. source cutoff·에너지 오프셋·c·J source-real convention은 원본과 대조한다.
3. 실제 W와 V=W−δ²/3을 유지하고, 한정된 δ 구간과 근 tube, 에너지 containing interval을 **새 실행 전에** 정한다. 원래 지지 [13.61,24.58]과 piecewise atomic cutoff를 넘는지 먼저 대수로 확인한다.
4. PHYS33의 exact Fraction 미분/Bernstein 구현과 증명을 재사용할 수 있으나, 하단 영역에서의 부호와 충분조건은 아직 평가되지 않았다. 예산·정밀도·분할·stop condition·input/code hash를 새 계약으로 동결한 뒤에만 그 새 작업의 bounded main을 수행한다. 기존 PHYS33 main의 예산을 수정하거나 ledger를 지우지 않는다.
5. 조건이 실패하면 실패한 셀·기울기·tube 부등식을 그대로 남기고 HOLD한다. 같은 실패를 감추는 domain 축소·level 변경·정밀도 변경·추가 root scan을 해서는 안 된다. 다른 계약이 필요하면 새 의무와 미실행 상태를 명시한다.
6. 후보 생성·검증 설계에 참여하지 않은 별도 reviewer가 actual evidence와 최종 후보 freeze를 읽고 final decision을 내리게 한다.

두 분지의 이동 부호를 각각 얻더라도 두 분지 사이 gap 이동의 부호는 자동으로 결정되지 않는다. gap을 주장하려면 두 이동의 차이를 같은 convention과 폭에서 엄밀히 비교하는 별도 경계가 필요하다. 현재는 그 계산·검증을 하지 않았다.

## 보호 상태와 실행 경계

`Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`.

고정 J/원자 fit의 물리적 불확실성은 미해결이다. 근의 매우 작은 수학적 잔차가 물리 정밀도 인증으로 승격되지 않는다. 새 native·gas IVP·NCP·과거 main/suite 실행은 이 인계만으로 시작하지 않는다. 필요한 새 연구 계약과 해당 작업의 권위를 먼저 확인한다.

새 결과의 원격 반영은 그 시점의 사용자 권위와 하네스 정책에 따른다. PHYS33 자체의 반영 범위는 기존 branch의 새 문서 prefix, nonforce expected-head CAS, 기존 경로·scientific source·PR 본문·draft·unmerged 유지다. 이 인계는 merge, PR 본문 변경, 외부 메시지 발송을 지시하지 않는다.

## 이어서 읽을 파일

- `report/PHYS33_REPORT_KO.md`: 결과와 의미
- `report/ROOT_TUBE_PROOF_KO.md`: 전체 근 존재·순서 증명
- `contributions/theory/DERIVATION_KO.md`: exact 다항식과 Bernstein 유도
- `PHYSICS_CONTRACT.json`, `EXECUTION_PROTOCOL.json`, `evidence/PREEXECUTION_FREEZE.json`: 실행 전 동결
- `evidence/CERTIFICATE_FIRST.json`, `evidence/CERTIFICATE_REPLAY.json`, `evidence/EXECUTION_RECEIPT.json`: 실제 결과와 사용한 예산
- `SOURCE_MANIFEST.json`, `inputs/PHYS32/`: 상속 원본 identity와 수학적 조건
- `independent/DECISION_REVIEW.json`, `state/FINAL_STATE.md`, `state/CLOSEOUT.json`: 최종 독립 판정과 handoff 권위

이 인계 작성 시 PHYS34의 과학 계산·원격 실행은 0회다.
