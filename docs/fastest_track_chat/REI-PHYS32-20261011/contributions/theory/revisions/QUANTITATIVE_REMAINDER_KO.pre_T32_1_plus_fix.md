# PHYS32 — 움직이는 공통 기하에서 사차 근 차이의 정량 나머지

연구 기여: **REI-PHYS32-20261011 · QUARTIC_SPLITTING_REMAINDER_AND_CONDITIONING**.  
기여자: /root/phys32_theory. 상태: **조건부 직접 유도 후보 완성, 별도 최종 판정 대기**.  
역할: 같은 호스트·상속 GPT-6 Astra Pro·부모 대화 문맥을 사용하는 NONBLIND 이론 생성자. 최종 독립 판정자가 아니다.

## 0. 결론과 근거의 범위

PHYS31의 같은 이차 모멘트·실제 분산·같은 정확한 수준 \(A\)를 유지하면, 근의 존재를 먼저 보장하는 고정 구간 조건 아래

\[
\boxed{
|\Delta W(\delta)-D_4\delta^4|
\le \delta^4\mathcal R(\delta),\qquad
\mathcal R(\delta)=
\frac{|\Delta\mu_4|B_H(\delta)/24+r_4(\delta)
|D_4|S_C(\delta)}{\kappa}
}
\tag{T32.1}
\]

를 얻는다. 여기서 \(\kappa>0\)는 응답의 실제 분산 미분 하한, \(B_H\)는 사차 도함수 가중합의 이동 상계, \(r_4\)는 두 프로파일 평균의 사차 Taylor 나머지, \(S_C\)는 근 사이 평균 기울기의 기준값 이탈 상계다. 각 양은 아래에서 근을 미리 안다고 가정하지 않고 정의한다. \(k\in C^4\)이면 \(\mathcal R(\delta)\to0\)이며, 유계 오차를 가진 입력과 도함수 상계가 실제로 확보되면 이 부등식은 유한 폭에서 사용할 수 있다.

추가 \(C^5\) 전제에서는 명시적인 상수 \(K_R\)로

\[
|\Delta W(\delta)-D_4\delta^4|\le K_R\delta^5
\tag{T32.2}
\]

라는 보수적인 충분조건을 준다. 대칭성만으로 이동하는 기하와 분모에서 나오는 오차까지 육차가 된다고 하지는 않는다. 엄격한 부호의 충분조건은 \(\mathcal R(\delta)<|D_4|\)다. 두 분지의 간격에는 각각의 나머지를 더해야 한다.

이 문서는 **직접 유도**다. 새로운 물리 커널·노드·도함수·근의 수치 평가 또는 과학 프로그램 실행은 0이다. 기존 물리 cache의 소수값을 구간 상계로 승격하지 않았다. 물리적으로 인증된 유효 폭의 숫자, 실제 원자 fit 오차 또는 실제 기체 이력의 승격은 이 결과에 포함하지 않는다.

## 1. 읽은 근거와 유지하는 정의

현재 [물리 계약](../../PHYSICS_CONTRACT.json), 실제 [연구 상태](../../state/RESEARCH_STATE.md), Astra 연구 하네스의 core와 관련 phase를 읽었다. 선행 과학 내용은 [PHYS31 전체 이론 유도](../../inputs/PHYS31/contributions/theory/DERIVATION_KO.md) 및 [PHYS32 인수문](../../inputs/PHYS31/next/PHYS32_NEXT_HANDOFF_KO.md)을 직접 읽었다. 읽은 파일·범위·SHA256은 [READ_MANIFEST.json](READ_MANIFEST.json)에 둔다. PHYS31의 과학 main을 다시 실행하거나 원 프로그램을 import하지 않았다.

\[
a<m<b,\quad L=m-a,\quad H=b-m,\qquad
a=13.61,\ b=24.58,\ m=18,\ L=4.39,\ H=6.58
\quad({\rm eV})
\tag{T32.3}
\]

를 보존한다. 두 프로파일 \(\nu,\sigma\)는 \([-1,1]\) 위의 고정된 대칭 Borel 확률측도이고

\[
\mu_2=\int z^2\,d\nu=\int z^2\,d\sigma,\qquad
\Delta\mu_4=\mu_{4,\nu}-\mu_{4,\sigma},\qquad
\mu_{4,\alpha}=\int z^4\,d\alpha .
\tag{T32.4}
\]

측도는 \(\delta,W,\) 중심과 분지에서 독립이며 원자를 허용한다. 폭은 \(\delta\ge0\)이다. 중심 구간은 항상 \([a+\delta,b-\delta]\)이고, 실제 분산 \(W\)와 중심 분산 \(V\)의 관계는

\[
V=W-\mu_2\delta^2,\qquad
\mu_2\delta^2\le W\le (L-\delta)(H-\delta)+\mu_2\delta^2.
\tag{T32.5}
\]

