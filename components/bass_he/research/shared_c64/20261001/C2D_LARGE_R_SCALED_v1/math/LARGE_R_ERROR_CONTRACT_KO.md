# C2d 큰 R: 두 원점의 scaled coupling과 오차 계약

이 문서는 새 물리 계산 전의 독립 수학 설계다. A2에서 채택한 해석적 결과, 부모의 저장된 수치, 여기서 유도한 오차 전파를 구분한다. 새 고유값 계산·파동함수 적분은 0회이며 부모 JSON의 scalar 비교만 수행했다. 아래 허용오차는 실행 전 권고다. 최종 실행 범위·값·예산의 권위는 루트 `CONTRACT.json`에 있다.

## 1. 정의·부호·점근 결과

고정 핵, spinless 비상대론적 한 전자 Coulomb Hamiltonian, 전하수 `(1,2)`, 양의 meridional phase인 최저 `m=0` 및 real cosine bright `|m|=1` 상태를 유지한다. 내적은 첫 인자에 반선형이다. 핵 반발은 전자상태와 gap에 영향을 주지 않는 공통 scalar로 제외한다. 전하중심 O에서 `z_A=-2R/3`, `z_B=R/3`이고 B는 He 핵이다. 물리 단위를 없애는 것이 아니라 다음 단위로 계산량을 표시한다.

\[
a_A=\frac{\hbar^2}{m_e\kappa},\quad E_A=\frac{\hbar^2}{m_ea_A^2},\quad
x=R/a_A,\quad\ell_C=\frac{\langle g,L_y^Cb\rangle}{-i\hbar},\quad
P=\frac{\langle g,p_xb\rangle}{-i\hbar/a_A},\quad
D=\frac{\langle g,x_{\rm cart}b\rangle}{a_A},\quad
\Delta=\frac{E_b-E_g}{E_A}>0.
\]

`x_cart`는 전자 Cartesian 좌표이며 핵 거리 x와 다르다. 정확한 항등식은

\[
\ell_O=\ell_B+\frac{x}{3}P,\qquad P=\Delta D.
\tag{1}
\]

운동량 P는 파동함수를 직접 미분해 계산하고, `Delta D`는 별도 검산량으로만 사용한다. A2.3, A2.12의 채택된 직접 유도는

\[
\ell_O=C_Ox+O(x^{-2}),\quad \ell_B=-C_Bx^{-2}+O(x^{-3}),
\quad C_O=\frac{32\sqrt2}{243},\quad C_B=\frac{128\sqrt2}{729}.
\tag{2}
\]

따라서 이번의 서로 다른 두 관측량은

\[
Q_O=\frac{\ell_O}{x}=C_O+O(x^{-3}),\qquad
Q_B=-x^2\ell_B=C_B+O(x^{-1}).
\tag{3}
\]

`C_O=0.1862338847569508…`, `C_B=0.2483118463426011…`이다. 특히 A2의 양의 `+i hbar C_B/x²`는 여기의 음의 ell_B와 같은 부호다. A2는 ell_O의 전체 `x^-2` 계수를 계산하지 않았으므로 그 계수를 `-C_B`로 동일시하면 안 된다. 식 (1)에서 P의 `O(x^-3)` 보정도 ell_O의 `O(x^-2)` 항에 기여한다.

A2의 유도는 fixed-sector 고립 고유상태, He 중심 polarized quasimode, 원격 Coulomb 특이점 안팎 분할, H¹ remainder와 Hardy bilinear torque bound를 사용했다. H1s와 He n=2의 전공간 퇴화가 이 두 sector ground gap을 0으로 만들지는 않는다. 그렇다고 이번 두 상태 계산으로 rank-5 cluster 또는 continuum을 검증하는 것은 아니다. 식 (2)의 Big-O 상수와 적용 반경은 수치적으로 알려져 있지 않다.

## 2. 이미 존재하는 scalar 증거

