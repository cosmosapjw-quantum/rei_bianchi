# C2g 다중 Ritz 고유상태 제공자

`optimized_solver.solve_many(...)`는 한 m-sector의 Hamiltonian·mass matrix를 한 번 조립하고, `eigsh`를 한 번 호출하여 요청한 **모든** 고유벡터를 보존한다. 기존 C2d 구현은 `nroots=2`를 요청해도 첫 벡터만 반환했으며 두 번째 에너지·잔차만 metadata에 남겼다. C2g에서는 `1 <= nroots < matrix_dimension`을 명시적으로 확인한다. m은 0 또는 1이며 m=1 원시 상태는 정규화된 실수 cosine 대표이다. ±m 복소 상태의 구성은 공통 공간 embedding 계층이 담당한다.

## 호출 및 반환

```python
from optimized_solver import solve_many
from multistate_provider import save_sector, load_sector, validate_identity

result = solve_many(R=4.0, m=0, center="O", lmax=12,
                    rmax=20.0, elements=24, degree=4,
                    quadrature=14, nroots=6, backend="numpy")
receipt = save_sector(result, "/absolute/new/sector.npz", "R4-m0-L12")
archive = load_sector(receipt["source_path"], receipt["source_sha256"])
validate_identity(archive)
```

위 코드는 인터페이스 예시이며 실행 허가 또는 수렴 결과가 아니다. 실제 물리 계산은 별도의 사전등록 계약·검토·자원 제한을 따른다.

`MultiStateResult`의 필드는 다음과 같다.

| 필드 | 정의 |
|---|---|
| `states` | 에너지 오름차순 `PartialWaveState` tuple, 각 root의 실제 FEM 계수 포함 |
| `coefficient_vectors` | 정규화·위상 고정 후 내부 Dirichlet 자유도 벡터 C, shape `(matrix_dimension, nroots)` |
| `projected_operator` | 조립된 H로 측정한 `C.T @ H @ C`; 에너지 대각행렬을 대입한 값이 아님 |
| `mass_gram` | 조립된 M으로 측정한 `C.T @ M @ C` |
| `metadata` | source hash, backend 및 native library identity, 모든 Ritz energy·residual, 조립 조건·시간, 연산자·잔차 범위 |

C 배열을 mass norm으로 각각 정규화한 후, 각 열에서 절댓값이 가장 큰 **첫 계수**가 양수가 되도록 부호를 정한다. 이 규칙은 excited state의 양성을 가정하지 않는다. 정확하거나 가까운 축퇴 부분공간에서는 eigensolver·라이브러리에 따른 내부 직교 회전이 여전히 가능하므로 개별 위상 고정만으로 root 추적을 주장하지 않는다. source ordinal은 해당 에너지 정렬 목록의 0-based 순번이며 R 변화에 걸친 원자 상태 상관관계 식별자가 아니다.

기존 `solve(...)`는 `solve_many`를 한 번 호출한 뒤 첫 상태를 반환한다. 원래의 sector-ground meridional probe-sum 부호 규칙을 독립 계수 복사본에 적용하므로 기존 호출 형태와 ground-phase convention은 유지된다. 반환 metadata에는 요청한 모든 energy·residual이 들어가지만 여러 벡터가 필요하면 반드시 `solve_many`를 사용한다.

## 수치 잔차와 연산자 범위

각 열 c_j에 대해 저장하는 값은

\[
\rho_j = \frac{\|Hc_j-E_jMc_j\|_2}
 {\|Hc_j\|_2+|E_j|\,\|Mc_j\|_2}.
\]

이는 유한 generalized matrix 문제의 **무차원 상대 Euclidean 대수 잔차**다. PDE의 차원을 가진 residual norm이나 물리 Hilbert-space 잔차로 바꿔 해석하지 않는다. 분모가 0이거나 norm·고유쌍이 비유한이면 실패한다. 전역 tolerance 통과 여부는 별도 실행 계약이 판단한다.

