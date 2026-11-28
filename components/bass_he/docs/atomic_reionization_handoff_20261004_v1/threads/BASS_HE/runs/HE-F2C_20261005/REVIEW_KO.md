# HE-F2C: 조건부 수락 동기화와 isolated RCT 기준해

최종 실행 상태는 기존 root의 LOCAL_RHS_BINDING_ACCEPTED_WAIT_STEPPER_AND_F09다. actual_RCT_binding_accepted=true, HE_F2_global_completed=false, physical admission=false다. Codex가 508b6c366515b1d7b168285f20327138036cdefa에서 먼저 게시한 동일 수락을 보존한다. 중복 intake를 독립 과학 검증이나 두 번째 milestone으로 세지 않는다. 이번 변경은 additive reference이며 root/TASKS/CODEX_START/execution을 덮어쓰지 않는다.

## 수락 범위

Native commit41e4592aa494b48929dcd23fc8504c169a98a908/tree f44469e09cefe8b7c92a822e9913c47d0919782f, he_rct.rs blob37f83f83bb67cf0ad174b56ee748cf6733857701을 결속했다. 원 HE-F2의 여섯 조건은 explicit conditional local RHS에 한정해 충족한다. nu=(-1,1,0,1,-1,0), direct electron=0, density는 소비기가 한 번 적용한다. chemical=-QR, thermal=(Q-Ebar)R, escape=EbarR이다. emitted/escaped count=R, retained photon0은 명시적 escape이지 source null의 대체가 아니다. DEFAULT=OFF, 모든 source photon/heat/recoil/spectrum moment는 null이다.

Owner116 native tests와 E2/E2X 및 confirmed review는 수신증거다. 재실행하지 않았다. combined_ft03_rhs는 actual ft03_rhs를 보존하며, RCT는 아직 production stepper에 연결되지 않았다. FT03 underflow rejection이 RCT ordinary products에도 자동 적용된다고 하지 않는다.

## 새 직접 유도

정적 proper volume, 고정 k/Ebar, 다른 반응 없음, source-temperature domain 안의 구간만 가정한다. A=nHI0,B=nHeIII0,xi'=k(A-xi)(B-xi),xi0=0. m=min(A,B),M=max(A,B),d=M-m,phi(x)=-expm1(-x)/x,phi0=1이면

    xi_exact=m*M*k*t*phi(k*d*t)/(1+m*k*t*phi(k*d*t)).
    A=B=m: xi=m*m*k*t/(1+m*k*t).

h=k*dt일 때 backward-Euler의 유일한 물리 root는

    xi_BE=2*h*A*B/[1+h*(A+B)+sqrt(1+2*h*(A+B)+h*h*(A-B)^2)].

F(xi)=xi-h(A-xi)(B-xi)는 [0,m]에서 F'>=1이다. 감소하는 반응률에서 xi_BE<=xi_exact다. isolated RCT에서는 free electrons와 n_tot가 일정하므로 g=(Q-Ebar)*EV_ERG, C_V=1.5*kB*n_tot에 대해 T=T0+g*xi/C_V다. 첫 온도 경계 cap은 heating C_V*(Tmax-T0)/g, cooling C_V*(T0-Tmin)/(-g), g0 infinity이다. 반응물 cap m도 적용한다. 0<cap<m의 정확 도달시간은 log1p[xi*d/(M*(m-xi))]/(k*d), d0이면 xi/[k*m*(m-xi)]다.

합성 A=B=1,k*dt=1,cap=.4에서 BE=.38196601125지만 exact=.5다. T=50000-50000xi,Tmin=30000이면 BE30901.6994 K는 admissible, exact25000 K는 inadmissible이다. BE endpoint 보존/양성/domain이 exact path를 인증하지 않는 반례이며 현행 코드의 버그 판정이 아니다. 실제 source를 domain 밖에서 평가한 결과도 아니다. cap 초과시 extent를 clamp하지 않고 step을 거절하거나 경계시각에서 재시작한다. full FT03의 다른 반응·가변 ne/T는 별도 계약이 필요하다.

## 검증과 다음 작업

새9개 reference tests, symbolic4식, finite8경우가 통과했다. 4개 주 인터페이스의 예상 assertion실패 뒤 동일검사통과를 기록했다. 80/120자리 상대차1.82131146055e-81, 별도5구적의 도달시간 상대잔차1.00538234169e-101, BE 방정식잔차2.09587444461e-100이다. 동일 mpmath backend의 유한-input 검산이지 물리 정확도나 rigorous enclosure가 아니다. 이 루프 Rust0, atomicfit0, cosmologicalhistory0, consumer mutation0, 신규 독립 과학검토0이다.

HE-F3는 실제 REI-F09 결과 대기다. 현 FT03[30000,110000]K와 GM25[200,10000]K의 교집합은 공집합이다. OFF/KF96만으로 common-source campaign 완료를 주장하지 않는다. guard변경/clamp/extrapolation/자동 source전환은 하지 않는다. owner 구현은 RCT-STEP01, mixed photoionization HE-FLRW02B는 별도 pending이다.

전체 Python reference/tests/verifier, 상세 유도와 로그·provenance는 BASS_HE_HEF2C_RCT_STEP_REFERENCE_20261005_v1.zip에 있다. Git에는 결속/수락범위/도메인/요약/동기화/다음지침을 게시한다. 정확 archive/object identity는 DELIVERY_RECEIPT.json을 따른다. 원자 PDF와 원격 전체 archive는 재배포하거나 복원하지 않았다.
