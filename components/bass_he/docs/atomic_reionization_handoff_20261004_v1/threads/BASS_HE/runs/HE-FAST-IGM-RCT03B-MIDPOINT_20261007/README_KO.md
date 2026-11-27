# HE-FAST-IGM-RCT03B: sourcefree midpoint 시간정확도

SOURCEFREE_MIDPOINT_N1600_ORIGINAL_GATES_PASS__PHOTON_ROUTING_AND_OWNER_ADOPTION_OPEN.
부모 RCT03A의 실제 staged receiver를 재사용했다. owner short-hhe-midpoint/coupled.rs의 material midpoint 식을 sourcefree에 한정해 기존 RCT결합 BE half-stage로 실현했다. 새 generic nonlinear solver는 없으며 원 BE prefix24795bytes와 기존 entrypoint/default는 불변이다. 원격 receiver/root/기본OFF는 변경하지 않았다.

## 새 수치 결과

기존 H3e-18/s,nH0=1e-4cm^-3,fHe.083,Tcmb0=20K,IC(.1,.05,.9),T0=2000K,0..1e15s,photon/source0 조건이다. OFF와 KF96/GM25 각각 mean30/35/Q의7경우, N100/400/1600과101epochs를 유지했다. 원 state1e-9+1e-8max,T1e-5+1e-8max,J1e-12+1e-7max 및 globalledger1e-10을 변경하지 않았다.

최종21이력/14700step은 모두 완료. N100는7FAIL,N400는5PASS와GM30/GM35 두FAIL,N1600는7PASS다. 전체12PASS/9FAIL이고 선택된N1600 범위만 수락한다. Finest 전체의최대허용량비는state .06612502512,T .001601971074,J .01285835711이다. GM30 N100/400/1600 T오차1.2320421092e-5/7.7002550825e-7/4.8134779718e-8K, J오차3.1541371056e-10/1.9713345539e-11/1.2320851804e-12events/H이며약2차수렴을관측했다. 기존BE21FAIL과midpoint photon prototype의overallPARTIAL은보존한다.

최종maxfullresidual1.0975325402e-16,energy1.4160984944e-15,species3.0986498090e-16이다. 기존고차reference재계산0,독립atomic검증/과학심사/구간인증은아니다. 새13native tests와기호11그룹15성분,3합성controls를검사했다.

## 중요한 산술 수정

처음 Y=y0+h/2 F(tmid,Y) 뒤 반사 y1=2Y-y0를 썼다. 유한stage residual rho가 full잔차2rho로 증폭되어 추가quarter/half stage budget에서 표현가능 고정점이 멈췄다. quarter버전21개는모두중도실패했고, half버전20개완료와KF30 N1600의213번째step 실패를보존했다. 국소trace에서는동일state에서residual2.9222261926e-16가iteration156..159동안불변이었다.

최종은원BEcontrol1e-15로Y를구한뒤표준RK출력 y1=y0+hF(Y)를사용한다. M=(y0+y1)/2=Y-rho를재구성하고 모든장부/최종잔차는F(tmid,M)에서재평가한다. 정확산술 rfull=h[F(Y)-F(Y-rho)]이므로반사형의2rho와다르다. 실제fullresidual1e-15와energy1e-10은그대로검사하며projection/clipping/실패완화는없다. stage_estimate와실제collocation stage를반환에서분리했다. 배경과proper밀도정규화도tmid를사용한다.

Midpoint는unconditional positivity나stiff accuracy를보장하지않는다. 실제neutralexpansion control에서양성BE stage라도최종음수/온도범위이탈이면명시적거절됨을확인했다. Publiccontrol검증순서bug와두plateau회귀실패는별도RED/GREEN으로보존했다.

총3개수정버전의history시작63회,acceptedstep28425이며서로다른독립과학성과가아니다. 원자/기존과학suite와23reference는재실행하지않았다. wrapper는구성명령수행및syntax확인,추가wholewrapper replay는없다. Rust1.94.1실행해시는기록했지만GPG인증은미완료다.

전체source/부모432payload/실패버전/원reference/21최종이력/patch/검산기는 DELIVERY_RECEIPT의ZIP에있다. Git은이요약과입력/반환/patchidentity를보존하며실행source전체가여기있다고하지않는다. Delta patch는RCT03A stagedreceiver에1변경2추가,combinedpatch는원39c39eab에2변경5추가이며둘다exact-base apply/hash검증했다. 다음은선택sourcefree고차경로의owner채택과별도photon/source same-stage 결합이다. HE-F2globalfalse,HE-F3/F09미완료,baselineOFF,source모멘트null,physicalHOLD를유지한다.
