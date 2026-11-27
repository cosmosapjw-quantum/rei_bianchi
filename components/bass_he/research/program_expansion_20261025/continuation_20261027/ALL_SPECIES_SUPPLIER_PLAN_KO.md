# 모든 구성 종의 충돌·열화 공급자 후속 계획

**입력은 `sources/CONSUMER_PROJECTION.json` 하나이다.** WU HEAD `87933da5654bb2e4d93f7de4341df5e0fa0f8716`의 원전92 ID를 아래에서 atomic70, molecular17, neutron1, anion1, electron3으로 한 번씩 분류한다. 공급자128개와 사건149개는 원전 참조이며, 현재 이 투영이 승인한 완전 미분 공급자는0개이다. 본 문서는 새 원전 조회·수치/과학 실행·WU 재컴파일 없이 작성한 다음 작업의 범위이다.

## 게시 직전 최신 원전 갱신

위128 variants/27방향 reference는 테스트에 사용한 R1/R2 snapshot의 시점이다. `sources/r3_update/OVERLAY.json`은 WU80c0d758의 R3를 별도로 소비한다. 현재92 IDs와149 saved event columns는 그대로이고,4 EXFOR variants/36 native rows가 추가되어132 variants 및 원래19 targets/28방향 모두의 primary reference가 존재한다. 24 SIG와12 CM angular DA를 구별하고7 E2 보조행을 따로 둔다. 기존 원전 snapshot은 수정하지 않았다. Source-reference closure는 동일-D 정규화, 전체각 support, ionic/state binding, covariance, rate/Q 또는 MeV consumer 승인이 아니다.

## 1. 모집단과 소유권을 먼저 고정한다

Historical20 atomic charge states+neutron1은 원전 view 그대로 유지한다. 동일한 조성·전하의 unresolved aggregate, Case-A all-bound-level aggregate, ground, excited, parent/residual state는 서로 다른 표현이다. **Aggregate와 resolved states를 함께 진화시키려면 배타적인 partition map을 먼저 명시한다.** 원전92개를 동시 독립 모집단92개로 해석하지 않는다. `H`, `He`, `H+`, `He+` 등의 원전 표제와 WU의 선택 isotope 좌표도 구별하며, 표제만으로 isotope rate transfer를 승인하지 않는다.

기존32 fixture는 material21+electron2+synthetic9이다. `ground/free/synthetic`와 원전 상태의 문자열 일치는0개이므로 자동 alias를 만들지 않는다. 조성·전하·pool 후보가 있어도 상태 binding을 별도로 수행한다. C12/C13/C12m/C12C13은 현재 원전의 후보도 없는 synthetic 확장이다. 이 네 개를 활성 source ID로 만들어 추가하지 않는다. Nuclear catalogue5,843행도 활성 종에 더하지 않는다. 현재92개에는 non-ground nuclear isomer가 없으며, 전자 여기상태와 nuclear isomer는 구분한다.

에너지 소유권은 사건별 한 번만 둔다. 열용량은 고정된 독립 population에서 열적 에너지의 편미분이고 입자수 생성항과 분리한다. Explicit excitation·binding·molecular/nuclear energy, bulk kinetic energy, 비열적 전자, photon/neutrino escape는 각각의 항에 기록한다. 분자 내부상태를 population으로 풀면 같은 상태 에너지를 별도 partition heat capacity에 다시 넣지 않는다. Fast pool은 자격을 갖춘 에너지 전달 사건을 거쳐 thermal pool에 들어간다.

## 2. 모든 군에 적용할 공급자 계약