C2b `evidence/RECONCILED_GRID.json`의 direct 값과 h/p/tail 차이를 재사용했다. 각 계산을 재실행하지 않았다.

| x | Q_O | Q_B | Q_O−C_O | Q_B−C_B | 최대 h/p/tail Q_B 차이 |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.1835194514565239 | 0.2840449521010721 | −2.71443330043e−3 | 3.57331057585e−2 | 2.62684318741e−12 |
| 8 | 0.1860561418326787 | 0.2516600016020830 | −1.77742924272e−4 | 3.34815525948e−3 | 8.77858896686e−12 |
| 16 | 0.1862615195970930 | 0.2487577174038179 | +2.76348401422e−5 | 4.45871061217e−4 | 3.63546692750e−11 |

Q_O의 편차는 이미 8과 16 사이에서 부호가 바뀐다. signed 접근 방향이나 일정한 contraction을 acceptance로 고정할 근거가 없다. x=16에서 부모 네 profile의 최대 `x²*|ell_B(direct)−ell_B(force)|`는 `3.81017994933e−11`, 최대 `x³*|P−Delta D|/3`은 `6.65143791897e−10`이었다. 이는 새로운 x=32,64의 수렴을 보장하지 않는다. 상속된 direct quadrature는 부모의 두 order 검증이며, 새 세-order plateau로 소급해서 표현하지 않는다.

## 3. 사전등록을 권고하는 수치 기준

새 scientific 지점은 x=32,64 두 점이다. 4,8,16은 저장된 증거를 재사용하고 x=128은 이번에 실행하지 않는다. 같은 x의 h/p/tail, 독립 operator lane, 연속 quadrature 증가량을 각각 비교한다. 원래 C2a raw cap과 아래 scaled cap을 **동시에** 만족시킨다.

| 검증량 | Q_O cap | Q_B cap |
|---|---:|---:|
| h/p/tail 각각의 차이 | 2e−6 | 2e−6 |
| direct–force 차이 | 1e−7 | 1e−7 |
| 연속 두 quadrature 증가량 각각 | 1e−8 | 1e−8 |
| native/reference 차이 | 1e−8 | 1e−8 |
| 원점 identity 전파량 | 1e−7 | 1e−7 |
| momentum identity 전파량 | 1e−7 | 1e−7 |

에너지 `1e−8`, norm `1e−10`, algebraic residual `1e−9`, dark `1e−12`, 원점 identity raw `1e−10`, 직접 운동량 identity raw `1e−7` 등의 기존 기준도 유지한다. 독립 B-centered spherical anchor를 실행한다면 scaled agreement `1e−4`, 기저 마지막 increment `2e−5`, quadrature `1e−6`를 두 Q 각각에 권고하며 부모의 해당 raw cap도 AND로 적용한다. 독립 앵커 기준은 주 prolate 수렴 기준보다 느슨한 별도 표현 검산이다.

Q_O의 오차는 `delta ell_O/x`, Q_B의 오차는 `-x² delta ell_B`다. 큰 x에서는 Q_B가 더 엄격한 요구를 한다.

| x | Q_B spatial에서 허용되는 raw ell_B 차이 | direct–force raw 차이 | quadrature raw 증가량 | momentum identity의 raw P 차이 |
|---:|---:|---:|---:|---:|
| 16, 재사용 | 7.8125e−9 | 3.90625e−10 | 3.90625e−11 | 7.32421875e−11 |
| 32 | 1.953125e−9 | 9.765625e−11 | 9.765625e−12 | 9.1552734375e−12 |
| 64 | 4.8828125e−10 | 2.44140625e−11 | 2.44140625e−12 | 1.1444091796875e−12 |

