# REI physical-provider 통합 검토

날짜: 2026-10-10 UTC  
판정: **`PROMOTE_INTEGRATION_SCOPED`**  
전역 과학 admission: **`HOLD`**  
검증한 integration code head: `7346bea6f6b08165bd64d742ec684bd06caf6318`

## 결론

PR96은 단순 제안이나 고정 photo-rate packet이 아니다. 고정된 HM12 `UVB.out`로 photon IC를 만들고 별도 `emissivity.out`를 매 stage source로 사용하며, 방향·에너지가 변하는 photon node, HII/HeII/HeIII와 thermal energy를 실제 opacity 및 기존 native atomic/AXI 함수로 함께 진화시킨 조건부 warm H/He 연구 lane이다. 저장된 11 histories와 원자료·NPZ를 포함한 PR96 manifest 87개 payload의 SHA-256을 이 checkout에서 전부 재검증했다.

동시에 이 결과는 사용자의 본래 **low-energy cosmic-ray deposition in primordial IGM** 목표를 해소하지 않는다. PR96은 `z_a=5.807`, `T_i=50000 K`, dust+Lambda test-field Bianchi-I, HM12 photon IC/emissivity, primary-only Case-A escape를 선택했고 CR/RCT/HH는 OFF다. REC 초기조건, cold mean IGM, secondary-electron/Compton, diffuse reabsorption, 장기 history와 production `PhysicalHistory`는 여전히 열려 있다.

## 병합 그래프

병합은 sibling 관계를 보존했다.

- PR96 head `528bb69a24ce9345efec78c6d406d3c392e2671d`, base PR93 `17bd1cc0ce1484ee61cac60ab1bda207ae264381`.
- PR94 head `2ee78d593f97f715495f38e629678f5affba5750`, parent PR93. Merge commit `8e949ec356a3cfa0001e8b7f946f38fa61ad2675`.
- PR95 head `73bd78d051ba448cfa71d638615e2c360b37c86d`, parent PR92 `beaaf68595f5ab493654b812d66a4fa3e3177d84`. Merge commit `7346bea6f6b08165bd64d742ec684bd06caf6318`.

PR95를 PR94의 자식으로 재작성하지 않았고, PR96 원 evidence bytes도 수정하지 않았다. PR94 때문에 `axisym_coupling.rs`의 build identity는 PR96 실행 당시와 달라졌으므로 새 merged source hash `6bb3feb6a290894bd8bdd45f9745f28329265cee8ce89589a11960b523e6b008`을 사용한다. PR95 adapter source hash는 `31c8b1005bf9500d365450b33617d8a2675066b7cee5efa43ca91ccb9d6f7e5b`다.

## PR96에서 실제로 닫힌 범위

| 항목 | 확인한 내용 | claim ceiling |
|---|---|---|
| background/time map | Einstein dust+Lambda LRS Bianchi-I, `s_i/H_i=10^-3`, proper elapsed time `0..10^11 s`, directional characteristic와 volume-redshift map | model-defined test-field; observational Bianchi calibration 아님 |
| normalized IC | `T_i=50000 K`, fixed-temperature charge-neutral H/He equilibrium, HM12 UVB photon IC | warm parcel; REC/cold primordial IC 아님 |
| photon/source history | UVB는 최초 photon IC만, emissivity는 stage source; `N_rel=a_rel^3 n`, `E=qR`, source Jacobian `R^-3` | HM12-to-Bianchi volume-redshift mapping은 채택 가정 |
| closure | homogeneous primary-only Case-A escape; recombination **energy** escape ledger | emitted recombination photon count/spectrum, diffuse reabsorption, secondary/Compton 미정 |
| interval | 2904 nodes, 17 epochs, `q=10..50000 eV`, `0..10^11 s` | conditional research interval; production `PhysicalHistory`와 global EoR admission 아님 |

Puchwein 같은 UVB는 이 PR96 lane에 새로 섞지 않았다. HM12의 초기 field와 별도 emissivity가 각각 한 역할을 가지며, 이후 HM12 `J_nu`/photo-rate를 덮어쓰지 않는다. 향후 Puchwein을 쓸 경우 external field, emissivity input 또는 comparison 중 정확히 한 역할을 정해야 하며 같은 photon/heat를 transport와 table에서 중복 계상하면 안 된다.

## 무결성 및 실행 검증

