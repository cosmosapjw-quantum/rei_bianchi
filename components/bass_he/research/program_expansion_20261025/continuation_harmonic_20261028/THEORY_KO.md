# HARMONIC10 S03 — R3/C3 구성적 정리와 인증 알고리즘

## 1. 정리의 대상

고정된 선언값 \(A=m_\alpha c^2,\ M=m_dc^2,\ e=E_\gamma\)에 대해
\(s=A^2+2Ae,\ H=s-4M^2>0,\ G=A+e,\ R=H/s\)라 둔다.
\(A,M,e\)는 energy이고 \(c,\hbar,k_B=1\)이라는 설정은 하지 않는다.
실수의 저장 표현을 exact rational로 읽는 것은 실제 질량·에너지 불확실성의 인증이 아니다.

CM 방향의 \(\mu\in[-1,1]\), 방위각 turns \(t=\phi/(2\pi)\in[0,1)\)에서
\[
F(\mu)=\frac{e+G\sqrt R\,\mu}
{\sqrt{(e+G\sqrt R\,\mu)^2+H(1-\mu^2)}}.
\]
기존 KINEMATIC08의 퇴화점·역상 branch 계약을 그대로 따른다.
같은 사건 두 딸의 방향은 \((F(\mu),t)\), \((F(-\mu),t+1/2\bmod1)\)이다.
Detector A,B는 각각 최대8개 polar-window×azimuth-arc patch의 union이다.
원·반사된 모든 patch endpoint로 분할한 strip마다 azimuth membership은 상수다.

이번 법칙은
\[
dm=q(\mu,t)d\mu dt,\quad
q=\rho_0(\mu)+\rho_c(\mu)\cos4\pi t+\rho_s(\mu)\sin4\pi t
\]
이며 \(\rho_j=\sum_{i=0}^{n}b_{j,i}B_i^n((\mu+1)/2)\), \(0\le n\le8\)다.
세 배열은 길이가 같고 \(b_{j,i}=b_{j,n-i}\)다. 입력은 정확하게
\[
b_{0,i}\ge0,\qquad b_{0,i}^2\ge b_{c,i}^2+b_{s,i}^2
\]
를 만족해야 한다. API tag SECOND_HARMONIC_DECLARED를 명시한다.
실제 실험 분포·절대 DCS·polarization fit을 입력했다고 해석하지 않는다.

## 2. 비음수 측도와 정규화

각 계수에서 Cauchy–Schwarz에 의해
\[
b_{0,i}+b_{c,i}\cos4\pi t+b_{s,i}\sin4\pi t
\ge b_{0,i}-\sqrt{b_{c,i}^2+b_{s,i}^2}\ge0.
\]
Bernstein basis는 비음수 partition of unity이므로 \(q\ge0\)다.
\(\sqrt{\rho_c^2+\rho_s^2}\le\rho_0\)도 triangle inequality로 따른다.
특히 \(|\rho_c|,|\rho_s|\le\rho_0\)이고
\(q\le B=2B_0,\ B_0=\max_i b_{0,i}\)다.
Harmonic 계수가 모두0이면 \(B=B_0\)로 좁힌다.

Full-turn sine/cosine 평균이0이고
\(\int_{-1}^1 B_i^n((\mu+1)/2)d\mu=2/(n+1)\)이므로
\[
\sigma=\int dm=\frac{2}{n+1}\sum_i b_{0,i}.
\]
\(\sigma=0\)이면 각 \(b_{0,i}=0\), cone에 따라 모든 harmonic 계수도0이다.

이 coefficient cone은 **충분조건**이다. 필요조건이나 양성 다항식의 완전한 판정기가 아니다.
예를 들어 \(b_0=(1,0,1),b_c=(0,1/2,0),b_s=0\)이면
\(\rho_0-|\rho_c|=(1+3\mu^2)/4>0\)이나 가운데 coefficient cone은 실패한다.
API는 이 입력을 certificate-domain 밖으로 거절하며 양성 불가능이라고 결론내리지 않는다.

## 3. 같은 사건의 Boolean 기하

