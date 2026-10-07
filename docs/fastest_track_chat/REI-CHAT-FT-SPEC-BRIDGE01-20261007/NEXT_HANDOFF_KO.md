# FT-SPEC-BRIDGE01 -> 기존 F08 시계의 cohort 후보 연결

같은 rei_bianchi, forward/rust-reion-kernels-20260922, PR83. Source pin dbb54009a517242ff5a41c805512471a74dd25f4와13개blob. 시작/경계/게시전후liveHEAD 및관련delta만읽는다.

이번에는SPEC05 bound개선과실제fastest-track을다시연결했다. 정확sourcebytes의 CharacteristicRay::pullback, primary_stage_step_conservative를새opt-in caller에서사용해grid8와no-reprojection birth-cohort를같은clock/source quadrature로비교했다. F08 paired_runtime전체실행이나production기본값변경은없다.

FT03/S0 초기값,0..1e12s,H1e-14,soft13.7eV,initial.05/H,source5e-15/H/s. 방출은midpoint-cohort quadrature이고연속방출오차0아님. 반응BE때문에대칭배치도일반적으로1차. N256 cohortT47918.42442809899K,grid8T47943.15324638324K,계승한연속수치참조47917.629222632495K. 같은clock차24.72881828425K,계승한exacttime차24.83533929670K. Cohort는재투영확산을만들지않지만time/source/fit오차가남는다.

최종7이력2920stage,21독립4gasroots,5258scalar비교,9unit통과. ZIP내부명령은 python reproduce.py --output NEW --rustc /path/to/rustc. 이repo의 RUN_FROM_ARCHIVE.py는정확ZIP을검증하고고립된실행폴더를만든다. Network/Cargo없음. 기존lowTIGM와FT03/S0모형을혼합하지않는다.

다음bounded작업 FT_SPEC_BRIDGE02_EXISTING_F08_SCHEDULE_ADMISSION: 실제F08 caller의기존시간/sourceownership에후보를명시적으로연결하고fixed-grid/cohort의time/sourceerror를별도검사한다. 옛1.25e9 nativecertificate나SPEC05 exact-timebound를이newnative1e12s에재사용하지않는다. 기존clock이source/threshold정확도를충족하지않으면그실패를보존한다. Productiondefault로자동전환하지않는다.

Bianchi에는실제angularweights/birthq/ray와원transaction이필요하다. FLRW대표방향을재사용하지않는다. Photoncohort압축은새kernel별오차조건없이하지않는다. 이전signedbulk/boundary증명은별도open,동일raw요청/대규모campaign반복없음.

Knownfailures: projectionstub와passiveguard누락 BRIDGE_PROJECTION_DOMAIN. 수정대상은새caller뿐. 첨부compiler실행은검증했고archive서명진본성은이번미검증. OutgoingR1metadata와restore/science는별개. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존.
