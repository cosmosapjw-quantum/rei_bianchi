# C2f native weighted overlap 구현 기록

범위는 manufactured complex frame의 $U^\dagger W V$ 계산이다. 실제 전자 Hamiltonian 고유값 계산, 연속체 gap 인증, 충돌 궤적 계산, D1/Eq55 실행 또는 NCP 64코어 성능 인증은 수행하지 않았다.

## API와 입력 의미

`native_overlap.overlap(u, v, weights, *, library=...)`는 complex128 `(N,k)`, `(N,l)` 프레임과 float64 길이 `N`의 양의 유한 가중치를 받아 complex128 `(k,l)` 행렬을 반환한다. 입력 precision을 자동 변환하지 않는다. 배열 차원, 유한성, 양의 metric, native identity, 실행 thread 설정을 확인하며 backend fallback은 없다. 가중 직교정규성 또는 물리적 rank는 이 저수준 overlap kernel이 판정하지 않는다.

`native_overlap.identity(library)`는 실제 binary SHA-256/크기, 실제 Fortran source SHA-256, binary에 삽입된 source digest, ABI, binary64/complex128 저장 크기, 고정 build flags를 검사한다. compiler wrapper와 실제 Fortran frontend의 SHA, 버전, target은 build JSON에 보존된다. 이는 지정된 build artifact의 provenance 검사이며 임의 공격자에 대한 코드서명 체계라는 주장은 하지 않는다.

## 계산 순서와 정확도 범위

실수부와 허수부를 분리하여 각 행의 복소 곱을 binary64에서 계산한다. 최종 구현은 행들을 고정된 8개 lane으로 나누고 각 lane의 합과 보정항을 Neumaier 방식으로 유지한다. `MERGE`는 큰 절댓값 피연산자와 작은 피연산자를 고르는 데만 사용한다. 따라서 순서를 재배열하지 않고 각 lane의 보정 덧셈을 SIMD로 수행할 수 있다. 마지막에는 각 lane의 합과 보정항을 **별개의 항**으로 고정 순서에 따라 다시 보정 합산한다. 합과 보정항을 미리 반올림해 더하면 lane 간 상쇄에서 작은 보정이 손실될 수 있어 금지했다.

OpenMP는 서로 다른 출력 행렬 원소만 분배한다. 한 원소의 합산 순서는 thread 수에 의존하지 않는다. GNU Fortran의 실제 vectorization report에서 8-lane update loop의 16-byte SIMD를 확인했다. 마지막 소규모 보정 병합이 vectorized되지 않는 것은 의도된 범위다. `-fno-fast-math`, `-fno-associative-math`, `-ffp-contract=off`, `-fprotect-parens`가 고정되어 있고 외부 FFLAGS/FCFLAGS/LDFLAGS는 거부한다.

보정 합산은 binary64에서 이루어지며 정확 산술 또는 임의 입력에 대한 error certificate가 아니다. 곱셈 자체의 반올림 오차를 제거하지 않는다. 유한 입력이라도 중간 곱이나 합이 overflow할 수 있으며, 결과가 비유한이면 명시적으로 실패한다. 해당 오류 경로를 시험했다. 출력의 조건수가 매우 나쁜 임의 입력에서 reference와 항상 bitwise 동일하거나 모든 다른 합산보다 정확하다는 주장은 하지 않는다.

## 메모리와 실행 제약

대형 `(N,k,l)` 임시배열을 만들지 않는다. Fortran column-major 보장이 없는 프레임은 `O(N(k+l))` 복사할 수 있고, 출력은 `O(kl)`이다. 각 OpenMP worker의 accumulator scratch는 고정 8-lane 배열이다. API의 입력 유한성 검사, identity 검사 및 필요한 데이터 복사 비용도 public-API benchmark에 포함해야 한다.

`OMP_NUM_THREADS`는 명시적 단일 양의 정수, `OMP_DYNAMIC=FALSE`는 필수다. 실제 생성된 team size가 요청과 다르면 결과를 거부한다. 향후 NCP 레이아웃을 위해 kernel 자체에 4-thread 상한을 넣지 않았다. 실행자가 실제 자원 preflight와 rank×thread budget을 적용해야 한다. 이 노드의 검사에서는 OpenMP 1/4 threads, BLAS 1 thread만 사용했다.

## 증거와 변경 이력

- 최초 scalar fixed-order Neumaier 구현: `native/baseline_v1/MANIFEST.json` 및 보존된 source/adapter/strict/debug binary. 최초 native 검사는 15개 PASS였다. root의 동일 작업량 benchmark가 최적화 계기를 제공했다.
- 첫 8-lane 시도: `native/build-v2/FIRST_ATTEMPT_SOURCE.f90`. 17개 정확도 검사는 PASS였으나 조건부 부동소수점 표현 때문에 실제 SIMD가 생성되지 않았다. 이 실패한 최적화 근거를 보존했고 이 시도에 대한 속도 주장은 없다.
- 최종 8-lane 구현: `native/build-v2b/libbass_overlap.so`, `native/build-debug-v2b/libbass_overlap.so`. 고정 피연산자 선택 후 보정식 계산으로 SIMD가 생성되었다.
- 최종 검사: `native/build-test-evidence-v2b/TEST_REPORT.json`, `TEST_LOG.txt`. 17개 PASS, 정확한 source/adapter/test/strict/debug binary identity 포함.
- 검사 내용: 해석적 복소 nonuniform metric, `math.fsum` 독립 scalar reference, 큰 수의 상쇄, mixed-exponent 상쇄, lane 보정항의 조기 반올림 방지, strict/debug bitwise parity, 독립 subprocess 1-vs-4-thread bitwise parity, shape/precision/metric/유한성 거부, binary/flag 변조 거부, 누락된 실행 설정과 library의 fail-closed 처리.

성능 선택은 root가 별도로 기록하는 동일 작업량 public-API 측정 결과를 따른다. 이 구현 기록 자체는 native가 reference보다 빠르다거나 production default로 승격되었다고 주장하지 않는다.
