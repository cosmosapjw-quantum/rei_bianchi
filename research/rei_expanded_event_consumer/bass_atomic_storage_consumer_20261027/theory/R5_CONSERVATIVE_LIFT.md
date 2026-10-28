# R5 — 유한 원자 거래의 보존적 coarse map과 energy port

## 1. 대상과 단위

한 개의 source-qualified finite transaction을 고정한다. 원자 순서는
\(N=(N_g,N_s,N_p,N_c)^T\)이고, 모든 \(N\)은 같은 기준 부피
\(V_0=1\,{\rm m^3}\)로 나눈 재고다. 따라서 수치의 단위는 count per
reference cubic metre다. \(N_a,N_b\)는 source의 common-\(V_0\) endpoint,
\(d\)는 source의 event increment다. 저장 표현에서
\(r_N=N_b-N_a-d\)를 그대로 둔다. 실제 값과 event 값을 강제로 일치시키지 않는다.

가정은 admitted effective-H를 target H1에 식별한다는 명시적 source map,
동일한 거래·frame·volume, thermal continuum electron, 원래 five energy
sector ownership이다. 311 virtual radiation unknowns는 원자 재고가 아니다.
원래 frozen-left activity-clock 모형을 전체 native-history 모형으로 바꾸지 않는다.

## 2. 수와 전자의 사상

\[
P=\begin{pmatrix}1&1&1&0\\0&0&0&1\\0&0&0&1\end{pmatrix},
\qquad z=PN=(N_{\rm HI},N_{\rm HII},N_{e,\rm th})^T.
\]

**명제 1.** 모든 유한 증감 \(d\)에 대해
\[
d_{\rm HI}+d_{\rm HII}=\mathbf1^Td,\qquad
d_{\rm HII}-d_{e,\rm th}=0.
\]
또한 bound-bound 전이 \(e_i-e_j\), \(i,j\in\{g,s,p\}\)는 \(P\)의 kernel에
속한다. continuum에서 어느 bound level로의 전이는
\((1,-1,-1)^T\)로 사상된다.

**증명.** 첫 두 행의 합은 \(\mathbf1^T\), 두 번째와 세 번째 행은 같다.
\(P e_g=P e_s=P e_p=(1,0,0)^T\),
\(P e_c=(0,1,1)^T\)를 직접 대입하면 나머지가 따른다. 선형성 때문에
임의의 sourcewise signed channel sum에도 성립한다. □

따라서 Lyα down event \((1,0,-1,0)\)의 coarse composition 변화는0이다.
Source의 thermal continuum 수를 fast electron \(\zeta\)에 넣지 않는다.
선택된 거래에 fast-electron channel이 없으므로 event \(\Delta\zeta=0\)다.

저장된 \(d\)의 실제 baryon residual \(\mathbf1^Td\)를 출력한다.
\(\Delta N_{\rm HI}=\sum_{i=g,s,p}d_i\)와 conservation complement
\(-d_c\)를 함께 기록하되 하나로 덮어쓰지 않는다.

## 3. 에너지의 구성적 보완

Source의 atomic internal energy를 \(U_B\), 명시적인 target H ion reference를
\(\chi_R\,[{\rm J/atom}]\)로 둔다. 새 scalar port를
\[
U_h=U_B-\chi_R N_c
\]
로 정의한다. 이상적인 source 모형에서
\[
U_B=\epsilon_{21}^B(N_s+N_p)+\epsilon_I^B N_c
\]
이면
\[
U_h=\epsilon_{21}^B(N_s+N_p)
       +(\epsilon_I^B-\chi_R)N_c.
\]
각 \(\epsilon^B\)는 source의 실제 SI encoding이다. Source가 이미 제공한
J 값을 다시 eV→J 변환하지 않는다.

**명제 2.** 저장된 finite event atomic energy \(A\), continuum event \(d_c\)
및 나머지 source sector energies \(E_j\)에 대해
\[
E_{\rm ion}=\chi_R d_c,\qquad E_h=A-\chi_R d_c
\]
로 두면
\[
E_{\rm ion}+E_h+\sum_{j\ne{\rm atom}}E_j
=A+\sum_{j\ne{\rm atom}}E_j.
\]
따라서 source의 저장 event-energy residual을 정확히 보존한다.

**증명.** \(+\chi_Rd_c\)와 \(-\chi_Rd_c\)가 소거된다. 이는 저장된
decimal을 정확한 rational로 해석한 표현 항등식이며, source residual을
0으로 만드는 정밀도 주장과 다르다. □

