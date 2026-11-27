# DR7 convention lock: Eq. (52) support + scoped Eq. (50)

정체성:
- `PAPER_DERIVED_REIMPLEMENTATION`
- `NOT_AUTHOR_CODE`
- `AUTHOR_CR_SECTION_IDENTITY_NOT_CLAIMED`

## Eq. (52) support correction

이전 계획의 `Re Rc + Delta Rc` 표기는 원문 판독 오류였다. 출판된 Eq. (52)는

`rho <= Re(Rc) + Im(Rc)`

를 직접 쓰고, 바로 이어지는 문장에서 `Im(Rc)`를 non-adiabatic-coupling matrix
element의 semi-width라고 설명한다. DR7은 별도 fitted width를 만들지 않고 이 원문
cutoff를 그대로 사용한다.

## Eq. (52) / Eq. (55) factor-of-two

동일 논문에는 동시에 다음이 인쇄되어 있다.
- Eq. (52): `p_k = exp[-Delta_k(rho)/v]`
- Eq. (55): Q-series single-pass `P^Q = exp[-2 Delta/v]`

DR7은 이를 임의로 화해시키지 않는다.

Eq. (50) assembly의 main lane은 Eq. (52)를 문자 그대로 사용하며, 각 active branch
결과에 `p_eq52_literal`과 `p_eq55_singlepass=p_eq52_literal^2`를 동시에 기록한다.
Eq. (55) 값은 이 노드에서는 source-discrepancy diagnostic이다.

## Scoped branch registry

Appendix A의 Nmax=3 He2+ + H test에 인쇄된 5개만 사용한다.
- Q12: 1sσ ↔ 2pσ
- Q23: 2pσ ↔ 3dσ
- Qother: 2sσ ↔ 3pσ
- Qm1: 2pπ ↔ 3dπ
- S23: 2pσ ↔ 3pσ

Eq. (50)에 따라 Re(Rc) 증가 순으로 정렬한다.

Nmax=3 upper shell로 끝나는 branch는 Eq. (53) absorbing block을 쓰며, Q12만
Eq. (51) bound-bound block이다. DR6의 derived P_rot를 Eq. (50) 중앙에 삽입한다.

## 이 노드에서 주장하지 않는 것

- complete branch enumeration
- Eq. (52)/(55) factor-of-two source discrepancy 해결
- author CR_SECTION identity
- Eq. (54) impact-parameter integrated cross sections
- BASS CT2 production promotion
