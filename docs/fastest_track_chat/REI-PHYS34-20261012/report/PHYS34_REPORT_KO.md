# REI-PHYS34: 하단 분지의 유한 폭 근 존재와 프로파일 순서

연구일: 2026-10-12 KST. 대상 프로젝트: `cosmosapjw-quantum/rei_bianchi`. 실제 첫 실행 및 복원 경로 재실행 결과는 모두 **PASS_SCOPED, 25/25**다. 이 본문은 독립 최종 판정을 위해 동결한 과학 결과이며, 최종 채택 상태와 범위는 `state/FINAL_STATE.md`, `state/CLOSEOUT.json`, `independent/DECISION_REVIEW.json`이 정한다.

## 1. 이번 루프에서 확보한 결과

PHYS33의 상단 분지에 이어, PHYS34는 **하단 분지 하나**의 전 유한 폭 구간을 인증했다. 정확한 하단 수준을

\[
A_-=-3.2582515\times10^{-137}\ \mathrm{s}^{-4}
\]

로 고정하고, 실제 분산 \(W\), 폭 \(0\le\delta\le10^{-3}\) eV, 저장 중심 \(\widehat W\)의 반경 \(0.25\) eV² tube를 사용했다. 두 고정 프로파일은

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16}=\frac{1+P_4(z)}2,
\quad -1\le z\le1.
\]

고정된 source-real 커널에 대해 다음을 얻었다.

1. 두 프로파일 모두 각 허용 폭에서 \(F_\alpha(\delta,W)=A_-\)의 근을 갖는다. 그 근은 지정한 tube 안에서 유일하다.
2. 전 폭에서 \(|W_{-,\alpha}(\delta)-\widehat W|\le0.170563\) eV²이므로 존재 증명에 필요한 반경보다 작다.
3. 모든 양의 허용 폭에서

\[
\boxed{
-0.0150208\,\delta^4
\le W_{-,p}(\delta)-W_{-,u}(\delta)
\le-0.00000603100\,\delta^4<0.
}
\tag{R34.1}
\]

여기서 두 계수의 단위는 eV⁻²이고 근 차이의 단위는 eV²다. \(\delta=0\)에서는 두 프로파일의 응답과 유일근이 같으므로 엄격한 부등호를 붙이지 않는다. 최대 폭 \(\delta=0.001\) eV에서는

\[
\boxed{
-1.50208\times10^{-14}
\le W_{-,p}-W_{-,u}
\le-6.03100\times10^{-18}\quad\mathrm{eV}^2.
}
\tag{R34.2}
\]

이 결과는 실제 유한 폭에 대한 포함 경계다. 작은 폭의 선도항을 계산한 뒤 나머지를 생략한 결론이 아니다. 근을 개별적으로 수치 탐색해 빼는 방식도 사용하지 않았다. 원시 근 차이 계수는 정확한 Peano 항등식, 연속 영역의 4차 도함수 경계, 분산 기울기 경계를 결합해서 얻었다.

현재의 강한 결론은 고정된 수학적 모델에 관한 것이다. 원래 J와 원자 fit의 불확실성, 관측 입력, coupled history의 물리적 타당성은 해결하지 않았다. **Physical HOLD**를 유지한다. 상단과 하단의 프로파일 이동 차이, 즉 두 분지 사이 gap 변화의 부호도 이번 결과에 포함하지 않는다.

주요 원증거는 `evidence/CERTIFICATE_FIRST.json`, `evidence/CERTIFICATE_REPLAY.json`, `evidence/EXECUTION_RECEIPT.json`이다. 상세한 수학적 연결은 `contributions/theory/LOWER_BRANCH_DERIVATION_KO.md`와 `report/ROOT_TUBE_PROOF_KO.md`에 있다.

## 2. 이어받은 상태와 이번에 고정한 대상

연속성의 기준은 다음 원격 identity다.

