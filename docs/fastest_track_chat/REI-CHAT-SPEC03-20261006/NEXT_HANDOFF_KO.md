# SPEC03 -> SPEC04 threshold-reaching thermal window

같은 cosmosapjw-quantum/rei_bianchi, forward/rust-reion-kernels-20260922, PR83. 시작/단계경계/게시전후 liveHEAD와 관련delta만 읽는다. 원 production source/CODEX_SYNC/runtime_returns/F00/F03/FT03/S0 변경금지.

SPEC03은 실제 FT03 thermalHHe CI/RR/2DR+13.7eV 초기 .05/H 및 continuous source5e-15/H/s, FLRW H1e-14에서 0..1.25e9s의 grid-exact-time vs continuum-energy-exact-time gas error를 조건부 interval로 제한했다. ygas4+birth survival TV의5block comparison을 사용했다. w는 w0로 정규화. 실제 timecontinuous fixed-grid와continuum모두 같은 원 IC, 초기error0은 원 시작점이라 정당하며 이후slab에서는이전error전파필수.

결과 xH<4.149128e-12,T<8.625482e-7K. 기존firstmacrotimecertificate와 합쳐 native대continuumenergy endpoint xH<2.473080e-7,T<.006163378K. 이전timecertificate는hash계승이지 재실행아님. 해당initialwindow와신뢰base외에global/BI/physicalfit/tailenergy 승격금지.

새방법은 mean-zero Markov energy fluctuation의variance로 cumulative count/heat forcing의O(dE) polynomial bound를 만든다. Cutoff아래 C2positiveTaylor continuation은 증명용보조함수이며 실제provider변경아님. Hit8 Poisson remainder로 원cutoff와의차이를추가한다. Dgas끝값만사용하지않고전체polynomial envelope를M,C로전파한다. sourcebirthconvolution을포함한다.

독립55자리RK4/agemoment7개IVP는검산용. spectral energy continuum age TaylorK4/K6 차이확인은별도trajectorycertificate아님. 이를productionroot나정답source로주입금지. 초기spectralbias는gridphoto증가/heat감소이며longfrozenbath와다른regime다. leadingtau²의부호만증명, fullwindow signed error는미인증.

다음최소이론SPEC04_THRESHOLD_REACHING_THERMAL_WINDOW: cutoffhit가흔한창에서는원Poissonrarebound를무단외삽하지않고 stopping/split-boundary reward와terminalfrontier를명시하여열적forcingbudget확장. 실제gas trajectory/tube의권위가있을때그짧은창에적용. 전체campaign재시작/BIraw요청재생산은하지않는다. BIactualfirsttransaction은별도open.

재현 python research/run_checks.py --output NEW_DIRECTORY. 이명령은새interval증거4단계를실행하고저장reference를검사한다. check_reference.py직접실행만새7개IVP를추가. 부모suite/증명은반복하지않는다. 초기Decimalshiftunaryminus오류와로그보존,수정은copy_negate이며물리코드변경아님. tests-after,formalindependentproof없음.

samebranchappend-onlynonforce와기존Drive/Dropboxcreate-onlybackup. local<2e-4,width<2e-3,[160,161]FAIL,tick160,physicalHOLD와auxiliaryescapeFAIL보존. R1metadata/byteidentity/restore/과학검증별도.
