# FLRW05 -> native common spectral-stage regression

다음 chat node REI-CHAT-FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION은 별도 external REI-F06 collisionless task와 다르다. Repo cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, draftPR83. Source752e360a 및 후반7e1e590a의 F06 결과를 실제 수신했다. 외부nextF07, F04/F05/F08/F09는 open이다. 시작/단계/게시 전후live ref를 읽고 관련diff만 보존한다.

읽기: README/COHERENT_SPECTRAL_CONTRACT -> SOURCE_BINDING/CONCURRENT_SOURCE_ACK -> immutableZIP의 results/final_verification 및 REPORT필요절. 기존 FT/FLRW/RCT/native 전수suite, 원자연구를 반복하지 않는다. CODEX_SYNC/runtime_returns/F00/F03/FT03와 production source는 변경하지 않는다.

선택한 closure는 N,U를 맞추는 finite-bin exponential, uniform dE기준이다. photon thermodynamic entropy나 arbitrary spectrum recovery가 아니다. N=0이면U=0; 경계mean은delta경로,clip금지. numerical|lambda|<=10000,집중도실제검사는<=1000이다.

다음 최소 작업은 ZIP의 inputs/NATIVE_CALL_VECTORS.json 3bin/96positive-node를 actual public homogeneous_photo_rates에 호출하여 J/A/B/Q와 같은 stage의 PhotonInput을 비교하는 것이다. Python expected값은 native 반환이 아니다. 실제rustc/cargo및sourceidentity를 먼저 확인하고 준비된값을 실행결과로 대체하지 않는다. source가 바뀌면 고정regression과새버전평가를 구분한다.

Old photo node는 P*nHc*MPC_CM^3 per cMpc3, new PhotonInput/PhotonPacket은 P*nHc per reference comoving cm3다. mean-stage perH rate를 다시 nH로나누지 않는다. bin을 한energy로 압축하면 J/A/여러종을 모두 보존할 수 없다. 같은재구성/양의quadrature로 number,energy,heat,edge를 전달한다.

현재 photon_balance에는 독립 U/edge-energy/work state가 없으므로 별도 bounded caller 계약이 필요하다. FT03를사용한다면 raw photo를 포함한 ft03_rhs에 quadraturephoto를 또 더하지 않는다. photons0인local nonphoto를한번호출하고 coherentJ/A를더하는경로는 아직 제안이지 native검증결과가아니다. HG CaseAthermal과rawCaseBnumber를혼합하지않는다.

새 angular_photons.rs의 실제 finite packet geometry를 다시 만들지 않는다. scalarN/U로 occupation/각도분포를 임의생성하지 않는다. 외부124tests는 수신증거이며 이번native실행아니다. fixedE에서는높은에너지donor trace,명시적topboundary,threshold분할을지킨다. exactremap은g<=1,현재상단유입0이며crossingEmin*Nexit를세고retention과중복하지않는다.

양의remap/frozenattenuation을합쳤다는이유로coupled splitting order/timeaccuracy를승인하지않는다. reactioncurvaturebound는smoothK와진짜M2가필요하고 N/U만으로edge오차는bounded되지않는다. powerlaw3..48bin오차를보편화하지않는다. 실제acceptedstage return및독립U수지 검증뒤에만새boundedhistory를판단한다.

기존strictlocal<2e-4/publicwidth<2e-3,[160,161]FAIL=2.1245050576368385e-4,tick160,physicalHOLD,PB02/FT07deferred유지. samebranchappend-onlynon-force와기존Drive/Dropboxcreate-only백업. R1metadata/localhash/remote restore/sciencevalidation별도.
