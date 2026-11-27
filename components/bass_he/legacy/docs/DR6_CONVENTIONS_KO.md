# DR6 Eq. (47) rotational ODE convention lock

정체성:

- `PAPER_DERIVED_REIMPLEMENTATION`
- `NOT_AUTHOR_CODE`
- `AUTHOR_WRN_MODKG_IDENTITY_NOT_CLAIMED`

## 출판된 식

CPC §2.6 Eqs. (47)-(48):

```text
i dA/dt = [ epsilon R(t)^2 Lx^2 + omega(t) Lz ] A

epsilon = 6 Z1 Z2 (Z1+Z2)^2 /
          [ N^3 l(l+1)(2l-1)(2l+1)(2l+3) ]
```

Hilbert space 차원은 `2l+1`; 논문은 even/odd z-projection 사이의 전이가 없다는 selection rule을 명시한다.

## 이 clean-room 구현에서 추가로 고정한 derived conventions

1. 논문 §2의 직선궤도 `R=(vt,rho,0)`를 사용한다.
2. `theta=atan2(rho,vt)`이므로 `omega=dtheta/dt=-rho*v/R^2`로 둔다.
3. Eq. (47)은 small-R 식이고 논문은 rotational transition이 approach의 S-series 이후부터 receding의 S-series까지 일어난다고 서술한다. 기본 integration boundary는 Eq. (36)의 `S_{l,sigma}` (`m=0`) limit-point 실수부:

   `R_rot = Re R_inf(l,m=0)`.

   이는 generic transparent boundary policy이며 hidden author-WRN boundary와 동일하다고 주장하지 않는다.
4. ODE는 signed `m=-l,...,+l` basis에서 푼다. Eq. (49)의 `|m|` state basis로 옮길 때는 unresolved ±m pair를 equal incoherent mixture로 보고 final ±m을 합하는 degeneracy adapter를 쓴다.
5. main integrator는 Hermitian midpoint exponential(Magnus-2)이라 각 step이 unitary다. 독립 auditor로 fixed-step RK4를 같이 계산한다. 저자 WRN의 RKF-45와 implementation identity를 주장하지 않는다.

## claim gate

DR6에서 닫을 수 있는 것:

- Eq. (47)-(48) operator의 독립 구현
- normalization/unitarity
- even/odd `m` selection rule
- numerical step convergence
- derived `|m|` probability block과 Nmax=3 block-diagonal `P_rot`

DR6만으로 닫지 않는 것:

- 저자 `WRN/MODKG`와 numeric identity
- low-energy curved nuclear trajectories
- hidden-crossing support semiwidth Eq. (52)
- full branch enumeration
- Eq. (50)+(54) end-to-end cross section
- BASS CT2 production promotion
