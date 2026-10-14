# PHYS27 — 반폭 0.05 eV 균일 대역족의 정확한 응답 구간

연구: REI-PHYS27-20261011 · FINITE_WIDTH_RESPONSE_ENVELOPE  
기여자: /root/phys27_theory · GPT-6 Astra · 이론 후보 생성  
근거 상태: **derived, 동결 입력에 조건부 · 독립 최종 판정 전**  
범위: 평균 18 eV, 반폭 δ=0.05 eV 하나, 초기 ε²t⁴ HeIII 응답

## 0. 결론과 근거 상태

같은 반폭의 균일 대역들을 광자 수 기준으로 혼합하는 명시적 분포족에서는, 실제 광자 에너지 분산 W의 허용 구간이

\[
\boxed{W_{\min,\delta}=\frac1{1200}\ {\rm eV}^2
\le W\le W_{\max,\delta}=\frac{850231}{30000}\ {\rm eV}^2}
\tag{T27.1}
\]

다. 각 W에서 모든 가능한 초기 응답은 두 중심점 균일 대역 혼합이 달성하는 정확한 닫힌 구간이다. 상단과 하단을 달성하는 중심 측도 및 실제 에너지 밀도는 각각 유일하다. 양 끝 분산에서 두 경계는 같은 단일 응답으로 합쳐진다.

더 강하게, 같은 **실제 광자 분산** W에서 PHYS26의 델타 선 허용 전체 측도족과 비교하면

\[
\boxed{A_{0,-}(W)<A_{\delta,-}(W)
\le A_{\delta,+}(W)<A_{0,+}(W)}
\quad(W_{\min,\delta}\le W\le W_{\max,\delta}).
\tag{T27.2}
\]

바깥 두 부등식은 유한 폭 분산의 양 끝에서도 엄격하다. 가운데 등호는 그 양 끝에서만 성립한다. 이는 유한 표본 비교가 아니라, 유한 대역 밀도의 절대연속성과 PHYS26 원자 극값의 유일성에서 나온다.

두 유한 폭 영점이 존재하면 그 **물리 분산**을 \(W_{*,\delta}\), \(W_{0,\delta}\)로 정의하여

\[
\boxed{V_{*,0}<W_{*,\delta}<W_{0,\delta}<W_{0,0}}
\tag{T27.3}
\]

를 얻는다. \(V_{*,0}\), \(W_{0,0}\)는 PHYS26의 두 정확근이다. 유한 폭의 비음수 응답 가능 문턱은 증가하고, 모든 스펙트럼의 비음수 응답을 보장하는 문턱은 감소한다. 이 방향은 새 근의 소수값을 비교해서 정하지 않는다.

