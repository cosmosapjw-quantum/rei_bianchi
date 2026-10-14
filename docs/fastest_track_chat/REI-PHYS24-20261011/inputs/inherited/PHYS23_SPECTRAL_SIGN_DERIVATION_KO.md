# PHYS23 — HI Verner fit의 초기 spectral response 부호 증명

## 1. 결론과 증거의 범위

현재 pinned HI fit을 source binary64 상수의 exact-real 함수로 해석하면, HI만 직접 광이온화하는 열린 구간

\[
I=(E_{\mathrm{cut,HI}},E_{\mathrm{cut,HeI}})
=(\operatorname{f64}(13.60),\operatorname{f64}(24.59))\ {\rm eV}
\tag{S1}
\]

전체에서 초기 HII, 열에너지/H, \(T_*=50000\,\mathrm K\) 온도의 선도 \(\epsilon^2t^3\) 응답은 모두 엄격히 음수다. 각 response function의 영점 수는 0이다. 이 결론은 더 넓은 유리수 \(z\) 구간에서 수행한 exact polynomial sign certificate를 따른다.

추가로 signed heat curvature와 signed ionization curvature의 비

\[
r(E)=
\frac{\mathscr C[\lambda(E)(E-\chi)]}{\mathscr C\lambda(E)}
\tag{S2}
\]

는 \(I\)에서 엄격히 증가한다. 정확한 유리수 끝점값을 바깥쪽으로 반올림한 안전한 경계는

\[
\boxed{16.98<r(E)<68.33\ {\rm eV}.}
\tag{S3}
\]

따라서 이 구간의 어떠한 비영인 양의 photon-number spectrum도 \(T_*=50000\,\mathrm K\)에서 HII나 온도의 선도 부호를 양수로 바꾸지 못한다. 가정은 초기 gas state, source의 \(\epsilon\)-독립성, positive measure, threshold-separated support다. 일반 thermal criterion은 §5에 적었다.

근거 상태는 **derived + exact-arithmetic certificate implementation-verified**다. Proof-assistant kernel에서 형식화한 정리, native binary arithmetic와의 동등성, 유한시간 sign 또는 remainder certificate로 확대하지 않는다. 이 문서는 후보 유도·증명서 작성자의 contribution이며, 독립 최종 승격 판정은 통합 루프의 별도 reviewer가 맡는다.

## 2. 정의·상수·계승한 초기시간 식

입력 계약은 [PHYSICS_CONTRACT.json](../../PHYSICS_CONTRACT.json), SHA256
888eb11c8a53f828b0ed5d3a053d91dc4da671d727e49c519cb3110bb5b6d200이다. Source input commit은 e334866a4ac1be963f573c0b35182d25eb4d666b, scientific Rust src tree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이다.

실제 HI fit은 [atomic_provider.rs](../../inputs/pinned_source/rust/rei_microphysics/src/atomic_provider.rs)의 cross_section에서 읽었다. 이 구간에서 \(x=E/E_0>1\)이고 \(y=x\)이므로

\[
\sigma(E)=\sigma_0\,10^{-18}\,
(x-1)^2x^{P/2-11/2}(1+\sqrt{x/y_a})^{-P}\ {\rm cm}^2 ,
\tag{S4}
\]

\[
E_0=\operatorname{f64}(0.4298)\ {\rm eV},\qquad
y_a=\operatorname{f64}(32.88),\qquad
P=\operatorname{f64}(2.963),\qquad
\sigma_0=\operatorname{f64}(5.475\times10^4).
\tag{S5}
\]

여기서 \(\operatorname{f64}(s)\)는 decimal 표기의 binary64 literal을 **그대로 하나의 유리수로 해석**한다는 뜻이다. Native 연산마다 반올림하는 것을 재현한다는 뜻은 아니다. 증명서에는 각 상수를 numerator/denominator로 보존했다.

\[
\lambda(E)=c\,n_H(1-x_{\rm HII,*})\sigma(E)>0,\qquad
D=E\partial_E,\qquad
\mathscr C=D(D+3).
\tag{S6}
\]

Gas state를 고정한 spectral 미분이다. Metric signature는 \((-+++)\), 시간은 proper seconds, energy는 eV를 유지한다. \(c\)는 식 (S6)의 광속이고, 아래 \(H_c\)의 첨자 \(c\)는 별도 에너지 parameter다.

PHYS22의 닫힌 식을 재유도·재실행하지 않고 다음과 같이 소비한다.

\[
a_{3,x}(E)=\frac{qN_0}{45}\mathscr C\lambda(E),\qquad
a_{3,w}(E)=\frac{qN_0}{45}\mathscr C[\lambda(E)(E-\chi)],
\tag{S7}
\]

