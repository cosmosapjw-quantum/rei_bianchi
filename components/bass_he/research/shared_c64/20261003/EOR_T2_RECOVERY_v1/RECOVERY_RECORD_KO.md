# BASS_HE EOR_T2 중단 복구 기록

날짜: 2026-10-03 KST. 원 T2 파일의 20261002 표기는 유지한다.

## 판정

RECOVERY_COMPLETE__T2_REFERENCE_REPLAY_VERIFIED__PHYSICAL_GATES_UNCHANGED.

원 EOR_T2 scientific verdict는 CONDITIONAL_DYNAMICAL_ERROR_CONTRACT_AND_REFERENCE_KERNELS_READY다. 마지막 응답 실패에도 T2 ZIP, 보고서, DAG는 Library에 저장되어 있었다. 실제 bytes를 회수해 검증했으며 transcript-only 완료를 상속하지 않았다. 이번 복구에서 원 이론과 제품 코드는 변경하지 않았다.

## 고정 archive

원본: BASS_HE_EOR_T2_COHERENT_CONTRACT_20261002_v1.zip
bytes: 1789941
SHA256: df77a6c4c572e79c3f28a8cb4e26be6c1dbee9f7fbbf84b8307eb3d8ba83e5bb
검사: ZIP CRC, 51개 manifest payload, 부모 T1의 50개 payload, 원 DAG 16개 node.

복구 묶음: BASS_HE_EOR_T2_RECOVERY_20261003_v1.zip
bytes: 1845443
SHA256: 10669704b978cbf0b9027d4b41c8219b34c7260bed3c4b1c7156e0a8bee631e5
검사: 33개 ZIP entry, 32개 manifest payload. 원 T2 archive를 같은 bytes로 포함한다.

## 원문 근거 보완

A1b의 A1B_CHANNEL_EMBEDDING_DERIVATION_KO.md 26157 bytes를 실제 회수했다.
SHA256: 99e97891c6c7a52e24a8dcabbf70afc00a2525701a6fa4d4e1438886de5dea05
Git blob: 48c25526647733d9392ad781f51eca70fe29547b
고정 commit: 771b1fe1b70930196a0f812bdb118bec04049c8c

원 T2에 기록된 hash와 새 GitHub read의 blob이 일치한다. 이 문서의 raw recovery만 보완한 것이며 A1b 전체 archive 또는 독립 심사를 다시 수행한 것은 아니다. 원 T2의 미복구 기록은 삭제하지 않고 recovery addendum으로 보존한다.

## T2 수학적 결과와 한계

A1/A1b의 moving metric, ETF와 정확한 P/Q memory는 계승한 정식화다. 비직교 S=X†X에서 iℏS cdot=(h−iℏD)c, Sdot=D+D†를 유지한다. 서로 다른 spatial ETF는 일반적으로 동일-span gauge가 아니다.

T2는 isometry Y와 operator-domain 조건 아래 F=HY−iℏYdot, K=Y†F, B=(I−YY†)F, d=iℏadot_h−Ka_h에 대해 lifted residual r=Yd−Ba_h 및 ||r||²=||d||²+||Ba_h||²를 오차전달 계약으로 연결한다. Unitariy full propagator 아래 초기오차에 ℏ⁻¹∫||r||dt를 더하는 조건부 상한이다.

raw H¹ FEM은 별도 weak dual-residual 경로를 사용한다. 필요한 regularity와 energy-norm majorant가 있을 때 무차원 form norm에서 e²(T)≤e0²+2∫(G_exact+G_approx)ηdτ다. 실제 Coulomb norm upper bound를 계산한 것은 아니다.

정적 projector 거리만으로 time-derivative connection을 제한할 수 없고 initial Q=0이어도 memory가 남는다. Q norm 또는 잘린 채널의 norm loss를 물리 ionization으로 합산하지 않는다. 같은 residual 안에 포함된 기저/Q/time 오차는 중복 합산하지 않는다.

## 새 환경 재현

Python3.13.5, NumPy2.3.5, SciPy1.17.0, pytest9.0.2. 실제 CPU quota4 cores, affinity5 logical CPUs, memory4GiB. NCP64 성능 주장은 없다.

원 focused tests: 48 passed, exit0. 원 시험의 28개 test-first와 20개 tests-after 구분을 유지한다.
6개 4×4 Hermitian manufactured systems의 최대값:
- residual 분해 차이: 9.305364597889227e-16
- 직교 제곱합 결손: 1.1102230246251565e-15
- Gamma Y−Ydot: 2.105814259841454e-16
- 32점 memory integral identity: 9.602787394150765e-16
- 비직교 coefficient ODE와 physical expm 차이: 3.089781295685785e-12
- 같은 ODE norm 결손: 4.480860127387132e-13

Memory 검사는 exact full a(s)를 입력한 적분 identity이며 독립 Volterra solve가 아니다. 두 manufactured CLI는 exit0과 physical_certificate=false, matrix-only 요청과 같은 output 덮어쓰기는 exit2였다. 실행 전후 원 manifest가 동일하게 통과했다.

새 molecular solve, physical cross section/rate, cosmological history, Fortran build, MPI, 독립 심사는 모두 NOT_RUN이다. binary64/no-fast-math/no-reassociation/explicit backend 정책과 기존 native code를 유지했다.

## gate와 다음 작업

C0 physical_ready=false; EOR_THEORY_GATE=NOT_SATISFIED; independent_review=NOT_RUN; scientific_PROMOTE=HOLD; full_C2_closed=false; continuum_certificate=false; full_H_gap_certificate=false; atomic_correlation_established=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

다음 단일 node: EOR_T3_IN_DOMAIN_TRAJECTORY_CHANNEL_CONTINUUM_AND_TAIL_CONTRACT. 첫 제한 단위는 nuclear-motion model의 적용조건과 bound/continuum/return/time·impact·energy tail의 오차 소유권을 명시적으로 결속하는 것이다. 미확정 physical input은 매개변수로 유지한다. R_CX는 별도 provider를 요구하며 비방사 Hamiltonian으로 생성하지 않는다. 이번 복구에서 T3 science를 실행하지 않았다.

## 배포 범위

이 commit은 additive 공개 복구·이론범위·검증·archive identity 기록이다. 전체 product code를 개별 Git 파일로 게시한 것은 아니다. 완전한 실행 코드와 실패/검증 근거는 원 T2 ZIP과 이를 포함한 새 복구 ZIP에 있다. 복구 ZIP은 승인된 Drive/Dropbox/Library에 저장했고 두 클라우드에서 ACK/object ID/size를 확인했다. 새 Drive/Dropbox restore는 미실행이다. Library 원 T2는 실제 materialization/hash 검사 후 재현했다. 최종 commit/tree 및 private provider IDs는 별도 detached delivery receipt가 소유한다.