마지막 열은 다음 절의 `x³/3` 전파에서 나온다. base의 `root_xtol=2e−12`를 그대로 두면 root tolerance가 이 identity를 제한할 가능성이 있다. 새 상태의 root tolerance를 실행 전에 `2e−14`로 강화하는 것이 합리적이다. 이것은 허용오차 완화나 고정밀도 사용을 주장하는 것이 아니며 binary64의 실제 plateau는 결과로 확인해야 한다. 같은 x에서 실패하면 사전등록한 tighter solve/refinement까지만 허용하고 기준을 사후 완화하지 않는다.

이 cap은 경험적 discrepancy 기준이다. h/p/tail 차이, 적분 증가량, 작은 algebraic residual은 continuum error enclosure가 아니다. 두 Q의 유한 R 편차는 각각의 **관측된** 수치 spread보다 충분히 클 때 해석한다. 기준에 통과했다는 이유만으로 cap보다 작은 유한 R 보정의 정확한 차수까지 읽어내지 않는다.

## 4. 원점 상쇄와 안정적인 force 표현

원점 불일치 `I=ell_O−ell_B−xP/3`와 운동량 불일치 `J=P−Delta D`의 전파량은

\[
\epsilon_{I,O}=|I|/x,\quad \epsilon_{I,B}=x^2|I|,
\qquad\epsilon_{P,O}=|J|/3,\quad\epsilon_{P,B}=x^3|J|/3.
\tag{4}
\]

이들을 raw I,J와 함께 저장한다. 단순히 scaled ell_B와 scaled ell_O의 차이를 비교하는 것이 아니다. ell_B를 두 큰 최종 scalar의 차이로 재구성하는 경우의 상쇄 지표는

\[
\chi_B=\frac{|\ell_O|+|(x/3)P|}{|\ell_B|}
\sim\frac{2C_O}{C_B}x^3=\frac32x^3.
\tag{5}
\]

leading 값은 x=32에서 49152, x=64에서 393216이다. 부모 x=16의 실제 지표는 6134.8976으로 leading 6144와 가깝다. 따라서 `ell_B=ell_O−xP/3`를 주 계산 경로로 삼지 않는다. B 원점의 직접 미분 integrand와 아래의 force 표현을 각각 사용하고 식 (1)은 검산으로 둔다. `unit_roundoff*chi_B`는 이 scalar 차감의 척도이며 전체 eigensolve·파동함수 평가·적분의 roundoff enclosure가 아니다.

무차원 `T_C=a_A²<g,x_cart/r_C³ b>`라 하면 정확한 torque 관계는

\[
\ell_O=\frac{2x(T_B-T_A)}{3\Delta},\qquad
\ell_B=-\frac{xT_A}{\Delta},\qquad
Q_O^F=\frac{2(T_B-T_A)}{3\Delta},\qquad
Q_B^F=\frac{x^3T_A}{\Delta}.
\tag{6}
\]

큰 R에서 `T_B→16/(27sqrt(2))`, `T_A=D_infinity/x³+O(x^-4)`, `D_infinity=64sqrt(2)/243`, `Delta→3/2`이다. 따라서 (6)은 (3)의 두 계수를 재현한다. Q_B의 force 경로는 작은 양의 T_A만 적분하므로 O(x) 크기의 scalar 둘을 빼지 않는다. T_A 자체가 작아도 양의 sector ground meridional 진폭에서는 그 적분의 물리적 sign cancellation이 없다. 다만 실제 기저 평가의 roundoff와 공간·적분 오차는 별도다. O 경로의 `(abs(T_B)+abs(T_A))/abs(T_B−T_A)`는 큰 R에서 1로 접근한다.

유한 차분으로 `U=T_B−T_A`, `Delta_hat=Delta+delta Delta`라 쓰면

\[
\widehat Q_O^F-Q_O^F=\frac23\left(
\frac{\delta U}{\widehat\Delta}-\frac{U\delta\Delta}{\Delta\widehat\Delta}\right),\qquad
\widehat Q_B^F-Q_B^F=x^3\left(
\frac{\delta T_A}{\widehat\Delta}-\frac{T_A\delta\Delta}{\Delta\widehat\Delta}\right).
\tag{7}
\]

