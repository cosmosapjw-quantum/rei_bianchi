# C2f finite-frame API

이 모듈은 유한한 weighted frame의 선택·guard 의미와 projector transport를 구현한다. 분자 Hamiltonian을 풀지 않으며 continuum gap, 실제 원자 channel correlation, collision coverage 또는 D1/Eq55의 유효성을 인증하지 않는다. 입력 에너지·잔차·sector 라벨과 source identity는 호출자가 제공한 선언이다. SHA 형식 검사는 원본 데이터와의 byte binding을 대신하지 않는다.

## 주요 객체와 호출

```python
from projector import (
    StateID, StateRecord, Role, Representation, Snapshot,
    TargetSpec, TargetKind, ValidationTolerances,
    validate_snapshot, parallel_transport,
)

# 모두 synthetic finite-Hilbert 예제용이다. 물리 tolerance로 재사용하지 않는다.
tolerances = ValidationTolerances(
    gram_atol=1e-10,
    degeneracy_atol=1e-12,
    residual_max=1e-10,
    external_gap_min=1e-8,
)

# vector column 순서와 records 순서가 일치해야 한다.
state = StateRecord(StateID("source-local-state-001"), m=0,
                    energy=-0.5, residual_norm=1e-14,
                    role=Role.SELECTED, is_ground=False)

# 실제 Snapshot은 complex128 N×n vectors와 float64 N-vector weights,
# tuple[StateRecord, ...], Representation을 받는다.
# 각 ndarray는 유한하고 weights는 양수여야 한다.
# Snapshot(coordinate, vectors, weights, states, representation,
#          selected_projected_operator=None)

# raw selected frame V에서 계산한 Hermitian form V† W H V가 있을 때만
# selected_projected_operator에 k×k complex128 행렬을 넣는다.
# 단순 energy diagonal을 이 인자에 넣어 실제 projected H라고 선언하지 않는다.

target = TargetSpec.large_R_rank5()
# counts=(m=0:3, +1:1, -1:1), full-energy candidate, ground excluded.
# 이 factory는 finite-R correlation 또는 실제 rank-5 isolation을 입증하지 않는다.

# diagnostics = validate_snapshot(snapshot, target, tolerances,
#                                 backend="reference")
# result = parallel_transport(previous, current, target, tolerances,
#                             sigma_min=0.2, backend="reference")
# result_native = parallel_transport(previous, current, target, tolerances,
#                                    sigma_min=0.2, backend="native",
#                                    native_library="/absolute/path/kernel.so")
```

`Representation`의 필수 필드는 다음과 같다.

| 필드 | 의미 |
|---|---|
| `embedding_id` | 실제 공통 row/basis embedding identity |
| `metric_id`, `weights` | 내적 정의 identity와 정확한 동일 positive diagonal metric |
| `hilbert_space_id` | 유한 표현이 속하는 Hilbert-space 명세 |
| `energy_convention_id`, `energy_unit` | 에너지 원점·규약과 단위 |
| `coordinate_unit`, `Snapshot.coordinate` | 좌표 단위와 값; 생산 R 범위를 자동 생성하지 않음 |
| `source_id`, `source_sha256` | 입력 출처와 lowercase SHA-256 선언 |
| `spectrum_coverage` | `finite_full_ambient` 또는 `finite_sector_subset` |
| `sectors_present` | 실제 supplied state의 서로 다른 m 값 tuple |
| `axial_real_spinless` | ±m 동등성 검사를 허용하는 명시적 물리 가정 |
| `continuum_threshold` | 입력 energy convention에서 선언된 threshold; 인증값 아님 |

`TargetSpec(name, kind, sector_ranks, excludes_ground, selection_basis)`의 `kind`는 `TargetKind.FULL_ENERGY` 또는 `TargetKind.SYMMETRY_BLOCKS`다. rank-5 factory 이외의 목표는 정확한 sector count와 선택 근거를 직접 등록한다. 임의의 복소 `U(k)` gauge로 섞인 출력 열에 개별 m/eigenstate 라벨을 재부착하지 않는다. 입력 sector 라벨 자체가 올바른지는 실제 solver와 symmetry operator가 따로 검증해야 한다.

## 선택과 guard 검사

모든 selected/guard 열을 합친 Gram 행렬을 검사하므로 selected–selected, selected–guard, guard–guard 중 어느 중복도 통과하지 않는다. 허용 기준은 `||G-I||₂ <= gram_atol`이며 elementwise maximum으로 rank 결손을 숨길 수 없다. 수정 없이 이 검사를 실패시키며, selected/guard 각각의 선언된 `residual_norm <= residual_max`도 요구한다.

Full-energy target은 supplied 모든 sector의 selected–guard energy difference를 검사한다. `known_degenerate_partners`가 선택에서 누락되거나 명시적 axial symmetry의 ±m partner energy/count가 맞지 않으면 거절한다. Symmetry-block target은 같은 m의 boundary만 검사하므로 다른 sector와 같은 에너지를 가지는 direct sum을 full-H energy projector라고 부르지 않는다. 내부 splitting이 0인 것은 허용하며 외부 guard boundary와 구별한다.

