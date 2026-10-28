# 작업 프롬프트: all-selected-isotope + directional photons + anisotropic-DM background + phenomenological emissivity pilot

이 문서는 사용자가 work thread에 전달할 작업 지시 초안이다. 프롬프트 작성 자체는 실행·게시가 아니다. 아래 권고 기본값은 사용자에게 명시한 pilot 설계 선택이며, 관측 보정이나 새 계산 예산의 기존 승인을 뜻하지 않는다.

## 0. 목표와 완료 정의

$physmath-research-loop를 사용해 기존 rei_bianchi 연구 lane을 보존하면서, 선택된 모든 isotope/ion의 population과 charge fraction을 포함하는 **유한 해상도, 처방된 배경의 현상론적 emissivity pilot plot**을 만든다.

포함:
- 기존 LRS Bianchi I, non-tilted photon angular transport 및 anisotropic redshift.
- 검증된 저장 배경에 포함된 비등방 **DM**의 분포 또는 moments와 그 배경의 H/shear. DM은 이 pilot에서 새로 진화시키지 않고 저장된 evolution을 재사용한다.
- 명시적으로 선택한 현상론적 stellar 및 unresolved-IGM 광자 방출 입력.
- 선택 21 heavy-particle states와 전자·온도·광자·보존 ledger.

제외:
- baryonic anisotropic distribution, baryonic pi_ab closure, finite baryon tilt, full non-axisymmetric/spin-2 transport.
- 새 원자·핵반응 채널, 동위원소 고유 rate 승인, n/T의 임의 활성화.
- 새 radiation/baryon stress를 Einstein 방정식으로 되먹이는 계산.
- 관측에 보정된 astrophysical EoR history, z=0 또는 전체 CMB optical depth, continuum/production PASS 주장.

최종 제목/캡션에 반드시 다음을 넣는다:
“Phenomenological emissivity pilot on a prescribed anisotropic-DM Bianchi-I background; finite angular/spectral resolution; no new Einstein feedback.”

## 1. 먼저 읽고 식별할 근거

매 노드 전에 AGENTS.md, 실제 HEAD, dirty state, 병렬 담당자 예약, 최신 publication hold, durable checkpoint, source/build/input/result hashes 및 누적 예산을 확인한다. 아래 pin은 시작점이지 현재 HEAD라고 가정하지 않는다.

- 기존 REI 인계:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17/research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md
- 선택 종·rate 계약:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0d795da7f9114f89353c72a5829e5efcb64dfa44/research/rei_hheli_pilot_20261021/PHYSICAL_CONTRACT.md
- 재사용할 ANGTHERM01 결과:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/d870ce943005bf93e332ca32ca8c945798b1331c/research/rei_angular_thermochemistry_20261023/SCIENTIFIC_DECISION.md
같은 디렉터리의 THEORY.md, EXECUTION_CONTRACT.md, FINAL_RUN_RECEIPT.json, source 및 raw manifest를 읽는다.
- ANGTHERM02 scoped review:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d10231b1f0f788164d5eadbe1bcee0b802cceca/research/rei_lithium_threshold_20261023/INDEPENDENT_REVIEW.md

현재 중앙 source/admission 변경은 별도로 대조한다. 중앙 수신 JSON의 admission을 실제 provider의 독립 raw-byte 재현으로 확대하지 않는다. REC131의 U5 history coverage는 특정 recombination face의 결과이며, 물리 파라미터 불일치와 H5 미보정 상태를 late-time pilot의 IC로 조용히 전용하지 않는다.

완료된 ANGTHERM01 10개 이력, 기존 83개 전구간, NCP campaign은 재실행하지 않는다. 원본 source와 복구 source가 다르면 별도 lineage로 기록한다.

## 2. 선택 종과 DM 소유권

21 states:
- n
- H1(0,+), D(0,+), T(0,+)
- He3(0,+,2+), He4(0,+,2+)
- Li6(0,+,2+,3+), Li7(0,+,2+,3+)
전자는 charge neutrality로 산출한다. 기존 계약에서 n/T는 0이고 추가 source도 없으므로 absent로 표시한다. 0/0 charge fraction과 log-axis fake floor를 만들지 않는다. 같은 원소의 동위원소 electronic-rate equality를 명시하고, 별도 nucleus abundance로 population을 복원한다. isotope spectroscopy 또는 모든 nuclear target의 완료라고 부르지 않는다.

