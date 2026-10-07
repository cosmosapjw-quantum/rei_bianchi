# BRIDGE05 BOXJOIN -> energy-parameter lift의 첫 source 구간

같은 rei_bianchi / forward/rust-reion-kernels-20260922 / PR83. 시작·게시 전후 liveHEAD와 관련 delta만 읽는다. 원 S0/FT03/source/CODEX_SYNC/runtime 반환은 유지한다. 이번에 root 호출부를 실제 실행했으므로 parent-box join 자체를 전부 부재로 반복하지 않는다.

완료: 첨부 BRIDGE04 800-output계획의 첫macro0..1.25e9s,9subflow,birth6,packet1->7. 실제 primary_stage_root가incoming gas/count intervals를받으며 이전rootbox와conservativepoint의hull을다음parent로넘긴다. Native point는부모firstoutputgas와byte같다. Wholemacro후에만외부상태commit하며새birthnegativepacket/parentmismatch의거절은전체rollback됐다.

Claim ceiling: stage E/sigma/nh/H/dt와birthtimes는fixedf64다. Countweightbox는fixedf64 cell경계의S*(r-l)/2를감싼다. Sourcequadrature/time/physical/원paired_trialfullgate가아니다. Non-degenerateenergybox는ENERGY_PARAMETER_BOX_UNSUPPORTED로거절한다.

다음한작업 FT_SPEC_BRIDGE06_PARAMETRIC_ENERGY_LIFT_FIRST_SUBFLOW: 동일firstsource구간의E-parameter를sigma와흡수energy/heat에일관되게포함할새parameter평가계약을마련하고작은family에서실행한다. 먼저cutoff에서분리된smoothbranch를선택한다. 특이cutoff구간은parameterbranchpartition을검사하되하나의불확실한packet을두물리광자로복제하지않는다. 원고정에너지kernel을조용히고치거나기존certificate를대체하지않는다.

한ULPbelow13.6->13.6eV에서HII차5.93446648e-5,두rootbox비중첩을반례로보존한다. 고정gas의dJ/dE뿐아니라 dQ/dE=J+(E-chi)dJ/dE의explicit항도필요하다. 다음root의uniformTheta에는실제포함한parameter만명시한다. Birthtiming/frontier/order가불확실하면별도domain분할이필요하며이작업에서자동완료하지않는다.

재현 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. 새7개명령중6개는fresh실행,마지막exactreadoutchecker는별도실행으로모두exit0확인. 원13sourcebyte검사,8unit,13nativecalls,29독립4gasroots,4symbolic/64rational/37energy검사다. Archive끝무결성실패와State명충돌/energyguardredgreen로그보존. 실제작동한rustc/std사용과정상archive/공식서명은다르다.

IVP/fullcampaign/과거증명재실행없음. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD와BIraw/signedSPEC/생략물리의별도상태보존. Samebranchappend-onlynonforce와기존Drive/Dropboxcreate-only. R1metadata와원격restore/과학검증구분.