관측된 boundary gap이 `max(degeneracy_atol, external_gap_min)` 이하면 거절한다. 이는 supplied finite 값과 등록 문턱의 검사이고 연속 연산자의 spectral lower bound가 아니다. Guard가 없거나 해당 sector가 빠졌다면 진단에 `None`/불완전 상태를 남긴다. 순수 기하학적 frame transport는 가능하지만 isolation이나 path continuity를 인증하지 않는다. `supplied_frame_spans_finite_ambient`도 단지 supplied column 수·Gram·coverage 선언의 일치이며 continuum claim이 아니다.

## 명시적 Gram 정규화와 transport

`transport_frames(u, v, weights, *, sigma_min, gram_atol, backend, native_library=None)`는 저수준 선형대수 primitive다. 호출자가 공통 embedding을 먼저 확립해야 한다. `parallel_transport`는 source metadata, embedding/metric/Hilbert identities, 단위·energy convention·threshold와 **weights의 정확한 array equality**를 먼저 확인한다. 서로 다른 mesh의 계수 dot product를 공통 물리 내적으로 간주하지 않는다.

허용된 작은 Gram defect에도 raw frame에서 계산한 `V-U(U†WV)`는 정확한 projector residual이 아니다. 따라서 이 API는 알고리즘 일부로 다음 정규화를 **명시적으로 수행하고 결과에 기록**한다.

\[
G_U=U^\dagger WU,\quad C_U=G_U^{-1/2},\quad \widehat U=UC_U,
\qquad \widehat V=VC_V.
\]

입력 배열을 수정하지 않고, tolerance 밖의 frame을 몰래 복구하지 않는다. 수치적으로 positive definite인 Gram만 허용한다. 반환값에는 원 Gram, inverse-square-root 행렬, 정규화 correction norm, `normalization_policy`가 담긴다.

\[
M=\widehat U^\dagger W\widehat V=A\Sigma B^\dagger,
\quad Q=BA^\dagger,\quad V_{aligned}=\widehat VQ.
\]

등록된 양수 `sigma_min`에 대해 실제 최소 singular value가 **엄격히 큰 경우에만** 반환한다. `right_rotation=Q`, `source_basis_transform=C_VQ`이므로 `current.selected_frame @ source_basis_transform`이 반환된 aligned frame과 일치한다. 이는 개별 eigenvector rephasing 규칙이 아닌 전체 `U(k)` gauge에 대한 공변적 연산이다.

Weighted Euclidean representation에서

\[
Z=W^{1/2}(\widehat V-\widehat U M),\quad
\|P_U-P_V\|_2=\|Z\|_2,\quad
\|P_U-P_V\|_F=\sqrt2\|Z\|_F.
\]

수치 상쇄가 큰 `sqrt(1-sigma_min²)` 대신 이 residual을 사용한다. Principal angles는 residual singular values와 overlap singular values를 적절히 정렬해 `atan2(sinθ,cosθ)`로 구하므로 tiny-angle 정보를 유지한다. 동일 subspace에서 남는 machine-roundoff 바닥은 물리 오차가 아니다.

## 작은 연산자와 라벨의 의미

`SnapshotTransport.source_state_ids`, `source_energies`, `source_residual_norms`는 변환 전 입력 record를 보존한다. 출력 `aligned_column_labels`는 `transported_frame[i]`이며, `aligned_columns_are_individual_eigenstates`는 항상 false다.

- `selected_projected_operator=Hsmall=V†WHV`를 제공했다면 반환 행렬은 `(C_VQ)† Hsmall (C_VQ)`다. 허용 energy tolerance 안의 Hermitian 반올림 오차만 대칭화한다. `actual_operator_projection_supplied=true`는 호출자가 그 의미로 입력을 제공했다는 상태이며 H action을 별도로 검증했다는 뜻이 아니다.
- 그 행렬이 없으면 반환 행렬은 정규화된 source frame에 **명목상 부여한** `Q†diag(E)Q`다. 실제 raw frame으로 계산한 Ritz operator라고 주장하지 않으며 `reduced_operator_semantics`에 이 차이가 명시된다.

두 경우 모두 `actual_ritz_residual_certified=false`, `continuum_certificate=false`다. 특히 nonorthonormal raw vector와 eigenvalue 목록만으로 실제 `V†WHV`를 재구성할 수 없다.

## Backend와 실행 경계

`weighted_overlap(u,v,weights,*,backend,native_library=None)`만 heavy overlap kernel을 dispatch한다. Reference는 NumPy binary64, native는 explicit library의 `native_overlap.overlap`이다. `auto` backend, native 경로 누락, reference에 native 경로 혼합을 거절하고 native 실패 때 reference로 fallback하지 않는다. 작은 Gram eigensystem과 SVD는 두 backend에서 같은 NumPy 선형대수 경로를 사용한다.

독립 MPI 작업이 여러 프로세스로 실행될 때 BLAS thread 수를 외부 launcher에서 제한한다. 이 파일은 process-wide thread 환경변수를 import 시점에 바꾸지 않는다. NCP64 성능이나 실제 cloud topology는 여기서 가정하지 않는다.

저자 검사는 다음처럼 **새 manufactured tests만** 실행한다.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python tests/test_projector.py
```

이 API는 입력/결과 file writer가 아니다. Root runner가 exact input identity, backend/library identity, 실행환경, 등록 계약, 결과를 atomic write+fsync로 보존한다.