DM donor에서 다음을 직접 확인한다: component identity가 실제 DM인지, 분포/moment의 정의와 단위, tetrad/frame, normalization, 시간변수, H/shear와 동일 trajectory identity인지, pi_DM가 실제 배경 Einstein evolution에 반영됐는지. 'massive Vlasov'라는 이름만으로 DM이라고 재명명하지 않는다. 분포가 없고 moments만 있으면 moments만 그린다. 누락 성분을 임의로 복원하지 않는다.

소유권 표를 만든다:
DM: frozen donor f_DM 또는 moments, pi_DM, H/shear 재사용.
Baryons: 현행 isotropic/common-temperature closure; pi_b=0 가정 명시.
Photons: directional transport에서 pi_gamma 및 mean/shear work를 진단하지만 새로운 feedback 없음.

## 3. Emissivity 계약: 권고하는 최소 모형

첫 pilot은 모형의 예시적 선택을 명시하고, hidden astrophysical calibration 없이 진행한다. 기존 승인된 source contract가 있으면 우선 재사용한다. 없으면 아래 형태의 명시적 파라미터 모형을 설계하고 config에 수치·단위·선택 이유를 고정한다. 숫자는 관측 best-fit으로 꾸미지 않는다.

기본 선택:
- stellar: escaped stellar photon source. 정상 tetrad에서 등방·비편광 방출.
- IGM: 현재 계산의 gas parcel과 겹치지 않는 unresolved external IGM emitters의 현상론적 diffuse source. 동일 parcel의 RR/cooling 재방출이라고 주장하지 않는다.
- stellar/IGM angular source는 기본적으로 등방이다. 전파 중 anisotropy가 생기는 것과 비등방 방출을 구별한다. DM anisotropy에서 방출 anisotropy를 임의 추론하지 않는다.

예시적 수학 형식:
j_N(E,z) = A_star(z) f_esc(E,z) s_star(E) + A_IGM(z) s_IGM(E)

정의 예: j_N은 normal-frame proper time당 Href nucleus당 에너지당 photon number source [photons Href^-1 s^-1 eV^-1]. s의 적분 정규화, f_esc 적용 전/후 amplitude, 에너지 support, A의 단위를 분리한다. A(z)는 비음수 smooth turn-on envelope, s_star는 명시한 blackbody 또는 cutoff spectrum, s_IGM은 명시한 cutoff power law 등 최소 파라미터 형태를 선택한다. 이미 필요한 문헌값을 사용하면 원문·version·유효영역을 인용한다. 사용자 승인이 없는 fitting/sweep는 하지 않는다.

반드시 수행:
- per-Href/proper-volume/comoving-volume 변환, dt/deta 및 redshift convention 유도.
- normal-frame 방출량을 기존 fixed-covariant-momentum measure와 angular weights로 보존적으로 옮기는 source column 유도.
- 광자수와 energy injection을 같은 spectrum에서 계산하고 gas에 같은 에너지를 중복 가열하지 않는다.
- 외부 주입 에너지는 명시적 external-energy ledger에만 더한다. 흡수 때 photon energy가 threshold/internal energy와 thermal heat에 어떻게 분할되는지 기존 convention과 맞춘다.
- escape fraction은 한 번만 적용한다. 출력 에너지 영역 밖 tail, boundary flux, 미표현 spectrum은 ledger와 제한으로 남긴다.
- 지속 방출은 매 시각의 새 birth cohort다. 새 photon을 기존 초기 packet에 단순히 더해 모든 photon이 같은 age/redshift를 갖게 하지 않는다. cohort 또는 equivalent conservative source-time discretization을 설계한다.
- 원래 6-bin initial UV와 지속 emissivity는 별개다. 최소 본실험은 initial UV=0에서 stellar source를 켜고, 기존 initial-UV 결과는 재사용 대조군으로 둔다.

IGM을 '현재 gas의 재결합/냉각 재방출'로 바꾸려면 별도 내부 reprocessing 계약이 필요하다. 그 경우 Eesc에 이미 계상된 RR energy를 수송 photon source에 중복 계상하면 안 된다. number/energy/threshold/escape ledger와 가스 에너지 소유권을 재유도하고, 고정된 bolometric ledger만으로 임의 spectrum을 물리적으로 검증됐다고 주장하지 않는다. 이 확장은 첫 pilot의 기본값이 아니다.