\[
\theta_3(E)=\frac{qN_0}{45}\frac{\mathcal A_T}{\Pi_*}
\mathscr C\{\lambda(E)[E-\chi-e_{\rm th,*}]\},
\quad
\mathcal A_T=\frac{2e_{\rm V}}{3k_B},\quad
e_{\rm th,*}=\frac{3k_BT_*}{2e_{\rm V}}.
\tag{S8}
\]

\(\chi=\operatorname{f64}(13.598434599702)\,\mathrm{eV}\)는 opacity cutoff와 다르다. 이는 [hhe_events.rs](../../inputs/pinned_source/rust/rei_microphysics/src/hhe_events.rs)의 physical threshold다. \(k_B=\operatorname{f64}(1.380649\times10^{-16})\,\mathrm{erg\,K^{-1}}\), \(e_{\rm V}=\operatorname{f64}(1.602176634\times10^{-12})\,\mathrm{erg/eV}\)는 [paired_history.rs](../../inputs/pinned_source/rust/rei_microphysics/examples/paired_history.rs)의 온도 변환과 일치하며

\[
e_{\rm th,*}\simeq6.462999946608883\ {\rm eV}.
\tag{S9}
\]

\(q=2\varsigma^2>0\)는 physical shear 제곱이며 \(a_3,\theta_3\)는 시간 \(t^3\) 자체의 계수다. 추가 factorial은 없다. \(N_0=0\) 또는 \(q=0\)인 퇴화 경우에는 이 선도 응답들이 0이다.

## 3. 유리함수 환원

\[
z=\sqrt{\frac{E}{E_0y_a}},\qquad
x=y_az^2,\qquad
D=\frac z2\frac{d}{dz}.
\tag{S10}
\]

식 (S4)을 로그 미분하면

\[
\begin{aligned}
\alpha:=D\ln\sigma
&=\frac{2x}{x-1}+\frac P2-\frac{11}{2}
-\frac{Pz}{2(1+z)}\\
&=-\frac72+\frac2{x-1}+\frac{P}{2(1+z)},\\
\beta:=D\alpha
&=-\frac{2x}{(x-1)^2}-\frac{Pz}{4(1+z)^2}.
\end{aligned}
\tag{S11}
\]

따라서

\[
\mathscr C\lambda=\lambda A,\qquad
A=\alpha^2+3\alpha+\beta.
\tag{S12}
\]

Energy parameter \(c\)를 고정하면 product rule로

\[
\mathscr C[\lambda(E)(E-c)]
=\lambda H_c,\qquad
H_c=(E-c)A+E(2\alpha+4).
\tag{S13}
\]

\(A\)는 무차원, \(H_c\)와 \(r=H_\chi/A\)는 eV다. HII, heat, \(T_*=50000\,\mathrm K\)의 부호는 각각 \(A,H_\chi,H_{\chi+e_{\rm th,*}}\)의 부호와 같다. \(\lambda\), \(qN_0/45\), \(\mathcal A_T/\Pi_*\)가 양수이기 때문이다.

이제 \(a=y_a,\ k=E_0y_a\)로 놓고

\[
B=az^2-1,\quad C=1+z,\quad G=BC,
\quad N=-7G+4C+PB
\tag{S14}
\]

를 정의한다. 이 \(B,C\)는 PHYS22의 shear tensor나 기체 injection matrix와 무관한 국소 다항식 기호다. 명시적으로

\[
N=-7az^3+(P-7)az^2+11z+11-P,\qquad
\alpha=\frac{N}{2G}.
\tag{S15}
\]

미분을 \(z\)에 대한 prime으로 쓰면

\[
\begin{aligned}
P_A&=N^2+6NG+z(N'G-NG'),\\
P_{H,c}&=(kz^2-c)P_A+4kz^2G(N+4G),\\
A&=\frac{P_A}{4G^2},\qquad
H_c=\frac{P_{H,c}}{4G^2}.
\end{aligned}
\tag{S16}
\]

\(P_A\)는 6차, \(P_{H,c}\)는 8차의 유리수 계수 다항식이다. \(P_Q=P_{H,\chi}\), \(P_T=P_{H,\chi+e_{\rm th,*}}\)로 표기하면

\[
r=\frac{P_Q}{P_A},\qquad
\frac{dr}{dE}=
\frac{P_R}{2kzP_A^2},\qquad
P_R=P'_QP_A-P_QP'_A.
\tag{S17}
\]