\(A_+,A_-,B_+,B_-\)를 각 딸의 detector membership라 하자.
\[
Q_1=A_+\cap B_-,\quad Q_2=A_-\cap B_+,\quad C=Q_1\cup Q_2.
\]
Coincidence \(C\)는 서로 다른 두 딸이 A/B에 배정될 수 있는 사건이다.
한 딸이 겹치는 두 detector에 함께 들어간다고 \(C\)로 세지 않는다.
\(H_A=A_+\cup A_-\), \(H_B=B_+\cup B_-\)이고
both_detectors_hit=\(H_A\cap H_B\)는 별도 결과다.
assignment_overlap=\(Q_1\cap Q_2\), assignment count는
\(m(Q_1)+m(Q_2)=m(C)+m(Q_1\cap Q_2)\)다.

겹친 patch는 union하며 wrap-around arc는 원 위에서 분할한다.
Boundary는 연속 측도에서 measure0이므로 endpoint 중복은 결과를 바꾸지 않는다.
At most16 active patches의 original 및 half-shifted arc endpoint에0,1을 더해
strip 수 \(P\le65\)다. Strip midpoint는 azimuth의 상수 membership만 선택한다.
\(\mu\) integration의 numerical quadrature나 independent-event sampling이 아니다.

각 strip의 모든 Boolean event \(E\)에 대해 inherited exact set algebra가
\(E^-\subseteq E\subseteq E^+\)인 \(\mu\)-interval unions를 준다.
원 polar inverse enclosure와 \(\mu\mapsto-\mu\) 반사를 동일 사건에서 공유한다.
신규 measure에 기존 uniform numerical response를 대신 사용하지 않는다.

## 4. Signed primitive와 outward 계산

\[
A_j(E)=\int_E\rho_j(\mu)d\mu
\]
는 Bernstein basis를 exact rational power coefficients로 변환한 뒤 정확히 적분한다.
\(A_c,A_s\)는 음수일 수 있다. Strip \([l,h]\)에서
\[
I(E;l,h)=A_0(E)(h-l)+A_c(E)C(l,h)+A_s(E)S(l,h),
\]
\[
C(l,h)=\frac{\sin4\pi h-\sin4\pi l}{4\pi},\qquad
S(l,h)=\frac{\cos4\pi l-\cos4\pi h}{4\pi}.
\]

C,S는 아래 rational interval로 감싼다. Signed scalar 곱셈은 endpoint 방향을
정확히 처리하며 각 harmonic 성분을 개별적으로0 이상으로 clip하지 않는다.
각 strip에서 lower\(I(E^-)\), upper\(I(E^+)\)를 더하고 전체 event를 \([0,\sigma]\)와 교차한다.
결합 밀도 \(q\ge0\)에 의해 inner/outer set 포함이 적분 포함으로 이동한다.
이 마지막 clipping은 참값을 보존하고 폭을 늘리지 않는다.

### Rational trigonometric certificate

Machin 식
\[
\pi=16\arctan(1/5)-4\arctan(1/239)
\]
을 사용한다. \(\arctan x\) alternating series의24항·8항과 바로 다음 항을 양 끝으로 잡고
결과를 \(2^{-96}\) dyadic grid로 바깥 반올림한다.
\[
\operatorname{width}(\pi_I)<2^{-94}.
\]
Machin 식은 \(\tan(4\arctan(1/5)-\arctan(1/239))=1\)과 첫 사분면 범위로 직접 확인된다.

\(u=2t\bmod1,\ k=\lfloor4u\rfloor,\ r=u-k/4\in[0,1/4)\)로 phase를 줄인다.
\(x=2\pi_I r\)의 midpoint를 \(2^{-96}\) grid 아래쪽으로 옮긴 \(w\)를 쓰며
\(d_x=\max(|w-x_L|,|x_U-w|)<2^{-94}\), \(0\le w<2\)다.
\[
s_{20}=\sum_{j=0}^{19}\frac{(-1)^jw^{2j+1}}{(2j+1)!},\quad
c_{20}=\sum_{j=0}^{19}\frac{(-1)^jw^{2j}}{(2j)!}.
\]
Taylor remainder를 각각 \(2^{41}/41!\), \(2^{40}/40!\)로 감싸고
\(|\sin'|,|\cos'|\le1\)에 따라 \(d_x\)를 더한다.
\(2^{-88}\) grid로 outward round하고 \([-1,1]\)과 교차한다.
각 sine/cosine interval 폭은 \(2^{-86}\)보다 작다.
Quadrant는 exact 부호·swap으로 복원한다. \(r=0\)은 exact0,±1이다.