## 4. DAG와 노드별 acceptance

N0 authority/source/budget/owner lock
  ├─ N1 frozen photon+DM donor recovery and identity
  └─ N2 species+emissivity+energy-owner contract
N1 + N2 → N3 source-time/spectral/angular conservative adapter
N3 → N4 algebra/implementation/unit gates
N4 → N5 bounded new emissivity pilot cases
N5 → N6 observable-wise refinement and control comparisons
N6 → N7 all-state plots and claim audit
N7 → N8 independent review and durable handoff

N0: STATE.json, SOURCE_IDENTITY.json, OWNER_LOCK.json, BUDGET_LEDGER.json을 작성한다. source/head/병렬 작업을 식별하고 미계측 비용은 UNKNOWN, 기존 예산은 초기화하지 않는다.

N1: 기존 NPZ/manifest/receipt의 바이트와 해시를 대조하고 미회수 자료만 가져온다. DM identity, normalization, H/shear/density/time-domain 연결표를 만든다. DM의 중력 효과가 배경에 이미 포함됐다면 별도 forcing으로 다시 더하지 않는다. 부족한 근거는 물리적 FAIL이 아니라 MISSING_EVIDENCE다.

N2: SOURCE_CONTRACT.json, 21-state registry, energy-owner 표, MODEL_CONFIG.json을 만든다. 단위·frame·normalization·escape 및 photon/internal/thermal/external energy의 single-owner가 명확해야 한다.

N3: 기존 방향 수송을 다시 구현하지 않고 작은 additive emissivity adapter를 구현한다. REI-L0 balanced source column이 이미 있으면 담당자 예약과 commit을 존중해 재사용한다. 9-fraction quotient의 rate equality·angular symmetry를 다시 확인한다. 새 source가 가정을 깨면 조용히 축약하지 말고 필요한 unfolded 표현을 사용하거나 해당 확장을 보류한다. 각 새 광자는 자신의 birth time/energy/direction을 갖고, 기존 광자의 age를 초기화하지 않는다.

N4: 다음 독립 검사를 수행한다.
- source-off: 저장된 결과와 좁은 기존 회귀 fixture를 재사용한다. 옛 campaign은 재실행하지 않는다.
- zero-opacity source: 적분 주입 number/energy를 해석해 또는 독립 quadrature와 비교한다.
- monoenergetic birth cohort: 방출 시점 이후의 기존 directional redshift map과 비교한다.
- zero-shear/FLRW, 등방 source의 각도 대칭, angular weights와 spectral boundary flux를 확인한다.
- stellar-only, IGM-only, 합산 source의 수지를 각각 검사한다.
- source-aware residual/Jacobian 또는 JVP와 독립 차분 검사를 수행한다.
- 주입 에너지가 있는 계에 내부 에너지 상수를 강요하지 말고 external injection을 포함한 수지식을 검증한다.
기존 정확도 기준은 낮추지 않는다. 새 source에 대한 observable별 허용 오차는 실행 전에 수치로 고정하고 미확정 상태로 실행 gate를 통과시키지 않는다.

N5: 동일 donor/초기 atomic state에서 최소 case 표를 사전 고정한다.
P0: 저장된 no-continuous-source baseline 재사용.
P1: initial UV=0 + stellar-only + directional transport.
P2: initial UV=0 + stellar+external-IGM + directional transport.
P3: P2와 동일 H/density/source에서 directional redshift만 mean-only로 바꾼 counterfactual control.
P3는 self-consistent isotropic-DM universe도 DM의 독립 인과효과도 아니다. 서로 다른 배경 비교는 별도 범위로 취급한다. 새 P1/P2/P3 실행은 예산·승인 확인 후에만 한다. 모든 완료·실패·partial receipt를 보존한다.

N6: P2를 anchor로 timestep, source birth-time, spectral threshold, angular resolution을 각각 구분해 비교한다. refinement case 수와 비용을 실행 전에 고정하고 무제한 sweep하지 않는다. 기존 ANGTHERM01 M4/8/16 결과를 continuous-source 계의 수렴 증명으로 전용하지 않는다.
관측량: charge fractions, abundance-weighted populations, T, n_e/Href, 해당 구간 tau, photon number/energy, mean age/age CDF, 종별 적분 photo-events, Li/He threshold-sensitive observables, pi_gamma, shear work.
보존·구현 일치·continuum error는 별도 gate다. 수렴 부족 시에도 finite-resolution pilot 그림은 HOLD 표시와 함께 제출할 수 있지만 전체 정확도 PASS로 승격하지 않는다. endpoint만 보지 말고 transient maximum도 비교한다.