| 의무 | 다음 산출물과 판정 범위 |
|---|---|
| **DCS** | 정확한 초기 isotope/isomer/charge/state와 최종 branch별 미분 단면적의 변수·단위·정규화·원전 support·불확실도를 명시한다. 적분값을 기존 scalar 원전과 비교할 수 있어야 한다. Scalar rate나 thermal integral만으로 유일한 DCS를 복원하지 않는다. |
| **각분포** | Source frame, CM/lab 변환, 입사·산란 방향, 축대칭/등방성 가정, 필요한 각 moment를 지정한다. 소스에 없는 등방성을 넣으면 별도의 조건부 모델로 표시한다. |
| **유한질량** | Neutral/bare/molecular rest mass와 상태 에너지 convention, reduced mass·recoil 및 frame을 묶는다. 질량수 A를 kg 질량으로 쓰지 않는다. 원전 covariance가 없으면 물리 오차 배정을 보류한다. |
| **공동 최종상태 법칙** | 생성물 에너지·각·branch·multiplicity의 상관관계를 보존한다. 각각의 marginal을 독립 추출하여 에너지·운동량을 깨뜨리지 않는다. Schematic gamma token이나 빈 external-product 배열은 실제 광자 수/에너지를 정하지 않는다. |
| **열화·에너지 재분배** | 입자종·상태·에너지 구간별 slowing-down/redistribution과 thermal·fast·radiation 소비자를 연결한다. 빠른 전자 생성, recoil, 여기·이온화·해리의 에너지 분배를 동일 사건에서 처리한다. 즉시 열화는 선언된 모델 가정으로만 유지한다. |
| **에너지·운동량 교환** | 같은 사건 법칙의 number·momentum·bulk/thermal/internal/fast/radiation energy moment를 제공한다. 닫힌 사건의 합과 escape flux를 구별하고, 수신 소비자 ACK·frame·proper event flux를 고정한다. |

공통 완성 조건은 전체 source identity와 support, 질량/상태 binding, 필요한 각·에너지 moment, 단일 에너지 소유권, 독립 검토가 함께 존재하는 것이다. 현재처럼 물리 budget·covariance·branch가 열려 있으면 해당 항은 null/pending으로 유지한다. Source count 증가로 이 조건을 대신하지 않는다.

## 3. 군별 재사용과 다음 최소 질문

| 군 | 현재 재사용 | 정확히 남은 연결 | 선호하는 다음 최소 질문 |
|---|---|---|---|
| **Atomic70** | WU PI/RR/CI/CE의 기존 상태·사건 참조와 historical20 view. H1/He4 neutral ground의 추가 질량 후보2개와 bare mass5개를 그 정확한 state에만 연결한다. CR의 He4+ ground capture/external interface는 완료 범위대로 재사용한다. | 위6의무 전부를 실제 pair/process별로 채운다. 다른 isotope·excited/aggregate mass를 두 neutral ground 값으로 대체하지 않는다. 10개 finite-CI gap과 source isotope/state·domain·consumer binding을 보존한다. | **H1 ground–He4 ground 한 쌍**에서 기존 HE moment 결과와 선택 질량/state binding을 연결하는 데 필요한 추가 angular/energy 입력은 무엇인가? 이미 완료한 moment 계산은 재사용하고, 새 검증은 바뀐 질량/state·consumer 연결에만 한정한다. 다음 CE 후보는 `PHYS83_CE_1s_to_2s`의 event-energy/domain·named-consumer binding이다. |
| **Molecular17** | REC HD9 levels/8 lines/2colliders/18pairs/54rates. T=50/100/200 K, ortho/para-H2 분리. WU 분자 사건은 원전 identity/ref로 재사용한다. | Molecular/isotope mass, unresolved vibration/electronic state, state-specific energy defect, recoil/angle·joint daughter law·dissociation/attachment energy partition. HD7 line bridge는 HOLD이므로 주파수/에너지 binding이 완료됐다고 쓰지 않는다. | **`LAMDA_HD_C_2_1`: HD J1→0 + para-H2** 한 사건에서 이미 있는 REC finite-domain 결과를 HE 소비자에 참조로 연결하고, scalar rate 외에 momentum·recoil moment가 무엇을 더 요구하는지 명시한다. REC parser·54rates·상향률/보간 검증을 재구현하지 않는다. |
| **Neutron1** | 기존 capture/β 사건 정수 투영, p/n/d/t/helion bare mass 참조, `PHYS81_COLD_np_d_gamma`의 기존 kinematics source 참조. | `PHYS81_COLD_np_d_gamma`에 명시된 physical rate·joint mass covariance·consumer binding. ENDF H1 MT102의 source atomic→bare map·event-energy/domain·named-consumer binding. Capture recoil·photon cascade와 β의 e/ν joint spectrum/angles·thermalization은 별도 자격이 필요하다. | **n+p→d+gamma 한 채널**의 기존 kinematics와 rate source를 같은 state/frame/domain으로 연결할 수 있는가? Atomic-to-bare 및 consumer 조건부터 판정하고, 이미 있는 cold kinematics나 WU compiler를 반복하지 않는다. |
| **Anion1** | H- 원전 ID와 UMIST 사건 참조. 이를 H1 neutral fixture나 electron pool의 별칭으로 만들지 않는다. | Isotope/rovibronic state, anion rest mass·binding, attachment/detachment 및 mutual-neutralization branch, outgoing-electron/photon 에너지·각 상관관계, shielding/environment·event flux·pool ownership. | **`UMIST22_8742` 한 사건**의 H와 e:umist 입력을 실제 state/pool에 bind할 수 있는가? Source isotope/state·electron ownership·flux·environment·Q/partition을 하나의 소비자 계약으로 명시하고, 외부 생성물 빈 배열을 무복사 증거로 읽지 않는다. |
| **Electron3** | Thermal/free와 fast/β count carrier, source-pool-unresolved UMIST carrier를 구별한다. CR의 완료된 He4 capture/external consumer와 E/I/(E+I) ledger를 참조한다. | Thermal/fast 분포·frame·normalization; 에너지와 각의 joint collision/secondary spectrum; finite target recoil; fast→thermal deposition; source β e의 energy distribution과 ν 부호/energy accounting. UMIST 좌표의 thermal label은 열화 승인이 아니다. | **`PHYS83_CE_1s_to_2s` 한 사건**의 기존 state pair와 named thermal/fast consumer를 연결하여 incident electron energy가 excitation·recoil·outgoing electron으로 한 번씩 전달되는 조건을 정한다. 기존 CR He4 RR 또는 외부 history 계산을 재실행하지 않는다. |

