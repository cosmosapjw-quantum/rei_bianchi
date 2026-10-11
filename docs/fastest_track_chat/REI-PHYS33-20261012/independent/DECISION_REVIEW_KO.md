# REI-PHYS33 — 독립 최종 판정

**판정: PROMOTE_SCOPED.** `C33-01`–`C33-08`의 8개 주장을 동결된 source-real 커널과 지정한 상단 분지 tube에 한정해 채택한다. `H33-01`–`H33-02`는 HOLD로 유지한다. 치명적 발견과 미완료 필수 수정은 0건이다. 이번 판정은 실제 기체 이력의 Physical HOLD를 해제하지 않는다.

최종 검토자: `/root/decision_review`. 후보 생성과 검증 설계에 참여하지 않은 별도 에이전트다. 검토는 **NONBLIND**이며 같은 GPT-6 Astra 모델·호스트·입력 계보를 공유한다. 독립 물리 자료 검증 credit은 0이다. 검토자는 새 물리 커널·근·jet·과거 과학 프로그램·main·replay를 실행하지 않았다. 수행한 것은 정적 코드·증명·원시 기록 읽기, 파일 identity 및 JSON 구조 확인, 산술 라이브러리 공식 문서 확인이다.

## 1. 판정이 결부되는 동결본

판정 대상은 `evidence/FINAL_CANDIDATE_FREEZE.json`이며 SHA256은 다음과 같다.

```text
bfbe9e564c4c07d3063f1fcb95fa8fb30377c43a886d82a9be328a3c61703a79
```

이 manifest의 **44개 파일, 2,480,481 bytes**를 실제 파일의 크기·SHA256과 대조했고 모두 일치했다. 실행 전 동결의 계약·프로토콜·두 입력·세 코드·대수 증명 8개도 일치했다. metadata 검증은 과학 계산을 다시 수행한 것으로 세지 않았다.

직접 전부 읽은 현재 코드 세 개는 `outward_decimal.py`, `rational_kernel.py`, `certify_upper_branch.py`다. 현재 계약·프로토콜·주장 목록·두 증명/보고서·source manifest·실행 기록과 후속 인계도 검토했다. 상속 증거에서는 PHYS31의 입력/정칙성/프로파일 정의, PHYS32의 정확 Peano 문서, 일반 root-tube 증명의 정의·기울기·잔차·존재 부분과 조건 분석의 관련 식을 선택적으로 읽었다. PHYS32의 전체 과학 검산을 반복하거나 44개 파일 모두의 내용을 전면 재감사했다고 주장하지 않는다.

## 2. 주장별 판정

| 주장 | 판정 | 근거와 범위 |
|---|---|---|
| C33-01: 고정 입력·비영 공통 A·계보 | PROMOTE_SCOPED | PHYS29/22의 전체 문자열, 고정 키·해시, source-real 상수 의미를 보존한다. 입력 identity는 물리적 정확도와 별개다. |
| C33-02: 유리수 미분 인수분해·Bernstein 경계 | PROMOTE_SCOPED | 곱미분 재귀와 exact 기저 변환을 정적으로 검토했다. 0–4차의 다항식 차수는 8+n≤12다. |
| C33-03: 전체 [13.61,22] eV의 k″, k⁽⁴⁾ 양성 | PROMOTE_SCOPED | exact 유리수 cell의 Bernstein 상계와 outward 초월 인자 계산이 원시 양의 하한을 지지한다. Decimal 산술 의미를 신뢰하는 계산 인증이다. |
| C33-04: actual W 기하·패킷·기울기 경로 포함 | PROMOTE_SCOPED | V=W−δ²/3과 모든 폭/분산 tube의 feasibility를 보존한다. 기울기에 필요한 두 패킷 사이 선분도 같은 에너지 구간에 포함된다. |
| C33-05: 같은 A의 근 존재·tube 안 유일성 | PROMOTE_SCOPED | 양의 기울기와 Bdisp+εr<κη에서 양 끝의 부호를 얻는다. 지정한 tube 바깥의 전역 유일성은 판정하지 않는다. |
| C33-06: 양의 폭에서 Wp<Wu 및 크기 경계 | PROMOTE_SCOPED | 정확한 양의 Peano 평균과 근 사이 양의 기울기를 결합한다. δ=0의 엄격 부등호는 제외한다. |
| C33-07: 저장 중심의 비영 잔차·정확근 거리 | PROMOTE_SCOPED | 저장 중심을 정확한 A의 근으로 가정하지 않고, 재구성한 exact 중심과 실제 잔차 enclosure를 사용한다. |
| C33-08: first/replay 29/29 및 raw identity | PROMOTE_SCOPED | 두 구조화된 원시 파일·started/finished receipt·복원 기록을 확인했다. 외부 exit=0은 owner 관측 attestation이며 원 도구 envelope의 독립 재확인은 아니다. |
| H33-01: Physical admission·J/fit·coupled history | HOLD | 실제 물리 입력 오차나 기체 이력의 유효성이 이번 계산에 의해 확보되지 않았다. |
| H33-02: 하단 분지와 두 분지 gap | HOLD | 이번 인증 영역은 상단 분지 하나다. 두 분지 gap 부호는 채택하지 않는다. |

