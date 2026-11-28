# Prepared canonical moments 독립 검토

**판정: PASS_SCOPED_PHYSICAL_INTERVAL.** 실제 HE31 물리 구간 `0≤eta≤ln(7)`에서 채택을 막는 수식·캐시·입력·자원 결함을 발견하지 않았다. 원본과 달라질 수 있는 subnormal 연산 순서는 물리 pilot 구간 밖의 범위 주석으로 기록했다. 원본 모듈은 수정하지 않았다.

## 검토한 파일과 identity

- `src/prepared_moments.py`: SHA256 `5d2f877b6e511c421ed95fc3fabde29e97998ec40c8d191768fda769cc5e0c37`.
- `tests/check_prepared_moments.py`: SHA256 `71f27b15a7c65e4715942fb0dfbecba5d30a0e4173b66fd532f7b8309001166b`.
- 원본 `../he29_rei_pilot_20261021/vendor/canonical_fv.py`: SHA256 `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5`.

이 판정은 위 source bytes와 scope에 대한 것이다. 이후 docstring 변경은 별도 readback hash로 결속하면 된다.

## 정규화와 압력

준비된 값은 `w=N/E_ref`, `q_perp²=q²(1-mu²)`, `q_parallel²=q²mu²`다. 현재 geometry의 scale을 곱한 에너지 E를 사용하면 원본과 같은 `rho=e^-3eta ΣwE`, `P_perp=e^-3eta s_perp Σ(wq_perp²/E)/2`, `P_parallel=e^-3eta s_parallel Σ(wq_parallel²/E)`를 얻는다. 횡방향 압력의 1/2, 현재 부피의 e^-3eta, reference energy norm은 올바르게 보존된다. 압력3개 합을 에너지로 오인하거나 새 quadrature로 바꾸지 않는다.

## 캐시·불변성

cross-object lookup이나 반올림한 state key를 도입하지 않는다. 각 prepared instance가 실제 원본의 질량, 각도 분포, quadrature, norm 및 number/cell 소유권을 별도 snapshot으로 보유한다. 배열은 immutable bytes 위의 NumPy view이므로 WRITEABLE=True로 바꿀 수 없다. 실제 작은 독립 확인에서도 여섯 배열 모두 쓰기 플래그 변경을 거절했다. 원본 객체의 mass와 norm을 나중에 재할당해도 prepared output은 그대로였다.

source pin과 모듈 SHA는 상위 caller가 결속해야 한다. `isinstance`가 source provenance를 인증하지는 않는다. 이는 이 모듈의 documented caller contract이며, 새 driver의 별도 검토 대상이다.

## 배치 메모리

packet 수를 K라 하면 두 work matrix의 메모리는 `16*K*width` bytes다. width가 `min(chunk, cap//(16*K), N)`이므로 선언한 **두 packet matrix의 cap**은 구조적으로 지켜진다. persistent 배열은 대략 `8*(5*K+cell_count)` bytes와 객체 overhead다.

입력/출력, 입력 유효성 검사에서 생기는 O(N) 배열, O(width) geometry/reduction 벡터 및 BLAS 내부 workspace까지 전체 RSS가 cap 아래라는 주장은 하지 않는다. 기존 check가 two-state budget을 인수로 주어 실행하는 것은 기능 검증이며 peak RSS 계측은 아니다. 벤치마크나 메모리 profiler는 실행하지 않았다.

## energy-work와 number 검증 독립성

검사 코드는 prepared output에서 derivative를 다시 조립하지 않고 original q,mu,N로 mass-shell energy를 직접 미분한다. `v=db/deta`에 대해

`rho' = -3rho -(2P_perp+P_parallel)+2v(P_perp-P_parallel)`

이므로 `rho'+3(rho+pbar)+6v*pi_s=0`, `pi_s=(P_parallel-P_perp)/3`가 된다. 현재 test의 부호와 factor는 이 식과 일치한다. number 검사는 original total_cell_number를 별도 비교 기준으로 사용한다. 이는 동일 canonical discretization의 algebraic check이며 quadrature 또는 ODE convergence 증명은 아니다.

## 실제 발견한 subnormal 경계

독립 실험은 4개 scalar state만 비교했다. 파라미터는 mass=1e5, amplitude=2, radial4×angular4, Gauss4다.

| eta | b | original rho | prepared rho | rtol=3e-14, atol=0 |
|---:|---:|---:|---:|---|
| ln7 | -0.1 | 0.0029154518932053407 | 0.0029154518932053407 | 통과 |
| 240 | 0 | 2.0322204584e-313 | 2.0322308011e-313 | 불일치 |
| 245 | 0 | 0 | 6.217e-320 | 불일치 |
| 247 | 0 | 0 | 1.53e-322 | 불일치 |

원본은 r³/reference_norm을 먼저 구하므로 더 일찍 underflow한다. prepared 식은 normalized weights를 먼저 계산해 subnormal rho를 더 오래 유지한다. 둘의 유한 입력 허용 범위는 같지만, 임의로 큰 eta까지 zero-atol 상대 parity를 보장할 수 없다. eta1000에서 양쪽 모두0인 기존 test만으로 중간 underflow 영역을 대표할 수 없다.

Root는 실제 HE31 driver 구간이 eta≤ln7임을 확인하고 **구현 docstring과 계약에 이 scope만 명시하는 교정**을 수락했다. 산술은 바꾸지 않고 추가 테스트를 확장하지 않는다. 이 경계는 실제 z20→2 pilot을 막는 결함이 아니다.

**새 ODE·물리 trajectory·벤치마크·전체 suite 실행은 모두0이다.** 실행한 것은 원본/새 scalar4상태 비교와 snapshot 불변성 확인뿐이다. 더 자세한 수치와 판정 항목은 PREPARED_INDEPENDENT_REVIEW.json에 저장했다.

