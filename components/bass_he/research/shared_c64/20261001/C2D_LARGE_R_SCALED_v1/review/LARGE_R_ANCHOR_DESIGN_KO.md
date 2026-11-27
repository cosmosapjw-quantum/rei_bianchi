# C2d 큰 R 독립 구면 앵커: 계산 전 설계

근거 상태: 아래 수학적 범위 구분은 직접 유도/코드 검토이고, 비용·오차 수치는 C2a의 보존 결과를 읽은 것이다. 이 설계에서 새 물리 고유값 계산 또는 적분은 수행하지 않았다. 최종 설정·예산·허용오차는 루트의 사전 등록 계약이 소유한다.

## 1. 선택과 수치 영역

새 앵커는 x=R/a_A=32를 권고한다. 루트가 채택한 큰 R 수열 32,64 중 가장 작아서 He-centered 작은 각운동량의 x² 오차 증폭을 최소화한다. 독립 표현은 기존 B-centered spherical partial-wave hp-FEM이며, prolate B-spline 표현과 좌표 미분을 공유하지 않는다. 공통 물리 Hamiltonian, binary64, SciPy 고유값 알고리즘은 공유하므로 전체 소프트웨어가 완전히 독립적이라고 부르지는 않는다.

현재 `sphere_adapter._configuration`, `_validate_state`, `optimized_solver.radial_mesh`는 모두 두 핵을 수치 상자 안에 포함하는 계약을 갖는다. 따라서 R=32에서 rmax=24를 그대로 쓰면 adapter만 수정해도 solver가 거부한다. 이 오류를 단순 archive 제약으로 간주하여 우회하지 않는다.

수학적으로 B 중심 rmax<R인 Dirichlet ball에서 원격 A의 정확한 Coulomb potential을 포함하는 유한영역 문제는 적법하다. A가 영역 밖이면 potential의 해당 부분은 영역 내 매끄럽고 radial knot R도 필요 없다. 정확한 knot가 필요한 곳은 영역에 포함되는 핵 반경이며, 그것은 multipole radial coefficient의 내부/외부 식이 바뀌는 지점이다. 그러나 유한영역 문제의 적법성은 외부에서 잘라낸 분자파동함수의 오차 인증이 아니다. 현재 단계에서 이 새로운 영역 의미론과 archive 조건을 동시에 도입할 이익이 작다.

**권고안은 rmax=40으로 두 핵을 모두 포함하며 기존 solver 조건을 유지하는 것이다.** C2a R8 l96 m0 archive에 실제 저장된 radial boundaries 전체 [0,24]를 읽고, 28,32,36,40을 추가한다. 따라서 near-B 분해능을 그대로 유지하고 A 핵 R=32를 정확한 knot로 포함한다. C2a 기본 56 exponential cells와 추가 knot8을 유지하면 총 radial cells=61이다. `elements=61`로 명시하되 실제 mesh는 `boundaries`가 결정한다. 새로 40까지 exponential mesh를 전체 재분배하면 near-B cell도 커지므로 그 방식을 기본안으로 삼지 않는다.

## 2. 최초 두 수준과 선택적 진단

| 수준 | lmax | radial partition | degree | Hamiltonian q | rmax | 상태 수 |
|---|---:|---|---:|---:|---:|---:|
| angular low | 72 | 보존 R8 inner partition + 28,32,36,40 | 4 | 14 | 40 | 2 |
| angular high | 96 | 같은 partition | 4 | 14 | 40 | 2 |
| 선택적 h | 96 | 최초 partition의 각 interval 정확히 이등분 | 4 | 14 | 40 | 2 |
| 선택적 p | 96 | 최초 partition 그대로 | 5 | 16 | 40 | 2 |

공통 설정은 `R=32, ZA=1, ZB=2, center=B, m=0 또는1, nroots=2, tol=1e-11, maxiter=2000`이다. root가 등록한 경우에만 h/p 진단을 실행하며 결과 후 새로운 angular level이나 tolerance를 선택하지 않는다. h/p를 모두 허용하면 selected states 최대8, requested Ritz roots 최대16이다. 각 고유상태는 isolated worker task 하나로 계산한다. 두 root 중 lowest를 선택하고 둘째 root는 유한행렬 gap 진단만 제공한다.

두 angular levels가 같은 radial/domain 오차를 공유한다는 한계를 분명히 남긴다. h/p 진단은 basis refinement이지 tail certificate가 아니다. rmax40 자체의 엄밀 tail bound는 이 설계에 없다. 필요하면 계산 전에 별도 tail 상태 두 개(rmax48, 동일 [0,40] partition +44,48)를 등록할 수 있지만, 그것은 위 최대8상태안과 다른 예산이다. 추가 tail 없이도 main prolate tail refinement와 독립 표현 비교를 결합한 유한정밀도 교차검증은 가능하되 continuum closure는 아니다.

## 3. 관측량·부호와 gate 후보

실수 계산량을 Lbar_O=L_O/(-i ħ), Lbar_B=L_B/(-i ħ), pbar=a_A p_x/(-i ħ)로 정의한다. A2 식은

Q_O=Lbar_O/x → 32 sqrt(2)/243,

Q_B=-x² Lbar_B → 128 sqrt(2)/729

