# REI-ACCEL02 C07R 후속 local Codex 시작문

REI-ACCEL02의 **C07R 실제 복구 결과**에서 이어서 작업하라. 목표는 이미 실행된 z=15.9→4 H/He·온도·광자 결합 history의 spectral blocker를 해소하고, 수치 근거를 갖춘 FLRW/Bianchi 비교와 새 native BASS 연결로 진행하는 것이다. 완료된 RUN002나 기존 128-grid 시간 검산을 반복하지 마라. 현재 실패를 숨기거나 원자율·source·closure·허용 기준을 바꾸지 마라.

## 복구와 증거 경계

REI PR110의 최신 publication receipt와 additive branch `research/accel02-native-broad-20261011`을 확인하라. 이번 복구의 Git 기준점은 `304afc3592ae60242e3bb72efc56d806519b4a60`이다. C07R2 archive는 `research/accel02_20261011` 전체, raw NPZ/JSON, as-run drivers, N1 provider tables와 검증된 native binary를 담는 Git용 overlay다. ACCEL02 바깥의 `research/physical_provider_20261010/{background.py,hm12_data.py,sources/emissivity.out,sources/UVB.out}` 네 source pin도 최종 R2에 포함한다. 나머지 runtime 의존성은 published Git repository에서 가져온다. 이것을 archive 하나만으로 독립 실행되는 전체 repo bundle이라 부르지 마라.

실제 object ID·SHA·업로드 상태는 `recovery/C07R*_BACKUP_RECEIPT.json`과 최신 publication receipt를 읽어라. 새 raw 실행은 C07R1에 먼저 이중백업했다: archive SHA-256 `5e3a694338c5c7d9c62661ad302d9b107401b9018cf21e012e273f4fb2ec93ee`, 620,910 bytes, Drive `1m60Z8BwtqxUNq7bHucybAueLmAQa7yG1`, Dropbox `id:BSpOijBcT10AAAAAAD35_w`. 최종 문서·판정·DAG는 이후 C07R2 receipt를 따른다. 정상 복구·게시 때 필요한 identity 확인만 하고 불필요한 반복 다운로드를 하지 마라. `UPLOAD_VERIFIED`와 `RESTORE_VERIFIED`는 별개다.

먼저 현재 checkout, 파일, 실행 중인 process, source/binary/input hashes를 확인하라. 이전 local-only EVENT003와 ce40 commit은 scratch 정리로 유실되어 채택하지 않았다. 지금의 authoritative 새 raw는 `n2/evidence/EVENT_COUPLED003_RECOVERED/`다. 대화 요약의 수치를 파일 존재나 검증 완료의 근거로 쓰지 마라. 캠페인 이름 20261011은 한국 날짜이며 실제 복구 timestamp는 UTC를 사용한다.

ZIP 해제기가 Unix 실행 권한을 복구하지 않았다면, native SHA-256 `3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac`를 확인한 뒤 `chmod u+x research/accel02_20261011/n1/native/target/release/rei_n1_native`를 적용하라. 확인된 바이너리를 자동 재빌드하지 마라.

## 필수 읽기와 확정 상태

`research/accel02_20261011/`에서 다음을 읽어라.

1. `NEXT_DAG.json`, `REPORT_KO.md`, `integration/CONTRACT.json`, `n1/CONTRACT.json`, `n2/CONTRACT.md`.
2. `review/recovery/SPECTRAL_DECISION.json`, `SPECTRAL_REVIEW_KO.md`, `SAVED_ARITHMETIC.json`.
3. `n2/evidence/EVENT_SPECTRAL_COMPARISON_RECOVERED.json`, `n2/SPECTRAL_RECOVERY_REPORT_KO.md`, `n2/evidence/SPECTRAL_BAND_LOCALIZATION_RECOVERED.json`.
4. `recovery/QUADRATURE_NEXT_STEP.md/.json`, `recovery/Q0_SOURCE_ATTRIBUTION.md/.json` 및 Q0의 제한된 독립 검토. Q0 계산은 완료됐으므로 같은 후처리를 반복하지 않고 실제 결과를 재사용하라.

N1은 actual source/cold Case-A provider 연결의 scoped DONE이다. N2_TIME은 기존 128×2 EVENT001/002 시간 비교의 scoped DONE이며, 최대 field 차이 1.4231727742e-8이 기준 2e-6을 통과했다. 기존 EVENT002 energy/number residual은 5.2481356770e-11과 5.0103782457e-10이다. EVENT002의 all-accepted gas domain은 원 실행에서 측정하지 않았으므로 **NOT_EXPLICITLY_MEASURED**로 유지한다.

