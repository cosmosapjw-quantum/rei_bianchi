# PHYS32 — 정확한 같은 수준, 근 조건과 사차 계수의 오차 전파

기여자: /root/phys32_conditioning. NONBLIND 조건 분석·직접 유도 역할이며 최종 decision reviewer가 아니다. 같은 GPT-6 Astra Pro, 호스트, 부모 맥락과 입력 계보를 공유한다. 독립 물리 데이터 credit은 0이다.

현재 PHYS32 실행 계약과 Astra research v4.0.0 핵심 10파일을 실제 읽었다. 이 역할의 새 물리 커널·도함수·근·quadrature·toy 평가, 과학 main, 과거 과학 코드 import/main/replay는 모두 **0**이다. 문서 작성과 읽은 파일의 byte identity 기록만 수행한다. 실제 수치 검사는 owner의 별도 고정 프로토콜과 실행 증거에 속한다.

## 1. 결론과 근거의 층위

**Derived, conditional.** 저장된 사차 계수에 유한 폭의 부호를 붙이려면, 정확히 같은 수준 \(A_j\)의 기준근, 그 근을 포함하는 기울기 하한, 저장 노드와 이상적 중심 사이의 거리, \(k^{(4)}\) 값과 변화량의 상계가 필요하다. 아래 식은 각각의 오차가 계수·유한 폭 문턱 차이·두 분지 간격으로 전달되는 방법을 명시한다. 실제 물리 수치 상계는 이번 계약에서 평가하지 않는다.

**Derived, fixed-source interpretation.** 고정 source binary64 상수를 정확한 실수로 읽고 저장 \(J\)를 고정한 커널은 선택 지지 구간의 열린 근방에서 해석적이다. 이는 필요한 도함수와 연속성 모듈러스의 존재를 준다. 그 상계의 숫자, 실제 원자 fit의 도함수 정확도, native floating-point 반환 사상의 미분가능성을 주지는 않는다.

**Derived, exact special-pair identity.** PHYS31의 \(P_4\) 프로파일과 균일 프로파일 사이에는 양의 사차 적분 커널이 있다. 따라서 관련 광자 지지 전체에서 \(k^{(4)}>0\), 양의 근 기울기와 같은 수준의 두 근 존재가 별도로 증명되면, 양의 유한 폭에서 \(W_p<W_u\)를 직접 결론 낼 수 있다. 이 조건은 이번 물리 소스에서 수치 인증되지 않았다. 두 분지 각각의 순서는 두 분지 간격 차이의 부호를 결정하지 않는다.

전체 나머지 \(\mathcal R_j\), 움직이는 중심과 끝점, root tube의 직접 유도는 별도 [이론 기여](../theory/QUANTITATIVE_REMAINDER_KO.md)에 속한다. 본문 §5는 그러한 정확한 정리에 입력 오차를 접합하는 식이다. 이 문서에서 \(\mathcal R_j\)의 수치값이나 검증 성공을 추정하지 않는다.

## 2. 실제 소스가 정의하는 세 가지 대상

다음 세 대상을 구별한다.

| 대상 | 이번에 사용할 수 있는 근거 | 그 자체로 제공하지 않는 것 |
|---|---|---|
| 정확한 고정 실수 모델 \(k_0\) | pinned source 식, source binary64 리터럴의 정확 실수 해석, 고정 직렬화 \(J\) | 원 \(J\), 원자 fit·기체 상태의 물리 불확실성 |
| 유한 산술 평가 \(\widehat k,\widehat C,\widehat D_4\) | PHYS31 저장값과 두 표현의 실제 일치 기록 | 엄밀한 평가오차 enclosure, 정확한 근·노드 enclosure |
| 불확실한 물리 입력 또는 다른 참조 모델 \(k_*\) | 별도 입력 범위와 모델 오차가 주어질 때의 조건부 전파식 | 현재 미제공 입력 범위나 실험적 물리 정확도 |

직접 읽은 pinned source에서 H I fit은

\[
\sigma_{\rm HI}(E)=\sigma_0 A_{\rm cm^2}(x-1)^2
x^{P/2-5.5}\left(1+\sqrt{x/y_a}\right)^{-P},
\qquad x=E/E_0
\tag{CS32.1}
\]

이다. H I cutoff는 source 13.60 eV, He I cutoff는 24.59 eV이고, H I binding energy \(\chi\)는 별도의 source 13.598434599702 eV다. 연구 지지 \([13.61,24.58]\) eV는 cutoff 사이의 한 분기 안에 있다. 실제 읽은 범위는 atomic_provider.rs 290–375행 중 cross_section 함수 전체, coupled_primary.rs 1–130행의 CHI와 absorber 호출이다. PHYS31 source manifest와 현 계약의 source subtree는 같으며, 현재 원격 head 확인은 owner가 수행했다. 이 역할이 별도 원격 fetch를 했다는 뜻은 아니다.

선행 실제 식은

\[
\phi(E)=\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)],
\quad D=E\partial_E,\quad
k_0(E)=K(D^2+3D)\phi(E),
\tag{CS32.2}
\]

