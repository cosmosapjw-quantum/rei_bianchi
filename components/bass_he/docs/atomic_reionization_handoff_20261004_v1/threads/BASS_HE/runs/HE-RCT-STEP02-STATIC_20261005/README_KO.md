# HE-RCT-STEP02-STATIC: 누적 사건수와 continuous-time 오차

SCOPED_STATIC_TRAJECTORY_PASS__OWNER_ADOPTION_PENDING. 기존 STEP01 add-on과 vendor86payload를 그대로 두고 public try_adaptive_step을 호출하는 별도 bounded history caller를 구현했다. 원 소비기/F08/dispatcher 변경0, whole current crate build0, 물리승인false다. 이전 게시 대기3355cd79252deb325b9e1290d618885947f0fcf8은 이번 정상 non-force update_ref로 반영됐다. 이전 safety block은 과거 실패로 보존한다.

사전등록: 정적 proper nH=1e-4,nHe=8.3e-6 cm^-3,T0=50000K,fractions=(.9,.3,.6),photon=(.05,.005,.001)*nH,E=(20,35,70)eV,시간0..1e11s. OFF 및 KF96 k=1e-14 cm3/s, explicit Ebar=Q-1,Q,Q+1의 네 경우에 macro dt cap1e9,5e8,2.5e8s를 적용했다. PREREGISTRATION.json은 과학 실행 전에 고정됐으며 SHA256 f41fae10c01c299827c94323bd5ab4b7d58120084f741900a92509ed79ea526b이다. source/Ebar 자동전환, GM25, 팽창/S0 실행은 없다.

기존 event allowance aJ=1e-14 events/H,rJ=2e-4, residual1e-14,max_iterations80,strict state difference<2e-4 및 floors를 유지했다. 각 accepted macro step은 두 BE half의 상태/장부다. Full 후보는 누적하지 않는다. 지정된 local-error/nonconvergence만 dt/2로 재시도하고 source-domain/underflow는 terminal이다. 종료시각에 맞춘 dt 축소만 허용하며 상태 clipping은 없다.

총12이력,100/200/400 macro steps씩 총2800 accepted macro steps를 계산했다. 각 이력의 사건/종/광자/열+결합+복사+탈출 energy 장부를 합산했다. 최대 global scaled ledger defect1.99347e-12, 최대 step residual6.17309e-15다. 이것은 continuous-time 오류가 그 정도라는 뜻이 아니다.

Ebar=Q에서 Jref=4.8832734736574474e-10 events/H. dt1e9/5e8/2.5e8의 native J error는4.54198609e-14/2.27132862e-14/1.13574823e-14 events/H다. 상대오차9.30111e-5/4.65124e-5/2.32579e-5, 관측차수.9997868/.9998934로 order1 수렴한다. xHII 절대오차8.46037e-7/4.23092e-7/2.11565e-7이다.

local e_n<=aJ+rJ*max(jfull,jhalf)에서 sum e_n<=N*aJ+rJ*sum max만 따라온다. aJ는 global tolerance가 아니고 sum local estimators도 rigorous flow bound가 아니다. 이 실험의 J actual error/sum estimator 비는.954973/.954454/.954195였지만 다른 궤적에 일반화하지 않는다.

직접 RCT 전자항은0이나, 실제 연속식 ON-OFF의 최종 delta(ne/nH)=-9.18359101384123e-12다. 원 다른 반응의 population feedback 때문이다. delta xHII=4.79083317e-10,delta yHeII=5.88273609e-9,delta yHeIII=-5.88273496e-9이다. 원자율의 물리적 중요도나 실제 우주론 예측이 아니라 고정 수학적 모형의 수치 결과다.

reference는 이전 독립 oracle의 equations 본문을 byte-preserving AST 추출해 재사용했다. DOP853 두 tolerance 설정(8solves)과 mpmath45자리 RK4 256/512(OFF/ON_Q,4solves)를 대조했다. 두 reference 방법은 동일 equations를 공유하며 독립 과학리뷰가 아니다. DOP853 J refinement 상대차최대2.75260e-15, RK4 state refinement 차이2.32885e-19다. 초기 summary가 먼저 float로 바꾸어 차이를0으로 출력한 문제는 두 regression의 RED/GREEN으로 수정했다. physics/tolerance 변경없고 첫 script/results는 보존한다.

새 native caller9tests와 Python metric2tests 통과. 전체 run_checks.sh를 새 output에서 실행해 warnings-as-errors build,fmt,tests,12native histories,reference,입력 post-hash를 실제 확인했다. 개발 실행과 최종 E2E로 같은12이력 캠페인은총2회이며 독립 성과로 합산하지 않는다. 이전 STEP01/mixed/atomic/F04/F05 scientific suites는 재실행하지 않았다.

이 caller는 O(N) 기록의 bounded research 도구이며 terminal error 시 accepted prefix의 persistent checkpoint 반환은 미구현이다. production restart engine 또는 uniform interval/flow certificate가 아니다. Rust1.94.1 user archive hash는 일치하나 GPG authenticity NOT_VERIFIED다.

Git에는 요약/수치반환과 실제 runner library를 보존한다. 전체 input/vendor/addon/tests/example/oracle/실패 및 최종 로그는 HE_RCT_STEP02_STATIC_20261005.zip에 있다. Git 요약만으로 전체 crate를 checkout한 것으로 취급하지 않는다. 자세한 REPORT와 source manifest,preregistration은 ZIP에 있고 archive/cloud identity는 DELIVERY_RECEIPT.json이 소유한다.

다음은 owner가 기존 STEP01의 event/underflow 예산을 채택하고 예약된 실제 경로로 통합하는 일이다. HE-F2global=false,HE-F3 WAIT_REI_F09_RESULT,RCT baseline OFF,moments null,physical HOLD,Eq55 NOT_RUN,legacy PARKED_OPEN을 유지한다. 같은 단일-step 설계나 이미 닫힌 finite gate를 다시 만들지 않는다.