| 항목 | 고정값 |
|---|---|
| 저장소 | `cosmosapjw-quantum/rei_bianchi` |
| branch | `forward/rust-reion-kernels-20260922` |
| PR | 83, open·draft·unmerged |
| PHYS34 시작 commit | `06e65fa291685fcec0e012ee84d291b356922748` |
| 시작 tree | `7850e776a3574278499a326d95b5d6aecb78e9c9` |
| scientific source subtree | `cb69b4736dd046e4675557577eb8e0ead037d1f3` |
| 직전 완료 작업 | REI-PHYS33-20261012, 상단 유한 폭 인증 |

이 identity와 최신 인계는 `evidence/CONTINUITY_AUDIT.json`, `SOURCE_MANIFEST.json`으로 묶었다. 현재 PHYS34에 필요한 9개 PHYS33 원격 문서는 내용과 Git blob identity를 대조했다. repository metadata 확인을 native 실행이나 전체 coupled source의 물리 검증이라고 부르지 않는다.

PHYS33의 first1/replay1은 이미 소진되어 있으며 재사용하지 않았다. PHYS29–PHYS33 과학 entrypoint, ACCEL02/C13/PILOT02/COMMON18, NCP/native 등 별도 lane을 재실행하지 않았다. PHYS34의 새 두 슬롯에서 하단 영역만 평가했다.

상단과 하단의 수준은 서로 다르다.

| 분지 | 정확한 고정 수준 \(\mathrm{s}^{-4}\) | 상태 |
|---|---:|---|
| 상단 PHYS33 | \(-2.2748589\times10^{-137}\) | 기존 결과 상속, 이번 재실행 0회 |
| 하단 PHYS34 | \(-3.2582515\times10^{-137}\) | 이번에 새로 인증 |

각 분지 안에서 두 프로파일이 **같은 그 분지의 A**를 사용한다는 뜻이다. 두 분지가 서로 같은 A를 사용한다는 뜻은 아니다. 하단 A의 원 키는 `second_order.jet_chain.lower_root.response_s-4`다. 더 긴 `stored_PHYS26_response_s-4`, 다른 계산 경로의 응답, 상단 A, 0 또는 새로 계산한 \(F_0(\widehat W)\)로 바꾸지 않았다.

하단 중심의 원 키는 `constants.stored_PHYS26_root_strings.lower_root`이고, 다음 전체 문자열을 정확한 십진 유리수로 읽었다.

```text
23.42021899235339297211351479315057454874081817054292481189118799276998028222045968598367218051982929113154658725620727981626004744285172054408046783979559490765
```

이 값이 \(\widehat W\)이며 단위는 eV²다. 따라서 인증한 tube는 정확히 \([\widehat W-0.25,\widehat W+0.25]\)이고, 표시용으로 그 양 끝을 쓰면 약 23.170218992353393 및 23.670218992353393 eV²다. 표시용 반올림으로 tube 자체를 다시 정의하지 않는다.

## 3. 커널·단위·상수 convention