한 분지를 고정하고 다음 표기를 쓴다.

| 분지 | \(s\) | \(R\) | \(e=m-sR\) | \(x_0=m+sw/R\) |
|---|---:|---|---|---|
| 상단 \(+\), 선행 \(*\) | \(+1\) | \(L\) | \(a\) | \(m+w/L\) |
| 하단 \(-\), 선행 \(0\) | \(-1\) | \(H\) | \(b\) | \(m-w/H\) |

\[
r=R-\delta,\quad
e_\delta=e+s\delta,\quad
x_{\delta,W}=m+\frac{s(W-\mu_2\delta^2)}r,
\quad
p_{\delta,W}=\frac{W-\mu_2\delta^2}{r^2+W-\mu_2\delta^2},
\quad q_{\delta,W}=1-p_{\delta,W},
\tag{T32.6}
\]

\[
f_{\delta,\alpha}(y)=\int k(y+\delta z)\,d\alpha(z),\qquad
F_\alpha(\delta,W)=
p_{\delta,W}f_{\delta,\alpha}(e_\delta)
+q_{\delta,W}f_{\delta,\alpha}(x_{\delta,W}).
\tag{T32.7}
\]

같은 \(\mu_2\) 때문에 T32.5–7의 기하는 두 프로파일에 정확히 공통이다. 모든 \(W\) 미분은 \(\delta\)를 고정한 **실제 분산 미분**이다.

기준점과 수준은

\[
0<w<LH,\qquad F_\nu(0,w)=F_\sigma(0,w)=A
\tag{T32.8}
\]

를 정확하게 만족한다고 가정한다. \(A\)는 정확히 같은 수준이며 0일 필요가 없다. 저장된 기준점에 대해 \(A=F(0,w)\)를 정확 실수 함수의 정의로 채택하는 경우와, 별도로 저장된 반올림 \(A\)가 그 등식을 만족하는지를 인증하는 경우를 구별한다. 후자는 이 가정만으로 해결되지 않는다.

