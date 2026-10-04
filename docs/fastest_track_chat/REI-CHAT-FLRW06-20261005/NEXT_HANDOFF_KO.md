# FLRW06: 실제 native spectral-stage 회귀를 계속한다

같은 rei_bianchi/forward/rust-reion-kernels-20260922, draftPR83. 다음 chattask는 계속 REI-CHAT-FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION이다. Compiler 부재를 native 성공으로 바꾸거나 FLRW07로 자동 승격하지 않는다. 새로운 80자리 기준 및 moment-cone 하위연구는 끝났다.

먼저 live ref를 읽고 b553698a114fbff05640ab6ecb95d260410de492 이후 필요한 source diff만 수신한다. 외부 REI-F04는 pinned static numerical domain에 한해 completed, 외부 nextREI-F05다. 기존 역사적 pending 문구와 최신 상태를 구별하며 그 인증을 evolving spectrum에 이전하지 않는다.

README의 SHA로 REI_CHAT_FLRW06_20261005.zip을 확인하고 rei_chat_flrw06_20261005/에서:

    python research/run_native.py --repo /path/to/rei_bianchi --output /path/to/new_result_directory

기존 repo와 rustc가 필요하다. Network/cargo/과거suite/history 없이 source6개를git show로추출하고 Git blob을검사한다. Scientificmodule5개는byte동일,원lib의공통type정의와minimal wrapper/driver만사용한다. 단일rustc compile과단일probe process다. Driver자체는이번환경컴파일미검증이다. Output은새directory만허용한다.

입력11valid+6invalid,비교167scalar다. PhotonInput absorption은원nativephoto API bin0/1/2 actualreturn의events합으로만계산한다. Expectedsink/RHS/C/Qdot를주입하지않는다. Source/input/compiler/binary/stdout identity와compile/run성공,독립reference비교및정확errorcode가있어야NATIVE_EVENT_PHOTON_POINTWISE_REGRESSION_PASS다. Python protocol제조출력을그증거로쓰지않는다.

Native실행이통과해도fullcrateintegration,독립U소비자,accepted-stagecoupled/FLRWhistory,Qgeometry,원자physical/interval승인이아니다. 원rawphoto와FT03thermal route를무기록혼합하지않는다. 새로운stagespectralclosure전체도출을반복하지말고이좁은실행경계를닫는다.

Moment-domain은N>=0,U-LN>=0,RN-U>=0이다. 고정FE방향의exacthmax는음의방향face까지시간의최솟값이다. Error estimator/productiontimestep이아니다. Boundarydelta를클리핑하지않고finiteexponential의strictinterior를지킨다.

원CODEX_SYNC/runtime_returns/F00/F03/FT03는변경하지않는다. strictlocal<2e-4/publicwidth<2e-3,[160,161]FAIL=2.1245050576368385e-4,tick160/physicalHOLD보존. 기존Drive/Dropboxcreate-only와samebranchnon-forceappend를유지하고R1metadata와remote restore/science를분리한다.
