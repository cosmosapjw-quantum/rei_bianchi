# BASS_HE C2h1 — 외부 sector 하한과 general-m 구현

판정: C2H1_STATIC_EXTERIOR_BOUND_AND_GENERAL_M_IMPLEMENTATION_COMPLETE__MOLECULAR_PILOT_NOT_RUN.

C2g 실제 archive를 회수한 뒤 C2h의 첫 bounded substep을 수학 유도, 코드 확장, analytic/manufactured 시험 및 review-gated 외부-runtime 패키지까지 완료했다. 독립 심사와 새 R=4/4.25 분자 pilot는 수행하지 않았다. 전체 C2h/C2는 OPEN이다.

## 회수 identity
부모 commit: 327ecb934d858deca2e34e263891209ae221d890
부모 tree: 08bd6fc6ef5d97617cdd441b38e6067a35658d45
첨부 C2g ZIP: 6756037 bytes, SHA256 e702446b097522f0c06e96ac0a2c90556b55527c523e0e26dfda4fce8cd6fd47.
168개 파일 inventory 및 parent final review가 묶은 13개 evidence의 실제 size/hash를 확인했고, 종료 시 부모 168개 파일의 불변성을 재확인했다. 기존 첫 MPI 실패와 성공 retry를 구분하여 보존했다. 원 연구 prompt와 원 논문 전체를 이번 단위에서 새로 회수했다고 주장하지 않으며 source-bound parent DAG를 계승했다. 종료 후 steward prompt의 조건부 활성화는 아직 성립하지 않는다.

## 자체 유도
정지한 핵들이 같은 z축에 있고 T=-Delta/2, 비음수 Coulomb 전하, 무스핀/무자기장 scalar H를 가정한다. Q=sum Zi, wi=Zi/Q이면

H = sum_i wi (T-Q/ri).

z축 평행이동은 m을 보존한다. 단일 원자에서 l>=|m|이고

D_l = d/dr-(l+1)/r+Q/(l+1),
h_l + Q^2/[2(l+1)^2] = D_l^dagger D_l/2 >= 0.

따라서 H restricted to direct-sum |m|>=M >= -Q^2/[2(M+1)^2]. ZA=1,ZB=2,M=2이면 모든 |m|>=2에 -0.5 E_A 하한이다. R과 무관하고 R=0에서 포화한다. 유한 m 계산을 무한 m로 외삽한 결론이 아니다. 무한공간 form 부등식이며 Dirichlet ball에는 H1 zero-extension으로 상속된다. 회전/ETF/trajectory 항까지 포괄하는 정리가 아니다. 최초 발견이나 독립 심사 통과를 주장하지 않는다.

C2g fine selected 최대 Ritz 에너지와 nominal 여유:

| R/a_A | selected 최대 E/E_A | -0.5 대비 nominal 여유/E_A |
|---|---:|---:|
|4.00|-0.6807548935849548|0.1807548935849548|
|4.25|-0.6728107014160001|0.1728107014160001|

ordinary-quadrature Ritz 수치는 인증된 참 고유값 상한이 아니다. 따라서 이 nominal 여유를 full-H gap certificate로 승격하지 않는다. selected 참 오차, 같은 m의 미반환 근, 독립 selected-state discretization, observable/continuum enclosure와 collision-domain coverage가 남는다.

## 실제 구현과 검증
부모 대비 변경 diff를 PARENT_TO_C2H1_CODE.patch에 게시한다. angular/solve_many general-m, archive writer v2 및 부모 v1 m0/1 reader, 같은 O/box의 positive physical-L2 embedding, explicit +/-m partners를 지원한다. rank5 선택은 그대로 두고 새 m>=2는 guard만 추가한다. 기존 Fortran 원소 kernel은 수정하지 않았다.

