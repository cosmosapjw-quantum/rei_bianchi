# RCT03E6: 전체 저장시각의 endpoint rate 예산

ALL_EPOCH_ENDPOINT_FINITE_RATE_BUDGET_PASS__OWNER_AND_TRUE_ERROR_OPEN.

요청한 E4 게시/백업은 이미 ddb02a9926d644fbf347dce816c2777d422a23f8에 있었고 E5도 91218a1d496fad1b7231f96488a8df56e4fd532a에서 완료됐다. 이번 retry는 새 Drive 사본 1xSd3sRGdXnFnLoBuHHbOXNgkANowAmSZ의 성공과, Dropbox ALREADY_EXISTS 뒤 기존 id:BSpOijBcT10AAAAAAD3Wpw의 일치 확인이다. 기존 사본/기록은 삭제하거나 덮어쓰지 않았다. 실제 retry 기록은 47fc37087a99f36dab4f0bfa65be8285fdd32ca1이며 이전 unknown exit는 그대로다. E4/E5 과학실험을 반복하지 않고 E6를 수행했다.

## 새 유한 계산

동일 z12 FLRW 제조모형, T0=2000K, 초기(.1,.05,.9), 초기광자0, 13.7..100eV source1e-15 photons/H/s, Delta ln a=2e-4, OFF/KF/GM과 명시적 ON mean35eV를 유지했다. 원 가스/원자/수송 코드는 변경하지 않았다. 기록된 gas H에서 원 positive characteristic 재귀 f_j=C_j(eta,Uj-1,Uj)[f_j-1]를 실행하며, source/EOS/fit/Q/허용오차를 바꾸거나 스펙트럼을 임의 보간하지 않았다.

선택 observer는 기존 source/cutoff N24-anchor grid에 현재 시각의 최대5개 경계를 추가한다. P512는 원 E4 helper, P256은 같은 기존 양의 규칙/anchor를 재사용한다. Gauss2/4, active-grid cap4096이며 실제최대2456이다. E5 exact-eta-bit cache는 불변이다. 모든 새질의의 key합집합을 계산 전 점검하고32768 cap을 집행했으며 최대20940keys다. active cap과 cache cap을 혼동하지 않으며 peakRSS/속도개선비는 측정하지 않았다.

각 mode에서 N384/P512/H4의 Q4/Q2, N384/P512/H2의Q2, N384/P256/H4의Q4, N192/P512/H4의Q4를 계산했다. 15표5199행, 한 생산캠페인3process 모두exit0. 새coupledstep/가스이력0, native characteristic 호출30113280회다. N384의385개시각에서분광비교하고, 시간비교는 N192의193개exact-common시각에한한다.

기존 첨부계열의 rate allowance1e-22/s+1e-6 relative로 time/panel/diagonal-order 최대비의합을판정했다. 서로다른remoteE3의2.5e-23/s 기준으로바꾸지않는다.

|mode|HI sum|HeI sum|HeII sum|
|---|---:|---:|---:|
|OFF|0.9625720460|0.1015416851|0.0069493843|
|KF|0.9626911986|0.1015544436|0.0068969088|
|GM|0.9645971372|0.1017585813|0.0060572529|

아홉finite목표모두PASS다. 최악GM-HI는time.4869484737300262(finalstep384)+panel7.852460741758294e-9(step167)+order.47764865565610315(step16)이다. 같은시각의동시최악이아니며여유가넓지않다. sameH4-order최대.4776511429031944는추가진단이고diagonal기준을대체하지않는다. 정확한연속해/원자fit/노드사이오차인증이나새Gamma의coupledfeedback채택이아니다. 원legacy9rateFAIL은그관측정의의실패로보존한다.

## 검증과 전달

새native8시험(최초runtimeRED5/control3), Python8시험(최초stuberror8)통과.45개fullnodewitness78816행의225exact-rational reduction에서최대상대차3.16701371481059e-15. E5의216Gamma가bit동일하며uncached원재귀135node도bit동일(추가16317C_j호출). 이는같은source의유한산술/표현검사이지독립원자평가또는과학심사가아니다. parent371payload와선택12이력은불변이다. Rust1.94.1 archive pin은확인했고GPG인증은NOT_VERIFIED다.

Git에는이projection/RETURN/INPUT_PIN/수치계약/실행sourceidentity/NEXT와정확metrics코어를둔다. 전체실행source,원E5dependency,선택이력,5199행,fullnodewitness,RED/GREEN/실행로그는DELIVERY_RECEIPT가가리키는immutableZIP에있다. Gitprojection만으로전체crate를checkout한것은아니다.

다음은 RCT03E7_OWNER_READOUT_ADOPTION_AND_CONDITIONAL_ERROR_CONTRACT. 이finite실험을필수검증으로다시반복하지않고opt-in읽기경로와sourceidentity/출력계약을owner에게전달한다. 기본RCTOFF,실제원자momentsnull,physicalHOLD,HE-F2/F09globalOPEN과receiver예약은유지한다.
