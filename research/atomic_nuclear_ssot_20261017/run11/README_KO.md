# RUN11: 실제 BASS 첫 스펙트럼 셀의 native 연결과 공동해

2026-10-18 KST. RUN10의 미완료 단계 `P4-S4C-SPECTRAL-EDGE-SUPPORT/NATIVE-INTEGRATION`을 수행했다. Parent는 831d798a94cd2462eb1eb047c5172ce24d983a58다. 이 브랜치는 add-only 연구 기록이며 기존 main·production·원자 owner·이전 checkpoint는 변경하지 않았다. 사용자 local/Codex/NCP/SSH 및 별도 native subagent는 실행하지 않았다.

## 실제 복구와 구현

RUN09 ZIP SHA256 039fbce620bfa90e43822727d01cb8a2734fbfa78ef894673c7de9a06aa16029와 204개 payload를 재검증했다. RUN10 후보 원본은 게시 Git blob 2f9ae1fc86331901b62b61546618153cb6dd0673와 일치한다. 과거 미실행 기록을 소급해서 PASS로 바꾸지 않는다.

처음 실행한 후보 Rust 시험은 6개 중 4개 통과, 2개 MomentConvergence 실패였다. 3차 모멘트의 successive Simpson 변화가 512→1024에서 7.263378512481126e-13 M0로 고정 기준 5e-13 M0를 넘었고, 1024→2048에서는 4.539537806710278e-14 M0로 낮아졌다. 최대 분할 2048만 추가하고 허용오차는 유지했다. 후보 6개와 실제 adapter 3개를 포함해 최종 native 160/160, Python 새 3개와 기존 retarded 8개, strict Clippy와 신규 파일 rustfmt가 통과했다. 핵심 adapter의 red→green, 최초 실패·API 오독·Clippy 로그도 보존했다.

원자 owner 12개를 포함한 기존 Rust 83개, 입력 13개, 기존 retarded/gas Python 2개는 byte-identical이다. lib.rs는 exact prefix 뒤에 두 모듈 선언만 추가했다. 실제 Rust의 고정 응답을 RUN10 MP55와 비교한 relative-error 값의 최대 차이는 3.89372e-15였다. 실제 연속 평균과 기존 Simpson32 평균 차이는 -3.44436e-12 eV다. 같은 원자 입력에 대한 구현·정밀도 대조이며 독립 원자자료 검증이 아니다. Wolfram Jacobi moment 0..3 항등식의 네 잔차는 0이었다.

## 동일 입력과 문턱 처리

BASS121 SIGNED_MINUS의 실제 prescribed Einstein–Vlasov 기하, X=ln(a/a_ref), a_ref=1/21, X=.7.. .7004를 사용한다. MD14/BB50k fesc=.2, 160개 출생시각, GL8 방향, Grackle/Verner/Savin/DAtomicProvider는 유지했다. T10000K, HII=DII=.1, He4(.8,.15,.05), D/H2.5e-5, YHe=.245, D 결합차이 .0037eV는 기존 제조 초기조건이다. 외부 CMB bath는 2.7255/aK다. REC 초기조건, 정밀 동위원소 분광자료, 새 gas/photon stress에 따른 Einstein feedback은 도입하지 않았다.

첫 셀 [13.6,14.112863291954786]eV만 세분했다. H binding13.598434599702, H fit edge13.6, D edge13.602134599702eV를 구별했다. D 단면적은 기존 threshold-gated H-equality다. 다른 47셀의 tuple과 출생시각은 동일하다. 조건부 양의 Gauss2 가중치로 부모 광자수를 배분하며 사후 정규화·clipping·tailcut은 없다.

단조감소 ray E=R Eb에 대해 문턱 epsilon의 교차 구간 epsilon<Eb<epsilon/eta를 사용했다. eta는 각 실제 native Killing ray에서 계산했고 기존 H>0,-1/2<b_X<1 구간 검사를 재사용했다. 제조 FLRW eta를 대신 넣지 않았다. baseline 61440→m1 70400 physical cohorts, 정확한 ±mu 쌍 집계 후 m1은 35237 ODE다. H1520+D1520=3040 paired 교차, 전체 3200 적분 구간이 생겼다. 물리적 ±mu 중복까지 세면 6080교차다. 최대 root 에너지 잔차는 1.77636e-15eV다.

모든 출생·교차 분할점을 유지하면서 열린 구간의 활성 branch를 양 끝점에 한쪽으로 연장했다. 이는 endpoint 문턱 판정에 따른 반복 step 축소를 줄이는 표현이며, 유한 개 끝점의 값은 적분방정식의 해를 바꾸지 않는다. 구간 내부 문턱을 제거하거나 에너지를 clip하지 않았다. 원래 native provider는 변경하지 않았다. 새 구간별 함수는 기존 fit과 내부 구간에서 일치하는 시험을 통과했다.

## 완료된 공동해

세 설정을 완료했다: baseline m0 DOP853(3e-11), m1 DOP853(3e-11), m1 DOP853(6e-12). 새로운 Radau 대조는 없으며 m1의 두 실행은 같은 알고리즘·RHS를 공유한다. m2 입력(80640코호트,40357ODE,6080paired교차)은 생성했지만 공동 적분은 NOT_RUN이다.

