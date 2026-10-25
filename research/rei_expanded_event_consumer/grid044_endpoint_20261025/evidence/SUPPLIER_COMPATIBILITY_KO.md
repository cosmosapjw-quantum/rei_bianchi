# REI 선택 시나리오를 위한 공급자 intake

조사 시각: 2026-10-25 12:57 UTC. 범위는 공개된 원 코드·계약·저장 결과의 read-only 복구다. 새 provider 수치 호출, IVP, NCP, 완료 suite 재실행은 모두 0이다. `FETCH_MANIFEST.json`의 42개 텍스트 파일은 Git blob SHA와 로컬 바이트가 일치한다 (`INTAKE_BYTE_CHECK.json`). 전체 ZIP 복원이나 전체 scientific rerun으로 해석하지 않는다.

## 현재 owner와 병렬 변경

여섯 owner branch와 expansion branch의 실제 ref를 읽었다. 모두 고정 인계의 SHA와 같다. 최신 open PR 5개씩도 확인했다. `FRESH_REFS.json`, `FRESH_PARALLEL_PRS.json`에 원 식별자가 있다. 미게시 native/local 변경은 이 경로에서 관측되지 않는다.

| 저장소 | expansion HEAD | owner HEAD | 현재 주된 gate |
|---|---|---|---|
| WU088_HH | `34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad` | `2912a315aa39e7293000b7b2b8c7cc7a706fea9e` | finite compiler 사용 가능, empirical rate/nuclear Q는 별도 |
| rec_bianchi | `5dd414982c5c9ada97dfdfcc0b77cf83af86d66e` | `ea89c97abeb7a663a813f00e9aadddaf0b32a6a9` | PB01 재사용, actual H5/H6/H7 입력 open |
| bass_cr | `8d0a5c375589fbddadc2bb90c8117311c80bad09` | `b1aed87852d4f8994494c2ae41a913afd390eccd` | H1 ground RR scoped, N6/N7 predecessor gated |
| BASS_HE | `c456b05e0f1c53faa3ae36720826f43e57c06a91` | `28a26f4db951ab9085180e2ecc5d600d981a1f71` | HE101 C8 open, physical provider false, reserve 0 |
| bass | `d6af237b66e78ca6ed4572068f6bc1a805bbb2d9` | `cc602e209e7deeb511ab2a1f3b2268d55206c43c` | B3g actual cohort/B3h finite absorption open |
| vigilode | `72836e0290b66d33f4ca1771284b1c8070669a74` | `a01f1c5c78e6b06e23565cd4e482716f99efbe97` | D5 gateway 재사용, V6 derivative/V8 whole domain 별도 |

CR C23E의 현재 sibling PR100 HEAD는 `8623d7b2035677fc231976d85fea309f48afd57c`다. 수정 날짜가 더 늦다고 PR105의 H1 RR lineage를 교체하지 않는다. 여기서 복구한 C23E 파일은 expansion tree에 보존된 버전이므로, sibling의 후속 변경을 적용하려면 그 affected files를 비교해야 한다.

## 1. WU event compiler: 재사용할 실제 코드

정본 경로: `WU088_HH/research/rei_chem_ledger_20261025/chem_ledger.py`; Git blob `62be292325ddc0b6f121ed72373bee140ba7c3a2`. 인계의 249 checks 승인과 코드가 함께 복구됐다.

호출 가능한 핵심은 `catalog`, `conservation`, `stoichiometry`, `source`, `source_residuals`, `register_ownership`이다. 코드의 단일 rate 정규화는 `events_per_reference_nucleus_per_proper_second`다. `source`는 명시된 exact rational rate에 stoichiometric column을 곱한다. rate는 사용자가 채택한 물리 source에서 별도로 온다.

