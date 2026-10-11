# PHYS31 — 같은 이차 모멘트의 대칭 프로파일을 구별하는 첫 국소 차수

연구 기여: REI-PHYS31-20261011. 기여자 /root/phys31_theory.  
상태: **이론 후보 초안 — 새 PHYS31 계약 대기; 최종 freeze와 최종 판정 전**.  
근거: **직접 유도**, 고정 커널과 명시한 정칙성·단순근 전제에 조건부.  
역할: 같은 host·GPT-6 Astra Pro·부모 대화 이력을 사용하는 NONBLIND 후보 생성자이며 최종 독립 판정자가 아니다.

## 0. 답과 적용 범위

PHYS30의 고정 중심 구간, 실제 분산, 일반 대칭 확률측도 정의를 유지한다. 같은 이차 모멘트를 가진 두 프로파일의 차이를 첫째 프로파일에서 둘째 프로파일을 뺀 방향으로 정의한다.

상속한 \(k\in C^3([a,b])\)만으로도 같은 정확한 기준 수준의 두 문턱은 삼차까지 같은 전개를 가지며

\[
W_{j,\nu}(\delta)-W_{j,\widetilde\nu}(\delta)=o(\delta^3)
\qquad(\delta\downarrow0)
\tag{T31.1}
\]

이다. 이 결과를 \(O(\delta^4)\)로 강화하려면 추가 전제가 필요하다. 아래의 같은 양의 밀도 프로파일 쌍에 대해, 허용되는 \(C^3\) 커널의 문턱 차이가 임의의 \(3<p<4\)에 대해 비영 \(\delta^p\) 항부터 시작하는 반례를 구성한다.

추가로 \(k\in C^4([a,b])\)를 가정하면

\[
\boxed{
\Delta b_{4,j}
=-\frac{\Delta\mu_4}{24C_j}\mathcal H_{4,j},\qquad
\mathcal H_{4,j}=p_j k^{(4)}(e_j)+q_j k^{(4)}(x_j),\qquad
C_j=F_W(0,w_j)>0,
}
\tag{T31.2}
\]

\[
W_{j,\nu}(\delta)-W_{j,\widetilde\nu}(\delta)
=\Delta b_{4,j}\delta^4+o(\delta^4).
\tag{T31.3}
\]

여기서 \(b_{4,j,\nu}=W_{j,\nu}^{(4)}(0^+)/24\)다. **사차는 첫 허용 정수 차수이며, \(\Delta\mu_4\mathcal H_{4,j}\ne0\)일 때만 실제 첫 비영 차수**다. 사차 계수가 소거되면 다음 차수가 반드시 육차라는 결론은 나오지 않는다.

주 수치 비교에 넘기는 프로파일은 균일 밀도와 아래의 양의 사차 다항식 밀도다. 둘 다 \(\mu_2=1/3\)이고 \(\Delta\mu_4=8/315\)이므로

\[
\boxed{\Delta b_{4,j}^{P_4-u}=-\frac{\mathcal H_{4,j}}{945C_j}.}
\tag{T31.4}
\]

이 기여자는 새 물리 도함수 값이나 이 계수의 소수값을 계산하지 않았다. 물리 커널의 추가 정칙성 확인과 고정 노드의 \(k^{(4)}\) 수치값은 다른 기여의 실제 근거를 필요로 한다.

## 1. 실제로 읽은 선행 근거와 불변조건

PHYS30의 물리 계약, PHYS31 인수문, 전체 이론 유도와 주장 목록, 최종 검토 한국어 본문을 직접 읽었다. 최종 decision JSON에서는 실제 PROMOTE_SCOPED, fatal_issue_count 0, 수학 평가, 남은 한계와 다음 질문의 PROPOSED / NOT_RUN 상태를 선별적으로 읽었다. PHYS30의 판정은 이차 결과를 승인한 것이며 이 문서의 고차 결과를 선행 승인한 것이 아니다. 새 계약이 고정되기 전에는 이 문서를 이론 후보로만 취급한다.

고정 에너지와 거리의 수치는

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad H=b-m=6.58\quad({\rm eV})
\tag{T31.5}
\]

이다. 폭은 물리적으로 \(\delta\ge0\)이고

\[
0\le\delta<\min(L,H),\qquad
Y\in[a+\delta,b-\delta].
\tag{T31.6}
\]

두 프로파일 \(\nu,\widetilde\nu\)는 \([-1,1]\) 위의 비음수 대칭 Borel 확률측도다. 폭, 실제 분산 \(W\), 중심 \(Y\), 분지 \(j\)와 독립인 고정 측도다. 밀도의 존재나 매끄러움은 일반 정리에 요구하지 않으며 원자를 허용한다. 모든 홀수 모멘트는 0이고

\[
\mu_2=\int z^2d\nu=\int z^2d\widetilde\nu,\qquad
\Delta\mu_4=\int z^4d\nu-\int z^4d\widetilde\nu.
\tag{T31.7}
\]

