# PHYS35 다음 물리 연구 루프 인계

## 먼저 확인할 닫힘 상태

현재 작업은 `REI-PHYS34-20261012`다. 최종 채택 여부는 `state/FINAL_STATE.md`, `state/CLOSEOUT.json`, `independent/DECISION_REVIEW.json`을 함께 읽는다. 이 인계 및 과학 본문은 독립 판정 전에 고정한 후보 자료다. 과거 snapshot을 최종 판정으로 대체하지 않는다. 실제 원격 반영은 최종 전달 archive의 `publication/PUBLICATION_RECEIPT.json`에 별도 기록한다.

PHYS34가 실제로 수행한 새 main은 첫 실행1회와 복원 경로 재실행1회다. 모두25/25 PASS_SCOPED이고 raw는 각각1,028,560 byte, SHA256 `9b576de7e6079b5a9a3352f6049f550fde13646dda8a1d36022febcf6e11ccf4`다. stdout/stderr, parent-observed returncode, 실제 exec tool envelope를 함께 보존했다. 이 두 슬롯은 **SPENT**이며 재실행·초기화하지 않는다. PHYS33 및 다른 lane의 기존 ledger도 그대로 소진 상태다.

## 확보한 두 개의 개별 분지 결과

| 항목 | 상단 PHYS33 | 하단 PHYS34 |
|---|---|---|
| 정확한 A, s⁻⁴ | −2.2748589E−137 | −3.2582515E−137 |
| 폭 | 0≤δ≤0.001 eV | 0≤δ≤0.001 eV |
| 근 tube | 각 저장 중심±0.25 eV² | 각 저장 중심±0.25 eV² |
| 같은 분지의 P4와 uniform | 양의 폭에서 Wp<Wu | 양의 폭에서 Wp<Wu |
| 의미 | 고정 source-real 상단 국소 근 정리 | 고정 source-real 하단 국소 근 정리 |

두 분지는 같은 source-real convention, 같은 실제 W, 같은 프로파일과 폭을 사용한다. 그러나 저장 A는 서로 다르다. A−와 A+를 바꿔 끼워 같은 수준의 cross-branch theorem이 이미 증명된 것처럼 쓰지 않는다. PHYS34의 `claim_ceiling.lower_branch=TARGET_NOT_YET_EVALUATED`는 사전 계약 snapshot이며, 실제 인증 결과와 최종 결정은 별도 상위 상태에서 읽는다.

## 다음 최소 연구 단위의 제안

제안 이름: `JOINT_BRANCH_PROFILE_DISPLACEMENT_COMPARISON`.

목표는 개별 근 이동의 부호를 반복해서 확인하는 것이 아니라, 두 분지의 프로파일 이동 **차이**를 직접 비교할 수 있는 정리를 세우고 필요한 최소 계수 경계를 인증하는 것이다. 두 음수의 차이는 자동으로 부호가 정해지지 않는다. PHYS33/34의 개별 거친 계수 범위만으로 gap 부호를 이미 닫았다고 주장하지 않는다.

시작할 때 비교 대상을 먼저 고정한다.

\[
G_\alpha(\delta;A_-,A_+)
=W_{-,\alpha}(\delta;A_-)-W_{+,\alpha}(\delta;A_+),
\]
\[
G_p-G_u=\Delta W_- -\Delta W_+.
\]

이 정의는 현재 두 고정 수준을 보존한 **root separation**이다. 사용자가 의도한 물리량이 두 분지에 공통인 하나의 A를 요구한다면, 위 정의로 대체하지 말고 그 목표와 새 근 존재 의무부터 구별해야 한다. 어떤 정의를 채택하든 새 계약에 두 level convention을 명시하고 실행 전에 고정한다. 현재 인계는 새 공통 A를 정하거나 그 근을 계산하지 않았다.

가능한 다음 수학적 경로는 각 분지의 정확한

\[
\Delta W_s=-\frac{\delta^4}{945}
\frac{\mathcal S_s(\delta,W_{s,u})}{\overline C_{s,p}}
\]

를 함께 사용하여, 두 비율의 **차이** 또는 그 순서에 대한 공통 경계를 얻는 것이다. 분지별 상한·하한이 겹친다는 이유로 무작정 정밀도나 cell 수를 늘리지 않는다. 먼저 packet geometry, 실제 근 tube, 이동에 따른 계수 변화의 공통 의존성을 정리하고 어떤 불확실성이 부호를 가리는지 파악한다. 이 식의 새 비교 정리·계수 평가·부호 판정은 모두 **NOT_RUN / NOT_CERTIFIED**다.

실행 순서는 다음과 같다.

1. 최신 branch/PR 원본과 현재 최종 닫힘을 확인한다. 기억의 작업 번호보다 원격 source와 저장 final decision을 우선한다.
2. PHYS33/34의 정확 A 키, 전체 저장 W, 원 J·binary64 literal 해석, cutoff, c, actual W를 그대로 읽고 새 비교 대상의 정의를 고정한다.
3. 기존 exact Peano·기울기·근 존재 정리를 재사용하고, 새 gap 의무에 필요한 비교 정리를 먼저 유도한다. 변하지 않은 helper의 기초검사나 과거 main을 다시 돌리지 않는다.
4. 새 물리 평가가 필요하다면 그 전에 범위·정밀도·분할·source/code identity·작은 작업량 cap·종료조건을 새 계약에 명시한다. PHYS34의 소진 슬롯은 사용하지 않는다. 인계 자체는 새 과학 main을 시작한 기록이 아니다.
5. 경계가 겹치거나 부호 판정이 실패하면 원 실패를 보존한다. A·domain·정밀도·예산을 묵시적으로 바꾸지 않는다.
6. 후보 생성·검증 설계에 참여하지 않은 실제 별도 reviewer가 완성된 후보와 증거를 읽고 최종 판정한다. 기존의 통과를 새 gap의 독립 검증으로 재표기하지 않는다.

## 보호 상태와 읽을 자료

`Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`.

J 및 원자 fit 불확실성·coupled history는 미해결이다. gap 비교가 성공하더라도 물리 승인이 자동으로 따라오지 않는다. 새 native·gas IVP·NCP·과거 main/suite·PR 본문 수정·merge·외부 메시지는 이 인계의 범위가 아니다.

우선 읽을 자료는 `report/PHYS34_REPORT_KO.md`, `report/ROOT_TUBE_PROOF_KO.md`, `contributions/theory/LOWER_BRANCH_DERIVATION_KO.md`, `evidence/CLAIM_LEDGER.json`, `evidence/CERTIFICATE_FIRST.json`, `PHYSICS_CONTRACT.json`, `EXECUTION_PROTOCOL.json`, `SOURCE_MANIFEST.json`이며, 상단 결과는 `inputs/PHYS33/`에 보존했다.

이 인계 작성 시 PHYS35의 커널·근·계수 비교·과학 main·원격 실행은 **0회**다.