`qualified_energy`는 `energy_qualification == "SYNTHETIC_EXACT"`만 승인한다. `radiation_event`의 승인 이름도 `SYNTHETIC_SINGLE_ENERGY_PHOTON`이다. 실제 물리 입력을 이 label로 바꾸면 안 된다. 실제 source 에너지 ledger는 원 계약의 physical threshold·kinetic moment·radiation debit을 갖춘 REI consumer에서 별도로 묶고, WU의 conservation/source 경로를 재사용한다. 이 경우 기존 compiler energy status는 `UNQUALIFIED:ENERGY`인 채 보존할 수 있다.

`register_ownership`은 같은 `ownership_slot`과 같은 full directed key의 중복을 막는다. directed key에 `provider_domain`, `frame`, `state_resolution` 문자열이 포함되므로 다른 문자열로 표시된 물리적으로 겹치는 입력까지 판정하지 않는다. REI는 선택된 physical event ID, source interval/support, parcel, epoch, isotope/state에 대한 한 owner와 한 extent를 먼저 고정해야 한다. 그 extent를 입자·binding·fast·radiation ledger로 분배하고 두 번 더하지 않는다.

## 2. CR 외부 photon source: 실제 저장된 유한 입력

복구된 원 데이터는 `bass_cr/research/cr_c23e_d43_source_binding_20261024/inputs/C23B_CASES_EXACT.json`이며 blob `61bcbc0b44206f496534da6bdffcdfe1731ad063`다. 3 epoch × 3 channel의 9개 결과가 있다. 원 구현과 source contract도 `implementation/reuse/c23b/`에 복구했다.

- source: Taira2025 PW19 v1.0.0 subset, DOI `10.5281/zenodo.15367103`, upstream commit `863c3b7fa73a8510fbf57ee7b75ad1e8c34086de`.
- 원 spectrum convention: `S(E)=4*pi*nu*J_nu`, erg s^-1 cm^-2 per dlnE. bin integral이 아니다.
- 승인 epoch: 정확히 `2.316`, `2.479`, `2.649`. source contract의 redshift interpolation은 NOT_IMPLEMENTED.
- 원 Verner photo.dat SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.
- HI/HeI/HeII threshold는 각각 13.6/24.59/54.42 eV이며 photon 상한 50000 eV다.
- 각 row는 `bath_frame_rest_target`, `per_absorbing_target_per_proper_second`, ground state, zero recoil이다.
- H1/D/T 또는 He3/He4 mapping은 source 자체의 isotope 측정이 아니다. 선택 시나리오의 명시된 atomic-label assignment와 원 유효범위를 함께 저장한다.

구체적인 저장값, HI at z=2.316:

| 양 | 원 저장값 |
|---|---:|
| Gamma | 1.2040291922113047e-12 s^-1 |
| primary kinetic moment | 4.5278278094592344e-12 eV target^-1 s^-1 |
| binding moment | 1.6374797014073745e-11 eV target^-1 s^-1 |
| absorbed photon moment | 2.0902624823532978e-11 eV target^-1 s^-1 |
| signed energy residual | -1.6155871338926322e-27 eV target^-1 s^-1 |
| secondary thermal heating | null |

이 분해의 source 소유권은 `Gamma*x_HI` 한 event extent, H1 neutral 감소/ion 증가/e_fast 증가, binding 증가, primary fast kinetic 증가, radiation 감소다. fast kinetic을 thermal heat에 다시 가산하지 않는다. photon 상한 밖 원 intensity가 있어도 atomic event rate는 null이다.

재사용 가능한 source assembly: `research/cr_c23b_source_frame_20261023/implementation/primary_source_assembly.py`, blob `fd6785565ac02637c1e8dc8cb7ebcda79a89a5dc`. 이 adapter는 HI/HII/HeI/HeII/HeIII 다섯 population과 세 흡수 source를 모두 요구한다. H1 하나만 선택한 모델은 이 세-channel assembly를 그대로 억지로 호출하지 않고, 저장된 HI row와 WU의 해당 column을 소비한다. 별도의 H/He fractions를 0으로 채워 제공한다고 source 의존성이 자동 해소되지 않는다.

