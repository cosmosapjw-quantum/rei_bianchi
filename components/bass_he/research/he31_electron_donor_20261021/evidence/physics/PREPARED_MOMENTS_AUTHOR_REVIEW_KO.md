# Prepared canonical FV moments: author validation

범위는 실제 CanonicalMomentumFV 인스턴스의 고정 quadrature를 준비된 배열로 재배열하는 것이다. donor, Einstein RHS, vendor originals, 시간 적분법은 이 구현에서 수정하지 않았다.

API는 PreparedCanonicalMoments(source), moments(eta,b), moment_batch(eta,b,chunk=32,max_work_bytes=64*1024*1024)다. 원본 FVMoments 타입과 다섯 필드, cell_numbers, total_cell_number, packet_count, distribution_change_deta를 보존한다. CanonicalFVSpecies.momentum에 대입할 수 있으며 호출자는 먼저 원본 모듈 SHA를 검증해야 한다. wrapper는 원본 객체의 불변 내용을 복사하고 이후 source 파일·보간기·물리 solver를 호출하지 않는다.

다섯 packet 배열의 계산을 준비 단계로 이동했다. 매 scalar call은 energy/inverse의 두 배열, sqrt 한 번, reciprocal 한 번, dot reduction 세 번을 사용한다. batch는 두 작업 행렬의 합을 명시된 cap 이하로 제한한다. 입력/출력 크기 및 BLAS 내부 workspace는 별도다. 모든 배열은 binary64이며 bytes backing을 사용하므로 writable flag를 다시 켤 수도 없다. scalar metadata도 frozen dataclass다.

검증은 원본 2개 분포와 각 6개 대수 상태, 실제 source FVMoments 반환, scalar/batch, source domain rejection, immutable flags, number/energy-work 항등식에 한정했다. ODE·benchmark는 실행하지 않았다. PREPARED_MOMENTS_CHECK.json에 source/implementation/test SHA와 수치 결과가 있다.

| 확인 항목 | 관찰 |
|---|---:|
| 최대 moment 상대차 | 3.691846187591282e-16 |
| 최대 energy-work scaled residual | 1.3615622634293834e-15 |
| 최대 number relative residual | 4.440892098500626e-16 |
| 새 ODE / benchmark | 0 / 0 |

dot reduction은 sum과 반올림 순서가 달라 bitwise parity를 주장하지 않는다. 독립 reviewer의 subnormal 관찰(eta=245 등)은 전체 eta 영역에서 float64 출력이 동일하다는 해석을 배제한다. 실제 HE31 범위 0≤eta≤ln7에서 tolerance parity를 적용한다. eta=1000 두 값 0이라는 단일 경계 체크는 그 사이 모든 late-time 값을 검증한 결과가 아니다.

상주 준비 배열 메모리는 증가하는 대신 반복 연산과 임시 배열을 줄인다. speedup 또는 전체 프로그램 memory reduction 수치는 측정하지 않았다. ACCEL02의 96×32 MassiveDistribution kernel은 discretization identity가 달라 직접 대체하지 않았다.

이 파일은 작성자의 검증 기록이다. 독립 구현 reviewer의 별도 판정과 root의 donor/driver 결과 판정이 실행 또는 과학적 승인 범위를 결정한다.
