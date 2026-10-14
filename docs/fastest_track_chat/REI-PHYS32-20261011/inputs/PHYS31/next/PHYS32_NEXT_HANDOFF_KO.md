# PHYS32 인수문 — 사차 프로파일 차이를 유한 폭의 정량적 조건으로 옮기기

**제안 식별자:** `QUARTIC_SPLITTING_REMAINDER_AND_CONDITIONING`  
**상태:** `PROPOSED_NOT_RUN`  
**직전 완료 연구:** `REI-PHYS31-20261011`

이 문서는 다음 사용자의 물리 연구 루프 요청을 위한 문제와 경계를 기록한다. PHYS32의 정리·수치 실행·유효 폭 인증을 수행했다는 기록이 아니다. PHYS31의 실제 최종 판단은 [판정서](../independent/DECISION_REVIEW_KO.md)와 [판정 JSON](../independent/DECISION_REVIEW.json)에 있으며, 이 인수문 자체가 승격이나 실행 권한을 만들지는 않는다.

## 1. 이어받을 과학적 결과

고정된 대칭 확률 프로파일 \(\nu,\widetilde\nu\)가 \([-1,1]\)에서 같은 이차 모멘트 \(\mu_2\)를 가지면, 실제 분산 \(W\)와 물리 폭 \(\delta\ge0\)를 사용하는 두 중심 혼합족의 기하가 정확히 공통이다. 중심분산은 \(V=W-\mu_2\delta^2\), 공통 중심 구간은 \([a+\delta,b-\delta]\)다. \(a=13.61,b=24.58,m=18\) eV, \(L=4.39,H=6.58\) eV를 보존한다.

단순한 내부 기준근과 같은 수준 \(A_j\)에 대해 PHYS31이 직접 증명한 것은 다음이다.

\[
k\in C^3:\qquad W_{j,\nu}-W_{j,\widetilde\nu}=o(\delta^3),
\]
\[
k\in C^4:\qquad W_{j,\nu}-W_{j,\widetilde\nu}
=D_{4,j}\delta^4+o(\delta^4),\qquad
D_{4,j}=-\frac{\Delta\mu_4\mathcal H_{4,j}}{24C_j},
\]
\[
\mathcal H_{4,j}=p_jk^{(4)}(e_j)+q_jk^{(4)}(x_j),\qquad
C_j=F_{j,W}(0,w_j)>0.
\]

양의 절대연속 프로파일 쌍은

\[
h_u=\frac12,\qquad h_p=\frac{35z^4-30z^2+11}{16},\qquad
\mu_{2,u}=\mu_{2,p}=\frac13,\quad \Delta\mu_4=\frac8{315}
\]

이며 \(D_{4,j}^{p-u}=-\mathcal H_{4,j}/(945C_j)\)다. 저장된 같은 분지 수준의 유한 산술 결과는 다음과 같다.

| 분지 | 보존 수준 \(A_j\), s⁻⁴ | \(D_{4,j}^{p-u}\), eV⁻², 표시값 |
|---|---:|---:|
| 상단 \(*\) | \(-2.2748589\times10^{-137}\) | \(-0.00110495859229183348\) |
| 하단 \(0\) | \(-3.2582515\times10^{-137}\) | \(-0.000619616589313442784\) |

두 계수의 하단−상단 차이는 \(+0.000485342002978390693\) eV⁻²다. 이 숫자는 저장 입력의 국소 계수이며 양의 유한 폭에서의 문턱·간격 부호를 인증하지 않는다. 정확 영점 또는 실제 물리 커널의 오차 enclosure도 아니다.

C3만으로는 사차 잔차가 보장되지 않는다. PHYS31은 같은 양의 밀도 쌍에 대해 임의의 \(3<p<4\)에서 첫 차이가 \(\delta^p\)인 허용 커널을 구성했다. 사차가 소거되면 다음 차수가 반드시 6인 것도 아니다. 매끄러운 허용 커널에서 움직이는 기하 때문에 비영 \(\delta^5\) 차이가 생기는 예가 있다. 다음 루프를 단순히 “대칭이므로 6차 계산”으로 바꾸지 않는다.

