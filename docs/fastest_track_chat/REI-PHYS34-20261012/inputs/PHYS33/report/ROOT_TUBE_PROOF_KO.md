# PHYS33 — 고정 커널의 유한 폭 상단 분지: 존재·유일성·엄격한 순서

작성: `/root`. 후보 대수 기여는 `../contributions/theory/DERIVATION_KO.md`, 실제 인증서는 `../evidence/CERTIFICATE_FIRST.json` 및 복원 재실행 원본이다. 이 문서는 계산 이후의 증명 연결 문서이며 실행 전 계약·코드·영역을 수정하지 않는다. 독립 최종 판정은 `../independent/DECISION_REVIEW.json`이 맡는다.

## 1. 고정된 대상과 명제

`PHYSICS_CONTRACT.json`의 source-real 커널을 사용한다. 원 소스의 binary64 상수 값 자체를 정확한 유리수로 해석하고, 원 JSON의 두 J 문자열과 공통 높이 A를 정확한 십진 유리수로 해석한다. 그 위에서 정확한 실수 곱을 취한다. native binary64 연산 순서의 재현이나 원자 fit·J의 물리적 오차를 포함하는 명제가 아니다.

단위는 E, a, b, m, R, δ가 eV, 실제 분산 W가 eV², k와 A가 s⁻⁴다. 다음은 정확한 선언값이다.

\[
a=13.61,\quad b=24.58,\quad m=18,\quad R=m-a=4.39,
\quad d=0.001,\quad \eta=0.25,
\]
\[
A=-2.2748589\times10^{-137}\ \mathrm{s}^{-4}.
\]

A의 원 키는 PHYS29 `second_order.jet_chain.upper_root.response_s-4`다. 같은 문서의 `stored_PHYS26_response_s-4`나 0으로 바꾸지 않는다. 중심 \(\widehat W\)는 다음 저장 문자열 전체의 정확한 값이다.

```text
16.33994465458970734510914472551741998431355423898342002148048461097774940400782385510690504823436286634289461446838932341278953576065611895671628803067445872017
```

명제의 영역은 \(0\le\delta\le d\)와 \(I_W=[\widehat W-\eta,\widehat W+\eta]\)다. `upper`는 상속된 극값 분지의 이름이다. 두 분산 근 중 수치적으로 큰 쪽이라는 뜻으로 재해석하지 않는다.

프로파일 변수 z∈[−1,1]에 대해

\[
h_u(z)=\frac12,\qquad h_p(z)=\frac{35z^4-30z^2+11}{16}
=\frac{1+P_4(z)}2.
\]

둘 다 양의 확률밀도이고 짝함수다. \(h_p\ge2/7>0\), 평균은 0, 공통 \(\mu_2=1/3\), \(\mu_{4,u}=1/5\), \(\mu_{4,p}=71/315\)이므로 \(\Delta\mu_4=8/315\)다. 아래 적분은 각각의 확률측도 \(d\alpha=h_\alpha(z)dz\)에 대한 적분이다.

## 2. 실제 분산과 패킷의 기하

\[
r=R-\delta,\quad V=W-\mu_2\delta^2,\quad
e_\delta=a+\delta,\quad x_{\delta,W}=m+\frac Vr,
\]
\[
p=\frac{V}{r^2+V},\qquad q=\frac{r^2}{r^2+V}=1-p.
\]

이 두 중심의 이산 분산은 V이고 프로파일 분산이 \(\mu_2\delta^2\)를 더하므로 실제 분산은 W다. 응답은

\[
F_\alpha(\delta,W)=p\int k(e_\delta+\delta z)d\alpha(z)
 +q\int k(x_{\delta,W}+\delta z)d\alpha(z).
\tag{R33.1}
\]

전체 직사각형에서 코드가 정확한 유리수 비교로 확인한 충분조건은

\[
\mu_2d^2<\widehat W-\eta,
\qquad \widehat W+\eta<(R-d)(b-m-d).
\tag{R33.2}
\]

따라서 V>0, p,q>0, 두 중심 및 패킷은 허용 구간 [a,b]에 남는다. 전체 endpoint 패킷은 [a,a+2d]=[13.61,13.612]에 포함되고, 내부 패킷은

\[
\left[m+\frac{\widehat W-\eta-\mu_2d^2}{R}-d,
      m+\frac{\widehat W+\eta}{R-d}+d\right]
\tag{R33.3}
\]

