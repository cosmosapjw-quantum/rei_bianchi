# FLRW07: 실제 기하-반응 분할 연결과 시간격자 반례

판정: SCOPED_NATIVE_COMPOSITION_VERIFIED__TIME_ACCURACY_AND_PHYSICAL_HOLD.

원 CharacteristicRay::pullback과 primary_stage_step을 실제 Rust1.94.1로 연결했다. Scientific source13개는 변경하지 않았다. 각 run은2또는4macro이며 threshold/source 장벽으로 나눈 최종6run/50source segment를 독립4D endpoint root와 대조했다. 기존 FLRW06의167개 회귀, full crate, F04/F05 전체 checker, S0 campaign은 실행하지 않았다.

## 핵심 결과

문턱 partition을 생략하면 새 pulse의 흡수가0인데도 장부가 닫혔다. Event-resolved F4의 초기13.7eV흡수는5.3686240464955945e-5/H, 새13.65eV pulse흡수는1.9204723264695193e-5/H다. No-event 대조군은 각각7.280655881575747e-5/H와0이다. 초기과흡수와pulse누락이 합계에서 거의상쇄되므로 total count만으로 검증할 수 없다. 이는 새 diagnostic caller의 negative control이며 원 native source의 버그 판정이 아니다.

B-F 최종온도차: 독립 continuous +0.6364318614723743K, 각 geometry의 별도eventgrid -0.3267900653008837K, 두geometry eventtime의공통합집합 +0.6335372789180838K. 공통grid의contrast차이는-0.002894582554290537K(약0.4548%)로 줄었지만 개별온도편향 약26.8K가 남는다. 이를 물리신호나 production 시간오차 통과로 승인하지 않는다.

Continuous T_F=46140.78206449299K,T_B=46141.41849635446K. Common-grid native는46167.605437427206K,46168.238974706124K다. 원자율의 물리오차, 지배적인 생략냉각, 연속각도/스펙트럼, Einstein해, 독립QV는이번범위밖이다.

## 모델과 연결

nH0=1e-4cm^-3,fHe=.083,fractions=(.9,.3,.6),T0=50000K. F의H_i=(1,1,1)e-12/s,B의H_i=(.7,1,1.3)e-12/s,같은부피팽창. t_end=4e10s,pulse=2e10s. 초기4개의antipodal쌍(E/count)=(13.7/.004,20/.05,35/.005,70/.001),pulse13.65eV/.003/H의antipodal쌍. Explicit finite beams이며 isotropic continuum/S0가 아니다. FT03 HG rate-moment CaseA의기존guard30000..110000K와비영H/He를유지한다.

각smoothsegment에서 G(t0,mid)->nH(mid),E(mid)의BE source->G(mid,t1)다. Gas -2Hw는source에서한번만, photon work는각halfgeometry의에너지차로계산한다. p는perH이므로-3Hp를추가하지않고density를다시나누지않는다. 모든birth는실제방출시각에한번붙인다. Fitcutoff와physicalHIchi의event를구분하며subthresholdpacket을보관하므로energyexport를중복하지않는다.

Geometry-half/BE-source/geometry-half는일반적으로1차다. 순수thermal부분은 w_BE/w_exact=exp(2HT)/prod(1+2Hh_j), logbias=2H²sum(h_j²)+O(H³sum(h_j³)). 따라서다른eventgrid는같은평균H에서도차분오차를만든다. Common-grid는이순수thermal편향을정확히상쇄하지만일반coupled오차를보증하지않는다.

## 검증과 실패 보존

최종5명령exit0,새unit2,symbolic4,독립root50/485함수평가/2300scalar비교. Max state 또는lnT차이5.551115123125783e-16,eventrelative5.519004640936958e-13,geometry차이7.771561172376096e-16. Independent BE residual5.212301944224063e-16,globalnumber1.2006557260996359e-15/H,globalenergy2.0707631301960377e-14eV/H.

Continuous reference는28변수,두geometry의DOP853/Radau4개이력,총24개event-split solve다. 동일원자입력을공유한독립방정식/적분기검증이며원자물리독립검증이아니다. 마지막확인에서는그reference를hash검증하여재사용했다. 최종6diagnostic은초기4개와공통grid2개이며새2300개물리초기조건을뜻하지않는다.

새whole-world transaction의첫시험은source실패후pulse/ray/ledger가남아exit101이었다. Clone후모든단계성공시에만commit하도록수리해동일시험exit0. 원실패/원코드/log를보존했고과학source나허용오차는변경하지않았다. Zero-duration도검사했다. 별도reviewer dispatch는없다.

## 전체 재현 패키지

REI_CHAT_FLRW07_20261005.zip:1408512bytes,72entries,71payloadhashes및CRC검증.
SHA256=24a4927211ddb6a5130e2f9e2ef5b50c21f15a082739fec6ad1484b3d34862b9.
Drive:https://drive.google.com/file/d/1-tzETqoiEHZwIhWyhFp18doyYdQbjfZ0/view?usp=drivesdk
Dropbox:/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW07_20261005.zip

ZIP의rei_chat_flrw07_20261005/아래fullREPORT,13원source,실제binary/stdout,독립검사기,모델/사전등록/공통gridaddendum,실패로그가있다. 여기repo에는8개요약/계약/결과/인계/영수증만추가한다. 기존rustc를사용해 python research/run_replay.py --out 새폴더 --fresh-continuous 로재현한다. Toolchainarchive는재배포하지않으며공식서명진본성은trustedkey미확인상태다.

다음chat은REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL. 외부REI-F08와독립된제한된time-error작업이다. 기존strictlocal<2e-4/publicwidth<2e-3,[160,161]FAIL=2.1245050576368385e-4,tick160,physicalHOLD와canonical반환을보존한다. Outgoing backup은R1metadata이며remote restore는미수행이다.
