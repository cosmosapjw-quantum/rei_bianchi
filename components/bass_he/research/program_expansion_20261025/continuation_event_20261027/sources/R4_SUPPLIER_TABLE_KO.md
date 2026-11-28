# HE-EXP-EVENT-03: WU R4 원전과 소비자 범위

WU `research/provider-registry-20261025@f949c21cca6e2534b725241068bd6c6e06158495`를 고정했다. 실제 catalog 경로는 `registry/provider_overlay.json`이다. 원형13파일231,150bytes를 `raw_wu_r4/`에 저장하고 각 Git blob·SHA256·bytes·URL을 `raw_wu_r4/SOURCE_MANIFEST.json`으로 확인했다. `SOURCE_REFS.json`은 문서와 row pointer를 연결한다. Full paper PDF와 WU 실행 코드는 가져오지 않았고 저장된 fit·compiled·독립검증 결과만 재사용했다.

## 1. 인벤토리 관계와 승인 경계

| 관계 | 결과 |
|---|---|
| 기존 HE snapshot | 92 species IDs / 132 variants / 149 saved event references |
| R4 species 파일 | 14 records; 기존 H+·D+ 2개는 동일 ID와 compiler record |
| 이번 consumer reference union | **104 IDs / 138 variants / 155 event references** |
| ID 증가 | 12개, 구성은 atomic4 + molecular8 |
| 전체 inventory 역할 | atomic74 / molecular25 / neutron1 / anion1 / electron3 |
| R4 variant / 소유권 | 6 variants / 5 source ownership groups; TIQM·SQM은 같은 사건의 대안 |
| R4 선언된 material 채널 | RA 2→1+primary photon 1개, material2→2 5개 |
| 새 물리 승인 | populations/rates/Q/energy/DCS/activation 모두 false |

`WU_R4_CONSUMER_UNION.json`은 WU ID를 새로 만들거나 바꾸지 않는다. 기존92 projection과 R3 overlay의 원래 SHA를 유지했다. R414개를92개에 단순 더하여106으로 쓰지 않는다. Source ensemble이 겹치므로104개를 동시에 진화하는 독립 population으로 읽지 않는다. `automatic_rate_DCS_mass_binding=false`이며, 실제 consumer의 분포·질량·상태·각법칙을 자동으로 채우지 않는다.

## 2. 실제 native 값·support·방법·소유권

수치 예시는 원전의 첫/마지막 인쇄 행을 그대로 옮겼다. 새 fit 계산이나 보간 결과가 아니다. 전체77 coefficient cells와 exact literals는 `raw_wu_r4/sources/MOLECULAR_SOURCE_PACKET.json`에 있다. 모든 source references와 원문 식별자는 machine-readable `provider_supply`에 포함한다.

| Variant / material 채널 | Native 수치와 support | State·방법·spin·단일 소유권 | 미해결된 DCS·각·질량·공동분포·열화 입력 |
|---|---|---|---|
| **BENNETT2003_LIH_SPONTANEOUS_RA_TABLE3** — Li(2s)+H(1s)→LiH(X)+primary photon | 27cells, 50–10,000K. k(50)=3.86×10⁻²⁰, k(10,000)=24.6×10⁻²⁰ cm³s⁻¹. Spontaneous association; stimulated-blackbody curves와 분리. | Source7Li; H의 질량수 미명시. LiH는 bound/quasibound survival-weighted aggregate. Electronic factor1/4는 원계수에 이미 포함. 한 association 사건의 primary photon1개와 cascade/escape를 구별. **NR material2→2 대상이 아니다.** | Photon's joint energy/direction·recoil·survival/cascade branch, Li/H/LiH state masses와 binding, radiative consumer/escape·deposition 필요. Scalar k(T)로 angular law를 만들지 않는다. Total cascade/escaped yield·energy는 null. |
| **BOVINO2009_LIH_H_TO_LI_ORTHO_H2_TABLE1** — LiH+H→Li+ortho-H2 | 14cells, 10–10,000K. k(10)=1.57×10⁻¹¹, k(10,000)=6.20×10⁻¹¹ cm³s⁻¹. J=0 coupled-channel 결과에 uniform J-shifting 적용. | Source7Li; 초기 LiH v,j 미지. Final ortho rovibrational sum. Para와 spin normalization 결속 전 합산하지 않음. 고유 ownership group. Printed fit의 b 단위 충돌로 fit 평가 격리. | State-resolved branch와 Δε, isotope/mass convention, differential angular moment·finite recoil·outgoing correlation 및 named deposition 필요. Native exothermicity2.258eV는 승인된 branch Q가 아니다. |
| **BOVINO2009_LIH_H_TO_LI_PARA_H2_TABLE1** — LiH+H→Li+para-H2 | 14cells, 10–10,000K. k(10)=1.71×10⁻¹¹, k(10,000)=4.90×10⁻¹² cm³s⁻¹. 동일 J=0+J-shifting 방식. | Initial v,j 미지; final para rovibrational sum. Ortho와 source-weight 결속 전 합산하지 않음. Ortho와 별도 group이지만 미확인 spin 요인을 덧붙이지 않음. Fit b 단위 충돌 보존. | Ortho 행과 같은 질량·state defect·DCS/angular/joint/deposition 공백을 para branch별로 채워야 한다. 기존 수렴오차 표기는 전체 PES/rate의 물리 오차 한도가 아니다. |
| **HONVAULT2013_CORRECTED_HD_FORMATION_TIQM** — D++p-H2(v0,j0)→HD(sum)+H+ | Corrected Table1의10cells, 10–100K. k(10)=1.35219×10⁻⁹, k(100)=1.66138×10⁻⁹; source unit은 cm³ molecule⁻¹s⁻¹. 채택한 보간 없음. | TIQM. Initial para v0,j0 명시, HD product v,j 미분해. 아래 SQM과 **동일 ownership group 및 physical-event key**. 두 방법을 별도 물리 사건으로 더하지 않음. | HD final-state branches와 state energies, 질량 convention, channel별 DCS/angular/recoil·joint products, actual state population와 thermalization consumer 필요. Corrected scalar total은 이를 제공하지 않는다. |
| **HONVAULT2013_CORRECTED_HD_FORMATION_SQM** — 같은 material2→2 채널 | 같은10 nodes. k(10)=1.75178×10⁻⁹, k(100)=1.86348×10⁻⁹; source unit cm³ molecule⁻¹s⁻¹. | SQM 대안. TIQM과 source-row variant는 분리하되 physical ownership은 공유. Method 차이를 확률적 불확실도 분포로 바꾸지 않음. | TIQM 행과 같은 state/mass/DCS/angular/joint/deposition 의무. 한 방법을 선택하는 계약이 필요하며 두 계수 합산은 금지. |
| **GONZALEZ_LEZANA2022_HD_HPLUS_DESTRUCTION_THERMAL** — H++HD(thermal)→D++H2(sum) | 실제 인쇄 비교점2개: k(205K)=1.21×10⁻¹⁰, k(295K)=2.21×10⁻¹⁰ cm³s⁻¹. 논문의 계산 범위5–3000K와 fit 검증 support를 구별. 이번 WU 원식 비교는 두 native 점만. | SQM thermal HD v0,j0…8 Boltzmann mixture at kinetic T; product H2 v0,j0…9 source-spin-weighted sum. Honvault initial p-H2와 다른 ensemble이라 자동 detailed balance 없음. | 동일 T의 전체 initial-state d_j·energies·spin weights, 실제 x 또는π, state masses·branch defect, angular/joint recoil·deposition 필요. Aggregate2점에서 d_j를 역산하지 않음. Fit405K는 activation parameter이고 Q가 아님. |

