# 다음 단일 의존성: C2C_SMALL_R_SCALED_NUMERICAL_AUDIT

C2b의 frozen-state 적분 gate는 모두 통과했다. 기존 7개 유한 R 점별 기준과 18개 지점·34개 fixed-m 인접 연결을 복구했지만 full C2는 닫히지 않았다. D1으로 넘어가지 않는다. CODE_I02_CLOSED=true, scientific_PROMOTE=HOLD, Eq55=NOT_RUN, full certificate fail-closed와 production 기본값 미승인을 유지한다.

## 재사용할 증거

C2a archive의 39개 prolate 상태쌍과 독립 구면 앵커를 그대로 보존한다. 부모 archive SHA256은 CONTRACT.json에 있다. 이번 frozen/ 폴더의 15개 쌍은 inputs/FROZEN_IDENTITY.json과 원래 RESULT의 size/SHA를 확인한 복사본이다. C2b 적분 결과와 기존 성공 evidence를 합친 상태는 evidence/RECONCILED_GRID.json 및 RECONCILED_CONTINUATION.json이다. 원래 실패 기록은 지우거나 소급 PASS로 바꾸지 않았다.

새 적분 모듈은 code/force_integral.py, code/overlap_integral.py다. 높은 차수에서도 32 patch streaming, scalar B-spline batch, Fortran real64/OpenMP/SIMD, explicit OpenMPI 작업 분배를 유지한다. CONTRACT의 기준과 geometry cap, no-fast-math, source/ABI/binary pins, atomic+fsync/create-only 출력은 그대로 인계한다. 두 물리 실행의 당시 소스는 provenance/*CODE_SNAPSHOT.zip에 고정했다. 최종 소스에 보고용 postprocessing과 미실행 replay manifest가 추가된 점을 실행 당시 identity와 혼동하지 않는다.

## 다음 연구에서 먼저 고정할 계약

목표는 작은 x=R/a_A에서 L_O/(−iℏx³)가 4√2/15에 접근하는 유한 수열을 수치적으로 조사하는 것이다. 현재 최소 x=0.25만으로 점근 적용범위를 주장하지 않는다. C2b의 적분 성공을 작은 R로 전용하지 않는다.

1. x=0.25 성공 증거를 identity 확인 후 재사용한다. 후보 새 수열은 {0.125,0.0625,0.03125}지만, 실제 지점·기저·물리적 box·고정 fallback과 최대 깊이는 실행 전에 machine-readable 계약으로 확정한다. 이 파일은 그 실행 계약 자체가 아니다.
2. 전하(1,2), 단위, 공통 O/B 원점, 최저 m=0 및 밝은 |m|=1 상태와 위상 규약을 유지한다. 독립 direct/force, p/d, dark, norm/residual을 기록한다. direct p를 Δd로 정의해 독립 검산을 없애지 않는다.
3. h/p/q/tail 오차를 분리하고 raw δL_O와 scaled δL_O/x³를 각각 제한한다. 기존 raw 기준은 완화하지 않는다. 작은 R의 cancellation·roundoff가 scaled budget을 넘으면 명시적인 수치 한계로 중단한다. 해석적 O(x^(7/2))의 미지 상수·유효 반경을 유한 R의 알려진 오차 상한으로 쓰지 않는다.
4. 새 구간의 physical overlap·양방향·자기 노름·연속 두 차수 증가를 확인하고 R 순서로 phase를 연결한다. 적어도 한 새 작은 R 지점의 독립 구면 앵커와 그 기저 증가를 사전 등록한다. 해당 지점·수준·state 수는 예산 안에서 계약에 확정한다.
5. 모든 eigensolve·적분·독립 앵커·fallback 개수, task/총 wall, 메모리와 STOP을 계산 전에 기록한다. 새 물리 계산을 지금 수행한 것은 아니다. 이번 두 적분 문제와 관련 없는 완료된 suite를 재실행하지 않는다.

제안 STOP은 SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED 또는 SMALL_R_SCALED_NUMERICS_UNRESOLVED다. 성공하더라도 유한 수열의 경험적 검증에 한정한다. 목표 계수 fitting, 숨은 mixed precision 또는 허용오차 완화로 통과시키지 않는다.

## 실행 경계와 남은 의무

초기 C2b의 preflight 실패 후 잘못된 launch는 provenance/EXECUTION_ANOMALY.json에 있다. 후속 1-worker 배치는 정상 preflight를 통과했다. 다음 실행은 preflight exit0를 실행의 필수 조건으로 연결한다. 선택적 serial replay는 메모리 부족으로 NOT_RUN이며 다시 실행해야 할 과학 의존성으로 바꾸지 않는다. NCP64 실제 scaling도 NOT_RUN이다. NCP에서는 실제 topology와 메모리를 확인하고 승인된 새 workload로 rank/thread를 선택한다. 로컬 sandbox의 --bind-to none 예외를 NCP 기본값으로 전파하지 않는다.

소 R 다음에도 대 R scaled 수렴, collision-relevant 전체 R/adaptive 점검, hidden crossing/isolation, H1s+He n2 rank-five cluster, continuum error enclosure가 남는다. 상세 읽기 자문은 review/NEXT_DEPENDENCY_ADVISORY.md에 있다. 외부 업로드 ACK와 size는 복원 증명이 아니며 다음 세션은 필요한 파일만 SHA/size를 확인해 재사용한다.
