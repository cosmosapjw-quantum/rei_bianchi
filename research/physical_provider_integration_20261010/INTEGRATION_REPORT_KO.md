# REI physical-provider 통합 검토

날짜: 2026-10-10 UTC  
판정: **`PROMOTE_INTEGRATION_SCOPED`**  
전역 과학 admission: **`HOLD`**  
PR94/95 compatibility를 실행한 code ancestor: `7346bea6f6b08165bd64d742ec684bd06caf6318`

PR98 route merge commit: `242313d49c35ee70a0759169126b79c69ef5bf30`

## 결론

PR96은 단순 제안이나 고정 photo-rate packet이 아니다. 고정된 HM12 `UVB.out`로 photon IC를 만들고 별도 `emissivity.out`를 매 stage source로 사용하며, 방향·에너지가 변하는 photon node, HII/HeII/HeIII와 thermal energy를 실제 opacity 및 기존 native atomic/AXI 함수로 함께 진화시킨 조건부 warm H/He 연구 lane이다. 역사적 PR96 commit `528bb69a...`에서는 저장된 11 histories와 원자료·NPZ를 포함한 manifest 87개 payload가 전부 일치한다. Original PR98 commit은 sealed `RESEARCH_DAG.json`을 바꿔 86/87이었지만, integration correction은 이 파일을 manifest bytes로 복구해 현재 tree도 87/87이다.

동시에 이 결과는 사용자의 본래 **low-energy cosmic-ray deposition in primordial IGM** 목표를 해소하지 않는다. PR96은 `z_a=5.807`, `T_i=50000 K`, dust+Lambda test-field Bianchi-I, HM12 photon IC/emissivity, primary-only Case-A escape를 선택했고 CR/RCT/HH는 OFF다. REC 초기조건, cold mean IGM, secondary-electron/Compton, diffuse reabsorption, 장기 history와 production `PhysicalHistory`는 여전히 열려 있다.

## 병합 그래프

병합은 sibling 관계를 보존했다.

- PR96 head `528bb69a24ce9345efec78c6d406d3c392e2671d`, base PR93 `17bd1cc0ce1484ee61cac60ab1bda207ae264381`.
- PR94 head `2ee78d593f97f715495f38e629678f5affba5750`, parent PR93. Merge commit `8e949ec356a3cfa0001e8b7f946f38fa61ad2675`.
- PR95 head `73bd78d051ba448cfa71d638615e2c360b37c86d`, parent PR92 `beaaf68595f5ab493654b812d66a4fa3e3177d84`. Merge commit `7346bea6f6b08165bd64d742ec684bd06caf6318`.
- PR98 head `c168e578354c2f1e191a7064ffa31bd762d2a949`, parent PR96 `528bb69a24ce9345efec78c6d406d3c392e2671d`. PR97 sibling에 merge한 commit은 `242313d49c35ee70a0759169126b79c69ef5bf30`이다.

PR95를 PR94의 자식으로 재작성하지 않았고 역사적 PR96 commit도 재작성하지 않았다. PR98이 바꾼 sealed `RESEARCH_DAG.json`은 manifest bytes와 P01 `ready`로 복구했다. PR94 때문에 `axisym_coupling.rs`의 build identity는 PR96 실행 당시와 달라졌으므로 새 merged source hash `6bb3feb6a290894bd8bdd45f9745f28329265cee8ce89589a11960b523e6b008`을 사용한다. PR95 adapter source hash는 `31c8b1005bf9500d365450b33617d8a2675066b7cee5efa43ca91ccb9d6f7e5b`다.

## PR98 production route 통합과 실행 gate

PR98은 기존 `PhysicalHistory`를 열지 않고 별도 `SourceBoundConditional` Python/Rust route를 추가한다. Static time/state/unit/sign trace에서 이 frozen warm IVP에 대한 명백한 arithmetic blocker는 발견하지 못했다. PR94 zero-temperature guard와 PR95 adapter는 PR98에 없었지만 sibling merge에서 모두 보존했다.

Merged component validation은 새 solver 없이 수행했다: Rust conditional `8 passed`, Python boundary `5 passed`, 기존 contract `6 passed`, coupling `5 passed`, PR95 adapter `4 passed`. PR98이 보고한 production JSON/NPZ 원 bytes도 `/tmp/rei-p01-final-nrAQew/output`에서 복구했고 SHA-256 `9bf3795a2725ef628d6e5312f7351b2a26e58a165caeda3b72184bc8fe75f295`와 `77a144347d8f85c91320c7acc694e770544ff61f79bc418cebe3f8f13403483a`가 producer return identity와 일치했다. Parent worker의 독립 static cloud inspection은 Dropbox archive `REI_PHYSINPUT_P01_PRODUCTION_20261010_c168e578.tar.gz`, 3,288,066 bytes, SHA-256 `9a82f25e...`, provider ID `BSpOijBcT10AAAAAAD3sHQ`에 두 payload가 있음을 확인했다. 이 workspace에서는 archive를 다시 materialize하지 않았다.

