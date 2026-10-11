# PHYS29 — 작은 균일 대역폭의 이차 문턱 이동과 항별 분해

연구: **REI-PHYS29-20261011 · SMALL_WIDTH_SECOND_ORDER_DECOMPOSITION**  
기여자: **/root/phys29_theory**, 같은 대화 안의 이론 후보 생성자, **NONBLIND**  
모델 근거: trusted developer designation **GPT-6 Astra Pro**; 연구 하네스 gpt6-astra v4.0.0  
근거 상태: **derived, 동결 커널·단순 내부 정확근 존재 전제에 조건부**  
판정 범위: 이론 후보와 자체 대수 점검. **독립 최종 PROMOTE 판정이 아니다.**

## 0. 핵심 결과

실제 광자 분산 \(W\)를 고정한 편미분으로

\[
B=F_\delta,\quad C=F_W,\quad
K=F_{\delta\delta},\quad M=F_{\delta W},\quad N=F_{WW}
\quad\text{at }(0,w_j)
\]

를 정의하면 두 정확한 분산 문턱은 물리적인 \(\delta\downarrow0\)에서

\[
\boxed{W_j(\delta)=w_j+c_j\delta+d_j\delta^2+o(\delta^2),\qquad
c_j=-\frac BC,\qquad
d_j=-\frac{K+2Mc_j+Nc_j^2}{2C}.}
\tag{T29.1}
\]

를 갖는다. 여기서 \(d_j=W_j''(0^+)/2\)는 전체 이차 미분의 **절반**이다. \(\delta\)는 eV 단위의 반폭, \(c_j\)는 eV, \(d_j\)는 무차원이다. 아래의 한쪽 \(C^2\) 논증은 단지 형식적 이차 계수를 비교한 것이 아니라 실제 우이차 미분의 존재까지 보인다.

고정 실제 \(W\)에서 \(V=W-\delta^2/3\)를 함께 미분하면

\[
K=K_{\rm average}+K_{\rm support}-\frac23C.
\tag{T29.2}
\]

따라서 이차 문턱 계수에서 중심 분산 보정은 정확히

\[
\boxed{d_V=+\frac13,}
\qquad
\boxed{d_{\rm average}
=-\frac{p\,k''(e)+(1-p)k''(x)}{6C}<0.}
\tag{T29.3}
\]

다. \(d_V\)와 \(d_{\rm average}\)는 전체 \(d_j\)의 항별 기여다. 끝점·내부 중심·확률의 지지구간 이동과 암묵근 교차·곡률항이 추가되므로 이 두 항만으로 \(d_j\) 전체의 부호를 정하지 않는다. \(d_*,d_0\)의 부호나 비영성은 사전 가정하지 않았다.

이 기여에서 물리 커널 평가, 새 과학 main, 새 근 탐색, 과거 main/suite/root, 수치 유한차분·적분·폭 sweep은 모두 **0회**다. 새 계수의 소수값과 기존 \(\delta=.05\) 비교는 별도의 동결된 수치 실행 대상이다.

## 1. 현재 계약과 소비한 전제

현재 [PHYSICS_CONTRACT.json](../../PHYSICS_CONTRACT.json)과 실제 [PHYS29 인수문](../../inputs/PHYS28/next/PHYS29_NEXT_HANDOFF_KO.md)을 소비한다. 선행 유도는 [PHYS28](../../inputs/PHYS28/contributions/theory/DERIVATION_KO.md) 전체, [PHYS27](../../inputs/PHYS27/contributions/theory/FINITE_WIDTH_DERIVATION_KO.md)의 정의·평균화·경계식·단순근·영폭 극한 부분, [PHYS26](../../inputs/PHYS26/contributions/theory/ENVELOPE_DERIVATION_KO.md)의 물리 정의·두 선 측도·분산 기울기·정확근 부분을 실제 읽었다. 정확한 읽기 범위와 파일 identity는 [PROVENANCE.json](PROVENANCE.json)에 남긴다.

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad H=b-m=6.58\qquad({\rm eV}).
\tag{T29.4}
\]

\[
\alpha=a+\delta,\quad \beta=b-\delta,\quad
\ell=L-\delta,\quad h=H-\delta,\qquad
V=W-\frac{\delta^2}{3}.
\tag{T29.5}
\]

실제 허용 분산은

\[
\mathcal I_\delta=
\left[\frac{\delta^2}{3},\,
(L-\delta)(H-\delta)+\frac{\delta^2}{3}\right].
\tag{T29.6}
\]

중심 측도의 각 원자점을 반폭 \(\delta\)의 균일 대역으로 바꾸므로 질량1·평균 \(m\)·실제 광자 분산 \(W=V+\delta^2/3\)를 정확히 유지한다. 지원구간 밖으로 대역을 잘라내거나 재정규화하지 않는다.

현재 상속되는 함수 전제는