따라서 위 C,S의 실제 interval 폭은 각각 \(2^{-84}\) 이하다.
양의 denominator \(4\pi_I>12\)를 사용하며 참값의 포함과 폭을 코드에서 확인한다.
\(2(h-l)\)가 정수인 zero/half/full-turn strip은 endpoint interval dependency를
독립 차감하지 않고 **정확0**으로 반환한다. Production 경로의 float sin/cos 호출은 없다.

## 5. 전체 경계와 기본 tolerance

Inherited 한 polar window의 불확실 \(\mu\)-길이는 \(5\delta\) 이하다.
At most \(N\le8\)개의 서로 다른 active window와 reflected counterpart가 있으므로
모든 strip을 합친 event 불확실 면적 \(a_E\le10N\delta\)다.
실제 geometry gap의 질량은 \(B a_E\) 이하이다.

한 strip에서 사용한 inner·outer 적분 interval의 실제 폭을 더해 \(a_{\rm num}\)이라 한다.
\(|A_c(E)|,|A_s(E)|\le\sigma\)이므로
\[
a_{\rm num}\le4\sigma P\,2^{-84}.
\]
반환 구간의 실제 폭 \(w_E=U_E-L_E\)는
\[
w_E\le B a_E+a_{\rm num}
\le10NB\delta+4\sigma P2^{-84}.
\]
첫 부등식은 geometry gap에 lower/upper arithmetic slack을 더한 것이다.
Signed component의 부분 폭을 물리 event mass로 해석하지 않는다.

기본 선택은
\[
\delta=\frac{\sigma}{20NB\,2^{40}}
\]
이며 zero measure 또는 active window가 없을 때는 exact shortcut을 사용한다.
그때 Boolean event에 대해
\[
w_E\le\sigma(2^{-41}+260\,2^{-84})<\sigma2^{-40}.
\]
이 보장은 **기본 delta의 Boolean event 질량**에 대한 것이다.
수동 delta에는 반환한 actual width/width_bound를 사용한다.
입자 수와 energy는 해당 scale을 곱하며 conditional ratio는 별도 denominator 경계를 따른다.

\(B/\sigma\le n+1\le9\)이므로 \(\delta\ge1/(1440\,2^{40})\).
길이2인 bracket은 최대52회 이분이면 이 길이에 도달한다.
이는 각 bracket의 유한 횟수 보장이다. 임의로 큰 rational bit length에 대한
보편 walltime 보장이나 전체 descendant aggregate preemption 보장은 아니다.

## 6. 조건부 수용, 입자 수 및 에너지

\(C\subseteq H_A,H_B\)이므로 \(H_L>0\)이면
\[
P(C\mid H)\in
\left[\frac{Y_L}{H_U},\min\left(1,\frac{Y_U}{H_L}\right)\right].
\]
\(H_U=0\)이면 undefined/null,
\(H_L=0<H_U\)이면 unresolved/null로 반환한다.
작은 denominator에 무조건 epsilon을 보장하지 않는다.

짝대칭 계수와 half-turn 주기 때문에
\(J(\mu,t)=(-\mu,t+1/2)\) 아래 \(dm\)과 \(C\)가 불변이다.
따라서 \(\int_C\mu\,dm=0\).
\[
E_\pm(\mu)=\frac{G\pm e\sqrt R\,\mu}{2}
\]
를 적분하면
\[
N_{\rm selected}=2Y,\quad
E_{\rm pair}=GY,\quad
E_+=E_-=\frac G2Y.
\]
이 에너지에는 rest energy가 들어 있다. Thermal deposition이나 \(C_vT\)로
전환하는 응답·시간·species 결속은 이 정리에 없다.

