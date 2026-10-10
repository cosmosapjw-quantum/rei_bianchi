# FLRW02: 실제 F03 수지 연결과 Q=1 포화 기준계

판정: SOURCE_BOUND_ALGEBRA_AND_MANUFACTURED_REFERENCE_CLOSED__NATIVE_CONSUMER_REGRESSION_BLOCKED.

새 F03의 실제 RHS와 BE residual을 읽고, 국소 반응·광자 수지가 source와 어떤 관계를 갖는지 유도했다. 별도 ranked sharp-phase 기준계에서는 Q=1 이후 초과 광자를 저장량에 남기는 보존형 update를 만들고 독립 해석 reference로 검사했다. 전체 FLRW 소비자나 원자 물리 정확도, native 실행을 승인한 것은 아니다. 기존 F00/F03 fixture와 runtime 반환은 그대로다.

## 실제 source 연결

Source snapshot: c1d7f89c8abc90a6adf971390f2bce7ae7530a23.
- hhe_events.rs blob: 57a63eee1e9d8c4aa2b5ed663dbea15619359f71
- microstep.rs blob: 3a78b40d1823a1e1c8541538bd94481b4cab0277
- thermal.rs blob: d43a09450f2b2ed17f7032d4a3aecc3ff3f5d365
경로는 rust/rei_microphysics/src/ 아래다. Full file content와 metadata를 connector로 읽었다. 원 파일 전체 bytes를 ZIP에 복원한 것은 아니며, ZIP에는 선택 excerpt와 정확한 source identity를 넣었다.

실제 정지 Case-A source에서 dne/dt+sum dNg/dt=sum CI-sum RR다. H 이온만 세는 budget에는 helium photo sink를 남긴다. BE residual r=y1-y0-h*rhs(y1)에 대해 Delta_ne+sum Delta_N-sum CIcount+sum RRcount=w.r, w=(nH,nHe,2nHe,1,1,1)이다. 정확 residual bounds가 주어지면 원 fixture의 per-H 계수는1.471이다. 이는 binary64 norm의 rigorous enclosure나 flow 오차증명이 아니다.

Accepted two-half event는 half1+half2다. 순수 H 제한 반례에서 h/tstar=.01의 full/two-half fraction-lnT 차이는1.62575453e-5<2e-4지만, 최종 endpoint 하나로 사건수를 재구성하면1.64836090e-5/H가 빠진다. 실제 F03는 올바른 합을 사용한다. 이번 반례를 현행 구현의 버그로 판정하지 않았다.

## 포화와 표준 충전율 극한

새 기준계는 X=M(Q)=integral_0^Q Delta(v)dv로 질량과 부피를 구분한다. Uniform 및 앞 절반1.6/뒤 절반.4의 dense-first profile을 사용한다. r(X)=gamma*integral_0^Q Delta(v)^2dv다. Potential absorption k*eta와 손실 ell*eta는 처방이며 실제 opacity·redshift edge를 도출한 값이 아니다.

보존형 BE는 X1-X0=h*k*eta1-h*r(X1)-Lcap, eta1-eta0=h*s-h*(k+ell)*eta1+Lcap, Lcap>=0, Lcap*(1-X1)=0을 만족한다. 양성·유일성과 전체 photon/ion inventory를 유도했다. 단순 Q clipping 반례는0.9/H의 광자를 누락한다. Unsaturated uniform branch, eta0=0, 고정 h에서 k가 무한대로 갈 때 표준 filling equation의 BE update를 복원한다. 이 모델은 실제 spatial front나 post-overlap 물리 closure가 아니다.

적분형 회귀는 Delta_Q-(S_star-R_ref)=-Delta_eta-Z-O+I-Delta_Xi-(R_eff-R_ref)+E_num이다. 실제 같은 stage의 누적 사건을 쓰고, reference recombination은 사전에 고정한다.

## 실행과 한계

기호14식, exact source64점, exact capacity120점(포화44점), invalid capacity input8개 및 narrow unit test1개를 검사했다. 최종 runner4명령 모두 exit0. 여덟 개의 두 상태 이력을 두 개의 독립70자리 초등함수·branch-root reference와 비교했다. Native Rust0, production history0이다.

s=t/tstar, Q0=.1,eta0=.3,k10,gamma.1,ell.2,source1.2(0<=s<3), 이후off, s_end12에서 reference Q는 uniform .93383439697077349, dense-first .46456774649682138이다. Dense-first X=.74330839439491421로 Q와 다르다. Source가 꺼진 후에도 저장된 광자가 재결합을 보충하는 동안 포화한다. 실제 우주론 유지시간의 예측은 아니다.

최대 inventory residual은2.11e-13/H 이하지만 h=.005의 Q오차는 uniform2.41737e-4, dense-first1.63185e-4다. 보존과 시간정확도는 다르며 step halving은1차 수렴을 보였다. 기존 production gate의 통과로 표시하지 않는다.

Container의 직접 다운로드는 DNS 오류, native probe는 rustc 부재로 차단됐다. Connector 읽기는 성공했다. research/run_native_probe.py는 Python 문법만 확인했고 embedded Rust compile/run은 미검증이다. 기존 local repo의 정확한 세 blob을 임시 디렉터리에서 단일 rustc로 실행하도록 준비했다. Cargo 전체 build나 이전 suite replay는 필요하지 않다.

## 동기화·다음 단계

F03의63개 외부 시험 반환은 수신했으며 반복하지 않았다. 연구 중 REC-PB02 문서4ad4080 및 영수증9455c2a를 수신·보존했다. 실제 BE residual은 이제 있지만 F04의 box/root/derivative/remainder는 남아 있다. REC 공급자를 REI가 호출했다는 증거는 아니며 PB02/FT07은 deferred다.

다음은 FLRW03_EXPANDING_ADAPTER_AND_INTEGRATED_BUDGET이다. 실제 density history, emissivity, proper/comoving와 spectral-edge를 연결하고 원 H=0 fixture를 보존한다. Native probe의 실제 결과 전에는 native-verified로 바꾸지 않는다.

## 재현 패키지

REI_CHAT_FLRW02_20261004.zip: 62727 bytes,45 entries.
SHA256: 35e002b6e891e1f168290824dadc531bb6577961b48a51fa84cd84bdd0052b35
Drive: https://drive.google.com/file/d/1ZBiTqjQQeRud4rGUYf-rScnlLd5Uycpk/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW02_20261004.zip
전체 보고서·기계가독 계약·연구 코드·상세 결과·실패 로그·manifest는 ZIP의 rei_chat_flrw02_20261004/ 아래에 있다. 이 repo 폴더는 요약과 전달 계약이며 전체 source archive가 아니다.

기존 strict local<2e-4, public width<2e-3, [160,161] FAIL=2.1245050576368385e-4, tick160 및 physical HOLD를 보존한다. 새 branch, merge, force push는 없다. Backup R1 metadata와 실제 restore는 별개다.
