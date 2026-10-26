# 다음 병렬 결합 연구 루프 — 2026-10-26

전체 DAG는 **29/88**이다. 이번 루프의 추가 canonical 완료는0개이며 기존59개 gate는 열린 상태로 유지한다. 이번에 구현·검증한 산출물은 정규화된6상태 beta caller와 움직이는 열화 경계의 보존적 교환이다. 새15개 검사는 한 번 실행해15/15통과했다. 이전25개 검사나83전구간,source atom census는 재실행하지 않았다. 독립 최종 판정은 review/VALIDATION.json, 최종 게시·백업은 후속 delivery/FINAL_DELIVERY_RECEIPT.json에서 확인한다.

## 전체 목표에서의 위치와 병렬 연결

기존 연구 branch HEAD95eb74e673553c3bf4c16f73077d2955dac455ee와88개 원래 gate를 기준으로 이어갔다. 최신 관련PR조회에서6개 공급자HEAD가 같았고, 조회한backup metadata의 변경도 없었다. 접근 가능한 범위와 각 실제HEAD는 intake/DELTA_HEADS.json 및 recovery/BACKUP_DELTA_SUMMARY.json에 있다. 보이지 않는 대화·로컬dirtytree까지 조사했다고 주장하지 않는다.

|병렬 작업|이번 실제 산출물|전체 gate에서 남은 연결|
|---|---|---|
|nuclear → REI/REC/VigilODE|움직이는 기준밀도·고유시간·두beta branch를 포함한6상태RHS,36개Jacobian항,JVP,양의tube와Lipschitz/curvature상계|실제33/30상태native client,물리provider jet·domain,원래H5history|
|stopping → HE reservoir|moving finite-volume mesh-work와같은flux의입자·에너지교환,implicit thermalcutoff,명시적BED에너지표현변환|실제evolvededge/source/closure오차와전체충돌kernel|
|geometry ← source moments|실제endpoint의H/shear에결합한조건부positive stress response와angular오차전달식|시간변화·충돌·deltaH·다른sector·Einsteinconstraint|
|evaluated tritium → stopping|DDEP실제branch/endpoint/electronfirstmoment를property별packet으로확보|charge/environment맞춤,spectrum·recoil·sourceamplitude,고에너지stopping|
|HD source → REC|표준CDMS출력precision의35Hzgate제약을정량화|고정밀same-fit energy/frequency원자료;서버취득실패보존|

서로 반영한 변경은 다음과 같다. Independentreview가 moving-grid moment 자체의속도의존성을지적했고 theory가 I_h=I0+L theta_dot를유도해 implementation이같은단일실행전에반영했다. Nuclear가electronbirth count를제공하고 stopping은물리kineticenergy·taggedcoordinate·heat를구분했다. Tritium의평균전자에너지는현재150eVstopping범위의입력의무를구체화했다. Geometry는localcollision교환과공간팽창work의소유권을분리했다.

## 실제 유도와 구현

### 기준밀도·clock을 포함한 beta caller

x_i=n_i/r, ell=ln(r/rstar), chi=dtau/deta, alpha=dlnr/dtau, theta=dlnV/dtau라둔다.
z=(x_n,x_p,x_H0,x_e_fast,x_antinue,ell)이며
nu_c=(-1,1,0,1,1), nu_b=(-1,0,1,0,1).
물리체적·propersecond당source S를받으면

f_x=chi[e_n S/r+nu_c lambda_c x_n+nu_b lambda_b x_n-(theta+alpha)x],
f_ell=chi alpha.

S/r의ell미분,rate/source/clock의모든stategradient를포함한전체6x6Jacobian을구현했다. Boundbeta의H0는boundelectron을포함하며freeelectronpool에중복추가하지않는다. Exactcomoving-lift oracle은기존parenttransfer를재사용해모든daughter에도같은referencefactor를적용한다. x와r의표현을바꿔도물리밀도r*x가같은지검사했다.

w=(3,1,2,1,1)에대해w nu_c=w nu_b=0이므로W=w*x는proper time에서
dotW=3S/r-(theta+alpha)W
를따른다. 이식으로실제providerbox가주어졌을때닫힘을판정할수있는명시적양의tube를구성했다. 원래33/30상태client와H5의313queryhistory는이6상태component와별도다.

### 움직이는 열화 경계

상대edgecurrent F=j-w_edge*N와cellcount n_i를사용하면
dotn_i=F_i-F_(i+1).
이산에너지U=sum e_i n_i의미분에는sum dot(e_i)n_i라는mesh-work가필요하다. cutoff c에서Phi=-F0라두고같은currentmoment I_h를쓰면
dotN_reservoir=Phi,
dotU_resolved=I_h-cPhi,
dotU_reservoir=cPhi-I_h
로정확히짝지어진다. Phi는부호를유지해backflow를허용한다.

선택한Maxwellcaloricclosure에서theta=k_B*T_gas를eV로표시하고c=kappa*theta라두었다. I_h=I0+L*dot(theta)인경우
Ceff=C-kappa(c-h)Nedge+L,
dot(theta)=[-(c-h)jedge-I0]/Ceff.
Ceff<=0은해당closurebranch를거부한다. 양의branch에서도보존식만으로thermalization을승인하지않는다. L항은새로운실제상호반영결과이며테스트에는L=0과L=2의독립유리수기준을모두넣었다.

