# FLRW04: 사건 에너지 measure와 이산 수지

판정 SOURCE_BOUND_CONTRACT_AND_DISCRETE_REFERENCE_CHECKED__EXPANDING_NATIVE_CONSUMER_OPEN. 현재 number-only FLRW callback과 새 FT03 Case-A thermal callback을 source에 연결하고 accepted stage의 사건수와 흡수 energy를 동일measure로 누적하는 계약을 작성했다. 원자/수치 모형의 기존production source는 수정하지 않았다. 외부 REI-F04 interval 작업과 이 chat FLRW04는 다르다.

## 연구 결과

dJ_s=c*n_s*sigma_s(E)*P*dt*dE*dOmega에서 J_s와 A_s=integral E*dJ_s를 함께 계산한다. Binding=chi_s*J_s, heat=A_s-chi_s*J_s다. Number-only output은 에너지 witness가 아니다. Bin[14,26]의 delta20과 halfdelta16+halfdelta24는 N=1,U=20eV,edge0이 같지만 시험 sigma proportional E^-3에서 흡수율1 대4375/3456이다. 약26.6%차이는 N,U,edge만으로 모든 spectrum의 원자 moments를 정확히 결정할 수 없음을 보여준다.

Delta(EP)=E1*DeltaP+P1*DeltaE-DeltaE*DeltaP. 마지막endpoint absorption과work를 함께 쓰면 residual=-DeltaE*DeltaP다. (P0,P1,E0,E1)=(1,.5,20,16)에서-2eV/H. 평균endpoint product rule은 선언한선형경로에정확하지만 midpoint decay kh=3에서는 P1/P0=-1/5다. 보존과양성/정확도는별개다. 같은RK tableau E/P의bilinear defect도직접유도했다. 외부exactgeometry E(t)를읽으면그전제가달라지므로endpointproduct를직접확인하며 사후heat보충으로결함을감추지않는다.

세absorber 문턱을통과하는70eV photon의지정hazard 기준해는 counts=(.484567815027,.304209283572,.081069572986),survivor=.130153328415/H,redshiftwork=27.3249516276eV/H다. 이는기체/Einstein진화나실제원자율모형이아니다. 실제filling_defect identity residual에는Q,Qdot가상쇄되므로잔차0이독립phasegeometry검증은아니다.

## 검증과 source 경계

최종unit3,symbolic9,exactendpoint80,spectral반례1쌍,cohort21,manufacturedstage3,invalid/rejected12. 최종4명령exit0. Numberresidual<=2.221e-16/H,energyresidual<=1.777e-14eV/H,finitecohort 최대relative차7.996e-16. H=0,E=chi의active E>=chi조건을확인한실패/수정/동일시험green을보존했다. Native/Cargo/ODE/과거suite 실행0. 유한기준검산이지physical/uniformcertificate가아니다.

6279036f의FT03 successor와reported92tests를수신했다. ft03_rhs는실제energycallback이지만 nH>0,nHe>0,T30000–110000K조건이다. Energy변경시cachedsigma를함께갱신하며pureH rawK2 numberroute와혼합하지않는다. 41e4592의opt-inhe_rct,a5d24047및7a15daa3의RCT문서/영수증추가도보존했다. RCT는활성화하지않았고외부tests는여기서재실행하지않았다. 첫non-force update의422거절후7a15daa3를실제게시parent로사용한다. 과학입력은같으며상세동기화는CONCURRENT_SOURCE_ACK.json이다.

## 전체 패키지와 다음 작업

REI_CHAT_FLRW04_20261005.zip:77147bytes,57entries,SHA256=f5bc20bbec974aa371bc568fe4a40338fefdffc1bbe7f9a6659e318509415c39. Drive ID18sfTilR9TJmADLjctOI7Le2Azya32-jN,Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW04_20261005.zip.

전체REPORT_KO.md,fullEVENT_WEIGHTED_CONSUMER_CONTRACT.json,코드/결과/실패로그/manifest는ZIP의rei_chat_flrw04_20261005/아래다. Repo8파일은요약/계약/결과/source/반환/인계/동기화/백업기록이다. 재현은 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python research/run_all.py.

다음 REI-CHAT-FLRW05_COHERENT_SPECTRAL_MEASURE는한양의reconstruction으로edge/count/absorption/heat를함께구성한다. Native expanding stage-return이오면이번계약에연결한다. actualcaller/history,독립QV,atomicaccuracy,externalF04certificate는열려있다. Local<2e-4/publicwidth<2e-3,[160,161]FAIL=2.1245050576368385e-4,tick160,physicalHOLD보존. 새branch/merge/forcepush/기존코드수정0.