Atomic의 남은 finite-CI 방향은 D:0, T:0, He3:0/1, He4:1, Li6:0/1/2, Li7:1/2이다. Missing bare mass는 He4:2, Li6:3, Li7:3이다. 이들은 다른 scalar candidate 존재와 별개인 기존 승인 공백이다.

원래19 target/28 directions는 그대로 유지한다. Source reference가 있는27방향도 rate/Q/state/branch 승인을 뜻하지 않으며, **target6 He4(gamma,dd) forward**의 수치 원전은 최신 R3에서 회수됐다. 다음 의무는 native angular/beam response·동일-D 정규화·상태와 실제 소비자의 결속이다. Exclusive deuterium, factorized He3, inclusive Li7, response-averaged He4 공급자를 구별한다. 다음 새 원전 확보는 남아 있는 특정 source-to-consumer binding 또는 위 한 채널의 명시적인 추가 angular/joint-law datum을 대상으로 잡고, 전체 완료 suite를 반복하지 않는다.

REC의 line bridge는1 pass/7 fail이고 H5 physical coverage0/313, physical error budget=null이다. CR He4 결과는 native threshold24.59 eV·stationary heavy target/recoil0의 scoped 결과로 재사용하며 이를 유한반동 완료로 넓히지 않는다. HE101 C8 OPEN 및 기존 소진 예산, PHYS91 remaining0, WU249 reuse, HH_R10 OFF, production NOT_ISSUED를 보존한다. 각 실제 다음 노드의 실행 전에는 부모 workflow에서 최신 AGENTS/HEAD/병렬 소유자·자료·receipt를 다시 고정한다.

## 4. 92개 원전 ID의 배타적 목록

아래 **다섯 inventory 군만 서로 배타적**이다. 물리적 population의 aggregate/resolved 중첩은 앞의 partition 의무로 별도 처리한다. `원전 표제`는 첫 source label을 표시하며 전체 label·source qualification·사건 참조는 입력 JSON의 동일 ID에 있다. `구성/q`는 WU compiler 좌표이고 source isotope/state 자격을 자동 승인하지 않는다. 모든 material 구성의 nuclear isomer 표기는 ground이다. Atomic/molecular/neutron/anion의 pool은 material이며 electron pool은 별도로 적었다.

### Atomic 70

