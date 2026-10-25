# 다음 연구 인계 — BASS_HE — 2026-10-25

먼저 PR101의 실제 HEAD, CLAIM_GATE와 RESOURCE_LEDGER를 읽습니다. finite-mass direct CBA는 scoped numerical PASS이며 전달 19/20, C8 export가 열려 있습니다. reserve는 0이므로 현재 allocation에서 science/plot/export를 추가 실행하지 않습니다. 원 PASS/FAIL/FAIL과 실패 원인을 보존합니다.

확장 임무는 일곱 핵종의 모든 전하 상태와 source-selected 분자에 대한 differential collision, 유한질량 운동량·에너지 전달, thermalization 및 heat-capacity/particle-count closure입니다. 외부 nonthermal distribution/cascade/stopping의 lead는 CR이며 HE는 collision kernel을 제공합니다. WU species/elementary channel, REC populations/spectra, BASS geometry, REI scenario와 연결합니다. TASK_ASSIGNMENT의 조건부 의존성은 선택한 채널에만 적용합니다.

## 고정 source와 세부 재개 기록

$physmath-research-loop를 적용한다. REPO_CHARTER_KO.md와TASK_ASSIGNMENT.json으로 모든목표핵종·동위원소·이온·선택분자의 kinetic energy/momentum/stress와externalparticle/photon-produceddaughter source연구를이어간다. 요청Astra-tier와실제runtimeNOT_OBSERVABLE을구별한다.

관측base는 cosmosapjw-quantum/BASS_HE PR101,branch research/he-ang-finitemass-cba-20261025,HEAD28a26f4db951ab9085180e2ecc5d600d981a1f71이다.
https://github.com/cosmosapjw-quantum/BASS_HE/pull/101
먼저actualHEAD/AGENTS/parallelowner를다시읽고research/he_ang_finitemass_cba_20261025/CLAIM_GATE.json,THEORY_KO.md,LOOP_PROGRESS.json,RESOURCE_LEDGER.json,HANDOFF_RESEARCH_KO.md,delivery/를읽는다.

현재finiteMdirectCBA는theory/finitechecksPASS_SCOPED,actualdelivery19/20,C8PARTIAL_EXPORT이다. ScienceS9fc8185437f145a6ba4569e1b38aa2e12d15acd9,DeliveryD28a26f4db951ab9085180e2ecc5d600d981a1f71,centralC46a102b22b54cc03a91ad92bbd58d68dd82b7964,E38ea3bbccc4f62e5e6d579fd1b6fb8c3453ddd30.
ActualchildPASS/FAIL/FAIL,exit0/-9/-9. 두개별CPUovershoot와killcauseNOT_OBSERVABLE유지. SVG/producerFIGURE_METADATA/원REPAIRSUMMARY없음,C9-EXPORT-01OPEN. 실패를PASS로바꾸거나원summary를fabricate하지않는다.

새unitCPU11.882829s/wall11.985978921002243s,cap12/35. PR100+이번CBAlineage16.870803/17.108468335994985,cap20/60. repairreserve1used/0remaining. 현재allocation에서science/plot/export새START없음. 새node로cost/failure/unknown/reserve초기화금지. 새allocation과owner승인이필요한export는기존HE101owner에남긴다.

PR99finiteMkinematics와PR100stableNordsieckoverlap을재사용한다.
mu=M/(M+1),nu=(M+1)/(M+2),B=mu/2,epsilon=nuE0-mu/2.
유한mass의두위상 exp(i muDelta·r)-exp(-iDelta·r/(M+1)) 모두필요.
FM의source는L_mu(muDelta,k)-L_mu(-Delta/(M+1),k),W=4|FM|²/(|P|Delta⁴),
Jacobi=mu nu q kW,lab의모든positive simpleroot에해당W를각각평가한다.
Er은pairrelativeenergy이며labEB가아니다. a0,p0,Eh 변환과nonrel/labelled/directC1closure를유지한다.
Exchangecomplete3bodyphysicalprovider/totalphysicaleventsigma/physicalrecoil분포/HE-X1empiricalcorrection은false.

17targetedmethods,12generic,3two-termoriginalintegral,12tiny,4kinematic,24/48/96fold,73angles,8masspoints의실제저장결과재사용. 기존suite나완료prefix재실행0.
PR97PWBE19/20historicalsnapshot의C8은PR98d477aafcc620a010e954aa711d108fa2761a1d7e의actualsaved-outputcontinuation으로완료됐다. PR101C8은별도현재OPEN이다.
DDCS20finitewindow(20eVbeam,3–6eVdetected,15–120deg),CCCconditionalphase,TDCS54twoanchors,TDCS41313pointshape검사는각범위그대로다. sparse/marginaldata를fulljointlaw로승격하지않는다.