정확한 함수 정리와 수치 입력의 역할을 분리한다. (T27.1), (T27.2), 경계식·유일성·단조성은 동결된 \(k\in C^3\), \(k''>0\), \(k'''<0\)에 대한 직접 유도다. 두 영점의 존재와 전체 부호 표에는 끝값의 부호가 추가로 필요하다. 이 기여는 그 부호를 PHYS26의 **닫힌 numerically checked 두 부호 입력**으로 연결하는 보조논증을 제시한다. 새 평균화 적분·근 수치는 별도 수치 기여가 담당하며 여기서는 그 값을 만들거나 읽지 않았다. 끝값 부호를 엄밀 interval 인증으로 승격하지 않는다.

이 기여는 full-history와 owner의 포함관계·끝값 논증 제안에 노출된 **NONBLIND** 후보 생성이다. 새 PHYS27 수치 결과 열람, 커널 평가, 근 탐색, 도함수 부호 캠페인, 과거 main/suite, native, gas IVP 실행은 모두 0회다. 최종 PROMOTE 판정은 이 생성자와 분리된 reviewer가 담당한다. 실제 열람과 identity는 [PROVENANCE.json](PROVENANCE.json)에 남긴다.

## 1. 정의와 동결 물리 계약

\[
a=13.61\ {\rm eV},\quad b=24.58\ {\rm eV},\quad m=18\ {\rm eV},
\quad\delta=0.05\ {\rm eV},
\]
\[
L=m-a=4.39\ {\rm eV},\quad H=b-m=6.58\ {\rm eV},
\]
\[
\alpha=a+\delta=13.66\ {\rm eV},\quad
\beta=b-\delta=24.53\ {\rm eV},
\]
\[
\ell=m-\alpha=L-\delta=4.34\ {\rm eV},\quad
h=\beta-m=H-\delta=6.53\ {\rm eV}.
\tag{T27.4}
\]

에너지와 δ는 정확한 십진 값이며, \(0<\delta<\min(L,H)\)다. 대역의 **전체 폭은 0.10 eV**다. 중심 측도 Q는 \([\alpha,\beta]\) 위의 비음수 Borel 광자 수 확률측도다. Q의 원자점은 허용하지만 실제 광자 에너지 측도는

\[
P_\delta^Q(dE)=p_\delta^Q(E)dE,\qquad
p_\delta^Q(E)=\frac1{2\delta}
\int_\alpha^\beta\mathbf1_{[c-\delta,c+\delta]}(E)dQ(c)
\tag{T27.5}
\]

로 정한다. 밀도의 값은 거의 모든 곳에서의 동등성으로 이해한다. 각 지시함수의 끝점 값은 아무 모멘트도 바꾸지 않는다. 이 밀도는 일반적으로 점프를 가질 수 있다. 따라서 이 족은 절대연속 에너지 측도를 가지지만 매끄러운 밀도를 전제하지 않으며, 모든 연속·매끄러운 스펙트럼을 대표하지 않는다.

중심을 \([\alpha,\beta]\)로 제한했으므로 각 대역은 원 지원구간 \([a,b]\) 안에 완전히 들어간다. 대역을 잘라내거나 경계에서 다시 정규화하지 않는다. HI cutoff와 HeI cutoff 사이의 상속된 매끄러운 커널 구간을 벗어나지 않는다.

응답의 물리 정의는 [PHYSICS_CONTRACT.json](../../PHYSICS_CONTRACT.json), SHA256 **46fe6fb98a78ca549f27ed78968850c14bdc12cdd3250892f28e239574005443**을 따른다.

\[
D=E\partial_E,\quad \mathscr C=D(D+3),\qquad
\lambda(E)=c_{\rm light}n_H(1-x_{HII})\sigma(E),
\]
\[
k(E)=\frac{qN_0}{45}\,
\frac{J_x\mathscr C\lambda(E)+J_w\mathscr C[\lambda(E)(E-\chi)]}{4}.
\tag{T27.6}
\]

여기서 중심 에너지 기호 c와 빛의 속도 \(c_{\rm light}\)를 구별한다. 빛의 속도를 자연단위계로 제거하지 않는다. \(N_0\)는 source binary64 0.05 photon/H의 정확한 실수 해석이다. 고정된 초기 기체·q·직렬화 수치 J를 유지하며 \(k\)에는 \(qN_0/45\)가 이미 포함되어 있다. Metric (-+++), gas-comoving proper seconds, 열 변수 w in eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\), 시간계수의 추가 factorial 없음, 초기 등방 각분포 및 ε에 대한 초기 에너지 분포의 독립성을 유지한다.

\([k]=[A]={\rm s}^{-4}\), \([p]={\rm eV}^{-1}\), \([W]=[V]={\rm eV}^2\)다. \(k\)를 먼저 물리 에너지 E에서 구성한 뒤 평균한다. 에너지 의존 계수를 갖는 \(D=E\partial_E\)를 임의로 \(c\partial_c\)로 바꿔 평균 단면적에 재적용하는 절차를 사용하지 않는다.

상속 조건과 그 승인 범위는 [PHYS26 원 유도](../../inputs/PHYS26/contributions/theory/ENVELOPE_DERIVATION_KO.md), [claim 목록](../../inputs/PHYS26/contributions/theory/THEORY_CLAIMS.json), [최종 판정](../../inputs/PHYS26/independent/DECISION_REVIEW_KO.md)에서 소비한다.

\[
k\in C^3([a,b]),\qquad k''(E)>0,\qquad k'''(E)<0.
\tag{T27.7}
\]

PHYS24/25의 닫힌 도함수 인증을 새로 실행하거나 모든 중간 다항식을 다시 감사하지 않는다. 정확한 정리는 직렬화 수치 J와 소스 상수를 정확 실수 입력으로 해석한 계약에 조건부다. 원 J·원자 데이터·기체 상태의 불확실성을 둘러싼 결과가 아니다.

## 2. 정규화·평균·실제 분산

(T27.5)는 보조변수 \(C\sim Q\), \(S\sim U[-\delta,\delta]\)를 독립으로 잡고 \(E=C+S\)로 놓은 분포와 같다. 이 독립성은 정의된 균일 대역 혼합의 수학적 표현이며 새로운 물리적 확률 가정이 아니다. 직접 적분하면

\[
\frac1{2\delta}\int_{-\delta}^{\delta}1\,ds=1,\qquad
\frac1{2\delta}\int_{-\delta}^{\delta}s\,ds=0,\qquad
\frac1{2\delta}\int_{-\delta}^{\delta}s^2\,ds=\frac{\delta^2}{3}.
\tag{T27.8}
\]

Tonelli와 유계 지원에서의 Fubini를 적용하면

\[
0\le p_\delta^Q(E)\le\frac1{2\delta},\qquad
\int_a^bp_\delta^Q(E)dE=1,
\]
\[
\int_a^bE p_\delta^Q(E)dE=\int_\alpha^\beta c\,dQ(c).
\tag{T27.9}
\]

따라서 \(\int c\,dQ=m\)이면 실제 평균도 m이다. 중심 분산 V와 실제 광자 분산 W는