## 3. 수학·구현을 연결한 핵심 검토

### 고정 함수와 미분

커널은 고정된 J에 대해 k=𝒫(D²+3D)φ, D=E∂E이다. u=√(E/B), B=E0 ya로 바꾸면 D=(u/2)∂u이고, ordinary energy 미분은 (2Bu)⁻¹∂u다. `derivative_numerator`의 두 계수 기여는 정확히

\[
\mathcal T_{a,b}Q=[a+(a+b)u]Q+u(1+u)Q'
\]

이며 ordinary 미분마다 u 지수가 2 감소한다. D²+3D를 같은 인자로 묶을 때 3D 항의 계수 6, 최종 multiplier 1/[4(2B)ⁿ]을 확인했다. 원 J의 부호는 다항식 안에 보존되며 φ의 로그를 취하지 않는다.

Bernstein 변환은 affine power 전개와 binomial 기저 항등식에서 나오므로 점 표본에 대한 경험적 경계가 아니다. 검토 중 지적한 exact cell과 표시용 Decimal `z_interval`의 구분이 최종 R33.5에 반영되었다. 다항식 경계는 정확한 rational cell에만 적용하고, 더 넓은 구간에서 얻은 외부 인자 경계를 곱하는 방식은 유효하다.

### 바깥 반올림

Fraction의 Decimal 변환과 사칙연산은 각각 ROUND_FLOOR/ROUND_CEILING을 사용한다. 일반 곱은 네 endpoint 곱, 부호 반전은 context에 영향을 받지 않는 `copy_negate`, 절댓값 상한은 `copy_abs`를 쓴다. 0을 포함한 분모는 명시적으로 거부한다. 실수 거듭제곱은 interval exp(α ln x)로 구성하므로 `Decimal.power`의 반올림 한계에 의존하지 않는다.

