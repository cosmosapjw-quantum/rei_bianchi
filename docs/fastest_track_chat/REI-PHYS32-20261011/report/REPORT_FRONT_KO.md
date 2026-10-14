# PHYS32 — 사차 프로파일 차이의 유한 폭 나머지와 근 안정성

연구 단위: REI-PHYS32-20261011  
이어받은 과제: QUARTIC_SPLITTING_REMAINDER_AND_CONDITIONING  
과학 작업 상태: 조건부 정리 도출 및 고정 exact-rational 검증 완료  
최종 채택 권위: [별도 실제 검토서](../independent/DECISION_REVIEW_KO.md)와 [판정 JSON](../independent/DECISION_REVIEW.json)  
물리 admission: **HOLD 유지**

## 1. 이번 루프에서 실제로 달라진 것

PHYS31은 같은 이차 모멘트의 대칭 프로파일이 사차에서 처음 구별될 수 있음을 보였고,
\(\Delta W=D_4\delta^4+o(\delta^4)\)의 계수를 얻었다.
PHYS32는 그 나머지를 근의 이동과 조건수까지 포함하는 명시적 상계로 바꾸었다.
또한 실제 사용한 두 프로파일의 차이에 양의 적분 표현이 있음을 확인했다.
이 구조는 추가 구간 부호 증거가 있을 때 사차 근사 오차를 거치지 않고도
같은 수준의 유한 폭 근 순서를 직접 결정하게 해 준다.

| 결과 | 근거 상태 | 채택 범위 |
|---|---|---|
| 일반 C4 사차 근 나머지와 근 존재·이탈 조건 | derived | 고정 동일 \(\mu_2\), 실제 W, 동일한 정확 A, 내부 튜브, 양의 기울기 |
| C5에서 명시적인 \(K_R\delta^5\) 상계 | derived | 도함수 상계와 전체 폭 구간 조건이 주어진 경우 |
| 선택한 쌍의 정확한 양의 Peano 적분 표현 | derived; exact-rational identity checked | \(h_p\)와 균일 \(h_u\), C4 커널, 실제 지원 안 |
| 비영 A·움직이는 기하의 유한 폭 toy 근 8개 | numerically checked; implementation-verified | 두 사전 고정 폭, 두 분지, 두 프로파일, 무차원 다항식 |
| 근·노드·J·평가오차에서 계수·부호·gap으로의 전파식 | derived | 필요한 입력 오차가 실제로 제공되는 경우 |
| 실제 물리 커널의 인증 폭·부호·원 J 정확도 | unresolved | 새 물리 평가 및 해당 enclosure 없음 |

단위와 source·모델·실행 장소를 바꾸지 않았다.
연구·코딩 하네스는 현재 trusted developer designation의 GPT-6 Astra 계열에 맞는
v4.0.0을 실제 읽어 적용했다. 모델 전환·경험적 모델 신원 검증·성능 비교를 수행한 것은 아니다.

## 2. 비교 대상과 공통 기하

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=4.39,\quad H=6.58\quad(\mathrm{eV})
\]

를 유지한다. 프로파일은 \([-1,1]\) 위의 고정 대칭 확률측도이며
\(\delta,W,\) 중심과 분지에서 독립이다. 일반 정리는 원자도 허용한다.
물리 폭은 \(\delta\ge0\), 중심 구간은 \([a+\delta,b-\delta]\)다.
같은 이차 모멘트 \(\mu_2\)에서 중심 분산과 실제 분산은

\[
V=W-\mu_2\delta^2,\qquad
\mu_2\delta^2\le W\le(L-\delta)(H-\delta)+\mu_2\delta^2.
\]

한 분지에서 \(s=\pm1,\ R=L\) 또는 \(H,\ e=m-sR\)라 하면

\[
r=R-\delta,\quad e_\delta=e+s\delta,\quad
x_{\delta,W}=m+sV/r,\quad p=\frac{V}{r^2+V},\quad q=1-p,
\]
\[
F_\alpha(\delta,W)
=p\int k(e_\delta+\delta z)d\alpha(z)
+q\int k(x_{\delta,W}+\delta z)d\alpha(z).
\]