광자 법칙은 중심 법칙과 프로파일의 독립 곱측도를 \(E=Y+\delta Z\)로 밀어낸 것이다. PHYS30에서 직접 증명한 정확한 모멘트 관계는

\[
W=V+\mu_2\delta^2,\qquad
V=W-\mu_2\delta^2,\qquad
\mu_2\delta^2\le W\le(L-\delta)(H-\delta)+\mu_2\delta^2.
\tag{T31.8}
\]

같은 \(\mu_2\) 때문에 두 프로파일의 중심 분산, 허용 분산 구간, 중심 위치와 확률은 모든 허용 \((\delta,W)\)에서 정확히 같다. 프로파일의 실제 지원이 좁다는 이유로 중심 구간을 넓히지 않는다.

상속 커널 전제는

\[
k\in C^3([a,b]),\qquad k''>0,\qquad k'''<0.
\tag{T31.9}
\]

끝점 미분은 물리 구간 안에서의 한쪽 미분과 연속 극한이다. 추가 \(C^4\) 전제는 필요할 때 명시한다. 여기서 T31.9의 부호나 물리 모델의 \(C^4\) 여부를 재인증하지 않는다.

\(k,F,A\)의 단위는 초기 HeIII의 \(\epsilon^2t^4\) 응답 계수인 \({\rm s}^{-4}\)다. 기존 metric \((-,+,+,+)\), gas-comoving proper seconds, 에너지 eV, 열 변수 eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\)와 시간계수의 추가 factorial 없음이라는 정의를 보존한다. \(c_{\rm light},\hbar,k_B\)를 새로 1로 놓지 않는다.

## 2. 비교에 쓰는 공통 중심 기하

끝점 확률을 먼저 쓰는 두 분지의 공통 표기를 유지한다.

| 분지 | \(s\) | \(R\) | \(e=m-sR\) | \(x(0,W)=m+sW/R\) | 영폭 기준점 |
|---|---:|---|---|---|---|
| 상단 응답 \(F_+\) | \(+1\) | \(L\) | \(a\) | \(m+W/L\) | \(w_*\) |
| 하단 응답 \(F_-\) | \(-1\) | \(H\) | \(b\) | \(m-W/H\) | \(w_0\) |

\[
r=R-\delta,\quad e_\delta=e+s\delta,\quad
x_{\delta,W}=m+\frac{sV}{r},\quad
p_{\delta,W}=\frac{V}{r^2+V},\quad
q_{\delta,W}=1-p_{\delta,W},\quad V=W-\mu_2\delta^2,
\tag{T31.10}
\]

\[
f_{\delta,\nu}(y)=\int k(y+\delta z)d\nu(z),\qquad
F_\nu(\delta,W)=p_{\delta,W}f_{\delta,\nu}(e_\delta)
+q_{\delta,W}f_{\delta,\nu}(x_{\delta,W}).
\tag{T31.11}
\]

\(p,q,e_\delta,x_{\delta,W}\)는 두 프로파일에 공통이다. 따라서 두 응답의 차이는 평균 커널 차이 두 개의 같은 비음수 가중합이다. 이 구조가 기하의 복잡한 고차 미분을 전부 새로 계산하지 않고도 프로파일 차이를 구할 수 있게 한다.

T31.9의 Hermite 부호 아래에서 이 두 응답이 극값이라는 PHYS30의 증명은 **해당 고정 공통 프로파일의 중심 혼합족 안에서만** 사용한다. 양의 폭에서 임의 광자 모멘트 법칙 전체의 극값으로 확장하지 않는다. 비교 정리 자체에는 T31.11의 응답 정의와 \(F_W\ne0\)가 핵심이며, Hermite 부호는 이 응답의 극값 해석을 지지한다.

정확한 수준 \(A\)와 내부 기준점 \(w\in(0,LH)\)를 택하고

\[
F_\nu(0,w)=F_{\widetilde\nu}(0,w)=A
\tag{T31.12}
\]

라고 한다. \(A=0\)이면 정확한 영폭 문턱이고, 유한 저장 기준점을 쓸 때는 정의된 비영 수준 \(A=F(0,\widehat w)\)를 그대로 유지한다. 정확한 영점의 존재나 저장점 오차의 수치 enclosure는 이 정리의 결과가 아니다.

## 3. 일반 측도에 대한 균일 Taylor 나머지

\(n=3\) 또는 \(4\)이고 \(k\in C^n([a,b])\)라 하자. \(k^{(n)}\)의 연속성 모듈러스를

\[
\omega_n(h)=\sup\{|k^{(n)}(u)-k^{(n)}(v)|:
u,v\in[a,b],\ |u-v|\le h\}
\tag{T31.13}
\]

로 두면 \(\omega_n(h)\to0\)이다. \(y,y+h\in[a,b]\)이면 그 사이 선분도 이 구간에 있고, 반복한 미적분의 기본정리로

\[
k(y+h)=\sum_{\ell=0}^{n}\frac{h^\ell}{\ell!}k^{(\ell)}(y)
+r_n(y,h),\qquad
|r_n(y,h)|\le\frac{|h|^n}{n!}\omega_n(|h|).
\tag{T31.14}
\]

실제로 \(n-1\)차 적분 나머지는
\(h^n/(n-1)!\int_0^1(1-t)^{n-1}k^{(n)}(y+th)dt\)다.
여기에서 \(k^{(n)}(y)\)를 더하고 빼면 T31.14를 얻는다. \(h\)의 부호와 무관하며 끝점에서는 원 구간 안의 선분만 사용한다.

각 \(\delta\)에서 \(y\in[a+\delta,b-\delta]\)이고 \(|z|\le1\)이므로 \(h=\delta z\)를 넣을 수 있다. 두 측도에 대해 적분하고 빼면

\[
f_{\delta,\nu}(y)-f_{\delta,\widetilde\nu}(y)
=\sum_{\ell=0}^n\frac{\delta^\ell\Delta\mu_\ell}{\ell!}
k^{(\ell)}(y)+\mathcal R_n(\delta,y),
\tag{T31.15}
\]

\[
|\mathcal R_n(\delta,y)|
\le\frac{\delta^n\omega_n(\delta)}{n!}
\left(\int|z|^n d\nu+\int|z|^n d\widetilde\nu\right)
\le\frac{2\delta^n\omega_n(\delta)}{n!}.
\tag{T31.16}
\]

질량과 \(\mu_2\)가 같고 대칭이므로 \(\Delta\mu_\ell=0\) for \(\ell=0,1,2,3\). 따라서 \(C^3\)에서

\[
\boxed{\Delta f_\delta(y)=o(\delta^3)}
\tag{T31.17}
\]

가 허용되는 모든 중심에서 균일하게 성립한다. \(C^4\)에서는

\[
\boxed{
\Delta f_\delta(y)=\frac{\Delta\mu_4}{24}
k^{(4)}(y)\delta^4+o(\delta^4)
}
\tag{T31.18}
\]

가 균일하게 성립한다.

이는 일반 유한 측도에 대한 직접 나머지 적분이다. 프로파일의 도함수·밀도·수치 적분·커널의 지원 밖 연장을 쓰지 않았다. T31.16은 미지의 \(\omega_n\)로 표현한 해석적 부등식이며, 물리 모델의 수치 나머지 상계나 안전한 폭을 계산한 것은 아니다.

## 4. 움직이는 중심의 삼차·사차 미분 점검

T31.15만으로도 응답 차수는 정해지지만, 움직이는 중심 때문에 대칭성이 모든 홀수 폭 미분을 없앤다고 오해하지 않도록 chain rule을 명시한다.

허용되는 매끄러운 경로 \(Y(\delta,W)\)에 대해
\(\Psi_\nu=\int k(Y+\delta z)d\nu\)라 하고, 영폭에서 \(u=Y_\delta\), \(v=Y_{\delta\delta}\), \(t=Y_{\delta\delta\delta}\), \(h=Y_{\delta\delta\delta\delta}\)라 쓰자. 모든 값은 실제 \(W\) 고정 편미분이다. 직접 곱미분으로

\[
\Psi_{\delta\delta\delta}
=k'''(Y)(u^3+3u\mu_2)+3k''(Y)uv+k'(Y)t,
\tag{T31.19}
\]