[Python 3.12 Decimal 문서](https://docs.python.org/3.12/library/decimal.html)는 ln·exp의 정확한 HALF_EVEN 반올림과 인접 representable 값 연산을 명시한다. [mpdecimal arithmetic 문서](https://www.bytereef.org/mpdecimal/doc/libmpdec/arithmetic.html#square-root)는 sqrt의 정확한 HALF_EVEN 반올림을 명시한다. 이 의미 아래에서 같은 precision의 바로 앞/뒤 값으로 확장한 endpoint가 exact 값을 감싼다. 본 판정은 라이브러리 구현의 형식 검증이나 독립 산술 backend 재계산을 추가하지 않는다.

### 근 존재와 actual W

V=W−μ2δ², eδ=a+δ, x=m+V/(R−δ), p=V/[(R−δ)²+V]를 쓰면 실제 광자 분산은 W이고 두 프로파일의 기하는 같다. 고정 δ에서 직접 미분한 기울기는

\[
F_{\alpha,W}=\int_0^1t\int k''((1-t)e_\delta+t x+\delta z)
\,d\alpha(z)dt.
\]

전체 기울기 경로가 [13.61,22] 안에 있으므로 m2/2≤Fα,W≤M2/2가 성립한다. 이 영역은 양의 곡률이 필요한 두 패킷 사이 선분까지 포함하며, k⁽⁴⁾의 패킷 부호만으로 기울기를 추정하지 않는다.

저장 중심에서 pδ′의 분자는 2(R−δ)(ŵ−μ2Rδ)>0이다. 따라서 pδ≤pd, qδ≤q0와 코드의 중심 이동 상계 Dx를 사용한 Bdisp는 0≤δ≤d 전체의 균일 상계다. 원시 잔차는

\[
F_0(\widehat W)-A\in[-9.86683597866,-9.86683596720]\times10^{-143}
\ \mathrm{s}^{-4}
\]

이며 0으로 대체되지 않았다. 정확한 A=−2.2748589×10⁻¹³⁷ s⁻⁴와 전체 ŵ 문자열을 유지한 상태에서 κη−(Bdisp+εr)>1.7215394631×10⁻⁶⁷ s⁻⁴>0을 얻는다. 따라서 두 프로파일 각각의 근이 지정한 ±0.25 eV² tube 안에 유일하게 존재한다. 이 논증은 근의 존재를 먼저 가정하여 tube를 구성하는 순환을 포함하지 않는다.

### 정확한 순서

h_p−h_u=[(1−z²)⁴]⁽⁴⁾/768이고 0–3차 경계항이 양 끝에서 사라진다. 네 번 부분적분과 ∫(1−z²)⁴ dz=256/315가 계수 1/945를 준다. 따라서 같은 W에서 두 응답의 차이는 δ⁴/945에 양의 k⁽⁴⁾ 확률평균을 곱한 정확한 양이다. 같은 A의 두 근을 비교하고 양의 평균 기울기로 나누면

\[
-\frac{M_4}{945\kappa}\delta^4\le W_p-W_u
\le-\frac{m_4}{945K}\delta^4<0,\qquad0<\delta\le0.001\ \mathrm{eV}.
\]

원시 경계를 바깥으로 줄여 표시한 −8.8300×10⁻³δ⁴≤Wp−Wu≤−1.0760×10⁻⁵δ⁴는 유효하다. 계수는 eV⁻²이므로 분산 차이의 단위 eV²와 일치한다. 이는 같은 이차 모멘트의 임의 프로파일 쌍에 관한 정리나 두 분지 gap에 관한 정리가 아니다.

## 4. 실행 근거와 보존 한계

두 원시 JSON은 각각 959,245 bytes이고 SHA256은 모두 다음 값이다.

```text
98b23330410982d6c09a31f1e8b6e431396a9fdfe71b61acf080de2d9183d6aa
```

각 파일은 PASS_SCOPED, 검사 29/29, `failure=null`이다. 기록된 첫 실행/replay wall time은 0.970251060/0.916249877초, CPU time은 0.967341850/0.915743442초, peak RSS는 각각 14,464 KiB다. main당 Bernstein box 172, 초월 인자 box 170, 별도 ordinary-energy joint jet 2, 영폭 잔차 조립 1을 기록했다. 과거 과학 프로그램·새 root search·finite-width quadrature·native·gas IVP·NCP 실행은 기록된 프로그램에서 0이다. 코드의 call graph도 이 구분과 일치한다.

8개 pointwise expression overlap은 구현 대조이며 연속 부호 증명의 대체물이 아니다. 동일 호스트의 byte-identical replay는 복원·재현성 근거이고, 별도 물리 자료나 독립 backend 검증은 아니다. 검토자는 이 170개의 enclosure를 별도 프로그램으로 다시 계산하지 않았다.

**원 exec 도구 envelope 및 분리된 stdout/stderr 파일은 보존되어 있지 않다.** `HOST_EXECUTION_ATTESTATION.json`의 두 exit_code=0은 owner가 실제 관측한 결과를 나중에 기록한 것이다. 본 검토자가 원 도구 응답을 독립적으로 읽었다고 주장하지 않으며, stderr가 비어 있었다고 새로 단정하지 않는다. 구조화된 원시 과학 결과와 started/finished receipt는 실제 바이트로 남아 있다. 이 보존 한계를 숨기거나 reconstructed receipt를 raw 도구 캡처로 바꾸지 않았다.

검토에서 요청했던 tube 유일성의 적용 범위, §4의 e=eδ 및 x=xδ,W 약어, Bernstein cell 구분은 최종 동결본에서 해결되었다. 이들은 문서 명확화이며 과학 코드 변경이나 추가 실행을 수반하지 않았다. 원시 first/replay에 실패는 기록되지 않았고, 기존 [160,161] FAIL 및 auxiliary escape FAIL은 유지되었다.

## 5. 종료 범위

본 연구 단위는 고정 수학적 커널에 대한 bounded 계산 인증으로 채택한다. novelty/우선권이나 원자 fit 정확도의 독립 문헌 인증은 판정하지 않는다. 후속 PHYS34는 별도 하단 분지 연구 제안으로 읽으며 현재 결과·예산에서 실행 성공을 상속하지 않는다.

**유지 상태:** Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0. PHYS33의 first 1/1과 replay 1/1 예산은 SPENT이고, 검토자 추가 과학 실행은 0이다. 이 최종 판정은 publish·merge·PR 본문 변경·외부 메시지 권한을 새로 부여하지 않는다.