\(P_R\)는 13차다. \(\chi\)에 대한 constant shift는 \(r'\)에서 상쇄된다. 따라서 \(P_R\)의 양의 부호는 response ratio의 단조성에 직접 대응한다.

## 4. 구간 전체의 exact certificate

증명서가 사용하는 닫힌 유리수 구간은

\[
J=\left[\frac{49}{50},\frac{33}{25}\right].
\tag{S18}
\]

다음 부등식을 source 상수의 exact fractions로 검사했다.

\[
0<L<U,\qquad
kL^2<E_{\mathrm{cut,HI}}<E_{\mathrm{cut,HeI}}<kU^2,
\qquad aL^2-1>0,\qquad1+L>0.
\tag{S19}
\]

즉 physical 열린 구간 \(I\)의 모든 에너지는 \(z\in\operatorname{int}J\)에 대응하고 \(G>0\)이다. Primary compact interval \([13.61,24.58]\,\mathrm{eV}\)도 \(I\) 내부에 있다는 별도 exact check를 수행했다. \(J\)가 더 넓다는 사실은 fit의 **analytic continuation**에 대한 계산 편의이며 cutoff 아래에서 actual piecewise opacity를 바꾸는 처방이 아니다.

임의 \(n\)차 polynomial \(p\)에 대해 \(z=L+(U-L)t\)로 치환하여

\[
p(L+(U-L)t)=\sum_{j=0}^n a_jt^j
=\sum_{k=0}^n b_k\binom nk t^k(1-t)^{n-k},
\tag{S20}
\]

\[
b_k=\sum_{j=0}^k a_j\frac{\binom kj}{\binom nj}
\tag{S21}
\]

를 계산했다. Bernstein basis는 \(0\le t\le1\)에서 음이 아니고 합이 1이다. 따라서 모든 \(b_k<0\)이면 polynomial은 구간 전체에서 음수이며, 모든 \(b_k>0\)이면 전체에서 양수다. 이는 sample interpolation에 관한 가정이 필요 없는 부호 증명이다.

실제 결과는 다음과 같다.

| 다항식 | 차수 | 요구 부호를 가진 Bernstein 계수 | 결론 |
|---|---:|---:|---|
| \(P_A\) | 6 | 7/7 negative | \(A<0\) |
| \(P_Q\) | 8 | 9/9 negative | \(H_\chi<0\) |
| \(P_T\) | 8 | 9/9 negative | \(H_{\chi+e_{\rm th,*}}<0\) |
| \(P_R\) | 13 | 14/14 positive | \(dr/dE>0\) |

총 39개 coefficient에 대한 exact 부호가 일치했다. Basis conversion을 역으로 전개한 power coefficients가 원래의 affine polynomial과 일치하는지도 각각 exact equality로 검사했다. 인증에 tolerance, 수치 root finder, density scan, interval subdivision 선택은 쓰지 않았다.

정확한 power coefficients, Bernstein coefficients, domain endpoints와 denominator positivity의 유리수 근거는 [EXACT_SIGN_CERTIFICATE.json](EXACT_SIGN_CERTIFICATE.json)에 있다. 유리수 수열을 사람이 읽는 본문에 중복 복사하지 않고 machine-readable 증명서에 보존했다.

특히 \(r\)의 \(J\) 끝점은 유리수이므로 단조성과 식 (S19)로

\[
r(kL^2)<r(E)<r(kU^2)
\tag{S22}
\]

를 얻는다. 양 끝점의 표시용 근사값은 각각 \(16.984193187340512\), \(68.32314439642778\) eV다. 정확한 경계는 JSON의 fractions이고, 식 (S3)은 그보다 넓은 안전한 반올림이다. 이 하한이 \(e_{\rm th,*}\)보다 크다는 exact comparison도 검사했다.

### 짧은 부등식 증명

Bernstein certificate와 별개로, 부호의 물리적 이유를 보기 위한 elementary bound도 쓸 수 있다. \(z\in J\)에서
\(x>31,\ P<3,\ P>1+z\)이므로

\[
-3<\alpha<
-\frac72+\frac1{15}+\frac{25}{33}
<-\frac83<-\frac52.
\tag{S23}
\]

또한 \(x/(x-1)^2\)는 \(x>1\)에서 감소하고 \(z/(1+z)^2\le1/4\)이므로

\[
0<-\beta<
\frac{62}{900}+\frac3{16}
=\frac{923}{3600}<\frac13.
\tag{S24}
\]

따라서

\[
A<0,\qquad 0<-A<\frac54+\frac13=\frac{19}{12},
\qquad -(2\alpha+4)>1.
\tag{S25}
\]

Physical \(E>\chi\)를 사용하면

\[
r=(E-\chi)+
E\,\frac{-(2\alpha+4)}{-A}
>\frac{12E}{19}>
8.58\ {\rm eV}>
e_{\rm th,*}.
\tag{S26}
\]

이것만으로도 heat와 50000 K temperature가 음수라는 결론은 얻는다. 부등식 (S23)–(S26)은 analytic explanation이며 별도 수치 test count를 추가하지 않는다. 구간 전체의 \(r'>0\)와 더 강한 범위 (S3)는 위 polynomial certificate의 결과다.

## 5. Positive spectrum으로의 연결

PHYS22의 선형 initial response map에서 양의 finite measure \(d\nu_0(E)\)를 사용하면 \(N_0=\int_I d\nu_0>0\)이고

\[
a_{3,x}=\frac q{45}\int_I\lambda A\,d\nu_0,\quad
a_{3,w}=\frac q{45}\int_I\lambda A\,r\,d\nu_0,
\tag{S27}
\]

\[
\theta_3=\frac q{45}\frac{\mathcal A_T}{\Pi_*}
\int_I\lambda A(r-e_{\rm th,*})\,d\nu_0.
\tag{S28}
\]

즉 response ratio는 단순 photon-number average와 다르고

\[
dW(E)=\frac{-\lambda(E)A(E)\,d\nu_0(E)}
{\int_I-\lambda A\,d\nu_0},\qquad
\bar r_W=\int_I r\,dW
\tag{S29}
\]

를 사용하여

\[
a_{3,w}=a_{3,x}\bar r_W,\qquad
\theta_3=
\frac{\mathcal A_T}{\Pi_*}a_{3,x}
(\bar r_W-e_{\rm th,*})
\tag{S30}
\]

로 쓸 수 있다. \(dW\)는 양의 확률 measure다. 그러므로 식 (S3)의 bounds가 그대로 \(\bar r_W\)에도 적용되고 \(a_{3,x}<0,\ a_{3,w}<0,\ \theta_3<0\)가 따른다.

여기서 \(D\)는 각 에너지에서 \(\lambda\)와 event/heat observable에 작용한다. Spectrum density를 미분하거나 적분 부분적분으로 threshold boundary term을 도입한 것이 아니다. Compact threshold-separated support에서는 초기시간 전개와 적분의 교환에 필요한 local regularity를 유지할 수 있다. 열린 구간의 끝점에 축적되는 measure에 대해 이 교환을 아무 추가 조건 없이 자동 정당화하지 않는다.

일반 초기 온도를 형식적으로 비교할 때 thermal sign condition은
\(e_{\rm th}<\bar r_W\)이면 음수, 같으면 0, 크면 양수다. 그러나 PHYS23의 실제 state는 \(T_*=50000\,\mathrm K\)로 고정되어 있고, 온도 변경을 production initial state 변경으로 수행하지 않았다.

\(r(E)\)는 signed response coefficients의 비다. 실제 한 photoionization event의 excess energy \(E-\chi\)와 같지 않으며, 그보다 큰 값을 “한 사건당 가열량”으로 해석하면 안 된다.

## 6. 실행·재현·정지

재현 시 phys23 디렉터리에서 다음처럼 fresh output path를 사용한다.

    python3 -B contributions/signs/exact_sign_certificate.py \
      --output /tmp/PHYS23_EXACT_SIGN_CERTIFICATE_FRESH.json

최초 실제 command, Python version, tool command identity, 출력·코드 SHA256, 실패 분류는 [EXECUTION.json](EXECUTION.json)에 있다. 프로그램은 기존 결과를 덮어쓰지 않도록 fresh output path만 허용하며 Python 표준 library의 fractions.Fraction만 사용한다.

최초 exact certificate 실행은 **31/31 PASS, exit 0**이었다. 내용은 contract identity, 상수와 domain 및 denominator, log-slope bound, polynomial identity, 네 polynomial의 exact sign 및 basis conversion, ratio/thermal-cost 비교, 네 rational point에서 독립적으로 쓴 log-slope·product-rule 식과 polynomial의 exact 일치를 포함한다. 최초 scientific failure는 없고 tolerance 변경이나 certificate 재실행도 없었다. 선행 7-point float preview는 경로를 정하는 탐색이었으며 영점 부재 증거나 독립 검증 수에 포함하지 않는다.

이 contribution은 native history 0회, gas IVP 0회, PHYS22 및 그 이전 닫힌 suite 0회로 완료했다. Exact certificate와 그 설명을 생성·검산한 같은 실행자를 독립 최종 reviewer로 부르지 않는다. H/T spectral sign과 ratio monotonicity에 대한 필요한 증거가 확보되어 이 contribution의 추가 검산은 종료한다. He의 간접 응답에 대한 threshold 연결과 spectrum normalization에 따른 수치 예시는 통합 실행자의 별도 PHYS23 산출물 범위다.

Protection은 physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED로 유지한다. 이 부호 정리는 prescribed geometry의 국소 초기시간 응답에만 적용하며 Einstein backreaction, finite-time gas trajectory, cutoff crossing 이후 응답을 해결한 결과가 아니다.
