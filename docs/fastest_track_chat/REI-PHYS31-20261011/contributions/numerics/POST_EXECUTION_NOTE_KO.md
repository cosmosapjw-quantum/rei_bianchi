# PHYS31 — 실제 첫 실행과 별도 경로 replay의 결과

기여자 `/root/phys31_numerics` · **NONBLIND 수치 구현자, 최종 reviewer 아님**. 이 문서는 root가 실행한 첫 main의 실제 raw와 첫 실행·replay의 execution receipt 및 byte equality receipt를 읽은 뒤 작성했다. 구현자 자신의 science main 호출은 **0회**이며, root 소유 wrapper는 첫 main **1회**와 별도 복원 경로의 replay **1회**, 합계 **2회** 실행했다. 이 역할에서 새 확인용 계산·추가 물리 평가·toy 실행·finite difference를 실행하지 않았다.

## 1. 실제 결과

첫 main은 **`PASS_SCOPED`, exit 0, 사전 고정 79/79 check PASS**로 끝났다. 미평가 ID와 실패 ID는 없고, raw의 최대 고정-scale 오차는

\[
4.6819296\times10^{-74}<10^{-60}
\]

였다. 이는 Decimal80, ROUND_HALF_EVEN의 두 물리 표현·문턱 quotient·정확 toy에 관한 계약 범위 내 수치 결과다. 79라는 수는 byte identity, 대수, exact toy, 실행 장부 check를 합한 값이며 서로 독립적인 79개의 물리 관측이 아니다.

근거는 다음 두 실제 파일이다.

- `QUARTIC_PROFILE_FIRST.json`: 69,411 bytes, SHA256 `843335dd8754bfaf57d201d9db888e80a7713d95a8147de08ffdb97db609e66a`.
- `../../execution/first/EXECUTION.json`: root wrapper의 실제 argv, UTC 시각, exit, stdout/stderr, 원시 결과 identity, 실행 전후 runtime 10파일의 보존과 실제 count.

첫 실행의 시작은 **2026-10-11 10:05:38.367462 UTC**, 종료는 **10:05:38.743066 UTC**, 측정 wall time은 **0.3752320980129298 s**였다. timeout은 60초, timeout 발생·자동 재시도는 0회, Python 버전은 3.12.14, stderr는 0 bytes였다. 실행 전후 입력·코드·프로토콜·freeze의 바이트가 보존되었다. `NUMERICS_NOTE_KO.md`의 작성 시점에 기록한 미실행 상태는 그 이전 시점의 상태로 유지한다.

replay도 **79/79 PASS, exit 0**이었다. 시작은 **10:07:02.722317 UTC**, 종료는 **10:07:03.109715 UTC**, wall time은 **0.38734157200087793 s**였다. root의 `../../portability/REPLAY_RECEIPT.json`은 10개 runtime payload를 새 경로에 복원한 실행, 실행 전후의 SHA·크기·mode 보존, first와 replay raw의 **byte equality와 parsed JSON equality**를 기록한다. 두 raw는 모두 69,411 bytes와 위 SHA256을 공유한다. 이 역할은 해당 receipt를 실제 읽었으며, 별도 파일 재복원이나 science main을 추가로 실행하지 않았다. 같은 호스트·Python 3.12.14의 replay이므로 독립 물리 데이터 credit은 0이다.

## 2. 네 노드의 새 k⁽⁴⁾

아래는 log-energy 경로의 표시용 축약값이다. 전체 80자리 Decimal 문자열과 별도 ordinary-energy 결과 및 잔차는 raw에 보존되어 있다. 같은 네 노드 문자열을 사용했고 새 에너지 노드를 만들지 않았다.

| 보존 노드 | \(k^{(4)}\), s⁻⁴ eV⁻⁴ |
|---|---:|
| \(a\) | \(1.11549550203365440476\times10^{-65}\) |
| \(v_*\) | \(3.51864559996025841356\times10^{-67}\) |
| \(u_0\) | \(7.29797573047476616100\times10^{-66}\) |
| \(b\) | \(1.33026437065898735696\times10^{-67}\) |

`PHYSICAL.k4.a`, `.v_star`, `.u_zero`, `.b`는 서로 다른 log/ordinary series 조립의 k⁽⁴⁾ 결과를 고정 \(S_4=10^{-64}/18^4\)로 비교하여 모두 통과했다. 두 경로는 동일한 fit·원 J·source-real 상수·노드·Decimal primitive를 공유한다. 이 일치를 별도 물리 데이터 확인이나 interval 부호 인증이라고 부르지 않는다.

## 3. 같은 μ₂인 P4−uniform 문턱 차이

\(\Delta\mu_4=8/315\), \(D_4=-\Delta\mu_4\mathcal H_4/(24C)\)의 보존점 평가 결과다.

| 양 | upper branch | lower branch |
|---|---:|---:|
| \(\mathcal H_4\), s⁻⁴ eV⁻⁴ | \(5.30866785316891123466\times10^{-66}\) | \(4.78279009824157376627\times10^{-66}\) |
| 응답 차이의 \(\delta^4\) 계수, s⁻⁴ eV⁻⁴ | \(5.61763793986128172980\times10^{-69}\) | \(5.06115354311277647224\times10^{-69}\) |
| \(D_4\), eV⁻² | \(-0.00110495859229183347782\) | \(-0.000619616589313442784491\) |