에 포함된다. R33.3과 endpoint 패킷 모두 [13.61,22] eV 안에 있음을 인증했다. 같은 z에서 두 에너지 사이를 잇는 모든 선분도 이 볼록 구간 안에 있다. 이 포함관계가 아래 미분·평균값 정리에 쓰는 전체 영역을 확보한다.

## 3. 전체 에너지 구간에서의 미분 부호 인증

대수 문서 T33.17은 \(u=\sqrt{E/(E_0y_a)}\), \(B=E_0y_a\)를 써서

\[
k^{(n)}(E)=\frac{C}{4(2B)^n}
u^{P-11-2n}(1+u)^{-P-2-n}Q_n(u),\quad0\le n\le4
\tag{R33.4}
\]

를 정확히 유도했다. C>0이고 Qn은 exact Fraction 계수의 차수 8+n 이하 다항식이다. 따라서 양의 외부 인자와 다항식의 부호를 분리할 수 있다.

원시 JSON `certificate.covering.z_domain`의 두 Decimal 끝점을 정확한 유리수 \(u_-,u_+\)로 해석한다. 실제 다항식 cell은

\[
l_i=u_-+\frac{i}{32}(u_+-u_-),\quad
u_i=u_-+\frac{i+1}{32}(u_+-u_-),\quad i=0,\ldots,31
\tag{R33.5}
\]

이다. 각 cell에서 Qn의 정확한 Bernstein 계수 최소·최대가 전체 cell의 다항식 범위를 덮는다. JSON 각 record의 `z_interval`은 외부 초월 인자 평가를 위해 이 exact cell을 다시 Decimal로 바깥 확장한 구간이다. **다항식 Bernstein 상계는 R33.5의 exact cell에 적용된다.** 이를 더 넓은 표시용 `z_interval`의 다항식 범위라고 주장하지 않는다. 외부 인자는 더 큰 구간에서 덮으므로, 두 범위를 곱하면 필요한 exact cell에서의 R33.4가 포함된다.

u-domain 자체는 E∈[13.61,22]의 outward sqrt로 만들었다. 느슨한 유리수 상자 [49/50,5/4]는 포함관계 확인용이다. 실제 사용한 sqrt-grid의 E 역상 양 끝은 H I source cutoff real64(13.60)보다 크고 He I cutoff real64(24.59)보다 작다. 따라서 조각별 provider에서 다른 식으로 넘어가는 점을 통과하지 않는다. χ=real64(13.598434599702)는 가열 에너지 오프셋이며 cutoff와 같게 두지 않는다.