## 2. 다음 한 질문

**사차 계수와 양의 근 기울기가 주어졌을 때, 두 프로파일의 문턱 차이에 정량적인 나머지 상계를 주기 위해 정확히 무엇이 더 필요한가?**

목표는 예를 들어

\[
\left|W_{j,p}(\delta)-W_{j,u}(\delta)-D_{4,j}^{p-u}\delta^4\right|
\le \delta^4\,\mathcal R_j(\delta)
\]

형태의 명시적 조건부 상계를 유도하고, \(\mathcal R_j\)가 의존하는 양과 단위를 분리하는 것이다. 이 식과 충분조건은 다음 루프의 목표이지 현재 증명 완료 항목이 아니다. 처음부터 숫자가 붙은 유효 폭을 약속하지 않는다.

필요한 분석 대상은 \(k^{(4)}\)의 연속성 모듈러스 또는 더 높은 도함수 상계, 끝점·내부 중심·확률의 이동, 두 근의 기준점 이탈, 양의 \(F_W\) 하한이다. 응답 차이의 Taylor 나머지만 작다는 사실로 근 차이의 수치 나머지가 완성됐다고 하지 않는다. 같은 \(\mu_2\)에서 공통 기하가 정확히 소거하는 항을 먼저 이용한다.

기준근·분모의 조건도 상계의 일부다. 같은 비영 \(A_j\) 수준을 유지하고

\[
G_j=N_j-A_jQ_j,\qquad (G_j)_W=N_{j,W}-A_j=Q_jC_j
\]

를 보존한다. \(A_j\)가 작다는 이유로 0으로 바꾸지 않는다. 물리 편미분에서 \(W\)와 중심분산 \(V\)를 바꾸어 고정하지 않는다.

## 3. 이론과 숫자 사이에 남은 간극

현재 고정 Rust 식을 source binary64 상수의 정확 실수 해석으로 읽고 직렬화된 J를 고정하면, 선택 구간은 같은 양의 해석적 fit 분기에 들어간다. 따라서 고차 정칙성은 있다. 그러나 해석성만으로 수치적인 도함수 상계나 유효 폭이 제공되지는 않는다.

PHYS31의 두 수치 표현은 같은 fit·상수·J·하위 cache·Decimal scalar 함수를 공유한다. 표현 간 일치는 원 J 오차, 원자 fit 정확도, 저장근의 정확 영점과의 거리, 반올림된 내부 노드와 이상적 기하의 차이를 enclosure하지 않는다. 이 미해결 항목들을 상수 0으로 두거나 재현 일치로 대신하지 않는다.

다음 루프는 우선 명시적인 가정 아래의 정량 정리를 완성할 수 있다. 고정 실수 모델의 수치적 부호·유효 폭까지 주장하려면 기준근, 기울기, 사차 계수, 관련 도함수·기하 상계에 필요한 별도 오차 근거가 있어야 한다. 그러한 근거가 예산 안에서 확보되지 않으면 조건부 이론과 미평가 상수를 분명하게 구분하여 닫는다. 실제 기체 이력이나 관측 물리 정확도에 대한 승격은 다른 문제다.

## 4. 가장 먼저 읽을 실제 자료

| 파일 | 사용하는 내용 |
|---|---|
| [PHYS31 보고서](../report/PHYS31_REPORT_KO.md) | 결과·한계·전체 증명 두 부록 |
| [전체 이론 유도](../contributions/theory/DERIVATION_KO.md) | 균일 Peano 나머지, 한쪽 근 정칙성, 가중 기하, C3 및 5차 반례 |
| [커널 정칙성](../contributions/kernel_scope/KERNEL_REGULARITY_AND_PROFILES_KO.md) | 현재 분석 구간과 원 식의 정칙성, 정확 프로파일 쌍 |
| [두 도함수 표현](../contributions/kernel_scope/INPUT_KEYS_AND_TWO_EXPRESSIONS_KO.md) | 원 입력 key·단위·독립 조립식 및 공유 의존성 |
| [실제 원자료](../contributions/numerics/QUARTIC_PROFILE_FIRST.json) | 새 네 노드 \(k^{(4)}\), 두 분지 계수, 79개 검사와 실제 횟수 |
| [실행 계약](../PHYSICS_CONTRACT.json) · [프로토콜](../contributions/numerics/PROTOCOL.json) | PHYS31에만 적용된 범위·정밀도·허용치·회계 |
| [실제 재현 receipt](../portability/REPLAY_RECEIPT.json) | 첫 실행 1회+복원 재현 1회, raw 바이트 동일성 |
| [주장 목록](../evidence/CLAIM_LEDGER.json) · [최종 판정](../independent/DECISION_REVIEW.json) | 개별 주장 근거와 승격/보류의 실제 범위 |
| [고정 소스](../SOURCE_MANIFEST.json) | 현재 source identity와 보호 범위 |