GRID044는 root가 별도로 복구한다. 고정 인계의 z2가 정확히 z=2라면 위 세 CR 저장 epoch와 다르다. 한 모델의 같은 source로 합치려면 실제 GRID source/frame/threshold/support identity를 대조해 CR의 per-event ownership interface에 연결하거나, 선택한 공통 epoch에서 신규 source binding을 별도 명시해야 한다. z=2.316 rate를 z=2 rate로 재명명·외삽하지 않는다.

## 3. H1 RR: 선택할 때만 요구할 원 계약

`research/cr_n5_rr_milne_20261025/inputs/reused/REI_H1_T10000_SAVED_ROWS.json`과 `implementation/rr_engine.py`, `inputs/CONFIG.json`을 복구했다. source-dependent ground spontaneous RR는 원 HI threshold 13.6 eV와 g_H=2, g_p=1을 쓴다. 고정 T=10000 K의 saved thermal alpha_g_sp는 `1.5893516133029456e-13 cm^3 s^-1`이고 all-level RR `4.192322735308633e-13`과 다르다.

N5 fast electron의 tagged hazard는 `n_HII*v(E)*sigma_RR(E)`다. 설정의 n_HII=0.1 cm^-3와 thermal ne=0.14 cm^-3를 교환하지 않는다. electron kinetic -E, internal -I, radiation +(E+I)의 에너지 합은 0이다. full source와 후속 PI feedback, stimulated/all-level RR, finite-mass recoil은 별도 조건이다. 단지 재이온화 PI 시나리오를 묶기 위해 RR를 일괄 필수선행조건으로 만들 필요는 없다.

## 4. HE 열화·충돌: 연결할 계약과 실제 열린 입력

`research/he_ang_provider_contract_20261023/code/heang_contract/metadata.py`와 `exact_events.py`, `theory/PROVIDER_TEMPLATE.json`이 복구됐다. metadata precheck는 source/event-law/preparation/angle identities, count/exchange convention, support, relative flux, SI 단위, source uncertainty와 numerical error의 분리를 검사한다. metadata의 성공은 physical provider 승인이 아니다.

`exact_events.py`는 동시 event law의 전자 둘과 이온 recoil에 대한 exact momentum/energy·pair-correlation algebra를 제공한다. `integrate_events`, `cross_section_weighted`, `transform_raw`를 재사용할 수 있다. 이는 photoionization primary 한 전자의 분포나 전체 secondary degradation operator를 자동 공급하지 않는다.

HE101 `CLAIM_GATE.json`의 현재 값은 `physical_provider_admitted=false`, `event_sigma=false`, `physical_recoil_distribution=false`, `exchange_complete=false`, `HE_ANG=SOURCE_INPUT_PENDING`다. C8 export가 열려 있고 reserve=0인 원 상태를 유지한다. CBA 수치 PASS만으로 원자 전체 thermalization을 채우지 않는다.

HE32 pilot은 Tgas=20000 K, prescribed UV, photo+case A RR와 gas pi_b=0 closure를 쓴 완료 결과다. 열·광원 자기일관성 및 CI/DR/CX는 후속 과제다. 따라서 이 pilot을 실제 HE degradation/heating source의 대체값으로 사용할 수 없다.

선택 모델의 thermal consumer는 exact matched source law 또는 명시적 다른 승인된 열화 operator, birth spectrum, current gas composition/T, stopping/escape prescription과 공통 event extent를 받으면 진행할 수 있다. 현재 없는 heat/source 값은 null/입력 미결로 남기고 arbitrary zero나 fast kinetic 전체를 넣지 않는다.

## 5. BASS transport와 four-force