주 정리에는 \(k\in C^4([a,b])\)와 \(k''>0\)를 쓴다. 끝점 미분은 내부 한쪽 도함수의 연속 극한이다. 상속한 \(k'''<0\)는 중심 혼합족의 극값 해석에 남겨 두지만, 아래 근 나머지 증명에는 필요하지 않다. 이 문서는 상속 부호를 새로운 물리 구간 인증으로 재검증하지 않는다.

기존 metric \((-,+,+,+)\), proper seconds, 에너지 eV, \(k,F,A\)의 단위 s⁻⁴를 유지한다. \(c,\hbar,k_B\)를 1로 놓거나 새로운 단위 변환을 하지 않는다.

## 2. 근의 존재와 독립인 고정 구간 조건

먼저 \(\eta>0\)와 \(d>0\)를 정해

\[
d<\min(L,H),\qquad
\mu_2d^2<w-\eta,\qquad
w+\eta<(L-d)(H-d)
\tag{T32.9}
\]

를 요구한다. 이는 간단한 **충분조건**이다. 모든 \(0\le\delta\le d\)와 \(W\in[w-\eta,w+\eta]\)에 대해

\[
0<V=W-\mu_2\delta^2<(L-\delta)(H-\delta)
\tag{T32.10}
\]

이므로 해당 사각 영역은 실현가능 내부에 있다. 실제로 하한은 T32.9에서 바로 나오고, 상한은
\(V\le W\le w+\eta<(L-d)(H-d)\le(L-\delta)(H-\delta)\)다.
따라서 \(r>0,\ p,q>0\), 모든 중심과 평균에 쓰는 에너지는 원래 구간 안에 있다.

T32.9는 정확 상한의 \(+\mu_2\delta^2\)를 버려 보수적으로 만든 조건이다. 정확 상한
\(U(\delta)=LH-(L+H)\delta+(1+\mu_2)\delta^2\)가 모든 허용 폭에서 단조 감소한다고 가정하지 않았다. 더 넓은 영역이 필요하면 T32.5를 해당 전체 영역에서 직접 인증해 T32.9를 대체할 수 있다.

커널의 유계 상수와 연속성 모듈러스를

\[
m_2=\min_{[a,b]}k''>0,\quad
\kappa=\frac{m_2}{2},\quad
M_j=\sup_{[a,b]}|k^{(j)}|\quad(j=1,2),
\tag{T32.11}
\]

\[
\omega_n(h)=\sup\{
|k^{(n)}(u)-k^{(n)}(v)|:
u,v\in[a,b],\ |u-v|\le h\},\qquad n=2,4
\tag{T32.12}
\]

로 둔다. \(h\ge0\)에서 정의하며 구간 길이를 넘으면 같은 전구간 상계를 사용한다. \(\omega_n\)은 비감소이고 \(\omega_n(0)=0,\ \omega_n(h)\to0\)이다. 인증된 보수적 상·하한을 사용해도 이후 부등식은 유지된다. 단, 해석적으로 존재하는 최소·상한과 실제 숫자로 인증한 bound는 같은 근거가 아니다.

## 3. 양의 기울기의 정확한 적분 표현

\(g=f_{\delta,\alpha}\), \(x=x_{\delta,W}\), \(D=x-e_\delta=s(r^2+V)/r\)라 두자. \(D\ne0\)이며 부호는 \(s\)다. T32.6–7을 실제 \(W\)로 미분하면

\[
F_{\alpha,W}
=\frac{g(e_\delta)-g(x)+Dg'(x)}{D^2}.
\tag{T32.13}
\]

적분 \(\int_0^1t\,g''(e_\delta+tD)\,dt\)에 부분적분을 적용하면 T32.13과 같아진다. \(D<0\)인 하단 분지에서도 같은 식이다. 따라서

\[
\boxed{
F_{\alpha,W}(\delta,W)=
\int_0^1 t\int k''\!\left((1-t)e_\delta+t x_{\delta,W}+\delta z\right)
\,d\alpha(z)\,dt
\ge\kappa .
}
\tag{T32.14}
\]

평균 미분은 콤팩트 구간에서 유계인 \(k''\)로 정당화된다. \(\alpha\)의 밀도는 필요하지 않다. 모든 적분점은 허용 중심 구간의 선분에 \(\delta z\)를 더한 점이므로 \([a,b]\) 안이다.

기준 기울기는 두 프로파일에서 공통이고

\[
C=F_W(0,w)=\int_0^1t\,k''((1-t)e+t x_0)\,dt
\ge\kappa>0.
\tag{T32.15}
\]

T32.14의 전 영역 하한을 근 존재 이전에 얻었다. 이후의 근 이동 상계가 이미 존재하는 근을 전제로 기울기를 추정하는 순환은 없다.

## 4. 기준점의 응답 이동에서 근 존재와 이탈을 얻기

\(p_0=w/(R^2+w)\), \(q_0=1-p_0\)라 하고, 이 절에서
\(p_\delta=p_{\delta,w},\ q_\delta=1-p_\delta,\ x_\delta=x_{\delta,w}\)다.
두 고정 노드의 응답 차이를 \(O_0=|k(e)-k(x_0)|\)로 둔다.

대칭성으로 \(\int z\,d\alpha=0\)이므로 일차 Taylor 식의 적분 나머지에서

\[
|f_{\delta,\alpha}(y)-k(y)|
\le \frac{\mu_2M_2}{2}\delta^2.
\tag{T32.16}
\]

또한

\[
\begin{aligned}
&p_\delta k(e_\delta)+q_\delta k(x_\delta)
-p_0k(e)-q_0k(x_0)\\
&=(p_\delta-p_0)[k(e)-k(x_0)]
+p_\delta[k(e_\delta)-k(e)]
+q_\delta[k(x_\delta)-k(x_0)].
\end{aligned}
\tag{T32.17}
\]

\[
|x_\delta-x_0|=
\frac{|w\delta/R-\mu_2\delta^2|}{R-\delta}
\tag{T32.18}
\]

를 대입하여 다음의 프로파일 공통 상계를 얻는다.

\[
\boxed{
B(\delta)=
|p_\delta-p_0|O_0
+M_1\left[p_\delta\delta+
q_\delta\frac{|w\delta/R-\mu_2\delta^2|}{R-\delta}\right]
+\frac{\mu_2M_2}{2}\delta^2,
\quad
|F_\alpha(\delta,w)-A|\le B(\delta).
}
\tag{T32.19}
\]

\(B(0)=0\)이며 \(B(\delta)=O(\delta)\)다. 끝점과 내부 중심의 이동을 함께 포함하며, 평활화 오차의 두 확률이 합해 1이므로 T32.16의 오차를 두 배 하지 않는다.

이제 주어진 \(\delta\in[0,d]\)에서

\[
B(\delta)<\kappa\eta
\tag{T32.20}
\]

를 확인하면, T32.14와 T32.19가

\[
F_\alpha(\delta,w-\eta)-A
\le B-\kappa\eta<0,\qquad
F_\alpha(\delta,w+\eta)-A
\ge-B+\kappa\eta>0
\tag{T32.21}
\]

를 준다. 연속성과 엄격한 단조성으로 정확한 근
\(W_\alpha(\delta)\in(w-\eta,w+\eta)\)가 유일하게 존재한다. 다시 기울기 하한을 적분하면

\[
\boxed{
|W_\alpha(\delta)-w|\le
\rho(\delta),\qquad
\rho(\delta)=\frac{B(\delta)}{\kappa}<\eta ,
\quad\alpha\in\{\nu,\sigma\}.
}
\tag{T32.22}
\]

이는 새로운 근 탐색을 가정하지 않는, 기준점의 응답 잔차로부터 얻는 존재 및 이탈 정리다. 같은 \(\delta\)에서 두 근을 잇는 전체 선분도 \(|W-w|\le\rho\)에 있다.

## 5. 근 근방의 중심·확률·기울기 이동

### 5.1 중심 이동

\(|W-w|\le\rho\)이면

\[
x_{\delta,W}-x_0
=\frac{s[(W-w)+w\delta/R-\mu_2\delta^2]}{R-\delta}.
\tag{T32.23}
\]

따라서

\[
h_x(\delta)=\frac{\rho+w\delta/R+\mu_2\delta^2}{R-\delta},
\qquad
h(\delta)=\max\{\delta,h_x(\delta)\}
\tag{T32.24}
\]

에 대해 \(|e_\delta-e|\le h,\ |x_{\delta,W}-x_0|\le h\)다. 여기에 프로파일의 \(\delta z\)까지 더한 실제 에너지 선분의 이동은 \(h+\delta\)로 상계된다.

### 5.2 확률 이동

공통 기하에서 직접 통분하면

\[
p_{\delta,W}-p_0=
\frac{R^2(W-w-\mu_2\delta^2)
+w\delta(2R-\delta)}
{(r^2+W-\mu_2\delta^2)(R^2+w)}.
\tag{T32.25}
\]

T32.22와 양의 분모를 사용해

\[
\boxed{
P(\delta)=\min\!\left\{1,\
\frac{R^2(\rho+\mu_2\delta^2)+w\delta(2R-\delta)}
{(r^2+w-\rho-\mu_2\delta^2)(R^2+w)}
\right\}
}
\tag{T32.26}
\]

를 정의하면 \(|p_{\delta,W}-p_0|\le P\)다. 분모의 첫 인자는 T32.9와 \(\rho<\eta\)에서 양수다. \(\delta<R\)이므로 \(\delta(2R-\delta)\ge0\)다. \(P\)는 사용 가능한 닫힌 형태의 충분 상계이며 최적값이라는 주장은 하지 않는다. 필요하면 \(p_{\delta,W}\)의 \(W\) 단조성을 사용한 두 끝점의 최대 편차로 더 작게 잡을 수 있다.

### 5.3 사차 도함수 가중합 이동

\[
H_4(\delta,W)=
p_{\delta,W}k^{(4)}(e_\delta)
+q_{\delta,W}k^{(4)}(x_{\delta,W}),\qquad
H_{4,0}=p_0k^{(4)}(e)+q_0k^{(4)}(x_0),
\tag{T32.27}
\]

\[
O_4=|k^{(4)}(e)-k^{(4)}(x_0)|,\qquad
B_H(\delta)=P(\delta)O_4+\omega_4(h(\delta))
\tag{T32.28}
\]

로 두면 \(|H_4(\delta,W)-H_{4,0}|\le B_H\)다. 증명은 T32.17의 \(k\)를 \(k^{(4)}\)로 바꾸고, 두 노드 이동 항을
\(p\omega_4(\delta)+q\omega_4(h_x)\le\omega_4(h)\)로 상계하는 것이다. 양의 공통 확률이 핵심이다.

### 5.4 실제 분산 기울기 이동

T32.14의 적분점과 T32.15의 적분점을 같은 \(t,z\)로 짝지으면

\[
\left|(1-t)e_\delta+t x_{\delta,W}+\delta z
-[(1-t)e+t x_0]\right|\le h+\delta.
\tag{T32.29}
\]

따라서 각 프로파일에서

\[
\boxed{
|F_{\alpha,W}(\delta,W)-C|
\le S_C(\delta),\qquad
S_C(\delta)=\frac12\omega_2(h(\delta)+\delta).
}
\tag{T32.30}
\]

별도의 확률 미분 상계가 더 붙지 않는 이유는 T32.14가 이미 \(p,q,x\)의 분산 미분을 정확히 결합한 표현이기 때문이다. 기준 기울기 \(C\)와 단지 점별 \(k''\) cache를 혼동하지 않는다.

## 6. 일반 대칭 프로파일의 사차 나머지

반복된 미적분의 기본정리로 \(y,y+u\in[a,b]\)일 때

\[
k(y+u)=\sum_{\ell=0}^4\frac{u^\ell}{\ell!}k^{(\ell)}(y)
+R_4(y,u),\qquad
|R_4(y,u)|\le\frac{|u|^4}{24}\omega_4(|u|).
\tag{T32.31}
\]

이는 3차 적분 나머지에서 \(k^{(4)}(y)\)를 더하고 빼면 얻으며, \(u<0\)에서도 같은 매개화로 성립한다. \(u=\delta z\)를 대입하고 두 프로파일을 빼면 질량·평균·이차·삼차 모멘트가 소거되어

\[
f_{\delta,\nu}(y)-f_{\delta,\sigma}(y)
=\frac{\Delta\mu_4}{24}k^{(4)}(y)\delta^4
+\delta^4\varepsilon_4(\delta,y),
\tag{T32.32}
\]

\[
|\varepsilon_4(\delta,y)|
\le r_4(\delta):=
\frac{\mu_{4,\nu}+\mu_{4,\sigma}}{24}\omega_4(\delta).
\tag{T32.33}
\]

이 상계는 모든 허용 중심에서 균일하다. \(p,q\)가 같은 비음수 확률이므로

\[
\Delta F(\delta,W):=F_\nu-F_\sigma
=\delta^4\left[
\frac{\Delta\mu_4}{24}H_4(\delta,W)+\varepsilon_F(\delta,W)
\right],\qquad
|\varepsilon_F|\le r_4.
\tag{T32.34}
\]

서로 같은 측도처럼 추가 소거가 있는 경우 T32.33은 날카롭지 않을 수 있다. 필요하면 \(\mu_{4,\nu}+\mu_{4,\sigma}\)를
\(\int |z|^4\,d|\nu-\sigma|(z)\)로 대체할 수 있다. 본 정리에는 그 개선이 필요하지 않다.

## 7. 사차 응답 차이를 근 차이로 옮기는 정량 정리

\[
\Delta W=W_\nu-W_\sigma,\qquad
D_4=-\frac{\Delta\mu_4 H_{4,0}}{24C}
\tag{T32.35}
\]

로 정의한다. \(D_4\)는 ordinary 사차 계수의 차이이며 사차 도함수 자체의 차이는 \(24D_4\)다.

두 근에서 **같은 정확한 \(A\)**를 쓰므로

\[
0=F_\nu(\delta,W_\nu)-F_\sigma(\delta,W_\sigma)
=\overline C(\delta)\Delta W
+\Delta F(\delta,W_\sigma),
\tag{T32.36}
\]

\[
\overline C(\delta)=
\int_0^1F_{\nu,W}(\delta,W_\sigma+t\Delta W)\,dt.
\tag{T32.37}
\]

이 표현은 \(\Delta W=0\)에서도 정의된다. 두 근 사이 선분에 T32.14와 T32.30을 적용하면

\[
\overline C\ge\kappa,\qquad
|\overline C-C|\le S_C.
\tag{T32.38}
\]

\(\delta>0\)에서 T32.34–38을 사용해 정확히

\[
\frac{\Delta W}{\delta^4}-D_4
=-\frac{
\frac{\Delta\mu_4}{24}[H_4(\delta,W_\sigma)-H_{4,0}]
+\varepsilon_F(\delta,W_\sigma)
+D_4(\overline C-C)}
{\overline C}.
\tag{T32.39}
\]

따라서 T32.1을 얻는다. \(\delta=0\)에서는 양변이 0이다. 이 부등식에 포함된 세 오차는 각각 사차 가중합 이동, 평균의 Taylor 나머지, 근 사이 분모 이동이다. 응답의 Taylor 나머지만 작다고 해서 마지막 항을 버릴 수 없다.

원한다면

\[
\kappa_{\rm eff}(\delta)=\max\{\kappa,C-S_C(\delta)\}>0
\tag{T32.40}
\]

를 T32.1의 분모에 사용해 개선할 수 있다. \(\rho\)와 \(h,P,S_C\)는 이미 \(\kappa\)로 계산된 것이므로 이 개선에도 순환은 없다.

\(B=O(\delta)\), \(\rho=O(\delta)\), \(h=O(\delta)\), \(P=O(\delta)\)이고 \(\omega_n(t)\to0\)이므로 \(\mathcal R(\delta)\to0\)다. T32.20은 충분히 작은 양의 폭에서 성립한다. 이 결론은 PHYS31의 \(o(\delta^4)\)를 회복하지만, 현재 부등식은 유한 폭에서 확인해야 할 모든 상수를 드러낸다.

## 8. \(C^5\)에서 사용할 수 있는 완전한 상수 형태

이 절에서는 T32.9를 만족하는 \(d\)를 고정한다. 다음의 양수들을 정의한다.

\[
Q_b=(R-d)^2+w-\mu_2d^2,\qquad
Q_t=(R-d)^2+w-\eta-\mu_2d^2,
\tag{T32.41}
\]

\[
u_p=\frac{2wR+R^2\mu_2d}{Q_b(R^2+w)},\qquad
u_x=\frac{w/R+\mu_2d}{R-d},
\tag{T32.42}
\]

\[
K_B=u_pO_0+M_1\max\{1,u_x\}
+\frac{\mu_2M_2d}{2}.
\tag{T32.43}
\]

T32.25에 \(W=w\)를 넣고 분자 절댓값을 상계하면
\(|p_{\delta,w}-p_0|\le u_p\delta\)다. T32.18은
\(|x_{\delta,w}-x_0|\le u_x\delta\)를 준다. T32.19에서 \(p+q=1\)을 쓰면

\[
B(\delta)\le K_B\delta\quad(0\le\delta\le d).
\tag{T32.44}
\]

따라서 추가로 \(K_Bd<\kappa\eta\)를 확인하면 같은 전체 폭 구간의 근 존재가 보장된다. 이는 미지의 근에 대한 조건이 아니라 입력 상수들에 대한 명시적인 충분조건이다.

\[
c_\rho=\frac{K_B}{\kappa},\qquad
K_h=\max\left\{1,\frac{c_\rho+w/R+\mu_2d}{R-d}\right\},
\tag{T32.45}
\]

\[
K_P=
\frac{R^2(c_\rho+\mu_2d)+2wR}{Q_t(R^2+w)}
\tag{T32.46}
\]

라 두면 \(\rho\le c_\rho\delta,\ h\le K_h\delta,\ P\le K_P\delta\)다. 마지막 식은 T32.26의 분모를 \(Q_t(R^2+w)\)로 낮추고 분자를 일차 상계한 결과다.

이제 추가 \(k\in C^5([a,b])\)를 가정하고
\(M_3=\sup|k'''|,\ M_5=\sup|k^{(5)}|\)를 둔다. 평균값정리로
\(\omega_2(t)\le M_3t,\ \omega_4(t)\le M_5t\)다. 또한 4차 Taylor 식의 5차 적분 나머지는

