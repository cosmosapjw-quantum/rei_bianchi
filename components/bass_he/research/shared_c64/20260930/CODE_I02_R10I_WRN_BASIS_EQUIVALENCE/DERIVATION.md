# R10I: CPC Eq.(47)의 molecular-axis parity 축약

## Source statements

- CPC Eq.(47)의 clean-room signed 공간 구현은 `src/arseny_reimpl/rotational.py`의 `_hamiltonian` 및 `src/bass_he/rotation.py`이다. 작은 R에서 각운동량의 dimensionless signed 공간은 m=-l,...,+l이다.
- Hash-pinned distributed author `arseny.f` SHA256 `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`의 SECTION lines 1913-1962는 `WRN(AR,l+1)`을 초기 m=0,...,MI 열마다 호출하고 `PR(final,initial)=|AR|²`를 사용한다. DERIVS lines 2033-2070의 첫 결합계수는 `sqrt(l(l+1)/2)`이고 m>=1 인접 결합은 `sqrt((l-m)(l+m+1))/2`이다. 이 원문은 읽기 전용으로 사용했고 실행·복사하지 않았다.
- 같은 원문의 DERIVS line 2059는 l=1에서 계수가 0인 `Y(3)`을 식에 적는다. 실제 배열 경계/평가 동작은 저자 실행 없이 판정하지 않는다. 이 audit은 명시된 수학적 계수와 행렬 의미의 정적 판정이다.

## Independent derivation

CPC Eq.(47)을 `i dA/dt = [epsilon R² J_x² - dot(theta) J_z] A`로 쓴다. 정규화된 Wigner 회전 `V=exp(-i pi J_y/2)`를 molecular-axis eigenbasis의 위상 선택으로 사용하면

`V† J_x V = M = diag(-l,...,l)`, `V† J_z V = -J_x`.

부호가 반대인 충돌평면 배치는 diagonal gauge `D_mm=(-1)^m`로 연결된다. `D J_x D=-J_x`, `D M² D=M²`이고 최종 확률은 gauge 위상에 불변이다. 이 관계를 l=1,2에서 행렬로 검사했다.

이 위상 선택 후 유효 signed molecular-m 생성자는 `H = alpha(s) M² - beta(s) J_x`다. 직선 경로의 `x=vt`, `R²=x²+rho²`에서 `alpha=epsilon R²/v`, `beta=rho/R²`이다. Coulomb 경로의 `R=a+sqrt(a²+rho²)cosh(eta)`에서는 `alpha=epsilon R³/v`, `beta=rho/R`이다. Coulomb의 `dtheta/deta=rho/R`로 나누면 author DERIVS와 같은 `d=epsilon R⁴/(rho v)` 및 단위 `-J_x` 결합형이 된다. 이 등식은 궤적·gauge 변환이며 author FORTRAN 실행의 동등성 주장은 아니다.

반사 연산 `m -> -m`과 H는 교환한다. `|e_m>=(|+m>+|-m>)/sqrt(2)`, `|o_m>=(|+m>-|-m>)/sqrt(2)` 및 `|0>`으로 나누면

- even m=0,...,l: diagonal `alpha m²`, `K(0,1)=sqrt(l(l+1)/2)`, `K(m,m+1)=sqrt((l-m)(l+m+1))/2` for m>=1;
- odd m=1,...,l: 같은 diagonal 및 m>=1 인접 결합;
- 두 블록 사이 결합은 0이다.

`beta=1`, `alpha=d`, l=1이면 `H_even=[[0,-1],[-1,d]]`, `H_odd=[[d]]`다. l=2이면 even offdiagonal은 `-sqrt(3),-1`, odd offdiagonal은 `-1`이다. DERIVS의 l+1 진폭/계수는 이 **even** 블록에 대응한다.

## Probability map and resolved warning

`U_e`, `U_o`를 각 parity 진폭 행렬로 쓰면 author nonnegative-m 행렬은 `P_WRN(n|m)=|(U_e)_{nm}|²`다. Clean signed-m 비간섭 collapse의 결과는

- `P_clean(0|0)=|U_e(0,0)|²`;
- `P_clean(n>0|0)=|U_e(n,0)|²`;
- `P_clean(0|m>0)=|U_e(0,m)|²/2`;
- `P_clean(n>0|m>0)=(|U_e(n,m)|²+|U_o(n,m)|²)/2`.

따라서 전 행렬은 일반적으로 다르다. l=1에서 initial |m|=1 -> final m=0은 author even 확률의 절반이다. 그러나 **initial m=0 열은 정확히 같다.** 원 R10H의 factor-two warning은 이 full-matrix 방향에서는 성립하지만, 현재 초기상태가 소비하는 열에 자동 적용되지는 않는다.

현재 Eq50 approach 순서에서 초기 index 2의 가능 support는 `{2}->{2,7}->{2,7}->{0,2,7}->{0,2,7}->{0,2,5,7}`이다. Nmax=3의 m>0 인덱스 `{3,6,8,9}`는 pre-rotation에 도달하지 않는다. 이 정적 도달성은 저장 Delta 값이나 회전 적분 오차에 의존하지 않는다. 이후의 non-equivalence는 새로운 초기상태/branch/event topology에서는 효과를 낼 수 있다.

## Numerical boundary

사전 고정 R10G 소비 rho 300개 중 active 질의 3270개를 검사했다. 각 질의는 straight/Coulomb, CPC/author cutoff, E=0.5/5 keV/u, (N,l)=(2,1),(3,1),(3,2)를 포함한다. Author-even 및 clean signed 각각 low/high step과 unitarity/stochasticity를 통과했다. Full-matrix 최대 확률 차이는 `0.4997281277454655`; parity even+odd를 collapse한 값과 clean signed 값의 최대 차이는 `1.3933298959045715e-13`이다.

Worst query는 Coulomb/CPC, E=0.5, N=3,l=1, rho `0x1.9afbb98f335bcp-4`, final m=0 / initial m=1이다. 별도로 코딩한 signed full DOP853과 reduced even DOP853의 amplitude 차이는 `7.309742140011427e-14`; DOP 확률의 author-clean 차이는 `0.4997281277455441`이다. 이는 구현 표현 검사이지 독립 물리 인증이 아니다.