| WU source ID | 원전 표제 | 구성/q 또는 pool | 원전 state |
|---|---|---|---|
| `sp_c3cf5d7e86504457d820` | `D:0` | H2×1; q=0 | `population_aggregate_unresolved` |
| `sp_063621f2c3ed11763f45` | `D:0:Case_A_all_bound_levels` | H2×1; q=0 | `Case_A_all_bound_levels` |
| `sp_e122664dacbd50a873e3` | `D:0:ground` | H2×1; q=0 | `1s_ground` |
| `sp_67e18c83359dac9a96d8` | `D:1` | H2×1; q=1 | `bare_nucleus` |
| `sp_52bc19dffa06d76c0db7` | `H` | H1×1; q=0 | `source_electronic_rovibrational_unresolved` |
| `sp_3ebd8d3f3d9773d0c8ca` | `H+` | H1×1; q=1 | `source_electronic_rovibrational_unresolved` |
| `sp_4d0fdcd19fc29ce8b961` | `H1` | H1×1; q=0 | `source_fragment_state_unresolved` |
| `sp_5eba93637d9b34d2586c` | `H1:0` | H1×1; q=0 | `population_aggregate_unresolved` |
| `sp_d3ca404a20daa54d39ef` | `H1:0:2p` | H1×1; q=0 | `2p_LS_aggregate` |
| `sp_4414044a0789f10b558a` | `H1:0:2p_J1_2` | H1×1; q=0 | `2p_J1_2` |
| `sp_7008b223f053651bc0b7` | `H1:0:2p_J3_2` | H1×1; q=0 | `2p_J3_2` |
| `sp_0ba1d9b8e1e2dc814e71` | `H1:0:2s` | H1×1; q=0 | `2s` |
| `sp_9b48a2195197b1cd3ee5` | `H1:0:Case_A_all_bound_levels` | H1×1; q=0 | `Case_A_all_bound_levels` |
| `sp_7b3d2e472131e6c645d7` | `H1:0:ground` | H1×1; q=0 | `1s_ground` |
| `sp_4efa39d0560d4d0f0f09` | `H1:1` | H1×1; q=1 | `bare_nucleus` |
| `sp_570dc62663c8f6eedfd5` | `He` | He4×1; q=0 | `source_electronic_rovibrational_unresolved` |
| `sp_1151a406e229edf0e4a8` | `He+` | He4×1; q=1 | `source_electronic_rovibrational_unresolved` |
| `sp_e70bc4252792f04af423` | `He3:0` | He3×1; q=0 | `population_aggregate_unresolved` |
| `sp_4c01f54610e9404fd405` | `He3:0:Case_A_all_bound_levels` | He3×1; q=0 | `Case_A_all_bound_levels` |
| `sp_fbddbb115ce79716da1e` | `He3:0:ground` | He3×1; q=0 | `electronic_ground` |
| `sp_5fdd2b49904833e0097f` | `He3:1` | He3×1; q=1 | `population_aggregate_unresolved` |
| `sp_09fd1f68acd9920cdd59` | `He3:1:Case_A_all_bound_levels` | He3×1; q=1 | `Case_A_all_bound_levels` |
| `sp_ab718ceae93707d052cf` | `He3:1:ground` | He3×1; q=1 | `electronic_ground` |
| `sp_8db65f04f775dec37120` | `He3:1:one_bound_electron_unresolved` | He3×1; q=1 | `one_bound_electron_unresolved` |
| `sp_12980417abc2242f91dd` | `He3:1:parent_ion_unresolved` | He3×1; q=1 | `parent_ion_unresolved` |
| `sp_c3d8e1bb021c872166af` | `He3:1:residual_manifold_unresolved` | He3×1; q=1 | `residual_manifold_unresolved` |
| `sp_e38928cce79c74a915ca` | `He3:2` | He3×1; q=2 | `bare_nucleus` |
| `sp_398e8a2a9c72c42acc30` | `He4:0` | He4×1; q=0 | `population_aggregate_unresolved` |
| `sp_de43b0e3fa7326d20b3a` | `He4:0:Case_A_all_bound_levels` | He4×1; q=0 | `Case_A_all_bound_levels` |
| `sp_17efcd73203997543678` | `He4:0:ground` | He4×1; q=0 | `electronic_ground` |
| `sp_d4ce42397dd1fee0c009` | `He4:1` | He4×1; q=1 | `population_aggregate_unresolved` |
| `sp_a0f7e0bde6cf53829246` | `He4:1:Case_A_all_bound_levels` | He4×1; q=1 | `Case_A_all_bound_levels` |
| `sp_b6b245e320d25ff44c8e` | `He4:1:ground` | He4×1; q=1 | `electronic_ground` |
| `sp_71fc837e357245f93394` | `He4:1:parent_ion_unresolved` | He4×1; q=1 | `parent_ion_unresolved` |
| `sp_6d85bb5b9f56f407ee76` | `He4:1:residual_manifold_unresolved` | He4×1; q=1 | `residual_manifold_unresolved` |
| `sp_b3abd68cdace9fbcdb47` | `He4:2` | He4×1; q=2 | `bare_nucleus` |
| `sp_5cd7701ca871ee85ec0e` | `Li6` | Li6×1; q=0 | `source_fragment_state_unresolved` |
| `sp_3c4977667048f0028e56` | `Li6:0` | Li6×1; q=0 | `population_aggregate_unresolved` |
| `sp_c2650fdf6c75ce02c5e0` | `Li6:0:Case_A_all_bound_levels` | Li6×1; q=0 | `Case_A_all_bound_levels` |
| `sp_99af7ce35ec555e69971` | `Li6:0:ground` | Li6×1; q=0 | `electronic_ground` |
| `sp_353b9bec93a147ecd56e` | `Li6:1` | Li6×1; q=1 | `population_aggregate_unresolved` |
| `sp_1a3a85c3da9b9f88eea1` | `Li6:1:Case_A_all_bound_levels` | Li6×1; q=1 | `Case_A_all_bound_levels` |
| `sp_65801f255474d7033ee1` | `Li6:1:ground` | Li6×1; q=1 | `electronic_ground` |
| `sp_ad039096f21eb17c5f26` | `Li6:1:parent_ion_unresolved` | Li6×1; q=1 | `parent_ion_unresolved` |
| `sp_c13cdcb934f524985bed` | `Li6:1:residual_manifold_unresolved` | Li6×1; q=1 | `residual_manifold_unresolved` |
| `sp_bac4b72f28facde291d2` | `Li6:2` | Li6×1; q=2 | `population_aggregate_unresolved` |
| `sp_fa0c8c62b9185e048a4d` | `Li6:2:Case_A_all_bound_levels` | Li6×1; q=2 | `Case_A_all_bound_levels` |
| `sp_a79d57d0f3abb37c922b` | `Li6:2:ground` | Li6×1; q=2 | `electronic_ground` |
| `sp_50535eb9bd2c7544b3a0` | `Li6:2:parent_ion_unresolved` | Li6×1; q=2 | `parent_ion_unresolved` |
| `sp_bda6b2b8bd6bdb2beca3` | `Li6:2:residual_manifold_unresolved` | Li6×1; q=2 | `residual_manifold_unresolved` |
| `sp_10ab43569e8a04a21e55` | `Li6:3` | Li6×1; q=3 | `bare_nucleus` |
| `sp_29d5a576f8d2ed443ddc` | `Li7` | Li7×1; q=0 | `source_fragment_state_unresolved` |
| `sp_b7ec86fb0091e4a9dce2` | `Li7:0` | Li7×1; q=0 | `population_aggregate_unresolved` |
| `sp_cb5cd742ca9c40272c16` | `Li7:0:Case_A_all_bound_levels` | Li7×1; q=0 | `Case_A_all_bound_levels` |
| `sp_37d5b36369bbcb651c18` | `Li7:0:ground` | Li7×1; q=0 | `electronic_ground` |
| `sp_109ae417f6d5ebaa6fc9` | `Li7:1` | Li7×1; q=1 | `population_aggregate_unresolved` |
| `sp_5d41deff98d96e229b7c` | `Li7:1:Case_A_all_bound_levels` | Li7×1; q=1 | `Case_A_all_bound_levels` |
| `sp_bd587dbb3034b452d6ba` | `Li7:1:ground` | Li7×1; q=1 | `electronic_ground` |
| `sp_f6c6123f2ed40ac9d309` | `Li7:1:parent_ion_unresolved` | Li7×1; q=1 | `parent_ion_unresolved` |
| `sp_655d7d95f6c6dfba1b64` | `Li7:1:residual_manifold_unresolved` | Li7×1; q=1 | `residual_manifold_unresolved` |
| `sp_866e3024de7ad1a31320` | `Li7:2` | Li7×1; q=2 | `population_aggregate_unresolved` |
| `sp_ad6eacedd27f645668d8` | `Li7:2:Case_A_all_bound_levels` | Li7×1; q=2 | `Case_A_all_bound_levels` |
| `sp_790a52da05ed51a5ffb9` | `Li7:2:ground` | Li7×1; q=2 | `electronic_ground` |
| `sp_1d8c097e7a314bddf01d` | `Li7:2:parent_ion_unresolved` | Li7×1; q=2 | `parent_ion_unresolved` |
| `sp_d755e1bf1a95d99ae22f` | `Li7:2:residual_manifold_unresolved` | Li7×1; q=2 | `residual_manifold_unresolved` |
| `sp_fd180a74799e822a0775` | `Li7:3` | Li7×1; q=3 | `bare_nucleus` |
| `sp_54a9f3426cf6243e29c8` | `T:0` | H3×1; q=0 | `population_aggregate_unresolved` |
| `sp_d8ba2eb356c81cb095a6` | `T:0:Case_A_all_bound_levels` | H3×1; q=0 | `Case_A_all_bound_levels` |
| `sp_adcb237e10161ad9f1bc` | `T:0:ground` | H3×1; q=0 | `1s_ground` |
| `sp_091a4088df71e12a8ef6` | `T:1` | H3×1; q=1 | `bare_nucleus` |