NativeBED의13.6057eV와기존13.6eV는모든전하의장부를epsilon'=epsilon-delta*q,delta=.0057eV로동시에변환하면표현상연결할수있다. Electron의tagged좌표xi=E+delta를물리kineticenergyE와구별해야한다. 속도·압력·stopping은E를사용하며원래sourceatoms의물리적의미는변경하지않았다. 이변환은전하보존에따른에너지기준의자유도이고실제spectrum/threshold를새값으로물리적으로바꾸는승인이아니다.

### 각분포에서geometry로의다음연결

Fermi정상tetrad에서비상대론적collisionlessstress P에대해
dotP=-5HP-sigma P-Psigma+S,
S=(2K/5)(2I-M), M>=0,trM=1
을유도했다. 실제기존H1source의K=1.4625823043267652e-36J/m^3/s와저장endpointH/shear를앵커로삼되,상수유지source/background는명시적조건부모형이다.

P=pI+pi라분해하면dotpi에는-2p*sigma가들어간다. M=I/3의등방주입과빈초기P에서도
pi=-(2K/3)sigma*t^2+O(t^3)
이므로팽창비등방성과등방pressure의결합을버릴수없다. Matrixcongruence형정확해는PSD를보존하며,signedstress와sourceangularerror를고정Einsteinforcing연산자로보내는closedkernel을구성했다. Fullfeedback에서는deltaH항·다른sector·constraint·collision과freezingerror가추가로필요하다.

## 실제 source확인으로 줄인 불확실성

DDEP/BIPM2006평가에서H3전자평균kineticenergy5.68(1)keV등을직접확인해typedpacket으로보존했다. 분자상태half-life와원자endpoint의환경차이를유지했다. 하나의공통qualifiedlaw가0<=E<=Emax이고평균mu를가지면,
P(E>Ec)>=max(0,(mu-Ec)/(Emax-Ec)).
명목mu5680,Emax18564,Ec150eV를같은law로가정하면5530/18414다. 발표된표준불확도를hardbound로쓰거나property환경을섞어무조건적인물리tailbound로주장하지않는다. 같은law의평균이150eV보다높다면그law전체를현재150eVprovider에담을수없다는입력의무는명확하다.

Excitation원논문과database페이지는같은BEscaledrows에각각10.204와10.1988eV를표시한다. 3/4*13.5984=10.1988,3/4*13.6057=10.204275의hydrogenic관계는가능한mass/Rydbergconvention설명이다. 출처가명시한원인으로단정하지않고,서로다른energy값을행에조용히붙이지않았다.

HD의표준cataloglowerenergy소수4자리cm^-1과frequency소수4자리MHz는약2.998MHz의독립roundingallowance를가진다. 기본energy출력6자리cm^-1와frequency출력도30029.2458Hz수준이다. 이precision정보만으로원래35Hzgate를보증할수없다. 실제잔차가반드시그만큼크다는뜻은아니다. 고정밀same-fit원자료가필요하며현재endpoint의503/timeout을보존했다.

## 검증·근거 상태

- implementation-verified: 새15/15groups, beta8+moving7. source/rate는명시된syntheticanalyticjet·유리수fixture이며물리율교정과구분한다.
- derived+symbolicallychecked: stopping10개Wolframzeroidentity,geometry4개zeroresidual와regularseries. 실제경고와contexttool오류도보존했다.
- literature-supported: 고정된DDEP평가properties,CDMS출력format,NIST원논문규약.
- unresolved: 실제source/branch/state맞춤,fullcollision/feedback,originalH5/V6/V8와최종all-selectedphysicalplot.
- no new strong no-go claim: 원래일반목표의불가능성을주장하지않는다.

전체count는원래gate로만집계한다. 앞루프의HE-EXP-SPECIES와REC-EXP-SPECIES완료는보존했고이번component를새node로추가하지않았다. N6HOLD,L4=false,globalphysicalcompletion=null.

## 세물리축과자원

대칭성/게이지: 기준밀도재표현과properclock,직교tetrad회전,전하보존에따른에너지기준변환을각각분리했다.
불변량: baryon/charge/electronlepton장부,같은flux의number/energy교환,PSDmoment와signedSTF를검사했다.
관측가능량: 물리밀도r*x,열적energy/temperature,pi와forcedshear가각각실제source와closure에어떻게이어지는지명시했다. Arbitrarynormalizedx나taggedxi는그자체의관측량이아니다.

새childCPU .034406s,wrapperstartup .028315604s,기록tail예약.01s로새debit .072721604s이다. 알려진planning은9.874926553/10CPU s,child누적8.850973s이며historical/preexec/review/metadata비용은UNKNOWN_NOT_ZERO로별도유지한다. 산술잔여.125073447은추가실행허가가아니다. Main595.225063/600 NO_MORE_IVPs,다른owner예산,기존완료계산을보존했다.

다음최소연결은이15검사component를실제nativecaller/provider와연결하고,thermalinterface의actualedge와source조건을받는것이다. HD고정밀deck과tritiumcharge-qualifiedspectrum은독립적으로진행할수있다. 반복검토대신새입력과바뀐의존성만검증한다.
