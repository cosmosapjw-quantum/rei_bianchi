# PHYS36 다음 물리 연구 루프 인계

## 현재 닫힘을 먼저 읽는다

현재 후보는 REI-PHYS35-20261012 / JOINT_BRANCH_PROFILE_DISPLACEMENT_COMPARISON이다.
실제 최종 채택은 state/FINAL_STATE.md, state/CLOSEOUT.json, independent/DECISION_REVIEW.json을 읽는다.
이 인계는 독립 결정 전 고정한 자료다. 원격 반영 사실은 실제 publication/PUBLICATION_RECEIPT.json에서 확인한다.

PHYS35 첫 실행 및 별도 archive 복원 replay는 각각39/39 PASS_SCOPED다.
raw는 각각87,023 bytes, SHA256 2157dfcf9608590b6f0f2b94be3e6558b9414048117aff9a48ab6e083ad233c2이며 byte-identical이다.
first1/replay1은 SPENT, 남은 과학 main0. 이전 PHYS33/34와 다른 lane ledger는 유지한다.

## 새로 얻은 과학적 연결

원 A+=−2.2748589E−137, A−=−3.2582515E−137 s⁻⁴를 그대로 둔

\[
G_\alpha=W_{-,\alpha}(A_-)-W_{+,\alpha}(A_+)
\]

에 대해, 고정 source-real kernel과 기존 두 tube 및 \(0<\delta\le.001\) eV 전체에서

\[
1.31209\times10^{-4}\delta^4
\le G_p-G_u\le7.87027\times10^{-4}\delta^4
\]

를 얻었다. 계수는 eV⁻²이고, 최대폭에서 변화는 \([1.31209,7.87027]E-16\) eV² 안에 있다. \(\delta=0\)에서는 정확히0이다.
짧은 숫자는 raw 정확 유리수 끝점을 바깥쪽으로 표시한 것이며, 짧은 두 분지 표시값을 재조합하여 더 강한 경계를 주장하지 않는다.

새 개선은 \(\mathcal S\)에 패킷별 기존 k4 cell을 사용하고, 실제 기울기에

\[
|C-C^{ref}|\le M_3(d/6+H_c/3)+\mu_2M_4d^2/4
\]

를 사용한 것이다. 새 커널/Bernstein/초월함수/jet/root/quadrature0으로 exact rational 비교를 마쳤다.
같은 개별 부호나 같은 helper 검사를 다시 하는 것이 다음 연구는 아니다.

## 다음 최소 질문의 제안

식별자: **STRUCTURAL_STABILITY_OF_JOINT_PROFILE_ORDER**.
상태: **PROPOSED_NOT_RUN**, 수치 섭동·오차율·새 입력·커널 평가0.

현재 핵심 미해결은 원 \(J_x,J_w\) 입력에 대한 불확실성이다. 먼저 원 고정 원자식에서

\[
k(E;J_x,J_w)=J_x\,K_x(E)+J_w\,K_w(E)
\]

라는 정확한 선형성을 이용하여, **기존 두 수준을 고정한 상태에서 상대 근 순서가 유지되기 위한 조건부 섭동 정리**를 유도하는 것이 다음 유용한 단위다.
이 작업은 실제 물리 오차율을 임의로 정하거나 atomic-fit refinement를 시작하라는 승인으로 해석하지 않는다.

필요한 의무는 연결해서 다룬다.

1. \(\Delta J_x,\Delta J_w\)의 단위와 허용 영역을 상징적으로 정의한다. 실제 검증된 upstream 오차 범위가 존재하면 그 원본을 먼저 찾는다. 자료 없이1% 같은 수치를 물리적으로 승인된 오차로 채택하지 않는다.
2. 같은 \(A_-,A_+\)를 유지할 때 근 존재 및 tube 유지가 섭동 아래에도 성립할 충분조건을 먼저 도출한다. PHYS33/34의 baseline 근 존재가 자동으로 섭동 근 존재로 바뀌지 않는다.
3. 기울기 양성, Peano numerator 양성, 두 비율의 strict separation에 필요한 오차 margin을 같은 섭동 변수로 표현한다.
4. 새 component-kernel 구간 계산이 필요하다면 과학 main 전에 source/code/input, component convention, 정확 파라미터 영역, 작은 workload와 별도 예산을 고정한다. 현재 소진한 예산으로 미리 coefficient preview를 하지 않는다.
5. 실제 오차 범위가 없더라도 도출한 admissible set의 의미를 정확히 남긴다. 그것은 수학적 허용 조건이며 실제 \(J\) 오차가 그 안에 들어간다는 물리 판단은 HOLD다.

만약 원래 목표가 공통 하나의 \(A\)에서 두 분지를 비교하는 것이라면 이 섭동 문제와 별도 질문이다. 현재 두 다른 수준의 결과를 공통수준 정리라고 바꾸어 부르지 않는다. 새 공통 A를 실제로 채택하기 전에 그 대상과 근 존재 의무를 새 계약에 명시한다.

## 재사용할 증거와 금지된 추론

report/PHYS35_REPORT_KO.md, contributions/theory/JOINT_BRANCH_RATIO_DERIVATION_KO.md,
evidence/CERTIFICATE_FIRST.json, evidence/CLAIM_LEDGER.json, PHYSICS_CONTRACT.json,
EXECUTION_PROTOCOL.json과 inputs/PHYS33·PHYS34의 최종 증거를 읽는다.
새 상대 bound에 필요한 기존 exact grid와 retained point identity는 모두 보존했다.
Cref의 k와 kprime은 동일 retained energy에서 읽어야 하며 exact reconstructed root center와 혼용하지 않는다.

새 exact-rational 비교는 conditional fixed-source theorem이다. 반복실행 byte identity는 다른 backend oracle을 뜻하지 않는다.
J와 원자 fit 불확실성 또는 coupled history가 닫힌 것으로 해석하지 않는다.
후속 최종 승격은 해당 후보와 검증 설계에 참여하지 않은 실제 별도 reviewer가 해야 한다.

보호 상태:
**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0.**

현재 PHYS36 실행은0이며 위 제안 자체로 source/default, atomic scope, 허용오차, 공통 A, 전체역사 실행, NCP 또는 다른 lane을 변경하지 않았다.