\[
k\in C^3([a,b]),\qquad k''>0,\qquad k'''<0.
\tag{T29.7}
\]

그 가운데 새 이차 편미분의 존재에는 \(k\in C^2\)이면 충분하다. \(k''>0\)는 \(F_W>0\)를, \(k'''<0\)는 상속된 모멘트 경계와 일차 이동 방향을 담당한다. 두 정확근의 존재에는 이 곡률 조건 외에 PHYS26의 끝값 부호 전제가 필요하다. 그 끝값 부호와 저장된 근의 근거 등급은 **상속 수치 지원**이며 새 interval 근 인증으로 올리지 않는다.

동결된 source binary64 리터럴은 정확한 실수로, PHYS22의 직렬화 수치 \(J\)는 기록된 전체 소수로 해석한다. 기체 상태·\(J\)·지원구간·평균·광자 수를 폭과 함께 바꾸지 않는다. 원 \(J\)나 원자 자료의 불확실성을 둘러싸지 않는다.

\(k,A,F\)는 초기 HeIII의 \(\epsilon^2t^4\) 응답계수이며 단위는 s⁻⁴다. Metric \((-+++)\), gas-comoving proper seconds, 열 변수 \(w\) in eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\), 시간계수의 추가 factorial 없음, 기존 정규화를 한 번만 포함한다. 이하의 \(W\)는 분산이며 기체 열 변수 \(w\)와 다르다.

## 2. 상단과 하단을 함께 쓰는 정확한 식

두 경계에서 끝점 확률을 먼저 놓는 공통 표기를 쓴다.

| 경계 | \(s\) | \(R\) | 원 끝점 \(e=m-sR\) | 영폭 내부 중심 \(x=m+sW/R\) | 정확근 이름 |
|---|---:|---|---|---|---|
| 상단 \(A_{\delta,+}\) | \(+1\) | \(L\) | \(a\) | \(v=m+W/L\) | \(w_*=V_{*,0}\) |
| 하단 \(A_{\delta,-}\) | \(-1\) | \(H\) | \(b\) | \(u=m-W/H\) | \(w_0=W_{0,0}\) |

하단도 끝점 \(b\)의 확률을 \(p\)로 둔다. 이는 PHYS27 하단 식의 항 순서만 바꾼 것이다. 정의

\[
r_\delta=R-\delta,\quad e_\delta=e+s\delta,\quad
x_{\delta,V}=m+\frac{sV}{r_\delta},\quad
p_{\delta,V}=\frac{V}{r_\delta^2+V},
\]
\[
f_\delta(y)=\frac12\int_{-1}^{1}k(y+\delta z)\,dz
\tag{T29.8}
\]

로

\[
G(\delta,V)=p_{\delta,V}f_\delta(e_\delta)
 +(1-p_{\delta,V})f_\delta(x_{\delta,V}),
\]
\[
\boxed{F(\delta,W)=G\!\left(\delta,W-\frac{\delta^2}{3}\right).}
\tag{T29.9}
\]

이는 PHYS27 T27.22–23의 정확한 두 경계식이다. \(G\)의 \(V\)는 미분 분해를 위한 독립 좌표다. 최종 물리 비교의 고정 변수는 언제나 실제 \(W\)다.

영폭의 기호를

\[
\mathcal D=R^2+W,\quad p=\frac W{\mathcal D},\quad
q=1-p=\frac{R^2}{\mathcal D},\quad
\Delta k=k(e)-k(x)
\tag{T29.10}
\]

로 줄인다. \(\mathcal D\)는 양의 분모이고 \(\Delta k\)는 커널 차이다.

## 3. 물리적인 한쪽 \(C^2\) 정칙성

정확한 내부 단순근 \(w_j\in(0,LH)\)를 고정한다. 작은 닫힌 구간 \(J=[w_j-\eta,w_j+\eta]\subset(0,LH)\)를 택하면 허용 범위 양 끝의 연속성에 의해 어떤 \(\delta_0>0\)가 존재하여

\[
J\subset\operatorname{int}\mathcal I_\delta
\quad(0\le\delta\le\delta_0).
\tag{T29.11}
\]

따라서 반직사각형 \([0,\delta_0]\times J\) 전체가 물리적으로 허용된다. \(\delta_0\)의 수치 하한이나 \(.05\) 포함 여부는 여기서 인증하지 않는다.

내부 대역은 이 반직사각형에서 원 지원구간 안에 있다. 끝점 대역은

\[
f_\delta(a+\delta)
=\frac12\int_{-1}^{1}k(a+\delta(1+z))\,dz,
\]
\[
f_\delta(b-\delta)
=\frac12\int_{-1}^{1}k(b+\delta(z-1))\,dz
\tag{T29.12}
\]