\[
\begin{aligned}
\Psi_{\delta\delta\delta\delta}
={}&k^{(4)}(Y)(u^4+6u^2\mu_2+\mu_4)\\
&+6k'''(Y)v(u^2+\mu_2)
+3k''(Y)v^2+4k''(Y)ut+k'(Y)h.
\end{aligned}
\tag{T31.20}
\]

삼차식에는 \(\mu_3=0\)이 사용되었지만 \(u^3+3u\mu_2\)는 일반적으로 0이 아니다. 즉 개별 프로파일의 삼차 폭 응답이나 삼차 문턱계수가 사라지는 것은 아니다.

같은 \(\mu_2\)이면 \(V\)와 \(Y\)의 모든 도함수가 공통이고, T31.19가 공통이다. T31.20의 차이는 \(\Delta\mu_4 k^{(4)}(Y)\) 하나다. 확률을 곱미분한 항 중 확률의 도함수가 한 번이라도 작용한 항은 평균 커널의 폭 미분 차수가 3 이하이므로 프로파일 차이가 0이다.

더 일반적으로, \(\partial_\delta^a\partial_W^b\Psi\)의 적분항에서 \(z\)의 차수는 최대 \(a\)다. \(W\) 미분은 \(z\)를 새로 만들지 않는다. 따라서

\[
\partial_\delta^a\partial_W^b\Delta F(0,W)=0
\quad(a+b\le3),
\tag{T31.21}
\]

그리고 \(C^4\)에서 총차수 4인 편미분의 차이도 \((a,b)=(4,0)\) 이외에는 0이다. 남는 한 성분은

\[
\boxed{\Delta F_{\delta\delta\delta\delta}(0,W)
=\Delta\mu_4\left[p\,k^{(4)}(e)+q\,k^{(4)}(x)\right].}
\tag{T31.22}
\]

끝점 경로는 \(a+\delta(1+z)\), \(b+\delta(z-1)\)이므로 \(u=\pm1\)이고, 이 역시 실제 지원 안에서 T31.19–20을 만족한다. 음의 물리 폭은 사용하지 않는다.

## 5. 실제 물리 한쪽 근의 존재와 고차 정칙성

\(w\in(0,LH)\) 주위의 작은 닫힌 구간 \(J\subset(0,LH)\)를 고르면, T31.8의 양 끝 연속성 때문에 어떤 \(\delta_0>0\)에 대해 모든 \(W\in J\), \(0\le\delta\le\delta_0\)가 실현가능 내부에 놓인다. 모든 분모는 양수이고 \(r>0\)다.

\(k\in C^n\)이면 \(k^{(\ell)}\), \(0\le\ell\le n\), 는 유계다. 합성 미분의 항은 유계인 기하 도함수, \(|z|\le1\), 유계 커널 도함수의 곱이므로 고정 확률측도에 대한 지배함수가 있다. 따라서 \(F_\nu\)는 이 물리 반직사각형에서 \(n\)차까지 미분 가능하고 모든 편미분은 \(\delta=0\)에 오른쪽으로 연속 접한다. 원자 측도에도 동일하다.

PHYS30의 직접 분산 미분식을 다시 쓰면, \(g=f_{\delta,\nu}\)에 대해

\[
F_W
=\frac{g(e_\delta)-g(x)+(x-e_\delta)g'(x)}{(x-e_\delta)^2}
=\int_0^1 t\,g''(e_\delta+t(x-e_\delta))dt>0.
\tag{T31.23}
\]

\(m_2=\min_{[a,b]}k''>0\)가 존재하므로 \(g''\ge m_2\), \(F_W\ge m_2/2\)다. 여기서 \(m_2\)는 해석적 존재값이며 새 수치 최소값이 아니다.

\(F(0,W)-A\)는 \(w\) 양쪽의 가까운 점에서 부호가 다르다. 연속성은 그 부호를 작은 양의 폭에서 보존한다. 중간값정리와 T31.23은 유일한 근 \(W_\nu(\delta)\in J\)를 주고, 구간을 줄이면 \(W_\nu(\delta)\to w\)다. 평균값정리와 \(F(\delta,w)-A=O(\delta)\)는 \(W_\nu(\delta)-w=O(\delta)\)를 준다.

\(\delta>0\)의 내부에서는 암묵함수 미분이 가능하다. 첫 식 \(W'=-F_\delta/F_W\)와 그 반복 미분에서 최고 근 도함수의 계수는 언제나 \(F_W\)다. \(r\)차 근 도함수는 \(r\)차 이하의 \(F\) 편미분과 \(r-1\)차 이하 근 도함수의 다항식을 \(F_W\)로 나눈 것이다. 귀납하면 \(r\le n\)인 모든 근 도함수는 \(\delta=0\)에 유한한 연속 극한을 가진다. 한 단계 낮은 근 도함수의 평균값정리를 적용하면 이 극한이 그 함수의 실제 오른쪽 도함수다.

이로써 \(W_\nu\)는 물리 한쪽 \(C^n\)이고

\[
W_\nu(\delta)=w+c\delta+d\delta^2+b_3\delta^3
+b_{4,\nu}\delta^4+o(\delta^4)
\tag{T31.24}
\]

가 \(n=4\)에서 성립한다. \(n=3\)에서는 사차 항을 제외하고 나머지를 \(o(\delta^3)\)로 쓴다. 계수는 각각 \(W^{(r)}(0^+)/r!\)이다. 나머지는 근의 연속된 최고 도함수에 대한 적분 Taylor 식에서 얻으며 형식적 급수만 가정한 것이 아니다.

## 6. 근의 공통 삼차와 사차 차이

\(C=F_W(0,w)>0\)이고 PHYS30의 \(c,d\)를 사용하면 삼차계수는

\[
b_3=-\frac{
F_{\delta\delta\delta}
+3F_{\delta\delta W}c
+3F_{\delta WW}c^2
+F_{WWW}c^3
+6(F_{\delta W}+F_{WW}c)d
}{6C}.
\tag{T31.25}
\]

같은 \(\mu_2\)의 두 프로파일은 T31.21에 의해 모든 삼차 이하 편미분과 \(c,d\)를 공유하므로 \(b_3\)도 공통이다. 이 사실은 새 \(k'''\) 수치값이나 삼차 계수 소수값 없이 증명된다.

