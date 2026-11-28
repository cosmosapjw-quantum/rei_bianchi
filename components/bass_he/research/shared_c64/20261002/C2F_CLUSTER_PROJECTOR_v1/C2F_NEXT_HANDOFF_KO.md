# C2f 다음 연구 인계

다음 단일 node는 `C2G_MULTISTATE_EIGENSOLVER_ADAPTER_AND_REFERENCE_PREREGISTRATION`이다. C2f 결과 보고서·최종 독립 검토·실제 실행 receipt를 먼저 읽고, code/README_API.md와 contract/C2G_PHYSICAL_REFERENCE_DRAFT.json을 따라 실제 전자구조 provider를 연결한다. C2f는 유한차원 manufactured 구현 검증이며 molecular eigensolve, collision dynamics, continuum gap 인증을 수행하지 않았다.

## 다음 구현 작업

1. 기존 physical solver의 고유상태 반환 경로를 읽고, 각 m-sector에서 selected states와 exterior guards를 함께 반환하는 adapter를 작성한다. 필요한 고유상태 수와 잔차의 정의를 명시한다. 기존 g/bright pair 파일을 rank-5 원자 채널 묶음으로 재명명하지 않는다.
2. 정적 spinless 실수 축대칭 Hamiltonian에서 ±m 재구성이 성립하는 정확한 phase/azimuth convention을 보존한다. m=0 세 상태와 m=±1 각 한 상태라는 큰 R rank-5 후보의 multiplicity는 실제 유한 R atomic correlation을 증명하지 않는다. rotating frame/ETF에서 m이 동역학적으로 분리된다고 가정하지 않는다.
3. R마다 다른 prolate/spherical 좌표·격자의 계수 배열을 직접 내적하지 않는다. 같은 물리 Hilbert 공간으로 사상하고, common embedding identity와 positive diagonal physical quadrature weights를 명시한다. 사상 오차·공간 tail·quadrature 오차는 projector algebra 검사와 별도로 관리한다.
4. source state ID, energy convention, 실제 residual, source bytes/hash를 Snapshot에 제공한다. 가능하면 `selected_projected_operator=V†WHV`를 계산해서 전달한다. 이것이 없을 때 반환되는 작은 행렬은 normalized frame 위의 명목 diagonal-energy model이며 실제 H projection으로 사용하지 않는다.
5. 한 개 bounded reference pilot에 대해서만 exact R 배열, target/guard 수, basis/box, norm·gap·observable 기준, memory·wall·eigenstate budget을 구체적으로 사전 등록한다. 독립 검토 후 그 계약이 준비된 범위만 실행한다. 현재 draft의 null을 기존 pair tolerance나 diagnostic R proxy로 임의 치환하지 않는다.

## 계승해야 할 수학·구현 의미

`P=U(U†WU)^{-1}U†W`가 span의 직교 projector다. 허용 오차 내 Gram whitening을 명시적으로 기록한 뒤 normalized frame의 polar transport를 사용한다. 입력 eigenstate IDs는 원자료의 provenance로 유지하고, 혼합된 출력 열에는 개별 고유상태 이름을 붙이지 않는다. 내부 퇴화는 허용하지만 알려진 누락 partner·외부 경계 충돌·작은 principal overlap은 등록된 gate로 처리한다.

제공된 guard 간격은 외부 spectrum 전체에 대한 lower bound가 아니다. C2f manufactured 예에서는 supplied guard spacing이 0.7이어도 생략된 zero-energy complement 때문에 이상적인 전체 유한계 gap은 0.5다. L² projector 검증을 continuum enclosure 또는 비유계 L_y 오차 인증으로 승격하지 않는다. UA rank-5 장애는 ground-excluded full-H Riesz projector와 R↓0 uniform positive external gap에 관한 조건부 명제이며, positive-R_min compact interval을 배제하지 않는다.

## 실행·성능 정책

Fortran binary64/OpenMP/SIMD native kernel과 명시적 OpenMPI 경로를 유지한다. 측정에서는 작은 rank의 overlap public API에서 NumPy/BLAS가 더 빨랐으므로 native를 무조건 빠른 경로로 고정하지 않는다. backend 선택은 명시적이며 fallback이 없다. compiler/source/library identity, no-fast-math·no-FMA-contraction, reference parity를 유지한다.

현재 host는 CPU quota 8과 memory limit 8 GiB 환경이었다. NCP64 실측은 하지 않았다. contract/NCP64_MANUFACTURED_TASKS.json은 64개 유한차원 synthetic 작업과 96 GiB sampled watchdog budget을 준비한 미실행 profile이다. 실제 NCP에서 compiler/runtime을 확인하고 rank×thread가 topology/quota 안에 들어오는 layout을 비교한다. 이 profile로 물리 계산이 허용되지는 않는다. docs/RUNTIME_KO.md의 platform/support 범위를 따른다.

Launcher는 create-only output, atomic fsync, exact input/code/native identity와 rank별 작업 소유권을 기록한다. wall/memory watchdog은 sampling 기반이며 strict allocation bound가 아니다. local unbound에서는 OMP_PROC_BIND=FALSE, NCP core binding에서는 close를 적용한다. timeout·worker 실패 기록을 지우거나 성공 receipt로 덮어쓰지 않는다.

## gate·게시·백업

`CODE_I02_CLOSED=true`, `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. Production collision domain도 미해결이다. 이 미해결 상태가 trajectory-independent electronic adapter 구현을 막는 것은 아니다.

현재 승인된 같은 연구 브랜치의 additive namespace를 사용하고 기존 Google Drive+Dropbox 이중 백업을 이어간다. 게시 직전 HEAD를 다시 읽고 다른 작업을 보존한다. ACK/object ID/size가 닫히면 동일 bytes를 즉시 재다운로드하지 않는다. UPLOAD_VERIFIED와 RESTORE_VERIFIED를 구분한다. 완료된 C2a–e scientific evidence를 무관한 새 이름으로 재실행하지 않는다.
