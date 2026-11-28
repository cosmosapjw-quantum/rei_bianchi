# HE29 선택적 packed JVP bridge

이 crate는 기존 HE29 VigilODE bridge에서 C 경계와 sequential RODAS5P–GMRES 호출을 재사용한다. 새 ABI는 2이며 기존 `He29Stats` 메모리 배치를 유지한다. `he29_vigilode_segment`는 paired 비교용 기존 foreign JVP 경로이고, `he29_vigilode_segment_packed`는 같은 integrator에 native packed JVP를 공급한다. VigilODE 의존성은 `a21d573980f66fe02891bd216153443b5352f921`로 유지한다.

## 입력과 연산

상태 차원은 `n = 4 + K + 19`, `K > 0`이다. `prepare_jac`는 물리적 Jacobian의 gas 열을 `gas[n,4]`에, photon 열의 비영 항을 `photon[12,K]`에 C row-major로 쓴다. photon 행 순서는 gas 0–3, photon 대각, ledger 2·3·4·5·6·7·10이다. callback은 모든 저장 칸을 유한한 binary64 값으로 채워야 한다.

각 JVP는 기존 계산 순서로 `direction = v * scale`, 물리적 CSR 열 순서의 `sum`, `(dt * sum) / scale`을 수행한다. gas 열 0–3을 먼저 더하고 photon 열을 오름차순으로 더한다. 명시적 FMA, fast-math, 근접 상태 간 Jacobian 재사용은 없다. `u.to_bits()`와 상태 전체의 비트가 같을 때만 준비된 payload를 재사용한다. 새 segment마다 cache를 새로 만들며 준비 오류는 이후 호출에서도 보존한다. direction overflow는 준비 callback 전에 처리한다.

`threads=1`이 기본 비교 경로다. 선택값 2·4는 준비가 완료된 후 독립 photon 출력 행만 Rayon으로 계산한다. gas·ledger의 각 행 안 덧셈 순서는 고정되고 foreign callback은 순차 caller thread에서 실행된다. 전체 물리 solver나 native owner에 대한 동시 접근을 추가하지 않는다.

## 결과와 범위

외부 허용치는 기존 scaled state의 `rtol=1e-10`, `atol=1e-12`이고 GMRES 설정, 정상화 시간 `u∈[0,1]`, 출력 endpoint `[0,1]`, dense output 비사용도 그대로다. packed preparation 횟수와 native JVP 시도·완료 횟수는 JSON telemetry에 분리된다. `stats.callback_jvp_calls`는 실제 foreign per-vector JVP 호출만 세므로 packed 경로에서 0이다. `packed_workspace_bytes`는 주 배열 저장량으로, thread pool·allocator를 포함하는 RSS 상한이 아니다.

원래 네 Radau+DOP853 기준해와 기존 scientific admission은 이 crate에서 변경하지 않는다. 새 커널 검증, 분석적 합성 사례의 ABI 검증, 실제 HE29 반환의 source/table/관측량 분석은 별도 상태로 기록한다.

## 재현 build

`../ncp/build_bridge.py`가 게시된 BASS_HE의 clean checkout에서 필요한 다섯 소스를 새 외부 작업 디렉터리로 복사하고, Git에서 위 pinned VigilODE commit을 준비한 뒤 `cargo build --release --locked --lib`만 수행한다. `--source-revision`에는 해당 게시본의 전체 40자리 SHA를 전달한다. 이미 있는 clean VigilODE checkout은 `--vigilode-checkout`으로 재사용할 수 있다. Cargo.lock은 기존 bridge의 잠긴 graph를 재사용하며 이미 존재하던 Rayon 1.12.0을 직접 의존성으로 명시했다.

```bash
python research/he29_survival_budget_20261018/optimization_20261020/ncp/build_bridge.py \
  --out "$FRESH_BUILD_DIRECTORY" \
  --source-revision "$PUBLISHED_BASS_SHA"
```

Rust/Cargo 1.94.1, generic `x86-64`, `panic=unwind`를 사용한다. 실제 compiler, Cargo, 옵션, stage/source 해시와 새 실행 로그는 `evidence/`에 보존한다. 새 kernel 검사 7/7과 이후 형식 검사 1/1은 완료됐으며 다음 NCP 빌드는 이 검사를 자동 반복하지 않는다. `BUILD_IDENTITY.json`이 현재 라이브러리의 정체성이고, `RUST_DELIVERY.json`이 처음 검사한 라이브러리와 최종 라이브러리의 증거 관계를 기록한다. 현재 이 디렉터리의 빌더 경계 검사는 subprocess 시뮬레이션이며 실제 NCP 실행 결과가 아니다.

C 호출자의 유효한 포인터·배열 길이·비중첩·callback 수명 계약은 `include/he29_optimized_bridge.h`를 따른다. foreign 예외·잘못된 주소·process abort는 C 경계에서 복구할 수 없다.
