# Sequential source closeout (C1b)

Parent: `02634b078743f3556c569cc30f17322b11f2ce8a`.

사용자 결정: 여기에서 승인된 source 범위를 순차적으로 끝내고 local Codex 인계는 마지막 한 번만 한다. 이 follow-up은 새로운 연구단계나 local 검증 C2가 아니다.

## 원인과 수정

일곱 함수 본체는 C1에서 모두 존재했고 C1a에서도 byte-identical이다. 미이식 kernel을 새로 만들었다고 보고하지 않는다. 다만 evaluator의 기존 `let id=t.text()?; let op=t.text()?;`가 main에 있어 ID만 있는 한 줄이 whole-process error로 전파되는 source-level 결함이 있었다. `response_line` 안에서 이를 `ID ERR BAD_SHAPE`로 변환하고 다음 줄을 계속 처리하도록 최소 수정했다. 실제 Rust 재현/수리 시험은 실행하지 않았다.

원 84개 parity 입력과 13개 integration tests를 삭제하거나 완화하지 않았다. integration 8개를 덧붙여 21개로 만들고 frontend 5개를 작성했다. Cargo example `test=true`를 추가해 이 검사들이 최종 cargo test의 대상이 되도록 했다. 근거: Cargo Book, Cargo Targets, examples의 test 필드 (2026-09-23 확인).

비선형 polynomial은 p(x)=x^3-2x^2+x/2+1을 비균일 knots [-2,1/2,4]에서 좌측 knot 기준으로 정확히 전개한 합성 coefficient-layout witness다. 새로운 PCHIP fitting algorithm이나 물리 opacity table이 아니다. 8개 sample을 유리수로 독립 검산했다. 같은 toy에서 8개 identity (telescoping 1, mass 1, signed 3, 단위 2, redshift factor 1)를 확인했다. 이는 Rust/JAX 출력이 아니다.

## 함수별 source 확인

`SOURCE_PHASE_CLOSEOUT.json`이 7개 원문 함수의 실제 line range, Rust module, 추가/기존 test 선언을 연결한다. 원문은 두 고정 Git blob이고 새 physical source는 없다. library kernel 4파일, Cargo.lock, 원 fixture, PARITY_POLICY, SOURCE_IMPORT_LOCK, C1a checker/receipt tests를 변경하지 않았다.

잔여 조건은 Rust format/type/link/runtime 및 실제 JAX/Rust f64 parity다. 특히 subnormal/FTZ/reduction/libm은 이번 static 검토로 판정하지 않는다. CLI 공통 GroupParams의 유효 table 생성 요건과 gamma 함수 자체의 table 비의존성을 구분한다. MissingAuthority와 outsideband를 0으로 바꾸지 않는다.

## 종료와 상태

승인된 일곱 함수의 source 작성 단계만 종료한다. compilation, cargo test, Python/Rust parity, production admission 및 scientific PASS는 승격하지 않는다. 이후 인계는 START_HANDOFF_KO.md 한 곳에서 최종 검증으로만 이어진다. 더 많은 physical fit/ODE/전체 reionization solver 이식을 이 종료에 포함하지 않는다.

새 worktree/clone/reset/stash/clean을 하지 않았다. 작업공간은 C1 archive에 C1a의 필요한 exact bytes를 복원한 source overlay이며 사용자 PC checkout이 아니다. native raw download는 DNS 오류였고 connector 원문으로 계속했다. Python 검증은 현재 실행 결과이며 Rust는 요청에 따라 미실행이다.

별도 reviewer는 사용하지 않았고 static self-review다. 첫 static 감사의 Rust attribute 문자열 오인은 `#[...]` 대 `#![...]` 검사 실수로 분리해 원로그에 보존했으며 production source를 변경하지 않았다.