| 양 | baseline | m1 | (m1-baseline)/m1 |
|---|---:|---:|---:|
| T [K] | 9994.351244575617 | 9994.351243209323 | -1.3670661e-10 |
| 생존수 [comoving m^-3] | 5.107749173338790e-7 | 5.107816939964918e-7 | +1.326723861e-5 |
| H I 누적 흡수 | 5.552147926285805e-5 | 5.552147290119659e-5 | -1.145801999e-7 |
| He I 누적 흡수 | 4.024414265997353e-6 | 4.024414265958554e-6 | -9.64095359e-12 |
| He II 누적 흡수 | 3.395099851107722e-9 | 3.395099851083037e-9 | -7.27093520e-12 |
| D I 누적 흡수 | 1.386737268344058e-9 | 1.386321851859872e-9 | -2.996537086e-4 |

온도 절대 변화는 -1.366293873e-6K, 생존수는 +0.00132672%, D I 흡수는 -0.0299654%다. 문턱과 셀 내부 곡률을 함께 반영하므로 변화 전체를 D 교차 하나의 효과로 분류하지 않는다. 이는 유한 스펙트럼 표본 민감도이지 continuum 오차가 아니다. 작은 He 변화는 solver 민감도와 비슷해 물리 신호로 승격하지 않는다.

m1 허용오차 5배 강화에 따른 차이는 T +1.091393642e-11K, 생존수 -2.694749157e-15 상대, H I -1.281011810e-11 상대, D I -1.277536243e-11 상대다. m2 endpoint가 없어 spectral convergence는 HOLD다. 최대 photon ledger 2.29007e-11, energy/source 1.64462e-11이며 엄격 m1에서는 3.49647e-12/3.62333e-12다. 회계 잔차는 상태 정확도의 대용이 아니다. 첫 셀 ray별 count 잔차 최대 5.55112e-16, 원래 평균에너지 대비 이동 최대 3.44791e-12eV였다.

완료 구간의 적분 내부 wall 합은 295.225379334s다. 초기 진단·outer45s 중단의 미저장 부분·설치·모델 준비·checkpoint 쓰기·시험·복원·게시는 제외한다. 측정된 process 최대 RSS는 1364524KiB, 약1.30GiB다. 20~22초마다 사건 경계에서 세대별 state와 SHA를 저장하고 metadata를 commit한다. 두 chunk를 한 외부 호출에 묶어 중단한 시도는 부분 기록으로 분리했다.

## 복원·저장·재개

Full ZIP: REI_ATOMIC_NUCLEAR_RUN11_NATIVE_SPECTRAL_20261018.zip,17968344bytes,203entries,202payload hashes.
SHA256 cd9258a2b7ca6fee8f82155d4fa2bc016ac5d05a25b061f8fcf74db3c3e2d0a8.
새 디렉터리에서 202해시,160Rust+11Python,Clippy와 초기상태 baseline을 재실행해30757 endpoint 값의 binary64 exact equality를 확인했다. 엄격 m1은 저장된3012→3200의188구간을 재실행해35237 endpoint의 exact equality를 확인했다. 이는 refined tail 복원이며 전체 m1 초기상태 재실행은 아니다.

REI_RUN11_CORE_CODE.tar.xz에는 실제 새 소스·시험·exporter·replay 9파일이 있다. 12016bytes, SHA2566b106094db407d180112c3825adeb1f7dbb0866515941915b73f4338f4dc79ec, Gitblob62010c61beadca1e0b2090df508bcc480ab81731. RUN09 전체 소스와 lib.rs의 pub mod spectral_edge_support; pub mod spectral_native; 선언이 필요하다. 단독 full Git checkout이나 미완료 RUN06 Git backfill은 아니다. Full ZIP에는 완전한 실행 코드·입력·결과·실패·부모 RUN09·RUN10 텍스트가 있다.

Drive: https://drive.google.com/file/d/1RToO5ldCU_A9KB3OX2hjIjroIk_oSNSL/view?usp=drivesdk . 업로드 완료 후 인증된 전체 반환 파일 file_00000000bbd881fa9df987911b86afce의 SHA256가 원본과 일치했다.
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN11_NATIVE_SPECTRAL_20261018.zip, id:BSpOijBcT10AAAAAAD-68Q. 업로드 완료, provider content hash07132efb7c4bb69b1f05714c662ae7cf34cc7efe4ac75f315c1a0fb30cca04b3가 로컬 계산과 일치했다. 이번 raw 다운로드 호출은 runtime URL gate에서 차단됐으며, 전체 바이트 다운로드/복원 성공으로 세지 않는다.

판정: PASS_SCOPED_NATIVE_SWEPT_FIRST_CELL_JOINT_ENDPOINT_NO_SPECTRAL_CONTINUUM_BOUND.
다음: P4-S4C-SPECTRAL-EDGE-SUPPORT/M2-CONVERGENCE. 이미 생성된 동일 m2 입력을 개별 사건 checkpoint 호출로 적분하고 m1/m2 차이를 비교한다. 연속 스펙트럼·각도·출생의 엄밀 상계, 전체 donor, fullEoR, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Einstein feedback과 미완료 Li/Be/nuclearT1–T8는 HOLD다. 원래45/26DAG는 부모 archive에 보존했다. 외부 Rust1.94.1이 필요하며 toolchain/target/font/credential은 배포하지 않는다.

문헌 배경은 NIST DLMF3.5, SciPy1.17.0 solve_ivp 공식 문서, Mirocha etal2012 arXiv1204.1944, PawlikSchaye arXiv1008.1071이다. 문헌은 이번 수치값·독창성·실제 실행을 대신 인증하지 않는다.
