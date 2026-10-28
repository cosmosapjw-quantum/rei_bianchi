# WU088_HH 확대 연구 헌장 — 2026-10-25

WU088_HH는 전체 목표에 등장하는 모든 핵종·동위원소·원자·이온·상태와 이들이 이루는 분자·음이온의 species/reaction/source 물리를 책임진다. 기존 H–H 및 H/He/Li의 특정 채널 연구를 보존하면서, 외부 photon·baryon 공급과 방출·흡수·열적 변화에 필요한 미시적 반응 입력을 전체 프로젝트에 공급한다. 새 사용자 범위를 반영한 책임의 확대이며 기존 유한 결과의 물리적 채택 범위를 소급 변경하지 않는다.

Species key는 핵종(Z,A,isomer),전하q,electronic/rovibrational state,분자 isotope constituents와 thermal/fast pool을 분리한다. 확인된 시작 목록은 n,H1,D,T,He3,He4,Li6,Li7이다. 20atomiccharge states+free neutron21행은 기존 named view로 보존한다. 모든 configured nuclei/daughters/isomers와 음이온/분자는 새 registry에 추가하며 기존8nuclide를 영구 상한으로 삼지 않는다. 아직 회수되지 않은 nuclear network 전체 목록은 UNKNOWN으로 표시한다. H−,H2,HD,LiH,HeH+의 isotope-specific 확장은 계획된 source coverage이며 계산된 rates가 아니다.

WU의 공급 범위는 CI,PI,RR,DR,CX,CE/deexcitation,atomic/molecular formation/destruction,photodetachment/photodissociation,핵반응·weak decay의 source,질량·binding/Q값,threshold,branching,열적 rate와 number/energy/momentum moments,uncertainty/covariance다. 각 행은 source-native units/frame/support,상태·isotope mapping,정규화·clock·density와 유효온도/밀도를 명시한다. Missing source/value는 null이고 physicalthresholdzero,notapplicable,covered-not-evaluated와 구분한다. tail·threshold-gap·isotope transfer가 없는 유한 source를 전체물리 rate로 extrapolate하지 않는다.

역할 경계는 다음과 같다. BASS_HE는 differential collision·secondary/angular·finite-mass provider,rec_bianchi는 state/spectral emission/absorption/cascade·radiation history, bass_cr는 external injection/fast transport/thermal assimilation,WU는 재사용 species/stoichiometry/reaction identity compiler의 lead이고 rei_bianchi는 scenario event assembly와 coupled consumer다. WU는 state/branch source를 REC에,fast-product kernel과 evaluated beta source를 CR에,thermal/source registry를 REI에 전달한다. WU_SPECTRAL_GEOMETRY_COUPLING의 radiation-history 주관은 REC로, cosmological coupling 주관은 REI로 정렬한다. 기존 owner 작업은 유지하고 같은 provider를 새로 중복 구현하지 않는다.

사건마다 원자·분자에서는 각 isotope nucleus 수와 totalcharge를 보존한다. 핵반응에서는 반응식에 맞는 baryon/charge와 lepton ledger를 검사하고 isotope 수 자체가 보존된다고 요구하지 않는다. 동일 frame의 총에너지는 thermal/fast kinetic,internal/rest-mass convention,radiation,recoil,escape에 유일하게 배분한다. Nuclear Q를 mass ledger에 이미 포함했다면 별도 heat로 다시 더하지 않는다. isotope mass변경은 threshold/relativevelocity/recoil/branch-energy의 영향 의존성을 함께 갱신한다.

현재 PHYS91 parent `NUCLEAR_BARE_KERNEL_SOURCE_AND_CONSUMER_CONTRACT`는 PARTIAL_INPUT_DEPENDENCIES다. exact PSD distance enclosure는 채택된 유한 수학 결과이고 B1은 미결이다. 다음은 current MT102 nominal-covariance·formatter,실제atomic→bare kernel,mass/electron/targetstate,support-tailB0/BA 및 thermal/fast/radiation namedconsumer ACK의 물리 계약이다. 완료한 PHYS78–91과 각 inherited source/실행을 재사용한다. PHYS91 remaining0,globalremainingnull; noreset/noheavylaunch.

HH_R10=OFF와 productionNOT_ISSUED는 원 microscopic/native gates가 별도로 닫힐 때까지 유지한다. 과학유도·구현·실행·consumeradmission·전달은 독립 축이다. 새 파일은 전용 additive expansion branch에 게시하고 active owner branch나 historical result를 덮어쓰지 않는다. 기존 AGENTS의 frozen source·precision·tolerance·resource 규칙은 유지하며 오래된 PHYS71 scheduling priority보다 현재 사용자 범위와 실제PHYS91 handoff를 적용한다.

작업 readiness는 선택한 모형의 source/domain/consumer 조건으로 판정한다. 모든 미래 species/process의 전수완료를 각 bounded 작업의 필수 선행조건으로 삼지 않는다. 중앙 root 책임 계약의 최신 owner 정렬을 적용하고 기존 finite admission은 보존한다.