사차 차이는 두 근 사이의 평균값정리로 짧고 직접적으로 옮길 수 있다. \(W_\nu,W_{\widetilde\nu}\) 사이의 \(\xi_\delta\)에 대해

\[
W_\nu(\delta)-W_{\widetilde\nu}(\delta)
=-\frac{\Delta F(\delta,W_{\widetilde\nu}(\delta))}
{F_{\nu,W}(\delta,\xi_\delta)}.
\tag{T31.26}
\]

T31.17, T31.11, 양의 분모 하한으로 \(C^3\)에서 T31.1을 얻는다. \(C^4\)에서

\[
\Delta F(\delta,W)
=\frac{\Delta\mu_4}{24}\delta^4
\left[p_{\delta,W}k^{(4)}(e_\delta)
+q_{\delta,W}k^{(4)}(x_{\delta,W})\right]+o(\delta^4).
\tag{T31.27}
\]

나머지는 \(J\)에서 균일하다. \(W_{\widetilde\nu}(\delta)\to w\)이므로 대괄호는 \(\mathcal H_4(0,w)\)로, 분모는 \(C\)로 간다. 따라서 T31.2–3을 얻는다. 비영 계수이면 \(\Delta W/\delta^4\)가 비영 상수로 수렴하므로 정확히 사차부터 구별된다.

