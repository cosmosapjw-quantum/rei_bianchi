# C2 유한 R 결합 수치 감사 — 2026-10-01

**이번 반복의 결론은 `FINITE_R_MAGNITUDE_UNRESOLVED`다.** 계산·독립 비교·검토를 완료했지만, 큰 R의 force 적분과 일부 상태 overlap 적분이 사전 기준을 충족하지 못했다. C2 전체를 닫거나 D1로 넘어가지 않는다. 실패 결과와 동일 상태를 보존하여 다음 적분 개선에서 고유값 계산을 반복하지 않게 했다.

## 실행한 연구

물리적 전하중심 O, ZA=1·ZB=2, 단위 a_A/E_A/hbar를 유지했다. 주 감사 격자는 R={0.25,0.5,1,2,4,8,16}, 상태 연결 격자는 {0.25,0.5,1,2,3,…,16}이다. m=0의 최저 g와 |m|=1의 최저 bright b를 계산했다. 원점 변환 Lbar_O=Lbar_B+R pbar_x/3을 direct derivative로 검증하고, Coulomb 값만 쓰는 force lane을 독립적으로 평가했다.

각 주 격자점에서 base(d7, radial64, angular40, extent30), h(96×60), p(d9), tail(내부64cell 보존·extent40까지16cell 추가)를 실행했다. Hamiltonian quadrature12/14, direct16→24, force20→28을 실행 전에 고정했다. 총39쌍·78개의 prolate 상태와 R=0.5,8의 l72/l96 독립 구면 상태8개(요청 Ritz roots16)를 새로 계산했다. C1b R=2 구면 증거는 재사용했다.

## 수치 결과

| R/a_A | E_g/E_A | E_b/E_A | Lbar_O | Lbar_B | 해당 점의 모든 감사 |
|---:|---:|---:|---:|---:|:---|
| 0.25 | -4.133650926973 | -1.116091599473 | 0.003576493784 | -0.066314664188 | PASS |
| 0.5 | -3.665543943733 | -1.093116322645 | 0.020434211262 | -0.116986046145 | PASS |
| 1 | -3.033352518073 | -1.028312852517 | 0.099673303447 | -0.156319275040 | PASS |
| 2 | -2.512193016590 | -0.899646912168 | 0.340977757757 | -0.090418150352 | PASS |
| 4 | -2.250605387828 | -0.738874455110 | 0.734077805826 | -0.017752809506 | PASS |
| 8 | -2.125034906488 | -0.623178744113 | 1.488449134661 | -0.003932187525 | HOLD: force |
| 16 | -2.062502153613 | -0.562206445735 | 2.980184313553 | -0.000971709834 | HOLD: force |

Lbar=L/(-i hbar)이며 표는 계산된 direct 값이다. 표시 자릿수는 연속공간의 보장 정확도 자릿수가 아니다. R=0.25,0.5,1,2,4의 **다섯 점**이 사전 pointwise 기준을 통과했다. 이 결과는 그 사이 모든 R의 수렴을 뜻하지 않는다.

h/p/tail 변화에 대한 최대 에너지 차이는 6.512e-11, 최대 Lbar_O 차이는 1.966e-12였다. numerical dark의 최대 절댓값은 1.549e-17(기준1e-12)였다. dark는 sin(phi) partner의 32/64점 방위각 적분이며, 새로운 독립 고유상태를 계산한 것은 아니다.

| 독립 비교 R | 최대 에너지 차이 | Lbar_O 차이 | l72→96 결합 변화 |
|---:|---:|---:|---:|
| 0.5 | 5.119e-07 | 7.589e-08 | 9.968e-08 |
| 2 | 2.931e-07 | 1.107e-06 | 1.457e-06 |
| 8 | 2.758e-11 | 4.959e-10 | 1.474e-09 |

세 독립 앵커 모두 사전 기준(독립 에너지/결합1e-5, angular increment2e-6)을 통과했다. R=2는 기존 검증을 재실행하지 않았다.

## 남은 두 적분 문제

1. **Coulomb force 적분.** R=8의 q20→28 변화는 최대5.65e-8, R=16은3.51e-6으로 기준1e-8을 넘었다. R=16의 h 세분화에서 direct–force O 차이는1.36603e-7로 기준1e-7을 넘었다. 같은 R=16 h 상태와 q28을 원래 Python 코드로 평가한 값은 저장된 native 값과8.88e-16 이내로 일치했다. 따라서 해당 실패를 가속 구현의 차이로 설명할 근거는 없다.