\[
K=\frac{qN_0c_{\rm light}n_H(1-x_{\rm HII})}{180}.
\]

여기서 \(E\)는 eV, \(k\)는 s\(^{-4}\)다. \(c,\hbar,k_B\)를 자연단위로 바꾸지 않는다. 이 국소 커널 식에 \(\hbar,k_B\)를 새로 도입하거나 제거하지 않으며, 기본 metric convention은 \((-+++)\)다.

source binary64 리터럴의 정확 실수 값과 인쇄된 짧은 십진 리터럴을 임의로 교체하지 않는다. \(J\)를 고정한 뒤 에너지 도함수를 취하며 \(J\)의 에너지 의존성을 새로 가정하지 않는다. 양의 기저의 실수 거듭제곱, 제곱근, 곱과 미분의 합성으로 \(k_0\)의 해석성이 따른다. 그러나 각 유한 차수 도함수의 상한이 존재한다는 사실과 **확인된 수치 상한을 알고 있다는 사실**은 다르다.

PHYS31 원시 결과 1–260행을 실제 읽었다. 여기에 네 저장 노드의 \(k^{(4)}\), 같은 비영 \(A_j\), \(C_j\), \(D_{4,j}\), gap 계수, shared Decimal primitives와 claim ceiling이 들어 있다. 원래 PHYS22 \(J\) 파일 또는 PHYS29 실행 전체를 이번 역할이 다시 읽거나 계산했다고 주장하지 않는다. 그 계보는 PHYS31의 실제 kernel_scope 입력 키 문서와 원시 결과의 input identity를 통해 확인했다.

### 2.1 입력 \(J\) 오차와 도함수 오차

다른 모든 입력과 \(\chi\)가 고정돼 있다면

\[
A_r(E)=\partial_E^r\{K(D^2+3D)\sigma(E)\},\qquad
B_r(E)=\partial_E^r\{K(D^2+3D)[(E-\chi)\sigma(E)]\}
\]

로 정의하여 정확히

\[
k^{(r)}(E;J_x,J_w)=A_r(E)J_x+B_r(E)J_w.
\]

따라서 \(|J_x^*-J_x^0|\le\varepsilon_{J_x}\),
\(|J_w^*-J_w^0|\le\varepsilon_{J_w}\)와 구간 \(I\)의 인증 상계가 주어지면

\[
\boxed{\varepsilon_r^{\rm input}
 :=\|k_*^{(r)}-k_0^{(r)}\|_{\infty,I}
 \le \|A_r\|_{\infty,I}\varepsilon_{J_x}
       +\|B_r\|_{\infty,I}\varepsilon_{J_w}.}
\tag{CS32.3}
\]

이는 상관관계가 있어도 안전한 직사각형 상계다. 각 항의 단위는 s\(^{-4}\) eV\(^{-r}\)이며 서로 다른 \(J\) 성분의 단위를 같은 것으로 가정하지 않는다. 위 \(A_r,B_r\)는 kernel 의존성을 분리하는 함수이며, 분지의 목표 수준 \(A_j\)와 다른 기호다. 여기의 norm이나 \(\varepsilon_J\)는 평가되지 않았다.

다른 매개변수 \(\theta_\ell\)가 함께 변하면, 같은 매끄러운 source 분기 안의 매개변수 선분 \(\Theta\)에서

\[
\varepsilon_r^{\rm input}
\le \sum_\ell
\sup_{E\in I,\,\theta\in\Theta}
|\partial_{\theta_\ell}k^{(r)}(E;\theta)|\,
\varepsilon_{\theta_\ell}
\tag{CS32.4}
\]

라는 충분조건을 쓸 수 있다. 이 부등식은 해당 도함수 상계와 \(\Theta\)가 실제 주어질 때 적용한다. cutoff를 넘는 모델 가족에 현재 한 분기 식을 그대로 적용하지 않는다. 실제 원자 모델 차이가 이 매개변수 가족으로 설명된다는 가정도 새로 만들지 않는다.

에너지 값만의 fit 오차는 고차 커널 오차를 보장하지 않는다. 직접 곱미분하면

\[
\boxed{k^{(r)}=
K\{E^2\phi^{(r+2)}+(2r+4)E\phi^{(r+1)}
       +r(r+3)\phi^{(r)}\}.}
\tag{CS32.5}
\]

즉 \(k^{(4)}\)의 제어에는 \(\phi\)의 6차까지, \(k^{(5)}\)의 제어에는 7차까지의 정보가 필요하다. 함수값의 작은 오차만으로 높은 도함수 오차를 제어할 수 없다는 것은 작은 진폭·짧은 파장의 매끄러운 교란을 생각해도 확인된다. 물리 fit의 값 정확도와 사차·오차 상계의 정확도를 같은 수치로 대체하지 않는다.

## 3. 정확한 같은 수준과 저장근의 관계

분지 \(j\)를 고정하고 아래에서는 첨자를 생략한다. \(s=\pm1\), \(R=L\) 또는 \(H\), \(e=m-sR\)이며

