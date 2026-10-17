# rei_bianchi / ISO-COUPLE-P4/S2 / 2026-10-17

**이 패키지는 P3의 후속 Rust opt-in photon birth–opacity clock 독립 연구 결과다.** 원래 production PR150와 앞선 P3 source는 원형 그대로 남아 있다. 원본 Crate에서 스냅샷 복구한 12개 frozen `owner_src` Git blob, 68개 P3 테스트, 새 `positive_birth_clock.rs`, 신규 테스트 7개, source-native 32행 캠페인, analytic frozen-gas 7행 oracle과 실행 명령을 모두 포함한다.

기준: `rei_bianchi` P4/S1 [Draft PR #183](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/183) head `b0382198564c7e85e479d48011e880ef7c2c4d46`; P3 source PR #182 at `3a2721e58fc8bd68cdbbc92ca4669bd57609695b`; original production PR #150 fixed `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`.

## 실행

```bash
source '/mnt/data/rust_1_94_1_env(7).sh'  # this session's uploaded env file
bash scripts/RUN_STAGE_P4_S2.sh
```

외부 네트워크 필요 없음. Rust 1.94.1 source distribution extracted/installed at `/mnt/data/rust-1.94.1-prefix` after path inspection. Detached signature `.asc` was **not cryptographically verified** because public key 85AB96E6FA1BE5FE was unavailable, so `SIGNATURE_UNVERIFIED` is retained. `RUSTCORE(7).zip` is a separate Bianchi Rust repository snapshot, not a toolchain installer or REI source owner; no files were silently mixed into `rei_bianchi`.

## 레이아웃

- `rust/rei_iso_couple_p4_s2/`: compilable dependency-free Rust package (Cargo.toml, Cargo.lock), original `owner_src`, existing P3 tests, new opt-in source and P4 tests.
- `docs/THEORY_AND_COMPUTATIONAL_CONTRACT_KO.md`: explicit math and bounded results, failure-mode classification, science admission.
- `evidence/p4_birth_clock_campaign.csv`: 4 configurations x N8/16/32/64 x legacy P3 vs positive P4 = 32 matched actual native Rust runs.
- `evidence/p4_constant_opacity_oracle.csv`: exact Verner + H-equality D frozen-gas source analytic control, 7 step grids.
- `scripts/validate_science.py`: original P3 replay parity, photon number/energy, no negative gas/photon, completeness and source hashes; `scripts/RUN_STAGE_P4_S2.sh` carries executable test/compare commands.
- `inputs/`: original P3 frozen 32-row comparator, immutable Git owner identity, original P3 file manifest; source originals are not modified.
- `contracts/`: stages, source and claim/hold contracts.
- `manifest.sha256`: member SHA-256, excluding manifest itself.

**Acceptance:** `P4/S2 PASS_SCOPED_NATIVE_POSITIVE_CLOCK_REFERENCE`, not second-order coupled history, not continuum spectral convergence, not on-shell Bianchi or full EoR. Last comparison tracked no independent fresh-model review because native subagents are not available.
