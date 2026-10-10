# SPEC04 -> SPEC05 absorption-weighted stopping bound

같은 cosmosapjw-quantum/rei_bianchi, forward/rust-reion-kernels-20260922, PR83. 시작/경계/게시 전후 live ref와 관련 delta만 읽는다. 기존 source/runtime_returns/CODEX_SYNC/fixture는 변경하지 않는다.

이번 완료는 같은S0/FT03HHe thermal 모형의0..1e12s에서 rare-hit가아닌 boundary occupation B(a)와 uniform prefix forcing, 새 physical gas tube, 5block feedback absolute bound다. HII<.026467314,T<679.830K는조건부이고보수적이며accuracyPASS가아니다. Actualreference는HIIcontinuous-grid+.001208993,T-24.8353393K,129sample최대|Tdiff|56.4167K. Signed bias는수치검산이지intervalsignedcertificate아니다.

B(a)=a-z(a) beforeTc; Tc+z(a)-2z(Tc) afterTc. z=E min(Texit,a). Grid cutoffnodeactive9단계, meanexit7.33707454245e11s,std2.58900637426e11s. ContinuumTc7.32604009207e11s. Free survival은흡수된population이아님. Kerneljump sigma_c,heatjump(Ec-chi)sigma_c를smooth Lipschitzpart와분리. 모든prefix D와continuousbirthconvolution을유지한다.

새튜브one-sided초기면은exactbinary64 .9/.3/.6로설정했다. 전체 photonTV에는passivecohort가있어서M44=0을사용; 모든광자에양의흡수lower를강제하지않는다. 기존초기native-timecertificate를이긴창에옮기거나오차reset하지않는다.

다음SPEC05는실제absorbed survival로가중한early/late boundaryoccupation과bulk signedcancellation을사용해상계의보수성을줄인다. 필요한tube는이번certificate를계승할수있지만증명과수치정밀도는별개다. Physicalfit/omittedcooling/BI/globalgate는그대로HOLD. RawBItransaction요청이나wholecampaign을재생산하지않는다.

독립reference는continuousageTaylorK6/K8+delayedboundary,initiallineexit명시,fullHHeCI/RR/2DR. Kagreement는reference의uniformcertificate가아니다. Sourcepulse화,thermalpostcorrection,thresholdflag변경없음.

재현 python research/run_checks.py --output NEW_DIRECTORY. Parent235filehash만확인하며oldproof/suite/native는실행하지않는다. check_thermal_reference.py직접실행은10개작은IVP추가. Boundarybranch/initialfloatidentity의2red-green실패기록보존. 나머지는tests-after.

samebranchappend-onlynonforce와Drive/Dropboxcreate-onlybackup. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL보존. R1metadata/localhash/remote restore/science claim구분.