두 프로파일의 기하와 확률이 정확히 같다. 모든 W 미분은 실제 W에 대한 미분이다.
각 분지에서 \(F_\alpha(0,w)=A\)인 정확한 내부 기준근을 가정한다.
두 분지의 수준은 서로 달라도 되지만, 한 분지 안에서 두 프로파일이 쓰는 A는 정확히 같아야 한다.
기존 비영 A를 0이나 새로 정의한 수준으로 바꾸지 않는다.

## 3. 근의 존재를 먼저 보장하는 정량 조건

고정 튜브 \(W\in[w-\eta,w+\eta]\), 폭 \(0\le\delta\le d\)에 대해

\[
d<\min(L,H),\qquad
\mu_2d^2<w-\eta,\qquad
w+\eta<(L-d)(H-d)
\tag{R32.1}
\]

이면 전체 튜브가 실현가능 내부에 놓인다.
원 구간에서 \(k''\ge m_2>0\)를 두고 \(\kappa=m_2/2\)라 하면

\[
F_{\alpha,W}=
\int_0^1t\int k''((1-t)e_\delta+t x_{\delta,W}+\delta z)
d\alpha(z)\,dt\ge\kappa.
\tag{R32.2}
\]

이 식은 상단·하단 모두에서 성립하며, 이미 존재하는 근을 가정하지 않고 먼저 얻는 하한이다.
영폭 기준 확률·중심을 \(p_0,q_0,x_0\), W=w에서 폭만 이동시킨 값을
\(p_\delta,q_\delta,x_\delta\)라 쓰고 \(M_i\ge\sup|k^{(i)}|\)라 하자.

\[
B(\delta)=|p_\delta-p_0|\,|k(e)-k(x_0)|
+M_1\!\left[p_\delta\delta+q_\delta|x_\delta-x_0|\right]
+\frac{\mu_2M_2}{2}\delta^2
\tag{R32.3}
\]

는 두 프로파일 모두에서 \(|F_\alpha(\delta,w)-A|\)를 감싼다.
앞의 두 항은 움직이는 기하, 마지막 항은 대칭 프로파일 평균의 이차 오차다.
따라서

\[
B(\delta)<\kappa\eta
\quad\Longrightarrow\quad
\text{두 유일근 존재},\qquad |W_\alpha(\delta)-w|\le\rho(\delta)=B(\delta)/\kappa.
\tag{R32.4}
\]

증명은 튜브 양 끝의 반대 잔차 부호와 단조성이다.
근이 존재한다고 먼저 가정한 뒤 그 가정으로 근을 제어하는 순환을 피했다.

## 4. 일반 C4 사차 나머지

\(\omega_n\)을 원 구간에서 \(k^{(n)}\)의 연속성 모듈러스라 하자.
다음은 실제 두 근과 그 사이에서 성립하는 명시적 상계다.

\[
h=\max\left\{\delta,\frac{\rho+w\delta/R+\mu_2\delta^2}{R-\delta}\right\},
\]
\[
P=\min\left\{1,
\frac{R^2(\rho+\mu_2\delta^2)+w\delta(2R-\delta)}
{((R-\delta)^2+w-\rho-\mu_2\delta^2)(R^2+w)}
\right\},
\]
\[
B_H=P|k^{(4)}(e)-k^{(4)}(x_0)|+\omega_4(h),\qquad
S_C=\frac12\omega_2(h+\delta),
\]
\[
r_4=\frac{\mu_{4,\nu}+\mu_{4,\sigma}}{24}\omega_4(\delta).
\tag{R32.5}
\]

여기서 h는 중심 이동, P는 끝점 확률의 변화, \(B_H\)는 사차 가중합의 이동,
\(S_C\)는 분산 기울기의 이동을 제어한다.
기울기 식에는 이미 확률과 내부 중심의 W 미분이 정확히 합쳐져 있다.

\[
\mathcal H_4=p_0k^{(4)}(e)+q_0k^{(4)}(x_0),\quad
C=F_W(0,w)>0,\quad
D_4=-\frac{\Delta\mu_4\mathcal H_4}{24C}.
\]