- PR96 `SOURCE_MANIFEST.json` SHA-256: `b4cdad70c5ed64b2c127aea79b96876ce2417f80e160b47efb0ce61451d7d5c5`.
- Manifest 87/87 files: exact SHA-256/byte verification PASS, including raw HM12 tables and all NPZ datasets.
- HM12 intake tests: `10 passed`.
- Merged native conditional consumer tests: `6 passed`.
- PR94 axisymmetric coupling tests: `5 passed`.
- PR95 selected-He adapter tests: `4 passed`.
- One bounded integrated fixed interval was executed using the frozen PR96 IC/source/grid and 17 epochs. No other history or scan was run.

최초 exact-array 비교는 보존된 실패다. PR96 evidence는 Python 3.12.14/NumPy 2.3.5/SciPy 1.17.0, 이 통합 실행은 Python 3.12.3/NumPy 2.4.2/SciPy 1.17.0이었다. Quadrature energy 최대 상대차 `2.13e-16`, state 최대 상대차 `4.56e-13` 때문에 byte/numeric-array exact equality는 FAIL이었다.

PR96의 기록된 numerical targets로 다시 판정한 결과는 `SCOPED_PASS`다: 일반 history field 최대 상대차 `1.96e-15`, state 최대 상대차 `4.56e-13` (`2e-6` target), pressure difference/photon-energy `1.86e-16` (`1e-11` target), candidate energy ledger `1.58e-15`, photon-number ledger `5.71e-15` (`1e-9` target). 이것은 같은 parser/rates/grid를 쓰는 compatibility check이며 독립 원자물리 또는 continuum 검증이 아니다.

기존 initial campaign과 이 integration의 측정된 build/test/run/failed-comparison 합계는 약 CPU `25.87 s`, summed process wall `19.16 s`다. Git·파일·review overhead는 `UNKNOWN`이며 0으로 간주하지 않는다. 360초 budget 안에서 full 11-history 재실행은 하지 않았다.

## 보존한 제한

1. `CONTRACT.json`은 `...REVIEW_PENDING` 문자열을 유지하지만 같은 immutable folder의 `independent_review.json`과 `RUN_STATE.json`은 `PROMOTE_SCOPED`를 기록한다. 원 evidence를 고쳐 쓰지 않고 metadata discrepancy로 보존한다.
2. PR95는 stale cached residual acceptance만 막는다. 기존 `64*EPSILON`, naive summation과 mutable relative REC path를 그대로 두므로 production tolerance/immutable REC binding은 미선택이다.
3. PR94는 positive thermal energy가 binary64에서 `T=0`으로 underflow되는 것을 거부한다. PR96 warm interval에서 이 guard가 발동했다는 뜻은 아니다.
4. PR94/95 remote CI runs `38031760491`, `38031762177`는 두 patch 바깥의 inherited `cargo fmt --check`에서 실패했고 later tests가 skipped 됐다. 이번 targeted local PASS가 remote whole-CI PASS를 뜻하지 않는다.
5. PR96 production source는 unchanged였고 `PhysicalHistory`는 계속 `PhysicalExecutionNotImplemented`다. 별도 source-bound conditional consumer contract 없이 이 gate를 열면 안 된다.

## 남은 실제 결정

- **Warm conditional lane 다음 단계:** PR96의 exact dataset/closure를 별도 `SourceBoundConditional` production provider에 연결할지 승인해야 한다. 이는 warm HM12 lane의 production wiring이지 cold CR science admission이 아니다.
- **사용자의 CR 목표:** exact low-energy CR injection/deposition provider, spectrum/normalization, secondary-electron H/He partition, clock/units/error model이 필요하다. PR96에는 CR가 없으므로 HM12 source를 CR 대용으로 부를 수 없다.
- **Cold primordial IGM:** source-pinned REC/HyRec IC와 FT03 `30000 K` 하한 아래에서 유효한 atomic/thermal provider가 필요하다. PR96의 `50000 K` parcel을 단순히 냉각하거나 clamp하면 안 된다.
- **Radiation closure:** emitted recombination photon count/spectrum, diffuse fate, secondary/Compton, `>50 keV` boundary 및 source/atomic-fit uncertainty를 선택해야 한다.

권고하는 다음 bounded unit은 두 갈래를 혼동하지 않는 것이다. 먼저 PR96 warm lane에 대해 P01 production conditional wiring을 수행할 수 있다. 사용자의 CR-first 목표를 직접 진행하려면 그 전에 CR provider와 cold/low-temperature IC/rate 정책을 owner decision으로 고정해야 한다. 어느 경우에도 장기 history나 parameter scan은 아직 허용되는 다음 단계가 아니다.