기본 사칙연산은 90자리 ROUND_FLOOR/ROUND_CEILING, ln·exp·sqrt는 올바르게 반올림된 Decimal 결과의 바로 이웃으로 확장한다. 실수 거듭제곱은 exp(α ln x)로 감싼다. `Decimal.power`를 쓰지 않는다. 이 인증은 Python Decimal/libmpdec의 명시된 반올림 의미를 신뢰하는 계산 증명이며 형식증명기에서 검증한 산술 구현은 아니다. 구현 근거: [Python 3.12 Decimal](https://docs.python.org/3.12/library/decimal.html).

실제 원시 인증서가 얻은 범위를 더 느슨하게 바깥 반올림해 표시하면

| 양 | 하한 | 상한 | 단위 |
|---|---:|---:|---|
| k″ | 2.8173987399×10⁻⁶⁶ | 6.0442193357×10⁻⁶⁵ | s⁻⁴ eV⁻² |
| k⁽⁴⁾ | 3.0731179233×10⁻⁶⁷ | 1.1754655667×10⁻⁶⁵ | s⁻⁴ eV⁻⁴ |
| k′의 절댓값 | 0 | 1.5178992449×10⁻⁶⁴ | s⁻⁴ eV⁻¹ |

특히 \(m_2=\inf_{\mathrm{cert}}k''>0\), \(m_4=\inf_{\mathrm{cert}}k^{(4)}>0\)이고, \(M_1,M_2,M_4\)는 원시 인증서의 해당 절댓값·상한이다. 코드의 이후 연산은 위 표시용 자릿수가 아니라 원시 90자리 경계를 사용한다.

## 4. W 미분은 양의 평균: 기울기 경계

δ를 고정하고 \(f_\alpha(y)=\int k(y+\delta z)d\alpha(z)\)라 하자. 이 절에서 \(e=e_\delta\), \(x=x_{\delta,W}\)는 국소 약어다. \(\partial_W V=1\), \(\partial_W x=1/r\)이므로 R33.1을 직접 미분하면

\[
\partial_WF_\alpha=\frac{r^2}{(r^2+V)^2}
\left[f_\alpha(e)-f_\alpha(x)+(x-e)f_\alpha'(x)\right].
\]

\(x-e=(r^2+V)/r\)이며 괄호는 Taylor 적분 항등식으로
\((x-e)^2\int_0^1t f_\alpha''((1-t)e+tx)dt\)다. 따라서 정확히

\[
\boxed{\partial_WF_\alpha(\delta,W)
=\int_0^1t\int k''((1-t)e_\delta+t x_{\delta,W}+\delta z)
d\alpha(z)dt.}
\tag{R33.6}
\]

확률밀도의 비음성과 \(\int_0^1t dt=1/2\)를 쓰면 전체 tube에서

\[
0<\kappa:=\frac{m_2}{2}\le\partial_WF_\alpha
\le K:=\frac{M_2}{2}.
\tag{R33.7}
\]

이로써 각 δ에서 Fα가 W에 대해 엄격히 증가한다. 수치 기울기를 표본점에서 추정하는 논증이 아니다.

## 5. 같은 정확한 A에 대한 잔차와 근의 존재

저장 중심을 정확한 근으로 가정하지 않는다. δ=0에서는 두 프로파일이 같고

\[
x_0=m+\frac{\widehat W}{R},\quad
p_0=\frac{\widehat W}{R^2+\widehat W},\quad
q_0=\frac{R^2}{R^2+\widehat W}.
\]

원 JSON의 반올림된 retained v_star를 이 기하에 대입하지 않고 x0를 정확히 재구성했다. 실제 enclosure는

\[
F_0(\widehat W)-A\in
[-9.86683597866\times10^{-143},
 -9.86683596720\times10^{-143}]\ \mathrm{s}^{-4},
\tag{R33.8}
\]

이므로 \(\epsilon_r=9.86683597866\times10^{-143}\)를 쓴다. 이 작은 음의 잔차를 0으로 자르지 않았다.

W=ŵ에서 pδ의 미분은

\[
p_\delta'=
\frac{2(R-\delta)(\widehat W-\mu_2R\delta)}
{((R-\delta)^2+\widehat W-\mu_2\delta^2)^2}>0.
\tag{R33.9}
\]

분자의 양성을 별도로 exact 비교했다. 따라서 p0≤pδ≤pd이고 qδ≤q0다. 중심 이동은

\[
|x_{\delta,\widehat W}-x_0|
\le D_x:=\frac{\widehat Wd}{R(R-d)}+
\frac{\mu_2d^2}{R-d}.
\tag{R33.10}
\]

짝프로파일은 평균이 0이고 공통 이차 모멘트 μ2를 가지므로 Taylor 적분 나머지에서
\(\left|\int k(y+\delta z)d\alpha-k(y)\right|\le\mu_2M_2\delta^2/2\)다. 먼저 중심·가중치 이동을 분리하고 이 프로파일 경계를 더하면 두 α에 공통으로

\[
|F_\alpha(\delta,\widehat W)-F_0(\widehat W)|\le B_{\rm disp},
\]
\[
\boxed{B_{\rm disp}=(p_d-p_0)|k(a)-k(x_0)|
 +M_1[p_d d+q_0D_x]+\frac{\mu_2M_2d^2}{2}.}
\tag{R33.11}
\]

모든 항은 음이 아니고, 해당 패킷 및 중심 이동 경로는 이미 인증한 에너지 구간에 있다. 따라서 R33.11은 δ-grid 표본이나 δ= d 한 점의 경험적 오차가 아니라 **0≤δ≤d 전체에 대한 균일 상계**다.

실제 outward 계산은

\[
B_{\rm disp}<1.8002089619\times10^{-67}\ \mathrm{s}^{-4},
\]
\[
\boxed{\kappa\eta-(B_{\rm disp}+\epsilon_r)
>1.7215394631\times10^{-67}\ \mathrm{s}^{-4}>0}
\tag{R33.12}
\]

를 준다. R33.7–12에서 모든 허용 δ, 두 α에 대해

\[
F_\alpha(\delta,\widehat W-\eta)<A
<F_\alpha(\delta,\widehat W+\eta).
\]

연속성과 엄격한 단조성으로 각 tube 안에 정확히 한 근 \(W_\alpha(\delta)\)가 존재한다. 추가로

\[
|W_\alpha(\delta)-\widehat W|
\le\frac{B_{\rm disp}+\epsilon_r}{\kappa}<0.127793\ \mathrm{eV}^2,
\tag{R33.13}
\]
\[
|W_\alpha(0)-\widehat W|
\le\frac{\epsilon_r}{\kappa}<7.005\times10^{-77}\ \mathrm{eV}^2.
\tag{R33.14}
\]

R33.14의 자릿수는 고정된 수학적 입력과 A에 대한 거리다. 원자물리적 정밀도나 J의 실제 오차를 뜻하지 않는다.

## 6. 양의 Peano 표현으로 근의 순서와 크기 경계

PHYS32의 정확한 항등식은 Rodrigues 표현의 네 번 부분적분에서 나온다. \((1-z^2)^4\)의 0–3차 경계항은 ±1에서 사라지고

\[
\pi_4(z)=\frac{315}{256}(1-z^2)^4,\quad
\int_{-1}^1\pi_4(z)dz=1,
\]
\[
\boxed{\int k(y+\delta z)(h_p-h_u)(z)dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)\pi_4(z)dz.}
\tag{R33.15}
\]

이것은 유한 폭에서의 정확한 등식이다. 작은 δ의 4차 Taylor 항만 남기는 근사가 아니다. Rodrigues 공식의 일반 배경은 [DLMF 18.5(ii)](https://dlmf.nist.gov/18.5#ii), 이 특정 정규화의 직접 유도는 상속된 `POSITIVE_PEANO_AND_TOY_ORACLES_KO.md` 및 R33.15를 따른다.

R33.15에 p,q를 곱해 더하면 p+q=1에서

\[
\frac{m_4}{945}\delta^4\le
F_p(\delta,W)-F_u(\delta,W)
\le\frac{M_4}{945}\delta^4.
\tag{R33.16}
\]

따라서 δ>0에서 같은 W의 p 응답이 엄격히 더 크다. 두 근이 같은 A를 갖고 R33.7의 양의 기울기 경계가 근을 잇는 선분 전체에 있으므로 평균값 정리에서

\[
W_p-W_u=-\frac{F_p(\delta,W_u)-F_u(\delta,W_u)}{\overline C_p},
\qquad \kappa\le\overline C_p\le K.
\]

결론은

\[
\boxed{-\frac{M_4}{945\kappa}\delta^4
\le W_p(\delta)-W_u(\delta)
\le-\frac{m_4}{945K}\delta^4<0,
\quad0<\delta\le0.001\ \mathrm{eV}.}
\tag{R33.17}
\]

수치 계수를 바깥으로 줄여 표시하면

\[
\boxed{-8.8300\times10^{-3}\,\delta^4
\le W_p-W_u\le-1.0760\times10^{-5}\,\delta^4<0.}
\tag{R33.18}
\]

두 계수의 단위는 eV⁻², δ의 단위는 eV다. 특히 δ=10⁻³ eV에서

\[
-8.8300\times10^{-15}\le W_p-W_u
\le-1.0760\times10^{-17}\quad\mathrm{eV}^2.
\tag{R33.19}
\]

이는 보수적인 포함 구간이다. 실제 차이를 유효숫자 여러 자리로 예측한 값으로 읽어서는 안 된다. δ=0에서는 두 프로파일 근이 일치하며 엄격한 부등호를 적용하지 않는다.

## 7. 증명·구현·물리의 경계

대수 항등식과 포함관계가 이론 근거이고, exact Fraction 계수와 outward Decimal enclosure가 고정 입력에서 그 충분조건을 채운다. 두 보존 지점에서 ordinary-energy Taylor 표현과 교차 대조한 8개 값은 구현 오류 탐지용이다. 그 점별 대조가 연속 구간의 부호 증명을 대신하지 않는다. 복원 재실행의 byte identity는 같은 호스트의 재현성 근거이며 독립 물리 데이터가 아니다.

인증하지 않은 항목은 하단 분지, 두 분지 사이의 gap 부호, 원 J·원자 fit의 불확실성, 전체 coupled history다. 보호 상태는 `Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0`이다. 이 문서의 scoped root theorem이 이 상태를 해제하지 않는다.
