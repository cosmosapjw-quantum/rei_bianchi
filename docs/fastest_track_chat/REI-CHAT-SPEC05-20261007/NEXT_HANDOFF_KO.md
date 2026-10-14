# SPEC05 후속: signed bulk/boundary reward envelope

같은 cosmosapjw-quantum/rei_bianchi, forward/rust-reion-kernels-20260922, PR83을 유지한다. 시작·경계·게시전후 live HEAD와 delta를 읽고 새 외부 IGM foundation/thermal 모듈을 FT03/S0와 혼합하지 않는다. 현재 source-read HEAD는 a0001ca14644fc9fd2fbe52f8cfcae3edbedd110이다.

SPEC05에서 같은0..1e12s FT03/S0와 SPEC04 tube/M/C를 계승하여 killed-survival weighted early/late boundary와 Duhamel future attenuation을 계산했다. xHII<.017088875, T<437.810K의 조건부 absolute bound다. 이전679.830K보다작지만accuracyPASS나signederror인증은아니다.

m=.660774707935661은Tstar정규화 activehazard 하계다. exp(-m*min(age,TX))로과거survival을감싸고continuousfuture exp[-m(min(a,ac)-u)+]를흡수확률에사용한다. Early killed-exit Wm, late killed-active Am를별도로계산한다. Passive해가발생하면모든광자에exp(-m*age)를붙이면안된다. WholeTV의M44=0은유지된다.

Gasforcing 전체prefix와continuousbirth convolution을보존했다. Heat첫항에는pastsurvival만사용하고, survival차이가곱해지는continuousheat는cutoff후0이므로memory적분을min(age,ac)에서끊는다. Count용future damping을heat첫항에무단적용하지않는다. Initialerror는원t0에서만0이며후속시간구간에서reset금지.

다음 최소연구는같은tube에서signed bulk/threshold defect를따로감싸고signed cumulativeDg(t)를gasfeedback에전파하는것이다. Runningmaximum, global hazardminimum, Cauchy상계의느슨함을분해한다. 원자표/source/cutoffflag수정이나사후thermal보정금지. C2가깨지는terminal/exitfrontier를분리한다. 반복일반정리나새BI추출요청/전체campaign으로되돌아가지않는다.

ActualBIfirsttransaction은여전히별도open이며source확인없이없음/있음을추정하지않는다. 이전native1.25e9s시간certificate를1e12s로확대하지않는다. Fullphysical/omittedcooling/intervalglobal/BIgate는HOLD다.

재현 python research/run_checks.py --output NEW_DIRECTORY. 신규interval2killedchains128slab와3-command검증만수행; parentproof/native/IVP/cargo/history재실행0. Parent288payloadhash계승. Initialhelper3testsred-green,추가4tests와나머지수학검사는tests-after. 자동spreadsheetwarmup경고는환경문제로원로그보존, -S하위과정으로차단했고scientificsettings는불변이다.

같은branch 새scoped폴더만append-onlynon-force, Drive/Dropbox create-onlybackup. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존. R1 metadata/localbyte/remote restore/sciencevalidation분리.