로 쓴다. 모든 적분점은 \([a,b]\) 안이다. \(\delta=0\)에서 \(k\)의 끝점 도함수는 구간 안에서의 한쪽 미분과 연속 극한으로 해석한다.

적분점 좌표·확률은 양의 분모를 가진 \(C^2\) 함수이며 \(k,k',k''\)는 콤팩트 구간에서 연속·유계다. 따라서 합성함수의 도함수와 적분을 교환할 수 있고, \(F_\delta,F_W,F_{\delta\delta},F_{\delta W},F_{WW}\)는 반직사각형에 연속적으로 접한다. 폭에 대해서는 오른쪽 \(C^2\)라는 뜻이다. 고정 끝점 \(a\) 또는 \(b\)에서 물리적으로 불가능한 양의 폭을 먼저 정의할 필요가 없다.

이 논증은 음의 물리 폭, \([a,b]\) 밖의 커널 연장, 서로 다른 양의 폭의 분포족 포함을 사용하지 않는다. 내부 \(\delta>0\)에서의 통상적인 국소 미분은 이 물리 반직사각형 안에서만 수행한다.

## 4. 대역 평균과 위치 변화의 이차 미분

물리적으로 허용되는 한 중심 경로 \(X(\delta)\)에 대해 \(X(0)=y\), \(X'(0)=v_y\), \(X''(0)=a_y\)라 하자. 균일 변수의 모멘트 \(\langle z\rangle=0\), \(\langle z^2\rangle=1/3\)를 직접 사용하면

\[
\left.\frac{d}{d\delta}
f_\delta(X(\delta))\right|_{0^+}=k'(y)v_y,
\]
\[
\boxed{\left.\frac{d^2}{d\delta^2}
f_\delta(X(\delta))\right|_{0^+}
=k''(y)\!\left(v_y^2+\frac13\right)+k'(y)a_y.}
\tag{T29.13}
\]

\(1/3\)이 대역 평균의 **전체 이차 미분**이다. Taylor의 \(\delta^2\) 계수는 \(k''(y)/6\)이다. 속도와 균일 변수의 교차항 \(2v_y\langle z\rangle\)는 정확히 0이다. 끝점 대역에서도 T29.12를 직접 미분하면 같은 식을 얻는다. 예를 들어 상단 끝점의 전체 이차 미분은 \(k''(a)\langle(1+z)^2\rangle=4k''(a)/3\)이며 끝점 이동의 \(k''(a)\)와 평균의 \(k''(a)/3\)로 나뉜다.

## 5. 실제 \(W\)를 고정한 기초 도함수

다음 표는 모두 \(\delta=0\)에서의 편미분이다. \(x_\delta=x_{\delta,V(\delta,W)}\), \(p_\delta=p_{\delta,V(\delta,W)}\)를 물리 경로로 쓴다.

| 양 | \(\partial_\delta\) | \(\partial_{\delta\delta}\) | \(\partial_W\) | \(\partial_{\delta W}\) | \(\partial_{WW}\) |
|---|---|---|---|---|---|
| \(V\) | \(0\) | \(-2/3\) | \(1\) | \(0\) | \(0\) |
| \(e_\delta\) | \(s\) | \(0\) | \(0\) | \(0\) | \(0\) |
| \(x_\delta\) | \(sW/R^2\) | \(2sW/R^3-2s/(3R)\) | \(s/R\) | \(s/R^2\) | \(0\) |
| \(p_\delta\) | \(2RW/\mathcal D^2\) | \(8R^2W/\mathcal D^3-2W/\mathcal D^2-2R^2/(3\mathcal D^2)\) | \(R^2/\mathcal D^2\) | \(2R(R^2-W)/\mathcal D^3\) | \(-2R^2/\mathcal D^3\) |

고정 중심 분산 \(V=W\)에서의 지지구간 이동만 따로 두면

\[
x_{\delta\delta}^{\rm support}=\frac{2sW}{R^3},
\qquad
p_{\delta\delta}^{\rm support}
=\frac{8R^2W}{\mathcal D^3}-\frac{2W}{\mathcal D^2}.
\tag{T29.14}
\]

실제 \(V''=-2/3\)의 추가 기여는

\[
x_{\delta\delta}^{V}=-\frac{2s}{3R},
\qquad p_{\delta\delta}^{V}=-\frac{2R^2}{3\mathcal D^2}.
\tag{T29.15}
\]

다. 전체 이차 중심·확률 도함수를 이미 사용했다면 T29.15를 다시 더하지 않는다. 아래의 분해는 T29.14와 별도 \(V\) 보정을 사용하여 이중 계수를 피한다.

## 6. \(B,C,K,M,N\)의 명시적 일반식

이 절의 식은 정확근 조건을 전혀 쓰지 않는다. 모든 \(0<W<LH\)에서 성립한다. \(k_e,k_x\) 및 그 도함수는 각각 \(e,x\)에서 평가한다.

### 6.1. 일차 폭 미분과 양의 분산 기울기

\[
\boxed{B
=\frac{sW}{\mathcal D}(k'_e+k'_x)
 +\frac{2RW}{\mathcal D^2}\Delta k,}
\tag{T29.16}
\]

\[
\boxed{C
=\frac{R^2}{\mathcal D^2}\Delta k
 +\frac{sR}{\mathcal D}k'_x.}
\tag{T29.17}
\]

T29.16은 PHYS28의 두 일반 \(B_\pm\) 식과 같다. \(x-e=s\mathcal D/R\)를 대입하면

\[
C=\frac{k(e)-k(x)+(x-e)k'(x)}{(x-e)^2}
=\int_0^1(1-t)k''(x+t(e-x))\,dt>0.
\tag{T29.18}
\]

마지막 식은 \(k\)의 이차 적분 Taylor 항등식이다. 부호·방향과 관계없이 같은 양의 표현을 얻는다.

### 6.2. \(K=F_{\delta\delta}\)의 원인별 합

T29.9의 합성법칙과 \(V'(0)=0,V''(0)=-2/3\)로

\[
F_{\delta\delta}=G_{\delta\delta}-\frac23G_V,\qquad
F_{\delta W}=G_{\delta V},\qquad F_{WW}=G_{VV}.
\tag{T29.19}
\]

영폭에서는 \(G_V=C\)다. 다음 항들의 합이 정확한 \(K\)다.

| 항 | \(K\)에 대한 기여 |
|---|---|
| 균일 대역 평균 | \(K_{\rm average}=(p k''_e+q k''_x)/3\) |
| 끝점 위치의 곡률 | \(K_{\rm endpoint}=p k''_e\) |
| 내부 중심 속도의 제곱 | \(K_{\rm center\ curvature}=q W^2 k''_x/R^4\) |
| 내부 중심의 지지구간 가속도 | \(K_{\rm center\ acceleration}=2s qW k'_x/R^3\) |
| 끝점 확률의 지지구간 가속도 | \(K_{\rm probability}=(8R^2W/\mathcal D^3-2W/\mathcal D^2)\Delta k\) |
| 확률 변화와 위치 변화의 교차 | \(K_{\rm probability\ motion}=2(2RW/\mathcal D^2)s(k'_e-Wk'_x/R^2)\) |
| 실제 분산·중심 분산 보정 | \(K_V=-2C/3\) |

\[
\boxed{K=K_{\rm average}+K_{\rm endpoint}
+K_{\rm center\ curvature}+K_{\rm center\ acceleration}
+K_{\rm probability}+K_{\rm probability\ motion}+K_V.}
\tag{T29.20}
\]

끝점의 가속도 \(e_{\delta\delta}=0\)이므로 \(p k'_e e_{\delta\delta}\) 항은 0이다. 끝점 위치는 선형으로 움직여도 \(k''_e(e_\delta')^2\)는 남는다.

\(K_V\)는 다음 두 구체적인 변화와 정확히 같다.

\[
K_V
=-\frac{2R^2}{3\mathcal D^2}\Delta k
 -\frac{2s q}{3R}k'_x
=-\frac23C.
\tag{T29.21}
\]

첫 항은 \(V''\)에 따른 확률 변화, 둘째 항은 내부 중심의 변화다. 이 항을 단순히 내부 중심 하나의 가속도로 대체하면 확률 부분을 누락한다.

### 6.3. 혼합 편미분 \(M=F_{\delta W}\)

T29.16을 \(W\)로 미분하되 \(x_W=s/R\)와 확률의 도함수를 포함하면

\[
\boxed{\begin{aligned}
M={}&\frac{sR^2}{\mathcal D^2}k'_e
+\frac{s(R^2-2W)}{\mathcal D^2}k'_x
+\frac{W}{R\mathcal D}k''_x\\
&+\frac{2R(R^2-W)}{\mathcal D^3}\Delta k.
\end{aligned}}
\tag{T29.22}
\]

고정 중심 대역 평균의 일차 폭 도함수와 \(V_\delta(0)\)가 모두 0이므로, 이 혼합 편미분에 별도 \(k''/3\) 또는 \(V''\) 항을 넣지 않는다. 그 항들은 \(K\)에 있다.

### 6.4. 분산 곡률 \(N=F_{WW}\)

T29.17의 미분은

\[
\boxed{N=\frac{k''_x}{\mathcal D}
-\frac{2sR}{\mathcal D^2}k'_x
-\frac{2R^2}{\mathcal D^3}\Delta k.}
\tag{T29.23}
\]

를 준다. 이 결과 역시 원근 조건과 무관하다. 양의 \(C\)만으로 \(N\)이나 전체 \(d\)의 부호를 단정하지 않는다.

상속된 더 강한 조건 \(k'''<0\)를 쓰면 \(N\)의 부호는 별도로 정할 수 있다. T29.18에서 적분 변수를 바꾼 뒤 \(W\)로 미분하면

\[
C=\int_0^1t\,k''(e+t(x-e))\,dt,\qquad
N=\frac{s}{R}\int_0^1t^2k'''(e+t(x-e))\,dt.
\tag{T29.23a}
\]

따라서 \(N_+<0\), \(N_->0\)다. 이는 기존의 닫힌 세 번째 도함수 부호를 소비한 직접 적분 항등식이며 새 도함수 인증 캠페인이 아니다.

## 7. 실제 우이차 미분을 갖는 근의 존재와 전개

상속된 정확 내부근은

\[
F(0,w_j)=0,\qquad C_j=F_W(0,w_j)>0.
\tag{T29.24}
\]

T29.11의 근방을 줄여 \(F_W\)의 양의 하한이 존재하도록 한다. \(w_j\) 양옆의 고정 두 분산에서 \(F(0,W)\)의 부호가 다르고, \(F\)의 연속성은 작은 양의 폭에서 이 부호를 보존한다. 중간값 정리와 엄격 증가성으로 유일근 \(W_j(\delta)\in J\)가 존재한다. 끼우는 구간을 임의로 좁히면 \(W_j(\delta)\to w_j\)다.

PHYS28의 평균값 논증을 쓰면 \(W_j(\delta)-w_j=O(\delta)\)이며

\[
W_j'(0^+)=-B_j/C_j=:c_j.
\tag{T29.25}
\]

각 \(\delta>0\)의 물리 내부에서 \(F\)는 보통의 \(C^2\) 함수이고 \(F_W>0\)이므로 국소 근은 \(C^2\)다. 이때

\[
W_j'(\delta)
=-\frac{F_\delta(\delta,W_j(\delta))}
{F_W(\delta,W_j(\delta))}
\tag{T29.26}
\]

이며 우변은 \(\delta\downarrow0\)에서 \(c_j\)로 접한다. 한 번 더 미분한

\[
W_j''(\delta)
=-\frac{F_{\delta\delta}
+2F_{\delta W}W_j'(\delta)
+F_{WW}W_j'(\delta)^2}{F_W}
\tag{T29.27}
\]

도 연속적으로 유한한 우극한

\[
\lim_{\delta\downarrow0}W_j''(\delta)
=-\frac{K_j+2M_jc_j+N_jc_j^2}{C_j}
\tag{T29.28}
\]

을 갖는다. \(W_j'\)의 연속성과 미적분학의 기본정리, 또는 그 차분몫의 평균값 정리를 적용하면 이 극한은 실제 \(W_j''(0^+)\)다. 따라서 \(d_j=W_j''(0^+)/2\)라는 정의가 정당하다.

같은 결과를 물리 반직사각형 안의 선분
\((t\delta,w_j+t\eta)\), \(0\le t\le1\), 에 대한 적분 Taylor 식으로 직접 확인할 수 있다.

\[
F(\delta,w_j+\eta)
=B_j\delta+C_j\eta
+\frac12(K_j\delta^2+2M_j\delta\eta+N_j\eta^2)
+o(\delta^2+\eta^2).
\tag{T29.29}
\]

\(\eta=W_j(\delta)-w_j=c_j\delta+o(\delta)\)를 넣고 일차항을 소거하면 T29.1을 얻는다. 여기의 나머지는 연속 Hessian의 국소 작은 나머지이며 수치 상계가 아니다. 양의 폭의 물리 근방을 벗어나는 선분은 사용하지 않았다.

## 8. 문턱 이차계수의 직접 분해

각 \(K\) 항에 \(-1/(2C)\)를 곱하고, 암묵근의 추가 항 두 개를 분리한다.

\[
d_j=\sum_{\nu}
\left(-\frac{K_\nu}{2C_j}\right)
\underbrace{-\frac{M_jc_j}{C_j}}_{d_{\rm implicit\ mixed}}
\underbrace{-\frac{N_jc_j^2}{2C_j}}_{d_{\rm implicit\ curvature}},
\tag{T29.30}
\]

여기서 \(\nu\)는 T29.20의 평균·끝점·내부 중심 곡률·내부 중심 가속도·확률 가속도·확률×위치·\(V\)의 일곱 항이다. 모든 항은 해당 정확근 \(w_j\)에서 평가한다.

\[
d_V=-\frac{-2C_j/3}{2C_j}=\frac13,\qquad
d_{\rm average}
=-\frac{p k''_e+q k''_x}{6C_j}<0.
\tag{T29.31}
\]

첫 등식은 \(C_j\ne0\)인 이 물리 분산 좌표의 정확한 항등식이다. 둘째 부호는 \(p,q>0\), \(k''>0\), \(C_j>0\)로부터 나온다. 다른 항들과 전체 합의 부호는 이 두 사실로 정해지지 않는다.

추가로 T29.23a와 PHYS28의 \(c_*>0,c_0<0\)를 소비하면 \(c_j^2>0\)이므로

\[
d_{{\rm implicit\ curvature},*}>0,\qquad
d_{{\rm implicit\ curvature},0}<0.
\tag{T29.31a}
\]

이 역시 암묵근의 분산 곡률항 하나의 부호다. 다른 기여를 포함한 전체 \(d_j\)의 부호를 확정하지 않는다.

두 문턱 차이 \(\Gamma(\delta)=W_0(\delta)-W_*(\delta)\)에는

\[
\Gamma(\delta)=\Gamma(0)+(c_0-c_*)\delta
+(d_0-d_*)\delta^2+o(\delta^2)
\tag{T29.32}
\]

가 성립한다. \(d_V=1/3\)은 두 문턱에 같으므로 **문턱 간격의 이차계수에서는 정확히 상쇄**된다. 나머지 차이를 새 수치 평가 없이 특정 부호로 단정하지 않는다.

## 9. 네 노드의 \(k,k',k''\)만으로 충분한 이유

T29.16–23은 각 경계의 끝점과 내부 중심에서 \(k,k',k''\)만 사용한다. 따라서 두 저장 근에서 평가할 때 필요한 에너지는 상속된

\[
a,\quad v_*=m+w_*/L,\quad u_0=m-w_0/H,\quad b
\tag{T29.33}
\]

의 네 노드다. 이 문서에서 그 소수값을 새로 평가하지 않는다. \(k'''\)는 상속 모멘트 정리와 일차 부호 전제에 쓰이며 새 이차계수의 노드 평가에 요구되지 않는다.

원 물리 커널을

\[
\phi(E)=\sigma(E)[J_x+J_w(E-\chi)],\quad
\mathscr D_E=E\partial_E,\quad
\mathcal P=\frac{qN_0c_{\rm light}n_H(1-x_{HII})}{180}
\]
\[
k(E)=\mathcal P(\mathscr D_E^2+3\mathscr D_E)\phi(E)
\tag{T29.34}
\]

로 쓰면

\[
k'(E)=\frac{\mathcal P}{E}
(\mathscr D_E^3+3\mathscr D_E^2)\phi(E),
\]
\[
\boxed{k''(E)=\frac{\mathcal P}{E^2}
(\mathscr D_E^4+2\mathscr D_E^3-3\mathscr D_E^2)\phi(E).}
\tag{T29.35}
\]

둘째 식은 \(\partial_E=E^{-1}\mathscr D_E\)와
\(\partial_E(E^{-1}h)=E^{-2}(\mathscr D_E-1)h\)를 합성한 직접 유도다. 즉 log-energy Taylor 경로는 \(\phi\)의 네 번째 log 미분까지 필요하다. PHYS28의 \(k,k'\) 구현에 이름만 추가하여 \(k''\) 검증을 대신할 수 없다. 이 기여는 실제 kernel 함수나 과거 모듈을 호출하지 않았다.

## 10. 정확근과 저장 근의 잔차를 구별하는 항등식

T29.16–23은 일반 \(W\) 식이므로, 저장된 유한 소수 \(\widehat w\)에서도 그대로 평가할 수 있다. 그러나

\[
A:=F(0,\widehat w)
\tag{T29.36}
\]

는 일반적으로 정확히 0이 아니다. \(C\ne0\)에서

\[
\widehat c=-B/C,\qquad
\widehat d=-(K+2M\widehat c+N\widehat c^2)/(2C)
\tag{T29.37}
\]

를 쓰면 이것은 그 점을 지나는 **동일 잔차 수준 \(F=A\)** 의 한쪽 미분 계수다. 따라서

이 절의 등호는 저장 소수를 정확한 기준점으로 해석하고 편미분을 실수 수준에서 정의한 항등식이다. 실제 Decimal 평가의 유한 반올림은 별도 수치 오차이며, 원 \(J\)의 불확실성도 남는다.

\[
F\!\left(\delta,\widehat w+\widehat c\delta+
\widehat d\delta^2\right)=A+o(\delta^2).
\tag{T29.38}
\]

기존 수치 근이 정확근에 가깝다는 증거를 소비하여 정확근 계수의 근사치로 해석할 수는 있지만, 일반 식을 썼다는 사실이 \(A=0\) 또는 근 오차의 수치 상계를 증명하지 않는다.

정확근에서만 단순화되는 비정규화 분자 식과 비교하려면 잔차를 명시해야 한다. 다음 정확한 분자·분모를 정의한다.

\[
\mathcal Q(\delta,W)=(R-\delta)^2+W-\frac{\delta^2}{3},
\]
\[
\mathcal N(\delta,W)=
\left(W-\frac{\delta^2}{3}\right)f_\delta(e_\delta)
+(R-\delta)^2f_\delta(x_{\delta,V}),\qquad
F=\mathcal N/\mathcal Q.
\tag{T29.39}
\]

영폭에서 \(\mathcal Q=\mathcal D\), \(\mathcal Q_\delta=-2R\),
\(\mathcal Q_W=1\), \(\mathcal Q_{\delta\delta}=4/3\),
\(\mathcal Q_{\delta W}=\mathcal Q_{WW}=0\)이므로 곱의 미분법이

\[
\begin{aligned}
\mathcal N_\delta&=\mathcal D B-2RA,&
\mathcal N_W&=\mathcal D C+A,\\
\mathcal N_{\delta\delta}
&=\mathcal D K-4RB+\tfrac43A,&
\mathcal N_{\delta W}&=\mathcal D M-2RC+B,\\
\mathcal N_{WW}&=\mathcal D N+2C
\end{aligned}
\tag{T29.40}
\]

를 준다. 따라서 일반 \(\widehat c=-B/C\)에 대해 정확한 잔차 보정식은

\[
\boxed{\widehat c
=-\frac{\mathcal N_\delta+2RA}{\mathcal N_W-A},}
\]
\[
\boxed{\widehat d
=-\frac{\mathcal N_{\delta\delta}
+2\mathcal N_{\delta W}\widehat c
+\mathcal N_{WW}\widehat c^2-\tfrac43A}
{2(\mathcal N_W-A)}.}
\tag{T29.41}
\]

이다. 둘째 식의 유도에서는 \(B+C\widehat c=0\)를 사용한다. \(\mathcal N_W-A=\mathcal D C>0\)이다. **정확근 \(A=0\)에서만** 잔차 항을 버리고 \(c=-\mathcal N_\delta/\mathcal N_W\), 통상적인 분자 Hessian의 \(d\) 식으로 단순화한다. 저장된 근에서 잔차를 0으로 덮어써 이 단순화가 문자 그대로 정확하다고 주장하지 않는다.

이 항등식은 대수적으로 서로 다른 평가 경로를 비교할 때 쓸 수 있다. 양 경로가 같은 물리 입력·커널 적합식을 사용한다는 의존성은 남으며 독립적인 물리 자료나 입력 불확실성 enclosure가 생기지 않는다.

## 11. 이차 커널의 정확한 퇴화 점검

물리 커널 대신 이차 시험함수

\[
k_{\rm toy}(E)=a_0+a_1E+a_2E^2
\]

를 대수적으로 대입하면 모든 같은 질량·평균·실제 분산 분포에서

\[
F_{\rm toy}(\delta,W)=a_0+a_1m+a_2(m^2+W).
\tag{T29.42}
\]

그러므로 \(C=a_2\), \(B=K=M=N=0\)이다. \(a_2\ne0\)이고 내부근이 존재한다면 \(c=d=0\)이다. 세 번째 도함수의 엄격 음수 조건은 이 시험함수에서 제거되므로 원 모멘트 경계의 엄격 유일성을 그대로 주장하지 않는다.

항별로는 \(k''_{\rm toy}=2a_2\)라서

\[
K_{\rm average}=\frac{2a_2}{3},\qquad
K_V=-\frac{2a_2}{3},\qquad
K_{\rm support}=0.
\tag{T29.43}
\]

평균화의 \(d_{\rm average}=-1/3\)와 중심 분산 보정 \(d_V=+1/3\)가 정확히 상쇄된다. 고정 \(V\)의 중심 분포는 지지가 바뀌어도 질량·평균·분산을 보존하므로 기하 항들의 총합은 0이다. 이 점검은 \(V=W\)로 잘못 대체하거나 전체 이차 미분의 \(1/2\)를 누락할 때 드러나는 오류를 직접 판별한다. 여기서는 수치 toy 프로그램이나 물리 커널 평가 없이 이 항등식을 유도했다.

## 12. 단위와 한 폭 비교의 올바른 해석

| 양 | 단위 |
|---|---|
| \(\delta,e,x,R,c_j\) | eV |
| \(W,V,\mathcal D,w_j\) | eV² |
| \(k,F\) | s⁻⁴ |
| \(B=F_\delta\) | s⁻⁴ eV⁻¹ |
| \(C=F_W\) | s⁻⁴ eV⁻² |
| \(K=F_{\delta\delta}\) | s⁻⁴ eV⁻² |
| \(M=F_{\delta W}\) | s⁻⁴ eV⁻³ |
| \(N=F_{WW}\) | s⁻⁴ eV⁻⁴ |
| \(d_j\), 각 \(d\) 기여 | 무차원 |

따라서 \(K,2Mc,Nc^2\)는 같은 단위이고 \(2C\)로 나누면 무차원이다. 커널 전체의 공통 비영 상수 배율은 분자·분모에서 소거되어 \(c,d\)를 바꾸지 않는다. 이는 고정 정규화의 대수 점검이며 물리 모델이나 \(J\)의 상대 성분을 바꿀 권한이 아니다.

수치 기여자는 이미 저장된 PHYS26·27 원근과 PHYS28 일차 결과를 읽어, 기존 \(\delta_{\rm obs}=.05\ {\rm eV}\)에서

\[
\widehat W_{j,\rm quad}
=\widehat w_j+\widehat c_j\delta_{\rm obs}
+\widehat d_j\delta_{\rm obs}^2,
\]
\[
r_{j,\rm quad}
=\widehat W_{j,\rm PHYS27}-\widehat W_{j,\rm quad}
=r_{j,\rm lin}-\widehat d_j\delta_{\rm obs}^2
\tag{T29.44}
\]

를 비교할 수 있다. 마지막 등식은 **같은 일차계수**로 정의한 선형 잔차를 사용할 때 성립한다. 새 산술의 \(\widehat c\)와 PHYS28 직렬화된 \(\widehat c_{\rm old}\)를 구별한다면

\[
r_{\rm quad}
=r_{\rm lin,old}
-(\widehat c-\widehat c_{\rm old})\delta_{\rm obs}
-\widehat d\,\delta_{\rm obs}^2
\tag{T29.45}
\]

로 그 차이도 보존한다.

이 비교는 한 저장 폭에서의 이차 예측 진단이다. 잔차의 개선 여부·크기는 실제 원 수치 결과가 정한다. 한 폭만으로 \(O(\delta^3)\) 수렴률, 정량 Taylor 나머지, \(.05\)까지의 유효폭, 정확근 enclosure, 전역 폭 단조성을 인증하지 않는다. 이번에 증명하는 근 전개는 \(o(\delta^2)\)이며 수치적으로 계산된 나머지 상계는 없다.

## 13. 주장별 점검과 이번 기여의 종료

| 점검 | 상태 | 근거 |
|---|---|---|
| 실제 \(W\)와 중심 \(V\) 구별 | PASS — derived | T29.9, T29.19, T29.21 |
| 물리 한쪽 \(C^2\)와 실제 우이차 근 미분 | PASS — conditional derived | T29.11–13, T29.24–29; 내부 단순근 전제 |
| 평균·끝점·중심·확률·교차항 누락 방지 | PASS — derived | 기초 도함수 표와 T29.20의 일곱 항 |
| 이차 미분의 절반과 단위 | PASS — derived | T29.1, T29.30, 단위 표 |
| 정확한 \(d_V=1/3\), 평균화 항 음수 | PASS — conditional derived | T29.31; \(C>0,k''>0\) |
| 분산 곡률항의 상단 양수·하단 음수 | PASS — conditional derived | T29.23a, T29.31a; 상속 \(k'''<0,c_j\ne0\) |
| 두 문턱 간격에서 \(d_V\) 상쇄 | PASS — derived | T29.32 |
| 저장 근 잔차와 비정규화 분자 식 | PASS — derived | T29.36–41; 잔차를 0으로 두지 않음 |
| 이차 커널 퇴화 | PASS — direct algebra | T29.42–43 |
| 새 물리 수치 계수·한 폭 잔차 | 이 기여에서는 NOT_RUN | 별도 numerical owner의 실제 첫 실행과 재현 필요 |
| 최종 독립 승격 | 이 기여자의 역할 아님 | NONBLIND 후보 생성자, validation 설계 협의에 참여 |

이 문서의 자체 대수 점검은 **THEORY_CONTRIBUTOR_SELF_CHECK**다. 생성·검증 설계를 수행하지 않은 별도 reviewer의 최종 판정을 대신하지 않는다. 수식 조정은 같은 대화의 owner 및 수치 기여자와 공유했으며 blind 독립성이나 독립 물리 증거를 주장하지 않는다.

외부 문헌을 이 기여에서 새로 열람하지 않았다. owner가 별도로 확보한 문헌은 해당 owner의 실제 읽기와 관계 표시에 따르며, 이 한쪽 물리 정칙성·분해·잔차 보정은 직접 유도다. 선행 문헌 목록을 새 원문 열람으로 처리하지 않는다.

이 결과는 동결 초기 계수와 정해진 균일 대역 분포족에 한정된다. 유한 시간의 HeIII 총편차, 실제 emitter 또는 cosmological history admission, 모든 연속 스펙트럼 대표성, 원 \(J\)·원자·기체 불확실성, native 동등성 또는 새 세계 최초성을 주장하지 않는다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED, production source/default/runtime changes0**을 유지한다.

식·전제·증거 상태의 기계 판독 목록은 [THEORY_CLAIMS.json](THEORY_CLAIMS.json), 실제 읽기·identity·실행 횟수·도구 표시 사건은 [PROVENANCE.json](PROVENANCE.json)에 있다.
