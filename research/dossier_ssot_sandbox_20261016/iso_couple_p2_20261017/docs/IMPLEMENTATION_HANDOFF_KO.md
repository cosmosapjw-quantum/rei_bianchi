# `ISO-COUPLE-P2` 실행 계약

**범위:** 원본 Grackle/Verner/Savin/DAtomicProvider와 HHeModel/igm_thermal(극한 비교)을 동결된 `owner_src/`로 import한 standalone Rust reference. `src/full_network.rs`가 P2의 유일한 신규 결합 소유자이다. `src/igm_state.rs`는 **HHe-only 검산 어댑터**이며 source owner module은 아니다. `MixtureState`는 PR179에서 고정한 13종 EOS를 그대로 유지한다.

**기본 입출력:** `FullState{gas:MixtureState,photon_bins: Vec<PhotonBin>,escaped_j_m3,cmb_reservoir_j_m3,elapsed_s}`. `NetworkConfig`는 `DAtomicProvider`, `CxOwnership=ThermalSubstep`, `photon_source`, `cmb_temperature_k`와 opt-in 채널별 스위치를 가진다. `step`과 `run_substeps`는 성공 시 새 FullState 및 EventBudget, 실패 시 typed `NetworkError`만 반환한다. 초기값 불변. 허용된 photon bins <=64, E∈(0,5×10^4] eV, n_gamma>=0, T∈[Savin::MINIMUM_K,Savin::MAXIMUM_K], nonnegative nuclei, fixed proper volume.

**Source binding:** 10개 Git blob SHA는 `evidence/SOURCE_IDENTITY.json`, PR150 `da4bd0b9...`에서 read-only이다. Rust edition2024, version1.94.1. Library/Drive/GitHub root에서 복구할 때 original source 10개를 bytewise 보존한다. HHe source `igm_thermal.rs`는 자체 `igm_state` adapter를 통해 **순수 H/He 극한의 native comparison**에 실제 사용된다.

**동작:** H/He PI vs D PI는 하나의 photon pool에서 네 채널로만 이벤트를 분배. Grackle CI/RR/DR/CE 및 DAtomic RHS는 같은 기체 T, n_e의 source native rate; free-free/CMB는 한 global owner. CX는 `ThermalSubstep`만 실행하며 DAtomic RHS CX=Disabled, atomic+substep 중복 적분 거부. 증가 에너지와 photon/escaped/CMB reservoir를 함께 폐쇄. Case A RR photons only escape, no rediffusion.

**명령:** 아래를 패키지 루트에서 실행. 인터넷 설치 및 NCP/Ubuntu local 접근 없음.

```
source '/mnt/data/rust_1_94_1_env(6).sh'
export CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0
bash scripts/RUN_P2.sh
```

스크립트는 `python3 scripts/check_source.py`, `cargo test --offline --locked`, `cargo clippy --all-targets --offline --locked -- -D warnings`, `cargo run --release --offline --locked --example p2_campaign` 및 `python3 scripts/analyze_campaign.py`를 실행하고 byte-identity/검증 결과를 인쇄한다. 새로운 Rust 소스만 rustfmt 검사하고 `#[path]`로 참조한 소스의 바이트는 그대로 유지한다.

**물리/수치 gate:** full source-native external provider coefficients PASS; 56 targeted tests PASS, 45 actual manufactured histories PASS; 1차 정밀화와 total/photons ledger만 PASS_SCOPED. 원본 owner transfer 최신 PR과의 자동 편입, source-on photon births와 radiation redshift, 전역 chemical timed integration, free/HE ionized diffuse photon, full Bianchi/Thomson τ/observation은 NOT_RUN/HOLD. 학술 claim은 JSON per observable.

**후속 명령:** P3에서 실물 MD14/BB50k photon emissivity와 covariant q-reference source-age clock을 adapter로 물리고, Δt→0, q-resolution, angular/age 보정/isoHB 짝 비교를 허용된 샌드박스 범위로 진행. BI-SIGNED의 production convergence는 별도 source-bound 실행 필요. 절대 예전 full NCP 캠페인을 검산만을 이유로 재실행하지 않는다.
