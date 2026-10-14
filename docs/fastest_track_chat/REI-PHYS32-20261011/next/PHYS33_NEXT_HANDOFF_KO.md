# PHYS33 인수문 — 고정 커널의 국소 유한 폭 부호 인증

상태: PROPOSED_NOT_RUN  
직전 실제 완료 연구: REI-PHYS32-20261011  
제안 식별자: PINNED_KERNEL_PACKET_SIGN_AND_ROOT_TUBE_ENCLOSURE

## 1. 이어받는 결과

PHYS32는 같은 \(\mu_2\)·실제 W·동일한 정확 A의 두 근에
\[
|\Delta W-D_4\delta^4|\le\delta^4\mathcal R(\delta)
\]
를 증명했다. \(\mathcal R\)는 프로파일 평균의 Taylor 나머지, 움직이는 끝점·내부 중심·확률,
근 이탈 \(\rho\), 양의 \(F_W\) 하한과 그 변화량을 모두 포함한다.
C5에서 명시한 상수 \(K_R\delta^5\)의 전체구간 충분조건도 있다.
물리 상수들의 숫자는 미평가다.

사용하는 특별한 양의 밀도 쌍에는 더 직접적인 항등식이 있다.
\[
h_u=\tfrac12,\quad h_p=(35z^4-30z^2+11)/16,\quad
d\pi=\tfrac{315}{256}(1-z^2)^4dz,
\]
\[
\Delta f(\delta,y)=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)d\pi(z),\quad
\Delta W=-\frac{\delta^4\mathcal S(\delta,W_u)}{945\overline C}.
\]
따라서 같은 A의 두 근 존재·양의 slope·실제 두 photon packet에서 양의 k4를 인증하면
양의 폭에서 \(W_p<W_u\)가 직접 따른다.
이 순서만을 목표로 삼을 때는 사차 근 나머지의 수치값이 반드시 필요한 것은 아니다.
두 분지의 개별 순서에서 gap 변화의 부호가 나오지는 않는다.

## 2. 다음 한 질문

**고정 직렬화 J와 exact-source-real 상수를 유지한 모델에서,
선택한 프로파일 쌍의 국소 유한 폭 순서에 필요한 최소 부호·근 조건을
실제로 인증할 수 있는가?**

먼저 분석적 부호 분해 또는 엄밀한 구간 상계가 가능한지 살핀다.
범위와 계산 예산을 고정하기 전에 표본 확대·정밀도 증가·근 탐색을 시작하지 않는다.
첫 목표는 상단 또는 하단 한 분지의 명시한 작은 영역처럼 가장 작은 판별 단위로 정할 수 있다.
두 분지·gap·원 물리 입력 가족 전체를 처음부터 자동 묶지 않는다.

## 3. 가장 먼저 보존할 구분

- 목표 A는 각 분지 안의 두 프로파일에서 정확히 동일하고 기존 비영 수준을 유지한다.
  저장 \(\widehat w\)가 exact A의 근이라는 등식은 아직 enclosure되지 않았다.
  A를 \(F(0,\widehat w)\)로 새로 정의하거나 0으로 바꾸지 않는다.
- 항상 \(G_W=QF_W+(F-A)\)이며, \(G_W=QF_W\)는 해당 A의 정확근에서만 성립한다.
- 실제 분산은 W이고 \(V=W-\mu_2\delta^2\)다.
  중심 support \([a+\delta,b-\delta]\)를 바꾸지 않는다.
- k4 부호는 실제 두 photon packet의 합집합에서 충분할 수 있다.
  slope에 쓰는 k2의 영역은 그 둘 사이 선분과 profile shift도 포함해야 한다.
- 고정 실수 모델의 수치 인증과 원 J·원자 fit·기체 이력의 물리 인증을 구별한다.
  원 J·fit 오차를 재현 일치나 높은 정밀도로 0이라고 선언하지 않는다.

## 4. 실제로 읽을 자료

1. [PHYS32 보고서](../report/PHYS32_REPORT_KO.md)와 [최종 판정](../independent/DECISION_REVIEW.json).
2. [일반 정량 증명](../contributions/theory/QUANTITATIVE_REMAINDER_KO.md):
   T32.9의 튜브, B·rho·h·P·S_C와 R, C5 전체구간 상수, off-root 분자식.
