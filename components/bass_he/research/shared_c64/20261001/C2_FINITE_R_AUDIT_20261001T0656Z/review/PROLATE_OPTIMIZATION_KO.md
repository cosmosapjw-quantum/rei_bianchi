# C2 prolate 관측량 경로의 가속 및 검증 범위

`prolate_fast.py`는 C1 `coupling.py`의 direct Cartesian derivative와 독립 Coulomb-force 적분을 그대로 사용한다. 기존 dense B-spline basis × 계수 계산을 scalar BSpline으로 먼저 결합하고, 각 quadrature batch에서 중복된 1차원 좌표를 모아 값을 평가한다. union-cell tensor quadrature 및 두 핵 모서리의 Duffy 두 삼각형 적분점·가중치·patch 순서는 C1과 같다. direct (p_x\)는 밝은 상태의 Cartesian 미분으로 계산하며 에너지 차 × dipole로 대체하지 않는다. force 경로는 값만 평가한다.

Fortran `real(c_double)` 커널은 각 patch를 OpenMP 독립 작업으로 계산한다. patch 안의 quadrature point 합과 patch 사이의 합 순서는 고정한다. SIMD는 서로 독립인 관측량 출력 성분에 적용하며 부동소수점 reduction을 사용하지 않는다. 빌드에는 `-O3 -fopenmp -fno-fast-math -ffp-contract=off -fno-associative-math`를 적용했다. GCC vectorization report가 출력 성분 루프의 16-byte SIMD를 확인한다. Python backend는 같은 수식을 벡터화하고 patch 안에서 NumPy 합산을 사용하므로 native와 bitwise 일치를 요구하지 않으며 계약의 절대 오차를 검사한다.

`backend='python'|'native'`는 명시적으로 선택한다. native library, build manifest, ABI, source SHA, binary SHA 및 선택적 실행-pinned `BASS_PROLATE_EXPECTED_SHA256`가 맞지 않으면 실패하며 다른 backend로 전환하지 않는다. 기본 위치는 `native/build/libbass_prolate.so`, 환경변수 `BASS_PROLATE_LIBRARY`로 선택할 수 있다. `native_identity()`가 compiler, flags, source, binary identity를 반환한다. finite 계수·정규화·좌표·결과를 검사하며 m=1 좌표 미분은 열린 적분점에서만 허용한다. `Evaluator`는 상태 계수의 복사본이므로 mutable state를 identity cache로 참조하지 않는다.

`dark`는 같은 m=1 meridional amplitude에 sin(phi)를 붙이고 (K=z(A_\rho-A/\rho)-\rho A_z\)를 적분한다. (\sin\phi\cos\phi/(\sqrt2\pi)\)의 실제 32/64점 주기 quadrature 합을 곱한다. angular 합·meridional 적분·sin/cos normalization을 모두 반환하며 0을 상수로 주입하지 않는다. 이는 별도 고유상태 solve가 아닌 각방향 선택 규칙의 수치 진단이다. 이 진단의 구현은 NumPy이며 native 관측량 구현이라고 주장하지 않는다.

`PROLATE_OPTIMIZATION_MANUFACTURED.json`은 고유값을 풀지 않은 제조 spline 상태로 기존 코드와 새 코드를 검증한다. scalar 평가 최대차는 8.88e−16, direct/force 관측량 최대차는 1.14e−13으로 절대 1e−11 기준을 통과했다. native OpenMP 1/2 threads의 JSON 수치 출력은 bitwise 같았다. 잘못된 backend/order/좌표/실행 SHA는 거부됐다. 이는 구현 동등성 검증이며 물리적 수렴이나 정확한 상태 오차의 증명은 아니다.

물리적 parity와 timing은 C2 계약 안에서 계산한 R=2 base pair의 보존된 계수를 사용한다. 새 고유값 계산을 추가하지 않는다. `PROLATE_OPTIMIZATION_BENCHMARK.py`는 direct q16, force q20에 대해 reference 1회, 각 backend cold 1회 + warm 3회를 기록하고 1e−11 절대 허용오차를 검사한다. reference 1회 시간은 통계적 성능 분포가 아니며 local sandbox의 결과를 NCP64 scaling으로 주장하지 않는다. 결과는 별도 JSON에 기록한다.

실제 R=2 base 보존 상태 parity는 PASS다. direct q16 최대차는 2.22e−16, force q20 최대차는 5.55e−17이었다. reference 단일 측정 / native warm 3회 중앙값은 direct 2.38368s / 0.25043s (9.518배), force 3.43807s / 0.40094s (8.575배)였다. 같은 새 Python backend 중앙값은 각각 0.28967s / 0.41331s이며 이 측정에서 native가 더 빨랐다. 1-thread OpenMP 및 1-thread BLAS로 실행했다. 두 native lane 모두 반복 출력이 같았다. 전체 benchmark wall time은 11.233s, 같은 프로세스 전체 peak RSS는 210468 KiB였다. 이 peak는 reference와 새 backend를 모두 순서대로 실행한 프로세스 최고치여서 backend별 메모리 비교로 해석하지 않는다.

첫 benchmark 실행은 reference 디렉터리를 Python import 경로에 넣지 않아 상태 로딩 전 ModuleNotFoundError로 중단됐다. review harness의 import 경로만 고친 뒤 재실행했으며 과학 solve·계수·연산 kernel에는 변화가 없었다. C2 과학 판정의 q20→28 수렴 실패와 구현 parity PASS는 별도 항목이다.

R=16 h-refinement의 force 수렴 실패가 native 구현 때문인지 확인하기 위해 보존된 같은 상태에서 기존 reference force q28을 한 번만 평가했다. 새 고유값 계산·native 평가·상위 quadrature는 수행하지 않았다. 저장된 native 결과와의 최대차는 L_O의 8.88e−16이며 T_B는 1.67e−16으로 구현 parity 기준 1e−11을 통과했다. 실행 시간은 19.572s였다. 따라서 이 실패 지점에서도 관측된 과학 수렴 실패를 native 연산 차이로 설명할 수 없으며 실패 판정은 그대로 유지한다. 정확한 상태·저장 결과·reference source SHA와 각 성분 차이는 `PROLATE_OPTIMIZATION_R16_FORCE_PARITY.json`에 보존했다. 이 한 번의 확인 이후 검증 범위를 확대하지 않았다.
