# C2f 구현 독립 검토

판정: **PASS_IN_DEFINED_C2F_IMPLEMENTATION_SCOPE**. 이번에 정의한 finite-frame API·manufactured 검증 범위의 blocker는 없다. 실제 분자 고유상태 계산, continuum gap 또는 전체 C2 인증이 완료되었다는 판정이 아니다.

검토자는 core/native/runtime 코드 저자와 별도로 동작했고 독립 matrix checks를 작성했다. 다만 수학 설계 문서 작성에도 참여했으므로, 이 판정을 그 문서 자체에 대한 별도의 두 번째 증명으로 부르지 않는다. 코드·실행 증거의 검토와 명시적 대수 반례 검사가 판정의 근거다.

## 수학과 API

공통 positive metric와 physical embedding을 요구하는 입력 경계, symmetry-block과 full-energy target의 구별, dark partner 및 외부 guard 접촉 거절을 확인했다. 허용된 작은 Gram defect에도 먼저 정규화하여 실제 span projector를 사용하고, residual SVD로 projector 거리를 구한다. 작은 각도는 atan2로 복구하며 내부 퇴화에 대한 U(k) 공변성이 유지된다.

실제 projected form V†WHV를 공급한 경우에는 Gram 정규화와 polar 회전을 모두 작은 연산자에 반영한다. energy 목록만 있을 때의 작은 행렬은 명목 representation으로 구별하고 actual Ritz residual 인증을 false로 남긴다. 출력 혼합열에 개별 고유상태 또는 m 라벨을 잘못 붙이지 않는다.

독립 manufactured **13개 PASS**: weighted dense projector와의 비교, 복소 U(k) 공변성, 거의 직교인 동일 span, θ=10⁻¹⁰의 거리·각도, dark 누락, 불완전 guards, 서로 다른 embedding, rank 차이, 작은 overlap, 작은 Hamiltonian의 회전 및 실제 projected form의 Gram 변환을 포함한다. 초기 5개 TypeError는 tolerance 생성자가 2개 필드에서 4개 필드로 변경된 직후 독립 tester가 이전 API를 사용한 문제였다. 원 tester와 실패 receipt를 보존한 뒤 동기화했으며, 물리 실패나 native 산술 실패로 분류하지 않는다.

## 통합 실행 증거

변경된 구현 테스트 **61개 PASS**의 저장된 로그와 파일 identity를 확인했다. 이 안에는 native 17, core 28, runtime seam 15, workflow 1개가 포함된다. 별도 13개 독립 검사는 개념상 겹치므로 이 숫자를 새로운 독립 과학 검사 수로 합산하지 않는다.

12개 서로 다른 analytic manufactured case를 serial reference, serial native 1 thread, Open MPI reference 2×1, Open MPI native 2×4의 네 배치에서 실행한 48개 결과를 확인했다. 저장된 worker 결과에서 동일한 case source identities, 중복 없는 rank 소유권, 모든 PASS와 빈 post-identity error를 확인했다. 저장된 error scalar들로 재계산한 최대 analytic error는 **3.824832315146507×10⁻¹⁵**다. 35개 선택된 로컬 identity bindings 및 실제 worker code SHAs가 현재 파일과 일치한다. 변하지 않은 과학 suite를 다시 실행하지 않았다.

Fortran은 binary64 복소 overlap의 여덟 compensated lanes와 고정 순서 최종 merge를 사용한다. 최종 merge에서 lane 합과 correction을 미리 더해 작은 항을 없애지 않는 것을 확인했다. compiler report의 16-byte vectorization, strict flags, 1/4 thread parity 및 cancellation tests의 저장된 증거를 확인했다. 정확한 합 또는 모든 부동소수점 입력에 대한 무조건적 오차 보장을 주장하지 않는다.

MPI runtime의 실제 version은 이 실행환경의 Open MPI 4.1.6이다. 실행환경은 effective CPU 8개와 cgroup memory 8 GiB이므로 NCP 64코어 성능을 측정한 것으로 취급하지 않는다. runtime의 namespace-aware ownership과 pidfd signaling, detached child 메모리·정리 및 무관한 process 생존 검사를 검토했다. 메모리 감시는 sampled RSS watchdog이고 strict allocation/true peak bound는 아니다.

## 성능 판단과 남는 범위

동일 입력의 측정된 public API workload들에서는 reference BLAS가 native보다 모두 빨랐다. 따라서 이번 결과는 native 속도 향상이나 NCP64 scaling 주장을 지지하지 않는다. strict SIMD native는 명시적으로 선택할 수 있는 검증된 backend로 남고, fallback 또는 production 기본값 변경을 하지 않았다. v1과 v2b를 서로 다른 시점에 측정한 차이는 controlled speedup으로 해석하지 않는다.

manufactured H의 미반환 zero-energy complement 때문에 supplied guard spacing 0.7은 전체 finite gap과 같지 않으며 ideal orthonormal 모델의 전체 gap은 0.5다. 코드·결과에는 이 차이를 기록하고 인증을 false로 유지했다. 이는 실제 분자 continuum이나 L_y error enclosure를 대신하지 않는다.

다음 허용 node는 **C2G_MULTISTATE_EIGENSOLVER_ADAPTER_AND_REFERENCE_PREREGISTRATION**다. 다상태 solver와 물리적 공통 embedding을 연결하고 구체적인 단일 reference 실행 계약을 작성한다. 현재 exact R, basis/box, guards, 물리 tolerance 및 host budget가 null인 상태에서는 실제 physical launch를 허용하지 않는다.

유지 gate: CODE_I02_CLOSED=true, full_C2_closed=false, scientific_PROMOTE=HOLD, full_certificate_fail_closed=true, Eq55_next_node_authorized=false, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED. 실제 분자 solve·새 충돌 전파·이전 과학 suite 재실행은 0이다.