\[
\mathscr D=E\partial_E,\qquad
\phi(E)=\sigma_{\rm HI}(E)[J_x+J_w(E-\chi)],
\]
\[
k(E)=\mathcal P(\mathscr D^2+3\mathscr D)\phi(E)
=\mathcal P[E^2\phi''(E)+4E\phi'(E)].
\tag{R34.3}
\]

\[
\mathcal P=\frac{q_{\rm src}N_0c_{\rm light}n_H(1-x_{HII})}{180},
\qquad
q_{\rm src}=2\left(\frac{\operatorname{real64}(1.01\cdot10^{-14})-
\operatorname{real64}(0.99\cdot10^{-14})}{2}\right)^2.
\]

여기서 원 커널의 \(q_{\rm src}\)와 아래 패킷 확률 \(q\)는 서로 다른 양이다. \(N_0=\operatorname{real64}(0.05)\), \(c_{\rm light}=\operatorname{real64}(29979245800)\) cm/s, \(n_H=\operatorname{real64}(10^{-4})\), \(x_{HII}=\operatorname{real64}(0.9)\)를 보존했다. natural units로 전환하지 않았다.

H I fit의 사용 구간에서는

\[
\sigma_{\rm HI}(E)
=\sigma_0 a_{\rm area}(X-1)^2
X^{P/2-11/2}\left(1+\sqrt{X/y_a}\right)^{-P},
\qquad X=E/E_0,
\tag{R34.4}
\]

이며 원 리터럴은 \(E_0=0.4298\), \(y_a=32.88\), \(P=2.963\), \(\sigma_0=5.475\times10^4\), \(a_{\rm area}=10^{-18}\), \(\chi=13.598434599702\)다. 이 리터럴들은 `Fraction.from_float(float(literal))`에 해당하는 **binary64 값 자체의 정확한 유리수**로 해석한다. 그 뒤의 곱·함수는 정확한 실수 대상으로 정의한다. 따라서 원 binary64 연산 순서를 비트 단위로 모사한 결과나 저장된 rounded prefactor의 재사용과는 의미가 다르다.

J는 PHYS22 원 JSON `results.baseline_local.J_nonphoto[2][0]` 및 `[2][3]`의 직렬화 문자열을 정확한 십진 유리수로 해석했고 PHYS29의 복제 키와 일치를 확인했다. J를 이번에 다시 물리적으로 결정하지 않았다.

H I cutoff \(\operatorname{real64}(13.60)\), He I cutoff \(\operatorname{real64}(24.59)\), 가열 에너지 offset \(\chi\)를 구별한다. 평가 grid가 덮는 실제 에너지 구간은 두 cutoff 사이에 엄격하게 남는다. 단위는 \(E,\delta\)가 eV, \(W\)가 eV², \(k,F,A\)가 s⁻⁴, \(k^{(n)}\)가 s⁻⁴ eV⁻ⁿ이다. 기존 metric convention \((-,+,+,+)\)를 바꾸지 않았다.

## 4. 하단 패킷의 실제 분산과 지지

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
R=b-m=6.58\quad\mathrm{eV},
\quad\mu_2=1/3.
\]

\[
r=R-\delta,\quad V=W-\mu_2\delta^2,
\quad e_\delta=b-\delta,
\quad x_{\delta,W}=m-\frac Vr,
\]
\[
p=\frac{V}{r^2+V},\qquad q=\frac{r^2}{r^2+V}.
\tag{R34.5}
\]

중심 변수 Y가 \(e_\delta,x_{\delta,W}\)에 확률 \(p,q\)를 갖고 Z가 독립인 프로파일 변수이면 \(E=Y+\delta Z\)다. 평균은 정확히 m이고, 중심 분산은 V다. 두 프로파일의 평균 0과 공통 \(\mu_2\) 때문에 전체 분산은

\[
\operatorname{Var}(E)=V+\mu_2\delta^2=W.
\]

이는 PHYS34가 제어하는 분산이 실제 W라는 점을 보장한다. 단순한 두 원자 중심 분산 V로 바꿔 해석하지 않는다.

응답은

\[
F_\alpha(\delta,W)=p\int k(e_\delta+\delta z)h_\alpha(z)dz
+q\int k(x_{\delta,W}+\delta z)h_\alpha(z)dz.
\tag{R34.6}
\]

이번 exact 비교는 전체 직사각형 \([0,0.001]\times[\widehat W-0.25,\widehat W+0.25]\)에서 양의 확률과 실현가능성을 확보했다. endpoint 패킷은 \([24.578,24.58]\) eV다. 내부 패킷의 정확한 포함구간은

\[
\left[m-\frac{\widehat W+\eta}{R-d}-d,
m-\frac{\widehat W-\eta-\mu_2d^2}{R}+d\right],
\tag{R34.7}
\]

이며, 표시용 근삿값은 \([14.4011554959\ldots,14.4796901734\ldots]\) eV다. 두 패킷과 패킷 사이의 모든 직선 보간 경로는 고정 에너지 영역

\[
J=[14.35,24.58]\ \mathrm{eV}
\]

안에 있다. 도함수 부호를 패킷 중심 두 점에서만 확인하면 기울기 적분 전체를 덮지 못한다. PHYS34는 이 J 전체를 인증했다.

## 5. 연속 영역 인증의 방법과 실제 경계

프로파일 변수 z와 구별하기 위해 커널의 sqrt 좌표를 \(\zeta=\sqrt{E/B}\), \(B=E_0y_a\)로 쓴다. exact Fraction 미분 recurrence는 PHYS33에서 유도한 것을 그대로 재사용했다.

