# C2c 독립 구면 앵커 사전 설계

이 문서는 기존 코드와 보존된 수치 증거만 읽어서 작성했다. 새로운 물리 고유값 계산, 적분, 단위시험은 실행하지 않았다. 아래 값은 계약 후보이며 최종 실행 허가는 루트의 사전 등록 계약에 따른다.

## 권고 지점과 표현

새 독립 앵커는 **x=R/a_A=0.125**를 권고한다. 예정된 새 수열에서 가장 큰 R이므로 실제 작은 R 검증을 추가하면서 R³로 나누는 오차 증폭과 B→O 원점 이동의 상쇄를 가장 작게 유지한다. x=.0625 또는 .03125에서 동일한 raw 오차는 각각 8배 또는 64배 더 크게 증폭된다.

기존 `BASS_HE_NCP64_OPTIMIZATION_20261001_v1/code/optimized_solver.py`의 spherical partial-wave hp-FEM을 이용한다. 두 핵은 B 기준 z=(-R,0), 전하는 (1,2)이고, 수치 단위는 a_A=E_A=ħ=m_e=1이다. 물리 관측량의 원점은 기존 charge center O로 고정한다. 비교할 실수량은

\[
\bar L_O=\frac{L_O}{-i\hbar}
=\bar L_B+\frac{x}{3}\bar p_x,
\qquad Q(x)=\frac{\bar L_O}{x^3}.
\]

두 항의 크기, 합, `(|L_B|+|x p_x/3|)/|L_O|`를 모두 기록한다. `L_O`를 force/energy gap 또는 이론 계수로 대체하지 않는다. `p_x`는 radial derivative로 직접 계산하며 energy-gap×dipole로 정의하지 않는다. m=0과 real bright |m|=1 각각에서 lowest Ritz root를 선택하고 기존 nine-point positive meridional phase를 그대로 사용한다. 원점 이동이나 결과의 절댓값으로 위상을 맞추지 않는다.

## 최초 네 상태와 제한된 추가 상태

| 수준 | lmax | radial elements | degree | Hamiltonian q | box rmax/a_A | 신규 상태 수 |
|---|---:|---:|---:|---:|---:|---:|
| angular low | 72 | 56 | 4 | 14 | 24 | 2 |
| angular high | 96 | 56 | 4 | 14 | 24 | 2 |
| 선택적 h 진단 | 96 | 80 | 4 | 14 | 24 | 2 |
| 선택적 p 진단 | 96 | 56 | 5 | 16 | 24 | 2 |

모든 상태는 `R=.125, ZA=1, ZB=2, center="B", nroots=2, tol=1e-11, maxiter=2000`를 공유한다. 기존 exponential radial mesh에 핵 반경 R을 정확한 knot로 삽입한다. `nroots=2`는 낮은 두 Ritz root 간의 이산 gap 진단을 남기기 위한 것이며 continuum isolation certificate가 아니다. h/p 진단을 시행할 경우 최초 계산 전 계약에 상태 수까지 포함해야 한다. 실패 후 사후적인 차수 확대나 허용오차 완화를 하지 않는다.

직접 관측량은 기존 `fast_observables.direct_observables`의 q=14와 q=22로 각각 평가한다. 서로 다른 파동함수를 만들지 않는 이 두 적분은 `L_B`의 polynomial radial product와 `p_x`의 u_g u_b/r 항에 대한 quadrature 확인이다. 특히 `L_B`의 q 안정성만으로 momentum lane의 quadrature 정확도를 대체할 수 없다.

## 오차 기준 후보와 해석

최종 tolerance는 결과를 보기 전에 루트 계약으로 고정해야 한다. 엄격한 후보는 구면–prolate `|ΔQ|≤1e-5`, 구면 l72→96 `|ΔQ|≤2e-6`이다. x=.125에서 각각 raw `|ΔL_O|≤1.953125e-8`, `3.90625e-9`에 해당한다. 기존 raw cross-discretization `1e-5`, spherical increment `2e-6` 기준도 동시에 적용하여 과거 기준을 완화하지 않는다. 에너지의 기존 독립 비교 기준은 `1e-5 E_A`, algebraic residual은 `1e-9`, mass norm은 `1e-10`을 유지할 수 있다. 이 값들은 수치적 acceptance 기준이며 continuum 오차 상한이 아니다.

