# BASS_HE C2d: 큰 R의 두 원점 scaled coupling 검증

최종 상태: **SCOPED_LARGE_R_SCALED_SEQUENCE_CONVERGED**. 범위는 새 x=R/a_A=32,64의 수치 quartet, x=32의 독립 구면 표현, x=16,18,…,64의 공통 O 원점 상태 연결이다. 전체 C2와 물리 production 승격은 보류한다. 이 구현은 논문에서 독립적으로 도출한 코드이며 저자의 ARSENY 코드는 아니다.

## 두 coupling의 결과

ell=L/(-i hbar), Q_O=ell_O/x, Q_B=-x² ell_B를 사용했다. 상속된 해석적 계수는 각각 32√2/243=0.186233884756951, 128√2/729=0.248311846342601다.

| x | Q_O | Q_B | Q_O의 극한계수 대비 차이 | Q_B의 극한계수 대비 차이 | 근거 |
|---:|---:|---:|---:|---:|---|
| 4 | 0.183519451457 | 0.284044952101 | -1.45754% | +14.39042% | 상속 scalar |
| 8 | 0.186056141833 | 0.251660001602 | -0.0954407% | +1.348367% | 상속 scalar |
| 16 | 0.186261519597 | 0.248757717404 | +0.01483878% | +0.1795609% | 상속 scalar |
| 32 | 0.186240672795 | 0.248370388732 | +0.003644899% | +0.02357616% | 새 quartet |
| 64 | 0.186234948974 | 0.24831935751 | +0.0005714411% | +0.003024893% | 새 quartet |

이 차이는 유한 R에서 극한계수와 떨어진 정도다. 수치 오차 막대나 엄밀한 오차 상한으로 쓰지 않는다. x=4,8,16은 기존 C2a/C2b 결과를 재사용했고 새 세 적분 차수의 closure로 승격하지 않았다. 새로운 두 점으로 remainder 차수·상수·유효 반경을 개선하거나 단조 수렴을 인증하지 않았다.

## 독립 판정과 정확도

각 새 점에서 base/h/p/tail 네 격자, 직접 적분 q16/24/32와 force 적분 q12/20/28, 두 연속 증가량과 terminal 3×3 교차 비교를 적용했다. tail은 원래 내부 knot를 그대로 보존한다. raw 기준과 다음 scaled 기준을 모두 요구했다.

| 경험적 검산 | 관측 최댓값 | 등록 기준 |
|---|---:|---:|
| Q_O 공간 정밀화 | 6.90985e-11 | 2e-06 |
| Q_B 공간 정밀화 | 3.65449e-10 | 2e-06 |
| Q_O direct–force | 6.88519e-11 | 1e-07 |
| Q_B direct–force | 3.42764e-10 | 1e-07 |
| Q_O 원점 항등식 | 5.55112e-17 | 1e-07 |
| Q_B 원점 항등식 | 1.45519e-11 | 1e-07 |
| Q_O momentum 항등식의 전파 | 4.67404e-14 | 1e-07 |
| Q_B momentum 항등식의 전파 | 1.22527e-08 | 1e-07 |

독립 구면 l96과 prolate의 x=32 차이는 Q_O 4.17721e-14, Q_B 2.48702e-11다. 구면 표현은 별도의 l72→96 증가량, 적분 증가량, norm·잔차·momentum 검사를 포함한다. 구면 anchor 승인=True.

공통 O 좌표의 인접 거리 연결은 48개 edge-sector, 최소 |normalized overlap|=0.77116829751이다. 세 적분 차수의 두 증가량·양방향 일치·self norm을 검사했다. continuation 승인=True; 네 native/reference parity 승인=True. 중간 bridge의 base 상태는 phase/residual/overlap 근거이며 h/p/tail 공간 수렴 근거로 사용하지 않았다.

B coupling을 큰 항의 차감으로 계산하면 x=64에서 약393207의 상쇄 지표가 발생한다. 따라서 B 원점 직접 integrand와 Q_B=x³ T_A/Delta의 안정적인 force 경로를 각각 평가하고 원점 항등식은 검산으로 남겼다. 큰 R의 지수적으로 작은 A 쪽 꼬리에서 부호를 정하던 코드는 가장 큰 regular spline 표본을 양수로 정하도록 고쳤다. 이는 전체 ± 위상만 바꾸며, 표본 음의 L² 질량 진단과 physical overlap을 별도로 확인했다.

