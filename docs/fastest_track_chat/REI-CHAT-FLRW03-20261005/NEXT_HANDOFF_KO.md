# FLRW03 -> actual event-weighted consumer contract

다음 chat node는 REI-CHAT-FLRW04_EVENT_WEIGHTED_CONSUMER_CONTRACT다. 외부 Codex REI-F04 sparse nonlinear remainder와 별개다. PB02/FT07은 deferred. 같은 branch forward/rust-reion-kernels-20260922와 draftPR83을 유지한다.

시작/단계 경계/게시 전후 live ref를 읽는다. 최종 수신 ccbc15019296b9128a90fa45b9c68c7daddc7b77은 기존 aa3e98d7 이후4 commits다. 새 flrw_three_equations.rs와 외부84 tests를 읽었다. CONCURRENT_SOURCE_ACK와 실제 callback을 먼저 확인하고 이미 존재하는 pointwise hook을 부재로 취급하지 않는다. 기존 CODEX_SYNC/runtime_returns/F00/F03는 수정하지 않는다.

현재 실제 연결점은 connected_cell(AtomicProvider+hhe_rhs+photo bridge), photon_balance(fixed-energy caller-supplied edge spectrum), ensemble(같은 배경/고정 volume weights), filling_defect(외부 QV/derivative), sharp_filling_rhs(선언한0<QV<1 sharp closure)다. thermal/escape는 connected_cell의 소비범위 밖이며 독립 front/포화 모델도 아니다.

다음 bounded 결과: 실제 consumer call site의 stage time,a,H,nH,T,population,photon birth time/energy,source/count units,edge spectrum reconstruction,종별event와work를 exact commit/path/blob에 묶은 계약 및 작은 reference adapter. stage별 ensemble rate는 이미 perH이므로 다시 나누지 않는다. raw proper event는 R_j/nH_j로 매 stage 정규화한다. 새 PhotonInput의 comoving count는 a³*n per referencecm³이며 옛 cMpc^-3와 혼합하지 않는다.

q=aE,F=nE/(a*nH),source=sE/(a*nH),birth q=a(tb)*Eb. 두 half-step 사건은 각 stage normalization 이후합산한다. fixed threshold survivor Z를 absorption과 섞지 않는다. subthreshold를 유지하면 전체energy에 chi*Z를 다시 더하지 않으며 export를 택하면그때만 crossing energy chi*dZ를 기록한다.

R_n=n1-(nH1/nH0)n0-hS1=nH1R_q. Exact nuclear dilution+BE ion dilution의 혼합은 피한다. geometry pullback만으로 discrete energy conservation은 보장되지 않으므로 same-stage event/work 및 product rule을 검증한다. source-counting은 k/H뿐 아니라 tau_until_threshold,경쟁 species,finite-time storage를 검사한다.

이번 pureH reference는 constantalpha/E^-3 testcrosssection/CaseA의 별도 synthetic 모형이다. actual physical-rate model로 승격하지 않는다. QV는 homogeneous x와 다르며 FLRW02 적분형 defect의 각항을 실제 stage 누적값으로 조립해야 한다. expected RHS나 C/Qdot 강제주입으로 실제 consumer 검증을 대체하지 않는다.

외부84tests와 photon-only native history는 수신증거이지 본 runtime 실행이나 coupledhistory가 아니다. rustc가 없으면 compiler blocker를 유지하되 독립이론을 막지 않는다. 생산 surrogate, full cargo/Grackle/과거suite,대규모history/원자재감사 및 externalF04중복은 하지 않는다. 동일단위 source/contract가 실제 준비된 뒤에만 새 bounded native execution을 판단한다.

보고서/코드/상세결과는 REI_CHAT_FLRW03_20261005.zip의 rei_chat_flrw03_20261005/ 아래에 있다. 기존 strictlocal<2e-4/publicwidth<2e-3,[160,161]FAIL과tick160,physicalHOLD보존. 같은branch append-only non-force와 기존Drive/Dropboxcreate-only백업. R1metadata/localhash/remote restore/science claim별도.
