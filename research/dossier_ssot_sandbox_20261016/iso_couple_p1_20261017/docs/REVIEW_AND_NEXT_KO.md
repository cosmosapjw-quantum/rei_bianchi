# ISO-COUPLE 국소 검토 및 후속 DAG

**검토 방식:** native_subagent `NOT_RUN` (host lacks native spawn facility). 1회 local source-to-code adversarial pass: equations, repository identical bytes, owner alias, source/temperature units, transaction, dt and CMB/FF/photon ownership. 원 코드 보호를 위한 독립 branch만 기록하며 production native의 과학 인증을 주장하지 않는다.

## 관측된 결함과 교정

1. 최초 1차 implicit Euler full/half scheme이 엄격한 오차 기준에서 `WorkLimit`를 유발. 기존 owner가 이미 검증한 Heun full/two-half 구조로 변경. 오차 목표/원본 rate/domain 불변.
2. 첫 Heun port에서 `second_euler=z+h*g1`가 첫 Euler 기울기 `g0`를 누락해 source RHS의 절반 변화량 생성. `e=z+h*g0; v=e+h*g1; z_next=(z+v)/2`로 교정. 초기 실패 로그를 삭제하지 않음.
3. 원본 `rate_table.rs`의 Rust1.94 Clippy 2건과 `deuterium_thermal_charge_exchange.rs` 1건은 원본 소스 바이트를 보호하기 위해 `#[path]` import에만 `#[allow]` 적용. 새 코드 자체의 `-D warnings` PASS, 원본 전체 crate Clippy와 무관.
4. 비평형 정확도와 반응 fit model 정확도를 구분. 2015 MNRAS deuterium ionization-correction 논문이 지적한 Savin 독립 fits 상세평형 불일치는 별도 diagnostic. 현재 native Savin 계약을 수정하지 않음.

## 수용 가능 범위

- PASS_SCOPED: source-locked `DAtomicProvider::defect()`와 original Grackle3.4.1 H-equality rates + Verner HI cross section 경로 컴파일, Savin actual rates T-dependent CX finite time, 13-state He spectator heat capacity and charge, CX ownership XOR, no clip/extrapolation, 36 full Rust tests, 36 fresh numeric cases, 8 Git blob identities.
- Only mathematical/numerical evidence: no astrophysical HII or optical-depth prediction. Manufactured `chi_D-chi_H=0.0037 eV` and conditional densities.
- HOLD: physical isotope threshold measured/source pin, `BI-SIGNED`, full H/He/D non-CX+CX step simultaneous temporal integrator, full photon competitive absorption, FF/CMB global shared owner, actual NCP and FLRW time/angular/source-age convergence.

## 다음 선행관계

`ISO-COUPLE-P2`: 실제 `IgmPointRhs`의 H/He species/thermal LEDGER, `d_atomic_rhs`의 D PI/CI/RR/CE 및 선택적 thermal CX source를 shared EOS state에서 유일한 트랜잭션으로 결합한다. 각 action의 물리율 범위와 가스 온도를 단일 proper-time argument로 바인딩한다. source-on photon split (absorbers HI/HeI/HeII/D) event owner, split-step LTE/stiff error, negative stage/microstate, load on original source. 그 다음 원본 DAG `BI-SIGNED`의 time/angle/energy 수렴 승인이 충족돼야 ISO-RUN로 넘어갈 수 있다.
