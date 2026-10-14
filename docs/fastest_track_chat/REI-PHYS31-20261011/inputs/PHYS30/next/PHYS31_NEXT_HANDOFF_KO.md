# PHYS31 다음 연구 handoff

상태: **PROPOSED / NOT_RUN**. 이 문서는 REI-PHYS30-20261011의 실제 결과에서 다음 한 질문을 넘긴다. 최종 선행 판정은 `independent/DECISION_REVIEW.json`, 종료는 `state/CLOSEOUT.json`, 후속 publication과 전달은 분리된 실제 영수증을 권위로 삼는다.

## 1. 다음 한 질문

**같은 \(\mu_2\)를 갖고 고차 모멘트가 다른 두 고정 대칭 프로파일의 문턱 이동은 어느 다음 차수에서 처음 구별되는가?**

추가 커널 정칙성, 필요한 고차 도함수, 물리 \(\delta\ge0\) 근방에서의 고차 전개 존재를 먼저 명시한다. 차수나 부호를 미리 PASS 조건으로 두지 않는다. PHYS30의 \(o(\delta^2)\)만으로 더 높은 계수의 존재·값이 따라오지 않는다.

## 2. 실제 PHYS30 결과

같은 중심 구간 \([a+\delta,b-\delta]\), 고정 실제 광자 분산 \(W\), 고정 대칭 Borel 확률측도에서

\[
V=W-\mu_2\delta^2,\quad c_\nu=c_u,\quad
d_\nu=d_u+(\mu_2-\tfrac13)\left(1-\frac{\mathcal H}{2C}\right)
\]

를 직접 유도했다. \(C=F_W>0,\ \mathcal H=pk''(e)+qk''(x)\), \(d=W''(0^+)/2\)다. 같은 \(\mu_2\)의 두 프로파일은 동일 정확 내부근에서 이차까지 같으며 차이가 \(o(\delta^2)\)다. 양의 폭의 응답 경계는 지정된 공통 프로파일 중심 혼합족 내부에 한정한다.

| 저장 계수 | 균일 \(\mu_2=1/3\) | 삼각 \(\mu_2=1/6\) |
|---|---:|---:|
| \(c_*\) [eV] | 5.716380891398 | 5.716380891398 |
| \(c_0\) [eV] | −2.374948370062 | −2.374948370062 |
| \(d_*\) | 1.454082106621 | 1.753670510242 |
| \(d_0\) | −0.245144110608 | −0.131716002143 |

표는 비영 A-level과 유한 산술의 결과다. 정확근의 표기 자리수 인증은 아니다. 최초 cached main 1회와 별도 경로 replay 1회에서 매번 56그룹 PASS, raw bytes/JSON 동일이었다. 새 물리 커널·도함수·노드·근, 과거 PHYS19–29 main/import/suite는 0이다. 정확 profile 모멘트와 A=1 quadratic toy는 각 main의 별도 대수 작업이다. PHYS30 실행 예산은 이미 사용했으므로 다시 소모하지 않는다.

## 3. 다음 시작 때 실제로 읽을 입력

1. PHYS30 최종 decision JSON/KO note, CLOSEOUT, 이 handoff와 report.
2. PHYSICS_CONTRACT, SOURCE_MANIFEST, contributions/theory/DERIVATION_KO 및 THEORY_CLAIMS.
3. contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json, PROTOCOL.json, 필요한 실제 source 부분, EXECUTION.json과 portability/REPLAY_RECEIPT.json.
4. 실제 publication receipt와 이후 delivery ACK, 현재 branch/PR/head/tree 및 pinned source identity.

PHYS30 raw는 231082 bytes, SHA256 `5184af6139423792abc0a95e53bd5ccabca459820761aa1a3f350bda4ac7082e`다. 최초 입력 commit은 `45bd460d779e5a189fc75663d4ae61249e514751`였고 이후 head는 실제 publication receipt와 현재 원격 상태를 읽는다. 과학 source subtree 기대값은 `cb69b4736dd046e4675557577eb8e0ead037d1f3`이다.