3. [양의 적분 표현](../contributions/numerics/POSITIVE_PEANO_AND_TOY_ORACLES_KO.md):
   P32.2, P32.5, P32.7, P32.9.
4. [조건 분석](../contributions/conditioning/PHYSICAL_ENCLOSURE_REQUIREMENTS_KO.md):
   잔차/기울기의 root enclosure, 저장 node/weight/J/evaluation 오차,
   packet 반경과 CS32.29의 k4 하한.
5. [현재 계약](../PHYSICS_CONTRACT.json), [소스 manifest](../SOURCE_MANIFEST.json),
   [입력 시점 기록](../evidence/INTAKE.json), 개별 기여의 실제 읽기·provenance.
6. PHYS31의 고정 kernel_scope 문서와 실제 원자료.
   PHYS31의 point cache는 interval bound가 아니다.

현재 intake commit은 13436210ea925be268b4dc9034baf4a37b6dc091,
src subtree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이다.
PHYS32 실제 게시 commit은 이후 publication receipt에서 읽어야 한다.
다음 요청 때 실제 최신 head를 확인하며 이전 head를 최신이라고 가정하지 않는다.

## 5. 새 계산 전에 고정할 계약

대상 모델·J/source bytes·기준 수준·분지·에너지 및 분산 구간·폭 범위·derivative order·
산술 표현·바깥 반올림 근거·함수 호출 횟수·wall/CPU 한도·실패와 중단 조건을 먼저 고정한다.
초월함수 평가를 쓰면 그 함수도 포함해 enclosure가 보장되는 방법이어야 한다.
기존 근 보정과 새로운 물리 커널 평가는 PHYS32의 예산에 포함되지 않았다.

가능한 연구 경로는 두 가지다.
분석적으로 부호를 분해해 인증하거나,
명시적인 구간 오차 산술로 필요한 작은 영역만 감싼다.
조밀한 점, ordinary high precision 또는 두 표현 일치를 엄밀한 enclosure로 부르지 않는다.
한 방법의 동일 실패를 자료 변화 없이 반복하지 않는다.

인증된 잔차 \(\varepsilon_r\)와 양의 \(\kappa\)가 먼저 확보되면
\(|w-\widehat w|\le\varepsilon_r/\kappa\)를 적용한다.
유한 폭의 root tube는 저장점에서 새로 유효한 \(\widehat B\)와
\(\widehat B+\varepsilon_r<\kappa\eta\)로 제어할 수 있다.
이때 packet 반경에 root 이탈과 저장 node 차이를 함께 넣는다.
어느 상계가 부족하면 conditional theorem과 실제 missing constant를 구별해 남긴다.

새 실행 코드가 필요하면 first 1회와 다른 경로 replay 1회를 새 계약에 포함한다.
새 원자료·실패 원문·실제 명령·누적 예산·독립 판정을 보존한다.
동일 호스트 replay는 독립 물리 증거가 아니다.

## 6. 이미 소진된 PHYS32 실행과 보호 상태

PHYS32 과학 main은 first 1회와 replay 1회로 소진했다.
각각 같은 21개 검사 묶음, toy 근 8개, 정확 이분법 640단계였다.
원자료 31,328 bytes의 SHA256은
852a895d3fa52519717cbaaaee602ced253fb49c4e140ef6b1885dc9edc2d417이다.
새 물리 kernel/derivative/root 평가, 과거 과학 import/main/suite는 0이다.
이 프로그램을 다시 돌리거나 예산을 재사용하지 않는다.

Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL;
HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0.
클라우드의 가벼운 연구·코딩·검증을 수행하며, 별도 heavy/local Codex 작업은 자동 시작하지 않는다.

사용자의 연속적인 다음 물리 연구 루프 요청에서 이어 온 가벼운 연구·검토와
같은 branch의 additive docs 범위를 유지한다.
Repo cosmosapjw-quantum/rei_bianchi,
branch forward/rust-reion-kernels-20260922, PR 83이다.
새 연구가 실제 완료되고 별도 판단을 받은 경우에만 새 PHYS33 문서 prefix를 추가한다.
최신 head의 nonforce expected-head CAS, 기존 모든 경로·source 보존,
선별 raw readback 및 PR body·draft·미병합 상태를 확인한다.
생산 소스·default/runtime·PR body·merge·외부 메시지 권한은 추가하지 않는다.
이 인수문 자체는 미래 실행이나 승인 증거가 아니다.