\[
|R_4(y,u)|\le\frac{M_5|u|^5}{120}
\tag{T32.47}
\]

이므로, \(\beta_{5,\alpha}=\int|z|^5\,d\alpha\)라 할 때 T32.33 대신

\[
r_4(\delta)\le
\frac{(\beta_{5,\nu}+\beta_{5,\sigma})M_5}{120}\delta
\tag{T32.48}
\]

를 사용할 수 있다. 이 \(1/120\)은 표준 적분 나머지의 \(1/5!\)이며 사차 계수의 \(1/24\)와 다른 인자다.

결국

\[
\boxed{
K_R=
\frac1\kappa\left[
\frac{|\Delta\mu_4|}{24}(K_PO_4+M_5K_h)
+\frac{(\beta_{5,\nu}+\beta_{5,\sigma})M_5}{120}
+\frac{|D_4|M_3(K_h+1)}2
\right]
}
\tag{T32.49}
\]

가 T32.2를 모든 \(0\le\delta\le d\)에서 보장한다. \(C^5\)의 대칭 프로파일은 5차 모멘트 차이도 0이지만, 여기서는 이미 충분한 보수 상계를 사용했다. 설령 직접 평균의 5차 항이 소거되어도 \(H_4\)와 \(\overline C\)의 일차 이동은 일반적으로 남으므로 근의 나머지를 자동으로 \(O(\delta^6)\)로 바꾸지 않는다.

