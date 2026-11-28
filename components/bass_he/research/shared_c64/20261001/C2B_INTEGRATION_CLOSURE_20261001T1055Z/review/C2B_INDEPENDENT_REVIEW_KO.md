# C2b 독립 검토

판정은 `ACCEPT_SCOPED_CLOSURE_WITH_RECORDED_EXECUTION_DEVIATION`이다. 고정된 파동함수에 대한 두 적분 문제의 경험적 수렴은 승인한다. 초기 자원 preflight를 무시한 실행은 절차적으로 부적합하며, 그 사실을 보존한 수치 증거 회수와 1-worker 재개를 별도로 인정한다. 전체 C2, 연속 R 구간, rank-five cluster, continuum 오차 인증이나 production 승인은 이 판정에 포함되지 않는다.

검토자는 solver·force·overlap·Fortran kernel의 구현자가 아니며, 분자 상태의 새로운 적분이나 eigensolve를 수행하지 않았다. 구현 식과 영역 분할을 독립적으로 읽고, 저장된 결과의 scalar gate와 identity를 별도 Python 코드로 재계산했다. 재현 코드는 `C2B_INDEPENDENT_REVIEW_CHECK.py`, 상세 수치·파일 identity는 `C2B_INDEPENDENT_REVIEW_SCALARS.json`에 있다.

## 수학과 구현

Force는 원래의 값-only 적분 T_A,T_B 및 ΔE를 통한 L_O,L_B 관계를 보존한다. 핵 근처 a=xi−1, b=1∓eta에서 r=c(a+b)이고 적분함수의 핵심 구조가 ab/(a+b)²가 됨을 확인했다. 긴 셀을 기하만으로 이등분하는 방식은 원래 spline 셀을 빠짐없이 분할한다. 실제 Coulomb 모서리의 두 Duffy 삼각형은 올바른 양의 Jacobian을 사용한다. 새로운 상태, 근사 물리, 적합 계수나 허용오차 변경은 들어가지 않는다.

Overlap에서는 s=sqrt(xi²−1), theta=acos(eta)이고, 양의 물리 measure는

    (R³/8) (s²+sin²(theta)) (s/sqrt(1+s²)) sin(theta) ds dtheta

이다. 공통 charge-center O의 rho,z 변환, 내부·외부에 위치한 상대 핵의 cusp 분할, 외부 cusp의 ds/xi_star 대 dtheta metric 비율을 확인했다. 두 방향 적분과 두 self norm을 사용하고 유한 prolate domain 밖에서 상태를 0으로 연장한다. 서로 다른 기저의 coefficient dot product를 사용하지 않는다.

Fortran은 binary64, 고정 patch 내부 합과 고정 batch 순서를 유지하며 독립적인 곱·patch만 SIMD/OpenMP로 병렬화한다. fast-math, reassociation, FMA contraction은 사용하지 않는다. Streaming의 batch 합 그룹은 기존 전체배열 합과 다르므로 bitwise 동일성 대신 사전 지정 tolerance의 parity로 검증하는 것이 맞다. 실행 시 native source/binary/ABI identity와 frozen-state hash를 검사한다.

## 독립 수치 확인

15개 frozen pair의 STATE.npz는 RESULT의 size/SHA와 일치하며, STATE.npz·RESULT.json·TASK_INPUT.json은 부모 C2a의 해당 파일과 byte-identical이다. 원래 등록된 55개 고유 task가 모두 존재하고, task 입력·실행 source identity·native identity·RESULT hash·DATA size/hash가 연결된다. 새 고유상태는 0개다.

| 검증 | 독립 재계산된 최댓값 | 기준 |
|---|---:|---:|
| Force 두 연속 order 증분 | 4.6375570051e−10 | 1e−8 |
| Force와 직접 연산자의 차이 | 1.1098197916e−9 | 1e−7 |
| 새 overlap 두 연속 order 증분 | 3.7721936685e−11 | 1e−7 |
| 새 overlap 최고 차수 양방향 차이 | 2.6645352591e−15 | 1e−7 |
| 원래 Duffy q40→56 증분 | 9.2222318671e−10 | 1e−8 |
| 원래 Duffy와 새 force의 차이 | 1.0720313526e−12 | 1e−8 |
| 원래 overlap q48→64 증분 | 3.3119429976e−8 | 1e−7 |
| 원래 overlap과 새 좌표 적분의 차이 | 1.5562231503e−8 | 1e−7 |
| 네 native/Python parity 비교 | 2.2204460493e−16 | 1e−11 |