B2science2732504bytes SHA2560662cb03fd141886e5c77c1661d2fb5314173f46498c27a878bf6571188d4baf,Drive15RPRyRzRorUuYA4t5MvUMm2np_Nt7rjR,Dropboxid:BSpOijBcT10AAAAAAD_90g.
B3delivery688666bytes SHA256f86184b3422af7c48a3c006d0d5386e7674ce47d573bbd0dd6235512007607b3,Drive1dQRZYlTslOHE8atau97g4kS6ozaegdB3,Dropboxid:BSpOijBcT10AAAAAAD_90w.
당시actualdualACK+metadataid/size와localmemberbytePASS를재사용한다. 이번읽기가remotewholeGET검증은아니다. 복구필요시B2검증복원후B3overlay. B3는B2를embed하지않는다.

확장목표H1/D/Tq0..1,He3/4q0..2,Li6/7q0..3를전부명시하고n/e와source-selectedmolecularstates를별도추가한다. WU는 species identity와 elementary atomic/molecular/nuclear/weak channel·branching·energy를, REC는 level populations/spectra/history를, HE는 differential collision/thermalization·heat-capacity closure를 소유한다. CR는 external nonthermal distributions/injection/cascade/stopping, BASS는 geometry/background/covariant coupling, REI는 selected scenario/assembly, vigilode는 numerical integration을 소유한다.
한jointlaw에서electroncount/ionrecoil/crossmoment를얻는다. Birthkineticenergy는thermalizationrate가아니다.
pi_b=sum_s[pi_s+rho_s drift_<i drift_j>]로commonbulk에합성하고,commonT/u는timescale/observableerror로정당화한다. particlecount/heatcapacity/binding/bandboundary/nuclearQ/nonthermalreservoirmustremainseparate.
externalUVBz<=15.1를z20으로extrapolate하지않는다. source-validity밖relativistic/nonthermaldomain을기존nonrelkernel로처리하지않는다.

HE-ANGSOURCE_INPUT_PENDING,globalphysicalcompletionnull,physicalproviderfalse,productionNOT_APPROVED,activationfalse를유지한다. 다른ownerCR105/WU90/REIHI/C23E의scoped진전과OPEN을보존한다.
다음실행가능전이는HE-EXP-SPECIESactualsourceinventory와onepair/sourceintake다. provider가성립하면선언한selectedchannel만HE-EXCHANGE/CLOSURE로연결하며전종fullcampaign을선행조건으로삼지않는다.
확장branch는research/program_expansion_20261025/만additive로쓴다. 원HE101owner/계약/실행원장을보존한다.



공통 lead-object 정책은 root의 2026-10-25 expansion contract를 따른다. 모든 새 task는 TASK_ASSIGNMENT.json의 lead_repo와 consumer_repo를 구별한다. 기존 finite source 계약과 owner 기록은 historical evidence로 보존한다. Molecular LAMDA/CDMS/JPL/ExoMol adapters는 REC lead이며 elementary molecular channels/branching은 WU에서 소비한다. 새 WU chemical ledger compiler는 중앙 staged unit으로 별도 수행 중이므로 여기서 중복 실행하지 않는다.

P2 readiness 교정: WU-led HE-EXP-NUCLEAR는 species/mass/branch/source 입력에서 daughter payload를 생산한다. downstream HE-EXP-STOPPING의 완료를 기다리지 않는다. nuclear daughter를 선택한 stopping consumer가 HE-EXP-NUCLEAR에 조건부로 의존한다.

일곱 동위원소 목록은 extensible WU catalog의 초기 관측 view이며 미래 target universe의 상한이 아니다. 새 nucleus/isomer/anions/molecular identities와 source gaps를 명시적으로 확장한다.


## 중앙 조립 참조

정본: `DAG.json`. 개별 계약: `contracts/<node-id>.json`. 원 작성자 파일은 `authority/`에 변경 없이 보존했습니다. 아래 목록은 이 저장소의 정본 lead 노드이며, 다른 저장소 lead 작업의 소비자 관계는 원 TASK_ASSIGNMENT와 계약에 그대로 남아 있습니다.

- `HE-X1`
- `HE-ANG`
- `HE-EXCHANGE`
- `HE-RESERVOIR`
- `HE-CLOSURE`
- `HE-FEEDBACK`
- `HE-EXP-JOINT`
- `HE-EXP-PAIR`
- `HE-EXP-PHOTON-PAIR`
- `HE-EXP-CLOSURE`
- `HE101-EXPORT`

새 예산은 각 원 계약만 따릅니다. 완료 결과를 재계산하거나 자식 완료를 부모 완료로 승격하지 않습니다. 전역 물리 완료율은 null, L4 준비 상태는 false입니다.