이 상수식은 최적 폭을 주려는 식이 아니다. 인증 가능한 상수들만으로 검토자가 동일한 충분조건을 확인할 수 있게 하는 식이다. \(M_3,M_5,m_2\)에 수치 enclosure가 없으면 \(K_R\)도 미평가 조건부 상수로 남는다.

## 9. 같은 비영 수준과 분자식을 사용할 때의 주의점

\[
Q=r^2+V,\quad
N_\alpha=Vf_{\delta,\alpha}(e_\delta)+r^2f_{\delta,\alpha}(x_{\delta,W}),
\quad G_\alpha=N_\alpha-AQ,\quad F_\alpha=N_\alpha/Q.
\tag{T32.50}
\]

\(Q\)는 두 프로파일에서 공통이고 양수다. 항상

\[
G_{\alpha,W}=N_{\alpha,W}-A
=QF_{\alpha,W}+(F_\alpha-A).
\tag{T32.51}
\]

따라서 **해당 \(A\)의 근에서만** \(G_{\alpha,W}=QF_{\alpha,W}\)다. 영폭 기준근에서는

\[
N_W(0,w)=k(e)+sRk'(x_0),\qquad
N_W(0,w)-A=(R^2+w)C,
\tag{T32.52}
\]

\[
D_4=
-\frac{\Delta\mu_4\,[w\,k^{(4)}(e)+R^2k^{(4)}(x_0)]}
{24[N_W(0,w)-A]}.
\tag{T32.53}
\]

