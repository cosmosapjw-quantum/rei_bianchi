# Codex handoff — integrated PR96 + PR94 + PR95 + PR98

다음 작업은 `cosmosapjw-quantum/rei_bianchi`의 격리 branch `codex/physical-provider-integration-20261010`에서 시작해. Operational checkout은 branch head의 `research/physical_provider_integration_20261010/DELIVERY_RECEIPT.json`이 지정하는 `evidence_bearing_commit`을 사용해. PR94/95 same-input compatibility를 실제 실행한 code ancestor는 별도로 `7346bea6f6b08165bd64d742ec684bd06caf6318`이다. 두 identity를 혼동하지 말고 merge/main/release는 자동 수행하지 마.

## 반드시 보존할 source identity

- PR96 conditional warm provider: `528bb69a24ce9345efec78c6d406d3c392e2671d`, scientific commit `446c1263e1c4300fde0b860f221e0053568f4e00`, base PR93 `17bd1cc0ce1484ee61cac60ab1bda207ae264381`.
- PR94 thermal-underflow guard: `2ee78d593f97f715495f38e629678f5affba5750`.
- PR95 current-field selected-He closure guard: `73bd78d051ba448cfa71d638615e2c360b37c86d`, base PR92 `beaaf68595f5ab493654b812d66a4fa3e3177d84`.
- PR98 production conditional route: `c168e578354c2f1e191a7064ffa31bd762d2a949`, base PR96 `528bb69a24ce9345efec78c6d406d3c392e2671d`.
- Original PR96 manifest SHA-256: `b4cdad70c5ed64b2c127aea79b96876ce2417f80e160b47efb0ce61451d7d5c5`. Historical commit `528bb69a...`는 87/87이다. Original PR98 commit은 sealed `RESEARCH_DAG.json`을 `7a6ecb...`로 바꿔 86/87이었지만, integration correction은 이를 manifest value `012f742...`와 P01 `ready`로 복구해 현재 tree도 87/87이다. PR98의 원 commit/report는 execution certification으로 사용하지 마.

먼저 `research/physical_provider_integration_20261010/INTEGRATION_REPORT_KO.md`, `VALIDATION.json`, PR96의 `CONTRACT.json`, `independent_review.json`, `SOURCE_MANIFEST.json`, `RUN_STATE.json`, 그리고 production `axisym_contract.rs`/`axisym_coupling.rs`를 읽어. PR96 원 evidence를 수정하지 마.

## 정확한 claim boundary

PR96은 실제 coupled 연구 실행이다. HM12 UVB는 photon IC만 만들고, 별도 emissivity가 stage source다. 각 stage에서 `N_rel=a_rel^3 n`, `E=qR`, 방향 Jacobian `R^-3`, 동일 opacity/source time, thermal/binding 분리와 recombination escape **energy only**를 유지한다.

그러나 이것은 `z_a=5.807`, `T_i=50000 K`, dust+Lambda test-field, warm homogeneous H/He, CR/RCT/HH OFF, primary-only Case-A escape의 조건부 lane이다. cold primordial IGM/REC IC, low-energy CR deposition, secondary/Compton, diffuse photon count/spectrum/reabsorption, 장기 history, observational Bianchi calibration 또는 production `PhysicalHistory`를 승인하지 않는다.

PR95는 stale cached residual만 고친다. 기존 `64*EPSILON`, naive summation, relative mutable REC path를 physical policy로 승격하지 마. PR94/95/98은 sibling 관계를 보존한다. Remote CI runs `38031760491`, `38031762177`, `38033034271`, `38033014151`는 inherited fmt에서 실패하고 tests가 skipped 됐다.

PR98 route는 code/component level에서 통합됐지만 실행은 gate되어 있다. Python은 source bytes를 hash-verify하지만 임의 `--binary`를 받을 수 있고 그 binary/source hashes를 integration 뒤에 기록한다. Rust `BIND`는 전달된 hash 문자열만 확인하며 실제 파일이나 build를 증명하지 않는다. Recovered producer JSON/NPZ와 Dropbox archive `REI_PHYSINPUT_P01_PRODUCTION_20261010_c168e578.tar.gz` (`9a82f25e...`, provider ID `BSpOijBcT10AAAAAAD3sHQ`)의 payload가 일치하지만, archive에는 실제 production binary, P01 build transcript, P01 command/stdout/stderr receipt가 없다. 따라서 clean-build identity를 대신하지 않는다. `P01_EXECUTION_GATE.json`을 읽고 source-pinned clean-build receipt와 prelaunch binary/source check가 구현되기 전에는 새 solver interval을 실행하지 마.

PR99 `d6ad8b73d0ae63f16968bbb04331380554828f64`의 finite-grid diffuse screen은 merge/adopt하지 마. 보고된 cap `0.011107406480410278`과 cap/minimum-thermal `1.3218886276228445e-8`은 frozen-grid energy diagnostic일 뿐 diffuse-ON/coupled-state bound가 아니다. 또한 validation이 기록한 `screen_diffuse.py` hash `431277dd...`와 committed blob hash `fbc725be...`가 다르므로 run-source identity 해소 전까지 reported diagnostic / HOLD다.

## 다음 bounded task

사용자가 **warm PR96 lane의 production wiring**을 계속하면:

1. 현재 PR98 `SourceBoundConditional` route를 유지하고 기존 `PhysicalHistory` guard를 우회하지 않는다.
2. exact clean source commit/tree, Cargo inputs, toolchain, build command/exit와 executable hash를 묶은 immutable build receipt를 만든다.
3. Python이 subprocess 시작 전에 current source와 `--binary` hashes를 receipt와 비교해 mismatch를 거부하도록 하고 stale-binary negative component test를 추가한다.
4. 이 gate가 통과한 뒤에만 동일 17 epochs의 한 interval 실행을 별도 승인 대상으로 올린다. 현재 recovered output은 producer evidence이지 독립 certified run이 아니다.
5. current-field compensated conservation와 owner-adopted tolerance를 별도 결정한다. PR95의 `64*EPSILON`/naive sum을 자동 상속하지 않는다.

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
git switch codex/physical-provider-integration-20261010
evidence_commit=$(jq -r .evidence_bearing_commit research/physical_provider_integration_20261010/DELIVERY_RECEIPT.json)
git switch --detach "$evidence_commit"
sha256sum -c research/physical_provider_integration_20261010/INTEGRATION_SHA256SUMS
jq . research/physical_provider_integration_20261010/P01_EXECUTION_GATE.json
```

전체 11-history 재생산은 source/consumer가 바뀌지 않았다면 반복하지 마. 변경 범위만 검증하고, 최초 failure·명령·exit·CPU/wall·source hashes를 보존해. 상태는 `PROPOSAL`, `NOT_RUN`, `PARTIAL`, `FAIL`, `SCOPED_PASS`로 제한해 보고해.

