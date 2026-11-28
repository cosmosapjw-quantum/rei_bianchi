# HE38 유한질량 H1 kernel

원전 Le–Cambier2016 Eq2–7/85의 Jacobi 좌표와 §III.E의 uniform G를 명시적으로 채택한 모델이다. Common T/common bulk와 독립적인 infinitesimal electron/H0 STF first variations를 다룬다. 실제 H1 angular calibration, 유한 비등방 분포의 closure, coupled IVP는 포함하지 않는다.

## 공개 API

`h1_finite_mass.FiniteMassModel().evaluate(T)`는 scalar 또는 nonempty1D 배열을 받고 N개의 온도에 대한 결과를 반환한다. 온도 numerical contract는2000–200000K다.

- `moments_SI`: (N,4), alpha/beta/gamma/delta. Byte-preserved HE37 LC arithmetic donor에 sqrt(me/mu)=zeta^(-1/2)만 적용한다.
- `kappa1_m3_s`, `kappa2_m3_s`, `sharing_moment_J_m3_s=beta-theta*alpha`.
- `first_jacobi_energy_moment_J_m3_s=theta*alpha`.
- `heat_per_pair_J_m3_s`: (N,3), e/H0/p 순서. `ne*nH`를 곱하면 volumetric heat다.
- `heavy_heat_per_pair_J_m3_s`: 작은 H0+p 합의 직접 식. 개별 큰 항을 빼지 않는다.
- `stf_coefficients_m3_s`: (N,3,2), 출력 e/H0/p, 입력 electron/H0 순서. 열0에는 nH, 열1에는 ne를 곱한 후 해당 입력 STF에 작용시킨다.
- `identity`와 `energy_mapping`은 새 finite-mass 모델 소유다. 내부 donor의 heavy-target metadata를 공개 모형 metadata로 사용하지 않는다.

`finite_mass_source(T,ne,nH,pi_e,pi_H,linear_response=True)`는 종별 number/heat/STF/pressure source, direct totalQ/J/S, direct heavyQ와3×2 response를 반환한다. 양의 density에서 normalized STF 크기를 진단값으로 보고하며, 이를 유한 Grad 분포의 positivity 보증으로 해석하지 않는다. 실제 pressure tensor를 보정·투영·clipping하지 않는다.

`event_kinematics(v_e,v_H,upsilon_eV,direction_g1,direction_g2,ion_mass_kg=MP_KG)`는 원전 Eq4의 개별 사건을 구성한다. 입력 directions는 unit vector여야 하고 코드가 정규화하지 않는다. E는 입력 velocities의 reduced-mass relative energy, Upsilon은 원전 Jacobi energy-transfer variable이다. E>I 및 I<=Upsilon<=E가 필요하다. 다른 ion mass는 `artificial_ion_mass_kinematic_control_only`로 표시한다. 이 선택은 production finite-mass model의 파라미터가 아니다.

`h1_ci_source(T,Y21,nb,pi_e,pi_H,thermal_inventory_scope=...,charge_census_scope=...,linear_response=True)`는 기존 HE36 event adapter와 REI event class를 연결한다. Pure-H21 H0/H+ slots는1/2이고, 나머지 slot은0, YH+Yp=1, ne=nb*Yp다. 다음 scope 상수를 명시해야 한다.

```python
import numpy as np
from h1_finite_mass import h1_ci_source, ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS
y=np.zeros(21); y[1]=0.6; y[2]=0.4
out=h1_ci_source(2e4,y,1e6,np.zeros((3,3)),np.zeros((3,3)),
    thermal_inventory_scope=ALL_RETAINED_THERMAL,
    charge_census_scope=NEUTRAL_21_STATE_CENSUS,linear_response=True)
```

`physical_abundance_jacobian_s`는 고정T,nb에서 ne(Yp)를 미분한다. Pure-H normalized manifold에서는 dYH+dYp=0 방향만 사용할 수 있다. `frozen_ne_abundance_jacobian_s` 및 `event_row_frozen_ne['jacobian']`는 unary donor의 고정ne Jacobian이다. Temperature와 STF derivative는 이 Jacobian에 포함되지 않는다.

**과학적 STF 출력의 기준 필드는 wrapper `J` 또는 `species.total_J_Pa_s`다.** `event_tensor_source`는 변경하지 않은 donor의 audit snapshot을 보존한다. 그 안의 `event_tensor_source.J`는 기존 HE36의 trace subtraction으로 얻은 값이므로, isotropic 부분보다 매우 작은 STF가 roundoff로0이 될 수 있다. STF를 사용하는 계산·검증·그림은 wrapper의 direct `J` 또는 `species.total_J_Pa_s`를 읽어야 한다. Nested donor output은 rate/energy/tensor 연결과 기존 projection roundoff를 확인하는 audit 자료로 유지한다.

`species.total_Q_W_m3`, wrapper `Q`, donor reservoir `dEth`는 같은 물리량의 표현이다. 합하여 두 번 가산하면 안 된다. 직접 식과 donor 로그 rate 사이의 binary64 roundoff를 비교하여 일치 gate를 검사한다. Scalar heat를 STF projection에서 재구성하지 않으며 tinySTF는 direct `J`를 사용한다. Common retained thermal pool이라는 명시적 조건에서만 reaction dotT를 제공한다.

## 보존과 입력 계약

Native 모델은 mp=1.67262192595e−27kg, me=9.1093837139e−31kg, mH=mp+me의 Newtonian mass-additivity를 채택한다. Source threshold13.6eV는 internal-energy ledger에 한 번만 들어간다. 원전 Eq48의 표시 부호가 아니라 Eq2c의 사건 보존식으로 totalQ=−I*rate를 정한다.

Bool(혼합 Python list 포함), complex, string/object, NaN/Inf, 잘못된 shape, 음의 density, 비대칭/nontraceless STF를 거부한다. 반응물이 없으면 해당 종의 STF도0이어야 한다. 알려진 zero-reactant source와 양의 양이 계산상 underflow하여 사라진 경우를 구별한다. 후자는 representability error다. 결과 dataclass는 frozen이고 모든 반환 배열은 bytes-backed immutable storage다.

Scalar moment/heat/STF계수는 새로운 finite-mass algebra다. 기존 LC provider, HE36 reactive_moments/event_bridge, REI source lift는 변경 없이 vendor했다. 정확한 source/destination hashes는 `DONOR_PROVENANCE.json`에 있다.

## 실행한 affected controls

실행 명령:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_affected.py
```

첫 실행은107controls PASS다. 실제 process metadata와 입력 source SHA256은 `attempts/attempt_20261023T035118251745Z/START.json`, 결과와CPU/RSS는 같은 디렉터리의 `RESULT.json`에 보관했다. CPU0.918811231s. 기존 suite/IVP 재실행과 새 IVP는0이다.

이 controls는 새 finite-mass event conservation(physical plus labelled artificial masses12cases), species heat/STF sums, rotation covariance, tinySTF 보존, input/representation gates, zero-reactant boundary, donor attachment의 energy ownership, pure-H physical/frozen Jacobian 구별과 donor byte identity를 검증한다. 별도129T diagnostic, raw quadrature, plotting 및 독립 이론 리뷰는 root의 다른 구성요소에서 수행하며 이 receipt의 실행으로 세지 않는다.
