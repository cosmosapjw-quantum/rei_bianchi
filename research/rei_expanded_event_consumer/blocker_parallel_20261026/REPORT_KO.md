# 병렬 blocker 연구 결과 — 2026-10-26

이번 루프는 현재 중앙 DAG의 미완료61개 노드를8개 공통 blocker군으로 나누어 진행했다. 시작 집계는 독립 검토를 거친 **27/88**이다. 각 노드가 원래 선언한 산출물·gate를 충족했는지로 계산하며, 문서 수나 하위 lemma 수를 분자에 더하지 않는다. 조건부 유도만 끝난 REC-H5 전체 입력 의무는 완료에서 제외했고, 실제 채택 근거가 있는 기존 유한 결과는 재사용했다. 시작 원장과 모든 노드별 판정은 intake/BEFORE_NODE_LEDGER.json에 있다.

단일 경량 실행에서 **25/25 검사**가 통과했다. Beta8, species8, stopping9개 검사다. 신규 궤적·적분·307200개 source atom 재순회 없이 표준 라이브러리만 사용했다. 최종 독립 판정은 **PASS_SCOPED_PARALLEL_COMPONENTS_AND_TWO_CANONICAL_SPECIES_NODES**이며, HE-EXP-SPECIES와 REC-EXP-SPECIES를 채택해 달성 노드가 **27/88에서29/88로 증가**했다. 새 노드를 추가하지 않았고59개는 미완료다. review/VALIDATION.json, ADMISSION.json 및 GLOBAL_DAG_STATUS.json에 근거를 연결한다. 현재 중앙 기준은 a5db4bac9dafadae29685bbea3cec7f43ab990b2이며, integration branch의 새 근거 채택과 중앙 기준 브랜치로의 merge를 구분한다.

## 병렬 작업과 전체 목표상의 위치

|공통 blocker군|시작 미완료 노드|실제 연구 산출물|남은 전체 gate|
|---|---:|---|---|
|종 identity·소비자 연결|2|WU92개 identity에서 historical21과71개 확장을 연결하는 실행 가능한 projection; HE7원자핵종·전하 및 REC정확한 순서 대응|이 두 inventory gate만 독립 채택 대상; 반응률·미분 충돌 공급은 별도|
|감속·열화|5|실제 endpoint T/ne의 warm EE 계수; NIST native H BED의 2차 전자 에너지 법칙·paired ledger 구현|자기일관 screening, 나머지 산란/여기, 동적 경계·bath, 실제 cascade·침적|
|핵·약반응 생성|5|생성·beta·경쟁 손실의 정확한 전달식, 양의 해, Jacobian; charge/branch 의존 원전 확인|실제 생성 source, branch/상태별 rate·spectrum·recoil·stopping|
|원자·분자 원자료|12|HD7개 주파수 실패를 source 열의 불일치로 분리; LAMDA 포맷·CDMS새 버전 교차확인|원래35Hz gate를 충족하는 동일 source의 에너지·주파수 묶음 및 다른 state별 자료|
|각분포·쌍 충돌|7|H1 E1의 편광 coherency→각분포·응력 사상과 정확한 모멘트|같은 source의 방향/편광 정보, nondipole·유한질량 recoil 및 다른 pair법칙|
|geometry·수송|8|양의 moment cone에서 STF응력 상계와 입력오차 전달식|실제 시간 이력·BASS propagator·source uncertainty·feedback|
|history·수치 domain|14|실제 beta 구성요소의 rate/time까지 포함한 Jacobian, 양의 유한시간 tube와 유한-box Lipschitz 상계|전체 client 입력사상·나머지 연산자·동시 도달 영역·실제 결함 상계|
|결합·관측량|8|native binding 차이의 사건별 에너지 오류식, 단일 에너지 소유권과 관측량 연결조건|공통 에너지 convention의 승인, 실제 H/shear·조성·열 이력과 관측 오차|

총61개 노드의 정확한 ID·owner·gate·예산·조건부 의존성은 intake/BLOCKER_MAP.json에 보존했다. 각 군은 실제로 수행한 산출물의 범위로 판정한다. 종 연결 외 부모 노드를 위의 구성요소 결과만으로 완료 처리하지 않는다. N6 HOLD, L4=false, 전역 물리 완료율 null과 기존 owner 예약은 유지한다.

