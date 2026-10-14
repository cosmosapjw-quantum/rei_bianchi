# PHYS30 — 고정 대칭 프로파일의 국소 이차 문턱계수

연구: **REI-PHYS30-20261011 · SYMMETRIC_PROFILE_SECOND_ORDER_UNIVERSALITY**  
기여자: **/root/phys30_theory**, 같은 대화의 이론 후보 생성자, **NONBLIND**  
모델 근거: trusted developer designation **GPT-6 Astra Pro**; 연구 하네스 **gpt6-astra v4.0.0**  
근거 상태: **derived**, 동결 커널·정확한 내부 단순근 전제에 조건부  
역할 경계: 이론 기여와 자체 대수 점검이며 **독립 최종 판정이 아니다**.

## 0. 결론과 범위

공통 외곽 프로파일 구간 \([-1,1]\) 위의 고정 대칭 확률측도 \(\nu\)를 택하고, 중심 허용구간을 언제나 \([a+\delta,b-\delta]\)로 유지한다. 실제 광자 분산 \(W\)를 고정하면 중심 분산은

\[
V=W-\mu_2\delta^2,\qquad \mu_2=\int z^2\,d\nu(z)
\tag{T30.1}
\]

이다. 이 조건에서 영폭의 정확한 내부 문턱 \(w_j\)에서 출발하는 물리 한쪽 근은

\[
W_{j,\nu}(\delta)=w_j+c_j\delta+d_{j,\nu}\delta^2+o(\delta^2)
\tag{T30.2}
\]

를 갖고,

\[
\boxed{c_{j,\nu}=c_{j,\mathrm{unif}},\qquad
d_{j,\nu}=d_{j,\mathrm{unif}}
+\left(\mu_2-\frac13\right)
\left(1-\frac{\mathcal H_j}{2C_j}\right).}
\tag{T30.3}
\]

여기서 \(C_j=F_W(0,w_j)>0\), \(\mathcal H_j=p_jk''(e_j)+q_jk''(x_j)\)다. \(\mathcal H\)는 곡률의 가중합이며, 거리 \(H=b-m\)와 구별한다. 모든 \(\delta\) 편미분은 실제 \(W\)를 고정한 것이다. \(d\)는 전체 우이차 미분의 절반이고 무차원이다.

같은 \(\mu_2\)를 가진 두 고정 대칭 프로파일은 이차까지의 문턱 전개를 공유한다. 이 주장은 유한한 양의 폭에서 응답이나 근이 정확히 같다는 뜻이 아니다. 정량 Taylor 나머지, 유효 폭의 수치 하한, 일반 프로파일의 순서 또는 전체 \(d\)의 보편적인 부호를 주장하지 않는다.

이 문서의 수식은 직접 유도했다. 이 기여의 새 과학 main, 물리 커널·도함수 평가, 근 탐색·보정, 수치 적분, 유한차분, 수치 toy 실행, 이전 모듈 import와 재현 실행은 모두 **0회**다. 저장된 숫자의 새 대수 조합은 별도의 수치 기여자가 담당한다.

## 1. 정의, 입력과 전제

실제 [현재 PHYS30 물리 계약](../../PHYSICS_CONTRACT.json), [PHYS30 인수문](../../inputs/PHYS29/next/PHYS30_NEXT_HANDOFF_KO.md), [PHYS29 물리 계약](../../inputs/PHYS29/PHYSICS_CONTRACT.json), [PHYS29 이론 유도](../../inputs/PHYS29/contributions/theory/DERIVATION_KO.md), [PHYS29 최종 판정](../../inputs/PHYS29/independent/DECISION_REVIEW.json)의 승인·제외 범위를 소비한다. 계약·인수문·이론 유도는 전체를 읽었고, 판정문은 승인·제외 범위와 수학적 평가, 관련 주장 및 불확실성을 선별적으로 읽었다. 실제 원본 읽기와 이동 가능한 사본 포인터는 [PROVENANCE.json](PROVENANCE.json)에 분리했다.

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad H=b-m=6.58\quad (\mathrm{eV}).
\tag{T30.4}
\]

\[
0\le\delta<\min(L,H),\quad
\alpha=a+\delta,\quad\beta=b-\delta,\quad
\ell=L-\delta,\quad h=H-\delta.
\tag{T30.5}
\]

\(\nu\)는 다음 조건을 만족하는 Borel 확률측도다.

1. \(\nu\ge0\), \(\nu([-1,1])=1\), \(\nu(B)=\nu(-B)\).
2. \(\nu\)는 \(\delta,W\), 중심의 위치 및 상·하단 branch에 의존하지 않는다.
3. 지원은 \([-1,1]\)에 포함되면 충분하다. 실제로 두 끝점에 닿을 필요는 없다.
4. 중심 측도 \(\rho\)는 \([\alpha,\beta]\) 위의 임의의 Borel 확률측도이며, 평균 \(m\)과 분산 \(V\)를 갖는다.

프로파일의 대칭성과 콤팩트 지원으로

\[
\mu_1=\int z\,d\nu(z)=0,\qquad 0\le\mu_2\le1.
\tag{T30.6}
\]

광자 측도는 곱측도 \(\rho\otimes\nu\)를 \(T_\delta(y,z)=y+\delta z\)로 밀어낸

\[
P_{\delta,\rho,\nu}=(T_\delta)_\#(\rho\otimes\nu)
\tag{T30.7}
\]

로 정의한다. 즉 모든 중심에 같은 프로파일을 적용한다. 위치에 따른 profile 변경, 대역 절단·재정규화, 중심 허용구간의 추가 확장은 정의에 포함하지 않는다.