\[
V=\int_\alpha^\beta(c-m)^2dQ(c),
\]
\[
W=\int_a^b(E-m)^2p_\delta^Q(E)dE
=\int\!\left[(c-m)^2+\frac{\delta^2}{3}\right]dQ(c)
=V+\frac{\delta^2}{3}.
\tag{T27.10}
\]

교차항은 균일 변위의 일차 모멘트가 0이므로 사라진다. 이 등식은 작은 폭 근사가 아니다. 실제 광자 수·에너지는 각각 \(N_0\), \(N_0m\)이며 모든 후보에서 보존된다.

\(Q\)가 평균 m이면

\[
\int_\alpha^\beta(c-\alpha)(\beta-c)dQ(c)=\ell h-V.
\tag{T27.11}
\]

왼쪽은 비음수이므로 \(0\le V\le\ell h\). 다음 절의 명시적 측도들이 이 전체 구간을 실현하므로 필요충분조건이다. 현재 δ에서는

\[
\ell h=28.3402\ {\rm eV}^2,\qquad
d_\delta:=\frac{\delta^2}{3}=\frac1{1200}\ {\rm eV}^2,
\]
\[
W\in\mathcal D_\delta=[d_\delta,\ell h+d_\delta]
=\left[\frac1{1200},\frac{850231}{30000}\right]{\rm eV}^2.
\tag{T27.12}
\]

허용집합은 이 구간 밖에서 공집합이며 이후의 부호 양화는 \(W\in\mathcal D_\delta\)에만 적용한다. W=0은 이 유한 폭 족에 허용되지 않는다.

## 3. 평균화 커널로의 부호 이전

\[
f(c):=\bar k_\delta(c)
=\frac1{2\delta}\int_{-\delta}^{\delta}k(c+s)ds,
\qquad c\in[\alpha,\beta].
\tag{T27.13}
\]

\(k\in C^3\)이고 모든 \(c+s\)가 \([a,b]\)에 있으므로, 유계 연속 도함수를 사용해 적분 안으로 미분을 옮길 수 있다.

\[
f^{(j)}(c)=\frac1{2\delta}\int_{-\delta}^{\delta}k^{(j)}(c+s)ds,
\qquad j=1,2,3.
\tag{T27.14}
\]

따라서 \(f\in C^3([\alpha,\beta])\)이고