현재 Duffy corner의 첫 cell 종횡비는 R=16 base에서54.61, h에서81.92다. 고정 quadrature에서 h 세분화가 오히려 force 적분을 어렵게 만들 수 있다는 구조적 진단이다. 이는 원인에 대한 추론이며 적분 개선이 완료됐다는 증거가 아니다.

2. **공통 O 상태 overlap 적분.** 34개의 인접 sector edge 중 29개가 통과했다. 최소 raw normalized overlap은 0.897384999로0.5보다 크지만, 아래 m=0 edge의 q32→48 변화가1e-7을 넘었다. 해당 지점부터 g의 누적 phase 승인은 None으로 유지했다. 모든 m=1 edge는 통과했다. 계수 내적이나 에너지 정렬로 실패를 덮지 않았다.

| 실패한 g edge | 적분 차수 변화의 최대 차이 | raw overlap |
|---:|---:|---:|
| 11→12 | 1.053068e-07 | 0.931666818 |
| 12→13 | 1.247198e-07 | 0.931686764 |
| 13→14 | 1.457709e-07 | 0.931701229 |
| 14→15 | 1.684598e-07 | 0.931711974 |
| 15→16 | 1.927863e-07 | 0.931720122 |

이 HOLD는 overlap 수치 적분의 미수렴을 뜻하며 실제 branch crossing이 확인됐다는 뜻이 아니다. 실제 phase 연결은 수렴한 overlap에서만 승인한다. rank-five H1s+He n2 cluster는 이번에 검증하지 않았다.

## 속도와 정확도 보존

Fortran real64·OpenMP/SIMD의 고정 순서 합산과 scalar BSpline batch 평가를 적용했다. -O3, no-fast-math, no-FMA contraction을 사용했으며 eigensolver·물리 모형·허용오차·정밀도를 낮추지 않았다. 서로 독립인39개 상태쌍을 OpenMPI rank0+3worker로 실행해122.06초에 완료했다. worker peak RSS 최대716,492KiB, 주소공간 cap1.5GiB였다. 독립 구면 batch는23.71초였다.

| 동일 R=2 보존 상태 평가 | 기존 코드 1회 | native warm 중앙값(3회) | 비율 | 최대 결과 차이 |
|---|---:|---:|---:|---:|
| direct q16 | 2.38368s | 0.25043s | 9.52x | 2.22e-16 |
| force q20 | 3.43807s | 0.40094s | 8.58x | 5.55e-17 |

이 비율은 해당 operator 평가에 한정하며 기존 코드 시간은 단일 표본이다. 전체 연구나 NCP64 scaling의 가속률로 해석하지 않는다. 공통 O overlap 감사는 벡터화한 단일 프로세스에서 483.51초였으며, 남은 계산 병목이다. 다음 적분 개선에서는 독립 edge 적분을 MPI로 분배한 뒤 phase를 R 순서로 연결하는 구성을 적용한다.

현재 호스트는 CPU quota8·메모리8GiB다. 로컬 hwloc binding 제약 때문에 이 실행의 MPI는 unbound였다. 전달한 NCP launcher는 실제 topology/CPU/memory를 검사하고 core binding·no oversubscription·20% 여유 메모리를 유지한다. NCP 64코어 실측은 NOT_RUN이다.

## 해석과 다음 한 단계

A2 scaled 소/대 R 수열을 유한점 진단으로 기록했다. 그림의 점 사이 선은 표시용이며 fitting이나 보간을 acceptance에 사용하지 않았다. 알려지지 않은 Big-O 상수, continuum enclosure, collision 전체 범위, 숨은 교차와 cluster closure는 주장하지 않는다.

다음 단일 의존성은 **C2B_FROZEN_STATE_INTEGRATION_CLOSURE**다. 현재 NPZ/SHA를 그대로 사용해 R=8,16 force와 m=0 R=11→16 overlap의 적분을 해결한다. 고유상태 재계산이나 tolerance 완화가 출발점이 아니다. 자세한 preregistration 요구와 재사용 목록은 NEXT_HANDOFF_KO.md에 있다.

`scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `Eq55=NOT_RUN`, `Eq55_next_node_authorized=false`, production 기본값 변경 미승인을 유지했다. D1·충돌 전파·단면적 계산은 실행하지 않았다.

근거: CONTRACT.json, evidence/GRID_AUDIT.json, evidence/ANCHOR_COMPARISON.json, evidence/CONTINUATION_AUDIT.json, review/*PARITY.json 및 독립 검토. 계약 SHA256: 235bfc84597d4c1ae83106c4ce05c30130f011dee615dd61fe3a9f2fa103c0d4