### Molecular 17

| WU source ID | 원전 표제 | 구성/q 또는 pool | 원전 state |
|---|---|---|---|
| `sp_5f70c4bfa8842d90f014` | `H2` | H1×2; q=0 | `ortho_H2;source_state_as_tabulated` |
| `sp_ed7729406990eab1dc1e` | `H2` | H1×2; q=0 | `para_H2;source_state_as_tabulated` |
| `sp_05b2dcb1c84b7443c945` | `H2` | H1×2; q=0 | `source_electronic_rovibrational_unresolved` |
| `sp_b0b0c435bfed51a69806` | `H2+` | H1×2; q=1 | `source_electronic_rovibrational_unresolved` |
| `sp_32073288735b4e45e94f` | `H3+` | H1×3; q=1 | `source_electronic_rovibrational_unresolved` |
| `sp_4a8030facfe77e03809d` | `HeH+` | H1×1 + He4×1; q=1 | `source_electronic_rovibrational_unresolved` |
| `sp_89bdc5911ef77442d3e0` | `LAMDA_HD_level_1` | H2×1 + H1×1; q=0 | `HD:J=0;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_76bc868a230dd96a7ed4` | `LAMDA_HD_level_2` | H2×1 + H1×1; q=0 | `HD:J=1;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_f1920dc2d46fad7156f5` | `LAMDA_HD_level_3` | H2×1 + H1×1; q=0 | `HD:J=2;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_cbc45161aff59832aafc` | `LAMDA_HD_level_4` | H2×1 + H1×1; q=0 | `HD:J=3;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_33795cff8e05c2665e6a` | `LAMDA_HD_level_5` | H2×1 + H1×1; q=0 | `HD:J=4;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_7d9a6832bcd906d222aa` | `LAMDA_HD_level_6` | H2×1 + H1×1; q=0 | `HD:J=5;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_935396985931d260e03b` | `LAMDA_HD_level_7` | H2×1 + H1×1; q=0 | `HD:J=6;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_c82f710698a7907e6b16` | `LAMDA_HD_level_8` | H2×1 + H1×1; q=0 | `HD:J=7;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_484fca186bdf7b04f7e3` | `LAMDA_HD_level_9` | H2×1 + H1×1; q=0 | `HD:J=8;v=UNRESOLVED;electronic=UNRESOLVED` |
| `sp_d0e98469c93b2713d9d1` | `Li6H1` | H1×1 + Li6×1; q=0 | `source_electronic_rovibrational_unresolved` |
| `sp_d071dc5212f377e61933` | `Li7H1` | H1×1 + Li7×1; q=0 | `source_electronic_rovibrational_unresolved` |

### Neutron 1

| WU source ID | 원전 표제 | 구성/q 또는 pool | 원전 state |
|---|---|---|---|
| `sp_ffa035a18d4afc747777` | `n:0` | n1×1; q=0 | `bare_nucleus` |

### Anion 1

| WU source ID | 원전 표제 | 구성/q 또는 pool | 원전 state |
|---|---|---|---|
| `sp_5fec1c6319ca9d0f514c` | `H-` | H1×1; q=-1 | `source_electronic_rovibrational_unresolved` |

### Electron 3

| WU source ID | 원전 표제 | 구성/q 또는 pool | 원전 state |
|---|---|---|---|
| `sp_d3b4781786f4573ad194` | `e:fast` | electron_fast | `free_electron` |
| `sp_30a54105bfc934f6d65f` | `e:thermal` | electron_thermal | `free_electron` |
| `sp_5b2b7d80cc1049088f2e` | `e:umist` | electron_thermal | `source_pool_unresolved` |