일반적인 photon event 계산 경로는 `research/bass_b3a_event_source_20261024/code/event_measure.py`다. `PhotonEventMeasure`의 E_J>0, unit direction, nonnegative event rate m^-3 s^-1와 `Identity(owner,epoch,frame,clock,provenance)`를 소비한다. `moments`는 cQ(J m^-3 s^-1), observer-dependent K, number rate를 만든다. target-frame PiRate는 spatial tracefree 부분이며 일반 observer에서는 None이다.

`bass_binding.py`는 REC line down/up의 특정 OWNER와 invariant proper clock만 허용하며 matter energy를 `internal_excitation_energy`에 배정한다. 이 파일을 그대로 PI attachment로 쓰면 owner와 에너지 의미가 틀린다. 일반 `event_measure`를 재사용하고 REI의 PI ownership adapter를 별도로 적게 작성하는 것이 맞다. 기존 BASS `core.Source`의 pressure/pi는 현재 stock이고 U/J는 transfer rate다. PiRate를 stock pressure/pi에 직접 넣지 않는다. radiation과 matter transfer는 반대 부호다.

G1의 `kinetic.py`와 background `core.py`도 복구했다. B3f ADMISSION의 actual-history binding, native finite absorption, Source/U/J/PiRate transaction은 open이다. 제조 입력에서 검증된 finite error bound를 실제 시나리오 전체 오차로 복사하지 않는다. 실제 incident angular measure가 없는 경우 isotropic 모델을 선택하는 것은 명시된 추가 가정이며 측정된 Bianchi anisotropic source로 표기하지 않는다.

## 6. VigilODE 실제 client 연결

`research/d5_callback_contract_20261025/source/gateway.rs` blob `0600b75a8c376a46a237ba70ba1292723c1f4bd1`를 복구했다. const-N `BoxDomain::new`, `Gate::prepare_pair`, `eval_rhs`, `eval_jacobian`, `estimate_partial_t_centered`가 있다. full-write RHS/Jacobian scratch를 모두 채우고, epoch/FP witness와 finite output을 통과해야 한 Prepared가 반환된다. failure 시 caller의 기존 반환값은 보존된다. captured external side effects의 rollback은 보장하지 않는다.

domain은 유한 closed box다. simplex, positive thermal energy, provider temperature/support, current source identity 등의 model-specific domain은 client callback 안에서도 확인해야 한다. 실제 derivative는 WU/REC/CR/HE/BASS의 식과 state transform을 미분해 별도로 검증해야 한다. gateway가 finite but wrong J를 승인할 수 있다는 것이 원 D5 계약이다. centered-time difference는 점 근사이며 whole-domain certificate가 아니다.

D5의 원 polynomial 729-grid와 49-stencil 실행은 재사용한다. native `AffineErrorNorm`, Session, Transaction, output prepare/commit를 새로 구현하지 않는다. live owner/reservation/dirty/completion 상태는 원 D5 계약에서도 unresolved이며 원격 장치의 미게시 상태는 이번 public API intake로 확인되지 않는다.

## root에 반환하는 권고

1. 고정 comoving Nref와 실제 source/frame/epoch/support를 담은 한 시나리오를 동결한다.
2. WU column과 selected source moments를 같은 physical event ID로 묶는다. native source Γ를 두 번 곱하거나 서로 다른 source epoch를 같게 취급하지 않는다.
3. photon energy debit, binding, primary fast energy를 보존적으로 나누고 HE/CR 열화 입력의 실제 수신 범위를 별도로 기록한다.
4. BASS에는 한 event rate measure의 cQ/number moment를 제공하며, current stock과 rate는 분리한다.
5. VigilODE에는 그 same-source RHS/J를 full-write callback으로 제공한다. 관련식 derivative 검산과 provider whole-domain gate는 각각 기록한다.

이 경로는 공급자 모든 미래 channel의 완료를 기다리지 않는다. 선택한 physical slice에서 실제로 필요한 source/thermalization/transport 입력이 없는 지점만 precise input dependency로 남긴다. 전체망, L4 readiness, physical global completion은 기존 gate를 유지한다.