두 근 사이의 정확 평균 기울기를 \(\overline C\)라 하면
\(\overline C\ge\kappa\), \(|\overline C-C|\le S_C\)다.
같은 A 때문에 \(\overline C\Delta W+\Delta F(\delta,W_\sigma)=0\).
응답 차이에서 사차항을 더하고 빼고 이 quotient의 오차를 정리하면

\[
\boxed{
|\Delta W-D_4\delta^4|\le\delta^4\mathcal R(\delta),\qquad
\mathcal R=
\frac{|\Delta\mu_4|B_H/24+r_4+|D_4|S_C}{\kappa}.
}
\tag{R32.6}
\]

마지막 \(|D_4|S_C/\kappa\)가 근 기울기 이동의 비용이다.
응답 차이가 정확한 사차여도 이 항은 일반적으로 남는다.
분모를 \(\max\{\kappa,C-S_C\}\)로 개선할 수도 있지만,
\(\rho,h,P,S_C\)를 얻을 때 사용한 기존 \(\kappa\)는 유지한다.

C4에서는 \(\mathcal R(\delta)\to0\).
C5와 \(M_3\ge\sup|k'''|,M_5\ge\sup|k^{(5)}|\)가 있으면
\(\omega_2(t)\le M_3t,\ \omega_4(t)\le M_5t\)이고,
명시한 전체 구간 조건에서 \(K_R\delta^5\) 형태로 바꿀 수 있다.
그 \(K_B,K_h,K_P,K_R\)의 닫힌 식과 증명은 이 파일의 부록 A §8에 전부 수록했다.
대칭성만으로 근 나머지를 육차로 만들지는 않는다.

## 5. 선택한 쌍에는 정확한 양의 적분 표현이 있다

이번에 계속 쓰는 프로파일은

\[
h_u=\frac12,\qquad
h_p=\frac{35z^4-30z^2+11}{16}.
\]

차이는 \(P_4/2\)다. \(Q(z)=(1-z^2)^4\)로 놓으면
\(h_p-h_u=Q^{(4)}/768\).
\(Q,Q',Q'',Q'''\)가 양 끝에서 0이므로 네 번 부분적분해

\[
\boxed{
f_p(\delta,y)-f_u(\delta,y)
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)d\pi(z),\qquad
d\pi=\frac{315}{256}(1-z^2)^4dz
}
\tag{R32.7}
\]