\(\Delta G=\Delta N=Q\Delta F\)이므로 프로파일 차이의 분자에서 \(AQ\)는 소거된다. 그러나 T32.52–53의 \(-A\)는 남는다. 또한 근 사이 평균값정리의 중간점은 보통 \(F_\nu=A\)를 만족하지 않으므로, 전체 구간에서 \(G_{\nu,W}=QF_{\nu,W}\)라고 놓아 하한을 옮기면 안 된다. 이 문서는 T32.36–38에서 정규화된 \(F\)를 사용해 그 문제를 피했다.

저장된 \(A\)가 작다는 이유로 0으로 놓지 않는다. \(A_\nu\ne A_\sigma\)이면 T32.36에 수준 차이가 추가되어 본 정리의 같은 수준 비교가 아니다. 각 분지 안의 두 프로파일은 같은 정확한 \(A_j\)를 써야 하며 서로 다른 분지의 \(A_+\)와 \(A_-\)가 같을 필요는 없다.

## 10. 부호, 간격, 조건수의 충분조건

\(\delta>0\)에서 T32.1은 실제 차이의 구간

\[
\delta^4(D_4-\mathcal R)
\le\Delta W(\delta)\le
\delta^4(D_4+\mathcal R)
\tag{T32.54}
\]

을 준다. 그러므로 \(D_4\ne0\)이고 \(\mathcal R<|D_4|\)이면
\(\operatorname{sgn}\Delta W=\operatorname{sgn}D_4\)다.
\(\mathcal R=|D_4|\)이면 엄격한 부호까지는 얻지 못한다. \(D_4=0\)이면 이 부등식만으로 부호를 정할 수 없다.