\[
F(0,W)=p(W)k(e)+[1-p(W)]k(x(W)),\quad
p(W)=\frac{W}{R^2+W},\quad x(W)=m+\frac{sW}{R}.
\]

정확한 목표 수준 \(A\)의 기준근 \(w\)는 \(F(0,w)=A\)를 만족해야 한다. 저장 문자열 \(\widehat w\), 저장 응답 \(\widehat A\), 저장 기울기 \(\widehat C\)가 존재하는 것만으로 이 등식이 exact-real 의미에서 인증되지는 않는다.

두 서로 다른 선택을 분리한다.

1. **정해진 수준 유지:** 주어진 비영 \(A\)를 정확한 목표로 유지하고 \(\widehat w\)의 잔차를 enclosure한다. 본 연구의 정리를 수치 데이터에 적용할 때 필요한 경로다.
2. **새로운 anchor 정의:** \(A_{\rm anchor}:=F(0,\widehat w)\)라고 정확히 정의하면 \(\widehat w\)가 그 새 수준의 정확근인 것은 항등식이다. 그러나 그 값이 기존 \(A\)와 같다는 근거 없이 이 정의로 바꾸면 목표 수준을 바꾼 것이다. 저장 잔차를 0으로 덮어쓰는 방식으로 사용할 수 없다.

유한 문자열 \(A\)를 정확한 십진 목표로 정의할 경우 그 **정의 자체의 표현 오차**는 0이다. 이는 원래 물리 수준의 불확실성이나 계산된 \(\widehat A\)와 이상적 \(F(0,\widehat w)\) 사이의 오차가 0이라는 뜻이 아니다.

### 3.1 잔차와 양의 기울기로 정확근을 enclosure

\(\widehat w-\eta\)부터 \(\widehat w+\eta\)까지 모두 허용되는 내부 분산이라고 하자. 그 구간에서

\[
F_W(0,W)\ge\kappa>0,\qquad
|F(0,\widehat w)-A|\le\varepsilon_r<\kappa\eta
\tag{CS32.6}
\]

가 **인증돼 있다면**, 양 끝의 응답은 각각 \(A\)보다 작고 크다. 중간값정리와 엄격한 단조성으로 이 구간 안의 유일근 \(w\)가 존재하며

\[
\boxed{|w-\widehat w|\le\varepsilon_w
 :=\frac{\varepsilon_r}{\kappa}.}
\tag{CS32.7}
\]

증명은 \(F(0,\widehat w+\eta)-A\ge-\varepsilon_r+\kappa\eta>0\), 반대 끝에서는 역부등식, 마지막으로 근과 \(\widehat w\) 사이 평균값정리를 적용하는 것이다. 따라서 잔차/기울기 식을 쓰기 전에 근의 존재를 이미 가정해야만 하는 순환이 없다.

만약 \(\widehat r\)가 계산된 잔차이고 그 산술·모델·목표 수준의 불확실성을 분리했다면 충분한 선택은

\[
\varepsilon_r=
|\widehat r|+\varepsilon_{F,{\rm eval}}
+\varepsilon_0^{\rm input}+\varepsilon_A.
\tag{CS32.8}
\]

고정 기하에서 \(F\)는 확률 평균이므로 함수값 입력 오차
\(\varepsilon_0^{\rm input}=\|k_*-k_0\|_\infty\)가 그대로 응답 오차의 상계다. \(\varepsilon_{F,{\rm eval}}\)에는 계산된 잔차를 해석할 때 필요한 평가·산술·기하 구현 오차가 포함돼야 한다. 입력 정의가 달라지면 그 의존성도 따로 추가한다.

같은 논증을 \(0\le\delta\le\delta_0\)의 root tube에 적용할 수 있다. 저장점에서의 이동을 직접
\(|F_\nu(\delta,\widehat w)-F_\nu(0,\widehat w)|\le\widehat B_\nu(\delta)\)로 감쌌다면, 그 저장점의 잔차 상계는 \(\widehat B_\nu+\varepsilon_r\)이고 충분한 근 이탈 상계는 \((\widehat B_\nu+\varepsilon_r)/\kappa\)다. 이 합이 \(\kappa\eta\)보다 작으면 저장점 중심의 같은 tube 안에 근이 존재한다. 정확한 \(w\)에서만 유도한 \(|F_\nu(\delta,w)-A|\le B_\nu(\delta)\)의 값을 추가 근거 없이 \(\widehat w\)에 재사용하지 않는다. 기하 bound를 저장점에서 다시 해석하거나 두 기준점 사이의 응답 차이를 따로 감싸야 한다.

비영 수준 \(A\)의 근과 영수준 근을 모두 포함하는 구간에서 같은 기울기 하한이 있으면 두 근의 거리는 \(|A|/\kappa\) 이하이다. 이 역시 두 근의 존재와 기울기 인증이 필요하다. 현재 작은 \(A\)를 0으로 치환할 근거가 아니다.

### 3.2 같은 수준을 잃으면 생기는 추가 항

두 프로파일의 실제 목표가 \(A_p,A_u\)로 다르면, 두 근 사이 평균 기울기를 \(\overline C_p>0\)라 할 때

