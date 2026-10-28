# WU088_HH / bass_cr 과학 권위 감사 — 2026-10-25

이 감사는 현재 GitHub PR/head, 계약, 실제 결과 JSON, 실행 코드, 독립 검토, DAG와 선택 Library 원문을 읽어 2026-10-23 계획을 갱신한다. 새 과학 실행·원격 변경은 0이다. 런타임 모델 이름은 관측하지 않았고 지정된 scientific-authority 역할을 수행했다. 전체 비공개 대화·모든 branch 내용을 전수 열람했다는 뜻은 아니다.

## 현재 근거와 상태

| Repo/작업 | 실제 최신 확인 SHA | 선언/구현/실행/채택/전달 |
|---|---|---|
| WU PR148 PHYS91 | 2912a315aa39e7293000b7b2b8c7cc7a706fea9e | exact PSD distance 계약/코드/primary+reference 완료, PASS_SCOPED_EXACT_GLOBAL_PSD_DISTANCE_B1_UNRESOLVED. Draft 게시. 최종 dual R3는 owner receipts 재사용; 이번 원ZIP 다운로드0 |
| CR PR105 H1 ground spontaneous RR | b1aed87852d4f8994494c2ae41a913afd390eccd; science bdfd34499153575305871bd68a139e2878f5f49f | 8 finite-chain/160RHS 실행, 독립40RHS+72coefficient PASS, scoped consumer 채택. Library terminal 원문을 이번 직접 읽음. Library/Dropbox R3는 기존 receipt; Drive UNKNOWN_NO_ACK |
| CR PR100 C23E sibling | 8623d7b2035677fc231976d85fea309f48afd57c | D43 PI/RR/CX conditional source binding 완료·후속전달. PR105와 별도 활성 owner ancestry. 최신 수정일만으로 PR105를 대체하지 않음 |

WU PR139 S0와 CR PR96/C23B를 현재 작업으로 유지하면 완료 근거를 잃는다. WU PHYS83의 실제 완료는 PR140, rates132/steady324/transient732이며 N5 current matrix에서 6a2fc5aacb6182a916b9434c316e99e750e8273c로 확인된다. 오래된 C23C snapshot의 NOT_RUN은 보존하되 현재 상태를 이 값으로 계산하지 않는다. PHYS84 adapter는 준비·유도/정적검토 상태로 numerical admission WAIT였고, PHYS91 완료만으로 이를 수치실행으로 바꾸지 않는다. PHYS85 이론/정적 구현과 reference NOT_VERIFIED도 이후 다른 단위 성공에 의해 소급 승격되지 않는다.

PHYS91 raw RESULTS/REFERENCE와 C9를 읽었다. 동일 153×153 조건부 셀에 대해

0.5808771124940327 ≤ t_PSD ≤ 1.0015608216979872.

선택 dual cp4와 primal cp13은 독립 exact 검토를 받았고 각각11781상삼각 항을 검산했다. 4096projection/16checkpoint의 전체 factor를 모두 독립 재계산한 것은 아니다. β<1<α이므로 B1 존재/배제는 열린다. 이 결과는 formatter guarantee, 승인 C_phys, 물리 uncertainty 또는 실제 nuclear consumer ACK를 만들지 않는다. native cross-section153knots/152cells와 MF33 covariance153groups/154boundaries는 다른 격자다.

CR105 raw primary RESULT는8case,160RHS,24source rows,162comparisons, failures=[]를 기록한다. C9는 각 RHS 자체 norm의 최대상대차7.69509483627e-11<5e-10, intended-real-operator backward residual4.36604660049e-13<2e-12를 기록한다. binary64 diagonal에 tiny hazard가 완전히 반올림되는 항이 있다는 진단도 보존한다. 새 RR 확률1.26101–1.59845e-9와 시간감소0.37017–0.45707ms는 고정 baths의 finite-chain spontaneous ground component다. stimulated/all-level total RR와 postcapture feedback은 미결이다. 전자 에너지진단을 photon/internal energy와 중복 합산하지 않는다.

## 전체 목표에서의 진행