## 1. 종 연결: 실제로 닫을 수 있는 기존 두 노드

WU의 원본92개 identity, 독립 admission, HE consumer registry, REC atomic model 네 입력의 원본 Git blob과 SHA256를 고정했다. H1,D,T,He3,He4,Li6,Li7의20개 원자 전하 상태와 별도 neutron을 합한21개 material 항목을 정확히 연결했다. REC순서는 원본 crosswalk와 species_order로 연결하며 임의의 Li순서를 사용하지 않는다.

중요한 의미 차이도 보존했다. WU의 population_aggregate_unresolved와 HE의 ground bookkeeping 표기는 핵종·전하 projection만 공유하며 완전한 electronic state 동등성이 아니다. REC의 n_i/n_b와 REI의 n_i/n_ref를 단순 순서변환으로 바꾸지 않는다. e_fast와 e_th도 별도 pool이다.71개 확장 identity는 source행·분자 구성·isomer·qualification을 유지하면서 consumer_admission=UNADMITTED,active=false,rate=null로 남긴다.

HE-EXP-SPECIES의 원래 gate는7개 target의 명시와 unsupportedpair의 INPUT_PENDING 표시다. REC-EXP-SPECIES의 원래 gate는 historical21의 정확한 재현과 source-referenced UNADMITTED확장이다. 실행된 projection과 부정 대조가 이 gate를 검사했다. 이 결과는 WU권위를 보존하는 소비자 연결이며 새 물리 rate나 전체 WU registry완료 주장이 아니다.

## 2. 실제 상태의 warm EE와 native BED

저장 endpoint의 T=14994.847774798709K와 thermal bath로 선언한 n_e=5.996197830412253m^-3를 사용했다. lnLambda=20은 지정된 leading-log 모형 값이며 자기일관 screening 결과가 아니다. 기존 CR59/CR99의 Maxwell bath 연산자를 재사용했다. 에너지 단위 eV, theta=k_B T/(1eV), x=E/theta에서

    F(x)=erf(sqrt(x))-2sqrt(x)exp(-x)/sqrt(pi),
    D=theta b0 F, A=b0[2sqrt(x)exp(-x)/sqrt(pi)-F],
    j=-D[dN/dE+(1/theta-1/(2E))N].

따라서 N_eq proportional sqrt(E)exp(-E/theta)는 zero current다. 낮은 에너지에서는 A>0으로 bath에서 에너지를 얻는다. 초기 주입 에너지를 모두 단방향 냉각시켜 heat로 넘기는 모형과 다르다. 온도비 a=T1/T0, b=(n1 lnLambda1)/(n0 lnLambda0)*a^(-3/2)에 대해 A1(aE)=baA0(E), D1(aE)=ba^2D0(E)를 유도·검산했다. 원래 finite grid의 상단을 이 변환으로 옮겨도103.37248eV이므로134.47572eV까지 있는 현재 source전체의 동적 grid가 되지 않는다. 이번 구현은 실제 source범위를 포함하는 계수 query다.

NIST의 native H BED singly differential cross section을 실제30eV 원자료10행과 함께 확보했다. 출처는 https://physics.nist.gov/PhysRefData/Ionization/intro.html 과 Kim–Rudd1994 모델이다. 동일 사건의 출력 에너지를 W와 E-B-W로 묶고0<=W<=(E-B)/2만 적분하는 법칙을 구현했다. 사건 하나에 전자는 순증가1, HI는−1,HII는+1, kinetic loss는B, binding gain도B다. paired 법칙에 다시2를 곱하지 않는다.

native B=13.6057eV와 기존13.6eV convention은 다르므로 기존 network에 자동 활성화하지 않았다. 차이는 사건당0.0057eV이며, 물리 heat나 임의 offset reservoir로 숨기지 않는다. 실제 moving target convolution, 나머지 excitation/elastic/RR/ion process, finite boundary의 bath energy row와 cascade는 남은 입력이다. thermal_heat는 null이다. 원자료 근사 오차, printed-parameter 재현 오차, 부동소수점 오차를 구분했다.