달성 가능성은 **미검증**이다. C2a x=.5에서 구면 l72→96 raw L_O 증가량은 `9.968188244280363e-8`, scaled 값은 `7.97455059542429e-7`이었다. 같은 지점의 최고 수준 구면–prolate raw 차이는 `7.589044732220218e-8`, scaled 차이는 `6.071235785776174e-7`이었다. 이는 후보 precision을 탐색할 근거이지만 다른 R로 이전할 수 있는 오차 정리가 아니다. x=.125에서도 통과한다고 예측해 기록하면 안 된다. 신규 계수 Q(x)를 `4 sqrt(2)/15`에 맞춰 tolerance나 상태를 선택하지 않는다.

최초 네 상태만 허용된 경우 increment 또는 cross-discretization gate 실패는 `INDEPENDENT_SMALL_R_ANCHOR_UNRESOLVED`로 끝내는 것이 타당하다. h/p 진단이 사전 등록된 경우에만 angular truncation과 radial/cancellation 원인을 분리한다. 선택적 진단을 모두 통과해도 본 앵커는 한 지점의 독립 표현 점검이며 전체 작은 R 수열의 오차 certificate가 아니다.

## 실측 비용 근거와 실행 상한

C2a의 동일 (elements56,d4,q14,rmax24,nroots2) native 단일-state 작업에서 l72는 3.42–4.48초, RSS 320632–328044 KiB였고 l96은 6.07–6.96초, RSS 532672–545204 KiB였다. 이 기록은 x=.5 및 8에 대한 것이라 새 x=.125의 실행시간 보장은 아니다. 최초 네 상태의 총 순차 비용은 수십 초 규모를 예상할 수 있으나 task wall 120초, worker address-space 1.5 GiB의 기존 상한을 유지한다. 네 상태를 한 Python process에서 순차 solve하면 factorization/cache와 배열 수명이 겹칠 수 있으므로 **한 isolated worker task당 한 상태**를 유지한다.

기존 C1b의 Python reference pair 실행에서는 l96 h80 RSS 1178216 KiB, l96 p5 RSS 1206608 KiB가 기록되었다. 현재 native one-state 작업과 직접 비교한 메모리 실측은 아니므로 정확한 절감 배수로 해석하지 않는다. 추가 진단에도 1.5 GiB cap을 유지하고 초과 시 RESOURCE_LIMIT로 분류한다. 새 host preflight에서 허용되는 workers만 MPI로 실행하며 OMP/BLAS thread=1을 기본으로 한다. NCP64에서의 실제 성능은 별도 측정 전 NOT_RUN이다.

## 독립성과 재사용 경계

구면 모델은 prolate B-spline tensor discretization, prolate coordinate differentiation, torque integration과 독립적인 radial hp-FEM × associated Legendre 기저다. `L_B`는 정확한 angular-generator selection으로, `p_x`와 dipole은 독립 angular selection/radial derivative로 구성한다. 동일한 물리 Hamiltonian, 공통 SciPy sparse eigensolver, binary64 산술을 공유하므로 완전히 독립적인 전체 소프트웨어 구현 또는 interval enclosure라고 부르지는 않는다.

원본 HPC `task_worker.py`는 단일 상태를 `STATE.npz`로 저장하고 에너지/잔차/노름/mesh/기저 및 native identity를 남긴다. `analyze_anchors.py`의 reconstruction, source-hash, archived phase 검사를 재사용할 수 있지만 hard-coded `.5,8`과 이전 계약 경로는 새 앵커 adapter에서 명시적으로 바꿔야 한다. root가 adapter 인터페이스를 승인하기 전 본 검토자는 구현을 만들지 않았다.

확인한 근거는 C2a `code/analyze_anchors.py`, `inputs/SPHERICAL_TASKS.json`, `evidence/ANCHOR_COMPARISON.json`, 각 `SPHERICAL_MPI/*/RESULT.json`; HPC `code/task_worker.py`, `optimized_solver.py`, `fast_observables.py`; C1b `code/run_axis_audit.py` 및 l96 h/p/q/tail evidence다. 본 문서는 새로운 source-literature 주장을 하지 않는다.
