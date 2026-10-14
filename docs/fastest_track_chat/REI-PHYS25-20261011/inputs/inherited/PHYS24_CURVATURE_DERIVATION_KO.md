# PHYS24: HeIII 스칼라 커널의 엄밀한 볼록성

## 판정 범위와 결과

고정된 초기 기체 상태와 PHYS22에서 직렬화한 수치 야코비안 $J$를 입력으로 해석하면,

$$
I=[13.61,24.58]\ {\rm eV}
\quad\Longrightarrow\quad g''(E)>0.
$$

따라서 PHYS24의 스칼라 커널은 $I$ 전체에서 **엄밀하게 볼록하다**. 양 끝은

$$
g(13.61)>0>g(24.58)
$$

이므로 내부 영점은 정확히 하나다. 이 결론은 양의 유리계수 Bernstein 전개를 이용하는 연속 구간 증명이다. 에너지 격자의 부호 표본을 연속 구간의 증명으로 사용하지 않았다. 첫 새 범위 실행은 20/20 PASS였고, 다항식 부호 검사는 구간 분할 없이 통과했다. 근거는 [CURVATURE_CERTIFICATE.json](CURVATURE_CERTIFICATE.json), 고정된 절차는 [PROTOCOL.json](PROTOCOL.json), 최초 실행 영수증은 [EXECUTION.json](EXECUTION.json)에 있다.

이때 “엄밀”은 **직렬화된 수치 $J$를 정확한 유리수 상수로 취급한 수학 명제**에 붙는다. 원래 $J$의 수치 오차나 물리 입력의 불확실성은 둘러싸지 않았다. 연구 기여자의 산출물이며 최종 승격 판정은 별도 검토자가 맡는다.

## 1. 커널을 하나의 이동된 열 커널로 정리

PHYS24의 정의는

$$
g(E)=\frac14\bigl(J_x\mathscr C\lambda(E)
+J_w\mathscr C[\lambda(E)(E-\chi)]\bigr),
\qquad \mathscr C=D(D+3),\quad D=E\partial_E.
$$

여기서 $J_x=J_{h_2,x}$, $J_w=J_{h_2,w}$,

$$
\lambda(E)=\kappa\sigma(E),\qquad
\kappa=c_{\rm light}n_{\rm H}(1-x_0)>0.
$$

초기 기체는 에너지 미분에서 고정된다. 원래의 HI 광이온화 단면적 적합식은 매끄러운 HI-only 구간에서

$$
\sigma(E)=\sigma_0c_{\rm area}(X-1)^2
X^{P/2-11/2}(1+z)^{-P},\qquad
X=E/E_0=y_a z^2,
$$

$$
z=\sqrt{E/k},\qquad k=E_0y_a,
\qquad D=\frac z2\partial_z
$$

로 쓸 수 있다. $E_0,y_a,P,\sigma_0,c_{\rm area},\chi$ 및 초기 상태의 리터럴은 소스 binary64 값의 정확한 실수 해석이다. 소스에서 매 연산마다 수행하는 native 반올림을 재현한다는 뜻은 아니다.

$$
\alpha=D\log\sigma
=-\frac72+\frac{2}{y_a z^2-1}+\frac{P}{2(1+z)},
\qquad \beta=D\alpha,
$$

$$
A=\alpha^2+3\alpha+\beta,
\qquad
H_c=(E-c)A+E(2\alpha+4)
$$

라고 하면 $\mathscr C\lambda=\kappa\sigma A$,

$$
\mathscr C[\lambda(E)(E-\chi)]
=\kappa\sigma H_\chi.
$$

직렬화된 입력은 $J_x<0<J_w$이고,

$$
\eta=\chi-\frac{J_x}{J_w}
\simeq37.38891086747711\ {\rm eV}
$$

로 놓으면

$$
J_xA+J_wH_\chi=J_wH_\eta,
\qquad
\boxed{g(E)=\frac{\kappa\sigma(E)J_w}{4}H_\eta(E).}
$$

$\eta$는 대수적 이동 상수이며 새로운 물리 문턱이 아니다. 이후의 모든 곡률 부호에서 $\kappa$, $\sigma$, $J_w$는 양의 인자다.

## 2. 유리함수와 14차 곡률 다항식

다음의 유리계수 다항식을 정의한다.

$$
B=y_a z^2-1,\quad C=1+z,\quad G=BC,
\quad N=-7G+4C+PB,
$$

$$
W=N'G-NG',\qquad
\alpha=\frac{N}{2G},\qquad
\beta=\frac{zW}{4G^2}.
$$

