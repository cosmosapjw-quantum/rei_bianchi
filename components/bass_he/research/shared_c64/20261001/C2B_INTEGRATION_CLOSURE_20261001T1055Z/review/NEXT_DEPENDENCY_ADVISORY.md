# 다음 단일 의존성에 대한 독립 읽기 자문

조건: **C2b의 전체 frozen-state 적분 gate가 실제로 통과하고 독립 검토가 수락한 경우에만** 아래 다음 node를 선택한다. 이 문서는 새 실행 계약이나 C2b 판정이 아니다. 새 eigensolve 또는 물리 적분을 실행하지 않았다.

권고 node는 **C2C_SMALL_R_SCALED_NUMERICAL_AUDIT**다. 기존 최저 m=0 / 최저 |m|=1 쌍에서 작은 R의 cubic coupling을 공간·적분 오차와 분리하여 확인한다. 이는 가능한 후속 의존성 중 하나를 선택한 자문이며, 기존 handoff가 이 순서를 유일하게 강제했다는 뜻은 아니다.

## 선택 근거

C2a의 가장 작은 점 x=R/a_A=0.25에서 iL_O/(ℏx³)=0.2288956021988902이다. A2의 해석적 계수 4√2/15=0.3771236166328254와의 상대 차이는 약 39.3%다. 이 차이는 잘 수렴한 유한 R 값과 점근계수 사이의 차이이며, solver 오류나 A2 반증을 뜻하지 않는다. 현재 점으로 작은 R 적용범위를 판단할 수 없다는 구체적인 증거다. 반면 C2b가 복구하는 큰 R의 force·overlap 문제는 동결 상태의 적분 문제이므로, 그것이 닫혔다는 사실을 작은 R scaled 수렴으로 전용할 수 없다.

다음 연구에서는 이미 구현된 두 fixed-m sector와 독립 direct/force lane을 유지할 수 있다. 새 rank-5 고유부분공간 설계를 동시에 도입하지 않고도 아직 수행하지 않은 A2 수치 검증을 한 단계 진전시킨다. A2의 기존 해석적 유도/CAS와 통과한 C2a 전체 격자를 반복할 필요가 없다.

## 다음 실행 전에 고정할 정확한 범위

- 전하 (1,2), 단위 (a_A,E_A,ℏ), charge-center O 및 B 원점, g/b 정의와 positive-overlap 위상 convention을 상속한다. L_O=L_B+z_B p_x를 유지하며 direct p를 Δd로 정의하지 않는다.
- x=0.25의 기존 상태·성공 증거를 identity 확인 후 재사용한다. 새 dyadic 후보는 x={0.125,0.0625,0.03125}이며, 실행 전 해상도·비용 검토를 거쳐 **실제 배열, 사전 고정 fallback 배열과 최대 깊이**를 machine-readable contract에 확정한다. 이 후보 자체는 실행 승인이나 등록 완료를 뜻하지 않는다.
- 각 새 R에서 energy, direct L_O/L_B, 독립 force, p/d, dark, norm/residual을 기록한다. h/p/q 및 tail을 각각 변화시키며, 작은 R로 갈수록 변하는 prolate 좌표 스케일·핵 사이 공간 해상도·Coulomb 적분의 조건을 먼저 검토한다. 같은 물리적 box를 좌표상의 동일 숫자와 혼동하지 않는다.
- raw 오차와 **scaled 오차** δL_O/x³를 별도로 제한한다. 기존 raw 기준만 통과시키지 않는다. 새 scaled spatial/force/refinement 한계와 유한 점에서의 점근계수 접근 목표를 서로 분리해 실행 전에 수치로 고정한다. 기존 raw 허용오차를 완화하지 않으며, 작은 R의 cancellation·roundoff가 budget을 넘으면 명시적인 수치 한계로 STOP한다.
- 새 구간의 공통 physical measure overlap, selfnorm, 양방향 적분, 두 번의 차수 증가와 phase 연결 gate를 유지한다. C2b의 좌표 변환이 작은 R에서도 실제로 수렴하는지 affected scope만 검사한다. 단순 coefficient dot product나 energy sorting으로 phase를 정하지 않는다.
- 새 regime의 독립 표현 검증을 최소 한 지점에서 사전 등록한다. 예를 들어 작은 R의 독립 구면 표현에서 basis·domain 증가를 확인하되, C1b/C2a 앵커의 기존 정확도를 미계산된 작은 R로 전용하지 않는다. exact 지점·수준·state 수는 새 계약에 고정한다.
- 모든 eigensolve/적분/독립 앵커의 최대 개수와 재시도 수, worker 주소공간·wall/총 wall cap, fallback 실행 조건, cache identity와 반환 스키마를 먼저 확정한다. 호스트 사전검사 성공을 launch의 조건으로 두고, 실패하면 실행하지 않는다. MPI는 독립 상태/적분에 사용하고 위상 연결은 R 순서로 한다. Fortran real64/OpenMP/SIMD, no-fast-math, explicit reference/native 경로와 parity gate를 유지한다.