를 얻는다. \(\pi\)는 양의 확률측도이고, 이 식에는 Taylor 절단 오차가 없다.
표준 Legendre 다항식 정규화는 [NIST DLMF 18.5](https://dlmf.nist.gov/18.5)를 실제 확인했다.
새 근·나머지 정리와 동일 수준 조건은 직접 유도했으며 그 문헌에 귀속하지 않는다.

공통 기하에서
\(\Delta F=\delta^4\mathcal S/945\),
\(\mathcal S\)는 두 packet의 \(k^{(4)}\) 양의 가중평균이다.
따라서 같은 A의 두 근에서

\[
\Delta W=-\frac{\delta^4\mathcal S(\delta,W_u)}{945\overline C}.
\tag{R32.8}
\]

R32.5의 기하 상계로

\[
E_4=P|k^{(4)}(e)-k^{(4)}(x_0)|+\omega_4(h+\delta)
\]

라 두면 이 특수 쌍에 더 직접적인 나머지는

\[
\boxed{\mathcal R_p=
\frac{E_4+|\mathcal H_4|S_C/C}{945\kappa}.}
\tag{R32.9}
\]

또한 실제 두 photon packet 전체에서 \(0<m_4\le k^{(4)}\le M_4\),
기울기에 필요한 선분 전체에서 \(0<m_2\le k''\le M_2\)가 보장되면

\[
-\frac{2M_4}{945m_2}\delta^4
\le W_p-W_u
\le-\frac{2m_4}{945M_2}\delta^4<0.
\tag{R32.10}
\]

이는 조건부 유한 폭 순서다. 사차 도함수의 부호에는 해당 두 packet의 합집합만으로
충분할 수 있지만, \(k''\) 기울기 하한에는 두 중심 사이 선분과 profile shift도 필요하다.
정의역을 혼동하지 않는다. 실제 소스의 네 점이 양수라는 사실을 이 구간 전제로 대체하지 않았다.
두 분지 각각의 음의 이동은 두 분지 간격 차이의 부호를 결정하지 않는다.

## 6. 저장 입력의 오차와 같은 비영 A

저장 w가 정확한 목표 A의 근이라는 등식은 별도 enclosure를 필요로 한다.
인증된 잔차 \(\varepsilon_r\)와 feasible box의 양의 기울기로

\[
|w-\widehat w|\le\varepsilon_w=\varepsilon_r/\kappa,\qquad
|x(w)-\widehat x|\le\varepsilon_w/R+\eta_x,
\tag{R32.11}
\]

여기서 \(\eta_x=|\widehat x-(m+s\widehat w/R)|\)다.
이런 근·노드·가중치 오차를 도함수의 modulus와 합쳐
\(|H-\widehat H|\le\varepsilon_H,\ |C-\widehat C|\le\varepsilon_C\)를 확보해야 한다.
\(\alpha=\Delta\mu_4/24\)라 하면

\[
|D_4-\widehat D_4|
\le\varepsilon_D=
|\alpha|\left[
\frac{\varepsilon_H}{\kappa}
+\frac{|\widehat H|\varepsilon_C}{\kappa|\widehat C|}
\right]+\varepsilon_{D,\mathrm{asm}}.
\tag{R32.12}
\]

모든 값과 도함수 bound에 불확실성을 일관되게 포함한 뒤에만

\[
|\widehat D_4|>\varepsilon_D+\mathcal R(\delta)
\tag{R32.13}
\]

를 엄격한 부호의 충분조건으로 사용할 수 있다.
Gap에는 두 분지의 계수 오차와 나머지를 더한다.
공통 입력을 사용했다는 이유만으로 오차 상쇄를 가정하지 않는다.

분자식 \(G=N-AQ\)에는 중요한 구분이 있다.

\[
G_W=N_W-A=QF_W+(F-A).
\tag{R32.14}
\]

따라서 \(G_W=QF_W\)는 해당 A의 정확한 근에서만 성립한다.
두 근 사이의 임의 평균점 또는 저장 근사점에는 잔차가 남는다.
새 정리는 정규화된 F의 평균 기울기를 사용해 이 잔차를 조용히 버리지 않았다.
기존 작은 비영 A의 값을 0으로 바꾸지 않는다.

고정 source-real 커널의 도함수는
\[
k^{(r)}=K\{E^2\phi^{(r+2)}+(2r+4)E\phi^{(r+1)}
+r(r+3)\phi^{(r)}\}
\tag{R32.15}
\]
이므로 \(k^{(4)}\) 제어에는 \(\phi\)의 6차까지,
\(k^{(5)}\) 제어에는 7차까지의 정보가 필요하다.
함수값의 원자 fit 오차를 고차 도함수 오차로 그대로 사용할 수 없다.
고정 다른 입력 아래 J 의존성은 선형이지만, 원 J 오차와 계수 함수의 구간 norm은
이번 루프에서 수치 평가하지 않았다. 전체 조건부 전파식은 부록 C에 있다.

## 7. 실제 수행한 exact-rational 유한 폭 검증

검증은 무차원 다항식
\[
k(X)=1+X^2-X^3/10+X^4/100,\quad X\in[-2,2],\quad R=2,\ m=0,\ w=1
\]
에 대해 수행했다. 사전에 고정한 폭은 1/100, 1/50이며,
두 분지의 수준은 \(A_s=(813+60s)/400\)로 비영이다.
두 프로파일마다 이 수준의 유일근을 정확 유리수로 감쌌다.

직접 평균 경로와 중심·전체 모멘트 경로를 별도로 조립해 새 근 구간의 양 끝에서
같은 잔차를 주는지 확인했다. 각 근은 80회의 정확 이분법으로
폭 \(2^{-81}\)의 구간에 들었다. 두 근 구간을 바깥 방향으로 빼서
\(\Delta W/\delta^4\)의 전체 구간을 만들고 상계와 비교했다.

아래 값은 원자료의 정확 유리수를 읽기 쉽게 반올림한 표시다.
모든 양은 **무차원 toy 값**이며 물리 eV 폭이나 실제 커널의 문턱이 아니다.

| 분지 | \(\delta\) | \(D_4\) | 실제 \(\Delta W/\delta^4\), 표시값 | 나머지 상계 \(\mathcal R\) |
|---|---:|---:|---:|---:|
| 상단 | 0.01 | −0.000225249005737 | −0.000225643802004 | \(6.82229962\times10^{-6}\) |
| 상단 | 0.02 | −0.000225249005737 | −0.000226038530155 | \(1.37384776\times10^{-5}\) |
| 하단 | 0.01 | −0.000273820219912 | −0.000273499667768 | \(7.82074191\times10^{-6}\) |
| 하단 | 0.02 | −0.000273820219912 | −0.000273178882625 | \(1.57487654\times10^{-5}\) |

네 경우 모두 전체 근 차이 구간이 사차 나머지와 MVT 범위 안에 들고,
\(\mathcal R<|D_4|\)를 만족했다. 실제 근 차이는 엄격히 음수이며,
유한 폭에서 \(\Delta W=D_4\delta^4\)와 정확히 같지는 않다.
이 toy는 \(k^{(4)}=6/25\)가 상수라 응답 차이는 정확한 사차다.
근 차이의 나머지는 움직이는 분모에서 나온다.

Gap의 사차계수는 −0.0000485712141751이다.
두 폭에서 나머지 합은 각각 0.0000146430415295, 0.0000294872429604로
그 절댓값보다 작았다. 실제 scaled gap 변화는 약 −0.0000478558657642,
−0.0000471403524705이며 둘 다 음수다.
이 부호를 PHYS31 실제 물리 cache의 양의 gap 계수에 옮기지 않는다.
커널과 기준 수준이 다른 진단이다.

![PHYS32 유한 폭 toy의 사차 나머지 상계](PHYS32_FINITE_WIDTH_BOUNDS.png)

표시 그림은 이미 끝난 정확 유리수 결과만 읽었다.
사차 기준값 주위의 상계 구간과 실제 근 차이 구간을 비교한다.
근의 인증 구간은 마커보다 작다. 그림에는 새 커널·근 평가가 없다.

| 실제 실행 항목 | 첫 main | 한 번의 복원 replay | 합계·해석 |
|---|---:|---:|---|
| 실행 exit | 0 | 0 | stderr 각각 0 bytes |
| 검사 묶음 | 21/21 | 21/21 | 같은 19 수학 묶음+2 계약·회계 묶음 |
| 새 toy 근 구간 | 8 | 8 | 같은 8개 사례의 재현 |
| 정확 이분법 단계 | 640 | 640 | 합계 1,280 |
| moment 응답 호출 | 680 | 680 | 합계 1,360 |
| 직접 평균 응답 호출 | 24 | 24 | 합계 48 |
| 새 물리 kernel/derivative/root 평가 | 0 | 0 | 0 |
| 과거 과학 import/main/suite | 0 | 0 | 0 |
| 수치 quadrature·finite difference | 0 | 0 | 0 |
| main wall time | 0.064959 s | 0.068680 s | 실제 process receipt 기준 |

첫 원자료와 replay 원자료는 **31,328 bytes 전체와 parsed JSON이 같다**.
SHA256: 852a895d3fa52519717cbaaaee602ced253fb49c4e140ef6b1885dc9edc2d417.
최소 runtime의 5개 payload와 manifest를 다른 경로에 복원했고,
payload의 bytes·SHA·mode를 replay 전후 확인했다.
같은 호스트·Python 3.12.14·입력 계보의 재현이며 독립 물리 데이터 credit은 0이다.
첫 main 1회와 replay 1회의 과학 예산을 모두 사용했다.

## 8. 실제 소스와 남겨 둔 물리 한계

최신 intake에서 [PR 83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83)의 head는
13436210ea925be268b4dc9034baf4a37b6dc091,
tree는 242aae1871e1bf2ad19e37ea653d21b06f22559f였다.
전체 tree는 6,363 entries, truncated=false였다.
고정한 소스 7개의 Git blob·크기·mode와 복원된 bytes가 모두 맞았고,
과학 src subtree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이다.
이 식별자들은 내용 동일성 근거이며 물리 정확도의 증명은 아니다.

H I fit 출처는 [Verner et al.의 arXiv 서지·초록](https://arxiv.org/abs/astro-ph/9601009)과
[저자 자료 페이지](https://www.pa.uky.edu/~verner/photo.html)를 직접 확인했다.
전체 논문·표·Fortran 또는 정확도 검증을 수행했다고 주장하지 않는다.
실제 소스의 분석 구간은 cutoff를 가로지르지 않는 하나의 양의 해석적 분기에 놓인다.
Source binary64 리터럴을 정확 실수 상수로 읽고 직렬화 J를 고정한 모델의 정칙성과,
native 반환값의 반올림·원자 fit 및 원 J의 불확실성은 구별한다.

기존 물리 계수는 PHYS31의 저장 입력 결과로 유지한다.

| 물리 cache | 상단 | 하단 |
|---|---:|---:|
| 기존 비영 A, s⁻⁴ | \(-2.2748589\times10^{-137}\) | \(-3.2582515\times10^{-137}\) |
| 기존 \(D_4^{p-u}\), eV⁻² | −0.00110495859229183348 | −0.000619616589313442784 |

이번에는 이 값들을 다시 평가하지 않았다.
원 J, 기준근·저장 노드의 오차, 점별 도함수 평가오차,
구간 \(m_2,M_3,M_5,\omega_2,\omega_4\)의 숫자를 0으로 두지 않았다.
따라서 실제 물리 커널에서 어느 eV 폭까지 사차 근사가 부호를 보증하는지는 여전히 미평가다.
두 표현의 일치·재현·해석성은 그 누락된 enclosure를 대신하지 않는다.

## 9. 검토·수정·종료와 다음 질문

후보 생성자는 owner와 두 기여자이고, 최종 decision reviewer는 생성·검증 설계에 참여하지 않은
별도 실제 역할이다. 같은 host·model·input lineage의 NONBLIND 검토이며
독립 물리 실험으로 세지 않는다. 최종 판정의 실제 상태·범위는 앞의 판정서 링크를 따른다.

통합 중 선두 표시식 T32.1의 더하기 기호 한 글자 누락을 발견했다.
올바른 합은 상세 유도와 기계 판독 주장에 이미 있었고,
수정 전 전체 본문을 보존한 뒤 표시식만 수정했다.
이는 EDITORIAL_EQUATION_OMISSION으로 기록했다.
조건 분석 문서의 상대 링크 한 곳도 실제 파일명으로 바로잡았다.
과학 main 실패·재시도·허용치 변경은 없었다.
읽기 출력의 truncation은 해당 범위를 다시 표시해 보완했으며 과학 실행으로 세지 않는다.

다음 PHYS33의 제안은 **고정 source-real 모델에서 최소 국소 부호 인증의 가능성**이다.
먼저 정확하게 같은 수준, feasible root tube, 기울기와 두 photon packet의 \(k^{(4)}\) 부호에
필요한 증거를 정한다. Branch 순서만 목표라면 R32.7–10을 사용해
사차 근 나머지의 수치값 없이도 접근할 수 있다.
Gap 부호는 별도의 정량 오차 조건이 필요하므로 같은 성과로 묶지 않는다.
PHYS33은 PROPOSED_NOT_RUN이며 새로운 계산은 새 계약 전에는 실행하지 않는다.

**Physical HOLD; [160,161] FAIL; tick 160; auxiliary escape FAIL;
HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime changes 0.**

완료한 직접 증명 세 본문을 아래 부록에 수록한다.
단독 보고서에서도 정의·가정·유도·조건부 오차식을 확인할 수 있다.
코드·정확 원자료·실행 기록·전체 개별 주장·보존 입력은 함께 제공하는 연구 묶음에 있다.
