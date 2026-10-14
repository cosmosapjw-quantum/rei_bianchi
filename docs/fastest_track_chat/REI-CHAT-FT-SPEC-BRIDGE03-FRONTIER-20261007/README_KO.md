# BRIDGE03 FRONTIER: 사전등록 출력시각의 양의 방출 quadrature

상태: FINITE_REPORT_FRONTIER_QUADRATURE_NATIVE_VERIFIED__GLOBAL_SOURCE_INTERVAL_OPEN.
사용자 첨부 BRIDGE02의 다음 작업을 실행했다. 이 폴더는 동일 이름의 다른 원격 BRIDGE02와 충돌하지 않는 별도 scope다. 원 production source, S0, CODEX_SYNC, runtime 반환과 physical HOLD는 유지한다.

## 결과

같은 FT03/S0, 0..1e12 proper seconds, H=1e-14/s, nH=1e-4 exp(-3Ht)/cm3, fHe=.083, 초기 (.9,.3,.6,w0=13.620772387478219eV/H), 초기13.7eV photon .05/H와 연속source5e-15/H/s를 사용했다. HG rate-moment CaseA HHe CI/RR/두DR와 전자수·온도 되먹임, 아래 문턱 광자를 그대로 유지했다.

출력시각은 실행 전에 t/T=.25,.5,.75,1로 고정했다. Birth cell을 출력시각 및 t-log(Eb/Ec)/H에서 나눈다. Fit Ec=13.6와 binding chi=13.598434599702eV를 구분한다. 분할 cell [l,r]의 Gauss2는 b=(l+r)/2 ±(r-l)/(2sqrt3), photon weight=S(r-l)/2다. 양의 weight와 하나의 고정 cohort 목록으로 전체 이력을 계산한다. 출력 때 광자를 재배분하지 않는다.

원 T0 half-clock6.25e8s의1601개 경계를 모두 보존하고 여섯 source규칙의 birth/threshold/출력시각을 합친 공통2237구간을 사용했다. 같은G2B64 birth로 시간만4474구간으로 세분했다. 실제 CharacteristicRay::pullback 및 primary_stage_step_conservative를 사용했지만 원paired_trial의intervalroot/local/publicwidthgate를 실행하지 않았다. 원scientificmodule13개 무수정이다.

같은2237시계의 활성photon/H 참조차:
- plain midpointB128: +3.73609011346e-6
- split midpointB128: +1.82233432192e-7
- split Gauss2B32: +1.88710817871e-7
- split Gauss2B64: +1.88586739108e-7
- 같은G2B64의4474시계: +9.42947642668e-8

G2B32->B64 차이는 -1.24078762456e-10/H, 온도차는 -6.92038156558e-7K다. 그러나 G2B64의 온도 참조차는 .226857367459K이며 시간 이등분 뒤 .113450409117K다. Reference는 계승한 수치값 T=47917.629222632495K,active=.0024604381148211263/H이며 새로운 exact-solution interval이 아니다. Scalar Richardson의 참조차 T=4.34508e-5K, active=2.78943e-12/H는 진단이고 실제 상태/인증이 아니다.

## 이론적 범위

등록한 시각에서 무흡수·상수source active count는 정확 산술에서 정확하다. 실제float rule과80자리 기준 최대차5.161e-20/H를 확인했다. 반면 등록하지 않은 .831T에서 G2B64는 -3.02075460364e-5/H 오차가 남는다. 유한 출력시각의 성공은 전체시간창의 성공이 아니다.

각 cell C4 응답의 Gauss2 오차는 width^5 sup|F^(4)|/4320, midpoint C2는 width^3 sup|F''|/24다. 실제 coupled history 전체의 도함수 상계는 미확립이다. 잘못 배치한 frontier에는 jump*위치오차 항이 필요하다. 전역source CDF discrepancy는 상수source에서 delta=S maxwidth/(2sqrt3), 임의 birth interval count차<=2delta다. 이번free active 상계4.510548978e-5/H는 위 미등록시각 반례를 포함하지만 coupledgas bound가 아니다.

## 검증

Fresh reproduce.py의 test/compile/7native/nativecheck/theory 다섯명령 exit0. Unit8 중1개 red/green,7개 tests-after. 최종7이력17896source stage,21독립4gasBE roots,5006scalar비교. 최대normalizedgas차2.67226e-16,eventrelative3.92030e-15,독립BEresidual2.33018e-16. Number ledger1.00337e-14/H,energy ledger1.42109e-14eV/H. Symbolic5개와상수hazard96case를 별도검사했다. Directed intervalcertificate나physicalaccuracy가 아니다.

Pilot+fresh합계14이력35792stage42roots,sciencecompile2회이며 stdout byte가일치했다. Cargo/fullF08/과거suite/부모증명/새continuousIVP는0회다. 첨부Rust1.94.1실행은확인했지만서명진본성은미검증이다.

## 계승과 다음 작업

첨부 BRIDGE02 SHA b18d67eae4c3376846bc668f6cd30867f1c8c54bd6edbad0d0a8b28642d2d883와 원격 동명 SHA9820aee6de19f1e843ec083551a2dc9b2b7037dc6b7bdd351b893734978c4b8a는 다른산출물이다. 새sourcefrontier결과를 원격parent-box후속으로 위장하지 않는다. 연구중SYNC03영수증5파일이 추가돼7d12cb3a000cbbe8dc9e8d93e8fc441cf4e63577을게시부모로보존한다.

다음은 실제F08 public output시각과spectralpredicate를읽어한sourcepartition에연결하는 FT_SPEC_BRIDGE04_DECLARED_OUTPUT_GRID_ADMISSION이다. Cohort parentboxes/energy불확실성은별도원격lane의결과를먼저수신한다. Default교체,BI각도확장,cohort압축,physicalfit및nativeglobaltimecertificate는미승인이다.

전체보고서·코드·원source·실제binary/stdout·검사기·실패로그는 ARCHIVE.json의 ZIP에 있다. 실행: python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. Source13hash검사, network/Cargo없음.

기존local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존. BackupR1metadata와remote복구/bytehash/과학검증은구분한다.
