# C2g 다음 인계 — 독립 discretization과 exterior guard

현재 stop은 `C2G_MULTISTATE_ADAPTER_AND_BOUNDED_REFERENCE_PILOT_COMPLETE`이며 다음 단일 node는 `C2H_INDEPENDENT_DISCRETIZATION_AND_EXTERIOR_GUARD_AUDIT`다. `CLAIMS.json`, `C2G_REPORT_KO.md`, `review/PRELAUNCH_INDEPENDENT_REVIEW.json`, `review/INDEPENDENT_RESULT_CHECKS.json`, 최종 결과 review를 읽고 이어간다. frozen code/manifest를 바꾸어 기존 성공 evidence를 새 hash로 꾸미지 않는다.

## 확정된 구현과 수치

solve_many는 실제 m=0 여섯 root, m=1 세 root와 그 coefficients, C†HC, C†MC, per-state algebraic residual을 반환한다. source archive는 pickle 없이 정확한 bytes/SHA/ordinal과 메모리 변경 검증을 포함한다. ±1 reconstruction과 positive physical common grid로 selected5/guard7 Snapshot을 구성했다. current common_embedding은 동일 O origin, 같은 box, m0/|m|1만 지원하며 B-centered/prolate/different-box 입력은 거부한다. 그 거부를 해제하기만 하고 raw coefficient dot을 대입하면 안 된다.

R=4,4.25 a_A; lmax12/20/28, base radial24/32/40, degree4, box20, radialquad14. 두 layout 각각12sector/54roots, 총24sector/108roots, 재구성144열이다. 모든314등록 판정이 통과했다. backend energy 차이≤2.75335310e-14 E_A, projector 차이≤1.55698630e-14. 하지만 medium→fine ΔE 최대1.10863895e-03 E_A, projector 거리6.62167901e-03로 절대 물리 오차는 아직 닫히지 않았다.

## C2h 구현·연구 순서

1. 새 namespace에서 기존 C2g coefficients를 read-only 기준으로 사용한다. rank5는 m0 ordinals1,2,3 및 ±1 ordinal0인 후보일 뿐 finite-R atomic correlation을 선언하지 않는다. 각 비교에 target/gap/observable·source-binding을 보존한다.
2. Angular, radial, box의 효과를 별도로 구분한다. lmax만 늘리는 비교와 고정 lmax에서 radial degree/mesh를 바꾸는 비교를 새 계약으로 등록한다. 이번처럼 두 축을 동시에 바꾼 차이를 한 축의 오차 추정으로 해석하지 않는다. 변경 없는 C2g 기준 solve는 다시 돌리지 않는다.
3. 독립 discretization의 실제 excited states 경로를 연결한다. 현재 prolate pair archive는 ground/realbright 첫 상태뿐이므로 rank5로 이름만 바꾸지 않는다. 새로운 provider가 필요한 모든 selected+guard를 반환하도록 먼저 구현·시험한다. 좌표 사상·출처·residual definition을 명시하고 같은 Hilbert 공간으로 비교한다.
4. 최소 |m|=2의 낮은 exterior states부터 실제 finite spectrum 경계를 점검할 수 있도록 angular/general-m provider와 ± partner 규칙을 확장한다. 이것만으로 모든 높은 m·continuum을 배제했다고 주장하지 않는다. 누락 영역에는 별도의 이론적 lower-bound/enclosure가 있어야 full-H gap certificate를 열 수 있다.
5. box20→더 큰 box 비교는 현재 embedding contract 밖이다. 내부 knots를 보존한 box 확장, 작은-box FEM 함수의 정확한 zero-extension과 공통 positive physical quadrature를 유도·구현·검증한 뒤 등록한다. r16…20 집중도 약1e-10을 box 바깥 tail 상한으로 사용하지 않는다.
6. 실행 전 exact R/tasks/basis/guard/root count/tolerances/wall-memory를 고정하고 독립 검토한다. 기준은 요구 observable accuracy와 error allocation에서 정하며 결과를 본 뒤 기준을 느슨하게 바꾸지 않는다. 최우선 stop은 새로운 독립 reference가 현재 rank5의 기저 오차와 알려진 외부 경계 충돌을 판별하는 데 충분한지다. 생산 R-domain/trajectory 선택은 여전히 별도 미해결이며 electronic adapter 자체를 막는 역방향 의존성을 만들지 않는다.

## 실행과 복구

실제 성공 출력은 `results/numpy_serial_1x1.json`과 `results/native_mpi_2x1_retry1.json`이다. 원 `results/native_mpi_2x1.json`은 mpi4py 누락으로 물리 계산 전에 실패한 기록이다. `results/campaign_ledger/AMENDED_COMPLETED.json`이 두 성공 layout의 최종 ledger다. 원 실패를 지우거나 첫 MPI 파일을 성공본으로 덮어쓰지 않는다. `contract/ENVIRONMENT_RETRY_AMENDMENT.json` 및 `review/ENVIRONMENT_RETRY_REVIEW.json`은 환경 복구 재시도만 승인한다.

새 host에서 Python/NumPy/SciPy/mpi4py/OpenMPI import와 native loader를 먼저 확인한다. 기록된 조합은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, mpi4py4.1.2, OpenMPI4.1.6이다. `requirements.txt`와 private archive dependency wheel을 보존했다. compiler profile·source/library SHA·rank별 binding·thread env·process identity는 새 host에서 다시 관찰한다. 기록된 절대 경로는 당시 evidence 경로이지 다른 host의 존재를 보장하지 않는다. 새 실행은 CLI에 새 absolute output/native path를 명시하며 이 host용 provenance helper를 NCP launcher로 오인하지 않는다.

NCP64는 미실행이다. 유효 core/NUMA/available memory를 확인하고 충분한 독립 task 수와 rank별 메모리 측정에 맞춰 rank×thread layout을 사전 등록한다. Fortran/OpenMP/SIMD와 OpenMPI는 정확도·provenance를 유지하며, backend 선택은 동일 workload의 실제 측정에 따른다. 이번1.846배는 한 번의 local combined layout 관찰이고64코어 예측치가 아니다.

## 계승 gate와 완료 조건

`CODE_I02_CLOSED=true`, `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. selected/guard gap, L² projector, finite Galerkin form을 continuum/PDE/unbounded-Ly 인증으로 승격하지 않는다.

사용자가 승인한 같은 branch additive 게시와 Google Drive+Dropbox 이중 백업을 이어간다. 게시 직전 HEAD를 읽고 다른 변경을 보존한다. ACK/object ID/size 및 commit/tree 검증이 충분하면 동일 bytes를 다시 다운로드하지 않는다. UPLOAD_VERIFIED와 RESTORE_VERIFIED는 구분한다. 연구 종료 시 주장·DAG·다음 단일 node·실패 ledger를 함께 갱신한다.