\[
Q_\phi(\zeta)=(y_a\zeta^2-1)^2
[J_x-J_w\chi+J_wB\zeta^2],
\]
\[
T_{\lambda,\nu}Q=[\lambda+(\lambda+\nu)\zeta]Q
+\zeta(1+\zeta)Q',
\]
\[
U=T_{P-11,-P}Q_\phi,
\quad Q_0=T_{P-11,-P-1}U+6(1+\zeta)U,
\]
\[
Q_{n+1}=T_{P-11-2n,-P-2-n}Q_n.
\tag{R34.8}
\]

양의 공통 인자

\[
C=\mathcal P\sigma_0a_{\rm area}y_a^{P/2-11/2}
\]

를 사용하면

\[
k^{(n)}(E)=\frac{C}{4(2B)^n}
\zeta^{P-11-2n}(1+\zeta)^{-P-2-n}Q_n(\zeta).
\tag{R34.9}
\]

실제 grid는 \(\sqrt{J/B}\)의 outward 끝점으로 정한 32개 exact rational cell이다. 느슨한 \([1,4/3]\) 포함구간은 별도의 포함 검사에만 쓰였다. 각 다항식을 해당 cell의 Bernstein basis로 정확하게 변환하면 다항식 값은 그 계수들의 최소·최대 사이에 있다. 이 경계는 cell 전체에 적용되므로 지점 샘플의 부호를 이어 붙인 주장과 다르다.

양의 비다항 인자는 90자리 outward Decimal interval로 감쌌다. 기본 연산은 FLOOR/CEILING을 구별한다. ln·exp 및 sqrt의 근접 반올림 결과를 인접 표현값으로 바깥에 확장하며, 실수 거듭제곱은 `exp(alpha*ln(x))`의 interval 합성으로 구현했다. `Decimal.power` 자체의 근접 반올림을 그대로 엄밀 경계로 사용하지 않았다. 이는 Python 3.12 Decimal 공식 문서의 반올림·ln·exp·next_minus/next_plus semantics를 전제로 한 인증이다.[S4]

원시 JSON에는 **exact rational cell 양 끝점**과 그 cell을 다시 Decimal로 감싼 **prefactor/표시 구간**을 별도 필드로 저장했다. 후자의 폭이 조금 더 넓더라도 다항식 bound의 증명 대상은 전자의 정확한 cell이다. PHYS33에서 검토했던 이 구별을 이번 기록에서는 직접 드러냈다.

다음 표는 실제 원시 endpoint를 바깥 방향으로 단순화한 값이다. 표의 짧은 값으로 내부 계산을 다시 수행한 것은 아니다.