커널 전제는 PHYS29에서 상속한

\[
k\in C^3([a,b]),\qquad k''(E)>0,\qquad k'''(E)<0
\quad(E\in[a,b])
\tag{T30.8}
\]

다. 끝점 미분은 구간 안에서의 한쪽 미분과 그 연속 극한을 뜻한다. 새 한쪽 이차 정칙성 자체에는 \(k\in C^2\)가 충분하다. \(k''>0\)는 양의 분산 기울기에, \(k'''<0\)는 아래의 상·하단 모멘트 경계와 엄격한 접촉 집합에 사용한다. 이 부호 전제를 새로 수치 인증하지 않았다.

정확한 내부 영점의 존재는 별도 조건이다. 영폭의 두 응답이 정확근 \(w_j\in(0,LH)\)를 가진다고 가정한다. PHYS29의 저장 근 및 끝값 부호는 이 가정을 수치적으로 지원하는 입력이며, 본 기여가 새 근 enclosure를 제공하지는 않는다. 이 구별은 모든 근 정리에 유지한다.

물리 입력은 원 지원구간·평균·source-real 상수·PHYS22의 전체 직렬화 \(J\) 및 초기 기체 상태를 고정한다. \(k\)와 응답 \(F\)는 초기 HeIII의 \(\epsilon^2t^4\) 계수이고 단위는 s⁻⁴다. Metric \((-,+,+,+)\), gas-comoving proper seconds, 열 변수는 eV/H, \([\epsilon^2]=\frac12\partial_\epsilon^2|_0\), 시간계수의 추가 factorial 없음이라는 원 convention을 유지한다. \(c_{\rm light},\hbar,k_B\)를 새로 1로 놓거나 정규화를 바꾸지 않는다.

## 2. 지지·질량·평균·분산과 정확한 허용 범위

\(y\in[a+\delta,b-\delta]\), \(z\in[-1,1]\)이면 \(y+\delta z\in[a,b]\)다. 따라서 모든 허용 \(P_{\delta,\rho,\nu}\)는 원 물리 지원 안에 있고, 확률측도의 밀어내기이므로 총질량은 1이다. 직접 적분하면

\[
\int E\,dP=\int y\,d\rho+\delta\int z\,d\nu=m,
\]
\[
\int(E-m)^2dP
=\int(y-m)^2d\rho
+2\delta\left[\int(y-m)d\rho\right]\left[\int z\,d\nu\right]
+\delta^2\int z^2d\nu
=V+\mu_2\delta^2.
\tag{T30.9}
\]

이는 근사식이 아니다. 실제 분산 \(W\)를 고정하는 정의가 정확히 T30.1이다.

중심 측도에 대해 \((y-\alpha)(\beta-y)\ge0\)를 적분하면

\[
0\le\int(y-\alpha)(\beta-y)d\rho
=(m-\alpha)(\beta-m)-V=\ell h-V.
\tag{T30.10}
\]

또한 \(V\ge0\)다. 역으로 임의의 \(V\in[0,\ell h]\)에 대해 \(t=V/(\ell h)\)로 놓고

\[
\rho=(1-t)\delta_m+t\left[
\frac{h}{\ell+h}\delta_\alpha+
\frac{\ell}{\ell+h}\delta_\beta\right]
\tag{T30.11}
\]

를 택하면 같은 평균과 분산을 얻는다. 따라서 광자 분산의 필요충분 허용 조건은

\[
\boxed{\mathcal I_{\delta,\nu}
=\left[\mu_2\delta^2,\ (L-\delta)(H-\delta)+\mu_2\delta^2\right].}
\tag{T30.12}
\]

\(V=0\)에서는 중심 측도가 \(\delta_m\) 하나이고, \(V=\ell h\)에서는 T30.11의 끝점 측도 하나다. 이 두 경계도 물리 측도 정의에 포함하지만, 문턱 정리는 영폭의 내부 \(w_j\in(0,LH)\)에서 다룬다.

## 3. 일반 측도의 평균 커널과 정칙성

중심에 대한 평균 커널을

\[
f_{\delta,\nu}(y)=\int_{-1}^{1}k(y+\delta z)\,d\nu(z)
\quad(y\in[\alpha,\beta])
\tag{T30.13}
\]

로 둔다. \(k,k',k'',k'''\)는 콤팩트 구간에서 연속·유계이고, \(\nu\)는 유한한 고정 측도다. 중심 변수의 적분 미분 교환으로

\[
\partial_y^r f_{\delta,\nu}(y)
=\int k^{(r)}(y+\delta z)\,d\nu(z),\qquad 0\le r\le3.
\tag{T30.14}
\]

즉 \(f_{\delta,\nu}\in C^3([\alpha,\beta])\)이며