\(C^5\)의 전체 구간 조건 아래에서는 \(K_R>0\)일 때
\[
0<\delta\le d,\qquad \delta<|D_4|/K_R
\tag{T32.55}
\]
가 더 간단한 충분조건이다. \(K_R=0,\ D_4\ne0\)이면 T32.2에서 그 전체 구간의 정확한 사차 차이와 부호가 따른다.

간격 \(\Gamma_\alpha=W_{-,\alpha}-W_{+,\alpha}\)에는 두 분지의 정리를 각각 적용해야 한다. 공통 폭에서 두 분지의 존재·실현가능 조건이 모두 성립하면

\[
D_{4,\Gamma}=D_{4,-}-D_{4,+},\qquad
|\Gamma_\nu-\Gamma_\sigma-D_{4,\Gamma}\delta^4|
\le\delta^4(\mathcal R_-+\mathcal R_+).
\tag{T32.56}
\]

따라서 \(\mathcal R_-+\mathcal R_+<|D_{4,\Gamma}|\)가 간격 차이의 엄격한 부호 조건이다. 각각의 \(\Delta W_j\)가 음수라는 정보만으로 간격의 차이가 양수인지 음수인지 정할 수 없다.

근 조건수의 절대 상한은 \(1/\kappa\)다. 같은 \(\delta\)에서 응답 또는 수준이 \(\varepsilon\)만큼 바뀌고 비교할 두 근의 존재와 같은 기울기 하한이 별도로 보장되면 근 이동은 \(\varepsilon/\kappa\) 이하이다. \(\kappa\)가 작으면 응답 오차, 기하 이동 상계의 \(\rho=B/\kappa\), 최종 나머지까지 함께 나빠진다. \(D_4\)가 0에 가까우면 절대 오차가 작더라도 부호 판별이 어려워진다.

저장 사차 계수 \(\widehat D_4\)를 쓸 때는 인증된 \(|D_4-\widehat D_4|\le E_D\)와 보수적으로 계산한 \(\mathcal R\)가 있어야 한다. 그러면
\[
|\Delta W-\widehat D_4\delta^4|
\le\delta^4(\mathcal R+E_D),
\qquad |\widehat D_4|>\mathcal R+E_D
\tag{T32.57}
\]
가 그 저장 계수의 부호를 전달하는 충분조건이다. \(\mathcal R\) 자체 안의 \(|D_4|\), \(C\), 미분 bound에도 같은 오차 처리가 필요하다. 명목 중앙값만 넣고 \(E_D\)를 마지막에 한 번 더하는 것으로 모든 불확실성이 자동 처리되지는 않는다.

기준점이 근이라는 정확한 조건 T32.8을 대체하려면
\(|F(0,\widehat w)-A|\le\varepsilon_0\)의 인증 상계가 필요하다. 또한
\(\widehat B(\delta)\ge|F_\alpha(\delta,\widehat w)-F(0,\widehat w)|\)를 두 프로파일에 공통으로 다시 확보해야 한다. \(\widehat B\)는 T32.19의 기하·노드·확률을 \(\widehat w\) 중심에서 새로 구성해 얻거나 직접 증명한 상계다. 정확한 \(w\)에서만 성립한 \(B\)를 그대로 이동시키지 않는다. \(\widehat w\) 중심의 고정 구간과 기울기 하한이 보장되면 \(\widehat B+\varepsilon_0<\kappa\eta\)와 \(\rho=(\widehat B+\varepsilon_0)/\kappa\)로 그 근방의 근 존재를 먼저 다룰 수 있다. 그러나 정확한 사차 계수는 실제 영폭 근에서 정의되므로 그 계수 이동·노드 및 source 오차를 별도로 전달해야 한다. 이 문서의 T32.1을 단순히 \(w=\widehat w\)로 바꿔 그 부분까지 인증했다고 하지 않는다. 상세 입력·계수 오차 전파는 PHYS32의 별도 conditioning 기여가 다룬다.