원하는 비교의 수치 계산에는 각 기존 분지의 \(p,q,C\)와 끝점·내부 중심의 \(k^{(4)}\)만 필요하다. 개별 \(b_3\)나 \(b_{4,\nu}\) 전체를 계산할 필요가 없다. 상단과 하단의 기존 네 노드를 넘어서는 노드나 새 근도 이 차이 공식에는 필요하지 않다. 실제 평가의 허용 횟수와 오차 기준은 새로운 실행 계약·프로토콜이 정한다.

동일 프로파일을 두 분지에 쓸 때 간격 \(\Gamma=W_0-W_*\)의 사차계수 변화는

\[
\Delta b_{4,\Gamma}
=-\frac{\Delta\mu_4}{24}
\left(\frac{\mathcal H_{4,0}}{C_0}
-\frac{\mathcal H_{4,*}}{C_*}\right).
\tag{T31.28}
\]

각 분지의 정확한 기준 수준이 따로 정해졌다는 전제 아래 성립한다. 두 저장 \(A_j\)가 서로 같다는 가정은 필요하지 않고, 각 분지 안에서 비교하는 두 프로파일의 \(A_j\)가 같아야 한다. 간격 계수의 부호는 이 식만으로 보편적으로 정해지지 않는다.

## 7. 같은 비영 A 수준과 분자 경로

같은 \(\mu_2\)이므로 두 프로파일에 공통인 분모와 각 분자는

\[
\mathscr Q=(R-\delta)^2+W-\mu_2\delta^2,\qquad
\mathscr N_\nu=(W-\mu_2\delta^2)f_{\delta,\nu}(e_\delta)
+(R-\delta)^2f_{\delta,\nu}(x_{\delta,W}),
\qquad F_\nu=\frac{\mathscr N_\nu}{\mathscr Q}.
\tag{T31.29}
\]

정확한 수준 \(A\)의 근 방정식은

\[
\mathscr G_\nu=\mathscr N_\nu-A\mathscr Q=0.
\tag{T31.30}
\]

\(D=R^2+w\)로 쓰면 영폭에서

\[
\mathscr G_W=\mathscr N_W-A=DC,\qquad
\Delta\mathscr G=\Delta\mathscr N=\mathscr Q\,\Delta F.
\tag{T31.31}
\]

같은 \(\mu_2\)의 하위 편미분 차이가 0이므로

\[
\Delta\partial_\delta^4\mathscr G(0,w)
=D\,\Delta\mu_4\,\mathcal H_4.
\tag{T31.32}
\]

삼차까지 공통인 근 다항식 \(W_{<4}=w+c\delta+d\delta^2+b_3\delta^3\)에 \(\mathscr G_\nu\)를 대입하고 \(\delta^4\) 계수를 취하자. 미정 \(b_{4,\nu}\)를 더하면 그 계수에 \((\mathscr N_W-A)b_{4,\nu}\)만 추가된다. 두 프로파일을 빼면

\[
\boxed{
\Delta b_4
=-\frac{D\,\Delta\mu_4\,\mathcal H_4}
{24(\mathscr N_W-A)}
=-\frac{\Delta\mu_4\,\mathcal H_4}{24C}.
}
\tag{T31.33}
\]

사차 **차이의 분자**에서는 공통 \(A\mathscr Q\)가 소거되지만, 분모 \(\mathscr N_W-A\)와 공통 하위 근 계수의 A 보정을 버리면 안 된다. \(A=0\)일 때만 정확한 영점용으로 단순화할 수 있다. \(A\ne0\)에서 잘못 \(\mathscr N_W\)로 나누면, 그 분모가 0이 아닌 경우 잘못된 차이는 올바른 차이의 \(DC/(DC+A)\)배가 된다.

유한 저장 숫자를 이 식에 대입하는 것은 저장 기준점의 같은 A 수준에 대한 대수다. 실제 직렬화된 \(A\)·\(C\) 값의 반올림, 원 \(J\) 및 물리 입력 불확실성은 정확한 실수 함수의 T31.30–33과 별개다. 작은 저장 잔차를 0으로 덮어쓰거나 이것으로 정확한 영점 정밀도를 인증하지 않는다.

## 8. 실제 비교용 양의 절대연속 프로파일

