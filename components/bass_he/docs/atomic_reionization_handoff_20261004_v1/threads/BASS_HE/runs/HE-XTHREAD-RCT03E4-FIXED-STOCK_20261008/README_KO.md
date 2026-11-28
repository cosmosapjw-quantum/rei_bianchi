# RCT03E4: 고정 spectral parent의 cutoff-aware rate 읽기

FIXED_PARENT_CUTOFF_READOUT_DECOMPOSED__FULL_RATE_GATE_OPEN.

첨부 E3 SHA25f181e8...의 실제 가스 이력과 원 characteristic_path_selected를 재사용했다. 초기 photon0에서 같은 저장 affine gas path의 각 구간을 적용해 임의 eta의 양의 parent를 정의한다. Spectral samples의 임의 보간이나 정확한 연속해가 아니다. 원 grid에서 replay한22snapshot의66Gamma가 원 저장값과 bit-identical이며 실제 coupled2step의 전체density도 대조했다. 새 fullcoupled이력/물리모형은 없다.

H2/H4를 두 저장 가스경로, Q2/Q4를 두 원구적규칙이라 하면 G44-G22=(G44-G42)+(G42-G22)다. 앞은 같은H4의읽기변화,뒤는같은Q2의경로변화다. 원node/weight/density/energy/native sigma를 저장해 정확한 dyadic product sum과 cell분해를 계산했다. OFF 주실패의 경로항/총차 절댓값은 HI step5:2.365e-6,HeI step4:1.971e-7,HeII step52:2.512e-8이다. 차이는 거의 같은parent의 구적항이다.

원Grid는25개N24시각에 source/cutoff를 anchor하지만 gas는N384다. Step4/5/52의 현재 경계가 원셀 안에 있다. OFF 주셀은 HI13.699964..13.700078eV(source13.7),HeI24.589949..24.590154eV,HeII54.419887..54.420340eV다. 해당셀들과source상단의합이구적차이를거의전부설명했다.

진단reader에만 현재source min/max와fitcutoff를 추가했다. OFF 원 HI/HeI/HeII worst-point O2/O4 allowance ratio2.738981/5.978264/8.346595는 같은H4 parent의 경계분할 뒤 .028529618/1.71477e-6/1.67983e-6이다. KF/GM도 확인했다. OFF anchor16/48까지 포함한33field의 새O2/O4 최대비 .4776511431,영향셀국소이분4 최대비6.967122e-6이다. 허용량은 첨부E3의1e-22/s+relative1e-6 그대로다. 원격 E3의2.5e-23/s와다른계약임을보존한다.

33개유한표본의읽기비교가한계안이지만 전체385시각 rate9FAIL을PASS로바꾸지않는다. 반례 f=1,kernelTheta(eta-2/5),[0,1]에서미분할Gauss2/4는둘다1/2이나실제적분3/5다. 두규칙일치만으로참오차를닫을수없다.

수행: 새native8시험/Python8시험,77snapshot148268node,3327916characteristic macro호출. Native같은입력정확합231개 최대상대차4.37215e-15,다른Decimal90합231개와최대8.62e-89. 이는산술오차와원자fit오차를분리한것이며독립과학심사는없다. 기호4식/합성반례1개,33교차분해/33cell합/33stock삼각부등식을확인했다.73원source와6CSV불변,최대node2488<4096,Gauss8/cap증가/원source변경없음.

합성반례checker에서구간Jacobian1/2누락을assertion으로발견해해당식만고쳤다. 원nativegrid는올바른halfwidth를사용하며science재실행없다. 최초미완료verification메타데이터와실패로그도보존하고최종gate는exit/content확인후닫았다. Analysis-only 전체reproducer는실행됐고수치JSON이byte동일하다. Native전체wrapper추가재생없음.

전체Rust/Python/input/snapshot/실패및성공증거는 BASS_HE_RCT03E4_FIXED_STOCK_20261008_v1.zip(10353822bytes,SHA256ff7bb06718e98d2c060faccc7a87253c2deb3648a9141c9c99a15d3bbcd918b2)에 있다. Git은보고/반환/계약/분석코어의projection이며fullcratecheckout이라고하지않는다. Native3개신규파일delta는정확E3기준사본에서apply/hash를확인했다.

다음은 RCT03E5_CUTOFF_AWARE_PARENT_READOUT_FULL_EPOCH_SCOPE다. 같은parent/reader의전체시각검사를먼저하며추가N768/새원자율을선행조건으로만들지않는다. 원receiver/root/default미수정,baselineRCTOFF,atomicmomentsnull,physicalHOLD,HE-F2/F09globalOPEN과owner채택OPEN을유지한다. 실제게시/백업상태는별도DELIVERY_RECEIPT가소유한다.
