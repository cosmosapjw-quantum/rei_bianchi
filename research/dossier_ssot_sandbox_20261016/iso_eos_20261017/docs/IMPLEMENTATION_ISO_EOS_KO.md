# ISO-EOS 구현·수용 명세

- 구현 위치: `rust/rei_iso_eos_reference/src/mixture_eos.rs`. 원본 `owner_src/{deuterium_charge_exchange,deuterium_thermal_charge_exchange,isotope_state}.rs`는 현재 생산자 PR150 Git blob과 바이트 동일, `source_metadata/deuterium_thermal_coupling.rs`는 논리 경계만 읽는다.
- 타입 `MixtureState`, `EosSnapshot`, `CxEvent`, `CxInstantaneous`, `CxOwner`, `MixtureCxReference`, `MixtureError`. `source`, `defect` 및 공용 전자 중복부과 오류는 명시적으로 검사. Photon/CMB/freefree 원장은 이 H/D CX 사건에서만 0; 전체 물리 모형의 해당 항이 0이라는 주장이 아님.
- `MixtureState::eos()`는 native `IsotopeNumberState::moments()` 및 `thermal_particle_density_all_thermal_m3()`에 연결한다. 별도 중복 n_e input이 주어지면 정확한 일치가 아니면 거부한다.
- `MixtureCxReference::apply_extent()`는 제한된 단일 extent에서 H⁰, H⁺,D⁰,D⁺만 변화시킨다. 외부 반응률·시간 stepper는 수행하지 않는다. 방관자의 전하와 열용량은 변경하지 않는다. 비영 event에서는 Savin domain 2.7..2e5 K 검사를 각 양끝에 수행한다.
- `MixtureCxReference::savin_rhs()`는 원본 소스 `Savin2002::rates`를 그대로 호출한다. 사용자가 `rate_source`를 다르게 표기하면 오류; 그러나 별도 D binding-energy 실제 공급자 연결은 미완료.
- `temperature_derivative()`는 `Θ`, 다른 사건 `Q_other`, 화학적으로 생긴 열적 입자수 `R_part`, CX `R_CX`를 분리하여 받는다. `Q_other`는 CX 항 제외해야 하며, `R_part`는 순수 CX만 반영하면 0이다.
- 검증: source snapshots 4/4 blob SHA; Rust offline tests 20/20 PASS (그중 결정적 256개 조성·extent 벡터), `cargo clippy -- -D warnings` PASS with **one narrowly scoped allow on unmodified inherited owner source**; original full production lint certification과 다름; Rustfmt 신규 소스만 검사; 13-row manufactured sweep matches capacity analytic relation.
- 실제 요청한 native `ThermalCxComponent::thermal_substep`는 He 방관자에 대해 `UnsupportedSpectator`를 유지한다. 다음 노드 `ISO-COUPLE`에서 photon/CI/RR/CX 동시 사용 소유권 및 timestep/integrator 계약을 별도 통합한다. `FLRW-CONV`,`BI-SIGNED`, `ISO-RUN`,`REL-GATE`는 여전히 HOLD.

실행: `bash scripts/RUN_STAGE.sh` (Rust 1.94.1, --offline --locked). 주의: `rustfmt`는 `#[path]` 원본 모듈까지 탐색할 수 있으므로 `cargo fmt`로 전체 crate를 무심코 포맷하지 말 것. 실증된 실패·복구 로그와 실제 SHA를 저장한다.