## 3. n/T 생성과 beta daughter 전달

T는 삼중수소이며 온도는 T_gas로 구분한다. 일정한 source s>=0, 선언된 beta branch율lambda>=0와 경쟁 손실kappa>=0, proper durationh>=0에서 k=lambda+kappa라 놓으면

    P1=exp(-kh)P0+A s,
    I=A P0+C s,
    A=(1-exp(-kh))/k, C=(h-A)/k,
    B=lambda I, R=kappa I,
    P1+B+R=P0+sh.

k=0에서는 A=h,C=h^2/2다. 작은 kh에서는 안정적인 phi급수를 사용한다. n/T의 초기값이0이어도 s>0이면 부모와 daughter가 생긴다. beta가 경쟁 손실보다 빠른지와 실제 잔류량은 source 및lambda/kappa에 달려 있으므로 relic 생존만으로 이후 생성량을 결정할 수 없다.

계속되는 소스가 있을 때 n→p의 순기여는 beta 사건 수와 실제 daughter pool로 반응망에 연결한다. neutron의 continuum beta와 bound beta(n→H+antinu), tritium의 neutral/bare·continuum/bound branch는 전자·이온 pool을 다르게 만든다. 따라서 측정된 총 disappearance율을 정확한 free electron yield로 자동 치환하지 않았다. UCNtau2021의 mean lifetime, NIST2000의 tritiated-water half-life는 출처가 고정된 실험 입력으로 확인했으며, 코드의 empirical default로 넣지 않았다.

antinu_e+p→n+e+의 proton-rest threshold와 e−+p capture는 다른 반응이다. 원전의 kinematic threshold와 가능한 CR/열핵 생성 경로는 정리했지만, 실제 외부 spectrum·flux나 밀도가 없는 경우 우주론적 생성률을 만들어 넣지 않는다. 핵종·전하·lepton incidence와 에너지/spectrum/stopping 의무를 별도로 보존했다.

추가로lambda,kappa,h까지 포함한4×5 Jacobian과 양의 유한시간 tube를 직접 유도했다. 유한한 물리 scale과 source/rate box가 주어지면 명시적 Lipschitz상계를 얻는다. 이것은 V6/V8/H5에 넣을 수 있는 실제 구성요소 상계이며, 전체 coupled client의 source·clock·reference 입력사상까지 인증한 것은 아니다.

## 4. 각분포에서 응력으로

정상 tetrad, stationary H1 1s, nonrelativistic E1·heavy-ion 근사에서 transverse PSD trace-one coherency rho를 쓰면

    P(u|rho)=3/(4pi) u_i Re(rho_ij)u_j,
    <u_i u_j>=(delta_ij+2Re(rho_ij))/5.

비편광 photon 방향k에는rho=(I-kk)/2이며, <uu>=(2I-kk)/5다. 따라서 kinetic STF source는 사건당(4E/5)(Re(rho)-I/3)dW이다. 각분포의 정규화·양성성·trace2E와 기존 energy marginal을 보존한다.

비편광 source에서K=integral E dW,M=integral E kk dW/K라 두면M>=0,trM=1이므로

    ||dot(pi)||_F <= (2/5)sqrt(2/3)K.

이 식은 현재 유한 source의 K를 이용해 방향이 미지정된 경우의 조건부 응력 반경을 제공한다. 임의로 등방성을 넣어 반경을0으로 만드는 대신, 실제 입력의 부족을 유한한 상계로 전달할 수 있다. source의 energy-weighted total variation도 같은 계수로 stress오차에 전달된다. BASS의 실제 propagator·시간 이력, finite recoil와 nondipole오차는 별도로 필요하다.

PR233은 energy marginal을 저장했으므로 그 파일만으로 방향·편광의 joint measure를 복원하지 않는다. 새 CDF의 continuum오차도 이번 lemma로 인증하지 않았다.

## 5. HD 실패의 원인 분류

기존35Hz수준의 gate에서 실패한7개 항목은 source에 적힌 level energy와 transition frequency 자체의 불일치다. 실제 차이는6.865kHz–1.828MHz로, 명시된 자릿수의 반올림으로 설명되지 않는다. 구현 index나 단위 변환 오차로 분류하지 않았다.