\[
\boxed{W_p-W_u=
\frac{A_p-A_u-\Delta F(\delta,W_u)}{\overline C_p}.}
\tag{CS32.9}
\]

따라서 수준 차이 \(\Delta A\)는 \(|\Delta A|/\kappa\) 규모의 추가 근 오차를 만든다. 이 항은 \(\delta^4\)로 작아진다고 보장되지 않는다. 정확한 공통 \(A\)는 프로파일 차이의 사차 소거를 사용하는 실질적인 전제다.

분자 표현도 같은 수준을 유지해야 한다.

\[
Q=(R-\delta)^2+W-\mu_2\delta^2,\qquad
G_\nu=N_\nu-AQ.
\]

정확한 기준근에서만 \(G_W=N_W-A=QC\)를 사용할 수 있다. 임의 근사점에서는
\(G_W=QF_W+(F-A)\), \(Q_W=1\)이므로 잔차 항이 남는다. 이는 approximate base에서 분자와 normalized slope를 연결할 때 놓치기 쉬운 항이다. \(A\)를 분모에서 버리거나 근사점의 잔차를 0으로 가정하지 않는다.

## 4. 근·노드·입력 오차를 \(D_4\) 오차로 전달

### 4.1 내부 중심과 가중치

기하의 \(m,R\)가 정확히 고정됐다고 하자. 저장 내부 에너지 \(\widehat x\)와 저장 분산 \(\widehat w\) 사이의 반올림 불일치를

\[
\eta_x:=\left|\widehat x-\left(m+\frac{s\widehat w}{R}\right)\right|
\]

로 정의하면

\[
\boxed{|x(w)-\widehat x|
\le\varepsilon_x:=\frac{\varepsilon_w}{R}+\eta_x.}
\tag{CS32.10}
\]

\(\eta_x\)는 저장 문자열을 정확 유리수로 읽으면 직접 enclosure할 수 있는 양이다. 이번 역할은 이를 실제 평가하지 않았다. 더 높은 정밀도로 중심을 다시 만들었다고 해서 과거의 저장 노드가 같은 점으로 바뀌지 않는다. 끝점 \(e\)는 현재 고정 구간 정의의 정확한 값이지만, 별도 물리 에너지 불확실성이 있다면 아래에 \(\varepsilon_e\)로 추가해야 한다.

\(\widehat p\in[0,1]\), \(\widehat q=1-\widehat p\)인 정규화된 추정 가중치를 쓰자. \(\eta_p:=|\widehat p-p(\widehat w)|\)를 인증했다고 하고 \(w,\widehat w\ge w_{\min}>0\)이면

\[
\boxed{|p(w)-\widehat p|
\le\varepsilon_p:=\eta_p+
\frac{R^2\varepsilon_w}{(R^2+w_{\min})^2}.}
\tag{CS32.11}
\]

