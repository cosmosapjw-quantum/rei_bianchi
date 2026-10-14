# SPEC01 이후: nonautonomous reward와 gas-feedback 오차

같은 repo cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, PR83. 시작·연구 경계·게시 전후 live HEAD와 관련 delta만 읽는다. Originalsource/CODEX_SYNC/runtime_returns/fixture/thresholdflag/원자표는 수정하지 않는다.

이번의 frozen-bath 흡수·heat 편향은 새로운 diagnostic이다. Constant H=1e-14/s와 외부에서 유지하는 nHI=1e-5/cm3, exactdecimal source-shaped grid, factual Verner fit이라는 입력을 실제 coupled F08에 소급 대입하지 않는다. m8 absorption -3.7646%/heat +4.2429%는 그 진단의 결과다. Absorption의 signed interval과 heat의 고정밀 수치검증을 구분한다.

다음 ready theory는 SPEC02_NONAUTONOMOUS_REWARD_AND_FEEDBACK_BOUND다. Backward value u의 (partial_t-Hparallel E partial_E-k)u=-k_s q_s와 rewarderror=integral p_delta(L_delta-L)u를 선택한 gas tube에 연결한다. u_EE,thresholdboundary,sourceprojection,gasfeedback 안정성항을 따로 제한한다. Frozen product를 변하는 n_s(t)에 그대로 적용하지 않는다. 광자수 보존이나 시간세분화만으로 spectralaccuracy를 판정하지 않는다.

ActualBI 첫transaction 입력요청은 별도 열린 FLRW08 노드다. 도착하면 기존13Dblockcomparison을 actualdirectional residual/tube에 적용한다. 같은 추출요청을 재생산하거나 원8천단계이력을 재실행하지 않는다. FLRWmacrocertificate와auxiliaryescapeFAIL은 보존한다.

재현 python research/run_checks.py --output NEW_DIRECTORY. 새7tests,exactchains60,symbolic6,log8,weakmoment12,Erlang5,frozenHI10,intervalpanels512. Native/IVP/MC0,tests-after. 실제correctlyrounded primitive 의미와비형식검증trustbase를유지한다.

기존local<2e-4,width<2e-3,[160,161]FAIL/tick160/physicalHOLD 불변. 같은branch append-onlynonforce와기존Drive/Dropboxcreate-onlybackup. R1metadata/byterestore/physicsvalidation을구별한다.