최종 focused suite: 81 passed, 12 subtests passed (0.95초 단회). general-m 행동의 red->green을 실제 관측했다. bound/runtime 시험은 구현 후 작성했으며 전부 TDD라고 부르지 않는다. R=0 analytic atom m0..3 및 실제 m2 distinct roots를 시험했다. 새 R4/4.25 분자 task는 0개다.

strict Fortran 제조행렬 m2/3/4의 최대 NumPy 차이 1.4210854715202004e-14; OMP1/2 행렬 bytes 동일. R0 m2 native-reference maxDeltaE=2.220446049250313e-14 E_A, native matrix residual 최대 7.742950753956279e-13. 실제 CPU quota4/메모리4GiB host, gfortran14.2.0, Python3.13.5/NumPy2.3.5/SciPy1.17.0. OpenMPI/mpi4py 미설치로 MPI positive end-to-end는 NOT_RUN. local OMP probe는 core binding을 강제하지 않았으며 NCP 실행 환경이나 scaling으로 해석하지 않는다.

## 외부 실행 계약
각 R=4,4.25에서 m2 두 근: base lmax28/실제42radial cells, angular-only lmax36/동일 knots, radial-only lmax28/기존 knots를 보존한84cells. degree4/quad14/box20/centerO/tol1e-11/maxiter2000. NumPy1x1 및 strict Fortran/OpenMPI2x1, 각6tasks/12roots, wall300s 및 sampled owned RSS3GiB watchdog. 한 축만 바꾼 energy difference5e-4 E_A/projector5e-3은 empirical STOP 기준이고 엄밀 오차 상한이 아니다.

독립 review의 실제 SHA와 source/contract binding이 없으면 callback 전에 차단한다. 이 차단은 실제 CLI로 exit2/BLOCKED_PRELAUNCH/0launches를 확인했다. 런타임은 실패 후 자동 재시도하지 않는다. binary64/no-fast-math/no-reassociation/no-hidden-fallback을 유지한다. reviewer attestation은 암호학적 reviewer identity 인증 장치가 아니다.

## 배포 범위와 다음 node
이 공개 namespace에는 보고서, 수학적 근거, 코드 diff, exact-bound kernel, 기계판독 상태와 archive identity를 게시한다. 완전한 14개 source module, 모든 시험/실행기/분석기/계약/4개 참조 NPZ/결과/전체 DAG는 76-file ZIP에 있다. 전체 runtime source를 개별 Git 파일로 게시했다고 주장하지 않는다.

Archive: BASS_HE_C2H1_EXTERIOR_GUARD_20261002_v1.zip
Bytes: 1540292
SHA256: d4f7d6a180b53c172eb7a599ed9a00dafdb10fd94fca950f051481e179a3cc39
Package binding SHA256: ede6b35dc278d9150a509d87c434b4b3434fd22e98d9f4a9afd271379be1ee53
Physical contract SHA256: 93dedbcd2a296f87618a07b90091e01319772bfdc5a432d7c9cc924e4f42b051

Drive archive object 1moPiSxyIwe5D6TdMQ3D1vszhcQqUpm1D 및 Dropbox id:BSpOijBcT10AAAAAADxkIA의 저장 성공/size1540292를 확인했다. Library archive libfile_c51eb7e949b081918553c4cd8783238f에도 저장했다. Cloud restore는 수행하지 않았다. 전체 package의 handoff/EXTERNAL_RUNTIME_HANDOFF_KO.md가 실행/반환 계약이다.

다음 단일 실행 node: C2H1_INDEPENDENT_REVIEW_AND_REGISTERED_EXTERIOR_PILOT. 그 반환 이후 scientific priority는 C2H2_INDEPENDENT_SELECTED_STATE_DISCRETIZATION_AND_TRUE_ERROR_AUDIT. 부모 A/B/D-G dependency를 삭제하지 않는다. scientific_PROMOTE=HOLD, full_C2_closed/continuum_certificate/full_H_gap_certificate/atomic_correlation_established=false, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED.
