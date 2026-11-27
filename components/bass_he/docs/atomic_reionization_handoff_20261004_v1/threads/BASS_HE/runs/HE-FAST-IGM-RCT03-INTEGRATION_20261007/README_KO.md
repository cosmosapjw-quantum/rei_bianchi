# HE-FAST-IGM-RCT03A: 실제 receiver 연결과 시간정확도 실패

전체 판정은 PARTIAL_TEMPORAL_ACCURACY다. 현재 receiver39c39eab의 원 src tree d4209210(35개 source+Cargo2)를 바이트로 복원한 로컬 사본에 RCT를 연결했다. 새12native시험은 통과했지만 21개 backward-Euler 이력은 모두 원래 고차기준 시간정확도 조건에서 실패했다. 구현·장부 PASS와 연속시간 정확도 FAIL을 분리한다. 원격 receiver/root/기본OFF는 변경하지 않았다.

## 실제 변경

src/igm_step.rs와 src/lib.rs 두 파일 변경, 기존 point bridge를 내부 경로로 옮긴 src/igm_rct_point.rs와 새 tests/rct03.rs, examples/rct03_history.rs 세 파일 추가다. Point 식은 crate-path 변환과 같은 rustfmt를 거친 결과가 기존 코드와 byte-identical이다. 기존 positive 후보에 I_H+=k*nHe*z_guess, HeIII loss+=k*nH*(1-x_guess)를 추가하고 thermal root·endpoint·residual·에너지/광자 장부를 같은 selected RHS에 결속했다. 최종 endpoint의 RCT는 별도 sidecar이며 사건수dt*R/nH_endpoint를 반환한다. 전자밀도를 추가로 곱하거나 초기 nH0로 나누지 않는다.

OFF는 기존 API에 직접 위임하고 기존 result layout/source/masks/cache/수치budget을 보존한다. Active common EOS [1000,10000]K의 bracket은 원 energy-space root 구성 방식을 유지하며 입력/해 clipping은 없다. Direct electron source0, chemical=-QR, heat=(Q-Ebar)R, escape=EbarR, retained photons0은 explicit escape다. 실제 원자모멘트는 null이다.

## 실행 결과와 실패

원본upstream과 patched library에 동일한 별도 client를 빌드했다. OFF12경우는9정상결과의171개floatbits와 반복수,3동일 IGM_STEP_ENERGY_LEDGER 오류가 일치한다. 작은dt1e8/T2000 photon 실패는 원래OFF도 거절하며 이번 patch에서 숨기지 않는다. 같은packet dt1e12에서는 local energy/owner 검사를 통과한다. 해당 실패를 성공으로 대체하지 않고 명시적 rejection test로 보존했다. Photon/source history는 미검증이다.

주이력은 RCT02와 같은 H3e-18/s,nH0=1e-4cm^-3,fHe.083,Tcmb0=20K,IC(.1,.05,.9),T0=2000K,0..1e15s,source/initialphoton0이다. OFF와 KF96/GM25의30/35/Q eV를 N100/400/1600으로 실행했다. 총21history/14700BE step,101epochs이며 background는각끝점이다. 원23고차reference는 재실행하지 않았다.

전체 max nonlinear residual9.98746319487e-16, species ledger5.94142790522e-16, energy scaled3.68548458288e-15다. 원 global1e-10 장부는 통과하지만 state1e-9+1e-8max,T1e-5K+1e-8max,J1e-12+1e-7max의 원 시간정확도 조건은21개 모두FAIL이다.

GM30 N100/400/1600의 T최대오차는 .02050535624/.00513302530/.00128367494K, J오차는8.37539204e-7/2.09603419e-7/5.24145406e-8events/H다. N1600 상태허용량비3625.49495(HeII),T42.7219,J540.3762다. T/J의 관측차수는 약1이다. OFF도N1600상태비3140.0617로실패한다. 작은 비선형 잔차는 BE의 -h^2(F_t+DF F)/2 국소 시간결함을 제거하지 않는다.

## 다음과 전달

기존 receiver 연결을 다시 쓰지 않고 이 실제 patch를 재사용한다. 다음은 RCT03B_TEMPORAL_METHOD_AND_BUDGET_CLOSEOUT이며 동일 bounded source-free case에서 기존 owner의 고차/오차제어 경로와 same-stage RCT를 결속한다. 무조건적 수백만 BE step sweep이나 허용치 완화는 하지 않는다. 기존 midpoint prototype의 partial 상태를 자동 승격하지 않는다.

전체 원본/staged source, 시험, exact-base 적용검사를 마친 RECEIVER_INTEGRATION.patch, 21output, 원 reference와 모든 실패/성공 로그는 DELIVERY_RECEIPT의 ZIP에 있다. Git은 이 요약·반환·입력·patch identity를 보존하며 전체 source가 Git projection에 있다고 주장하지 않는다. Independent scientific review/interval 인증은 NOT_RUN, physical HOLD, HE-F2 globalfalse, HE-F3/F09 미완료다. Owner source 예약과 baseline OFF는 유지한다.