Force 8개 대상과 R2 control, overlap 5개 문제 edge와 2개 control 모두 등록한 gate를 통과한다. Fallback order는 필요하지 않았다. 이는 검증한 상태·격자의 경험적 적분 수렴이며 rigorous error enclosure가 아니다.

통합된 일곱 R점 자료는 기존 에너지·직접 연산자·공간 refinement를 유지하면서 R8/R16 force 증거만 갱신한다. 34개 인접 overlap은 7개 새 결과와 27개 기존 통과 결과를 결합한다. R 순서에 따라 누적 위상을 재계산하며 두 sector의 마지막 위상은 +1이다. 부모의 실패 자료는 수정하지 않았다. 점과 local edge의 통과를 숨은 crossing 부재나 연속 구간의 인증으로 해석해서는 안 된다.

## 실행 오류와 회수 범위

초기 preflight가 최대 1 worker를 허용했는데 root orchestration이 3 workers를 실행한 것은 `EXECUTION_CONTROL_ERROR`다. 원래 4-rank 실행 전체를 자원 검증 완료 또는 정상 완료라고 부르는 주장은 승인하지 않는다. 35개 완결 task만 독립적으로 identity를 검사하여 회수했으며, 미완결 overlap 3개는 보존했다. 24개 실행 당시 파일은 pre-edit snapshot과 일치하고 회수 분석을 위해 바뀐 파일은 analyze.py뿐이다. 과학 연산자·상태·계약은 바뀌지 않았다.

남은 20개 task는 새 preflight를 통과한 2 ranks/1 worker에서 완료했다. 새 방법 overlap 시도는 중단된 3개를 포함해 24개로 상한 35개 이내다. 완결 task wall 합 236.4645초에 세 미완결 task의 최대 허용시간 720초를 모두 더한 보수적인 상계도 956.4645초로 전체 1800초 이내다. 완결 task 최고 RSS는 79,876 KiB, 최고 실행시간은 26.546초였다. 관측 RSS와 설정 RLIMIT_AS는 서로 다른 지표다.

추가 serial replay는 자원 preflight에서 중단되어 실행하지 않았다. 따라서 이번 구현의 새 MPI-vs-serial 실측, NCP64 scaling, 새 속도 배율은 주장할 수 없다. 로컬 core binding 제한에 따른 unbound 실행도 실제 NCP topology 실험과 구분해야 한다.

## 유지할 한계

`scientific_PROMOTE=HOLD`, `full_certificate_fail_closed=true`, `full_C2_closed=false`, `Eq55=NOT_RUN`, production 기본값 미승인을 유지한다. D1 또는 충돌 계산으로 진입하지 않는다. 남은 전체 R 범위, rank-five cluster/hidden crossing, continuum enclosure, scaled asymptotic 극한은 별도 연구 계약의 대상이다.

최종 author 보고서·handoff·README·CLAIMS의 수치와 문구도 검토했다. 원래 실패 및 실행 제어 오류, 선택적 replay 미실행, 경험적 수렴의 범위, 차수가 다른 단회 timing의 한계를 올바르게 구분한다. 보고서의 배치 시간 상계 약 268.6초는 별도 wall-clock 기록과 일치하며, 위의 956.5초는 완료 task와 미완료 task cap을 합친 더 보수적인 독립 상계다. 둘은 서로 다른 집계다. 새 작은 R 연구의 후보 격자는 다음 계약의 제안이며 이미 실행된 결과로 표기하지 않는다. 최종 문서 hash는 `C2B_INDEPENDENT_REVIEW_DOCUMENT_CHECK.json`에 고정했다.