이는 \(p'(W)=R^2/(R^2+W)^2\)에서 따른다. 독립적으로 반올림된 \(p,q\)를 그대로 사용해 그 합이 1이 아니면 위 정규화 가정을 쓰지 말고 두 가중치 오차와 합의 오차를 따로 포함해야 한다.

### 4.2 점별 \(k^{(4)}\)와 가중합 오차

\[
\omega_r^0(h)=
\sup_{\substack{E,E'\in I\\|E-E'|\le h}}
|k_0^{(r)}(E)-k_0^{(r)}(E')|
\]

로 정의한다. 대상 \(k_*\)와 기준 \(k_0\) 사이
\(\|k_*^{(r)}-k_0^{(r)}\|_{\infty,I}\le\varepsilon_r^{\rm input}\)가 주어지고,
저장 점값 \(\widehat k_{4,e},\widehat k_{4,x}\)의 **인증된** 평가오차가
\(\varepsilon_{4,e}^{\rm eval},\varepsilon_{4,x}^{\rm eval}\)라면

\[
\varepsilon_{4,e}=
\varepsilon_{4,e}^{\rm eval}+\varepsilon_4^{\rm input}
+\omega_4^0(\varepsilon_e),\qquad
\varepsilon_{4,x}=
\varepsilon_{4,x}^{\rm eval}+\varepsilon_4^{\rm input}
+\omega_4^0(\varepsilon_x)
\tag{CS32.12}
\]

가 실제 끝점·내부 중심의 사차 도함수 오차를 각각 감싼다. \(k_0\in C^5\)와 인증 상계 \(M_5\ge\|k_0^{(5)}\|_\infty\)가 있으면 \(\omega_4^0(h)\le M_5h\)를 대입할 수 있다. 해석성만으로 \(M_5\)의 숫자를 얻지는 못한다.

\[
H=p\,k_*^{(4)}(e)+q\,k_*^{(4)}(x),\qquad
\widehat H=\widehat p\,\widehat k_{4,e}
+(1-\widehat p)\widehat k_{4,x}
\]

라 쓰면 정확히

\[
H-\widehat H=
p[k_*^{(4)}(e)-\widehat k_{4,e}]
+q[k_*^{(4)}(x)-\widehat k_{4,x}]
+(p-\widehat p)(\widehat k_{4,e}-\widehat k_{4,x})
\]

이므로 충분한 오차 상계는

\[
\boxed{\varepsilon_H
=\max(\varepsilon_{4,e},\varepsilon_{4,x})
+\varepsilon_p|\widehat k_{4,e}-\widehat k_{4,x}|
+\varepsilon_{H,{\rm asm}}.}
\tag{CS32.13}
\]

\(\varepsilon_{H,{\rm asm}}\)은 유한 산술로 \(\widehat H\)를 조립했다면 그 조립 오차다. 유리수로 정의된 추정량을 정확히 조립하는 별도 구현에서는 이 항을 정의에 의해 0으로 둘 수 있지만, 과거 Decimal 조립 오차를 그러한 구현 없이 0으로 선언할 수는 없다. 실제 \(p\)의 interval을 알면 max 대신 \(p\varepsilon_{4,e}+q\varepsilon_{4,x}\)의 interval 상한으로 개선할 수 있다.

### 4.3 기울기 오차와 하한

영폭의 기울기에는 나쁜 뺄셈을 피하는 적분 표현이 있다.

\[
C=F_W(0,w)
=\int_0^1 t\,k_*''(e+t(x-e))\,dt.
\tag{CS32.14}
\]

모든 관련 선분에서 \(k_*''\ge m_2>0\)가 인증되면 \(C\ge m_2/2\). 유한 폭에서도 평균 커널을 사용한 같은 표현으로 root tube의 \(\kappa=m_2/2\)를 얻는다. 여기의 \(m_2\)는 현재 숫자가 없는 조건부 상수다.

\(\widehat C\)가 nominal kernel와 저장 끝점·내부 중심으로 정의한 적분 표현의 추정값이고 그 평가오차가 \(\varepsilon_C^{\rm eval}\)라면

\[
\boxed{\varepsilon_C
=\varepsilon_C^{\rm eval}
+\frac12\varepsilon_2^{\rm input}
+\frac12\omega_2^0(\max(\varepsilon_e,\varepsilon_x))}
\tag{CS32.15}
\]

가 충분하다. 모든 interpolated energy의 차이가 \(\max(\varepsilon_e,\varepsilon_x)\) 이내이고 \(\int_0^1t\,dt=1/2\)이기 때문이다.

\(M_3\ge\|k_0'''\|_\infty\)가 인증됐으면 기하 항을 더 세밀하게

\[
\int_0^1 t\,M_3[(1-t)\varepsilon_e+t\varepsilon_x]dt
=M_3\left(\frac{\varepsilon_e}{6}+\frac{\varepsilon_x}{3}\right)
\tag{CS32.16}
\]

으로 쓸 수 있다. 끝점이 정확히 고정되고 노드 반올림이 없다면 기준근 오차가 기울기에 주는 항은 \(M_3\varepsilon_w/(3R)\) 이하이다.

PHYS31 두 표현의 일치 허용치나 출력 차이는
\(\varepsilon_{4,i}^{\rm eval},\varepsilon_C^{\rm eval}\)의 엄밀한 상계로 주어진 것이 아니다. 같은 입력과 초월함수를 공유한 계산의 상호 일치를 위 식의 enclosure에 직접 대입하지 않는다.

### 4.4 사차 계수의 절대 오차

\[
\alpha=\frac{\Delta\mu_4}{24},\qquad
D_4=-\frac{\alpha H}{C},\qquad
\widehat D_4=-\frac{\alpha\widehat H}{\widehat C}
\]

로 쓴다. 이 문제의 정확 프로파일 쌍에서는 \(\alpha=1/945\)이고 프로파일 모멘트 오차는 없다. \(C\ge\kappa>0\), \(\widehat C\ne0\)와 앞의 오차 상계가 주어지면

\[
\frac{H}{C}-\frac{\widehat H}{\widehat C}
=\frac{H-\widehat H}{C}
+\frac{\widehat H(\widehat C-C)}{C\widehat C}
\]

에서

\[
\boxed{|D_4-\widehat D_4|\le\varepsilon_D
:=
|\alpha|\left[
\frac{\varepsilon_H}{\kappa}
+\frac{|\widehat H|\varepsilon_C}{\kappa|\widehat C|}
\right]+\varepsilon_{D,{\rm asm}}.}
\tag{CS32.17}
\]

추정 기울기만으로 하한을 만드는 경우에는
\(\widehat C>\varepsilon_C\)를 실제 증명한 뒤
\(\kappa_C=\widehat C-\varepsilon_C>0\)를 정확한 **기준점 계수용 하한**으로 대입할 수 있다. 이것만으로 유한 폭 root tube 전체의 기울기 하한이 생기지는 않는다. 구간의 변화량을 별도로 포함해야 한다.

\(\widehat H\ne0,\widehat C>\varepsilon_C\)이고 조립 오차를 제외하면 상대 오차의 충분조건은

\[
\frac{|D_4-\widehat D_4|}{|\widehat D_4|}
\le
\frac{\varepsilon_H/|\widehat H|+\varepsilon_C/\widehat C}
     {1-\varepsilon_C/\widehat C}.
\tag{CS32.18}
\]

작은 기울기에는 \(1/C\)와 \(1/C^2\) 민감도가, 작은 \(H\)에는 상대 부호 불확실성이 나타난다. \(H=0\) 근방에서는 절대 오차 식을 사용해야 하며, 사차의 비영성이나 다음 차수가 짝수라는 결론을 추가하지 않는다. \(\widehat C-\varepsilon_C\le0\)이면 이 추정만으로 양의 수치 기울기를 인증하지 못한 것이고, 허용치를 바꿔 해결할 문제가 아니다.

## 5. 정량 나머지와 계수 오차를 결합한 부호·gap 조건

정확한 같은 \(A\)와 정확한 모델에 대해

\[
|\Delta W_j(\delta)-D_{4,j}\delta^4|
\le\delta^4\mathcal R_j(\delta)
\tag{CS32.19}
\]

가 증명됐다고 하자. 이론의 모든 root tube·support·기울기 전제를 만족하는 폭에서 CS32.17을 합치면

\[
\boxed{|\Delta W_j(\delta)-\widehat D_{4,j}\delta^4|
\le\delta^4[\mathcal R_j(\delta)+\varepsilon_{D,j}].}
\tag{CS32.20}
\]

따라서 \(0<\delta\le\delta_0\)에서

\[
|\widehat D_{4,j}|>
\varepsilon_{D,j}+\mathcal R_j(\delta)
\tag{CS32.21}
\]

가 성립하면 정확한 \(\Delta W_j\)의 부호가 \(\widehat D_{4,j}\)와 같다. 예를 들어
\(\widehat D_{4,j}+\varepsilon_{D,j}+\mathcal R_j(\delta)<0\)이면 \(W_{j,p}<W_{j,u}\)다. equality는 엄격한 부호 증명을 주지 않는다.

두 분지의 간격을 \(\Gamma_\nu=W_{0,\nu}-W_{*,\nu}\)라 하고
\(d_\Gamma=D_{4,0}-D_{4,*}\), 추정값을 \(\widehat d_\Gamma\)라 하면

\[
\varepsilon_\Gamma
\le\varepsilon_{D,0}+\varepsilon_{D,*}
+\varepsilon_{\Gamma,{\rm asm}},\qquad
\mathcal R_\Gamma=\mathcal R_0+\mathcal R_*
\]

가 안전한 상계이며

\[
\boxed{|\widehat d_\Gamma|>
\varepsilon_\Gamma+\mathcal R_\Gamma(\delta)}
\tag{CS32.22}
\]

가 정확한 \(\Gamma_p-\Gamma_u\)의 부호를 보장한다. 원 \(J\)와 다른 입력이 공통이라는 점을 이용한 더 작은 correlated bound를 별도로 증명할 수는 있다. 그러나 공유 입력 또는 같은 부호라는 사실만으로 두 branch 오차가 상쇄한다고 가정하지 않는다.

물리 입력 가족 전체에 결론을 확장하려면 \(\varepsilon_D,\mathcal R,\kappa\), root tube와 같은 \(A\) 조건이 그 가족 전체에 대해 균일하게 인증돼야 한다. 같은 입력이 두 프로파일에 공통으로 변하면 모멘트 소거 구조를 보존할 수 있으므로 모델 오차가 반드시 폭과 무관한 차이로 들어오는 것은 아니다. 반대로 프로파일마다 입력이나 수준을 독립적으로 바꾸면 같은 비교 정리를 그대로 적용할 수 없다.

직접 계산한 유한 폭 근의 차이를 사용할 경우에는 별도 잔차 인증으로
\(|W_\nu-\widehat W_\nu|\le\varepsilon_{W,\nu}\)를 얻어야 한다. 이때 차이의 오차는 최대
\(\varepsilon_{W,p}+\varepsilon_{W,u}\)다. \(\delta^4\) 신호와 비교하려면 이를 \(\delta^4\)로 나눈 항이 추가된다. 높은 자릿수 출력이나 동일 경로 replay만으로 이러한 직접 근 오차가 작다고 인증할 수는 없다.

## 6. 선택한 프로파일 쌍의 정확한 양의 적분 항등식

\([-1,1]\)에서

\[
h_p-h_u=\frac{35z^4-30z^2+3}{16},\qquad
P(z)=(1-z^2)^4
\]

로 둔다. 직접 네 번 미분하면

\[
P^{(4)}(z)=1680z^4-1440z^2+144
=48(35z^4-30z^2+3).
\]

그러므로 \(h_p-h_u=P^{(4)}/768\)이다. \(P\)가 \(z=\pm1\)에서 각각 4중 영점을 가지므로 \(P,P',P'',P'''\)는 양 끝에서 모두 0이다. \(k\in C^4\)이고 \(y+\delta[-1,1]\)이 실제 지지 안에 있으면, 네 번의 부분적분에서 모든 경계항이 사라져

\[
\Delta f_\delta(y)
=\frac{\delta^4}{768}\int_{-1}^1(1-z^2)^4
k^{(4)}(y+\delta z)\,dz.
\tag{CS32.23}
\]

또한 원시함수 계산으로

\[
\int_{-1}^1(1-z^2)^4dz
=2\left(1-\frac43+\frac65-\frac47+\frac19\right)
=\frac{256}{315}.
\]

따라서 양의 확률밀도

\[
\pi_4(z)=\frac{315}{256}(1-z^2)^4
\]

를 쓰면

\[
\boxed{\Delta f_\delta(y)
=\frac{\delta^4}{945}
\int_{-1}^1 k^{(4)}(y+\delta z)\pi_4(z)\,dz.}
\tag{CS32.24}
\]

이는 Taylor 절단이 아닌 모든 허용 폭의 정확한 항등식이다. 여기서 확률밀도 \(\pi_4\)는 root slope 하한 \(\kappa\)와 구별한다. \(\delta=0\)에서는 양변이 0이고, 물리 폭은 \(\delta\ge0\)로 제한한다.

두 프로파일의 actual \(W\), \(\mu_2=1/3\), 움직이는 중심과 비음수 확률이 같으므로 동일 \(W\)에서

\[
\Delta F(\delta,W)
=\frac{\delta^4}{945}\left[
p_{\delta,W}\mathbb E_{\pi_4}k^{(4)}(e_\delta+\delta Z)
+q_{\delta,W}\mathbb E_{\pi_4}k^{(4)}(x_{\delta,W}+\delta Z)
\right].
\tag{CS32.25}
\]

이는 exact \(V=W-\mu_2\delta^2\)를 사용한다. 같은 \(A\)의 두 근 사이 양의 평균 기울기로 나누면

\[
\Delta W=-\frac{\Delta F(\delta,W_u)}{\overline C_p}.
\tag{CS32.26}
\]

관련 photon support 전체에서 \(m_4\le k^{(4)}\le M_4\), \(m_4>0\)와
\(\kappa\le\overline C_p\le\overline K\)가 인증되면

\[
\boxed{-\frac{M_4}{945\kappa}\delta^4
\le \Delta W
\le-\frac{m_4}{945\overline K}\delta^4<0.}
\tag{CS32.27}
\]

상한 \(\overline K\)가 없더라도 \(\overline C_p>0\)와 \(k^{(4)}>0\)는 부호를 준다. \(k^{(4)}\ge0\)만 알면 비엄격한 순서 \(W_p\le W_u\)가 성립한다. 음의 \(k^{(4)}\)에는 반대 순서가 따른다. 이는 \(\Delta\mu_4\) 부호만으로 모든 커널·모든 프로파일을 순서화하는 정리가 아니다.

### 6.1 네 점의 부호를 필요한 구간으로 옮기는 조건

직접 순서에는 반드시 \([a,b]\) 전체의 \(k^{(4)}\) 부호가 필요한 것은 아니다. 고정 branch의 두 근이 인증된 tube 안에 있을 때, 실제 두 photon packet이 방문하는 구간의 합집합이면 충분하다.

예를 들어 기준근에서의 이탈이 \(|W-w|\le\rho(\delta)\), \(w>0\), \(R-\delta>0\)라면

\[
|x_{\delta,W}-x_{0,w}|
\le h_x(\delta):=
\frac{\rho(\delta)}{R-\delta}
+\frac{w\delta}{R(R-\delta)}
+\frac{\mu_2\delta^2}{R-\delta}.
\tag{CS32.28}
\]

끝점 packet은 기준 끝점 \(e\)에서 \(2\delta\) 이내, 내부 packet은 \(x_{0,w}\)에서 \(h_x(\delta)+\delta\) 이내에 있다. 저장 노드에 대한 비교에서는 §4의 \(\varepsilon_e,\varepsilon_x\)를 그 반경에 추가한다.

따라서 인증된 point evaluation error와 modulus가 있다면 각 packet에서

\[
k_*^{(4)}(E)\ge
\widehat k_{4,i}
-\varepsilon_{4,i}^{\rm eval}
-\varepsilon_4^{\rm input}
-\omega_4^0(r_i)
\tag{CS32.29}
\]

를 사용할 수 있다. 여기서 \(r_e=2\delta+\varepsilon_e\),
\(r_x=h_x(\delta)+\delta+\varepsilon_x\)가 충분하다. 오른쪽 하한 둘이 모두 양수라는 사실이 실제로 인증돼야 한다. 네 점에서 양의 숫자가 나왔다는 기존 기록은 이 modulus·반경·평가오차·root tube의 대체물이 아니다.

기울기 인증에 쓰는 \(k''\)의 구간은 두 중심을 잇는 선분과 profile shift를 포함해야 하므로 이 좁은 \(k^{(4)}\) packet 구간과 같다고 가정하면 안 된다. 국소 사차 부호 certificate와 slope certificate의 정의역을 따로 기록해야 한다.

## 7. 현재 남은 근거와 가장 작은 후속 단위

| 필요한 양 | 조건부 수학에서의 역할 | 현재 실제 상태 |
|---|---|---|
| 정확한 같은 \(A_j\), root box | 비교 대상을 유지하고 존재·유일성 보장 | 목표 유지; 저장점과 exact-real 등식의 수치 enclosure 미완료 |
| \(\varepsilon_r,\kappa\) | 정확근 위치, root tube, 안정적 나눗셈 | 물리 수치 상계 미평가 |
| \(\eta_x,\eta_p\) | 저장 노드·가중치와 이상 기하의 차이 | 전파식 유도; 새 값 평가 0 |
| \(\varepsilon_{4,i}^{\rm eval},\varepsilon_C^{\rm eval}\) | finite arithmetic를 exact model로 연결 | 두 표현 일치만 존재; rigor enclosure로 승격하지 않음 |
| \(\omega_2,\omega_4\) 또는 \(M_3,M_5\) | 노드 이동·폭 변화의 오차 | source-real 존재; 수치 bound 미평가 |
| 원 \(J\), 상태·원자 모델 불확실성 | fixed model 밖의 결론 | 입력 범위·도함수 오차 미제공 |
| \(\varepsilon_D,\mathcal R_j\) | 계수 기반 유한 폭 부호·gap | 조건부 공식; 물리 유효 폭 숫자 없음 |
| packet union의 \(k^{(4)}\) 부호 | 특수 쌍의 직접 유한 폭 순서 | 정확 항등식 유도; 실제 소스 구간 부호 미인증 |

**후속 최소 단위는 목적에 따라 구별한다.** 선택한 쌍의 finite-width branch 순서만 원한다면, 고정 폭 범위와 feasible root tube를 먼저 정한 뒤 동일 수준의 근 존재·기울기와 두 photon packet 구간의 \(k^{(4)}\) 부호를 인증하는 것으로 충분하다. CS32.24–27 덕분에 별도의 사차 근 나머지 수치값이 필수는 아니다. 반면 실제 사차 계수의 오차 또는 두 branch gap의 부호를 원한다면, 기준 계수 enclosure와 \(\mathcal R_0+\mathcal R_*\)의 정량 근거가 추가로 필요하다.

그 인증은 부등식을 보증하는 interval arithmetic·명시적 도함수 bound·분석적 부호 분해 같은 방법으로 수행해야 한다. 사용되는 초월함수도 포함한 바깥 반올림 근거와 정의역을 기록하고, 평가 대상·개수·중단 조건을 먼저 정한다. 조밀한 표본, 자릿수 증가, 저장값의 재현 일치를 enclosure로 이름만 바꾸지 않는다. 본 기여는 후속 프로그램·새 평가를 실행하거나 그 예산을 만들지 않는다.

PHYS31에서 보고한 두 음의 \(D_4\)와 양의 gap 계수는 그 저장 입력에서의 유한 산술 결과로 유지한다. 이번 문서는 그것을 확장할 정확한 조건을 제시했으며, 실제 물리 부호·안전한 \(\delta_0\)·기체 이력 admission을 새로 인증하지 않았다.

**유지 상태: Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0.**

## 8. 근거 포인터와 역할 한계

- [현재 계약](../../PHYSICS_CONTRACT.json): 새 physical evaluation 0, toy 실행은 별도 owner 역할, protected state.
- [실제 PHYS31 인수문](../../inputs/PHYS31/next/PHYS32_NEXT_HANDOFF_KO.md): 정량 나머지·conditioning의 미실행 목표와 상속 한계.
- [실제 PHYS31 최종 판정](../../inputs/PHYS31/independent/DECISION_REVIEW_KO.md): scope 채택, 원 root/J/node enclosure와 finite-width 부호의 미해결.
- [PHYS31 kernel 정칙성](../../inputs/PHYS31/contributions/kernel_scope/KERNEL_REGULARITY_AND_PROFILES_KO.md): K31.1–3, exact source-real 해석과 support.
- [PHYS31 입력과 두 표현](../../inputs/PHYS31/contributions/kernel_scope/INPUT_KEYS_AND_TWO_EXPRESSIONS_KO.md): 원 입력 key, source-real convention, 공유 의존성.
- [PHYS31 이론](../../inputs/PHYS31/contributions/theory/DERIVATION_KO.md): T31.10–12, 23–33을 포함한 실제 읽은 101–137, 244–376행.
- [PHYS31 원시 값](../../inputs/PHYS31/contributions/numerics/QUARTIC_PROFILE_FIRST.json): 실제 읽은 1–260행과 명시적 검색 범위. 전체 검사를 재독·재실행했다고 주장하지 않음.
- [읽기 기록](READ_MANIFEST.json) · [기여 provenance](PROVENANCE.json) · [주장 목록](CONDITIONING_CLAIMS.json).

외부 논문을 이 역할에서 직접 열람한 기록은 없다. 문헌상 최초성이나 원자 fit의 외부 정확도 주장을 하지 않는다. 위 수학식은 정의와 직접 미분·부분적분·평균값정리에서 유도한 조건부 결과이며, source와 선행 파일은 그 정의·적용 범위의 근거다. 최종 PROMOTE 권위는 별도 실제 reviewer와 owner의 후속 통합 절차에 있다.