를 준다. Q_B의 마이너스는 A2의 L_B=+i ħ C_B x^-2와 양의 meridional phase에 따른 것이다. 실제 archive의 signed Lbar_B를 먼저 보존하고 절댓값으로 위상을 맞추지 않는다. 원점 관계는 Lbar_O=Lbar_B+(x/3)pbar이며 pbar는 radial derivative로 계산한다. gap×dipole이나 원점 관계로 Lbar_B를 정의해서 작은 항을 재구성하지 않는다. 구면 lane의 Lbar_B는 angular-generator selection으로 직접 평가한다.

계산 전 권고 acceptance는 다음과 같다. 전자는 기존 raw C2 기준을 유지하고 후자는 새 scaled 진단이다.

| 항목 | 권고 한계 |
|---|---:|
| sphere–prolate energy | 각 1e-5 E_A |
| sphere–prolate raw Lbar_O | 1e-5 |
| l72→96 raw Lbar_O | 2e-6 |
| sphere–prolate Q_B | 1e-4 |
| l72→96 Q_B | 2e-5 |
| sphere fixed-state successive quadrature Q_B | 1e-6 |
| sphere–prolate Q_O | 1e-5 |
| l72→96 Q_O | 2e-6 |
| sphere fixed-state successive quadrature Q_O | 1e-8 |
| state relative matrix residual / mass norm error | 1e-9 / 1e-10 |

At x=32, Q_B limits map to raw Lbar_B differences 9.765625e-8, 1.953125e-8, 9.765625e-10 respectively. They are independent-representation sanity criteria, deliberately looser than the main prolate scaled spatial precision, and not rigorous error enclosures. Initial frozen quadrature orders14/22/30 require both successive increments; optional40/48 only if preregistered. The direct Lbar_B radial product is polynomial and integrated exactly in exact arithmetic once q is sufficient; pbar contains u_g u_b/r and must keep its own quadrature check.

A2's unknown remainder constants do not justify a finite-R closeness, monotonicity or contraction requirement. Report signed Q_O,Q_B and their differences from the analytic limits descriptively; never choose state levels/tolerances from the desired coefficient.

## 4. 보존 증거와 예상 비용

C2a `evidence/ANCHOR_COMPARISON.json` R8에서 l72→96 raw Lbar_B 차이는 3.3907261547116985e-11이고 x²를 곱하면 2.170064739015487e-9이다. 최고 구면–prolate raw Lbar_B 차이는 2.8257917707164015e-11이며 scaled 차이는 1.808506733258497e-9이다. 이것은 R32의 통과를 예측하는 보장이 아니지만 같은 near-B radial resolution과 두 angular levels를 유지할 유용한 선행 근거다. 기존 R8 수치는 새 R32 앵커의 대체 증거가 아니다.

동일한 C2a native 단일-state 작업의 l72 wall은3.42–4.48초/RSS320632–328044KiB, l96은6.07–6.96초/RSS532672–545204KiB였다. 새 mesh는57→61cells로 늘고 R도 달라져 실행시간·메모리가 달라질 수 있다. task240초/address-space1.5GiB와 fresh memory/topology preflight를 유지하면 현재 계획에 맞는 bounded execution이다. OMP/BLAS1, 실제 허용 worker 수만 MPI에 배정한다. NCP64 actual scaling은 별도 측정 전 NOT_RUN이다.

## 5. 최소 코드 변경 제안

상자를40으로 채택하면 `optimized_solver.py`, `reference/partialwave_centered.py`, Fortran kernel의 변경은 불필요하다. adapter는 explicit boundaries가 configuration에 제공되었을 때 실제 archive boundaries와 정확히 일치하는지 검증하는 보강만 필요하다. 현 코드는 metadata와 archive 사이의 일치는 보지만 요청한 explicit partition과의 일치는 별도로 확인하지 않는다.

`observe_pair`는 기존 L_O_scaled=Lbar_O/x³ key를 의미 변경하지 말고 보존하며, 새 `Q_O=Lbar_O/x`, `Q_B=-x² Lbar_B` 필드를 명시적으로 추가하거나 root analyzer에서 계산한다. archive의 양의 nine-point phase, 실제 rmax, nuclear positions, exact nuclear knot, Dirichlet endpoints, coefficient shape/dtype/finite 값과 size/SHA 검사를 유지한다. synthetic tests로 large-R enclosed mesh roundtrip, missing32 knot 거부, wrong explicit partition 거부, rmax24<R32 거부, 새 scaled 부호를 검사할 수 있다. 새 물리 계산이 필요한 테스트는 필요 없다.

## 6. 채택 후 최소 구현·검증

루트가 위 enclosing-box/보존 inner-mesh 설계를 채택했다. fallback h는 초기 partition의 각 interval을 정확히 이등분하는 방식으로 고정했으며 p는 같은 partition의 degree5다. `code/sphere_adapter.py`에 요청 explicit partition과 실제 STATE partition의 exact array equality 검사, 관측량 Q_O/Q_B 두 필드를 추가했다. 기존 scaled key 의미와 solver/reference/native 코드는 변경하지 않았다.

2026-10-01 affected synthetic tests 5개가 0.030초에 통과했다(exit0). 명령: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -p test_sphere_adapter_c2d.py -v`. enclosing large-R archive roundtrip, load/solve 양쪽의 요청 mesh 불일치 거부, nuclear knot 및 enclosing box guard 유지, Q_B 부호와 Q_O 및 기존 key를 검증했다. solve와 direct observable은 fixture/mock으로 대체했고 새로운 물리 고유값 계산·적분은0회다. 이 검증은 구현에 관한 것이며 새 R의 수치 정확도는 실행 전 미검증이다.