실제 상한 `e_U,e_T,e_Delta`가 있고 `e_Delta<Delta`라면 각 우변 절댓값은 삼각부등식과 `Delta−e_Delta`로 제한된다. 현재의 q/h/p 차이는 그러한 엄밀한 상한이 아니다. 특히 Q_B의 상대 force 오차는 1차에서 `delta T_A/T_A−delta Delta/Delta`이며, 작은 T_A를 기록하지 않고 LO 오차만 통과시키면 intrinsic coupling을 검증한 것이 아니다.

## 5. 물리 영역·angular 분해능·위상

solver의 `radial_extent=L`은 xi_max 자체가 아니다. 좌표는

\[
\xi_{\max}=1+2L/x,\quad
\rho=\frac{x}{2}\sqrt{(\xi^2-1)(1-\eta^2)},\quad
z=\frac{x}{2}\xi\eta-\frac{x}{6}.
\tag{8}
\]

경계 타원체는 midpoint `−x/6`를 중심으로 반장축 `L+x/2`, 반단축 `sqrt(L(L+x))`를 가진다. B focus에서 경계까지의 최소 거리는 모든 x에서 정확히 L이다. 이는 경계의 B-focus 거리 `(x/2)(xi_max−eta)`가 eta=1에서 최소이기 때문이다. 따라서 L=30을 유지해도 B 원자 주위의 물리적 상자가 큰 R 때문에 작아지지 않는다. 작은 R 문서의 O 중심 최소 거리 식을 x>L인 이번 경우에 연장하지 않는다. tail 검산은 내부 radial proxy `y=(x/2)(xi−1)=L(j/Nr)²` 셀을 유지한 채 L=40까지 바깥 셀을 추가한다.

He B 근처의 고정 원자 크기에서는 `1−eta=O(a_B/R)`이다. uniform eta cell의 물리적 축 방향 크기는 대략 `R/Neta`이므로 Neta=40 고정은 x 증가에 따라 분해능을 잃는다. 이번 설계의 `Neta=ceil(2.5x)`는 부모 x=16,Neta=40의 물리적 cell 폭을 유지한다. 새 scientific base의 Neta는 80,160이고 h는 120,240이다. h는 radial 및 angular 분해능을 함께 높이며 p는 같은 mesh에서 degree를 높인다. 원자 폭 유지가 고차 기저 수렴의 증명은 아니므로 각 quartet의 검산을 요구한다. Dense angular eigensolve의 대략적인 O(Neta³) 비용과 tensor 관측량 O(Nr*Neta*q²) 비용을 구별하고, 관측량은 patch streaming으로 peak memory를 제한한다. 실제 시간 단축과 NCP64 scaling은 측정하기 전 주장하지 않는다.

기존 `_Axis.lowest`는 첫 angular cell midpoint, 즉 A 쪽에서 고유벡터의 부호를 정했다. 큰 R에서는 그 값이 He 국소화에 의해 지수적으로 작아져 부호가 roundoff에 민감해진다. 정확한 lowest regular Sturm–Liouville eigenfunction은 내부 node가 없으므로, 조립 node 또는 mesh midpoint 중 **절댓값이 최대인 regular eigenfunction 값**이 양수가 되도록 부호를 정하면 기존 양의 meridional convention과 수학적으로 같다. global coefficient 최대값의 부호만 읽기보다 실제 collocation 값을 사용하고, 선택 probe와 값, 변경된 전체 부호를 metadata에 기록한다. 양의 국소화 영역의 phase와 물리 overlap을 따로 확인한다. 작은 음의 먼 tail 값만으로 phase를 정하지 않는다.

## 6. Common-O continuation과 실행 중단 경계

