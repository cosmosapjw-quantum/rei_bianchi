# PHYS28 — 작은 균일 대역폭에서 두 분산 문턱의 일차 민감도

연구: **REI-PHYS28-20261011 · SMALL_WIDTH_THRESHOLD_SENSITIVITY**  
기여자: **/root/phys28_theory**, 현재 대화 안의 클라우드 이론 기여자  
모델 근거: 이 실행자의 trusted host developer designation **GPT-6 Astra Pro**; 연구 하네스 **gpt6-astra v4.0.0**  
근거 상태: **derived, 동결 입력과 상속된 정확근 존재 전제에 조건부**  
판정 지위: 이론 후보 생성 완료. **최종 독립 승격 판정이 아니다.**

## 0. 이번에 얻은 결과

물리 광자 분산 \(W\)를 고정하여 균일 대역 반폭 \(\delta\)를 0에서 오른쪽으로 늘릴 때, PHYS26의 두 정확근을 출발점으로

\[
\boxed{W_{*,\delta}=V_{*,0}+c_*\delta+o(\delta),\qquad c_*>0,}
\]
\[
\boxed{W_{0,\delta}=W_{0,0}+c_0\delta+o(\delta),\qquad c_0<0.}
\tag{T28.1}
\]

를 얻는다. \(\delta\)는 반폭이며 단위는 eV, \(W\)의 단위는 eV², 두 계수 \(c_*,c_0\)의 단위는 eV다. 두 계수가 0일 가능성을 사전 배제하지 않았다. 아래의 가중 적분식과 \(k'''<0\)가 그 비영성과 부호를 결정한다.

이 일차항에는 **중심 지지구간 끝점, 이동하는 내부 중심, 광자 확률의 변화**가 모두 들어간다. 고정 중심에서의 대칭 균일 평균화와 실제 분산·중심 분산의 차이는 \(\delta\)의 일차 미분에 기여하지 않는다. 이는 평균화 효과 자체가 없다는 뜻이 아니라, 이번의 일차 문턱 이동을 만드는 항과 평균화의 시작 차수를 구분한 결과다.

이 문서는 새 커널 평가, 새 근 탐색, 새 수치 main, 과거 main/suite, 도함수 부호 캠페인, native 또는 gas IVP를 실행하지 않았다. 저장된 근에서 계수의 소수값을 평가하는 일은 별도 수치 기여자의 범위다. 최종 판정은 생성자·검증 설계자와 분리된 reviewer가 한다.

## 1. 정의, 상속 입력, 물리적 의미

현재 계약은 [PHYSICS_CONTRACT.json](../../PHYSICS_CONTRACT.json), SHA256 **d9c50cb43d60bf466eb92e91e8e62791fcf84680025c34fc0c42c899ed16fde2**다. 실제로 읽은 선행 입력은 다음과 같다.

| 증거 | 이번에 소비하는 내용 | 근거 상태 |
|---|---|---|
| [PHYS27 후속 계약](../../inputs/PHYS27/next/PHYS28_NEXT_HANDOFF_KO.md) §1–6 | 고정 실제 W의 우미분, 작은 폭 전개, 기존 한 폭과의 비교, 실행·보호 경계 | 기존 작업 계약 |
| [PHYS27 유도](../../inputs/PHYS27/contributions/theory/FINITE_WIDTH_DERIVATION_KO.md) 전체, 특히 T27.10·T27.22–23·T27.35·T27.46–48 | 두 분산 관계, 명시적 경계식, 양의 W 기울기, 평균화의 이차 시작 및 영폭 극한 | inherited derived, 해당 동결 입력에 조건부 |
| [PHYS26 유도](../../inputs/PHYS26/contributions/theory/ENVELOPE_DERIVATION_KO.md) 실제 읽은 29–89, 356–453행 | 동일 커널·단위·곡률 조건, 원 경계의 양의 기울기와 두 정확근 정의 | inherited derived; 존재 부호 전제는 inherited numerical support |
| [PHYS27 독립 판정](../../inputs/PHYS27/independent/DECISION_REVIEW.json) 선택 필드 및 [종료 상태](../../inputs/PHYS27/state/CLOSEOUT.json) | PROMOTE_SCOPED와 Physical HOLD, 기존 결론의 승격 범위·미승격 항목 | 실제 읽은 판정·상태 |

정확한 십진 에너지와 길이는

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad H=b-m=6.58\qquad({\rm eV}).
\tag{T28.2}
\]

0 근방의 \(0\le\delta<\min(L,H)\)에서

\[
\alpha=a+\delta,\quad\beta=b-\delta,\quad
\ell=L-\delta,\quad h=H-\delta,\quad
V=W-\frac{\delta^2}{3}.
\tag{T28.3}
\]

중심 법칙은 \([\alpha,\beta]\) 위의 광자 수 확률측도이고, 각 중심을 반폭 \(\delta\)의 균일 광자 대역으로 바꾼다. PHYS27의 정의에 의해 물리 분산은 정확히 \(W=V+\delta^2/3\)이며, 실제 허용 구간은

\[
\mathcal D_\delta=
\left[\frac{\delta^2}{3},\ (L-\delta)(H-\delta)+\frac{\delta^2}{3}\right].
\tag{T28.4}
\]

이 기여는 전체 모멘트 정리를 다시 증명하거나 닫힌 곡률 인증을 재실행하지 않는다. 소비하는 함수 조건은

\[
k\in C^3([a,b]),\qquad k''>0,\qquad k'''<0.
\tag{T28.5}
\]

