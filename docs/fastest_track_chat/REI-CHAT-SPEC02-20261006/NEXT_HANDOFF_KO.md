# SPEC02 -> SPEC03 thermal feedback tube application

같은 cosmosapjw-quantum/rei_bianchi, forward/rust-reion-kernels-20260922, PR83. Source parent87b5aebd442a0e06fe9f9036886a41a8b37e8d98. 시작/경계/게시전후 liveHEAD와관련delta만읽고SPEC01과거suite/F08campaign은반복하지않는다.

완료범위는prescribedHI nHI=n0 exp(-beta Ht)의finite-time probability/heat 상계다. beta3/103,Ht_end=.01,m8,64/128slab+Poisson-tail.128slab에서는두profile모두흡수음/heat양의bias가0을제외한다. 실제F08gas이력은아니다. Singleabsorber/downwardenergy/nonnegativeincreasingreward의단조성없이species경쟁reward에복사하지않는다.

Finitehorizon과threshold의frontier E*=Ec exp(H(T-t))에서u_E가점프할수있다. GlobalC2를가정하지말고frontier분할또는exactdivideddifference를사용한다. Discretecutoffactive와continuum즉시탈출의차이는 +integral p0*k0*q(Ec)dt로보존한다. FitEc/bindingchi별개.

다음최소연구 SPEC03_THERMAL_FEEDBACK_TUBE_APPLICATION: 실제선택한FT03 gas trajectory/tube에서fullgas+characteristicsurvival비교행렬M과gascolumnsC를구간으로제한하고,짧은공통시간창전체의cumulative spectral gasforcingDg(t)를감싼다. e'=Ae-D',v=e+D,e(T)=Phi*e0-D(T)-integralPhi*A*D를사용한다. D(T)만작거나0이어도gaserror는0이아니다. 초기연속오차/불일치jump/동일sourcebirth를유지한다. Heat사후보정이나Case/원자표교체없음.

PureH등온L1nonexpansion은exactcolumncancellation에의한제한정리다. HHe/thermal/CI/secondary에는자동확장하지않는다. 이번smallcoupled의alpha2e-13은합성상수이며heat는T에feedback하지않았다.

T0_BI첫transaction요청은별도pending. 도착시기존13Dangularblock에연결하며새추출요청/campaign중복은없다. Source-independenttheory를actualBIcertificate로이전하지않는다.

ZIP내읽기: THEORY_AND_FEEDBACK_CONTRACT.json,REPORT_KO.md §§2~6,results/verified/NONAUTONOMOUS_INTERVALS.json,THEORY_CHECKS.json,INDEPENDENT_REFERENCE.json. 기본재현 python research/run_checks.py --output NEW_DIRECTORY. 새interval증거와동일turn저장reference를비교하고IVP는재적분하지않는다. 별도check_reference/check_dual_identity실행시새14개IVPsegments가추가된다.

OriginalCODEX_SYNC/runtime_returns/F00/F03/FT03/S0/원자표/source보존. local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD유지. Samebranchappend-onlynonforce와기존Drive/Dropboxcreate-onlybackup. R1metadata/localhash/remote_restore/scientificvalidation구분.
