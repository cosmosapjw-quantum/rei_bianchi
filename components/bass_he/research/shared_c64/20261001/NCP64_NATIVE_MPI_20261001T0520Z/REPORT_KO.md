# BASS_HE NCP64 구현 최적화

OpenMPI 작업 병렬화, real64 Fortran/OpenMP/SIMD 커널, 메모리 절감 조립, 정확한 선택규칙 기반 관측량 연산을 구현했다. 고정한 비교 문제에서 정확도 기준을 통과했다. 실제 NCP 64코어의 scaling은 아직 측정하지 않았고, C2 과학 격자도 실행하지 않았다.

| 동일 작업 비교 | 기준 → 최적화 | 검증 범위 |
|---|---:|---|
| l96 direct 연산, warm 중앙값 | 86.86 → 5.28 ms; 16.44× | 동일 저장 상태·q14, 7회 |
| l96 direct 연산, cold | 84.26 → 24.17 ms; 3.49× | 각운동량 캐시 초기화 포함 |
| l40 단일 상태 전체 풀이 | 437.37 → 384.57 ms; 1.137× | fresh process 각3회, OMP1/BLAS1 |
| 같은 전체 풀이 peak RSS | 192656 → 137504 KiB; 28.6% 감소 | 각3회 중앙값 |
| 합성 Fortran 커널 OMP4 | NumPy 대비 약3.34× | 커널만, NCP64 speedup 아님 |

전체 풀이의 최적화된 NumPy 중앙값도381.88ms로 Fortran과 비슷했다. 따라서 Fortran이 항상 우월하다고 판단하지 않고 native/numpy/reference를 명시적으로 선택하게 했다. 기존 NumPy 코드를 전부 Fortran으로 옮기는 방식보다 독립 고유상태 작업의 MPI 병렬화와 정형 커널·메모리 최적화를 함께 사용한다. 단일 행렬의 ARPACK/SuperLU 자체는 분산 구현으로 바꾸지 않았다.

행렬 최대 차이는7.11×10⁻¹⁵, l96 기준 에너지 최대 차이는3.55×10⁻¹⁵ E_A, 관측량 최대 차이는1.00×10⁻¹⁵, 상태 L² 차이는3.72×10⁻¹⁵였다. 기존 물리 원점·위상·단위·적분 차수·basis·eigensolver tolerance를 유지했다. 이는 기록한 fixture의 구현 동등성이며 연속계 error enclosure나 임의 R 정확도 보증이 아니다.

Native portable/native-ISA/debug 각각7개, 관측량5개, 실행 경계14개 검사가 통과했다. 실제 OpenMPI1 rank와3 ranks(계산 worker2)의 네 작업은 에너지와 저장 상태 배열이 bitwise 일치했다. 변경된 launcher의 host-slot 표기만 따로 결속해 계산 코드가 같은 기존 serial 결과를 재사용했다. 현재 제한 환경에서는 hwloc core binding이 실패해 MPI 기능 시험을 unbound로 실행했다. NCP용 launcher는 core binding을 유지하며 NCP에서 검증해야 한다.

MPI 실행은 rank별 입력·코드·native SHA를 확인하고, 자식 프로세스의 wall time·주소공간을 제한하며, 원자적 create-only 저장과 실패 기록을 제공한다. 잘못된 cache reuse를 막기 위해 이번 버전은 resume를 지원하지 않는다. 작은 task에는 프로세스 시작 비용이 클 수 있으므로 실제 작업 단위로 throughput을 측정한다. 64×1/32×2/16×4는 후보이고, 실제 topology·worker당 memory envelope·작업 수와 함께 선택한다. 메모리20% 여유를 유지한다.

초기 느린 Fortran 커널·코드와 binary, compiler 환경 문제, OpenMPI version/slot 검출 오류와 수정, binding 환경 blocker를 보존했다. 자체 실행 budget의 ‘eigenstate’ 표기가 모호해 남은 실행 전에 target40/Ritz80으로 명시했으며, 이전 파일은 동시점 해시가 없어서 reconstruction임을 표시했다. 실제 실행은 target36/Ritz64다.

`HPC_POLICY_KO.md`와 root AGENTS의 추가 규칙이 이후 BASS_HE 연구 구현에 적용된다. 다음 과학 node는 C2이며 정확한 R-grid·continuation 계약을 먼저 고정한다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`은 그대로다. NCP 실행 절차는 `NEXT_HANDOFF_KO.md`, 수치는 `RESULT.json`, 감사와 전송 확인은 review 및 별도 delivery receipt에 있다.