기존 source binary64 상수의 exact-real 해석과 PHYS22 직렬화 수치 J를 고정한다. J 원자료 SHA256은 **6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79**이며, 이 identity와 조건은 현재 계약에서 소비한다. 이 이론 기여자가 J 파일 전체나 원 Rust 소스를 새로 감사했다는 뜻은 아니다.

\(k\)와 \(A\)는 초기 HeIII의 \(\epsilon^2t^4\) 응답계수로 단위가 s⁻⁴다. Metric \((-+++ )\), gas-comoving proper seconds, \(w\) in eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\), 시간계수의 추가 factorial 없음, 고정 초기 기체·광자 수·평균 및 기존 \(qN_0/45\) 정규화를 유지한다. 이후의 \(k'\)는 에너지에 대한 미분이다. 초기 gas 또는 J를 폭과 함께 변화시키지 않는다.

## 2. 폭 미분에 필요한 모든 항

평균화 커널을 고정 적분구간으로 쓰면

\[
f_\delta(c)=\frac12\int_{-1}^{1}k(c+\delta z)\,dz,\qquad f_0(c)=k(c).
\tag{T28.6}
\]

물리적으로 허용되는 내부 중심 근방에서 미분을 적분 안으로 옮길 수 있다. \(k'\)가 연속이고 적분구간이 콤팩트이므로

\[
\left.\partial_\delta f_\delta(c)\right|_{0^+}
=\frac12\int_{-1}^{1}z k'(c)\,dz=0,
\qquad \partial_c f_0(c)=k'(c).
\tag{T28.7}
\]

PHYS27 T27.46의 \(|f_\delta(c)-k(c)|\le M_2\delta^2/6\)도 이 일차항 소멸을 지지한다. \(M_2=\max|k''|\)의 새 수치 상계를 구하지 않는다. 원 구간 끝점에서는 고정 c에 대해 양의 폭을 두지 않고 **허용 경로 자체**를 미분한다.

\[
f_\delta(a+\delta)=\frac12\int_{-1}^{1}k(a+\delta(1+z))\,dz,
\]
\[
f_\delta(b-\delta)=\frac12\int_{-1}^{1}k(b+\delta(z-1))\,dz.
\tag{T28.8}
\]

따라서 이 두 전체 우미분은 각각 \(k'(a)\), \(-k'(b)\)다. 계산 중 \([a,b]\) 밖의 물리 커널이나 음의 반폭을 요구하지 않는다.

이제 고정 실제 \(0<W<LH\)에서 다음 영폭 기호를 쓴다.

\[
v=m+\frac WL,\quad u=m-\frac WH,\quad
D_L=L^2+W=L(v-a),\quad D_H=H^2+W=H(b-u),
\]
\[
p=\frac W{D_L},\qquad r=\frac W{D_H}.
\tag{T28.9}
\]

유한 폭 상단의 끝점 확률은 \(p_\delta=V/(\ell^2+V)\), 내부 확률은 \(1-p_\delta\)다. 하단의 오른쪽 끝점 확률은 \(r_\delta=V/(h^2+V)\), 내부 확률은 \(1-r_\delta\)다. 상단 내부 중심은 \(v_\delta=m+V/\ell\), 하단 내부 중심은 \(u_\delta=m-V/h\)다. 모든 우미분은 실제 W를 고정한 값이다.

| 양 | \(\delta=0\)에서의 값 | \(\partial_\delta|_{0^+,W}\) |
|---|---|---|
| \(V\) | \(W\) | \(0\) |
| \(\alpha,\beta\) | \(a,b\) | \(+1,-1\) |
| \(\ell,h\) | \(L,H\) | \(-1,-1\) |
| \(v_\delta,u_\delta\) | \(v,u\) | \(W/L^2,-W/H^2\) |
| \(p_\delta,r_\delta\) | \(p,r\) | \(2LW/D_L^2,2HW/D_H^2\) |
| 내부 확률 | \(1-p,1-r\) | \(-2LW/D_L^2,-2HW/D_H^2\) |
| 고정 내부 중심의 \(f_\delta\) | \(k\) | \(0\) |

\(V'|_0=0\)이므로 일차 결과가 같은 수치로 보이더라도 W와 V의 정의를 교환하지 않는다. \(V=W-\delta^2/3\)는 이차부터 차이를 만든다. 고정 W에서 중심 지지가 줄어들면 상단 내부 중심은 더 높은 에너지로, 하단 내부 중심은 더 낮은 에너지로 움직이고 두 끝점의 광자 확률은 증가한다.

## 3. 상단의 고정 W 폭 미분

PHYS27의 정확 경계는

\[
A_{\delta,+}(W)=p_\delta f_\delta(\alpha)
 +(1-p_\delta)f_\delta(v_\delta).
\tag{T28.10}
\]

표의 도함수를 모두 적용하면

\[
\begin{aligned}
B_+(W)&:=\left.\partial_\delta A_{\delta,+}(W)\right|_{0^+}\\
&=\underbrace{\frac W{D_L}k'(a)}_{\text{끝점 이동}}
 +\underbrace{\frac W{D_L}k'(v)}_{\text{내부 중심 이동}}\\
&\quad+\underbrace{\frac{2LW}{D_L^2}\,[k(a)-k(v)]}_{\text{확률 변화}}
 +\underbrace{0}_{\text{고정 중심 대역 평균}}
 +\underbrace{0}_{V'(0)\text{ 기여}}.
\end{aligned}
\tag{T28.11}
\]

각 표기 항은 전체 미분의 분해이며 항별 부호를 따로 가정하지 않는다. \(D_L=L(v-a)\)를 이용하면

\[
\boxed{B_+(W)=\frac W{L^2+W}
\left[k'(a)+k'(v)-2\frac{k(v)-k(a)}{v-a}\right].}
\tag{T28.12}
\]

이 식은 정확근에서만 성립하는 식이 아니라 모든 고정 \(0<W<LH\)에서 성립한다. 각 그런 W는 충분히 작은 양의 폭에서 실제로 허용된다.

## 4. 하단의 고정 W 폭 미분

하단 경계는

\[
A_{\delta,-}(W)=(1-r_\delta)f_\delta(u_\delta)
 +r_\delta f_\delta(\beta).
\tag{T28.13}
\]

같은 방식으로

\[
\begin{aligned}
B_-(W)&:=\left.\partial_\delta A_{\delta,-}(W)\right|_{0^+}\\
&=\underbrace{-\frac W{D_H}k'(b)}_{\text{끝점 이동}}
 +\underbrace{-\frac W{D_H}k'(u)}_{\text{내부 중심 이동}}\\
&\quad+\underbrace{\frac{2HW}{D_H^2}\,[k(b)-k(u)]}_{\text{확률 변화}}
 +\underbrace{0}_{\text{고정 중심 대역 평균}}
 +\underbrace{0}_{V'(0)\text{ 기여}},
\end{aligned}
\tag{T28.14}
\]

따라서

\[
\boxed{B_-(W)=-\frac W{H^2+W}
\left[k'(u)+k'(b)-2\frac{k(b)-k(u)}{b-u}\right].}
\tag{T28.15}
\]

하단 내부 중심의 미분 \(-W/H^2\)와 오른쪽 끝점의 미분 \(-1\)을 모두 포함했으므로 상단과 달리 전체 부호 앞에 마이너스가 남는다.

## 5. 비영성과 부호를 결정하는 정확한 적분식

\(a\le x<y\le b\)에 대해

\[
T(x,y):=k'(x)+k'(y)-2\frac{k(y)-k(x)}{y-x}
\tag{T28.16}
\]

라 두자. \(q(E)=(E-x)(y-E)\)이면 \(q(x)=q(y)=0\), \(q'(x)=y-x\), \(q'(y)=-(y-x)\), \(q''=-2\)다. 두 번 부분적분하면

\[
\begin{aligned}
\int_x^y q(E)k'''(E)dE
&=(y-x)[k'(x)+k'(y)]-2[k(y)-k(x)],
\end{aligned}
\]

즉

\[
\boxed{T(x,y)=\frac1{y-x}
\int_x^y(E-x)(y-E)k'''(E)dE<0.}
\tag{T28.17}
\]

내부 가중치는 양수이고 상속된 세 번째 도함수는 모든 점에서 음수여서 적분의 부호는 엄격하다. 같은 결론을 \(k'\)의 엄격 오목성과 사다리꼴 평균·적분 평균의 차이로 읽을 수도 있다. 여기서는 그 차이의 정확한 적분식을 직접 제시했다.

\(W>0\)와 양의 분모를 결합하면

\[
\boxed{B_+(W)<0,\qquad B_-(W)>0\quad(0<W<LH).}
\tag{T28.18}
\]

따라서 기존의 같은-W 엄격 포함이 주는 유한 폭 방향에 더하여, **영폭에서 일차 이동이 실제로 비영**임을 얻었다. 엄격 포함만으로는 일반적으로 일차계수가 0일 가능성을 배제할 수 없으므로 T28.17이 추가로 필요하다.

## 6. 분산 기울기와 정확근 민감도

PHYS26에서 소비한 양의 W 기울기는

\[
C_+(W):=\partial_W A_{0,+}(W)
=\frac{k(a)-k(v)+(v-a)k'(v)}{(v-a)^2}>0,
\]
\[
C_-(W):=\partial_W A_{0,-}(W)
=\frac{k(b)-k(u)-(b-u)k'(u)}{(b-u)^2}>0.
\tag{T28.19}
\]

양수성의 입력은 \(k''>0\)다. T28.18의 방향을 만드는 \(k'''<0\)와 역할을 구분한다. 두 기울기의 단위는 s⁻⁴ eV⁻²다.

원 정확근과 그 이동 노드는

\[
A_{0,+}(V_{*,0})=0,\quad v_*=m+V_{*,0}/L,
\]
\[
A_{0,-}(W_{0,0})=0,\quad u_0=m-W_{0,0}/H,
\qquad 0<V_{*,0}<W_{0,0}<LH.
\tag{T28.20}
\]

끝값 부호에 대한 기존 수치 지원을 소비하는 조건부 존재 명제이며, 곡률 부호만으로 이 두 영점의 존재를 새로 주장하지 않는다. T28.19가 양수이므로 두 근은 단순하다. §7의 한쪽 암묵함수 논증으로

\[
\boxed{c_*=-\frac{B_+(V_{*,0})}{C_+(V_{*,0})}>0,\qquad
c_0=-\frac{B_-(W_{0,0})}{C_-(W_{0,0})}<0.}
\tag{T28.21}
\]

정확근 항등식 \(V_{*,0}k(a)+L^2k(v_*)=0\), \(H^2k(u_0)+W_{0,0}k(b)=0\)을 사용하면 동등한 식은

\[
\boxed{c_*=-V_{*,0}
\frac{k'(a)+k'(v_*)+2k(a)/L}{k(a)+Lk'(v_*)},}
\]
\[
\boxed{c_0=W_{0,0}
\frac{k'(u_0)+k'(b)-2k(b)/H}{k(b)-Hk'(u_0)}.}
\tag{T28.22}
\]

분모의 양수성도 정확근에서 T28.19로 확인된다.

\[
k(a)+Lk'(v_*)=(L^2+V_{*,0})C_+(V_{*,0})>0,
\]
\[
k(b)-Hk'(u_0)=(H^2+W_{0,0})C_-(W_{0,0})>0.
\tag{T28.23}
\]

T28.22의 단위는 eV² × (s⁻⁴/eV)/(s⁻⁴) = eV이며 T28.21과 일치한다. 전체 커널에 공통 양의 상수를 곱하면 B와 C가 함께 배율을 받아 c는 불변이다. 이는 현재 고정된 정규화의 대수 점검이며 J의 상대 성분이나 물리 모델을 바꿀 권한은 아니다.

## 7. 음의 폭을 쓰지 않는 한쪽 암묵함수 논증

원 정확근 하나를 \(w_j\in(0,LH)\), 해당 경계를 \(F_j(\delta,W)=A_{\delta,\pm}(W)\)라고 쓰자. \(w_j\) 양옆의 작은 닫힌 W구간 \(J_j\subset(0,LH)\)를 고른다. T28.4의 양 끝은 \(\delta=0\)에서 각각 0, LH에 연속적으로 접하므로, **충분히 작은** \(\delta_0>0\)에 대해

\[
J_j\subset \operatorname{int}\mathcal D_\delta
\quad(0\le\delta\le\delta_0)
\tag{T28.24}
\]

가 성립한다. 여기서는 그러한 폭 근방의 존재만 사용하며 그 수치 하한이나 \(0.05\) 포함 여부를 인증하지 않는다.

T28.6·T28.8과 양의 분모의 명시적 식으로 \(F_j\)는 이 반직사각형에서 W에 대해 C¹이며, 폭에 대해 0에서 오른쪽 C¹이다. \(\partial_WF_j\)도 \((0,w_j)\)까지 연속이고 그 값은 \(C_j(w_j)>0\)다. 평균화 커널은 물리 구간 안에서만 평가되고 상속된 연속 도함수가 유계이므로 적분·미분의 교환이 정당하다.

\(F_j(0,W)\)가 \(w_j\)의 왼쪽에서 음수, 오른쪽에서 양수인 것을 사용한다. 경계 함수의 연속성은 선택한 두 W점의 부호를 작은 양의 폭에서 보존한다. 그 사이의 중간값 정리와 양의 W 기울기로 새 근 \(w_j(\delta)\)가 유일하게 존재한다. 원 근을 둘러싼 구간을 임의로 좁힐 수 있으므로 \(w_j(\delta)\to w_j\)다. PHYS27의 기존 근 수렴도 같은 결론을 지지하며, 이를 새 수치 root 탐색으로 취급하지 않는다.

W에 대한 평균값 정리로 두 근 사이의 \(\xi_\delta\)가 존재하여

\[
0=F_j(\delta,w_j(\delta))
=F_j(\delta,w_j)
 +\partial_WF_j(\delta,\xi_\delta)[w_j(\delta)-w_j].
\tag{T28.25}
\]

\(F_j(0,w_j)=0\)와 우미분의 정의에서 \(F_j(\delta,w_j)/\delta\to B_j(w_j)\)이고, 연속성에서 \(\partial_WF_j(\delta,\xi_\delta)\to C_j(w_j)>0\)다. 따라서

\[
\lim_{\delta\downarrow0}\frac{w_j(\delta)-w_j}{\delta}
=-\frac{B_j(w_j)}{C_j(w_j)}.
\tag{T28.26}
\]

이것이 현재 문제에 필요한 한쪽 암묵함수 미분과 T28.1의 \(o(\delta)\)다. 음의 폭의 물리 족이나 원 지지구간 밖 커널을 가정할 필요가 없다. 필요한 조건은 실제 내부 단순근, 허용 근방, F의 연속 우미분과 W 기울기의 연속성·비영성이다.

두 근의 차이에 대해서는 직접

\[
W_{0,\delta}-W_{*,\delta}
=(W_{0,0}-V_{*,0})+(c_0-c_*)\delta+o(\delta),
\qquad c_0-c_*<0.
\tag{T28.27}
\]

를 얻는다. 따라서 양·음 응답 공존 분산 구간의 폭은 영폭에서 일차적으로 감소한다. 이는 서로 다른 임의의 양의 폭의 분포족이 포함된다는 주장이나 전역 폭 단조성 정리가 아니다.

## 8. 정확근 식과 저장된 수치 중점의 구별

T28.12, T28.15, T28.19는 원 정확근 조건을 쓰지 않은 일반 W 식이다. 따라서 저장된 PHYS26 수치 근에서 계수를 근사할 때도 일반 \(-B/C\)가 직접적인 평가식이다. 반면 T28.22–23은 **정확근에서만** 대수적으로 단순해진다. 유한 소수 중점을 정확 영점으로 대입했다고 서술하지 않는다.

이 구별은 나머지 항을 명시하여 점검할 수 있다. 임의의 내부 W에서 \(A_\pm=A_{0,\pm}(W)\)로 쓰고, 정확근에서 단순해지는 식을 형식적으로

\[
\widetilde C_+=\frac{k(a)+Lk'(v)}{D_L},\quad
\widetilde B_+=\frac W{D_L}[k'(a)+k'(v)+2k(a)/L],
\]
\[
\widetilde C_-=\frac{k(b)-Hk'(u)}{D_H},\quad
\widetilde B_-=-\frac W{D_H}[k'(u)+k'(b)-2k(b)/H]
\tag{T28.28}
\]

로 정의하면 정확한 원근-잔차 항등식은

\[
C_+-\widetilde C_+=-\frac{A_+}{D_L},\qquad
B_+-\widetilde B_+=-\frac{2W A_+}{L D_L},
\]
\[
C_--\widetilde C_-=-\frac{A_-}{D_H},\qquad
B_--\widetilde B_-=-\frac{2W A_-}{H D_H}.
\tag{T28.29}
\]

분자에 \(A_+D_L=Wk(a)+L^2k(v)\), \(A_-D_H=H^2k(u)+Wk(b)\)를 넣어 직접 정리하면 얻어진다. 저장 중점에서 두 대수 표현이 근소하게 달라질 때 이 원근 잔차와 유한 산술을 구분할 수 있다. T28.29는 새 root 탐색이나 더 정밀한 원근 인증을 요구하지 않는다.

## 9. PHYS27의 한 폭 비교가 뜻하는 것

별도 수치 기여자는 기존 PHYS27 원 JSON에서 \(\delta_{\rm obs}=0.05\ {\rm eV}\)의 두 문턱을 읽고, 새로 평가한 \(\widehat c_*,\widehat c_0\)로

\[
\widehat W_{*,\rm lin}
=\widehat V_{*,0}+\widehat c_*\delta_{\rm obs},\qquad
\widehat W_{0,\rm lin}
=\widehat W_{0,0}+\widehat c_0\delta_{\rm obs}
\tag{T28.30}
\]

을 만들 수 있다. 관측 비교 잔차는

\[
\widehat r_* =\widehat W_{*,\delta_{\rm obs}}-\widehat W_{*,\rm lin},\qquad
\widehat r_0 =\widehat W_{0,\delta_{\rm obs}}-\widehat W_{0,\rm lin}.
\tag{T28.31}
\]

이다. 모자는 저장된 수치 값 또는 유한 산술 평가를 뜻한다. 이 이론 기여는 PHYS27 raw를 새로 수치 평가하지 않았고, 새 계수·예측·잔차 소수값을 생성하지 않았다. 한 폭의 잔차는 **그 폭에서의 선형 예측 진단**이다. 수렴률, \(\delta=0.05\)까지의 오차상계, root enclosure, 최적 유효폭, 모든 양의 폭 사이의 단조성을 인증하지 않는다.

이번 전체 문턱 전개의 나머지는 \(o(\delta)\)로 제한한다. 더 강한 정량 나머지가 필요하면 선택한 실제 폭·W 근방에서 고차 편미분과 단순근 분모의 양의 하한을 함께 제어해야 한다. 현재 \(k\in C^3\) 조건이 추가 미분을 가능하게 한다는 사실을, 실제로 그런 상계와 유효 구간을 산출했다는 주장으로 바꾸지 않는다. 평균화 커널 하나의 T27.46 상계를 전체 이동근의 오차상계로 대신 쓰지도 않는다.

## 10. 중간 점검과 주장 한계

| 점검 | 상태 | 직접 근거와 한계 |
|---|---|---|
| 실제 분산 W 고정 | PASS — derived | \(V=W-\delta^2/3\), \(V'(0)=0\)를 다른 항과 함께 미분 |
| endpoint·내부 중심·확률·평균화 항 누락 여부 | PASS — derived | T28.11, T28.14의 다섯 항 분해 |
| 광자 수·평균·분산 보존 | PASS — inherited exact identities and differentiation | 두 중심 법칙은 모든 허용 δ에서 질량1, 평균m, 실제 분산W를 가지므로 그 미분도 보존식과 일치 |
| 이차 커널 퇴화 | PASS — direct algebra | \(k=c_0+c_1E+c_2E^2\)이면 \(T(x,y)=0\), 따라서 \(B_\pm=0\); 같은 실제 W의 응답은 폭에 무관 |
| 적분 부호·계수 | PASS — derived | 두 번 부분적분한 T28.17; 양의 가중치와 \(k'''<0\) |
| 비영 c·단순근 분모 | PASS — conditional derived | 내부근의 \(W>0\), T28.18과 T28.19; 끝값 존재 전제의 수치 근거 수준 유지 |
| 허용 근방 및 일방향 극한 | PASS — derived | T28.24–26; 원자 극한을 밀도 점별/L¹ 수렴으로 해석하지 않음 |
| 끝 분산 \(W=0,LH\) | 범위 제한 | 이번 고정-W 물리 우미분은 내부 W만 대상으로 함; 두 끝은 양의 폭에서 같은 W로 허용되지 않음 |
| 계수의 새 수치값·δ=.05 잔차 | 이 기여에서는 NOT_RUN | 별도 preregistered numerical owner의 실제 실행 대상 |
| 정량 고차 나머지·유효폭·폭 sweep | NOT_RUN / NOT_CLAIMED | \(o(\delta)\) 이상 정량 보증 없음 |
| 독립 최종 판정 | 이 기여자의 역할 아님 | full-history·owner 메시지에 노출된 NONBLIND 후보 생성 |

지지구간 끝점과 내부 중심이 서로 반대 역할로 움직여도 평균·분산이 유지되도록 확률이 함께 조정된다. 따라서 중심 이동만 남기거나 \(f_\delta(c)-k(c)>0\)만 보아 문턱 부호를 설명하지 않는다. 전체 합의 부호는 T28.17이 결정한다.

이 결과는 동결된 초기 \(\epsilon^2t^4\) 계수에 대한 구조 연구다. 유한 시간의 HeIII 총편차, 유한 ε 나머지, 원 J·원자·기체 불확실성, native 동등성, 실제 emitter 또는 우주론 history admission을 다루지 않는다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED** 및 production source/default/runtime 변경 0을 유지한다.

## 11. 실제 작업 범위와 종료

이 생성자는 직접 수식 미분·부분적분·원근 잔차 항등식·한쪽 암묵함수 논증을 작성했다. 자체 대수 점검은 **THEORY_CONTRIBUTOR_SELF_CHECK**이며 독립 최종 판정이 아니다. 기존 PHYS27 전역 모멘트 정리, PHYS24/25 곡률 캠페인, PHYS26/27 수치 근을 재실행하지 않았다. 외부 문헌은 이 기여에서 새로 열람하지 않았으며, 선행 문서에 적힌 citation을 새로 읽었다고 주장하지 않는다.

실제 읽기와 파일 identity, 도구 표시 사건, 코드·수치 실행 0 기록은 [PROVENANCE.json](PROVENANCE.json), 식·의존관계·상태는 [THEORY_CLAIMS.json](THEORY_CLAIMS.json)에 있다. 이번 이론 기여는 현재 계약의 정확한 일차 미분 질문을 해결한 후보로 owner에게 전달하며, 최종 PROMOTE 판단을 대신하지 않는다.