그러나 PR98 실행은 독립 인증하지 않는다. Archive에는 실제 production binary, P01 clean-build transcript, P01 command/stdout/stderr receipt가 없다. Python `--binary`는 임의 executable을 허용하고 source/binary hashes를 integration 뒤에 기록한다. Rust `BIND`는 Python이 넘긴 identity 문자열을 비교할 뿐 파일이나 build provenance를 검증하지 않는다. 따라서 protocol-compatible stale binary도 production label을 받을 수 있다. 향후 interval 실행 전에는 clean source-pinned build receipt와 prelaunch source/binary hash 검증이 필수다. 이 gate는 `P01_EXECUTION_GATE.json`에 고정했고, 이번 통합에서는 solver를 다시 실행하지 않았다.

Original PR98 `p01/REPORT_KO.md`의 source-preflighted production execution 주장과 `RESEARCH_DAG.json`의 P01 `completed_scoped` 표시는 위 증거보다 강하다. Integration은 report 원문을 Git history에 보존하되 authoritative claim으로 채택하지 않고, sealed DAG를 P01 `ready`로 복구했다.

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
- Historical PR96 commit `528bb69a...`: manifest 87/87 exact SHA-256/byte PASS, including raw HM12 tables and all NPZ datasets.
- Original PR98 commit `c168e578...`: 86/87 because `RESEARCH_DAG.json` became `7a6ecb05545d15f685e3cf8bf8b8d11d75572509b91cefac358c32db3e51c1dd`.
- Current integration tree after corrective restoration: PR96 manifest가 열거한 87 payload 전부 PASS; `RESEARCH_DAG.json` again equals manifest SHA-256 `012f742ad251ec05134085ec9a0dec3cc797b7852b9f70ffca185bd3886cf7ec`. PR98 신규 파일은 이 역사적 manifest의 범위 밖이며 Git evidence commit과 integration checksum set으로 별도 결속한다.
- HM12 intake tests: `10 passed`.
- Merged native conditional consumer tests: `6 passed`.
- PR94 axisymmetric coupling tests: `5 passed`.
- PR95 selected-He adapter tests: `4 passed`.
- One bounded integrated fixed interval was executed using the frozen PR96 IC/source/grid and 17 epochs. No other history or scan was run.

최초 exact-array 비교는 보존된 실패다. PR96 evidence는 Python 3.12.14/NumPy 2.3.5/SciPy 1.17.0, 이 통합 실행은 Python 3.12.3/NumPy 2.4.2/SciPy 1.17.0이었다. Quadrature energy 최대 상대차 `2.13e-16`, state 최대 상대차 `4.56e-13`의 roundoff-scale deviation 때문에 byte/numeric-array exact equality는 FAIL이었다. Python과 NumPy version 차이는 관측 사실이지만 deviation의 원인은 분리하지 않았으므로 특정 library에 귀속하지 않는다.

PR96의 pre-existing numerical targets를 적용한 **새 same-input compatibility checks** 결과는 `SCOPED_PASS`다. 이는 원래 PR96 contract 전체를 재실행한 것이 아니다. 일반 history field 최대 상대차 `1.96e-15`, state 최대 상대차 `4.56e-13` (`2e-6` field target), per-epoch `|DeltaP_base-DeltaP_candidate|/U_gamma_candidate(t)` 최대 `1.8643520454027995e-16` (`2e-6` field target), candidate energy ledger `1.58e-15`, photon-number ledger `5.71e-15` (`1e-9` ledger target)다. `times_s`, `mu0`, `weights`의 exact equality와 finite state, nonnegative photon state, ionic fraction domain, `30000..110000 K` temperature domain도 saved NPZ/JSON에서 명시적으로 PASS했다. `1e-11` geometry target은 quadrature-energy compatibility에만 적용했다. 이것은 같은 parser/rates/grid를 쓰는 cross-environment compatibility check이며 독립 원자물리 또는 continuum 검증이 아니다.

기존 initial campaign, corrected saved-data check와 PR98 component checks까지 측정된 build/test/run/failed-comparison 합계는 약 CPU `35.90 s`, summed process wall `27.92 s`다. Git·파일·review overhead는 `UNKNOWN`이며 0으로 간주하지 않는다. 360초 budget 안에서 full 11-history 또는 새 production solver 실행은 하지 않았다.