프라임은 이 절에서 $z$ 미분이다. 따라서

$$
P_A=N^2+6NG+zW,\qquad A=\frac{P_A}{4G^2},
$$

$$
P_\eta=(kz^2-\eta)P_A+4kz^2G(N+4G),
\qquad H_\eta=\frac{P_\eta}{4G^2}.
$$

$P_A$는 6차, $P_\eta$는 8차다. 곡률은

$$
E^2g''=D(D-1)g
=\frac{\kappa\sigma J_w}{4}
\left[(\alpha^2-\alpha+\beta)H_\eta
+(2\alpha-1)DH_\eta+D^2H_\eta\right]
$$

로 주어진다. 다음을 놓으면

$$
Q=P_\eta'G-2P_\eta G',
\qquad V=N^2-2NG+zW,
$$

$$
DH_\eta=\frac{zQ}{8G^3},
\qquad
D^2H_\eta=\frac{z\bigl[(Q+zQ')G-3zQG'\bigr]}{16G^4}.
$$

이를 대입한 곡률 분자는

$$
\boxed{
R=VP_\eta+2z(N-G)Q
+z\bigl[(Q+zQ')G-3zQG'\bigr]
}
$$

이며 최종적으로

$$
\boxed{g''(E)=\frac{\kappa\sigma(E)J_w}{64E^2G(z)^4}R(z).}
$$

$R$은 14차다. 분모와 앞의 상수가 양수이므로 $R$의 엄밀한 양성만 증명하면 된다.

표기의 전사 오류를 확인하기 위해 원래 $\sigma P_\eta/G^2$에 $D$와 $D-1$을 차례로 작용시키는 두 번째 전개도 계산했다.

$$
U=NP_\eta+zQ,
\qquad
R_{\rm alt}=(N-2G)U+z(U'G-3UG').
$$

두 경로에서 나온 모든 유리계수에 대해 $R=R_{\rm alt}$가 정확히 성립했다. $J_wP_\eta=J_xP_A+J_wP_\chi$ 역시 정확한 다항식 항등식으로 확인했다. 이는 새 곡률 전개의 검증이며 기존 PHYS23 증명 프로그램은 실행하지 않았다.

차원은 $g$가 ${\rm s}^{-2}$, $g''$가 ${\rm s}^{-2}{\rm eV}^{-2}$다. $G,N,W,P_A,V$는 무차원, $P_\eta,Q,U,R$는 에너지 차원이다. 실제 계수는

$$
a_{4,h_2}=\frac{qN_0}{45}\int g\,dP
$$

이며 $qN_0/45>0$이므로 곡률과 부호를 보존한다. PHYS23의 `HeIII_t4_s-4` 값에는 이 정규화가 이미 포함되어 있다.

## 3. 연속 구간의 정확한 부호 인증

고정한 유리수 구간은

$$
L=\frac{49}{50},\qquad U=\frac{33}{25}.
$$

정확한 유리수 산술로

$$
kL^2<13.61<24.58<kU^2,
\qquad y_aL^2-1>0,\qquad 1+L>0
$$

를 확인했다. 따라서 $I$의 모든 $z$가 이 구간에 들어가고 $B,C,G$가 엄밀히 양수다.

유리수 보조 구간을 에너지로 되돌리면 HI-only 물리 구간보다 조금 넓다. 여기서는 **다항식 부호를 인증하기 위한 매끄러운 HI 적합식의 대수적 연장**만 사용한다. 물리 결론과 미분의 적용 범위는 두 문턱 사이에 들어 있는 원래의 $I$로 제한된다. HI 또는 HeI 문턱을 가로지르는 광자 이력이나 미분을 주장하지 않는다.

$t=(z-L)/(U-L)\in[0,1]$로 바꾸어 14차 다항식을

$$
R(L+(U-L)t)
=\sum_{j=0}^{14}b_j\binom{14}{j}t^j(1-t)^{14-j}
$$

로 정확히 전개했다. Bernstein 기저 함수는 비음수이며 합이 1이다. 결과는 다음과 같다.

| 항목 | 최초 실행 결과 |
|---|---:|
| 곡률 분자 차수 | 14 |
| 엄밀히 양수인 Bernstein 계수 | 15/15 |
| 전체 구간 시도 수 | 1 |
| 비인증 시도 | 0 |
| 실제 사용한 구간 분할 | 0 |
| 최소 Bernstein 계수 표시값 | 약 $8.732306038539001\times10^{10}$ |
| 최대 Bernstein 계수 표시값 | 약 $6.099106785058832\times10^{11}$ |

표의 표시값은 읽기 편한 근삿값이고 판정은 모든 계수의 분자·분모를 보존한 `Fraction` 부호로 했다. 원래 단항식 기저로 역변환한 계수도 정확히 일치한다. 양의 계수 전체와 원 다항식의 모든 계수는 JSON에 포함되어 있다.

따라서

$$
R(z)\ge\min_jb_j>0\quad(L\le z\le U),
\qquad g''(E)>0\quad(E\in I).
$$

사전 고정한 절차는 첫 시도가 인증하지 못하면 최대 깊이 8의 이진 분할을 허용했지만, 이번 실행에서는 그 분기를 사용하지 않았다. 허용 오차를 두거나 계수의 작은 음수를 양수로 취급하는 규칙은 없다.

## 4. 끝점의 엄밀한 부호와 유일 영점

에너지 끝점은 정확한 십진수다. 그러므로 $z_a=\sqrt{13.61/k}$, $z_b=\sqrt{24.58/k}$는 일반적으로 유리수가 아니다. 정수 제곱근으로 인접한 $10^{-18}$ 격자점 사이에 이들을 둘러싼 뒤, 그 좁은 **유리수 구간 전체**에서 8차 $P_\eta$의 부호를 인증했다.

$$
z_a\in
\left[
\frac{981363616202660087}{10^{18}},
\frac{981363616202660088}{10^{18}}
\right],
$$

$$
z_b\in
\left[
\frac{1318839145395601812}{10^{18}},
\frac{1318839145395601813}{10^{18}}
\right].
$$

각 구간 끝의 제곱과 $E/k$를 정확한 유리수로 비교했고, 아래 부호가 성립했다.

| 에너지 | 8차 $P_\eta$ Bernstein 계수 | 결론 |
|---|---:|---|
| $13.61\ {\rm eV}$ | 9/9 양수 | $g(13.61)>0$ |
| $24.58\ {\rm eV}$ | 9/9 음수 | $g(24.58)<0$ |

연속성과 반대 끝점 부호로 내부 영점이 적어도 하나 존재한다. 두 영점 $u<v$가 있다고 가정하면 볼록함수의 할선 기울기 순서에 의해

$$
0=\frac{g(v)-g(u)}{v-u}
\le\frac{g(24.58)-g(v)}{24.58-v}<0
$$

가 되어 모순이다. 따라서 내부 영점은 정확히 하나다. 영점의 소수 자리나 수치 bracket은 이 곡률 기여에서 새로 계산하지 않았다.

## 5. 최초 실행과 재현 범위

- 코드: [exact_curvature_certificate.py](exact_curvature_certificate.py).
- 고정 절차: [PROTOCOL.json](PROTOCOL.json).
- 실행 전 코드·절차 해시: [PREEXECUTION_FROZEN.json](PREEXECUTION_FROZEN.json).
- 첫 실행: 20/20 PASS, 종료 코드 0, `stderr` 0 bytes.
- 결과 SHA-256: `48a301226276efa5ae42815358a9629a45f28a64ba0a8a553dc517f63913d552`.
- 과거 main 호출 0, PHYS19–23 증명 묶음 재실행 0, native 0, gas IVP 0, 대규모 수치 캠페인 0.

`--output`은 기존 파일을 덮어쓰지 않으며, 결과 JSON에는 실행 시각이나 절대 경로를 넣지 않았다. 실행 시각·명령·소요시간은 별도의 `EXECUTION.json`에 보존한다. 새 재현 호출은 같은 입력과 이 프로그램만 필요하며 외부 수치 라이브러리는 요구하지 않는다.

증명 보조 프로그램은 파이썬의 정확한 유리수 산술과 명시적인 다항식 계산을 사용한다. 증명 보조기의 신뢰 커널에서 형식 검증된 정리라는 주장은 아니다. 곡률의 입력 조건, 대수적 도출, 부호 인증 데이터와 변환 항등식은 모두 검토 가능한 형태로 남겼다.

## 유지되는 제한

이 기여는 초기시간의 $\epsilon^2t^4$ 계수에만 적용된다. 유한 시간·유한 $\epsilon$ 잔차, 실제 native 연산 동등성, 전체 기체 이력 또는 물리 source 승인을 제공하지 않는다. `physical=HOLD`, `[160,161]=FAIL`, `tick=160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지하며 소스·기본값·runtime을 수정하지 않는다.