이 정의는 BASS의 저장 \(A\)와 \(d\) 사이의 작은 source 계산·표현 잔차도
보존한다. 상수와 재고로 \(A\)를 새로 계산해 원문을 바꾸지 않는다.
Photon, gas thermal, ambient radiation, geometry work는 원래 owner의
별도 port를 유지한다. \(E_h\)는 gas heat, fast kinetic 또는 \(w_{\rm ext}\)가 아니다.

두 순차 거래의 \(A,d\)를 동일한 energy convention 아래 합하면
\(E_h(A_1+A_2,d_1+d_2)=E_h(A_1,d_1)+E_h(A_2,d_2)\)다.
이는 동일 source의 disjoint finite transactions에 대한 식이다.
Source 대안이나 같은 거래의 cumulative views를 추가 사건으로 합하지 않는다.

## 4. 부피 변화와 endpoint correction

\(R=V_b/V_0>0\)라 둔다. Source final stocks는 common-\(V_0\) 재고이므로
right proper density는 \(PN_b/R\)이다. Proper endpoint change는
\[
D_p=\frac{PN_b}{R}-PN_a
=\underbrace{\frac{Pd}{R}}_{\rm event}
+\underbrace{PN_a(R^{-1}-1)}_{\rm volume}
+\underbrace{\frac{Pr_N}{R}}_{\rm saved\ endpoint\ residual}.
\]
\(N_b=N_a+d+r_N\)의 대입으로 증명된다. \(PN_b-PN_a\)와 proper-density
endpoint change는 서로 다른 관측량이다.

양쪽 recipient reference densities \(b_a,b_b>0\)가 명시되었을 때만
조건부 abundance diagnostic을 정의한다:
\[
D_Y=\frac{PN_b}{R b_b}-\frac{PN_a}{b_a}
=\frac{Pd}{R b_b}
+PN_a\left(\frac1{R b_b}-\frac1{b_a}\right)
+\frac{Pr_N}{R b_b}.
\]
실제 이 단위에는 recipient \(b\)가 제공되지 않았으므로 actual native25는
null이다. 위 조건부 진단은 전체 native state update가 아니다.

방향 \((\dot N_a,\dot N_b,\dot R,\dot b_a,\dot b_b)\)에 대한 full JVP는
\[
\dot D_Y=
\frac{P\dot N_b}{R b_b}
-\frac{P\dot N_a}{b_a}
-\frac{PN_b\dot R}{R^2b_b}
-\frac{PN_b\dot b_b}{R b_b^2}
+\frac{PN_a\dot b_a}{b_a^2}.
\]
기존 quotient와 양쪽-\(b\) endpoint proof를 재사용하고, 새 common-volume
factor \(R\)에 chain rule을 적용한 식이다. \(\dot R\)항을 생략하지 않는다.

에너지 sidecar의 방향식은
\[
\dot E_h=\dot A-\chi_R\dot d_c-\dot\chi_R d_c.
\]
실제 source를 고정하면 \(\dot\chi_R=0\)이지만 일반 API는 해당 항을 드러낸다.

## 5. Source energy work의 전달

Source의 common-volume endpoint energy, initial energy, event energy와
geometry work를 각각 \(U_b^0,U_a,E,W\)로 두고
\(r_E=U_b^0-U_a-E-W\)를 기록한다. Atomic sector의 각 \(U\)를 같은
\(\chi_R N_c+U_h\)로 분해하면 모든 source-sector 합과 \(r_E\)는 그대로다.
Source의 right proper energy \(U_b^{\rm proper}\)와 \(U_b^0/R\)의 저장
표현 차이도 별도 diagnostic으로 남긴다. \(W\)를 event photon energy에
중복해서 더하지 않는다.

## 6. 계산 계약과 완료 범위

구현은 exact Fraction arithmetic으로 이 선형 사상·차이·나눗셈을 계산한다.
Source raw bytes를 한 번 확인하고 기존 finite solution을 소비한다.
새 유도에는 quadrature, ODE, projection solve, history extrapolation이 없다.
Integrated event에 \(1/H\)를 넣지 않으며 평균 rate를 생성하지 않는다.
따라서 ddt와 ddeta를 혼용하는 clock 변환도 새로 수행하지 않는다.

실제 gas exchange가0이 아니므로 recipient EOS/state 없는 logT 갱신은 null이다.
Actual recipient b, native Vigil client/tube, 물리 반경 및 전체 물리 solution은
이 representation theorem의 결론에 포함되지 않는다. 이는 새 strong no-go가
아니라 source-qualified positive construction이며, 열려 있는 물리 입력의
정확한 다음 접속 지점은 그대로 유지된다.