## 3. HE 조건부 moment 이론과의 연결

다섯 material2→2 variant 행은 **조건부 NR 이론의 입력 형태 후보**이다. 현재 원전에서 실제 DCS나 각 moment가 승인된 것은 아니다. WU 번호 투영의 nuclei/charge 보존은 입자수 계약이며, 실제 source ensemble을 고정된 질량·상태 branch로 결속하는 작업은 별도다. Incoming/outgoing correlation과 공급자 source frame도 열려 있다.

부모의 NR2→2 유도는 보존되는 composition mass와 explicit internal-energy offset을 따로 선언하는 조건부 모델에서 사용한다. 실제 isotope ground rest mass에 binding defect를 이미 넣고, 같은 binding을 ε에도 다시 넣는 자동 매핑을 만들지 않는다. 현재 packet의 state/mass transfer는 false이므로 공급자 질량·Δε를 이 문서가 수치로 채우지 않는다. Bennett RA의 photon recoil은 material-only NR2→2 증명에 넣지 않는다.

에너지는 하나의 사건을 기준으로 number, bulk momentum/energy, thermal, internal/binding, fast pool, radiation·escape 항에 한 번씩 배분한다. Population에서 internal energy를 구성한다면 같은 event 내부에너지 변화를 별도 heating RHS로 다시 가산하지 않는다. 실제 thermalization을 채택하려면 해당 상태·분포·frame의 named consumer와 source flux가 필요하다.

## 4. 저장된 결과 재사용과 이번 기계 검증

WU scoped admission은 원전6variants/77cells, 조건부13claims, 새6integer columns 및29native formula points를 수용했다. 원식과 Decimal80의29점 대조, implementation28/28 및 독립8/8·1138assertions를 다시 실행하지 않았다. `registry/fit_diagnostics.json`, `raw/INDEPENDENT_RESULTS.json`, `verification/IMPLEMENTATION_RESULT.json`은 원형 bytes이다. Fit residual은 physical covariance·confidence distribution·DCS 오차가 아니다.

이번 `build_wu_r4_intake.py`는 표준 JSON·hash·ID/참조 관계만 처리하여77개의 기계 검사를 통과했다. 이77은 우연히 native coefficient cell 수와 같지만 서로 다른 수이다. 과학/fit 평가0, compiler0, 과거tests0이다. Exact source 13개와 immutable baseline identity, H+/D+ 중복2, 신규12, refs138/155, RA1 및 material2→2 5, 소유권5를 확인했다. Source rows의 optional photon_ledger 표시 도중 발생했던 KeyError는 `SOURCE_INTAKE_RESULT.json`에 보존했으며, optional native field와 명시된 event photon 필드를 구분하도록 표시 코드만 고쳤다.

`registry/COMPLETE.json`은 원문 그대로여서 본 최소 묶음에 필요 없는 lift_examples/projections의 hash도 참조한다. 이 두 보조 산출물은 다시 가져오지 않았으며 `SOURCE_REFS.json/unbundled_complete_members`에 명시했다. WU 과학 소유권, HE101 C8 OPEN·기존 소진 예산, DRIFT02/WU249 재실행0과 물리 activation=false를 유지한다.