LAMDA의 원래 포맷에서는 frequency가 informational column이지만, 현재 소비자는 population energy·radiation energy·열 장부에 같은 전이 에너지가 필요하다. 포맷 유효성과 이 더 강한 물리 계약은 다르다. CDMS의2026년 version3은 구체적인 후속 source 후보이나, 같은 URL에서 구버전 응답도 관측되어 immutable 원자료와 행 대응을 확보해야 한다. 원래 gate와 실패값을 유지하며, source 교정 없이 tolerance를 넓히지 않았다.

## 검증과 실행 자원

|검사|실제 결과|
|---|---:|
|전체|25/25PASS|
|warm EE 독립 anchor 상대차|1.5432100042289676e-14|
|EE dilation 상대차|2.220446049250313e-16|
|Maxwell current 잔차|0|
|BED 고정식 독립 anchor 상대차|7.771561172376096e-16|
|NIST rounded native table 상대차|2.537388238854632e-5<5e-5|
|paired energy 절대 잔차|1.2434497875801753e-14eV<3e-13|

NIST5e-5기준은 표시된 모수·자릿수의 재현성 기준이다. 물리 SDCS정확도는 별도 미확정으로 유지했다. Beta의 zero rate/duration, 작은·큰kh, semigroup, source-driven 양의 입력과 부정 대조를 검사했고, species의 잘못된 isotope/pool/normalization/state 등도 거부했다.

child CPU0.051992초, wall0.05464920999656897초. wrapper CPU0.039189227초와 최종 기록 tail의 보수적0.01초를 더한 planning debit은0.101181227초다. 실행 직후 planning은9.791011564/10초다. 이후 계측된 독립 검토 metadata CPU0.011193385초를 더한 현재 장부는9.802204949/10초, 산술 잔여0.197795051초다. 첫 metadata assertion과 일부 기록 tail·과거 미계측 비용은 UNKNOWN_NOT_ZERO이므로 산술 잔여를 추가 실행 허가로 해석하지 않는다. 원래 child 원장은8.816567초이며 기존 overhead와 합쳐 의미를 바꾸지 않았다. main595.225063/600 NO_MORE_IVPs와 타 repo예산은 보존했다.

원격 Wolfram의 CPU는 제공되지 않는다. 실제 호출·시간 제한·실패/경고는 각 lane에 보존했다. Angular의 첫5초 제한 실패는 azimuthal 적분을 해석적으로 처리한 후 polynomial 검산으로 교정하여 정확한5개0잔차를 얻었다. 이는 물리 실패가 아니며 실패 기록을 삭제하지 않았다.

실행 후 stopping계약의 상대경로2개만 교정됐다. 실행 snapshot과 current양쪽 identity를 검토 기록에 남기며, 식·입력값·허용오차 변화로 취급하거나 과학 실행을 반복하지 않는다.

## 세 물리 축과 다음 실제 작업

대칭성/게이지는 tetrad·편광기저·기준밀도·proper clock의 변환으로 다뤘다. 불변량은 확률·핵종/전하/lepton·사건 수·에너지 및 양의 moment cone으로 검사했다. 실제 관측가능량은 온도·이온분율·signed stress·H/shear이력으로 이어져야 하므로, 현 단계의 계수·주입률·상계를 그 관측량 자체로 부르지 않는다.

다음 최소 물리 작업은 native binding convention을 공유하는 실제 HI secondary 채널과 excitation 입력을 선택하고, warm EE의 동적 경계·bath 장부와 함께 source를 소비하는 것이다. 동시에 branch/state-qualified beta spectrum과 외부 생성 source, HD의 동일-source energy/frequency묶음을 받아야 한다. 전체 n/T·핵반응·coupled-history·관측량 노드는 이 실제 입력을 기다린다. 기존 완료 계산을 반복하지 않는다.

최종 독립 검토·root판정·DAG적용·게시·백업의 실제 상태는 각각 review/VALIDATION.json, ADMISSION.json, GLOBAL_DAG_STATUS.json, delivery/FINAL_DELIVERY_RECEIPT.json을 확인한다. 이 결과를 all-selected physical pilot plot완료로 확대하지 않는다.