원 \(J\)와 근 근사 오차는 계속 열린 상태다. 두 저장 \(A\)는 \(-2.2748589\times10^{-137}\), \(-3.2582515\times10^{-137}\) s⁻⁴다. 정확 영점 수준과 같은 비영 A 수준의 고차 계수를 혼동하지 않는다. 보관된 source identity를 현재 상태 확인 없이 최신 상태로 추정하지 않는다.

## 4. 최소 계약과 제안 순서

같은 지원·중심 구간·평균·실제 분산 convention을 먼저 고정한다. 두 profile은 폭·분산·중심·branch와 독립이어야 한다. 같은 \(\mu_2\)를 실제로 만족하고 비교하려는 고차 모멘트는 다름을 정의와 모멘트로 확인한다. 원자·절대연속성의 추가 조건을 구별한다.

그다음 같은 모멘트 조건 아래 응답 차이의 첫 허용 차수를 직접 유도하고, 그 차이를 근 차이로 옮기는 물리 한쪽 정칙성과 단순근 조건을 증명한다. 대칭성으로 소거되는 항과 움직이는 중심 기하에서 남는 항을 실제 chain rule로 구분한다. 형식 계수와 유효한 나머지 차수를 자동으로 동일시하지 않는다.

가능하면 기호 관계와 저장값만으로 해결한다. 새 물리 고차 도함수가 꼭 필요하면 사용 전에 노드·차수·평가 횟수·두 표현·허용오차·실패 보존을 새로운 계약에 명시한다. PHYS30의 k,k',k'' cache가 더 높은 도함수를 제공한다고 간주하지 않는다. 필요한 작업이 기존 승인 범위를 넘으면 가능한 유도를 먼저 완료하고 그 의존 작업만 보류한다. 기존 문맥에서 허용된 가벼운 파이썬·심볼릭 확인은 그 권한을 따른다.

수치 code가 생기면 필요한 최소 first 1회와 별도 경로 replay 1회를 사전 고정하고, 생성·검증 설계와 다른 reviewer가 최종 판정한다. 과거 프로그램 전체 main/suite/import를 새 고차 증거로 사용하지 않는다. 첫 실패는 보존하고 원인을 분류한다. 사후 tolerance 완화와 숨은 재시도는 하지 않는다.

## 5. 미실행 범위와 보호 상태

PHYS31의 답은 아직 유도하거나 계산하지 않았다. 고차 차수 확정, 새 도함수·profile 계산, 유한폭 root, 정량 Taylor 오차·유효폭·global ordering을 현재 성과로 쓰지 않는다. PHYS30의 두 수치 profile은 \(\mu_2\)가 다르므로 같은 \(\mu_2\)의 고차 구별을 확인한 사례가 아니다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0.**

별도 atomic/HH/RCT/CR lane, local Codex, heavy native 실행을 켜지 않는다. 새 물리 역사·방출원 admission을 하지 않는다. 같은 host/model/history의 reviewer와 replay를 독립 물리 실험으로 세지 않는다.

## 6. 지속되는 실행·publication 범위

사용자의 연속적인 다음 물리 연구 루프 요청과 실제 이전 handoff가 지원하는, 이 대화의 가벼운 연구·코딩·검토 및 **같은 branch의 additive docs** 범위를 이어받는다. handoff 문구 자체로 새로운 권한을 만들지는 않는다.

Repo는 `cosmosapjw-quantum/rei_bianchi`, branch는 `forward/rust-reion-kernels-20260922`, PR은 `83`이다. 새 PHYS31 연구를 승인된 범위 안에서 실제 완료하고 별도 판단을 받은 경우 새 `docs/fastest_track_chat/REI-PHYS31-<실행일>/` prefix에만 추가한다. 실제 최신 head를 확인한 expected-head nonforce CAS, 기존 모든 경로와 scientific source subtree 보존, 새 문서 raw readback, PR body·draft·미병합 상태 확인을 유지한다.

기존 source/default/runtime, PR body, merge와 타인에게 보내는 메시지는 변경·실행하지 않는다. 이미 승인된 가역 연구·검토·additive docs를 위해 같은 허락을 다시 묻지 않는다. 완료와 한계, 실제 실행 횟수, 첫 실패와 수정, 다음 미실행 질문을 파일과 대화에 명시한다.