old40nodes/17edges는 계획의 skeleton이지 전역물리 완료분모가 아니다. WU_CE83_OWNER_COMPLETION과 CR_N4_C23B_CUTOFF_BINDING은 완료된 owner 근거로 재사용한다. WU_NUCLEAR_PARTICLE_OWNERSHIP 아래 PHYS85–91의 유도·조건부수치 자식들은 진전했으나 physical atomic→bare source/consumer 부모는 PARTIAL_INPUT_DEPENDENCIES다. CR_N4_STOPPING_KERNEL/N5에는 EE, CE, EI, neutral elastic, H1 ground RR가 추가되었지만 full stopping/coverage는 PARTIAL_OPEN이고 N6/N7은 predecessor gated다. workflow20/20은 해당 유한 단위 완료이며 전체 물리 완료율은 null이다.

범위별 completeness를 구분한다: (a) source-qualified species/process/domain cells, (b) implemented operators, (c) executed input identities, (d) admitted named consumers, (e) delivered artifacts. 한 축의 완료를 다른 축으로 복사하지 않는다. 공개 결과 요약·구조검사·manufactured fixture는 empirical source coverage를 닫지 않는다.

## 모든 대상에 대한 확대 책임

새 사용자 지시는 일부 H/He/Li 채널 중심의 역사적 업무 배치를 확대한다. WU는 모든 configured nuclide/isotope/ion과 관련 반응의 **species/reaction/source 권위**를 맡는다. bass_cr는 같은 목록의 외부 photon·baryon·electron injection과 fast/thermal transport 및 보존적 consumer 권위를 맡는다. 목록을 H1 또는현재8nuclide로 hardcode해 책임을 축소하지 않는다. source identity의 실제 공급 여부는 별도 cell 상태로 유지한다.

확인된 초기 nuclide 집합은 n,H1,D,T,He3,He4,Li6,Li7이다. H1/D/T는q0..1,He3/He4는q0..2,Li6/Li7은q0..3,neutron은q0으로 20atomic populations+1free-neutron row=21이다. free electrons는 thermal/fast의 별도 pools이다. 현재 matrix168cells=21×8processes(CI,RR,DR,CX,PI,neutral_elastic,bound_bound,electron_ion)는 전수완료가 아니라 explicit inventory다. neutron의 atomic processes는 NOT_ATOMIC_CHANNEL이지0rates가 아니다.

전역 registry key는 (Z,A,isomer,charge,electronic_state,chemical_composition,thermal_or_fast_pool)로 확장한다. isotope 자체와 원자 charge/state, molecular isotopologue를 구별한다. n은 핵종, gamma/e±/neutrino는 별도 particle types다. H−,H2,HD,LiH,HeH+ 및 동위원소 확장들은 새 molecular/negative-ion coverage 후보다. H1H1/H1D/Li6H1/Li7H1/He4H1처럼 isotope constituents를 명시하며 source 없이 rate를 만들지 않는다. 이 후보가 현재 채택된 물리 population이라는 뜻은 아니다. 추가 nuclear daughters, isomers와 원래 network figure의 전체 목록은 미확인이다. 원 nuclear PNG=NOT_RECOVERED_NOT_READ를 보존하고, 검색하지 못한 핵종을 absent/zero로 쓰지 않는다.

책임 재배치:

- WU: 원자·이온·분자 species/reaction registry, isotope mass/threshold, thermal CI/RR/DR/CX/CE/PI source와 nuclear/weak event kinematics·mass/Q·branching·covariance. 기존 PHYS91 owner thread 계속.
- BASS_HE: 각 관련 species의 differential collisions/secondary law/finite mass/angular calibration; WU/CR의 별도 중복 provider 생성 방지.
- rec_bianchi: state-resolved bound-bound/free-bound radiation, cascade, recombination initial charge, opacity/emissivity/redistribution/escape. WU의 WU_SPECTRAL_GEOMETRY_COUPLING은 microscopic 공급자로 유지하고 radiation history 주관은 REC, coupled cosmological 적용은 REI로 옮김.
- bass_cr: 외부 particle source normalization/frame/clock/volume, spectral photon-to-photoelectron injection, fast electron/ion/baryon transport 및 thermal assimilation, reaction competition. CR_BETA_FULL_OWNER에서 평가 nuclear decay spectrum·Q supplier는 WU로 이동하고 CR은 Lorentz/pool injection consumer를 유지.
- WU088_HH: 재사용 species/stoichiometry/reaction identity compiler의 lead owner. 중앙에 준비된 REI-CHEM-LEDGER-01을 WU로 이관한다. rei_bianchi는 scenario event assembly, coupled thermochemistry/radiation/geometric RHS와 최종 consumer admission을 맡는다. Manufactured molecular canonicalization을 empirical rates로 승격하지 않는다.
- bass: 보존적 transport/geometry 소비·history operator, vigilode: numerical error/solver authority. WU 또는CR의 독자 cosmology solver 확장은 없음.