\[
f_{\delta,\nu}''>0,\qquad f_{\delta,\nu}'''<0.
\tag{T30.15}
\]

프로파일 밀도의 존재나 매끄러움은 이 결론에 필요하지 않다. 미분은 \(\nu\)가 아니라 매끄러운 \(k\)에 작용한다.

폭과 중심의 동시 변화는 물리적으로 허용되는 경로에서 다룬다. \(Y=Y(\delta,W)\)가 한쪽 \(C^2\)이고 모든 \(Y+\delta z\)가 \([a,b]\)에 남는다고 하자. \(\Psi=\int k(Y+\delta z)d\nu\)를 직접 미분하면

\[
\begin{aligned}
\Psi_\delta&=\int k'(Y+\delta z)(Y_\delta+z)d\nu,\\
\Psi_W&=\int k'(Y+\delta z)Y_Wd\nu,\\
\Psi_{\delta\delta}&=\int\left[k''(Y+\delta z)(Y_\delta+z)^2
+k'(Y+\delta z)Y_{\delta\delta}\right]d\nu,\\
\Psi_{\delta W}&=\int\left[k''(Y+\delta z)(Y_\delta+z)Y_W
+k'(Y+\delta z)Y_{\delta W}\right]d\nu,\\
\Psi_{WW}&=\int\left[k''(Y+\delta z)Y_W^2
+k'(Y+\delta z)Y_{WW}\right]d\nu.
\end{aligned}
\tag{T30.16}
\]

영폭에서 \(Y(0,W)=y\)라 하면 \(\mu_1=0\)을 사용하여

\[
\begin{aligned}
\Psi_\delta&=k'(y)Y_\delta,&\Psi_W&=k'(y)Y_W,\\
\Psi_{\delta\delta}&=k''(y)(Y_\delta^2+\mu_2)
+k'(y)Y_{\delta\delta},\\
\Psi_{\delta W}&=k''(y)Y_\delta Y_W+k'(y)Y_{\delta W},\\
\Psi_{WW}&=k''(y)Y_W^2+k'(y)Y_{WW}.
\end{aligned}
\tag{T30.17}
\]

를 얻는다. 프로파일이 직접 남기는 이차 항은 \(\mu_2 k''\) 하나다. 실제 \(W\)를 고정하면 경로의 이차 도함수에도 T30.1의 \(\mu_2\)가 들어가므로, 그 부분까지 포함해야 최종 이차계수를 얻는다.

끝점에서는 \(f_{\delta,\nu}(a+\delta)=\int k(a+\delta(1+z))d\nu\), \(f_{\delta,\nu}(b-\delta)=\int k(b+\delta(z-1))d\nu\)로 쓴다. 모든 적분점이 원 구간 안이고, 전체 이차 미분은 각각 \((1+\mu_2)k''(a)\), \((1+\mu_2)k''(b)\)다. 고정 \(a\) 또는 \(b\)에서 지원 밖으로 나가는 대역을 정의할 필요가 없다.

## 4. 이 분포족 안의 정확한 상·하단 응답

고정 \(\delta,\nu,W\)에서 \(g=f_{\delta,\nu}\)라고 쓰자. \(0<V<\ell h\)이면

\[
v=m+\frac V\ell\in(m,\beta),\qquad
u=m-\frac Vh\in(\alpha,m).
\tag{T30.18}
\]

중심의 두 후보 측도는

\[
\rho_+=\frac{V}{\ell^2+V}\delta_\alpha
+\frac{\ell^2}{\ell^2+V}\delta_v,
\qquad
\rho_-=\frac{h^2}{h^2+V}\delta_u
+\frac{V}{h^2+V}\delta_\beta.
\tag{T30.19}
\]

각 측도의 질량은 1이고 평균은 \(m\), 분산은 \(V\)임을 대입으로 확인한다. 예를 들어 상단에서 평균 편차는
\(-V\ell/(\ell^2+V)+\ell^2(V/\ell)/(\ell^2+V)=0\), 분산은
\([V\ell^2+V^2]/[\ell^2+V]=V\)다.

이들이 극값을 주는 사실을 PHYS27의 균일 프로파일 결론에서 자동 승계하지 않고 새로 증명한다. \(Q_+\)를 \(g(\alpha),g(v),g'(v)\)에 일치하는 이차 Hermite 다항식으로 두면

\[
g(y)-Q_+(y)=\frac{g'''(\xi_y)}6
(y-\alpha)(y-v)^2\le0.
\tag{T30.20}
\]

\(y\)가 접촉점이 아니면 부등호는 엄격하다. 나머지식은 \(g-Q_+-\lambda(y-\alpha)(y-v)^2\)가 \(\alpha,v,v,y\)의 네 영점(중복도 포함)을 가지도록 \(\lambda\)를 정한 뒤 Rolle 정리를 세 번 적용하여 얻는다. 원 함수는 \(C^3\)면 충분하다.