제안 STOP은 `SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED` 또는 `SMALL_R_SCALED_NUMERICS_UNRESOLVED`다. 전자는 사전 지정한 유한 수열의 경험적 수렴만 뜻한다. A2의 O(x^{7/2})는 미지 상수와 유효 반경을 가진 해석적 remainder다. 이를 유한 R의 정량 오차 경계로 쓰거나 수열에 계수를 fitting하여 목표를 맞추지 않는다. 접근 오차의 단조 감소는 그 remainder만으로 보장되지 않으므로 무조건적인 이론 gate로 주장하지 않는다.

## C2b 통과 뒤에도 남는 의무

| 남은 범위 | 현재 증거의 정확한 한계 |
|---|---|
| 소 R scaled 수열 | x=0.25,0.5,1의 진단뿐이며 새 축소 수열은 미실행. 위 권고가 이 의존성을 다룬다. |
| 대 R scaled 수열 | x=4,8,16의 진단뿐. iL_O/(ℏx)→32√2/243 및 −iL_B/(ℏx⁻²)→128√2/729에 대해 새로운 공간·tail/roundoff 오차와 분리한 수렴 검증이 필요하다. |
| collision-relevant 전체 R 범위 | 현재 7개 과학 지점과 18개 continuation 지점이다. 실제 적용 범위와 adaptive R 중간점·closest approach·large-R tail의 정의/검증이 없다. |
| hidden crossing / isolation | 두 최저 fixed-m 상태의 인접 overlap은 보존하지만 모든 중간 R의 isolation 또는 crossing 위치를 인증하지 않는다. |
| H1s+He n=2 rank-5 cluster | 두 fixed-m 상태는 rank-5 cluster가 아니다. 필요한 다중상태, 외부 spectral isolation, overlap singular values와 polar/Procrustes transport는 별도 의존성이다. |
| continuum error enclosure | 작은 이산 residual, h/p/tail spread와 독립 유한기저 일치는 continuum 인증이 아니다. full-space residual/domain·gap과 오차 bound의 미해결을 보존한다. E2의 scattering continuum/channel 수렴과도 별개다. |
| 연결 미분 diagnostic | finite-difference/connection derivative 제3 lane은 NOT_RUN이다. 원 계약의 가능하면 수행하는 diagnostic이며, 미실행을 숨기지 않는다. |

D1, 충돌 전파, 단면적, benchmark fitting, Eq55와 production 변경은 이 권고의 범위 밖이다. `full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `full_certificate_fail_closed=true`, `production_default_change=NOT_AUTHORIZED`를 유지한다. NCP 64코어 실측 scaling도 현재 실행 증거가 없으면 NOT_RUN이다.

근거 파일: C2b `CONTRACT.json`; C2a `CONTRACT.json`, `NEXT_HANDOFF_KO.md`, `evidence/GRID_AUDIT.json`, `provenance/C1B_NEXT_HANDOFF_KO.md`; root 지침의 보존본 `provenance/AGENTS_AT_PARENT.md`; A2 `NEXT_HANDOFF_KO.md`, `A2_ASYMPTOTIC_DERIVATION_KO.md`; 사용자 원계약 C2 절. 기존 파일은 수정하지 않았다.
