# SPEC03: 짧은 FT03 thermal H/He spectral-feedback 구간 상계

판정: SHORT_WINDOW_THERMAL_HHE_SPECTRAL_FEEDBACK_CONDITIONALLY_ENCLOSED.
0..1.25e9 properseconds, 같은 실제binary64node/초기S0/FT03HGCaseA에서 grid exacttime계와 continuumenergy exacttime계의 gas오차를 제한했다. PhysicalHOLD, 기존S0/F00/F03/FT03/source는 변경하지 않는다.

이번 상계: xHII<4.149128e-12, xHeII<1.863844e-17, xHeIII<5.004757e-19, w/w0<1.442549e-11, T<8.625482e-7K. 실제 CI/RR/2DR와 온도·전자수 되먹임을 포함하며 pureH등온정리로대체하지 않았다. 같은birth label의 survival totalvariation과 gas4를5block으로감싼것이며 물리radiation을scalarclosure로축약한것은아니다.

기존native firstmacro timecertificate와삼각합: endpoint xHII<2.473080e-7,T<.006163378K. 부모증명은hash계승,재실행0. Spectralbound는이짧은창전체, native합성은firstmacroendpoint만이다. Global/BI/physicalfit/tailenergy아님.

누적forcing는mean-zeroenergyfluctuation+variance를써서O(dE) polynomialbound로얻었다. Cutoff아래C2양의Taylor함수는증명보조이며실제provider를연장하지않는다. Hit8확률<3.078e-20항으로원cutoff차이를복구한다. Source는실제연속birthconvolution이며endpointpulse가아니다. D끝값만버리는경로없음.

독립55자리RK4 32/64/128및age-momentK4/K6 수치참조7회(max22변수): continuous-grid xHII=-3.20262257e-12, T=+1.64535497e-7K. 이참조는certificate입력아니며momenttruncation의독립intervalproof는없다. 초기gridabsorption증가/heat감소의leadingtau²부호는실제topcell나뉜차분으로확인,장시간SPEC01frozenbath의반대부호와regime가다름.

최종4명령exit0; unit8,symbolic6,Fractioncovariance80,intervalenergy64,derivative9,matrix5. Native/cargo/oldcampaign/부모증명재실행0. 초기newmatrixshift에서Decimalunarynegation이28자리context로round하여guard가실패; copy_negate수정과실패로그보존. Tests-after,formalindependentproof없음.

실행: python research/run_checks.py --output NEW_DIRECTORY. 기본은새interval증거와저장reference검사,check_reference.py직접실행만새7개IVP. 전체보고서REPORT_KO.md 및모든코드/로그/입력은sealedZIP에있다.

다음: SPEC04_THRESHOLD_REACHING_THERMAL_WINDOW. 이초기rare-tailbound를cutoff도달이흔한장시간에그대로외삽하지않는다. 실제BIraw미수신은별도open,같은추출요청/campaign중복없음. local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL보존.

## 재현 패키지

REI_CHAT_SPEC03_20261006.zip: 414142 bytes, 236 entries.
SHA-256: 3543ccce82b196e3b0ab03319228adf0b891c2ec07dfe99f68fa6c68e1666426
Drive: https://drive.google.com/file/d/1ZpCHX582GlgdwlPL7BFIIWSGJISZBodQ/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_SPEC03_20261006.zip
전체 보고서·코드·증거는 ZIP의 rei_chat_spec03_20261006/ 아래에 있다. 이 저장소 폴더에는 요약·계약·반환·인계·백업 8개 파일만 추가했다.