## 실행과 정확도를 보존하는 병렬화

Fortran real64/OpenMP/SIMD 커널, 명시적인 OpenMPI, OMP/BLAS 1 thread, strict 부동소수점 옵션을 유지했다. fast-math·혼합 정밀도·암묵적 backend fallback은 없다. 초기 상태 작업은 memory preflight가 허용한 2 workers, 후속 적분은 3 workers를 사용했다. 관측된 환경은 CPU quota8/affinity9, 메모리8GiB이며 NCP64 실제 scaling은 NOT_RUN이다.

로컬 MPI unbound 예외에서도 OpenMP close/cores가 native ABI 로드 시 모든 작업자를 CPU0에 묶는 문제를 발견했다. fresh subprocess 및 3 MPI ranks의 제조 검사로 원인을 재현했다. 명시적 local-unbound에서 부모 MPI와 자식 worker 모두 OMP_PROC_BIND=FALSE를 유지하도록 실행 경계만 수정했다. NCP의 core/close 기본값과 계산 worker·native·수식 코드는 그대로다. 실제 worker mask의 관측 기록은 review의 affinity 증거에 있다. 각 batch의 작업이 달라 동일 workload 속도 배수는 산출하지 않았다.

| Batch | 실측 wall 초 | 원 return code | 상태 |
|---|---:|---:|---|
| FOLLOWUP_MPI | 1800.894432 | 124 | WHOLE_BATCH_TIMEOUT_RECOVERED_WITHIN_ORIGINAL_BUDGET |
| MAIN3_MPI | 298.973306 | 0 | ALL_WORKER_RESULTS_PASS |
| RECOVERY_MPI | 131.697984 | 0 | ALL_WORKER_RESULTS_PASS |

선택 상태 64개, 완료된 고유 task 184개. 실제 시작 시도는 191개이며 중단 시도도 포함한다. 완료 작업의 재실행은 0회다. 전체 launcher의 보수적 과금 wall은 2231.649436초/등록3600초, 관측 최대 worker RSS는 580.804688MiB다.

원래 후속 batch의 1800초 상한·timeout·종료 기록을 보존했다. PARTIAL_BATCH_INDEX는 원본 BATCH_SUMMARY를 위조하지 않고 완료된 TASK_EXECUTION/RESULT/DATA를 결합한다. 복구는 정확히 같은 미완료 입력·상태·적분 차수만 대상으로 하며, 종료 신호가 확인된 중단 작업도 시도수에 포함한다. 메모리 preflight와 프로세스 cleanup, 완료 재실행0, 원래 총시간·시도수 한도를 별도로 검증한다. 실행 복구 상태=WHOLE_BATCH_TIMEOUT_RECOVERED_WITHIN_ORIGINAL_BUDGET; 이것만으로 과학 PASS를 추론하지 않는다.

## 남은 연구 범위

full_C2_closed=false, scientific_PROMOTE=HOLD, full_certificate_fail_closed=true, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED를 유지한다. 전체 충돌 R 범위, hidden crossing/isolation, H1s+He n2의 rank-five target, 연속공간 enclosure와 collision evolution·단면적은 아직 닫지 않았다.

다음 단일 의존성은 **C2E_COLLISION_DOMAIN_AND_SPECTRAL_TARGET_CONTRACT**다. 통과 시 먼저 실제 충돌 영역과 추적할 spectral projector/외부 gap의 정의를 회수·고정한다. large-R의 다섯 상태를 전 R의 고정 rank-five cluster로 자동 연장하지 않는다. 새 수치 실행 범위나 허용치를 이 보고서에서 임의로 추가하지 않는다.

## 재현 근거

현재 계약 SHA256: e43372481ba1ddc4a556a5eb199ec0fe9479247fbda59bea650681bcac1dee54. 실행 당시 소스는 provenance의 MAIN/FOLLOWUP/RECOVERY_CODE_SNAPSHOT.zip, scalar 판정은 evidence/FINAL_AUDIT.json, 독립 검토는 review에 있다. 전체 archive에는 상태·입력·로그·실패와 복구 증거를 포함한다. 원본 논문 PDF는 공개하지 않는다. archive의 로컬 CRC와 모든 payload SHA 검증, 외부 저장 ACK/size 확인을 구별하며 ACK를 restore 검증으로 부르지 않는다.