Hsmall은 실제 유한 Galerkin H의 행렬 원소이며, 이 자체로 물리 PDE Hamiltonian을 공통 quadrature grid에서 다시 작용시켜 측정한 결과가 되지는 않는다. embedding 계층은 `E† W E = M`을 점검하고 어떤 유한 연산자를 옮겼는지 명시해야 한다. 이 제공자는 continuum gap, 완전한 bound spectrum, finite-R rank-five 원자 상관관계, 회전/ETF를 포함한 동역학적 sector decoupling을 인증하지 않는다. 에너지 원점은 전자 Coulomb Hamiltonian의 ionization zero이며 nuclear repulsion은 포함하지 않는다. 좌표·에너지 단위는 기존 `a_A,E_A` 계산 단위다.

## 파일 및 provenance

`save_sector`는 NPZ의 numeric arrays와 UTF-8 `uint8` JSON만 저장한다. object array·pickle·NaN JSON을 허용하지 않는다. 같은 디렉터리 임시 파일을 fsync한 뒤 atomic hard link로 최종 경로를 생성하며, 기존 파일을 덮어쓰지 않는다. 최종 파일의 bytes·SHA-256을 측정하여 receipt로 반환한다.

`load_sector`는 정확한 schema와 member set, duplicate member/JSON key, dtype·shape·유한성, 정렬·source ordinal, mass norm·Dirichlet endpoint·계수 일치, solver residual definition, source/native digest 형식을 확인한다. 압축 해제 크기는 512 MiB로 제한한다. source ID가 `R4-m0-L12`이면 상태 ID는 `R4-m0-L12:root:0000`과 같이 구성된다. archive가 포함한 source ID는 caller가 정한 실행 task ID와 같아야 하며 외부 manifest 검증은 runner가 수행한다.

`SectorArchive`는 `result`, `source_path`, `source_id`, `source_sha256`, `source_bytes`, `state_ids`, `content_sha256`을 제공한다. 배열은 읽기 전용으로 로드한다. 기존 `PartialWaveState` 호환을 위해 객체 scalar·metadata 자체는 mutable이지만, `validate_identity`는 메모리 내용 fingerprint와 실제 source file bytes를 함께 확인하여 로드 이후 변경을 거부한다.

solver의 `source_files_sha256`은 solve 전후 관찰한 `optimized_solver.py`, `native_backend.py` 파일 hash다. 이 값만으로 이미 import된 bytecode의 외부 provenance를 증명하지 않는다. 독립 프로세스 runner가 실행 전후 전체 input/source identity를 추가로 묶는다. native 경로는 `BASS_NATIVE_LIBRARY`, 선택적 expected hash는 `BASS_NATIVE_EXPECTED_SHA256`으로 명시한다. loaded library hash는 기존 strict native build manifest와 함께 기록되며 solve 종료 시 실제 파일 hash와도 비교한다. 암묵적 numpy fallback은 없다.

## 성능 및 검증

기존 Fortran binary64/OpenMP element assembly와 Gaunt-table cache를 재사용하며, 추가 root마다 H/M을 재조립하거나 factorization을 별도로 요청하지 않는다. 각 열의 Hc/Mc와 small Gram/Hamiltonian은 block sparse-dense 연산으로 계산한다. fast-math나 정밀도 축소를 새로 넣지 않았다. 실제 처리량 향상은 동일 workload의 backend/layout 측정 결과로만 판단한다.

새 테스트 12개는 정확한 제조 generalized diagonal problem, mocked `eigsh` one-call/root retention, phase·sorting·algebraic residual, nroots 범위, legacy phase wrapper, source/bytes·memory binding, create-only save, object array·duplicate JSON·nonfinite/provenance 거부를 다룬다. 이 테스트에서 물리 분자 eigensolve는 실행하지 않았다. `results/multistate_tests_final.txt`가 실행 기록이다.