복구된 EVENT003은 **256×2, r=0, rtol=1e-11**의 실제 전구간 실행이다. 629.20 s에 218 segment를 완료했다. segment endpoint와 저장129 epoch를 합친 energy/initial-energy 최대값은 **6.6493278602e-11**, number/initial-nH 최대값은 **5.5014857431e-10**이다. accepted gas·finite·photon positivity 직접 검사가 통과했고 독립 reviewer가 그 범위만 승격했다. 이는 256-grid의 별도 same-grid 시간 수렴이나 연속 모든 시각의 bound가 아니다.

**Spectral은 FAIL이다.** 128→256의 최대 scaled 차이는 ΓHeI의 **0.1401807633**, 고정 기준은 **0.001**이다. 65와129 epoch 검사 모두 24개 field/moment 중23개가 실패했다. 129 epoch에서 ΓHI≈0.1269181, ΓHeII≈0.0631533, T≈0.00413458, source number/reference volume≈0.1150456, source energy/reference volume≈0.08630366, total proper photoheat≈0.01632884다. 각 표본 집합의 fine 최대 진폭으로 각각 정상화한다. 원 N2 frozen-bath 계약의65 epoch/number1e-10과 native integration의129 output epoch/number1e-9을 섞지 마라.

BASS N4는 PR140에서 **옛 ACCEL01 reduced FLRW/r=.1 cell 두 개**를 수신한 scoped DONE이다. 새 native H/He history의 BASS 수신은 아직 실행하지 않았다. N2 전체 완료, N3 비등방 signal, continuum/observational admission도 아직 HOLD다.

## 지금 수행할 연구 루프

Q0 source/IC 원인 분해는 완료됐다. 선언된 HM12 interpolation의 exact moment 대비 source reference-volume N 오차는 128에서10.31555%, 256에서5.08064%, E 오차는7.89482%와3.96376%다. 초기 UVB full-band photon number signed error는+0.08133%와+17.32147%로 비단조적이며, HI-ionizing N은−4.88387%/−0.35907%, HeI-ionizing N은−9.61879%/−2.62002%다. 256-grid 초기 full-N의 +17.32147% 차이는 독립 band 분해에서 거의 전부 sub-HI10–13.6 eV로 확인됐다. 이를17.3% ionizing-photon 또는 heating 오차로 바꾸어 쓰지 마라. 이 source-only 오차는 gas feedback 없이 직접 측정됐지만 evolved Γ/heat 오차 전체를 설명하지 않는다. Q0의 exact-reference 정상화는 공식 fine-grid spectral 정상화나 새로운 gate가 아니다. Q0는 `review/recovery/Q0_DECISION.json`에서 `ACCEPT_SOURCE_AND_INITIAL_FIELD_QUADRATURE_ATTRIBUTION_ONLY`로 승인됐다. 이 decision SHA-256은 `962c9979e759746e0145b23429312ec443e74e74eabbe8924949ba1d28e1511b`다. 검토는 초기8개 moment와4개 source epoch/32개 moment의 독립 적분이며129epoch 전체의 재적분은 아니다. **다음 action은 Q1A 후보 선택·구현**이다. 현재 에너지대역 합에서는 ΓHI의 차이가13.6–24.59 eV, ΓHeI는24.59–54.42 eV, source number는10–13.6 eV에서 주로 나타났다. 이는 fixed log-q midpoint quadrature와 움직이는 threshold/source knot가 관련된다는 가설을 지지하지만 유일한 원인을 증명하지 않는다. 원 HM12 table의 interpolation identity를 고정한 moment와 as-run 합은 Q0 자료에 있으므로 재계산하지 않고 후보 설계에 사용하라.

최소 변경 후보 **Q1A**는 고정 q와 양의 고정 weights를 유지하는 composite Gauss다. 초기 UVB jump 및 source/threshold trajectory를 참고해 사전 knots를 선택하고 bounded node budget을 정하라. 현재 native RHS·counter·Jacobian의 동일 source/absorption/heat pairing을 그대로 사용한다. 이 방법이 매시각 threshold에 정확히 정렬된다고 주장하지 마라. 성능과 정확도 개선은 실제 새 전구간 비교 전에는 미확정이다.