\[
\boxed{f''(c)>0,\qquad f'''(c)<0.}
\tag{T27.15}
\]

닫힌 끝점의 미분은 해당 한쪽 미분·연속 연장으로 해석한다. 가중치가 양수이고 상속 부호가 모든 적분점에서 엄격하므로 결과도 엄격하다. 경계 밖 외삽, 새 유한차분 부호 계산, 작은 δ 전개가 필요하지 않다.

연속 유계 k에 대한 Fubini로 실제 광자 응답은

\[
A_\delta(Q)=\int_a^bk(E)p_\delta^Q(E)dE
=\int_\alpha^\beta f(c)dQ(c).
\tag{T27.16}
\]

이제 PHYS26 모멘트 정리의 구간·커널·분산을 각각 \([\alpha,\beta],f,V\)로 옮길 모든 조건이 확인되었다. 단조성에는 f″>0가, 극값과 접촉의 방향에는 f‴<0가 쓰인다.

## 4. 모든 W의 경계 중심 측도와 실제 밀도

\(W\in\mathcal D_\delta\)를 고정하고

\[
V=W-d_\delta,\qquad
v=m+\frac V\ell,\qquad u=m-\frac Vh
\tag{T27.17}
\]

로 쓴다. \(0\le V\le\ell h\)이므로 \(v\in[m,\beta]\), \(u\in[\alpha,m]\)다. 두 후보는

\[
\boxed{Q_{\delta,W}^{+}
=\frac{V}{\ell^2+V}\delta_\alpha
+\frac{\ell^2}{\ell^2+V}\delta_v,}
\tag{T27.18}
\]
\[
\boxed{Q_{\delta,W}^{-}
=\frac{h^2}{h^2+V}\delta_u
+\frac{V}{h^2+V}\delta_\beta.}
\tag{T27.19}
\]

가중치는 비음수이며 합은 1이다. 상단 후보의 평균 편차와 중심 분산은

\[
\frac{-\ell V+\ell^2(V/\ell)}{\ell^2+V}=0,
\qquad
\frac{\ell^2V+\ell^2(V/\ell)^2}{\ell^2+V}=V.
\]

하단에서도 \([-h^2(V/h)+Vh]/(h^2+V)=0\),
\([h^2(V/h)^2+Vh^2]/(h^2+V)=V\)다. 따라서 두 실제 밀도 모두 평균 m과 **광자 분산 W**를 가진다.

실제 밀도의 완전한 식은

\[
\boxed{p_{\delta,W}^{+}(E)
=\frac1{2\delta}\left[
\frac{V}{\ell^2+V}\mathbf1_{[a,a+2\delta]}(E)
+\frac{\ell^2}{\ell^2+V}\mathbf1_{[v-\delta,v+\delta]}(E)
\right],}
\tag{T27.20}
\]
\[
\boxed{p_{\delta,W}^{-}(E)
=\frac1{2\delta}\left[
\frac{h^2}{h^2+V}\mathbf1_{[u-\delta,u+\delta]}(E)
+\frac{V}{h^2+V}\mathbf1_{[b-2\delta,b]}(E)
\right].}
\tag{T27.21}
\]

표현의 가중치는 광자 수 비율이며 밀도 높이 자체와 구별한다. 혼합 후 일부 대역이 겹치더라도 지시함수의 합을 그대로 사용한다. 겹침을 삭제하거나 재정규화하지 않는다.

경계 응답은

\[
\boxed{A_{\delta,+}(W)
=\frac{Vf(\alpha)+\ell^2f(m+V/\ell)}{\ell^2+V},}
\tag{T27.22}
\]
\[
\boxed{A_{\delta,-}(W)
=\frac{h^2f(m-V/h)+Vf(\beta)}{h^2+V}.}
\tag{T27.23}
\]

계산상 V를 넣는 위치에 W를 그대로 넣으면 실제 분산 제약을 바꾸게 된다. f 역시 k의 균일 대역 평균이며 중심점의 k값으로 대체하지 않는다.

## 5. 전역 부등식·등호 조건·끝점 퇴화

PHYS26의 닫힌 증명 구조를 새 구간에 적용하는 내용을 명시한다. 중심점 s를 고정하고

\[
R_s(c)=\int_0^1(1-t)f''(s+t(c-s))dt
\tag{T27.24}
\]

로 두면

\[
f(c)=f(s)+f'(s)(c-s)+(c-s)^2R_s(c),\qquad
\partial_cR_s(c)=\int_0^1t(1-t)f'''(s+t(c-s))dt<0.
\tag{T27.25}
\]

이 항등식은 c=s에서 \(R_s(s)=f''(s)/2\)로 정칙이며 c<s와 c>s를 함께 처리한다. 두 이차식

\[
\Pi_+(c)=f(v)+f'(v)(c-v)+R_v(\alpha)(c-v)^2,
\]
\[
\Pi_-(c)=f(u)+f'(u)(c-u)+R_u(\beta)(c-u)^2
\tag{T27.26}
\]

의 잔차는

\[
\Pi_+(c)-f(c)=(c-v)^2[R_v(\alpha)-R_v(c)]\ge0,
\]
\[
f(c)-\Pi_-(c)=(c-u)^2[R_u(c)-R_u(\beta)]\ge0.
\tag{T27.27}
\]

전역 접촉 집합은 정확히 \(\{\alpha,v\}\), \(\{u,\beta\}\)다. 질량·평균·중심 분산을 고정한 모든 Q는 모든 이차식의 기대값이 같으므로 두 부등식을 적분하면

\[
A_{\delta,-}(W)\le A_\delta(Q)\le A_{\delta,+}(W).
\tag{T27.28}
\]

각 후보는 대응하는 접촉점에만 지지되므로 양 끝을 달성한다. 비음수 연속 잔차의 적분이 0이면 Q는 해당 두 접촉점에만 지지되어야 한다. 질량과 평균으로 확률까지 고정되므로

\[
A_\delta(Q)=A_{\delta,+}(W)\iff Q=Q_{\delta,W}^{+},
\]
\[
A_\delta(Q)=A_{\delta,-}(W)\iff Q=Q_{\delta,W}^{-}.
\tag{T27.29}
\]

이는 중심 측도의 유일성을 직접 증명하고, 그 이미지인 실제 밀도도 각각 거의 모든 곳에서 유일하게 정한다. 모든 중심 측도에 대한 일반적인 역합성 유일성 정리를 추가로 가정할 필요가 없다. 어떤 다른 Q가 같은 극값 밀도를 만들더라도 응답도 극값이므로 (T27.29)에 의해 같은 Q여야 한다.

\(0<V<\ell h\)에서는 \(\alpha<u<m<v<\beta\)이고 하단 후보는 상단 접촉점 밖인 β에 양의 질량을 가진다. 따라서

\[
A_{\delta,-}(W)<A_{\delta,+}(W)
\quad(W_{\min,\delta}<W<W_{\max,\delta}).
\tag{T27.30}
\]

V=0에서는 \(\int(c-m)^2dQ=0\)가 \(Q=\delta_m\)를 강제한다. 이 경우 두 밀도와 두 응답은

\[
p_{\min}(E)=\frac1{2\delta}\mathbf1_{[m-\delta,m+\delta]}(E),
\qquad A_{\delta,\pm}(W_{\min,\delta})=f(m)
\tag{T27.31}
\]

로 합쳐진다. V=ℓh에서는 (T27.11)의 적분이 0이므로 Q의 지지는 \(\{\alpha,\beta\}\)에 들어야 한다. 유일 측도·밀도는

\[
Q_{\rm end}=\frac h{\ell+h}\delta_\alpha
+\frac\ell{\ell+h}\delta_\beta,
\]
\[
p_{\max}(E)=\frac1{2\delta}
\left[\frac h{\ell+h}\mathbf1_{[a,a+2\delta]}(E)
+\frac\ell{\ell+h}\mathbf1_{[b-2\delta,b]}(E)\right],
\]
\[
A_{\delta,\pm}(W_{\max,\delta})=B_\delta(m)
:=\frac{h f(\alpha)+\ell f(\beta)}{\ell+h}.
\tag{T27.32}
\]

두 끝 분산에서도 후보식의 분모는 양수이고 영 확률 대역을 제거하면 정확한 유일 밀도가 남는다.

## 6. 전체 응답 구간과 단조성

모든 중심 Q의 응답은 (T27.28)에 속한다. 내부 W에서 어떤 목표값 \(A_t\in[A_{\delta,-},A_{\delta,+}]\)에 대해

\[
\theta=\frac{A_t-A_{\delta,-}}{A_{\delta,+}-A_{\delta,-}},\qquad
Q_\theta=(1-\theta)Q_{\delta,W}^{-}+\theta Q_{\delta,W}^{+}
\tag{T27.33}
\]

를 택하면 같은 중심 평균·분산을 보존하고 응답은 \(A_t\)다. 실제 밀도는 \((1-\theta)p^-+\theta p^+\)이며 실제 광자 분산도 W로 유지된다. 양 끝 W에서는 유일 밀도 하나만 남는다. 따라서

\[
\boxed{\mathcal A_\delta(W)=[A_{\delta,-}(W),A_{\delta,+}(W)]}
\tag{T27.34}
\]

는 전체 달성 구간이다. 중심 측도의 허용집합은 닫힌 모멘트 제약과 콤팩트 지지로 약하게 콤팩트·볼록하지만, 위 구성만으로도 모든 중간값의 달성이 직접 확인된다. 이 혼합은 최대 네 중심·네 대역의 한 구성이다. 내부 응답의 모든 밀도 표현이 유일하거나 최소 대역 수가 네 개라는 주장은 하지 않는다.

δ가 고정되어 있으므로 \(dV/dW=1\)이다. (T27.22), (T27.23)를 직접 미분하면

\[
\frac{dA_{\delta,+}}{dW}
=\frac{f(\alpha)-f(v)+(v-\alpha)f'(v)}{(v-\alpha)^2}
=R_v(\alpha)>0,
\]
\[
\frac{dA_{\delta,-}}{dW}
=\frac{f(\beta)-f(u)-(\beta-u)f'(u)}{(\beta-u)^2}
=R_u(\beta)>0.
\tag{T27.35}
\]

마지막 양수성은 f″>0에서 나온다. 기울기 단위는 \({\rm s}^{-4}{\rm eV}^{-2}\)다. u는 W와 함께 감소하지만 하단 응답은 W와 함께 증가한다. 극값 방향·등호 구조와 단조성의 부호 전제를 섞지 않는다.

## 7. PHYS26 전체 측도족에 대한 엄격한 포함

PHYS26의 원 경계를 \(A_{0,\pm}\), 전체 허용 측도족을 \(\mathcal P_W\)라 쓰자. 원 분산 범위는 \([0,LH]\)다. (T27.9), (T27.10)으로 모든 유한 폭 측도 \(P_\delta^Q\)는 같은 W의 \(\mathcal P_W\)에 속한다. 또한

\[
W_{\min,\delta}>0,\qquad
LH-W_{\max,\delta}
=\delta(L+H)-\frac43\delta^2>0,
\tag{T27.36}
\]

이므로 유한 폭의 전체 허용 구간은 원 범위의 내부에 있다. 현재 위 차이는 정확히 \(3271/6000\ {\rm eV}^2\)다.

PHYS26은 그 내부의 각 W에서 원 경계를 달성하는 유일 측도가 두 원자점으로 이루어진 \(P_{0,W}^{+}\), \(P_{0,W}^{-}\)임을 증명했다. 반면 \(P_\delta^Q=p_\delta^QdE\)는 절대연속 확률측도이며 모든 단일점의 질량이 0이다. 따라서 어느 원자 극값과도 같을 수 없다. 원 정리의 등호 분류에 의해 **각** Q에서

\[
A_{0,-}(W)<A_\delta(Q)<A_{0,+}(W).
\tag{T27.37}
\]

여기서 모든 Q의 값이 열린 구간에 들어간다는 사실만으로 infimum·supremum의 엄격성을 자동 추론하지 않는다. 이번 족에서는 (T27.18), (T27.19)가 extrema를 실제 달성하므로, 그 Q 두 개를 (T27.37)에 대입하여 (T27.2)의 두 엄격한 바깥 부등식을 얻는다. 이 달성이 논증에 필요하다.

결론은 동일한 실제 W에서의 비교다. 중심 분산 V를 원 스펙트럼의 분산으로 비교한 결론이 아니다. 또한 다른 δ의 두 uniform-band 족이 서로 포함된다는 주장은 여기서 증명하지 않았다. 따라서 이 한 폭과 δ=0 사이의 결과를 모든 폭에 대한 단조 phase diagram으로 확대하지 않는다.

## 8. 영점 존재의 전제와 현재 폭에서의 부호 근거

두 유일 영점이 존재하기 위한 충분하고 필요한 엄격한 끝값 조건은

\[
f(m)<0<B_\delta(m).
\tag{T27.38}
\]

양 끝을 포함하는 두 함수가 연속·엄격 증가하며 끝값을 공유하기 때문이다. 이 조건은 단지 \(k''>0,k'''<0\)라는 곡률 부호만으로 따라오지 않는다. 예를 들어 k에 큰 양의 상수를 더하면 곡률은 그대로지만 모든 응답이 양수가 될 수 있다.

새 평균화 끝값을 계산하지 않고도 현재 폭에서 이 부호를 연결할 수 있는 **조건부 보조논증**이 있다. PHYS26 첫 원 결과에서 다음 두 값을 실제 열람했다.

| 상속 입력 | 원 수치 응답, s⁻⁴ | 근거 등급 |
|---|---:|---|
| \(A_{0,+}(8)\) | \(-5.03772352558500409185\times10^{-65}\) | inherited numerically checked |
| \(A_{0,-}(26)\) | \(+2.23978782425133756004\times10^{-65}\) | inherited numerically checked |

원문은 [PHYS26 첫 수치 JSON](../../inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json)의 variance_cases에서 label=eight, twenty_six인 두 레코드다. 이 기여가 원 프로그램을 재실행하거나 소수값을 rigorous interval로 재분류한 것은 아니다. 이 두 **정확한 응답의 부호를 기존 수치 evidence가 지지하는 전제로 소비**하면, 정확한 \(W_{\min,\delta}<8\) 및 \(26<W_{\max,\delta}\), PHYS26의 엄격 단조성과 (T27.2)로

\[
f(m)=A_{\delta,+}(W_{\min,\delta})
<A_{0,+}(W_{\min,\delta})<A_{0,+}(8)<0,
\]
\[
B_\delta(m)=A_{\delta,-}(W_{\max,\delta})
>A_{0,-}(W_{\max,\delta})>A_{0,-}(26)>0.
\tag{T27.39}
\]

이 논증은 유한 폭 효과가 작다고 암묵적으로 가정하지 않는다. 다만 최초 두 부호 전제의 근거 등급은 그대로 남는다. 수치 owner의 새 평균화 계산은 (T27.38)을 별도로 수치 확인하고 근을 근사할 수 있지만, 이 문서에서는 아직 그 결과를 읽거나 승인하지 않았다. 엄밀한 전산 구간 인증은 별도 미실행 항목이다.

## 9. 정확근·전체 부호 영역·문턱 이동

(T27.38)을 전제로 각 경계는 허용 내부에서 정확히 한 영점을 갖는다. 중심 노드의 정확근은

\[
(v_{*,\delta}-m)f(\alpha)+\ell f(v_{*,\delta})=0,
\qquad m<v_{*,\delta}<\beta,
\]
\[
h f(u_{0,\delta})+(m-u_{0,\delta})f(\beta)=0,
\qquad\alpha<u_{0,\delta}<m.
\tag{T27.40}
\]

실제 광자 분산 문턱은

\[
\boxed{W_{*,\delta}=d_\delta+\ell(v_{*,\delta}-m),\qquad
W_{0,\delta}=d_\delta+h(m-u_{0,\delta}).}
\tag{T27.41}
\]

중심 분산 문턱이 필요하면 \(V_{*,\delta}=W_{*,\delta}-d_\delta\),
\(V_{0,\delta}=W_{0,\delta}-d_\delta\)로 별도 정의한다. PHYS26 기호 \(V_{*,0}\)는 δ=0에서의 실제 분산이기도 하다.

상단 영점에서 내부 간격이 엄격하므로

\[
A_{\delta,-}(W_{*,\delta})
<A_{\delta,+}(W_{*,\delta})=0.
\]

하단이 엄격 증가하므로

\[
W_{\min,\delta}<W_{*,\delta}<W_{0,\delta}<W_{\max,\delta}.
\tag{T27.42}
\]

전체 부호 분류는 다음과 같다. 모든 Q는 해당 W의 비어 있지 않은 허용집합에 속한다.

| 실제 광자 분산 W | 경계 부호와 모든 허용 밀도에 대한 결론 |
|---|---|
| \(W_{\min,\delta}\le W<W_{*,\delta}\) | \(A_{\delta,-}\le A_{\delta,+}<0\); 모두 음수 |
| \(W=W_{*,\delta}\) | \(A_{\delta,-}<0=A_{\delta,+}\); 모두 비양수, 영 밀도는 \(p^+\) 하나뿐 |
| \(W_{*,\delta}<W<W_{0,\delta}\) | \(A_{\delta,-}<0<A_{\delta,+}\); 음·영·양 모두 가능 |
| \(W=W_{0,\delta}\) | \(A_{\delta,-}=0<A_{\delta,+}\); 모두 비음수, 영 밀도는 \(p^-\) 하나뿐 |
| \(W_{0,\delta}<W\le W_{\max,\delta}\) | \(0<A_{\delta,-}\le A_{\delta,+}\); 모두 양수 |

혼합 영역에서

\[
\theta_0=\frac{-A_{\delta,-}}{A_{\delta,+}-A_{\delta,-}}\in(0,1)
\tag{T27.43}
\]

의 (T27.33)은 영 응답을 내는 하나의 중심 측도·밀도를 준다. 정확한 식은 영 응답이지만 유한 소수로 계산하면 잔차가 남을 수 있다. 내부 영역의 모든 영 밀도의 유일성은 주장하지 않는다.

정확한 양화는

\[
\begin{aligned}
\exists Q:\ A_\delta(Q)\ge0&\iff W\ge W_{*,\delta},&
\exists Q:\ A_\delta(Q)>0&\iff W>W_{*,\delta},\\
\forall Q:\ A_\delta(Q)\ge0&\iff W\ge W_{0,\delta},&
\forall Q:\ A_\delta(Q)>0&\iff W>W_{0,\delta},\\
\exists Q:\ A_\delta(Q)=0&\iff W_{*,\delta}\le W\le W_{0,\delta}.
\end{aligned}
\tag{T27.44}
\]

따라서 비음수 응답 가능 최소 분산은 \(W_{*,\delta}\), 모든 응답의 비음수성을 강제하는 최소 분산은 \(W_{0,\delta}\)다. 엄격 양수 존재와 모든 엄격 양수의 분산 집합은 각각 \((W_{*,\delta},W_{\max,\delta}]\), \((W_{0,\delta},W_{\max,\delta}]\)여서 최소 원소가 없으며 각 아래끝이 infimum이다.

PHYS26 정확근과의 이동은 새 근 자체에서 (T27.2)를 적용해 얻는다.

\[
A_{0,+}(W_{*,\delta})>A_{\delta,+}(W_{*,\delta})=0
\ \Longrightarrow\ W_{*,\delta}>V_{*,0},
\]
\[
A_{0,-}(W_{0,\delta})<A_{\delta,-}(W_{0,\delta})=0
\ \Longrightarrow\ W_{0,\delta}<W_{0,0}.
\tag{T27.45}
\]

여기에 (T27.42)를 결합하면 (T27.3)을 얻는다. 이 증명은 옛 근이 새 허용 분산 구간에 속한다는 별도 가정을 요구하지 않는다. 새 근의 존재, 원 경계의 정확근·단조성, 같은 W에서의 엄격 포함이 충분하다. 방향은 derived이고, 이동량과 새 근의 소수는 이 기여에서 **미평가**다.

## 10. δ→0의 극한과 퇴화 점검

수치 캠페인은 δ=0.05 하나다. 다음은 그 계약의 델타 선 극한을 확인하는 해석적 점검이며 여러 폭의 새 수치 결과가 아니다. \(0<\delta<\min(L,H)\)에서 같은 식들을 생각하자. \(M_2=\max_{E\in[a,b]}|k''(E)|\)는 유한하고 Taylor 항등식의 홀수항은 균일 평균에서 사라진다.

\[
\left|\bar k_\delta(c)-k(c)\right|
\le\frac{M_2\delta^2}{6},\qquad c\in[a+\delta,b-\delta].
\tag{T27.46}
\]

이는 존재하는 유계 도함수로 얻는 해석적 한계이며 M₂의 새 수치 상계는 계산하지 않았다. 엄격 볼록성이므로 실제 차이는 양수지만, 이것만으로 같은 **광자 분산**에서의 경계 이동을 정할 수는 없다. 그 비교에는 중심 지지의 축소와 \(V=W-\delta^2/3\)가 함께 들어가며 §7이 이를 처리한다.

\(\delta_n\downarrow0\), \(W_n\in\mathcal D_{\delta_n}\), \(W_n\to W\in[0,LH]\)인 임의의 허용 경로를 잡으면

\[
\alpha_n\to a,\quad\beta_n\to b,\quad
\ell_n\to L,\quad h_n\to H,\quad V_n\to W.
\]

(T27.18)–(T27.23)의 노드와 확률은 연속적으로 원 PHYS26 노드·확률에 수렴하므로

\[
Q^\pm_{\delta_n,W_n}\ \Rightarrow\ P^\pm_{0,W},\qquad
A_{\delta_n,\pm}(W_n)\to A_{0,\pm}(W).
\tag{T27.47}
\]

실제 광자 측도도 같은 약한 극한을 가진다. 임의의 연속 시험함수 φ에서
\(|\int\phi\,dP_\delta^Q-\int\phi\,dQ|\le\omega_\phi(\delta)\to0\)이기 때문이다. 여기서 \(\omega_\phi\)는 콤팩트 구간에서의 연속성 계수다. 원자 극한이므로 밀도 함수의 점별 또는 L¹ 수렴을 주장하지 않는다.

고정 W가 \((0,LH)\) 내부이면 충분히 작은 δ에서 같은 W를 사용할 수 있다. W=0과 W=LH는 δ>0에서 불가능하므로 각각 \(W_n=W_{\min,\delta_n}\), \(W_n=W_{\max,\delta_n}\)를 따라 접근해야 한다. 이 경로에서 최소 분산 균일 대역은 \(\delta_m\), 최대 분산 두 대역은 PHYS26의 양 끝점 원자 혼합으로 수렴한다.

PHYS26 끝값 \(k(m)<0<B_0(m)\)를 전제로 하면 (T27.47)의 끝점 수렴으로 충분히 작은 δ에서 (T27.38)이 유지된다. 각 원 영점의 양쪽에서 원 경계는 반대 부호를 가지며, 그 두 고정 W에서의 경계 수렴과 엄격 단조성으로 새 영점을 끼울 수 있다. 따라서

\[
W_{*,\delta}\to V_{*,0},\qquad W_{0,\delta}\to W_{0,0}
\quad(\delta\downarrow0).
\tag{T27.48}
\]

δ=0.05가 그러한 충분히 작은 폭이라는 사실을 극한 명제만으로 단정하지 않는다. 현재 폭의 끝값은 §8의 별도 부호 근거를 사용한다. 문턱 이동의 수렴률·일차 계수나 다른 δ 사이의 단조성은 여기서 주장하지 않는다.

곡률 엄격성을 제거한 이차 커널 \(k(E)=c_0+c_1E+c_2E^2\)에서는

\[
\bar k_\delta(c)=c_0+c_1c+c_2(c^2+d_\delta),\qquad
A_\delta=c_0+c_1m+c_2(m^2+W)
\]

가 모든 같은 W의 측도에서 같다. 원 경계와 유한 폭 경계도 같으므로 (T27.2)의 엄격한 포함과 극값 유일성은 일반적으로 사라진다. 이는 k‴<0 조건의 실질적 역할을 보여 주는 직접 대수 점검이다.

## 11. 주장 등급과 완료 범위

| 결과 | 근거 상태와 실제 범위 |
|---|---|
| 정규화·평균·V와 W의 관계·정확한 분산 범위 | derived; 직접 적분과 비음수 모멘트 항등식 |
| 평균화 커널의 f″>0, f‴<0 | derived; 상속된 닫힌 부호를 양의 평균에 이전 |
| 모든 W의 sharp interval·중심 측도·밀도 유일성·끝점 | derived; 새 구간으로의 전역 이차 접촉식 적용 |
| 동일 실제 W에서의 엄격한 원 구간 포함 | derived; 절대연속·원 원자 극값의 유일성·새 극값의 달성 |
| 두 영점의 존재·전체 부호 영역 | derived conditional on endpoint signs; 끝값 전제는 상속 수치 부호로 지지됨 |
| 두 문턱의 엄격한 이동 방향 | derived conditional on root existence; 새 수치값 비교 없음 |
| δ→0의 경계·극값 측도·근 수렴 | derived; 약한 수렴, 고정 폭 수치캠페인 아님 |
| 새 PHYS27 평균 적분·근 수치·구현 정확도 | 이 기여에서는 미실행·미열람; 별도 numerical owner와 final gate 대상 |

단위·정규화, 끝점의 영 확률, 두 분산 정의, 부호·양화의 strict/nonstrict, 유한 폭 밀도의 절대연속성, 원자 극한의 수렴 위상을 직접 점검했다. 이론 기여자의 자체 논증 점검은 독립 최종 판정이 아니며 과학 실행 횟수로 세지 않는다.

첫 도구 출력의 일부가 길이 제한으로 잘렸고 필요한 원문·JSON 부분을 선택 재열람했다. 이는 도구 표시 사건이며 과학 실패나 허용오차 변경이 아니다. 새 외부 문헌 열람도 없으며 PHYS26에 실린 문헌을 새로 읽었다고 주장하지 않는다. 코드·원 수치·판정의 집계는 owner가 별도 수행한다.

초기 ε²t⁴ 계수의 부호는 유한 시간의 전체 HeIII 편차나 이온 분율 자체의 부호가 아니다. 영 경계에서도 높은 시간차수 또는 유한 ε 나머지의 소멸을 말하지 않는다. **Physical HOLD**, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 생산 source/default/runtime 변경, native 동등성, 물리 방출원 admission, J·원자·기체 불확실성, 모든 연속 스펙트럼 대표성, 세계 최초성을 승인하지 않는다.

이 기여의 이론 후보 생성은 여기서 완료한다. 핵심 주장·의존 관계·새 수치값 미평가 상태는 [THEORY_CLAIMS.json](THEORY_CLAIMS.json), 실제 읽기와 실행 범위는 [PROVENANCE.json](PROVENANCE.json)에 있다.