N7: 다음 그림을 실제 렌더링하고 확인한다.
1. isotope별 population 및 원소별 charge fraction, n/T absent 표시.
2. T, n_e/Href, 해당 z 구간 tau.
3. stellar/IGM emissivity와 누적 주입/흡수/escape.
4. photon angular moments 또는 방향별 spectrum, DM moments 또는 저장된 실제 분포. 서로 다른 단위는 별도 축/패널로 둔다.
5. mean/directional counterfactual 차이, Li/He threshold diagnostics.
6. conservation residual과 각 refinement 차이를 분리한 패널.
각 곡선에 source SHA, case, 단위, z 범위, finite-grid 및 외부 source 가정을 붙인다. 작은 Li abundance와 Li charge fraction을 혼동하지 않는다.

N8: 독립 reviewer가 이론·source diff·raw results·그림·claim gates를 읽는다. 구현자와 reviewer를 구분한다.
산출물: REPORT_KO.md, STATE.json, DAG.json, CASES.json, VALIDATION.json, BUDGET_LEDGER.json, MANIFEST.json, raw arrays/case receipts, PNG/PDF, REVIEW.md, RESUME.md.
미해결 gate, 원본 입력, 실패와 기존 baseline을 보존한다. 백업 존재, byte identity, restore 성공, scientific PASS를 별도 기록한다.

## 5. 실행·게시 권한과 중단 조건

assistant 자신의 cloud에서 이론·코딩·정적 감사·가벼운 제한 검증을 수행한다. local/NCP로 편의상 전환하지 않는다. 새 장시간 heavy campaign은 시작하지 않는다.

새 IVP 전에 기존 lane과 별개인 pilot unit의 source/input/build hashes, 최대 case/attempt 수, 누적·잔여 CPU/wall, 메모리, checkpoint/stop/resume을 고정한다. 미승인·불명 예산을 초기화하거나 추정 잔여량으로 실행하지 않는다. 승인 범위가 부족하면 계획·코드·승인 범위 내 작은 검증까지 진행하고 필요한 유한 실행 예산만 명시해 요청한다. 완료된 case를 반복하지 않는다.

push, 새 PR, 외부 backup, 다른 작업 thread에 대한 메시지 제출은 이 새 대상·자료를 포괄하는 확인된 승인이 있을 때만 한다. 옛 ZIP5/PR86이나 다른 대화의 요약으로 새 승인을 만들지 않는다. 최신 대상별 보류를 존중한다. cloud 격리 branch 작업과 외부 게시는 별도다.

중단 조건: source 불일치, owner 충돌, 예산 상한, input domain 이탈, single-owner energy 불성립, raw 결과 저장 실패, 예상하지 않은 물리 채널 확대. FAIL/NOT_RUN/BLOCKED/MISSING_EVIDENCE를 구별한다.

## 6. 최종 답변

pilot plot을 먼저 제시하고 새로 실행한 것과 재사용한 것을 분리한다. 채택 범위·미해결 정확도, DM/photon/baryon 소유권, case별 CPU/wall와 잔여 예산을 열거한다. 다음 최소 작업을 1–3개로 제한한다.

압축 판정 예시:
ALL_SELECTED_STATES = INCLUDED_WITH_N_T_ABSENT
DIRECTIONAL_PHOTON_TRANSPORT = FINITE_GRID_SCOPED
ANISOTROPIC_DM = FROZEN_DONOR_REUSED
BARYON_ANISOTROPY = OUT_OF_SCOPE
STELLAR_IGM_EMISSIVITY = PHENOMENOLOGICAL_EXTERNAL_SOURCE
NEW_EINSTEIN_FEEDBACK = NOT_RUN
CONTINUUM_ACCURACY = <실제 gate 판정>
ASTROPHYSICAL_EOR_CALIBRATION = NOT_CLAIMED
OVERALL_PRODUCTION_ADMISSION = HOLD