같은 O 좌표에서 x가 바뀌면 B 중심이 `delta x/3`만큼 이동한다. 따라서 dyadic 16→32→64 간격의 physical overlap이 작아지는 현상을 state crossing이나 잘못된 phase로 바로 해석할 수 없다. 예를 들어 16→32만으로도 B 중심이 `16/3 a_A` 이동하여 He 원자 크기보다 훨씬 크다. 이번 선택은 관측량 정의를 바꾸지 않고 **16,18,…,64의 간격 2 common-O bridge**를 사용하는 것이다. 각 단계 B 중심의 이동은 `2/3 a_A`다. 이는 `.5` overlap 기준 통과 가능성을 높이는 설계일 뿐 결과를 보장하지 않는다.

새 base pair는 24개, 두 scientific endpoint의 h/p/tail을 더하면 총 30 pair다. 중간 bridge의 base 값만으로 그 점의 h/p/tail 수렴을 주장하지 않는다. 각 bridge에서 m=0,1의 signed physical overlap, 자기 norm, 양방향 일치와 연속 두 q increment를 확인하고 부모 16의 phase에서 연결한다. 부족한 overlap 크기를 절댓값 또는 별도 B-comoving inner product로 바꿔 통과 처리하지 않는다. 등록한 적분 fallback으로도 실패하면 `STATE_TRACKING_AMBIGUOUS` 또는 명시한 대응 중단 상태로 보존한다.

권고 최소 fallback은 실패한 **scientific endpoint**만 하나의 완결된 finer quartet로 재계산하는 것이다. 예를 들어 d9/q14, Nr96, Neta=ceil(3.75x)를 finer base로 두고, 그 내부 h/p/tail 비교를 다시 수행한다. 초기 quartet는 보존하고 처음→finer base 차이도 보고한다. frozen-state quadrature 실패는 고유값을 다시 풀기 전에 등록한 추가 두 order로만 검사한다. phase·parsing·ABI 등 구현 오류, memory·timeout 등 실행환경 오류, 공간·적분 수치 미수렴, 물리·수학 항등식의 불일치를 서로 다른 실패 범주로 남긴다.

## 7. 허용되는 결론

이번의 성공은 등록한 두 큰 R 지점에서 두 원점의 raw+scaled 수치 검증과 common-O bridge가 통과했다는 유한 수열 결과다. `Q_O−C_O`, `Q_B−C_B`, 각각 `x³*(Q_O−C_O)`, `x*(Q_B−C_B)`를 진단으로 기록할 수 있다. 후자의 두 값이 일정해야 한다거나 편차가 단조 감소해야 한다는 gate는 두지 않는다. Big-O는 leading correction의 비영성·부호·단조성·최적 차수를 정하지 않는다.

해석적 상수와 적용 반경의 미지, 연속공간 오차 enclosure 부재, 아직 다루지 않은 rank-5 cluster 및 collision 범위를 이 계산으로 해소했다고 하지 않는다. `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. x=128, collision evolution, cross section, NCP64 실제 scaling은 이번 수학 설계로 실행 승인되거나 검증되지 않는다.

## 읽은 근거

- C2c `provenance/A2_ASYMPTOTIC_DERIVATION_KO.md`, 특히 A2.1, A2.3, A2.9–12 및 큰 R momentum 설명: 채택된 derived asymptotics.
- C2c `math/SMALL_R_ERROR_CONTRACT_KO.md`: 단위, 원점, 독립 lane, 물리 box의 기존 정의.
- C2a `math/OPERATOR_DERIVATION_KO.md`, `CONTRACT.json`, `reference/spheroidal_tail.py`, C2c `code/prolate_fast.py`, `code/force_integral.py`: 현재 computational form과 phase·mesh 구현.
- C2b `evidence/RECONCILED_GRID.json`: 부모 x=4,8,16의 scalar 증거. 새 물리 계산 없이 JSON 연산만 수행.

이 문서에는 새 문헌상의 주장을 추가하지 않았다. 새 오차 전파·상쇄·mesh scaling 설명은 위 정의로부터의 직접 유도이며, 실제 구현 채택 여부와 새 numerical PASS 여부는 실행 산출물이 소유한다.
