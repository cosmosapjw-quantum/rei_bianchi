# RUN10: H/D 문턱의 출생 에너지 역상과 양의 스펙트럼 구적

2026-10-18 KST. RUN09 commit 86ffbea52e3a786ef360cf1434b8e3504e2dfdbf 다음 P4-S4C-SPECTRAL-EDGE-SUPPORT를 수행했다. 이번 판정은 PARTIAL이다. 샌드박스 terminal은 ClientError, Python은 ServerError를 초기 호출과 최소 진단에서 각각 반환했다. Rust 컴파일/시험, r4 native packet 생성, BASS 공동 적분, 로컬 archive 복원은 실행하지 못했다. Wolfram 수치실험은 요청된 CAS 도구의 실행이며 샌드박스 Rust 실행으로 기록하지 않는다. 별도 native subagent, local/Codex/NCP/SSH는 NOT_RUN.

## 1. 실제 읽은 원본

부모 HEAD를 재조회했다. 같은 commit의 iso_couple_p3 owner_src에서 axbi_sources.rs(blob36d24eb13db3fc42321cb0ddb165e003c0a086c7), hhe_events.rs(57a63eee1e9d8c4aa2b5ed663dbea15619359f71), atomic_provider.rs(62211d8910cd332fffa8f94c6989cae77128916e), deuterium_atomic.rs(9d64984fe091b7e0ed1f13e63ce411b4d6ac5632)를 읽었다. 기존 파일은 변경하지 않았다. RUN09 ZIP의 새 로컬 SHA 검증을 수행했다는 뜻은 아니다.

원래 shape는 g(E)=E^2/expm1(E/kT), kT=(1.380649e-16/1.602176634e-12)*50000 eV. 첫 셀 [13.6,13.6*(24.59/13.6)^(1/16)] = [13.6,14.112863291954786...] eV. H binding13.598434599702, H fit edge13.6, inherited manufactured D edge13.602134599702 eV를 구분한다. D 단면적은 기존 H-equality approximation이며 isotope-specific 측정치가 아니다.

## 2. 문턱 역상 (직접 유도)

무산란 null ray의 에너지를 E(t)=R(t;tb,mu) Eb라 하자. 양의 단조감소 R(tb)=1,R(t1)=eta<=1이면 active threshold epsilon을 통과하는 birth energy는 epsilon<Eb<epsilon/eta이다. 따라서 셀의 분할점에는 birth edge epsilon뿐 아니라 terminal preimage epsilon/eta도 포함해야 한다. eta<=1인 endpoint만으로 단조성은 증명되지 않는다. BASS 도입 시 원래 H>0,-1/2<b_X<1 구간 검사를 먼저 적용해야 한다. 비단조/축수축 기하는 이 보조함수의 범위 밖이다.

제조 FLRW 대조 eta=exp(-.0004)에서 D crossing band는 (13.602134599702,13.607576541857753) eV이다. birth D edge만 나눈 GL3의 upper-panel 첫 노드는13.65969457387586eV여서 이 band를 전부 놓친다. 실제 연속 first-cell conditional photon mass는 .010871289873784619, 약1.08713%다. 이는 광자 가중치의 비율이며 실제 흡수 사건수 또는 전체 source의1.08713%가 아니다. 실제 BASS eta나 전체 r4 결과로 승격하지 않는다.

## 3. 양의 가중 Gauss2 구성

각 swept panel [a,b]를 local z=(E-mid)/half in[-1,1]로 옮기고 Mk=integral z^k g(E)dE,k0..3를 구한다. mu=M1/M0, v=M2/M0-mu^2>0, c3=M3/M0-3mu M2/M0+2mu^3, d=c3/v. Jacobi matrix [[mu,sqrt(v)],[sqrt(v),mu+d]]의 고유값 z-/z+를 쓰고 w-=(z+-mu)/(z+-z-), w+=(mu-z-)/(z+-z-)로 둔다. 양의 measure에서 nodes는 panel내부, weights는 양수이며0..3 polynomial moments가 일치한다. 실제 Rust port는 위반/음수/분해불능 구간을 error로 반환하며 repair/clipping하지 않는다.

부모 source count fraction f0를 새 점에 f0*(M0_panel/M0_cell)*w로 배분한다. 이것은 같은 shape의 conditional measure 정의이며 전체 photon 수의 사후 정규화가 아니다. 수치 residual을 보고하고 숨기지 않는다. 연속 shape의 number/energy moment는 보존하지만 원래 Simpson32 owner mean과 정확히 같은 수라고 가정하지 않는다. exact-decimal MP55 reconstruction에서 연속 mean13.854295937820614와 Simpson32 mean의 차이는-3.44448397956e-12 eV. 이 값은 실제 native binary64 bytes의 실행 parity가 아니다.

