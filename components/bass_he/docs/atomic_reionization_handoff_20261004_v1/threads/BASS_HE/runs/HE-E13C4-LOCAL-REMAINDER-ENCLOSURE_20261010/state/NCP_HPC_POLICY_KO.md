# 이후 BASS_HE 연구의 HPC 구현 원칙

사용자가 2026-10-01 요청한 64코어·128GB NCP 활용 방식을 이후 연구 코드의 기본 개발 정책으로 채택한다. 이는 연구 구현 정책이며 production 물리모형·기본값 승인이 아니다. exact R-grid, 근사, 상태, 오차 기준은 각 과학 node의 계약이 결정한다.

독립 R·sector·분해능 작업은 OpenMPI로 분배한다. 같은 R에서 direct/force와 state continuation처럼 선행 결과가 필요한 작업은 DAG 의존성을 지킨다. 독립 eigenstate를 먼저 계산한 뒤 공통 physical measure overlap으로 상태를 연결하며, MPI completion order로 상태를 정렬하지 않는다. rank0 controller 방식의 N ranks는 N−1 계산 worker라는 비용을 기록한다.

뜨거운 정형 루프는 real64 Fortran으로 작성하고 연속 메모리·사전 할당·정확한 selection-rule 희소화·OpenMP SIMD를 적용한다. 이미 최적화된 BLAS/LAPACK/SuperLU를 단순 Fortran 루프로 다시 쓰지 않는다. 고유값 풀이의 새 병렬 backend는 별도 검증이 있어야 한다. 현재 reference와 eigenproblem·ARPACK/SuperLU·수렴기준은 동일하다.

`-O3 -fopenmp -fno-fast-math -ffp-contract=off -fno-associative-math`를 사용한다. `-Ofast`, fast-math, 축소 정밀도와 순서 불명확한 부동소수점 reduction은 기본 금지다. SIMD는 독립 출력 원소에 적용하고 합의 순서를 보존한다. bitwise 재현성과 허용오차 내 수치 동등성은 따로 보고한다. `-march=native`는 동일 target host에서 별도 빌드·검증한 선택사항이다.

64는 사양상 논리 CPU인지 physical core인지 host에서 확인한다. MPI ranks×OpenMP threads와 BLAS threads를 중첩 증식하지 않는다. 기본 BLAS thread는1이며 CPU affinity·quota와 NUMA를 기록한다. 64×1, 32×2, 16×4는 후보일 뿐, 실제 작업 수·RSS·memory bandwidth·solver 병목을 측정해 선택한다. 적어도 메모리20%를 남기고 rank당 실측 peak RSS와 가상주소 공간 cap을 구분한다.

정확도 승인은 matrix parity → eigenenergy·잔차·norm·상태 → direct coupling → 독립 과학 convergence 순으로 분리한다. 빠르다는 이유로 격자, basis, domain, quadrature, tolerance를 낮추지 않는다. 실패한 성능 최적화도 결과를 보존하고 자동 default로 승격하지 않는다. 기존 Python reference와 fail-closed native 선택을 함께 전달한다.

입력·source·compiler·flags·binary·dependency 버전과 실행 구성을 SHA로 결속한다. 결과는 원자적 create-only로 저장하며 output 충돌·task 실패·timeout·MPI identity 불일치는 PASS가 아니다. 향후 C2 코드는 이 정책을 읽고 동일한 검증 계약을 적용한다. 실제 NCP64 strong/weak scaling은 NCP에서 실행한 증거가 생기기 전까지 NOT_RUN이다.