**Q1B**는 Q1A가 부족하거나 비경제적이라는 근거가 생겼을 때의 별도 대안이다. 고정 q-cell의 N과 Q=∫q dN, 양의 realizable reconstruction, native σ를 사용한 공통 source/absorption/heat moments를 사용하며 새 numerical closure와 Jacobian 검증이 필요하다. 현재 U_i=E_iN_i packet 식에 움직이는 q/weight만 대입하면 remap/weight-derivative 항이 빠지므로 금지한다. 한 packet에 모순되는 정확 source number와energy moments를 동시에 강제하지 마라. Γ/heat 사후 보정이나 ledger counter만 수정하는 방법도 금지한다.

선택한 한 후보를 구현한 뒤 **동일 z15.9→4 전체 구간**의 candidate/enriched pair를 수행하라. 새로운 discretization에서 필요한 same-grid 시간 evidence, 물리 domain, source·radiation·ionization·heat 및 gas field spectral 차이, number/energy ledger를 확인한다. 기준은 time2e-6, initial-energy ledger1e-9, initial-nH number ledger1e-9, geometry1e-11, empirical spectral/angular1e-3이다. zero channel은 exact zero를 유지한다. 누적 source로 정상화한 보조 energy metric으로 initial-energy 기준을 바꾸지 마라.

독립 판정 뒤 spectral 기준을 통과하면 r=0과r=0.05의 장기 paired run, 최소4/8 angle refinement로 진행한다. 그 case의 time/spectral/angle 근거를 확인하고 공통 mean-z에서 ΔxHII, ΔxHeII, ΔxHeIII, ΔT, ΔΓ 등을 수치오차와 비교하라. 오차보다 작은 신호를 검출로 부르지 마라. 고에너지 tail 확대, 무제한512→1024→4096 doubling, 좁은 redshift 반복 검사를 기본 경로로 삼지 마라.

## 병렬 작업과 BASS 연결

동시에 진행할 수 있는 것은 실제 checkpoint-resume CLI, source/serialization profiling, 새 native BASS schema다. 완료된 Q0는 재사용하고 새로운 profiling에만 소유자를 한 명 배정하라. 현재 `RESTART.npz`는 state evidence이고 `--resume`은 구현되지 않았다. resume 기능은 source/binary/grid/정상화/active-event/accepted-segment state identity를 검증하도록 실제 구현해야 한다. bare NPZ만으로 적분이 이어진다고 주장하지 않는다.

새 history가 수용되면 proper-time cell의 ne_eff=(∫ne dt)/Δt를 producer의 실제 quadrature와 함께 export하고 새 run/hash·cosmology·closure·units·frame을 BASS native receiver에 연결하라. 원래 reduced cell을 재명명하지 않는다. 실제 null-covector endpoint inversion이나 observer tail 없이 total CMB τ 또는 fixed-observed-z 방향별 visibility를 주장하지 마라.

## 유지할 물리와 저장 규칙

초기 T20 K, xHII2e-4, neutral He는 conditional IC다. pinned HM12 초기 UVB와 evolving emissivity, physical band10–50000 eV, primary-only Case-A escape, Grackle RR/CI/DR/CE/ff, prescribed isotropic T_CMB=2.7255(1+z)를 유지한다. 50 keV 위 원 source energy 누락이 z4에서7.668%라는 한계는 그대로 기록하되 이를 gas-heating/HeII 오차와 동일시하지 않는다. CR/RCT/secondary·diffuse recombination·backreaction·완전한 anisotropic CMB 물리를 포함한 것으로 승격하지 않는다. 원래 CR/RCT/HH 확장 lane은 보존한다.

실제 run 완료·첫 실패 즉시 raw와 as-run source를 새 이름으로 durable checkpoint하라. 그 뒤 독립 판정·보고서·DAG를 다음 단계로 저장한다. additive GitHub push/PR 및 기존 Drive+Dropbox 백업 권한을 사용하되 owner branch force update나 merge는 하지 않는다. 두 provider의 실제 ACK와 가능한 size/hash/object ID가 있어야 이중백업 완료라 기록한다. 다음 세션으로 넘어갈 때는 정확한 마지막 checkpoint와 다음 한 action을 제공하라. 이미 완료된 검산, 변하지 않은 blocker audit, 목적 없는 문헌 재탐색으로 이 작업을 대체하지 마라.