주 비교는

\[
h_u(z)=\frac12,\qquad
P_4(z)=\frac{35z^4-30z^2+3}{8},\qquad
h_{P_4}(z)=\frac{1+P_4(z)}2,\quad -1\le z\le1
\tag{T31.34}
\]

이며 구간 밖 밀도는 0이다. \(P_4'(z)=\tfrac52 z(7z^2-3)\)이므로 끝점과 세 내부 정지점을 대입하면

\[
-\frac37\le P_4(z)\le1,\qquad
\frac27\le h_{P_4}(z)\le1.
\tag{T31.35}
\]

따라서 두 프로파일 모두 같은 닫힌 구간 전체에 지지되는 양의 절대연속 확률측도다. \(P_4\)는 짝함수다. 정규화와 이차 모멘트의 차이는 다음 다항식 적분으로 정확히 0이다.

\[
\int_{-1}^1P_4(z)dz
=\frac18\left(35\frac25-30\frac23+3\cdot2\right)=0,
\]

\[
\int_{-1}^1z^2P_4(z)dz
=\frac18\left(35\frac27-30\frac25+3\frac23\right)=0.
\tag{T31.36}
\]

사차 모멘트의 차이는

\[
\frac12\int_{-1}^1z^4P_4(z)dz
=\frac1{16}\left(\frac{70}{9}-\frac{60}{7}+\frac65\right)
=\frac8{315}.
\tag{T31.37}
\]

| 프로파일 | 질량 | 평균 | \(\mu_2\) | \(\mu_4\) |
|---|---:|---:|---:|---:|
| 균일 \(h_u\) | 1 | 0 | \(1/3\) | \(1/5\) |
| \(h_{P_4}\) | 1 | 0 | \(1/3\) | \(71/315\) |
| \(P_4-u\) | 0 | 0 | 0 | \(8/315\) |

따라서 T31.4가 정확히 따른다. 이 기여의 모멘트 값은 해석적인 다항 적분이며 수치 프로그램 실행이나 quadrature 결과가 아니다. \(\delta>0\)에서는 각 프로파일의 밀도와 임의 중심 확률법칙의 혼합으로 광자 밀도가 존재한다. 일반 원자 프로파일을 허용한 주 정리 전체에 이 밀도 성질을 자동 확대하지 않는다.

## 9. C3만으로 더 높은 거듭제곱을 보장할 수 없다는 반례

같은 T31.34의 양의 밀도 쌍을 그대로 사용한다. \(3<p<4\), \(E_0>0\)를 정하고 \(t=(E-a)/E_0\), \(T=(b-a)/E_0\)로 둔다. \(K>0\)의 단위는 s⁻⁴이고

\[
k_{\rm ex}(E)=K\left[D t^2-t^3+\varepsilon t^p-B\right],\qquad
D>3T,\quad
0<\varepsilon<
\frac6{p(p-1)(p-2)T^{p-3}}
\tag{T31.38}
\]

로 정의한다. \(B\)는 원하는 상단 내부 기준점 \(w\)에서 \(F(0,w)=A\)가 되도록 정하는 고정 상수다. 상수 이동은 아래 부호를 바꾸지 않는다.

\[
k_{\rm ex}''=\frac K{E_0^2}
\left[2D-6t+\varepsilon p(p-1)t^{p-2}\right]>0,
\]

\[
k_{\rm ex}'''=\frac K{E_0^3}
\left[-6+\varepsilon p(p-1)(p-2)t^{p-3}\right]<0.
\tag{T31.39}
\]

이 커널은 원 구간에서 \(C^3\)이고 T31.9의 엄격한 부호를 만족한다. \(t=0\)에서 \(t^{p-4}\)가 발산하므로 \(C^4\)는 아니다.

상단 끝점에서 \(E=a+\delta(1+z)\)다. 두 프로파일의 비다항 성분 평균 차이는

\[
K\varepsilon\left(\frac\delta{E_0}\right)^p I_p,\qquad
I_p=\frac12\int_{-1}^1(1+z)^pP_4(z)dz.
\tag{T31.40}
\]

직접 다항 미분으로
\(P_4(z)=\frac1{2^4\,4!}\frac{d^4}{dz^4}(z^2-1)^4\)다.
네 번 부분적분하면 경계항이 모두 0이고

\[
I_p=
\frac{p(p-1)(p-2)(p-3)}{2^5\,4!}
\int_{-1}^1(1+z)^{p-4}(1-z^2)^4dz
=
\frac{2^p p(p-1)(p-2)(p-3)}
{(p+1)(p+2)(p+3)(p+4)(p+5)}
>0.
\tag{T31.41}
\]

두 번째 등식은 \(u=1+z\)를 넣어 \(u^p(2-u)^4\)를 구간 \([0,2]\)에서 적분해 얻는다. \(p>3\)이므로 끝점의 적분과 부분적분 경계 극한이 유한하다. 이는 새 특수함수·수치 적분 호출이 없는 직접 적분이다.

영폭의 내부 중심 \(x_0=m+w/L\)는 \(a\)에서 양의 거리만큼 떨어져 있다. 그 근방에서는 \(t^p\)가 매끄러우므로 내부 중심의 두 프로파일 평균 차이는 \(O(\delta^4)\)다. 이차·삼차 다항 성분은 같은 0–3차 프로파일 모멘트 때문에 정확히 소거된다. 끝점 확률은 \(p_{\rm end}(\delta,W)\to p_0=w/(L^2+w)>0\)이므로

\[
\Delta F(\delta,W_{\widetilde\nu}(\delta))
=\frac{K\varepsilon p_0 I_p}{E_0^p}\delta^p+o(\delta^p).
\tag{T31.42}
\]

T31.26에 의해

\[
\boxed{\Delta W(\delta)
=-\frac{K\varepsilon p_0 I_p}{C E_0^p}\delta^p+o(\delta^p),\qquad 3<p<4.}
\tag{T31.43}
\]

계수는 비영이다. 따라서 C3 전제만으로 \(O(\delta^4)\)를 말할 수 없다. 더 강하게, 임의의 \(\eta>0\)에 대해 \(3<p<\min(4,3+\eta)\)를 택하면 이 반례의 차이는 \(O(\delta^{3+\eta})\)도 아니다. **C3는 공통 삼차와 \(o(\delta^3)\)를 보장하지만, 고정된 양의 추가 거듭제곱은 보장하지 않는다.**

이는 명시한 함수 전제만의 한계를 보이는 해석적 반례다. 동결 물리 커널이 실제로 이 비매끄러운 함수라는 주장이 아니며 물리 코드·커널·source를 바꾸지 않는다.

## 10. 사차 퇴화와 다음 홀수 차수의 가능성

C4 정리에서 실제 사차 분리는 \(\Delta\mu_4\mathcal H_4\ne0\)를 요구한다. 다음 경우를 구별한다.

- \(\Delta\mu_4=0\): 두 프로파일의 사차 이하 응답 미분과 근 계수가 같고 차이는 \(o(\delta^4)\)다. 더 높은 모멘트의 차이를 쓰려면 추가 정칙성이 필요하다.
- \(\mathcal H_4=0\), \(\Delta\mu_4\ne0\): 해당 기준점의 사차 근 차이가 소거된다. 이것은 두 프로파일이 유한폭에서 같다는 뜻이 아니다.
- \(\mu_2=0\) 또는 1: 대칭 확률측도는 각각 \(\delta_0\), \((\delta_{-1}+\delta_1)/2\)로 유일하다. 같은 \(\mu_2\)를 가진 서로 다른 프로파일을 그 경계에서 만들 수 없다.
- \(C=0\) 또는 비내부 기준점: 이 단순근 전달 정리를 적용하지 않는다.

움직이는 중심 때문에 \(\mathcal H_4(0,w)=0\) 뒤의 첫 차수가 반드시 6일 수는 없다. 이를 직접적인 매끄러운 예로 확인한다. \(X=E-m\)라 하고

\[
k_{\rm deg}(E)=K_2X^2-K_3X^3
+\gamma(X^6-15wX^4)-B,\qquad K_2,K_3>0
\tag{T31.44}
\]

로 둔다. \(K_2>3K_3\max(L,H)\)를 먼저 택하고 충분히 작은 비영 \(\gamma\)를 쓰면, 콤팩트 구간에서 \(k''>0,k'''<0\)를 유지한다. 계수들은 각 항이 s⁻⁴가 되는 단위를 갖는다. \(B\)로 \(F(0,w)=A\)를 맞춘다.

이 커널의 사차 도함수 가중합은 중심 평균·분산만으로

\[
\mathcal H_4(\delta,W)=360\gamma(V-w),
\quad\text{따라서}\quad \mathcal H_4(0,w)=0.
\tag{T31.45}
\]

같은 \(\mu_2\), 대칭성, 같은 중심 법칙을 사용해 육차와 사차 모멘트를 전개하면 정확히

\[
\Delta F(\delta,W)
=15\gamma\Delta\mu_4(V-w)\delta^4
+\gamma\Delta\mu_6\delta^6.
\tag{T31.46}
\]

공통 근에서 \(V-w=c\delta+O(\delta^2)\)이고, \(\gamma=0\)인 cubic baseline의
\(F_\delta=-K_3s\,w(1+w/R^2)\ne0\)이므로 작은 \(\gamma\)에서도 \(c\ne0\)다.
따라서 \(\Delta\mu_4\ne0\)인 두 프로파일은

\[
\Delta W(\delta)
=-\frac{15\gamma\Delta\mu_4 c}{C}\delta^5+o(\delta^5)
\tag{T31.47}
\]

로 구별될 수 있다. 이 예에서는 커널이 다항식이라 필요한 정칙성이 모두 성립한다. 주 물리 모델의 오차·오차상계·오차차수 수치 결과로 해석하지 않는다. T31.47은 사차 소거 뒤의 짝수 차수 단정을 막는 직접 기호 반례이며 새 고차 물리 계산을 뜻하지 않는다.

한편 커널이 차수 3 이하의 다항식이면 모든 양의 폭에서도 동일 \(\mu_2\)·대칭 두 프로파일의 평균 응답이 정확히 같다. T31.15의 유한 다항식 항이 전부 소거되기 때문이다. 이 경우에는 그 응답으로 정의된 같은 유일 근도 같다. 이는 특별한 다항식 퇴화이지 일반 물리 커널의 유한폭 동일성이 아니다.

## 11. 단위, 계산으로 넘기는 형태와 근거 상태

| 양 | 단위 |
|---|---|
| \(z,\mu_2,\mu_4,\Delta\mu_4,p,q\) | 무차원 |
| \(E,a,b,m,L,H,R,\delta,c\) | eV |
| \(V,W,w,D\) | eV² |
| \(d\) | 무차원 |
| \(b_3\) | eV⁻¹ |
| \(b_4,\Delta b_4\) | eV⁻² |
| \(k,F,A\) | s⁻⁴ |
| \(C=F_W\) | s⁻⁴ eV⁻² |
| \(k^{(4)},\mathcal H_4\) | s⁻⁴ eV⁻⁴ |
| \(\mathscr Q,\mathscr N,\mathscr N_W-A\) | 각각 eV², s⁻⁴ eV², s⁻⁴ |

\(\mathcal H_4/C\)는 eV⁻²이고 \(\delta^4\)를 곱하면 근 차이의 eV²가 된다. 사차 미분의 차이에는 \(24\)로 나누지 않고, ordinary 사차 계수 \(b_4=W^{(4)}/24\)로 옮길 때만 \(24\)를 넣는다. \(C>0\)일 때 프로파일 변화의 사차 부호는 \(-\Delta\mu_4\mathcal H_4\)의 부호다. 상속한 \(k''>0,k'''<0\)만으로 \(k^{(4)}\)나 \(\mathcal H_4\)의 부호는 정해지지 않는다.

실제 물리 차이 계산에 넘기는 형태는 다음과 같다.

\[
D_j=R_j^2+w_j,\quad
p_j=w_j/D_j,\quad q_j=R_j^2/D_j,\quad
\mathcal H_{4,j}=p_jk^{(4)}(e_j)+q_jk^{(4)}(x_j),
\]

\[
\Delta b_{4,j}^{P_4-u}
=-\frac{\mathcal H_{4,j}}{945C_j}.
\tag{T31.48}
\]

기존 캐시에 \(k,k',k''\)만 있다는 사실을 \(k^{(4)}\) 값이 이미 있다는 뜻으로 바꾸지 않는다. 이론상 필요한 새 값은 네 기존 노드의 사차 도함수이며, 물리 커널의 추가 정칙성과 두 표현·정밀도·허용오차의 실제 확인은 별도 기여와 동결 프로토콜을 따른다. 이 기여의 수치·symbolic 코드 실행은 0이다.

| 주장 | 근거 상태 | 근거·한계 |
|---|---|---|
| 같은 \(\mu_2\)의 정확한 공통 기하 | derived, PHYS30 전제 재사용 | T31.7–11; 중심 구간 고정 |
| C3의 공통 삼차와 \(o(\delta^3)\) | conditional derived | T31.14–17, 21, 23–26 |
| C4의 사차 응답·근 차이 | conditional derived | T31.18, 20, 22, 26–27 |
| 같은 비영 A 분자식 | derived | T31.29–33; A와 denominator 보존 |
| 양의 AC 쌍의 같은 \(\mu_2\), 다른 \(\mu_4\) | derived | T31.34–37; 정확 다항 적분 |
| C3 가정의 sharpness | derived counterexample | T31.38–43; 실제 물리 커널 교체 없음 |
| 사차 퇴화 뒤 오차 가능성 | derived counterexample | T31.44–47; 별도 매끄러운 시험함수 |
| 물리 \(k^{(4)}\)와 계수의 소수값 | 이 기여에서 NOT_RUN | 별도 실제 정칙성·수치 근거 필요 |
| 새 정확근·J 오차·수치 유효폭·global ordering | 미주장 | 기존 한계 유지 |
| 최종 독립 판정 | 이 역할의 범위 밖 | 생성·설계와 분리된 reviewer 필요 |

이 문서의 검토는 THEORY_CONTRIBUTOR_SELF_CHECK다. PHYS30 과학 main·suite·import를 반복하지 않았다. 새 과학 main, 물리 커널·도함수·근·노드, 수치 toy, quadrature, finite difference, 폭 스윕, portable replay 및 코드 과학 산술 실행은 모두 0이다. 파일·해시·ZIP member 대조는 읽기와 메타데이터 작업으로 분류한다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes0**을 유지한다. 원자·기체·방출원·유한 역사 admission, local Codex 또는 heavy native 작업을 열지 않는다. 외부 원전·우선권·신규성 조사는 이 기여에서 수행하지 않았으며, 위 새 결과는 직접 증명과 실제 읽은 선행 전제에 근거한다.

