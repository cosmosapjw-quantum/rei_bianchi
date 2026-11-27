# HE37 pure-H CI net source adapter

Le–Cambier Eq.85의 energy sharing과 §III.E의 등방 outgoing 모델을 실제 number/heat/STF 사건 장부에 연결한다. `h1_net/lc_ionization.py`와 HE36 세 dependency는 원본과 byte-identical이며 `DONOR_PROVENANCE.json`에 source SHA256과 Git pin이 있다. 이 패키지는 NumPy·SciPy가 있는 sandbox에서 실행되며 import는 연구 사례를 계산하지 않는다.

## 계약

`h1_ci_source(T_K, Y21, nb_m3, electron_pi_Pa, *, thermal_inventory_scope, charge_census_scope)`를 호출한다. 입력은 다음과 같다.

| 입력 | 정의 |
|---|---|
| `T_K` | scalar electron temperature, numerical domain2000–200000K |
| `Y21` | HE32 ordering의 `n_species/n_b`; H0 index1, H+ index2, 다른19종0; Y1+Y2=1 |
| `nb_m3` | baryon density≥0, m⁻³ |
| `electron_pi_Pa` | symmetric trace-free3×3 **전자** pressure tensor, Pa |
| thermal scope | `ALL_RETAINED_THERMAL`의 명시적 채택 |
| charge census | `NEUTRAL_21_STATE_CENSUS`의 명시적 채택 |

Pure-H charge neutrality로 `ne=nb*Y2`, `nH=nb*Y1`를 계산한다. 전체 gas stress를 전자 stress로 간주하는 분배는 하지 않는다. `electron_grad_relative_norm=||pi_e||/(ne kBT)`는 입력 방향의 크기이며 유한 Grad PDF의 양성성이나 closure 정확도를 인증하지 않는다. 모델은 infinitesimal first variation이다.

Source-native `I=13.6eV`를 사용한다. CCC rate/threshold, isotope correction, finite-mass reaction kernel을 조합하지 않는다. 생성 전자가 빠르게 열화한다는 과학적 증명은 제공하지 않으며 all-thermal 선언은 이 adapter의 조건이다. Heavy H→p kinetic pressure는 recoil-free leading order에서 종 사이에 운반되어 합에서 상쇄된다. 유한 proton recoil은 후속이다.

## 식과 코드 대응

`LCModel.evaluate(T)`에서 같은 differential kernel의 α,β,γ,κ₂=4γ/(15(kBT)²)를 공급한다. 단위는 α·κ₂=m³/s이다.

```text
r = ne nH alpha                                [events/(m³ s)]
R_H=-r, R_p=R_e=R_part=+r, R_nucleus=0           [m⁻³ s⁻¹]
Q = -I r                                      [W/m³]
J = -nH kappa2 pi_e                            [Pa/s]
S = 2Q/3 Id + J                                [Pa/s]
per-event S = -2I/3 Id - (kappa2/alpha)(pi_e/ne) [J/event]
```

원래 생성 전자 두 개의 열은 사건당 `E-I`이고 입사 전자의 제거 열은 `-E`이다. net energy ledger는 `dI=+I`, `dEth=-I`, 나머지 reservoir0이다. `Q`와 `reservoir_sources_W_m3['dEth']`는 같은 열 source의 두 표현이므로 더하지 않는다. 순 source tensor는 부호를 가지며 음의 고윳값을 clipping하지 않는다.

양의 reactant 상태에서 unchanged `ResolvedEvent`와 `attach_event_tensor`를 실제 호출한다. 기존 REI class에 독립 자유전자 reactant가 없으므로 H0→H+의 effective unary hazard `ne*alpha`[s⁻¹]를 현재 상태에서 고정한다. H+를 가상의 촉매 reactant로 넣지 않는다.

## Jacobian 두 종류

`event_row_frozen_ne`의 gradient/Jacobian은 현재 ne가 고정된 unary event 미분이다. 이름과 `donor_jacobian_scope`에 그 한계를 명시했다. 이를 결합 population ODE의 전체 state Jacobian으로 사용하지 않는다.

