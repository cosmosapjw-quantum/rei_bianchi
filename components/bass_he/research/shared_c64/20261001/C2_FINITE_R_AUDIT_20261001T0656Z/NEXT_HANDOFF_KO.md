# 다음 단일 의존성: C2B_FROZEN_STATE_INTEGRATION_CLOSURE

C2a STOP은 FINITE_R_MAGNITUDE_UNRESOLVED다. DIRECT_COMMUTATOR_MISMATCH와 STATE_TRACKING_AMBIGUOUS가 각각 force·overlap 수치 적분에서 남았다. C2 closed=false이며 D1으로 진행하지 않는다. 기존 CODE_I02 closure와 scientific_PROMOTE=HOLD, Eq55=NOT_RUN, full certificate fail-closed, production 기본값 미승인을 유지한다.

## 그대로 재사용할 상태와 성공한 증거

- 과학 격자 R={0.25,0.5,1,2,4,8,16}, continuation 격자18점의39개 prolate 쌍은 evidence/PROLATE_MPI/*/STATE.npz에 있다. 인접 RESULT.json의 state_bytes/state_sha256을 확인한 뒤 로드한다.
- R=0.25,0.5,1,2,4의 pointwise h/p/tail/direct/force/dark/norm/residual 기준은 통과했다. 다섯 점을 연속 구간의 증명으로 바꾸지 않는다.
- 독립 구면 앵커 R=0.5,2,8은 통과했다. R2는 C1b 재사용이다. 새 eigensolve 없이 coefficient와 operator 증거를 재사용한다.
- 모든 m1 overlap edge와 m0의0.25→11 연결은 이번 quadrature 기준에서 통과했다. m0 R11→12부터 누적 phase 승인은 보류다.
- native와 원래 Python force의 R16_h q28 parity는8.88e-16이다. 단순 native 구현 오류를 가정하여 증거 없이 solver를 바꾸지 않는다.

## 다음 bounded contract를 먼저 고정할 항목

새 고유상태 예산의 기본값은0이다. frozen-state 적분만으로 두 문제를 분리할 수 있다. 정확한 R/configuration/edge 목록, order sequence 또는 변환 분할, 최대 평가 수·wall/RSS, acceptance와 stop을 새 계약에 기록한 뒤 실행한다. 이번 계약의1e-8 force quadrature,1e-7 direct-force 및 overlap 기준을 느슨하게 하지 않는다. 새 기준이 필요하면 명시적인 과학적 이유를 분리하며 기존 실패를 소급 PASS로 바꾸지 않는다.

1. Force: R8 및 R16의 base/h/p/tail 상태를 고정한다. 우선 가장 나쁜 R16_h를 진단하고 기존 q28 값을 보존한다. 첫 corner의 anisotropic Duffy 비율54.61→81.92와 잔여 denominator 경계를 분석한다. Coulomb 거리와 맞춘 좌표/분할 또는 사전 고정된 더 높은 quadrature 수열을 시험하되 direct lane과 독립인 force 값 적분을 유지한다. 최소 두 refinement의 증가량과 direct-force 기준을 각각 확인한다. 비용 절약을 위해 통과한 eigensolve·h/p/tail 계산을 반복하지 않는다.

2. Common-O overlap: m0 edges11→12,12→13,13→14,14→15,15→16을 고정한다. q32→48 변화는1.05e-7부터1.93e-7이며 magnitude는약0.932다. 이것은 branch switching 증거가 아니다. 서로 다른 R의 Coulomb cusp가 적분 좌표의 다른 위치로 이동하는 점과 양방향 적분 차이를 진단한다. 알려진 핵 위치로 physical domain을 분할하는 적분 또는 사전 고정 refinement로 selfnorm, 양방향 일치, 차수 증가를 함께 검사한다. 검증 후에만 실제 phase 연결을 복구한다.

독립 force 상태와 overlap edge 적분을 OpenMPI로 병렬 분배하고, phase 연결은 완료 순서와 무관하게 R 순서로 실행한다. Fortran real64/OpenMP/SIMD와 scalar BSpline batch 경로, no-fast-math, compiler/binary/source SHA, 주소공간·wall cap, create-only 원자 저장을 유지한다. 참조 lane과 native 비교는 변화한 변환/연산자에 한정한다. NCP 실제 topology와 quota를 먼저 확인하며 NCP64 scaling은 실행 증거 없이는 NOT_RUN이다.

## 이 적분 문제가 닫힌 뒤에도 남는 C2 범위

이번 자료만으로 collision-relevant 전체 범위, hidden-crossing 구간의 adaptive R 검증, rank-five H1s+He n2 cluster, continuum error enclosure, 소/대 R scaled 극한은 닫히지 않는다. 우선 이번 두 적분 의존성을 해결한 후 다음 하나를 선택한다. 그 전에는 D1, collision, cross section, Eq55, benchmark fitting을 실행하지 않는다.

공개 코드·선별 증거와 전체 archive의 범위는 README.md에 구분했다. provider upload ACK와 size 확인은 restore 검증이 아니며, 다음 세션에서 필요한 파일만 identity를 확인해 재사용한다.