원자료 SHA256은 `843335dd8754bfaf57d201d9db888e80a7713d95a8147de08ffdb97db609e66a`다. PHYS31 source 검증 기준 commit은 `5ac0bceaac2629682f777bc8223fbba07be810b9`, tree는 `22216f47b19bdb481e8cc16722222272d64edf34`다. 실제 문서 게시 commit은 별도 publication receipt에서 읽고 다음 턴의 최신 head와 대조한다. 이전 head 문자열을 최신이라고 가정하지 않는다.

## 5. 다음 실행의 경계와 판정

우선 현재 채택 모델의 연구 하네스, 실제 최신 소스와 선행 판단을 읽고 PHYS32의 별도 계약을 만든다. 이번 PHYS31은 main 2회, 물리 \(k^{(4)}\) 평가 16회, 전역 고유 보존 노드 4개로 예산을 모두 사용했다. PHYS31 프로그램을 다시 실행하거나 그 예산을 다음 작업에 재사용하지 않는다.

처음에는 상징적 부등식과 이미 보존된 근거로 진행한다. 새로운 수치 상계가 꼭 필요하면 계산하기 전에 대상·구간·도함수 차수·표현·오차 근거·평가 횟수·중단 조건을 새 계약에 고정한다. PHYS31의 점별 사차 cache를 구간 상계로 취급하지 않는다. 단순 precision 증대나 조밀한 표본을 엄밀한 enclosure로 이름만 바꾸지 않는다. 가벼운 연구·코딩 권한 안에서 해결할 수 있는 부분은 먼저 완성한다.

새 실행 코드가 필요한 경우 최소 first 1회와 별도 경로 replay 1회를 사전에 고정한다. 실패 원문과 수정은 보존하고 결과를 본 뒤 허용치를 완화하지 않는다. 최종 판정자는 후보 생성·검증 설계와 분리하며 실제 주장·증명·코드·원자료를 읽는다. 동일 호스트·모델·입력 계보의 재현이나 검토를 독립 물리 실험으로 세지 않는다.

## 6. 유지 상태와 지속되는 게시 범위

**Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0.**

별도 atomic/HH/RCT/CR lane, local Codex, heavy native 실행을 켜지 않는다. 이번 국소 문턱 결과를 재이온화 이력의 admission으로 확장하지 않는다.

사용자의 연속적인 다음 물리 연구 루프 요청과 실제 이전 인수문이 지원하는 이 대화의 가벼운 연구·코딩·검토 및 같은 branch의 additive docs 범위를 이어받는다. 이 문구 자체가 새로운 권한을 만들지는 않는다. Repo `cosmosapjw-quantum/rei_bianchi`, branch `forward/rust-reion-kernels-20260922`, PR `83`을 사용한다.

다음 연구를 실제 완료하고 별도 판정을 받은 경우 새로운 `docs/fastest_track_chat/REI-PHYS32-<실행일>/` 아래에만 추가한다. 실제 최신 head에 대한 expected-head nonforce CAS, 기존 모든 경로와 과학 source subtree 보존, 새 문서 raw readback, PR body·draft·미병합 상태 확인을 유지한다. source/default/runtime, PR body, merge, 타인에게 보내는 메시지의 변경·실행 권한은 추가하지 않는다. 이미 승인된 가역 연구·검토·문서 추가 게시를 위해 같은 허락을 다시 묻지 않는다.