| 양 | 인증한 보수적 경계 | 단위 |
|---|---:|---|
| \(\sup_J|k'|\) | \(\le1.13638\times10^{-64}\) | s⁻⁴ eV⁻¹ |
| \(k''\) | \(1.14150\times10^{-66}\le k''\le4.49452\times10^{-65}\) | s⁻⁴ eV⁻² |
| \(k^{(4)}\) | \(1.28077\times10^{-67}\le k^{(4)}\le8.10157\times10^{-66}\) | s⁻⁴ eV⁻⁴ |
| \(\kappa\), 분산 기울기 하한 | \(\ge5.70750\times10^{-67}\) | s⁻⁴ eV⁻² |
| \(K\), 분산 기울기 상한 | \(\le2.24726\times10^{-65}\) | s⁻⁴ eV⁻² |

단일 main은 5개 미분 차수의 32셀, 즉 160개 연속영역 enclosure를 만들었다. 정확한 기준 잔차의 두 점, 두 retained node에서 4개 차수씩 비교한 8점을 합쳐 Bernstein/prefactor box는 각각 170개였다.

별도의 ordinary-energy Taylor 전개를 \(b\) 및 `u_zero`에서 만들고 \(k,k',k'',k^{(4)}\)를 대조한 8개 비교도 모두 통과했다. 이 교차검사는 계산식이 서로 다르다는 의미에서 독립적이다. 같은 Decimal helper와 같은 입력을 사용하므로 다른 산술 backend나 독립 물리 데이터의 검증은 아니다. 연속 부호의 주 증거는 여전히 Bernstein cell의 전 영역 경계다.

## 6. 하단에서 기울기의 부호가 뒤집히지 않는 이유

고정 \(\delta\)에서 \(g(y)=\int k(y+\delta z)h_\alpha(z)dz\), \(e=e_\delta\), \(x=x_{\delta,W}\)로 두면

\[
D=x-e=-\frac{r^2+V}{r}<0,\quad
p_W=\frac1{D^2},\quad x_W=-\frac1r,\quad qx_W=Dp_W.
\]

따라서

\[
F_{\alpha,W}
=\frac{g(e)-g(x)+Dg'(x)}{D^2}
=\int_0^1t\,g''(e+tD)dt
\]
\[
=\int_0^1t\int k''((1-t)e_\delta+tx_{\delta,W}+\delta z)
h_\alpha(z)dz\,dt.
\tag{R34.10}
\]

하단의 역방향 선분은 D에 들어갈 뿐, 최종 적분 앞에 새 음의 부호를 만들지 않는다. 확률밀도는 양수이고 \(\int_0^1t\,dt=1/2\)이므로 전 tube에서

\[
0<\kappa:=m_2/2\le F_{\alpha,W}\le M_2/2=:K.
\tag{R34.11}
\]

이것이 두 프로파일 모두의 분산 단조성과 tube 안 유일성을 연결하는 핵심이다.

## 7. 정확한 A의 근 존재: 잔차와 균일 이동을 합쳤다

저장 중심 \(\widehat W\)를 exact root라고 가정하지 않았다. 기준 내부 에너지를 전체 W 문자열에서

\[
x_0=m-\widehat W/R
\]

로 재구성하고, \(p_0=\widehat W/(R^2+\widehat W)\), \(q_0=1-p_0\)에서

\[
F_0(\widehat W)-A_-=p_0k(b)+q_0k(x_0)-A_-
\]

를 outward 평가했다. 결과는 정확하게 다음 포함구간이다.

\[
F_0(\widehat W)-A_-
\in[-1.396128542248,-1.396128540852]\times10^{-142}\ \mathrm{s}^{-4}.
\tag{R34.12}
\]

잔차는 0을 포함하지 않는다. 그 절댓값 상계 \(\epsilon_r=1.396128542248\times10^{-142}\)를 그대로 근 존재 증명에 더했다. 과거 retained `u_zero` 문자열은 수식 교차검사에만 사용했으며 이 기준 잔차의 정확한 x0 대신 사용하지 않았다.

\(W=\widehat W\)를 고정한 폭 변화에서, \(\widehat W>\mu_2Rd\)의 exact 비교로 \(p_0\le p_\delta\le p_d\), \(q_\delta\le q_0\)를 확보했다. 중심 이동은

\[
D_x=\frac{\widehat Wd}{R(R-d)}+\frac{\mu_2d^2}{R-d}
\]

로 덮고, 평균 0인 프로파일의 평활화 나머지는 \(\mu_2M_2d^2/2\)로 덮었다. 결과적으로

\[
B_{\rm disp}=(p_d-p_0)|k(b)-k(x_0)|_{
\rm upper}+M_1[p_dd+q_0D_x]+\frac{\mu_2M_2d^2}{2}
\tag{R34.13}
\]

는 두 프로파일 및 전 폭에 공통인
\(|F_\alpha(\delta,\widehat W)-F_0(\widehat W)|\)의 상계다.

실제 인증 결과는 다음과 같다.

| 충분조건의 항목 | 바깥 방향으로 단순화한 결과 |
|---|---:|
| \(B_{\rm disp}\) | \(\le9.73485\times10^{-68}\ \mathrm{s}^{-4}\) |
| \(\epsilon_r\) | \(\le1.39613\times10^{-142}\ \mathrm{s}^{-4}\) |
| \(\kappa\eta-(B_{\rm disp}+\epsilon_r)\) | \(\ge4.53392\times10^{-68}\ \mathrm{s}^{-4}>0\) |
| \(\rho=(B_{\rm disp}+\epsilon_r)/\kappa\) | \(\le0.170563\ \mathrm{eV}^2<\eta\) |
| \(\epsilon_r/\kappa\) | \(\le2.44613\times10^{-76}\ \mathrm{eV}^2\) |

따라서 tube의 왼쪽 끝에서는 \(F_\alpha-A_-<0\), 오른쪽 끝에서는 \(F_\alpha-A_->0\)가 전 폭에 공통으로 성립한다. 연속성과 R34.11을 결합하면 각 폭·각 프로파일의 유일근이 tube 내부에 존재한다. 마지막 행은 폭 0의 정확한 수준 근이 저장 중심과 얼마나 가까운지 나타낸다. 이 작은 수학적 오차를 J나 원자 fit의 물리 불확실성으로 해석하지 않는다.

전체 폭 이동 상계 0.170563 eV²가 R34.2의 프로파일 간 차이보다 훨씬 크더라도 모순이 아니다. 앞의 값은 각 근이 저장 중심에서 얼마나 멀리 있을 수 있는지를 덮는 보수적 상계다. 프로파일 간 차이는 공통 부분을 소거하는 다음 정확 항등식으로 따로 제한한다.

## 8. 정확한 Peano 항등식이 엄격한 근 순서를 준다

\(Q(z)=(1-z^2)^4\)에 대해

\[
h_p-h_u=Q^{(4)}/768,
\quad\int_{-1}^1Q(z)dz=256/315.
\]

Q와 그 1·2·3차 도함수는 양 끝점에서 0이다. 네 번 부분적분을 하면 경계항 없이

\[
\int k(y+\delta z)(h_p-h_u)(z)dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)d\pi(z),
\]
\[
d\pi(z)=\frac{315}{256}(1-z^2)^4dz
\tag{R34.14}
\]

를 얻는다. \(\pi\)는 양의 확률측도다. 두 프로파일의 \(\mu_2\)가 같으므로 같은 W에서 두 중심과 p,q도 같다. 따라서

\[
F_p-F_u=\frac{\delta^4}{945}\mathcal S_-,
\qquad m_4\le\mathcal S_-\le M_4.
\tag{R34.15}
\]

이것은 \(k^{(4)}>0\)일 때 같은 W에서 \(F_p>F_u\)라는 뜻이다. 응답은 W와 함께 증가하므로 같은 A에 도달하는 P4 근은 더 작은 W에 놓인다. 두 근의 존재를 이미 확보했기 때문에 이 비교에서 존재를 가정하고 결론을 되돌려 쓰는 순환은 없다.

두 근 사이의 평균 기울기 \(\overline C_p\in[\kappa,K]\)를 사용하면 정확하게

\[
W_{-,p}-W_{-,u}
=-\frac{\delta^4}{945}
\frac{\mathcal S_-(\delta,W_{-,u})}{\overline C_p}.
\tag{R34.16}
\]

원 90자리 포함 경계에서 계산한 계수는

\[
C_{\rm small}=\frac{m_4}{945K}
\approx6.031004149108888\times10^{-6}\ \mathrm{eV}^{-2},
\]
\[
C_{\rm large}=\frac{M_4}{945\kappa}
\approx0.01502071153799949\ \mathrm{eV}^{-2}.
\]

이 approximate 표시값 자체를 엄밀 endpoint로 쓰지 않고, raw의 Csmall.lower보다 작은 `0.00000603100`, Clarge.upper보다 큰 `0.0150208`로 바깥에 단순화한 것이 R34.1이다. 앞 표의 짧은 m2·m4 값들을 새로 조합해 이 계수를 산출한 것이 아니다.

## 9. 실제 실행과 재현성

실행 전에 계약·프로토콜·입력·코드·이론·연속성 증거 **33개 파일**을 SHA256으로 고정했다. `evidence/PREEXECUTION_FREEZE.json`의 SHA256은 다음과 같다.

```text
c6c36f1d9a2c08a006f9f38a39feb395885dc9e555e567c66e63088eea62b76b
```

그 후 한 번의 첫 실행을 수행했다. 통과한 원본의 고정 파일과 freeze를 포함한 34-member ZIP을 별도 디렉터리에 실제로 풀고 모든 고정 해시를 대조한 뒤, 한 번의 복원 경로 재실행을 수행했다. 복원 archive는 `evidence/REPLAY_INPUT.zip`, 그 검증 기록은 `evidence/RESTORATION_RECEIPT.json`이다.

| 항목 | 첫 실행 | 복원 경로 재실행 |
|---|---:|---:|
| 판정 | PASS_SCOPED | PASS_SCOPED |
| 통과 check | 25/25 | 25/25 |
| Bernstein box | 170 | 170 |
| prefactor box | 170 | 170 |
| ordinary-energy joint jet | 2 | 2 |
| 조립한 기준 잔차 | 1 | 1 |
| main wall time | 0.941498452 s | 0.895135447 s |
| main CPU time | 0.940994652 s | 0.892254564 s |
| main 보고 peak RSS | 16,896 KiB | 16,768 KiB |
| parent가 관측한 child exit | 0 | 0 |
| 별도 보존 stderr 크기 | 0 byte | 0 byte |

실제 두 과학 main의 합계 wall time은 약 1.83663 s, CPU time은 약 1.83325 s다. 사전 cap은 main당 wall45 s, CPU40 s, memory384 MiB, Bernstein/prefactor 각각512개, joint jet4개였다. 과거 main·root iteration·유한 폭 quadrature·native·gas IVP·NCP·변경 없는 helper의 일반검사 반복은 모두 0회다. 새 연구 main 두 슬롯은 **SPENT: first1/1, replay1/1**이다.

두 원시 인증서는 각각 1,028,560 byte이며 바이트가 완전히 같다.

```text
SHA256 9b576de7e6079b5a9a3352f6049f550fde13646dda8a1d36022febcf6e11ccf4
```

경로·실행시간·역할을 scientific raw에 섞지 않았기 때문에 과학 결과의 바이트 동일성을 대조할 수 있다. 각 실행의 다른 runtime provenance는 별도 ledger와 process 파일에 보존했다. wrapper는 실제 child stdout과 stderr를 각 파일로 보존하고 실제 종료코드·timeout 여부를 관측했다. controller가 받은 원래 `exec_command` return envelope도 변경 없이 별도 JSON에 넣었다. 실행 tool의 `wall_time_seconds`는 서비스가 보고한 별도 필드이며, child의 main 시간이나 parent의 wait 시간을 재정의하지 않는다.

PHYS33의 일반 산술·Bernstein 검사는 바이트가 같은 두 helper와 기존 raw PASS·독립 판정의 해시를 묶어 상속했다. 그 검사를 이번에 또 실행하지 않았다. `outward_decimal.py` SHA256은 `1d7e9a4e810dbe0f54a525b542163959c38e596951fc70a5a090e967eb332bad`, `rational_kernel.py` SHA256은 `51fbc5574ab20f4a45305e8c5fedf3f81ef2cb1423f912b624c88686990690dc`다. 이전 PHYS33에서 보존하지 못했던 외부 process envelope를 이번 파일들로 소급 보충한 것처럼 표현하지 않는다.

동일 host에서 경로를 바꾸고 복원한 재실행이므로 독립 platform, 다른 산술 backend 또는 원자 데이터의 독립 물리 검증을 뜻하지 않는다. 이번 결과는 **직접 유도 + 선언한 Decimal semantics 아래의 구간 포함 + 해당 고정 구현의 실제 실행 검증**까지다.

## 10. 상태 해석과 남은 연구 의무

실행 전 계약의 `claims.lower_branch=TARGET_NOT_YET_EVALUATED`는 raw의 `claim_ceiling`에 그대로 들어 있다. 이는 immutable 계약 snapshot이다. 실행 후 실제 상태는 raw 최상위 `status`, `checks`, `certificate`, 실제 실행 영수증으로 판정하며 최종 채택은 독립 decision과 FINAL_STATE로 정한다. 원시 증거나 사전 계약의 미평가 라벨을 사후에 덮어쓰지 않는다.

이번 루프의 이론 기여자는 `/root/polynomial_theory`, 계약·구현·후보 작성자는 `/root`다. 두 역할은 독립 최종 reviewer가 아니다. 후보와 검증 설계에 참여하지 않은 `/root/decision_review`가 실제 새 후보 freeze와 원시증거를 읽고 마지막 판정을 내린다. reviewer의 과학 실행 예산도 0이며 첫 실행/재실행 결과를 또 계산하는 역할이 아니다.

남은 핵심 물리·수학 의무는 다음과 같다.

- 두 분지의 프로파일 이동이 각각 음수인 사실만으로 그 차이의 부호를 정할 수 없다. 다음 PHYS35 후보는 **두 분지의 이동 차이를 직접 비교하는 경계**다. 이때 현재의 서로 다른 A−,A+를 사용하는 root separation인지, 새 공통 A의 다른 문제인지 먼저 정확하게 정의해야 한다.
- J 및 원자 fit의 불확실성을 이번 source-real 결과에 전파하지 않았다. 따라서 아주 작은 수학적 잔차나 근 차이는 관측·원자 물리의 정밀도 주장이 아니다.
- 특정 두 프로파일과 특정 feasible tube의 결과를 모든 광자 분포의 전역 최적성이나 모든 폭의 명제로 확장하지 않는다.
- coupled production trajectory, atomic precision 승격, 새로운 escape channel은 이번 범위가 아니다.

보호 상태는 다음과 같이 그대로다.

```text
Physical HOLD
[160,161] FAIL; tick160
auxiliary escape FAIL
HH/RCT/CR OFF
precision atomic PARKED
production source/default/runtime changes0
```

PHYS34 결과를 branch에 반영하는 범위는 새 `docs/fastest_track_chat/REI-PHYS34-20261012/` prefix에 자료를 추가하는 작업이다. 기존 경로, scientific source, PR 본문, draft·unmerged 상태를 보존하는 expected-head nonforce 방식으로만 처리한다. 실제 반영 사실은 작업 후 생성한 `publication/PUBLICATION_RECEIPT.json`으로 확인한다. 그 영수증은 자신이 포함된 commit의 hash를 순환적으로 기록할 수 없으므로 최종 전달 archive에 따로 보존한다.

## 근거와 읽는 순서

**[S1]** 고정 원자료: `inputs/PHYS29_SECOND_ORDER_FIRST.json` SHA256 `40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f`; `inputs/PHYS22_INITIAL_COEFFICIENTS.json` SHA256 `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79`. 키·source 발췌·현재 provenance는 `SOURCE_MANIFEST.json`에 있다.

**[S2]** 이번 정확 유도 및 정리 연결: `contributions/theory/LOWER_BRANCH_DERIVATION_KO.md`, `report/ROOT_TUBE_PROOF_KO.md`. 재사용한 Bernstein 미분 유도는 `inputs/PHYS33/contributions/theory/DERIVATION_KO.md`, Peano 및 일반 기하 선행 증명은 `inputs/PHYS32/` 아래 세 기여 문서다.

**[S3]** 이번 실제 결과: `evidence/CERTIFICATE_FIRST.json`, `evidence/CERTIFICATE_REPLAY.json`, `evidence/EXECUTION_RECEIPT.json`, `evidence/process/`, `evidence/run_ledger/`, `evidence/RESTORATION_RECEIPT.json`. 수치 표의 짧은 endpoint는 `report/NUMERICAL_SUMMARY.json`에 출처와 방향을 기록했다.

**[S4]** 산술 semantics의 1차 문서: [Python 3.12 Decimal 공식 문서](https://docs.python.org/3.12/library/decimal.html), 특히 [exp](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.exp), [ln](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.ln), [sqrt](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.sqrt), [next_minus](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.next_minus), [next_plus](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.next_plus), [Context.power](https://docs.python.org/3.12/library/decimal.html#decimal.Context.power). 실제 실행 runtime은 Python3.12.14/libmpdec4.0.0으로 기록되어 있으며, 조회된 3.12 계열 웹 문서 표제는 3.12.15다. 웹 문서 조회로 실행 환경을 교체하지 않았다.

**[S5]** 최종 독립 판정·닫힘·다음 인계: `independent/DECISION_REVIEW.json`, `independent/DECISION_REVIEW_KO.md`, `state/FINAL_STATE.md`, `state/CLOSEOUT.json`, `next/PHYS35_NEXT_HANDOFF_KO.md`.