## 보존한 제한

1. `CONTRACT.json`은 `...REVIEW_PENDING` 문자열을 유지하지만 같은 역사적 evidence folder의 `independent_review.json`과 `RUN_STATE.json`은 `PROMOTE_SCOPED`를 기록한다. 이 metadata discrepancy는 그대로 명시한다.
2. PR95는 stale cached residual acceptance만 막는다. 기존 `64*EPSILON`, naive summation과 mutable relative REC path를 그대로 두므로 production tolerance/immutable REC binding은 미선택이다.
3. PR94는 positive thermal energy가 binary64에서 `T=0`으로 underflow되는 것을 거부한다. PR96 warm interval에서 이 guard가 발동했다는 뜻은 아니다.
4. PR94/95 remote CI runs `38031760491`, `38031762177`와 integration PR97 runs `38033034271`, `38033014151`는 inherited `cargo fmt --check`에서 실패했고 later tests가 skipped 됐다. 이번 targeted local PASS가 remote whole-CI PASS를 뜻하지 않는다.
5. `PhysicalHistory`는 계속 `PhysicalExecutionNotImplemented`다. PR98은 별도 conditional route를 추가했지만 이 fail-closed gate를 열지 않았다.
6. PR98 `SourceBoundConditional` route는 code/component level에서 통합했지만 clean-build executable binding이 없으므로 future execution은 `BLOCKED_PENDING_SOURCE_PINNED_CLEAN_BUILD_RECEIPT`다. Recovered raw outputs는 producer evidence로 보존하지만 독립 실행 인증으로 승격하지 않는다.

## 남은 실제 결정

- **Warm conditional lane 다음 단계:** PR98 route의 source-pinned clean-build receipt와 prelaunch executable check를 구현·검증해야 한다. 그 전에는 새 interval을 실행하지 않는다. 이는 warm HM12 lane의 production wiring이지 cold CR science admission이 아니다.
- **사용자의 CR 목표:** exact low-energy CR injection/deposition provider, spectrum/normalization, secondary-electron H/He partition, clock/units/error model이 필요하다. PR96에는 CR가 없으므로 HM12 source를 CR 대용으로 부를 수 없다.
- **Cold primordial IGM:** source-pinned REC/HyRec IC와 FT03 `30000 K` 하한 아래에서 유효한 atomic/thermal provider가 필요하다. PR96의 `50000 K` parcel을 단순히 냉각하거나 clamp하면 안 된다.
- **Radiation closure:** emitted recombination photon count/spectrum, diffuse fate, secondary/Compton, `>50 keV` boundary 및 source/atomic-fit uncertainty를 선택해야 한다.

## Fresh intake — 채택하지 않은 PR99 진단

PR99 commit `d6ad8b73d0ae63f16968bbb04331380554828f64` (parent PR98 `c168e578...`)은 17 frozen epochs/2904 nodes에서 finite-grid retained-energy cap fraction `0.011107406480410278`, cap/minimum frozen thermal `1.3218886276228445e-8`를 `PASS_DIAGNOSTIC`으로 보고한다. 이는 diffuse-ON, continuum/time convergence 또는 coupled-state bound가 아니며 spectrum, multiplicity, combined uncertainty budget도 없다.

더 중요한 provenance mismatch가 있다. 저장된 `repaired/VALIDATION.json`은 `screen_diffuse.py` SHA-256을 `431277ddc0654a6fb3bf145e43c7e71c9abea052c7bb5f1d9e7944411fb7e8ba`로 기록하지만 commit `d6ad8b73...`의 실제 blob bytes는 `fbc725be46dfbb114ef3f80b9c49d780675c0bda975b5cc0ae7bc46acaa189a6`이다. 따라서 PR99를 merge·science validation·closure adoption에 사용하지 않았고, 실행-소스 identity 해소 전까지 **reported diagnostic / HOLD**로만 보존한다. 이 handoff를 위해 재실행하지 않았다.

권고하는 다음 bounded unit은 두 갈래를 혼동하지 않는 것이다. 먼저 PR96 warm lane에 대해 P01 production conditional wiring을 수행할 수 있다. 사용자의 CR-first 목표를 직접 진행하려면 그 전에 CR provider와 cold/low-temperature IC/rate 정책을 owner decision으로 고정해야 한다. 어느 경우에도 장기 history나 parameter scan은 아직 허용되는 다음 단계가 아니다.