## 11. 단위, 예외와 실제 증거의 한계

| 양 | 단위 |
|---|---|
| \(z,\mu_2,\mu_4,p,q,P,K_h,u_x,\beta_5\) | 무차원 |
| \(a,b,m,L,H,R,\delta,d,h,h_x\) | eV |
| \(W,V,w,\eta,\rho,Q_b,Q_t\) | eV² |
| \(k,F,A,B,O_0\) | s⁻⁴ |
| \(m_2,M_2,\kappa,C,S_C\) | s⁻⁴ eV⁻² |
| \(H_{4,0},O_4,B_H,r_4,\omega_4\) | s⁻⁴ eV⁻⁴ |
| \(D_4,\mathcal R,E_D\) | eV⁻² |
| \(K_B,M_1\) | s⁻⁴ eV⁻¹ |
| \(c_\rho\) | eV |
| \(u_p,K_P\) | eV⁻¹ |
| \(M_3,M_5\) | 각각 s⁻⁴ eV⁻³, s⁻⁴ eV⁻⁵ |
| \(K_R\) | eV⁻³ |

\(\delta^4\mathcal R\)와 \(K_R\delta^5\)는 모두 실제 분산 차이의 단위 eV²다. \(\mu_2=0\) 또는 1에서는 대칭 확률측도가 각각 유일하므로 서로 다른 프로파일 비교가 퇴화한다. \(C=0\), \(m_2\le0\), 경계근, 폭에 따라 변하는 프로파일, 서로 다른 \(\mu_2\), 다른 정확한 수준을 본 정리에 자동 포함하지 않는다. 다른 양의 기울기 하한을 직접 증명하면 \(m_2>0\) 대신 그 하한을 사용할 수 있지만, 그런 확장은 현재 물리 입력을 인증한 결과가 아니다.

실제 물리 숫자를 내기 위해 아직 필요한 것은 기준근과 정확한 \(A\)의 관계, \(m_2\) 또는 그에 대신하는 양의 기울기 enclosure, 필요한 \(M_j\) 또는 \(\omega_j\)의 전 영역 bound, \(D_4\)의 입력·반올림·노드 오차, 그리고 원 \(J\)와 source의 불확실성 근거다. PHYS31의 네 점 cache 및 두 도함수 표현의 일치는 이 전 영역 증거를 제공하지 않는다. source의 정확 실수 해석에서 해석성이 있다는 사실도 숫자가 붙은 최소·상한을 자동 제공하지 않는다.

특수 \(P_4\)–uniform 쌍의 양의 Peano 적분 표현은 별도 PHYS32 기여가 직접 유도하며, 그 특수 구조로 T32.33의 일반 측도 상계를 개선할 수 있다. 이 문서의 일반 정리는 그 특수 양성이나 추가 물리 \(k^{(4)}\) 부호를 전제하지 않는다.

| 주장 | 근거 상태 | 제한 |
|---|---|---|
| 고정 구간의 실현가능성 | derived | T32.9의 충분조건 |
| 실제 \(W\) 기울기 하한 | conditional derived | \(k''\ge m_2>0\), 원 구간 |
| 근 존재·유일성·\(\rho\) | conditional derived | T32.9와 \(B<\kappa\eta\) |
| 일반 \(C^4\) 사차 근 나머지 | conditional derived | T32.1, T32.39, 같은 정확한 \(A\) |
| \(C^5\)의 명시적 \(K_R\delta^5\) | conditional derived | T32.41–49와 전체 구간 조건 |
| 분지·간격의 부호 충분조건 | conditional derived | 엄격한 오차 여유가 필요 |
| 물리 bound의 수치값·인증 폭 | unresolved, NOT_RUN | 본 기여의 계산 예산 0 |
| 저장근·\(J\)·fit 오차의 실제 enclosure | unresolved | 별도 근거 필요 |
| 실제 과학 검증과 최종 승격 | 이 기여의 범위 밖 | 별도 실행 증거 및 분리 reviewer |

본 기여의 점검은 THEORY_CONTRIBUTOR_SELF_CHECK이다. 과학 main·물리 kernel/derivative/root/node·수치 toy·quadrature·finite difference·새 폭 스윕·옛 과학 import 및 main은 모두 0이다. 파일 읽기·작성·해시는 문서와 identity 작업으로만 분류한다. 전체 증명에서 외부 문헌의 새 정리·우선권·신규성 주장을 사용하지 않았다.

**Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0**을 유지한다. 기계 판독 주장과 실제 읽기·역할·변경 provenance는 [THEORY_CLAIMS.json](THEORY_CLAIMS.json), [READ_MANIFEST.json](READ_MANIFEST.json), [PROVENANCE.json](PROVENANCE.json)에 기록한다.
