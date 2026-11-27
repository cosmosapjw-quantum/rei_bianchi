# C2e 다음 연구 인계

다음 단일 node: **C2F_SYMMETRY_COMPLETE_CLUSTER_PROJECTOR_IMPLEMENTATION**.

C2e는 source/domain/target **정의 단계만 완료**했다. 먼저 C2E_REPORT_KO.md, contract/C2E_TARGET_AND_DOMAIN_CONTRACT.json, contract/C2F_PREREGISTRATION_DRAFT.json, math/SPECTRAL_TARGET_DERIVATION_KO.md, review/C2E_INDEPENDENT_REVIEW.json을 읽는다. 종료 라벨은 SCOPED_DOMAIN_MAP_AND_SPECTRAL_TARGET_DEFINITIONS_COMPLETE이며 full C2 또는 production closure가 아니다.

유지할 과학적 구분:

- 기존 g+real bright pair는 각 symmetry sector의 최저 상태다. 누락된 dark partner 때문에 full-H energy Riesz rank2 target이 아니다. 기존 C2a-d 수치 근거를 재실행하지 않는다.
- 큰 R의 H1s+He⁺ n2는 rank5, (m0,m+1,m−1)=(3,1,1)이다. incoming H1s는 기존 g/bright pair에 포함되지 않는다.
- ground-excluded rank5가 R→0까지 continuum 포함 uniform exterior gap을 가진다는 요구는 UA complete-shell rank와 모순이다. 이를 모든 positive-R interval에서 rank5가 실패한다는 주장으로 바꾸지 않는다.
- energy-order projector, symmetry-block continuation, atomic channel labels를 구분한다. 내부 퇴화는 cluster 실패가 아니지만 exterior gap 및 principal-angle loss는 따로 검사한다.
- fixed-axis m 분리는 rotating/ETF dynamics의 m 분리를 보장하지 않는다. planar-even 축소는 아직 조건부 미채택이다.
- L² projector 정확도 및 Ritz gap만으로 continuum 또는 L_y 오차 인증을 선언하지 않는다.

회수된 물리 authority는 0.5·5 keV/u 조사 우선값과 세 가지 궤적 비교다. 공통 energy frame/mass·production 궤적·유한 b/time/R 구간은 미지정이다. diagnostic REAL/EXTENDED support 또는 DR9A turning point를 물리 cutoff로 채택하지 않는다. 조건부 domain map은 math/COLLISION_DOMAIN_DERIVATION_KO.md에 있다.

C2F 첫 작업은 multi-state target/guard-state API와 degeneracy-covariant projector transport의 구현 및 manufactured tests다. 실제 solver 진입 전에는 exact R 배열, state/sector 수, residual·projector·gap·observable 기준, basis/domain, 실제 host 예산을 구체적으로 등록한다. C2e의 null을 임의 기본값으로 바꾸지 않는다. Production domain 미지정은 이 전자구조 인터페이스 구현을 멈출 이유가 아니지만 전체 collision coverage claim은 계속 보류한다.

후속 코드는 binary64 Fortran/OpenMP/SIMD hot kernels, explicit OpenMPI task parallelism, pinned reference/parity, no-fast-math 및 실제 topology/memory preflight를 유지한다. local unbound는 OMP_PROC_BIND=FALSE를 부모/worker에 전파하고 NCP 기본 core/close는 유지한다. 새 성능 비교는 같은 workload의 실측으로 제한한다.

이번 신규 실행: 계약 의미 검사15, 저자 exact24, 독립 exact22. 서로 겹치는 검산을 하나의 총검사수로 합치지 않는다. 물리 eigensolve/quadrature/전파0, 이전scientificsuite재실행0, NCP64실측NOT_RUN. source SHA와 archive manifest를 필요한 입력에만 선택적으로 확인하고, 정상 저장 ACK/size를 remote restore 검증으로 부르지 않는다.

항상 유지: CODE_I02_CLOSED=true; full_C2_closed=false; scientific_PROMOTE=HOLD; full_certificate_fail_closed=true; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED. 같은 연구 브랜치의 additive namespace와 기존 Drive+Dropbox create-only 이중백업 관례를 이어간다.