이 배치는 새 global scientific admission이 아니라 책임/계약의 확대다. 모든 관련 외부 source를 local injection boundary까지 목록화하고, stellar/AGN/CR/decay source의 모델/시간·공간이력은 REI application 선택과 CR source manifest에 귀속한다. emission/absorption 미시계수는 WU/REC/HE 중 해당 physics owner 하나로 지정한다.

## 실제 다음 단위

즉시 가능한 새 단위는 중앙에 준비되고 WU lead ownership으로 이관되는 REI-CHEM-LEDGER-01 isotope-resolved composition/stoichiometry/energy-owner compiler다. C23C atomic_contract.py는 single-nuclide,nonnegative charge,CI/PI/RR39directions와 exact event energy/isotope quotient를 이미 구현했다. 그것을 재발명하지 않고 composition vectors,negative ions,molecules,isomers,reversible signatures,explicit electron pools로 확장한다. 이번 실제 source inspection에서 이러한 cross-molecular canonicalization은 관측되지 않았다. default-branch 검색0은 전 repo 부재증명이 아니다. 중앙 준비를 맡은 REI authority에 exact parent blob e308ceef315e9f40f96fa62c2667253a1283523e를 전달했다.

WU 다음 물리 단위는 current MT102 nominal에 대응하는 approved full-precision covariance/formatter, 실제 atomic→bare kernel, mass/electron/target state, support-tail B0/BA, named thermal/fast/radiation consumer ACK를 결속하는 source 계약이다. PSD 추가 탐색을 자동 기본값으로 삼지 않는다. 입력이 확보되면 그 변경 identity의 코드/검사만 수행한다.

CR 다음 후보는 He4 ground spontaneous RR의 기존 REI151/C23B provider를 새 named consumer에 결속하는 작업이다. 기존 PR105 owner thread/새 branch freshness 확인 후 source-native thresholds,statistical factors,isotope assignment,zero-recoil 또는 finite-mass convention,proper clock,targetdensity와 retained-photon energy를 먼저 고정한다. 이 audit는 numeric 실행을 승인·수행하지 않았다. 전체 N5를 이 한 component로 닫지 않는다.

## 예산·운영·근거 한계

PHYS91 primary/reference/Wolfram remaining0,budget_reset=false; historical/global CPU·currency·remaining=null. CR105 known lineage39.097868524CPU s는4.86342341 신규+34.234445114 inherited다. C23E의 다른 lineage15.493261114를 무작정 더하지 않는다. 새 단위 비용은 별도 cap/admission이 확인되기 전 UNKNOWN_NOT_ZERO,heavy_run=false다. 원 프로세스·lease를 건드리지 않는다.

WU 최신 branch AGENTS 첫 priority는PHYS71에 머물러 있다. 최신 immutable PHYS91 계약/결과와 현재 사용자 범위를 적용하는 최소 scheduling correction이 필요하다. preserved frozen source·원자물리·HH_R10OFF·productionNOT_ISSUED는 그대로다. CR main AGENTS는404였으나 PR105 branch에는 실제 AGENTS가 있으며읽었다. branch-specific 정책을 default branch 부재로 대체하지 않는다.

선택 Library terminal은 실제 읽었고PR105 source/head/20rows와 일치한다. root가 C23E terminal을 별도로 읽는다. WU dualbackup와 CR canonical rawarrays는 owner manifests/reviews를 재사용했으며 이 audit에서 새 wholeGET/restore를 했다고 쓰지 않는다. personal_context는 이번 agent에 UNAVAILABLE였다. 전체 private conversations와 external live runtime은 UNOBSERVED다.

## 최종 root 책임 정렬

`authority/ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md`에 따라 reusable species/stoichiometry/reaction identity compiler의 lead는 WU다. REI는 selected scenario event assembly와 consumer다. REC는 molecular state/spectral HD adapter를 맡는다. 모든 atomic repo는 자신의 process 책임을 동일한 전체 target catalog에 적용한다. 다음 작업 readiness는 선택 모형의 실제 입력·domain에 조건부이며, 모든 미래 channel의 전수완료를 bounded 작업의 선행 AND 조건으로 강제하지 않는다. 중앙 compiler의 별도30CPU s/120wall s/512MiB 허용량은 root 계약에 속하며, 이 audit가 이전예산을 reset하거나 새허용량을 만든 것은 아니다.
