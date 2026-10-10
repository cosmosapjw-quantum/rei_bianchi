# Codex handoff — integrated PR96 + PR94 + PR95

다음 작업은 `cosmosapjw-quantum/rei_bianchi`의 격리 branch `codex/physical-provider-integration-20261010`에서 시작해. 검증된 integration code head는 `7346bea6f6b08165bd64d742ec684bd06caf6318`이다. 원격 draft PR의 최신 head와 이 commit의 ancestry를 먼저 확인하고, merge/main/release는 자동 수행하지 마.

## 반드시 보존할 source identity

- PR96 conditional warm provider: `528bb69a24ce9345efec78c6d406d3c392e2671d`, scientific commit `446c1263e1c4300fde0b860f221e0053568f4e00`, base PR93 `17bd1cc0ce1484ee61cac60ab1bda207ae264381`.
- PR94 thermal-underflow guard: `2ee78d593f97f715495f38e629678f5affba5750`.
- PR95 current-field selected-He closure guard: `73bd78d051ba448cfa71d638615e2c360b37c86d`, base PR92 `beaaf68595f5ab493654b812d66a4fa3e3177d84`.
- Original PR96 manifest SHA-256: `b4cdad70c5ed64b2c127aea79b96876ce2417f80e160b47efb0ce61451d7d5c5`; 87/87 payloads including NPZ were rehashed successfully.

먼저 `research/physical_provider_integration_20261010/INTEGRATION_REPORT_KO.md`, `VALIDATION.json`, PR96의 `CONTRACT.json`, `independent_review.json`, `SOURCE_MANIFEST.json`, `RUN_STATE.json`, 그리고 production `axisym_contract.rs`/`axisym_coupling.rs`를 읽어. PR96 원 evidence를 수정하지 마.

## 정확한 claim boundary

PR96은 실제 coupled 연구 실행이다. HM12 UVB는 photon IC만 만들고, 별도 emissivity가 stage source다. 각 stage에서 `N_rel=a_rel^3 n`, `E=qR`, 방향 Jacobian `R^-3`, 동일 opacity/source time, thermal/binding 분리와 recombination escape **energy only**를 유지한다.

그러나 이것은 `z_a=5.807`, `T_i=50000 K`, dust+Lambda test-field, warm homogeneous H/He, CR/RCT/HH OFF, primary-only Case-A escape의 조건부 lane이다. cold primordial IGM/REC IC, low-energy CR deposition, secondary/Compton, diffuse photon count/spectrum/reabsorption, 장기 history, observational Bianchi calibration 또는 production `PhysicalHistory`를 승인하지 않는다.

PR95는 stale cached residual만 고친다. 기존 `64*EPSILON`, naive summation, relative mutable REC path를 physical policy로 승격하지 마. PR94/95는 sibling이며 선형 stack으로 재작성하지 마. Remote CI runs `38031760491`, `38031762177`는 inherited fmt에서 실패하고 tests가 skipped 됐다.

## 다음 bounded task

사용자가 **warm PR96 lane의 production wiring**을 선택하면:

1. 기존 `PhysicalHistory` guard를 우회하지 말고 `SourceBoundConditional` 또는 동등하게 명시적으로 분리된 contract/provider를 추가한다.
2. frozen PR96 bytes·background·IC·closure를 실제 production consumer가 읽도록 연결한다.
3. 동일 17 epochs의 한 interval만 frozen `extended.json`과 비교한다. research executable 재실행만으로 production integration이라 주장하지 않는다.
4. current-field compensated conservation와 owner-adopted tolerance를 별도 결정한다. PR95의 `64*EPSILON`/naive sum을 자동 상속하지 않는다.

사용자가 본래 **low-energy CR primordial-IGM** 목표를 선택하면, 위 warm lane을 CR 결과로 이름만 바꾸지 말고 먼저 다음 owner inputs를 고정한다:

1. exact CR injection/deposition provider bytes, spectrum/normalization, clock/units/error;
2. secondary-electron H/He ionization/excitation/heat partition;
3. REC/HyRec cold IC and an atomic/thermal provider valid below FT03's `30000 K` guard;
4. active UVB role (external field, emissivity-to-transport, comparison-only 중 하나)와 double-counting 금지;
5. C1/C2/C3 closure, emitted recombination photon fate, `>50 keV` boundary and adopted physical tolerances.

미서명 physics/accuracy choice가 있으면 documentation proposal로만 남기고 실행을 `HOLD`해. 새 long history, scan, optional channel, tolerance/default change를 수행하지 마.

## 시작 명령

```bash
git fetch origin codex/physical-provider-integration-20261010
git switch --detach 7346bea6f6b08165bd64d742ec684bd06caf6318
sha256sum research/physical_provider_20261010/SOURCE_MANIFEST.json
cargo test --locked --manifest-path research/physical_provider_20261010/native/Cargo.toml
cargo test --locked --manifest-path rust/rei_microphysics/Cargo.toml --test axisym_coupling
cargo test --locked --manifest-path rust/rei_rec_source_adapter/Cargo.toml
```

전체 11-history 재생산은 source/consumer가 바뀌지 않았다면 반복하지 마. 변경 범위만 검증하고, 최초 failure·명령·exit·CPU/wall·source hashes를 보존해. 상태는 `PROPOSAL`, `NOT_RUN`, `PARTIAL`, `FAIL`, `SCOPED_PASS`로 제한해 보고해.

