# C2g 성능 정책과 NCP 인계

이번 단계는 실제 전자구조 eigensolver의 다중 상태 반환을 연결한다. 행렬 조립과 shift-invert 인수분해를 root마다 반복하지 않고, 한 sector의 필요한 모든 selected/guard root를 한 번의 eigsh 호출에서 얻는다. 정적 실수 spinless 축대칭 H에 대해 -m 상태는 +m 상태의 정확한 켤레로 재구성한다. 이는 별도 -m 계산을 생략하는 대칭성 사용이며, 회전/ETF 항이 있는 동역학에서 sector가 분리된다는 주장이 아니다.

조립은 기존 binary64 Fortran ABI3 kernel을 사용한다. 닫힌 compiler profile은 O3, OpenMP, independent-entry SIMD, no-fast-math, no-associative-math, fp-contract=off다. 분자 고유해 계산의 NumPy 기준 경로도 명시적으로 유지하며 암묵 fallback은 없다. 이번 source는 새 C2g namespace에서만 바꾼다. 기존 연구 결과를 새 이름으로 다시 실행하지 않는다.

공통 공간 평가는 radial/eta의 분리 구조를 이용한 행렬곱 후 phi 위상을 붙여 수행한다. l×전체3D격자 중간배열을 만들지 않는다. 분석에서는 snapshot cache를 세 개로 제한하며 12개 full frame를 한꺼번에 보관하지 않는다. 작은 rank의 weighted overlap은 C2f 실측에 따라 reference BLAS 경로를 명시적으로 사용한다. optional native overlap의 검증된 source와 strict build도 보존하지만 이번 물리 pilot에서 그 kernel의 새 성능 검증을 주장하지 않는다.

OpenMPI는 독립 R/level/m task를 rank-stride로 분배하고, 각 rank는 NPZ와 task receipt를 즉시 원자적으로 저장한다. gather에는 작은 요약만 보낸다. BLAS thread는 1, OpenMP 수는 명시값, dynamic=false로 고정한다. 본 pilot의 두 조합은 numpy serial1×1과 native OpenMPI2×1이다. 이는 backend와 병렬도 모두 달라지는 비교이며 순수 native kernel 가속률을 추정하는 대조군은 아니다. 1회 workload wall time은 환경 의존 측정값이고 통계적 반복 성능 증거가 아니다.

현재 host는 CPU quota8, memory8GiB이며 NCP64 실행은 하지 않았다. 이 pilot의 hard cap을 풀어 NCP에서 자동으로64ranks를 띄우는 기능은 없다. 다음 NCP 계산에는 실제 topology/affinity/quota/available memory, compiler/OpenMPI/BLAS identities를 새로 관찰하고 독립 task 수와 rank별 peak-memory 측정에 맞춘 별도 계약이 필요하다. 충분한 R 작업이 있을 때 task 병렬성을 우선하고, rank×thread가 실제 예산을 넘지 않도록 한다. rank가 task 수보다 많으면 idle rank가 생기므로64라는 숫자만으로 layout을 선택하지 않는다. 후보 layout을 같은 물리 작업으로 비교한 뒤 선택하며, 이번 국소 wall time을64코어 가속률로 외삽하지 않는다.

NCP에서 element kernel을 다시 빌드할 때 native/build_element.py --output-dir에 새 경로를 준다. 기존 evidence binary를 덮어쓰지 않는다. host별 ISA 최적화는 --native를 명시한 별도 build이며 compiler/source/library hash와 부동소수점 parity를 함께 기록한다. 기존 compiler flags를 임의 FFLAGS로 바꾸는 경로는 없다. optional overlap은 native/build_overlap.py의 create-only profile을 사용한다.
