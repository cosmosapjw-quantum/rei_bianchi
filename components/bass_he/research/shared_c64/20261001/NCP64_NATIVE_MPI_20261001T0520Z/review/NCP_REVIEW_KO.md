# NCP64 최적화 독립 검토

판정: **ACCEPT_SCOPED_ACCURACY_PRESERVING_HPC_IMPLEMENTATION**. 변경된 계산식·배열 배치·병렬 실행 경계를 검토했고, 제한된 입력에서 정확도를 보존하는 HPC 연구 구현으로 수용한다. 실제 NCP 64코어 성능과 과학적 정확도 승격은 이 판정에 포함되지 않는다.

기존 Coulomb Hamiltonian, 이산 공간, Gauss 차수, Dirichlet 경계, ARPACK/SuperLU 고유값 문제, 부호·단위·phase 규약이 유지된다. Kronecker 질량행렬과 사전 할당 COO는 같은 자유도·원소를 조립한다. ABI3의 C/Fortran 배열 대응과 비대칭 입력 테스트를 확인했다. OpenMP는 독립 출력 블록을 분배하고, SIMD는 서로 다른 출력 원소에 적용한다. multipole k와 quadrature q의 합 순서를 유지하며 fast-math와 MPI 부동소수점 과학 reduction이 없다.

직접 연산자는 같은 각도 선택 규칙과 radial union partition을 사용한다. 물리적 원점 변환 L_O=L_B+Z_A R/(Z_A+Z_B)p_x를 보존하며, 에너지 차나 힘 항등식을 직접 결합의 대용으로 쓰지 않는다. 검토자가 고유값 계산 없이 operator 테스트 5개와 runtime 테스트 14개를 직접 통과시켰다. 마지막 localhost:slots 표기 수정은 코드·테스트 assertion으로 확인했다. 검토자의 신규 eigensolve는 0회다.

기록된 행렬 차이 최대값은 7.11e−15, l96 에너지 차이는 최대 3.56e−15 E_A, 상태 L² 차이는 3.72e−15, 직접 연산자 차이는 1.00e−15 이하다. producer의 ABI3 portable/local-ISA/debug 각 7개 테스트 로그를 확인했다. 직렬/3-rank MPI의 4개 task는 에너지와 상태 배열이 일치한다. 검토자가 모든 8개 NPZ의 크기·SHA와 배열 일치를 독립 확인했다.

초기 source/library/state 결속 누락, build manifest 누락 허용, scalar finiteness 검사와 단일 호스트 지정을 수정했다. 현재 worker 전후 source/native identity와 결과 NPZ identity를 검사하고, tamper 회귀 검사를 통과한다. 초기 실패·실행 소스·바이너리는 보존했다. 집계는 target solve 36회와 전체 Ritz root 64개로 분리한다. 40 target/80 Ritz 한도는 후속 실행 전의 명시적 운영 수정이며, 원 계약을 처음부터 그렇게 등록했다고 주장하지 않는다.

실측 이득은 분리해서 보고한다. 고정 상태 직접 연산자의 warm 중앙값은 16.44배, cold는 3.49배다. 전체 l40 solver의 최종 독립 3회 측정은 native가 reference보다 중앙값 1.137배 빠르고 peak RSS 중앙값은 약 28.63% 작다. 최적화 NumPy와 native의 시간 차이는 변동 폭 안이므로 native의 유일한 우위를 주장할 수 없다. 4-thread native 약 3.34배는 합성 element kernel에 한정된다.

이 환경에서는 엄격한 core binding이 hwloc 오류로 application 실행 전에 막혔다. 별도의 unbound MPI 기능 비교는 성공했으나 NCP binding·NUMA·64코어 scaling 검증으로 확대하지 않는다. launcher의 strict binding은 유지한다. 메모리 snapshot과 RLIMIT_AS는 RSS 예약을 보장하지 않으며, local-ISA 바이너리는 NCP에서 다시 빌드·검증해야 한다.

`scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, production 변경 미승인과 C2 미실행 상태를 유지한다. 원격 게시·백업 복원·최종 ZIP은 이 독립 검토 범위 밖이다. 상세 파일 identity와 판정 근거는 `NCP_REVIEW.json`에 고정했다.