## 7. 독립 기준식과 반례

### A. Full-polar antipodal arcs

\(\rho_0=1/2,\rho_c=\lambda/2,\rho_s=\kappa/2,\lambda^2+\kappa^2\le1\)이고
A arc \((a,w)\), B arc \((a+1/2,w)\), \(w\le1/2\)이면
\[
Y=2w+\lambda\frac{\sin4\pi(a+w)-\sin4\pi a}{2\pi}
+\kappa\frac{\cos4\pi a-\cos4\pi(a+w)}{2\pi}.
\]
\(w=1/8\)에서는
\[
Y=\frac14+\frac{(\lambda+\kappa)\cos4\pi a+(\kappa-\lambda)\sin4\pi a}{2\pi}.
\]
\((\lambda,\kappa)=(3/5,4/5)\)는 positivity cone 경계이며 방향 변화를 확실히 드러낸다.

### B. 비분리 polar–azimuth 법칙

\(b_0=(1/2,1/2,1/2),b_c=(1/2,-1/2,1/2),b_s=0\)이면
\(\rho_0=1/2,\rho_c=\mu^2/2\)다.
Full polar antipodal eighth-turn arcs는 \(Y=1/4+1/(6\pi)\).

더 강한 검사는 \(A=3,M=2,e=8/3\), \(k=40/51\)인 모델이다.
Forward A polar \([0,1]\)/arc \((0,1/8)\),
backward B polar \([-1,0]\)/arc \((1/2,1/8)\)에 대해
\[
Y=\frac{1-k}{8}+\frac{1-k^3}{12\pi},\quad
H_A=\frac{1+k}{8}+\frac{1+k^3}{12\pi},\quad H_B=Y.
\]
이는 두 assignment의 \(\mu\)-구간 \([k,1]\), \([-1,-k]\)를 직접 적분한 식이다.
Global marginal modulation \(1/3\)으로 대체한 분리화 결과와 차이는
\((k-k^3)/(12\pi)>0\)다. 따라서 단순 azimuth 비율 곱셈이 일반해가 아님을
구체적인 허용 입력으로 보인다. 모든 물리 모델에 대한 strong no-go는 아니다.

### C. 회전·중첩·고차 경계

Geometry를 a turns 회전하면 원 geometry 위의 effective coefficients는
\[
b'_c=b_c\cos4\pi a+b_s\sin4\pi a,\quad
b'_s=-b_c\sin4\pi a+b_s\cos4\pi a.
\]
\(a=1/8\)이면 \((b_s,-b_c)\)다. 법칙과 geometry를 함께 회전할 때는 역변환을 쓴다.
Full identical detector는 \(Y=\sigma,\ assignment=2\sigma,\ overlap=\sigma\).
동일 half-circle detector는 \(Y=0,\ both\_detectors\_hit=\sigma\).

Degree8 입력 \(b_{0,i}=1/2,b_{c,i}=(-1)^i/2,b_s=0\)는 \(\rho_c=\mu^8/2\)다.
계약의 서로 다른8개 내부 polar windows에서는 actual nonzero boundary bisection을 요구한다.
이 검사는 이전 AZIMUTH09의 boundary-iteration0 예를 소급해서 개선한 것으로 기록하지 않는다.

## 8. 채택 범위

증명은 고정 저장 parameter, 연속 측도, cone-certified even degree≤8 법칙,
명시적 finite detector union과 exact/outward arithmetic에 한정된다.
원 M0475002 정규화, liquid-He electron/target motion/response,
실제 DCS/편극 계수·flux/history·thermalization/global species binding은 열린다.

Binding 소유자는 population_rest_energy_witness 하나다.
Independent binding RHS, Gamma_thermal, Cv, species_heating, thermal_deposition은 null,
birth_pool=UNASSIGNED, global physical completion=null, L4=false,
production=NOT_APPROVED다.

이 단계는 이론·알고리즘 산출물이다. 실제 한 suite, 한 CAS, 저장값 plot과 독립 결과 검토
후에만 새 reference를 complete_scoped로 채택한다. **현재9/14 · 중앙28/88**.