같은 입력에서 두 경로 모두 \(\mathcal H_4>0\), \(D_4<0\)를 반환했다. upper 쪽의 음의 차이 계수의 절댓값이 더 크며, 이미 구한 두 계수에서 얻은 gap의 4차 차이 계수는

\[
D_{4,\mathrm{lower}}-D_{4,\mathrm{upper}}
\approx +0.000485342002978390693326\ \mathrm{eV}^{-2}
\]

였다. 이 gap 값은 새 물리 호출 없이 기존 두 계수를 빼서 저장한 보고용 값이다.

각 branch의 두 번째 quotient에서는 cached \(k(e),k'(x)\)로 \(N_W=k(e)+sRk'(x)\)를 별도로 구성했다. \(G_W=N_W-A\)와 \(QC\), normalized quotient와 unnormalized quotient, 그리고 두 미분 경로의 \(D_4\) 비교가 모두 원 허용치를 통과했다. raw에는 뺄셈 후 값과 잔차가 그대로 있다. 상속된 비영 수준 \(A_*=-2.2748589\times10^{-137}\), \(A_0=-3.2582515\times10^{-137}\) s⁻⁴를 0으로 대체하지 않았다.

**해석의 한계.** 이 결과는 저장된 점과 고정 J에서 같은 A-level의 4차 계수에 대한 finite Decimal 확인이다. 정확 영점의 4차 계수, 원 J의 불확실성, 모든 미소 오차가 포함된 엄밀한 부호 구간을 새로 인증하지 않았다. 어느 특정한 양의 폭에서 실제 문턱이나 gap이 이 순서로 놓인다는 유한 폭 결론도 아직 없다. 그 결론에는 정확 모델에서의 계수 부호와 나머지 또는 유효 폭 근거가 추가로 필요하다.

## 4. 정확 유리수 진단이 실제로 구별한 것

실제 moment 출력은 uniform의 \((1,0,1/3,0,1/5)\), P4의 \((1,0,1/3,0,71/315)\)였으며 positivity square와 \(\Delta\mu_4=8/315\)도 정확히 일치했다. \(\phi=E^n\), \(n=0,\ldots,6\), \(E=3\)의 두 미분 표현은 직접 다항식 도함수와 정확히 같았다.

dimensionless cubic toy는 두 branch의 profile root 차이가 0–4차까지 모두 정확히 0이었다. quartic toy의 1–3차 차이도 0이고, 4차 차이는 upper에서 \(-32/142065\), lower에서 \(-32/116865\)였다. 이는 사전 손유도 값과 일반 \(-\Delta\mu_4/(100C)\) 식 모두와 일치했다. 두 프로파일×두 kernel×두 branch의 총 8개 formal root series를 다시 대입한 normalized·unnormalized residual은 0–4차 모두 0이었다.

factorial과 비영 A의 negative control은 실제로 잘못된 식을 구별했다.

| quartic branch | 올바른 \(D_4\) | \(1/24\) 누락 | 분모에서 A 누락 |
|---|---:|---:|---:|
| upper | \(-32/142065\) | \(-256/47355\) | \(-4/24633\) |
| lower | \(-32/116865\) | \(-256/38955\) | \(-2/10269\) |

각 잘못된 값이 올바른 formal root coefficient와 정확히 다르므로 해당 4개 negative control이 통과했다. 이들은 무차원 유리수 toy의 진단값이고 물리 문턱의 측정 결과가 아니다.

## 5. 실제 예산과 남은 gate

첫 main은 두 경로 각 4회, 총 **8회의 새 물리 k⁽⁴⁾ 출력**을 생성했다. 새 물리 하위 도함수 출력·새 에너지 노드·근 탐색/보정·기존 프로그램 import/main/suite·구적·유한차분·physical width/root sweep·전체 구간 부호 캠페인·native/gas IVP/dense LP는 모두 **0회**다.

exact 작업은 사전 예산대로 moment 10개, positivity 항등식 1개, operator 경우 7개/표현 14개, toy 부호 경계 2개, toy branch 4개, profile root series 8개, formal step 32개, response-series 조립 48개였다. 첫 실행에서 과학 실패·예외·재시도는 없었다. 첫 실행 전 문서의 TeX 오타 수정 및 owner가 요구한 손유도 oracle 보강은 provenance에 보존했고, 실행 후 runtime 파일은 수정하지 않았다.

전체 수치 work unit의 상태는 **`DONE_SCOPED`**, 별도 최종 decision은 **pending**이다. 첫 main과 replay 합계 예산은 **main 2회, 새 물리 k⁽⁴⁾ 16회**로 모두 소진했다. 각 실행의 네 노드는 동일한 보존 집합이므로 전체 distinct retained node도 4개이며, 새 물리 에너지 노드는 0개다. 세 번째 main이나 추가 도함수·toy·원 cache 재계산을 허용하지 않는다. 최종 distinct NONBLIND decision reviewer의 판정은 별도 문서에서 수행해야 하며, 이 수치 구현자는 최종 PROMOTE 판정을 하지 않는다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**을 유지한다.