Gauss2 remainder는 C4 response에 대해 R4(xi)/4! * integral[(E-E-)(E-E+)]^2 dmu이다. 문턱에 의해 반응함수가 불연속인 구간에는 직접 적용하지 않는다. 이 나머지식도 nonlinear coupled ODE의 오차 상계가 아니다.

## 4. 실제 Wolfram 실행

spectral_edge_reference.wl은 MP55에서 같은 원본 Verner HI 식을 재구성하고 terminal E=eta Eb에 대한 conditional averages sigma_HI,sigma_DI,sigma_HI(E-chi_H),sigma_DI(E-chi_D)를 적분한다. 단위는 m2,m2,eV m2,eV m2. 고정 terminal response이며 진화 불투명도/기체/흡수누적/광원시간적분은 없다. 원자 constants는 같은 원본에서 읽었지만 독립 atomic-data validation이 아니다.

2-node weighted rule의 4 swept panels를 m1/2/4로 나누면8/16/32 nodes이다. 상대오차는 RESULTS.json에 있고, 가장 큰 D heat kernel 차이는3.9251703e-6,2.4588613e-7,1.5376707e-8이다. centroid 대조는4nodes에서 .0162141 Dheat오차를 남긴다. photon count와 mean energy만 맞추는 것이 heating 정확도를 보장하지 않음을 보여준다. 양수/노드범위/0..3moments/count/energy/crossing class의 여섯 Wolfram 검사가 True였다. 큰 정밀도에서 출력된0은 유한 정밀도 잔차이며 exact arithmetic proof와 구분한다.

Rust candidate에는6개 단위시험을 작성했지만 실행0개이다. cargo PASS, native integration PASS, joint spectral convergence PASS를 주장하지 않는다. 최초 Wolfram 코드의 Table list-destructuring 오류(Table::write)를 실제로 확인하고 integer-indexed iteration으로 고쳐 재실행했다. 초기 symbolic Sort 순서는 numeric Sort로 교정했다. 두 표현/구현 오류를 결과에 포함하지 않는다. TDD로 작성했다고 주장하지 않는다.

## 5. 다음 실행과 보존

상위 DAG는 PARTIAL. 다음은 같은 노드의 NATIVE-INTEGRATION child다. 샌드박스 복구 후 RUN09 ZIP 해시/복원, Rust6시험, 원래 first-cell adapter를 연결하고160births/GL8/다른47cells/기하/원자/IC를 고정한다. 각 실제 ray의 eta를 사용하고 manufactured FLRW eta를 재사용하지 않는다. first-cell m1~2를 우선 비교한 뒤 필요할 때만 세분한다. 최대4panels일 때 m1은전체55energy nodes로160*8*55=70400cohorts, m2는80640이다. 이는 배치 전 산술 추산이며 실제 비용/메모리/최종cohort수는 측정하지 않았다.

RUN09 parent ZIP은039fbce620bfa90e43822727d01cb8a2734fbfa78ef894673c7de9a06aa16029, Drive1PBxYh7wM0t7IUrsB2v7g5eu6vW1BB9wo, Dropbox id:BSpOijBcT10AAAAAAD-obA. 이 과거 저장을 신규 전체백업 성공으로 세지 않는다. 이번 신규 소스/결과/상태를 connector-native bundle로 보존하며 원격 실제ID와 확인수준은 외부 영수증에 기록한다. 새 완전ZIP/실행복원은 현재환경에서 만들거나검증하지 못했다.

스펙트럼/각도 연속수렴, full EoR, Einstein 반작용, Li/Be 및 기존 핵물리T1-T8는 HOLD. 원래45/26DAG와 production/main/원본입력은 변경하지 않았다.

## 문헌

NIST DLMF3.5 https://dlmf.nist.gov/3.5 (Gauss quadrature/remainder); Verner etal1996 https://arxiv.org/abs/astro-ph/9601009 및 https://www.pa.uky.edu/~verner/photo.html (원자 fit의 근거); PawlikSchaye https://arxiv.org/abs/1008.1071 (동일원자입력 비교); Mirocha,Skory,Burns,Wise2012 https://arxiv.org/abs/1204.1944 (spectral discretization sensitivity). 문헌은 이번 수치결과나 독창성을 대신 인증하지 않는다. SciSpace/Exa발견을원문으로확인했으며 repository등록연도를출판연도로쓰지않았다.