마찬가지로 \(Q_-\)를 \(g(u),g'(u),g(\beta)\)에 맞추면

\[
g(y)-Q_-(y)=\frac{g'''(\zeta_y)}6
(y-u)^2(y-\beta)\ge0.
\tag{T30.21}
\]

모든 허용 \(\rho\)는 질량·평균·이차 모멘트가 같으므로 이차 다항식 \(Q_\pm\)의 적분도 같다. \(Q_+\)는 \(\rho_+\)의 두 점에서, \(Q_-\)는 \(\rho_-\)의 두 점에서 \(g\)와 같으므로

\[
\int g\,d\rho_-\ \le\ \int g\,d\rho\ \le\ \int g\,d\rho_+.
\tag{T30.22}
\]

엄격한 \(g'''<0\)에서 등호는 각각 해당 두 점에 지지되는 중심 측도를 요구하고, 모멘트 조건이 그 확률을 정한다. \(V=0\)과 \(V=\ell h\)에서는 §2의 유일한 경계 측도로 처리한다.

따라서 **같은 \(\nu\)로 생성한 중심 혼합 분포족 안에서** 정확한 응답 경계는

\[
\boxed{F_{+,\nu}(\delta,W)
=\frac{Vf_{\delta,\nu}(\alpha)+\ell^2f_{\delta,\nu}(m+V/\ell)}{\ell^2+V},}
\]
\[
\boxed{F_{-,\nu}(\delta,W)
=\frac{h^2f_{\delta,\nu}(m-V/h)+Vf_{\delta,\nu}(\beta)}{h^2+V}.}
\tag{T30.23}
\]

이 증명에 별도의 일반 moment-extremizer 정리를 가정할 필요는 없다. 필요한 함수 전제는 T30.8에서 평균 커널로 옮긴 \(g'''<0\)와 허용 중심 모멘트다. 다만 \(\delta>0\)에서 T30.23을 같은 지원·평균·분산을 가진 **모든** 광자 측도의 극값으로 부르지 않는다. 최적화 변수는 정의한 중심 측도 \(\rho\)이고 프로파일 \(\nu\)는 고정되어 있다. \(\delta=0\)에서는 프로파일의 폭이 사라져 이 구별이 퇴화한다.

## 5. 공통 branch 표기와 물리 한쪽 근방

끝점 확률을 먼저 쓰는 공통 표기를 채택한다.

| 경계 | \(s\) | \(R\) | \(e=m-sR\) | \(x=m+sW/R\) | 영폭 정확근 |
|---|---:|---|---|---|---|
| 상단 응답 \(F_{+,\nu}\) | \(+1\) | \(L\) | \(a\) | \(m+W/L\) | \(w_*\) |
| 하단 응답 \(F_{-,\nu}\) | \(-1\) | \(H\) | \(b\) | \(m-W/H\) | \(w_0\) |

\[
r=R-\delta,\quad e_\delta=e+s\delta,\quad
x_{\delta,V}=m+\frac{sV}{r},\quad
p_{\delta,V}=\frac{V}{r^2+V},\quad q_{\delta,V}=1-p_{\delta,V},
\]
\[
G_\nu(\delta,V)=p_{\delta,V}f_{\delta,\nu}(e_\delta)
+q_{\delta,V}f_{\delta,\nu}(x_{\delta,V}),
\qquad F_\nu(\delta,W)=G_\nu(\delta,W-\mu_2\delta^2).
\tag{T30.24}
\]

영폭에서는

\[
\mathcal D=R^2+W,\quad p=W/\mathcal D,\quad
q=R^2/\mathcal D,\quad \Delta k=k(e)-k(x).
\tag{T30.25}
\]

정확 내부근 \(w_j\in(0,LH)\)의 작은 닫힌 근방 \(J\subset(0,LH)\)를 택한다. T30.12 양 끝의 연속성으로 어떤 \(\delta_0>0\)가 존재하여

\[
J\subset\operatorname{int}\mathcal I_{\delta,\nu}
\qquad(0\le\delta\le\delta_0)
\tag{T30.26}
\]

가 된다. 이 물리 반직사각형에서 모든 분모는 양수이고, 중심은 허용구간 안에 남는다. 끝점 경로는 §3의 안쪽 표현으로, 내부 중심은 T30.16으로 미분한다. 확률과 중심의 도함수 및 \(k,k',k''\)는 유계이고 연속이므로 \(F_\delta,F_W,F_{\delta\delta},F_{\delta W},F_{WW}\)가 \(\delta=0\)에 연속적으로 접한다.

\(\nu\)에 원자가 있어도 이 지배수렴·합성법칙은 그대로 성립한다. 물리 폭의 음수 연장이나 원 지원 밖의 커널값은 사용하지 않는다. \(\delta_0\)의 존재만 보이며 수치 하한을 주지 않는다.

또한 고정 \(\delta\)에서 \(V_W=1\)이다. \(g=f_{\delta,\nu}\), \(x-e_\delta=s(r^2+V)/r\)를 사용하면

\[
F_W=
\frac{g(e_\delta)-g(x)+(x-e_\delta)g'(x)}{(x-e_\delta)^2}
=\int_0^1 t\,g''(e_\delta+t(x-e_\delta))dt>0.
\tag{T30.27}
\]

이는 각 허용 폭에서 실제 분산에 대한 엄격 증가성이다. 서로 다른 폭이나 프로파일 사이의 응답 순서를 주장하는 식이 아니다.

## 6. 영폭의 \(B,C,M,N\)와 기하 항은 프로파일에 무관하다

모든 양을 \((\delta,W)=(0,W)\)에서 평가하고

\[
B=F_\delta,\quad C=F_W,\quad
K_\nu=F_{\delta\delta},\quad M=F_{\delta W},\quad N=F_{WW}
\tag{T30.28}
\]

로 둔다. \(F_\nu(0,W)=pk_e+qk_x\)는 \(\nu\)에 의존하지 않는다. \(V_\delta(0)=0\), \(V_{\delta\delta}(0)=-2\mu_2\), \(V_W=1\)이며 T30.17의 일차 및 혼합 항에는 \(\mu_2\)가 없다.

그 결과 PHYS29에서 읽은 일반식을 영점 조건 없이 얻는다.

\[
\boxed{B=\frac{sW}{\mathcal D}(k'_e+k'_x)
+\frac{2RW}{\mathcal D^2}\Delta k,}
\]
\[
\boxed{C=\frac{R^2}{\mathcal D^2}\Delta k
+\frac{sR}{\mathcal D}k'_x
=\int_0^1t\,k''(e+t(x-e))dt>0,}
\tag{T30.29}
\]

\[
\boxed{M=\frac{sR^2k'_e+s(R^2-2W)k'_x}{\mathcal D^2}
+\frac{Wk''_x}{R\mathcal D}
+\frac{2R(R^2-W)\Delta k}{\mathcal D^3},}
\]
\[
\boxed{N=\frac{k''_x}{\mathcal D}
-\frac{2sRk'_x}{\mathcal D^2}
-\frac{2R^2\Delta k}{\mathcal D^3}.}
\tag{T30.30}
\]

T30.24의 확률·중심을 곱미분하여 T30.29를 얻고, \(x_W=s/R\), \(p_W=R^2/\mathcal D^2\)를 사용해 이를 \(W\)로 미분하면 T30.30이다. 예를 들어 \(B=p_\delta\Delta k+psk'_e+q(sW/R^2)k'_x\)이며, \(p_\delta=2RW/\mathcal D^2\), \(p=W/\mathcal D\), \(q=R^2/\mathcal D\)를 대입하면 표시한 식이 된다. 이 식들은 정확한 영점 조건을 쓰지 않으며 모든 내부 \(W\)에서 성립한다.

고정 중심 분산 \(V\)에서 영폭의 위치·확률 도함수는

\[
e_\delta'=s,\quad e_\delta''=0,\quad
x_\delta'=\frac{sW}{R^2},\quad
x_\delta''=\frac{2sW}{R^3},\quad
p_\delta'=\frac{2RW}{\mathcal D^2},\quad
p_\delta''=\frac{8R^2W}{\mathcal D^3}-\frac{2W}{\mathcal D^2}
\tag{T30.31}
\]

이다. 이 여섯 식에는 \(\nu\)가 없다. 이 도함수들로 생기는 \(G_{\delta\delta}\)의 일곱 기하 항을 합쳐 \(\mathcal G\)로 둔다.

| 고정 \(V\)의 기여 | \(\mathcal G\)의 항 |
|---|---|
| 끝점 속도 제곱 | \(p k''_e\) |
| 내부 중심 속도 제곱 | \(qW^2k''_x/R^4\) |
| 끝점 가속도 | \(0\) |
| 내부 중심 가속도 | \(2sqWk'_x/R^3\) |
| 확률 가속도 | \((8R^2W/\mathcal D^3-2W/\mathcal D^2)\Delta k\) |
| 확률×끝점 이동 | \(4sRWk'_e/\mathcal D^2\) |
| 확률×내부 중심 이동 | \(-4sW^2k'_x/(R\mathcal D^2)\) |

평균화 자체의 기여는 이 표에 넣지 않았고, 다음 절에서 \(\mu_2\mathcal H\)로 한 번만 더한다. 실제 \(V''\)에 의한 내부 중심·확률 가속도도 다음 절의 \(-2\mu_2C\)에 포함한다. 따라서 고정 \(V\) 표에 이미 포함되었다고 중복 계수하지 않는다.

## 7. 프로파일 의존성의 정확한 이차 분해

T30.17과 T30.31로

\[
G_{\nu,\delta\delta}(0,W)=\mathcal G+\mu_2\mathcal H,
\qquad \mathcal H=p k''_e+q k''_x>0.
\tag{T30.32}
\]

T30.24의 합성법칙은 영폭에서

\[
F_{\delta\delta}=G_{\delta\delta}-2\mu_2G_V,
\qquad F_{\delta W}=G_{\delta V},\qquad F_{WW}=G_{VV}.
\tag{T30.33}
\]

\(G_V=C\)이므로

\[
\boxed{K_\nu=\mathcal G+\mu_2\mathcal H-2\mu_2C,}
\]
\[
\boxed{K_\nu-K_{\mathrm{unif}}
=\left(\mu_2-\frac13\right)(\mathcal H-2C).}
\tag{T30.34}
\]

이는 임의의 내부 \(W\)에서 성립하는 영폭 편미분 항등식이다. 따라서 \(B,C,M,N\) 및 \(\mathcal G\)의 일곱 항은 프로파일 공통이고, \(K\)에서 바뀌는 것은 평균화와 중심 분산 보정의 두 항뿐이다.

고정 실제 \(W\)에서 \(V''=-2\mu_2\)에 의한 추가 중심·확률 가속도는 각각

\[
x_{\delta\delta}^{V}=-\frac{2s\mu_2}{R},\qquad
p_{\delta\delta}^{V}=-\frac{2\mu_2R^2}{\mathcal D^2}.
\tag{T30.35}
\]

따라서 그 기여는

\[
K_V=-\frac{2\mu_2R^2}{\mathcal D^2}\Delta k
-\frac{2s\mu_2q}{R}k'_x=-2\mu_2C.
\tag{T30.36}
\]

확률 부분을 버리고 내부 중심의 가속도만 바꾸면 T30.36을 얻지 못한다. 반대로 이 두 항을 직접 넣었으면 \(-2\mu_2C\)를 다시 더하지 않는다.

## 8. 정확 내부근의 한쪽 \(C^2\) 전개와 보편식

영폭의 \(F_\nu(0,W)\)가 프로파일 공통이므로 정확한 근 \(w_j\)도 공통이다. §5의 물리 반직사각형을 줄여 \(F_W\)의 양의 하한을 확보한다. \(w_j\) 양쪽의 고정 분산에서 \(F(0,W)\)는 부호가 다르고, 연속성은 작은 양의 폭에서 이 부호를 보존한다. 중간값 정리와 T30.27로 유일한 근 \(W_{j,\nu}(\delta)\)가 존재하며, 끼우는 구간을 줄이면 \(W_{j,\nu}(\delta)\to w_j\)다.

평균값 정리로 \(F(\delta,w_j)=O(\delta)\)와 \(F_W\ge C_{\min}>0\)를 결합하면 \(W_{j,\nu}(\delta)-w_j=O(\delta)\)다. 따라서 일차 차분몫에서

\[
W_{j,\nu}'(0^+)=-\frac{B_j}{C_j}=:c_j.
\tag{T30.37}
\]

물리 내부 \(\delta>0\)에서는 통상적인 암묵함수 미분으로

\[
W'=-\frac{F_\delta}{F_W},\qquad
W''=-\frac{F_{\delta\delta}+2F_{\delta W}W'
+F_{WW}(W')^2}{F_W}.
\tag{T30.38}
\]

를 얻는다. 모든 편미분이 \(\delta=0\)에 연속적으로 접하므로 첫 식은 \(c_j\)로, 둘째 식은 유한한 극한으로 접한다. \(W'\)의 차분몫에 평균값 정리 또는 적분식을 적용하면 이 둘째 극한은 실제 \(W''(0^+)\)다. 이로써 형식적인 계수 비교를 넘어 물리 한쪽 \(C^2\) 근이 정당화된다.

\[
\boxed{d_{j,\nu}=\frac12W_{j,\nu}''(0^+)
=-\frac{K_{j,\nu}+2M_jc_j+N_jc_j^2}{2C_j}.}
\tag{T30.39}
\]

근 전개의 나머지는 물리 구간 안의 적분식
\[
W(\delta)=w+c\delta+\int_0^\delta(\delta-t)W''(t)dt
=w+c\delta+\tfrac12W''(0^+)\delta^2+o(\delta^2)
\]
에서 직접 얻는다. 연속적인 우이차 미분의 존재를 사용하며, 나머지의 수치 상계나 유효 폭은 계산하지 않았다.

T30.34에서 바뀌는 \(K\) 하나를 대입하면 T30.3을 얻는다. \(c_j\)가 공통이므로 두 암묵근 항도 프로파일에 무관하다. 완전한 항별 분해는

\[
d_{j,\nu}
=-\frac{\mathcal G_j}{2C_j}
\underbrace{-\frac{\mu_2\mathcal H_j}{2C_j}}_{d_{\mathrm{avg},\nu}}
\underbrace{+\mu_2}_{d_{V,\nu}}
-\frac{M_jc_j}{C_j}-\frac{N_jc_j^2}{2C_j}.
\tag{T30.40}
\]

즉

\[
\boxed{d_{V,\nu}=\mu_2,\qquad
d_{\mathrm{avg},\nu}=-\frac{\mu_2\mathcal H_j}{2C_j}.}
\tag{T30.41}
\]

\(\mu_2>0\)에서는 평균 기여가 엄격히 음수이고, \(\mu_2=0\)이면 두 프로파일 기여가 모두 0이다. 전체 \(d\)와
\(\Xi_j:=1-\mathcal H_j/(2C_j)\)의 보편적인 부호는 여기서 주장하지 않는다.

같은 \(\mu_2\)를 가진 두 고정 대칭 프로파일 \(\nu,\widetilde\nu\)는 모든 영폭 이차 편미분과 근 계수를 공유한다. 각 근의 한쪽 전개를 빼면

\[
W_{j,\nu}(\delta)-W_{j,\widetilde\nu}(\delta)=o(\delta^2).
\tag{T30.42}
\]

이 식은 국소 점근식이다. 같은 \(\mu_2\)만으로 양의 폭의 커널 평균, 응답, 문턱 전체가 같다는 결론은 나오지 않는다. 이 문서의 승격 요청은 이차까지의 주장으로 제한한다.

같은 프로파일을 양쪽 branch에 쓰므로 문턱 간격의 이차계수에서는 \(d_{V,\nu}=\mu_2\)가 정확히 상쇄된다. 구체적으로

\[
(d_{0,\nu}-d_{*,\nu})-(d_{0,\mathrm{unif}}-d_{*,\mathrm{unif}})
=-\left(\mu_2-\frac13\right)
\left(\frac{\mathcal H_0}{2C_0}-\frac{\mathcal H_*}{2C_*}\right).
\tag{T30.43}
\]

간격 변화의 부호나 크기는 실제 계수에 달려 있으며 사전 판정 조건이 아니다.

## 9. 저장된 기준점의 비영 응답 \(A\)를 유지하는 식

저장된 유한 기준점 \(\widehat w\)에서는 정확한 실수 함수의

\[
A=F_\nu(0,\widehat w)
\tag{T30.44}
\]

를 정의한다. 영폭 함수가 공통이므로 \(A\)도 프로파일 공통이다. 일반적으로 \(A\ne0\)다. \(C\ne0\)에서 T30.37·39의 같은 일반 편미분 식으로 만든 \(\widehat c,\widehat d_\nu\)는 **동일 \(F_\nu=A\) 수준**의 한쪽 계수이며

\[
F_\nu(\delta,\widehat w+\widehat c\delta+
\widehat d_\nu\delta^2)=A+o(\delta^2).
\tag{T30.45}
\]

를 만족한다. 따라서 T30.3의 프로파일 관계도 동일 A-level의 계수 사이에서 성립한다. 이를 정확한 영점 계수로 무조건 바꾸지 않는다. 실제 Decimal 결과에는 유한 산술의 반올림도 추가로 남는다.

분자 경로의 교차 확인에는

\[
\mathscr Q_\nu=(R-\delta)^2+W-\mu_2\delta^2,
\]
\[
\mathscr N_\nu=(W-\mu_2\delta^2)f_{\delta,\nu}(e_\delta)
+(R-\delta)^2 f_{\delta,\nu}(x_{\delta,V}),\qquad
F_\nu=\mathscr N_\nu/\mathscr Q_\nu
\tag{T30.46}
\]

를 사용한다. 영폭에서

\[
\mathscr Q=\mathcal D,\quad \mathscr Q_\delta=-2R,
\quad \mathscr Q_W=1,\quad
\boxed{\mathscr Q_{\delta\delta}=2(1-\mu_2)},\quad
\mathscr Q_{\delta W}=\mathscr Q_{WW}=0.
\tag{T30.47}
\]

곱의 미분법은

\[
\begin{aligned}
\mathscr N_\delta&=\mathcal D B-2RA,&
\mathscr N_W&=\mathcal D C+A,\\
\mathscr N_{\delta\delta}&=\mathcal D K_\nu-4RB+2(1-\mu_2)A,\\
\mathscr N_{\delta W}&=\mathcal D M-2RC+B,&
\mathscr N_{WW}&=\mathcal D N+2C.
\end{aligned}
\tag{T30.48}
\]

를 준다. 그러므로 잔차를 보존하는 정확한 식은

\[
\boxed{\widehat c=-\frac{\mathscr N_\delta+2RA}{\mathscr N_W-A},}
\]
\[
\boxed{\widehat d_\nu
=-\frac{\mathscr N_{\delta\delta}
+2\mathscr N_{\delta W}\widehat c+
\mathscr N_{WW}\widehat c^2-2(1-\mu_2)A}
{2(\mathscr N_W-A)}.}
\tag{T30.49}
\]

둘째 식에서는 \(B+C\widehat c=0\)를 사용했다. \(\mathscr N_W-A=\mathcal D C>0\)다. 정확한 영점 \(A=0\)에서만 A 항들을 버릴 수 있다. 균일 프로파일의 \(\mu_2=1/3\)은 PHYS29의 \(\mathscr Q_{\delta\delta}=4/3\)과 잔차 보정으로 돌아간다.

저장된 작은 응답값, 두 대수 경로의 일치, 파일의 동일성은 정확한 근의 수치 오차 상계가 아니다. 새 근 탐색·보정 없이 원 \(J\), 원자·기체 입력 및 근 근사 오차의 한계를 유지한다.

## 10. 원자·밀도와 해석적 극한 점검

**원자 프로파일.** \(\mu_2=0\)이면 \(z^2\ge0\)의 적분이 0이므로 \(\nu=\delta_0\)다. 그래도 중심 허용구간은 계약대로 \([a+\delta,b-\delta]\)로 축소된다. 따라서 평균화 및 분산 보정 기여가 사라져도 위치·확률 이동과 일차 문턱 이동이 사라진다고 말할 수 없다. \(\mu_2=1\)이면 \(1-z^2\ge0\)의 적분이 0이므로 \(\nu\)는 \(\{-1,+1\}\)에 지지되고, 대칭성으로 두 확률은 각각 \(1/2\)다. 두 경우 모두 함수 미분 증명은 유효하다.

**절대연속성.** \(\nu(dz)=h_\nu(z)dz\)이고 \(\delta>0\)이면, \(h_\nu\)를 \([-1,1]\) 밖에서 0으로 연장하여

\[
\frac{dP_{\delta,\rho,\nu}}{dE}
=\int\frac1\delta h_\nu\!\left(\frac{E-y}{\delta}\right)d\rho(y)
\tag{T30.50}
\]

를 얻는다. Tonelli 정리로 이 비음수 밀도의 적분은 1이다. \(h_\nu\)는 적분 가능하면 충분하며 매끄러울 필요가 없다. 원자 \(\nu\)를 허용하는 전체 계약에서는 광자 측도의 절대연속성을 보장하지 않는다. 특히 중심 극값 측도와 원자 프로파일의 조합은 원자 광자 측도를 만들 수 있다. 반대로 일반 중심 측도와의 합성이 어떤 경우에도 밀도를 가질 수 없다고 주장하지는 않는다.

**좁은 실제 지원.** \(r_\nu=\sup\{|z|:z\in\operatorname{supp}\nu\}<1\)로 실제 지원 반경을 정의하면 개별 프로파일의 실제 반폭은 \(r_\nu\delta\)이고 \(\delta\)는 공통 외곽 한계다. 단지 \(\operatorname{supp}\nu\subset[-r,r]\)라는 포함만 알면 실제 반폭은 \(r\delta\) 이하라는 뜻이다. 중심 구간을 \([a+r_\nu\delta,b-r_\nu\delta]\)로 바꾸면 이미 일차 기하 변화부터 달라지는 별도 계약이므로 여기서는 바꾸지 않는다.

**정확한 예시 모멘트.** 수치 비교에 사용할 수 있는 두 고정 프로파일은

\[
d\nu_{\rm unif}=\tfrac12\mathbf1_{[-1,1]}dz,\qquad
d\nu_{\rm tri}=(1-|z|)\mathbf1_{[-1,1]}dz.
\tag{T30.51}
\]

각 밀도는 대칭이고 비음수다. 정규화는 \(\frac12\int_{-1}^1dz=1\), \(2\int_0^1(1-z)dz=1\)이며, 이차 모멘트는

\[
\mu_{2,\rm unif}=\frac12\int_{-1}^1 z^2dz=\frac13,
\qquad
\mu_{2,\rm tri}=2\int_0^1z^2(1-z)dz=\frac16.
\tag{T30.52}
\]

이다. 이는 다항식 원시함수의 해석적 계산이며 수치 적분 실행이 아니다. 이 기여에서 두 프로파일의 새 물리 계수 소수값을 계산하지 않았다.

**이차 커널의 정확한 퇴화.** 시험함수 \(k_{\rm quad}(E)=a_0+a_1E+a_2E^2\)에는 T30.9의 실제 모멘트가

\[
F_{\rm quad}(\delta,W)=a_0+a_1m+a_2(m^2+W)
\tag{T30.53}
\]

를 준다. 따라서 \(C=a_2\), \(B=K=M=N=0\), \(\mathcal H=2a_2\), \(\mathcal G=0\)다. \(a_2\ne0\)이고 내부근이 있으면 \(c=d=0\)이고

\[
d_{\rm avg}=-\mu_2,\qquad d_V=+\mu_2,
\qquad \Xi=1-\mathcal H/(2C)=0
\tag{T30.54}
\]

가 정확히 상쇄된다. 이차 시험함수에서는 \(k'''=0\)이므로 엄격한 극값 측도 유일성의 가정을 제거했다는 점을 명시한다. 커널이 affine이면 \(C=0\)이므로 여기의 단순근 공식에 대입하지 않는다. 이는 직접 기호 대입이며 새 toy 수치 프로그램의 결과가 아니다.

## 11. 차원·부호·증거 상태와 종료

| 양 | 단위 |
|---|---|
| \(z,\mu_2,p,q,\Xi,d\) | 무차원 |
| \(a,b,m,L,H,\delta,e,x,R,c\) | eV |
| \(W,V,w_j,\mathcal D\) | eV² |
| \(k,F,A\) | s⁻⁴ |
| \(B\) | s⁻⁴ eV⁻¹ |
| \(C,K,\mathcal H,\mathcal G\) | s⁻⁴ eV⁻² |
| \(M\) | s⁻⁴ eV⁻³ |
| \(N\) | s⁻⁴ eV⁻⁴ |

\(K,2Mc,Nc^2\)는 같은 차원이고, \(2C\)로 나누면 \(d\)는 무차원이다. \(\mu_2\mathcal H\)와 \(-2\mu_2C\)도 같은 차원이다. 커널 전체의 공통 비영 배율은 \(c,d,\Xi\)의 비에서 소거되지만, 이는 고정 정규화의 대수 성질이며 입력이나 물리 모델을 바꿀 권한이 아니다.

| 점검 또는 주장 | 근거 상태 | 실제 근거와 한계 |
|---|---|---|
| 지지·질량·평균·실제 분산과 허용 구간 | derived | T30.7–12, 정확한 모멘트 적분 |
| 원자 측도를 포함한 평균 커널 정칙성·도함수 부호 | conditional derived | T30.14–17; 상속된 T30.8을 사용 |
| 공통 프로파일 중심 혼합족의 상·하단 경계 | conditional derived | T30.19–23, Hermite 이차 상·하한; unrestricted photon class 제외 |
| 물리 한쪽 \(C^2\) 근과 \(d=W''(0^+)/2\) | conditional derived | T30.26–27, T30.37–39; 정확 내부근 전제 |
| \(B,C,M,N,\mathcal G\)의 프로파일 독립성 | derived | T30.17, T30.29–33; 영폭에서만 |
| \(K\) 및 \(d\)의 \(\mu_2\) 의존성 | derived | T30.34–43; 고정 대칭 프로파일·같은 중심 구간 |
| 저장 A-level과 분자 잔차 보정 | derived | T30.44–49; A를 0으로 바꾸지 않음 |
| 이차 커널 극한·차원 검사 | derived | T30.53–54 및 단위 표; 수치 실행 0 |
| 새 저장 계수의 수치 조합·구현·재현 | 이 기여에서는 NOT_RUN | 별도 수치 기여와 실제 실행 기록의 범위 |
| 최종 독립 판정 | 이 기여자의 역할 아님 | NONBLIND 후보 생성자, 생성·설계와 분리된 최종 reviewer 필요 |

이 표의 직접 유도 점검은 **THEORY_CONTRIBUTOR_SELF_CHECK**다. 문헌 조사에 근거한 우선권·신규성 주장, 물리 입력의 독립 검증, 원자·기체·\(J\) 불확실성의 제거, native 동등성, 유한 시간·유한 \(\epsilon\)·emitter·cosmological history admission을 추가하지 않는다. 비대칭 프로파일이나 \(\delta,W\), 중심 또는 branch에 따라 바뀌는 프로파일은 본 정리의 계약에 포함하지 않는다. 대칭 프로파일이어도 중심 구간이 선형으로 움직이므로 근의 일차 항이 대칭성만으로 사라지지는 않는다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**을 유지한다. 이 기여에서 외부 문헌을 새로 열람하지 않았고, 원전 열람을 했다고 표시하지 않는다. 위 새 관계는 재현 가능한 직접 증명과 상속한 함수 전제의 조합이다.

다음 한 질문은 **같은 \(\mu_2\)를 가지지만 고차 모멘트가 다른 두 대칭 프로파일의 문턱 차이가 어느 다음 차수에서 처음 나타나는가**다. 필요한 추가 커널 정칙성과 고차 계수의 존재를 먼저 고정할 별도 연구의 제안이며, 여기서는 그 고차 정리나 수치 계산을 수행하지 않았다.

기계 판독 주장 목록은 [THEORY_CLAIMS.json](THEORY_CLAIMS.json), 실제 source 읽기·해시·실행 0의 범위·기여자의 도구 사건은 [PROVENANCE.json](PROVENANCE.json)에 있다.