`physical_abundance_jacobian_s`는 고정 T,nb에서

```text
F_H=-nb alpha Y_H Y_p,  F_p=+nb alpha Y_H Y_p
```

를 미분한다. 두 nonzero열은 Y_H와 Y_p이며 `∂ne/∂Y_p=nb`가 포함된다. Pure-H normalization의 admissible tangent는 `dY_H+dY_p=0`이다. 반환된21×21 matrix는 H0/H+ 두 변수 polynomial의 ambient extension이고, 다른 종 방향은 이 모델의 적용 범위 밖이다. T derivative는 포함하지 않는다.

## Zero와 numerical representability

`ZERO_ELECTRON`, `ZERO_TARGET`, `ZERO_DENSITY`는 실제 reactant/density zero 상태를 뜻한다. 이때 알려진 net source는0이며 undefined `pi_e/ne`나 positive-coefficient construction을 수행하지 않는다. `event_tensor_source`와 `event_row_frozen_ne`는 `None`이다. Zero-electron activation Jacobian과 zero-target derivative는 보존한다. `ne=0`인데 `pi_e≠0`이면 오류다.

`nb=0`이면 thermal temperature의 시간미분은 정의하지 않아 `dot_T_reaction_K_s=None`을 반환한다. 빈 공간의 반응0을 온도 evolution0으로 오인하지 않는다. 양의 밀도와 zero reaction에는 Tdot0을 반환한다.

양의 source가 binary64에서0으로 underflow하거나 overflow하면 실패한다. 물리적 support zero로 바꾸지 않는다. 부울값/복소값/비유한값/다른 종/부정확한 normalization/비대칭 또는 trace가 있는 stress는 거부한다. 배열과 반환 energy mapping은 immutable이다. 작은 STF가 큰 isotropic source에서 subtraction으로 소실되지 않도록 직접식의 `J`를 반환하며, donor projection과 source-scaled roundoff 검사를 함께 수행한다.

## 조건부 instantaneous temperature

Reaction-only, non-expanding, all-retained common thermal pool을 선택하면

```text
Tdot = -(r/npart) [T + 2I/(3kB)],  npart=nb(Y_H+2Y_p).
```

Particle-number 증가 항은 이 온도식에만 들어가며 heat ledger에 중복하지 않는다. 이 수치는 instantaneous closure의 결과이며 본 단원에서 IVP를 실행하지 않았다.

## 사용 예시

```python
import numpy as np
from h1_net import h1_ci_source, ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS

Y = np.zeros(21)
Y[1], Y[2] = 0.7, 0.3
source = h1_ci_source(
    20000.0, Y, 1e6, np.zeros((3,3)),
    thermal_inventory_scope=ALL_RETAINED_THERMAL,
    charge_census_scope=NEUTRAL_21_STATE_CENSUS,
)
```

## 실제 새 검사

`OPENBLAS_NUM_THREADS=1 python verify_net_bridge.py`의 최초 실행은7/7그룹 PASS다. Receipt는 `attempts/attempt_20261023T022026748127Z/RESULT.json`이다. 약0.060s이며 기존 과학 suite/IVP, 새IVP/render/benchmark는 모두0이다.

| 검증 | 결과 |
|---|---:|
| T2000/20000/200000K scalar heat/count/charge/baryon/trace | max normalized defect5.9952e−15 |
| 전자 STF 직접식·rotation·per-event trace | max relative1.1102e−16 |
| physical Jacobian pure-H tangent finite difference | maxrelative2.9018e−10<3e−9 |
| 명시적 zero 상태 |3개 PASS, activation derivative 보존 |
| 입력·scope 오류 |25개 거부 |
| 양의 underflow/overflow |2개 fail-closed |
| 별도 기존 thermal RHS 대조 | relative defect0 |
| 불변 결과 배열 |8개 확인 |

같은 입력·코드로 이 검사를 다시 실행할 필요가 없다. Named affected dependency가 바뀌면 `--groups <그룹명>`으로 영향을 받는 검사만 실행하고 기존 attempt를 보존한다.
