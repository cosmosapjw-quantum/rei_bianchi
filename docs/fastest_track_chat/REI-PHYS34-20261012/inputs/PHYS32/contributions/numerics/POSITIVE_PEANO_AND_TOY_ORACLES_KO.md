# PHYS32 — 양의 Peano 표현과 유한 폭 검증의 정확 기준

근거 상태: 직접 유도 후보. 작성자 /root, 최종 판정자는 별도 역할이다.
이 문서는 새 프로그램 실행 전에 고정하는 해석적 기준이다.
PHYSICS_CONTRACT.json의 실제 W, 물리 오른쪽 폭, 같은 분지 안의 동일한 정확 수준 A를 따른다.

## P32.1. 특수 프로파일 쌍의 정확 항등식

PHYS31의 두 확률밀도를 그대로 쓴다.

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16},\qquad -1\le z\le1.
\]

두 밀도는 대칭이고 정규화되며, 공통 이차 모멘트는 1/3이다.
차이는 \(P_4(z)/2\)이다. 표준 \(P_4\) 정규화는
[NIST DLMF 18.5.16](https://dlmf.nist.gov/18.5#E16)에서 실제 확인했다.
아래 나머지·근 전달 정리는 해당 문헌의 결과를 인용한 것이 아니라 직접 유도한 것이다.

\[
Q(z)=(1-z^2)^4,\qquad Q^{(4)}(z)=48(35z^4-30z^2+3),
\]
\[
h_p-h_u=\frac{Q^{(4)}}{768}.
\tag{P32.1}
\]

\(Q,Q',Q'',Q'''\)는 양 끝점에서 모두 0이다.
\(k\in C^4([a,b])\), \(y\in[a+\delta,b-\delta]\), \(\delta\ge0\)이면
네 번 부분적분의 모든 경계항이 사라진다. 네 번의 부호 반전은 양수이며,
합성함수의 네 번째 z 미분은 \(\delta^4 k^{(4)}(y+\delta z)\)다.
따라서 근사 나머지가 없는 정확 항등식은

\[
\boxed{
f_p(\delta,y)-f_u(\delta,y)
=\frac{\delta^4}{768}\int_{-1}^{1}(1-z^2)^4
k^{(4)}(y+\delta z)\,dz
=\frac{\delta^4}{945}\int_{-1}^{1}k^{(4)}(y+\delta z)\,d\pi(z).
}
\tag{P32.2}
\]

여기서

\[
d\pi(z)=\frac{315}{256}(1-z^2)^4\,dz,\qquad
\int_{-1}^1(1-z^2)^4\,dz=\frac{256}{315}.
\tag{P32.3}
\]

\(\pi\)는 양의 대칭 확률측도다. \(1/945=(8/315)/24\)는 PHYS31의
ordinary 사차계수 정규화와 일치한다. \(k\)가 사차보다 높은 함수여도 P32.2는
정확하며, Taylor 급수 수렴을 가정하지 않는다.

## P32.2. 움직이는 공통 기하와 정확 근 차이

각 분지에서 \(s=\pm1,\ R=L\) 또는 \(H,\ e=m-sR\)라 하자.

\[
r=R-\delta,\quad V=W-\delta^2/3,\quad
e_\delta=e+s\delta,\quad x=m+sV/r,\quad
p=\frac{V}{r^2+V},\quad q=1-p.
\]

두 프로파일의 기하가 정확히 같으므로

\[
\Delta F(\delta,W)=\frac{\delta^4}{945}\mathcal S(\delta,W),
\]
\[
\mathcal S(\delta,W)
=p\int k^{(4)}(e_\delta+\delta z)d\pi(z)
+q\int k^{(4)}(x+\delta z)d\pi(z).
\tag{P32.4}
\]

같은 A의 두 근 \(W_p,W_u\)가 같은 실현가능 내부 구간에 있고
\(F_{p,W}>0\)이면, 정확 평균 기울기

\[
\overline C=\int_0^1 F_{p,W}\bigl(\delta,W_u+t(W_p-W_u)\bigr)\,dt
\]

에 대해

\[
\boxed{W_p-W_u=-\frac{\delta^4}{945}
\frac{\mathcal S(\delta,W_u)}{\overline C}.}
\tag{P32.5}
\]

동일한 \(\mathcal Q=r^2+V\), \(\mathcal G=N-A\mathcal Q\)로 계산해도
기준점에서 \(\mathcal G_W=N_W-A=\mathcal Q C\)다.
두 응답의 차이에서 A가 소거된다는 사실은 근 기울기의 A를 버릴 이유가 아니다.

## P32.3. 사차계수에 대한 정량 나머지

일반 정리의 기호를 사용한다. 정확한 기준점 \(F(0,w)=A\)에서
\(p_0=w/(R^2+w),q_0=1-p_0,x_0=m+sw/R\)이고

\[
\mathcal H_4=p_0k^{(4)}(e)+q_0k^{(4)}(x_0),\quad
C=F_W(0,w)>0,\quad D_4=-\frac{\mathcal H_4}{945C}.
\]

근 존재를 먼저 보장한 뒤 두 근과 그 사이에서 다음을 확보했다고 하자.

\[
|W-w|\le\rho,\quad |p-p_0|\le P,\quad
|e_\delta-e|\le h,\quad |x-x_0|\le h,
\quad \overline C\ge\kappa>0,\quad
|\overline C-C|\le S_C.
\]

\(\omega_4\)는 원 구간에서 \(k^{(4)}\)의 비감소 연속성 모듈러스다.
영폭 가중합을 더하고 빼고, \(\pi\)가 확률측도라는 사실을 쓰면

\[
|\mathcal S-\mathcal H_4|
\le P\,|k^{(4)}(e)-k^{(4)}(x_0)|+\omega_4(h+\delta)
=E_4.
\tag{P32.6}
\]

가중치의 변화에는 두 기준값의 차이가 곱해진다.
합성점 이동에는 중심 이동 h와 프로파일 폭 \(\delta\)가 모두 들어간다.
정확 quotient 차이에서

\[
\boxed{
|W_p-W_u-D_4\delta^4|
\le\delta^4\mathcal R_p(\delta),\qquad
\mathcal R_p=
\frac{E_4+|\mathcal H_4|S_C/C}{945\kappa}.
}
\tag{P32.7}
\]

\(\mathcal R_p\)의 단위는 eV⁻²다. \(\omega_4(h+\delta)\)는
s⁻⁴ eV⁻⁴, \(S_C,C,\kappa\)는 s⁻⁴ eV⁻²다.
\(\mathcal R_p<|D_4|\)이면 양의 폭에서 \(W_p-W_u\)의 부호는 \(D_4\)와 같다.
이 부등식은 충분조건이고 필요조건은 아니다. \(D_4=0\)인 경우에는
이 비교로 부호를 정하지 않는다.

\(k\in C^5,\ |k^{(5)}|\le M_5,\ |k'''|\le M_3\)이면

\[
E_4\le M_5\{P|e-x_0|+h+\delta\},\qquad
S_C\le\frac{M_3}{2}(h+\delta).
\tag{P32.8}
\]

근 이동이 \(O(\delta)\)인 내부 튜브에서는 \(\mathcal R_p=O(\delta)\).
따라서 root remainder는 \(O(\delta^5)\)다.
대칭성만으로 기하·기울기의 일차 이동이 없어지지는 않는다.

## P32.4. 사차 도함수 부호가 주는 조건부 유한 폭 순서

두 근과 그 사이의 중심·프로파일 지원에서
\(0<m_4\le k^{(4)}\le M_4\)이며
\(0<m_2\le k''\le M_2\)라 하자.
분산 미분의 정확 적분식으로
\(m_2/2\le F_W\le M_2/2\)다.
P32.4는 \(\mathcal S\in[m_4,M_4]\)이므로

\[
\boxed{
-\frac{2M_4}{945m_2}\delta^4
\le W_p-W_u
\le-\frac{2m_4}{945M_2}\delta^4<0,\qquad\delta>0.
}
\tag{P32.9}
\]

이는 같은 A에서 존재하는 두 근에 관한 조건부 결론이다.
\(k^{(4)}\ge0\)만 주어지면 비엄격한 \(W_p\le W_u\)가 따른다.
반대 부호 조건에서는 순서가 뒤집힌다.
임의 프로파일 쌍 또는 임의 광자 모멘트 법칙으로 확장하지 않는다.
점 네 개에서의 양의 k4는 위 구간 전제의 증거가 아니다.
실제 rei_bianchi 커널에 P32.9를 수치적으로 적용했다고 주장하지 않는다.

## P32.5. 새 유한 폭 toy 검증의 정확 기준

새 검증은 무차원 좌표 X의

\[
k(X)=1+X^2-\frac{X^3}{10}+\frac{X^4}{100},\quad
X\in[-2,2],\quad m=0,\ R=2,\ w=1
\]

에 한정한다. PHYS31의 영폭 formal series를 다시 실행하지 않고,
새로운 양의 폭 \(\delta=1/100,1/50\)에서 실제 같은 수준의 근을 구간으로 감싼다.
각 분지 안에서 사용하는 정확 비영 수준·기준 기울기·사차계수는

\[
A_s=\frac{813+60s}{400},\qquad
C_s=\frac{411+40s}{400},\qquad
D_s=-\frac{32}{315(411+40s)}.
\tag{P32.10}
\]

고정 튜브는 \(w\pm\eta,\ \eta=1/4\)다.
도함수는
\(k''=2-3X/5+3X^2/25\),
\(k'''=-3/5+6X/25<0\)이므로 k''는 감소한다.
끝점 값과 k''의 양수성을 이용하면

\[
m_2=\frac{32}{25},\quad M_2=\frac{92}{25},\quad
M_1=\frac{138}{25},\quad M_3=\frac{27}{25},\quad
k^{(4)}=\frac6{25},\quad M_5=0,\quad \kappa=\frac{16}{25}.
\tag{P32.11}
\]

\(|k(e)-k(x_0)|=(1251+260s)/320\)도 정확한 다항식 대입으로 얻는다.
사차 도함수가 상수이므로 \(E_4=0\)이며

\[
\mathcal R_s=|D_s|S_C/\kappa,\qquad
\Delta F=\frac{2}{7875}\delta^4
\tag{P32.12}
\]

가 성립한다. 나머지를 0이라고 놓지 않는다. \(\overline C\)가 이동하므로
근의 사차 근사는 유한 폭에서 일반적으로 정확하지 않다.

서로 다른 두 구현 경로를 비교한다.

1. 밀도의 정확 모멘트와 이항 전개를 사용한 두 중심의 직접 평균.
2. 중심 모멘트 \(M_{3,Y}=sV(V/r-r)\),
   \(M_{4,Y}=Vr^2-V^2+V^3/r^2\)를 사용한
   \(F=1+W-M_{3,Y}/10+(M_{4,Y}+2\delta^2V+\mu_4\delta^4)/100\).

첫 경로는 평균 커널과 p,q를 직접 조립한다. 둘째는 독립성에 따른 총 모멘트를
조립한다. 둘 다 같은 toy와 정확 모멘트를 공유하므로 독립 물리 데이터는 아니다.
Fraction 이분법의 양 끝 잔차를 두 경로로 교차 확인하며,
부호가 반대인 정확 유리수 구간과 단조성으로 유일근을 감싼다.
80회 뒤 폭은 정확히 \(2^{-81}\)이다.
두 근 구간을 바깥 방향으로 빼서 \(\Delta W/\delta^4\)의 구간을 만들고,
전체 구간이 P32.7과 P32.9 안에 있는지 확인한다.
하단−상단의 차이에 대해서도 두 나머지의 합으로 간격 변화를 감싼다.

표준 Rodrigues 계수·경계항·\(\pi\) 정규화와 함께,
비상수 k4를 갖는 단항식 X⁵, X⁶의 P32.2를 정확한 다항 적분으로 확인한다.
이 두 단항식은 항등식 진단용이고 물리적으로 허용된 커널이라고 주장하지 않는다.
밀도 수치 quadrature, float finite difference, 물리 커널 평가, 과거 과학 프로그램 실행은 없다.

실제 실행 상태는 별도의 PROTOCOL.json, 원시 결과와 receipt가 결정한다.
이 문서 작성만으로 검사 통과·재현 성공을 주장하지 않는다.
