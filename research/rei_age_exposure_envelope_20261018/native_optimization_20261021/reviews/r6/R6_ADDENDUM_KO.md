# R6 계약 변경 addendum

**PASS_SCOPED 유지, 열린 지적 0개.** THEORY SHA256 `fc780203aefab9b523d8eac755ca7db20dabcb13ba67dc71d33695af95edeb66`은 최초 검토와 정확히 같다. 현재 IMPLEMENTATION_CONTRACT SHA256은 `3478de728294ebd6ade45a39b2bd183a24cb519d8b03f0b37dade798d4bbb5e0`이다. 최초 계약 hash `5d9475c69f394f7b2a89d68d1776b469c503a3bcbd41381548ef5c6601007b21`과 최초 R6 receipt는 별도 이력으로 유지한다.

1. **유효한 작은 control domain.** 실제 원 driver/angular/source guard에서 거부된 transport4/n_mu2/source1 대신 2births/n_mu8/source8/transport8과 짧은 mesh를 사용한다. 이는 검산 입력을 원 domain 안으로 옮긴 변경이다. 원 gates와 본 time8/16/32의 birth32/source8/n_mu8/transport16 계약은 유지된다. 보존된 COMMANDS 및 tiny_attempt003/TINY_RESULT를 읽어 선행 실패 기록과 현재 물리 출력 parity PASS의 구분을 확인했다. 검토자가 실행을 반복하지 않았다.

2. **작은 allocation의 elapsed cap.** 3개 고유 case 각각 1800s라는 상한과 aggregate child wall 5400s를 유지하면서, jobs가 3/2/1이면 elapsed cap을 각각 2000/3800/5600s로 둔다. 식은 ceil(3/jobs)*1800+200이다. 작업을 직렬화할 때 마지막 case를 2000s에서 잘라 버리는 문제를 해소한다. 작업 수·원 case cap·원 gate·연구 admission은 확대되지 않는다. 실제 자원 할당과 persistent debit의 구현 검토는 C9 범위다.

3. **한 번의 absorption kernel microbenchmark.** source8/n_mu8/transport16의 prepared fixture, 32 cohort jobs, 고정 absorber/dt에서 원 serial과 ordered widths1/2/4를 비교한다. 설정당 5회, 동일 iterations, 측정 aggregate cap30s가 기존 light budget240s 안에 포함된다. shared-gas RHS/IVP/time history를 포함하지 않으므로 측정 결과는 이 kernel에 한정한다. MICROBENCH와 COMMANDS를 읽어 해당 scope·보존된 모든 반복·물리 필드 parity·실제 debit을 확인했다. 64-core 속도 또는 전체 native campaign 속도 주장으로 확대하지 않는다.

세 변경은 이미 검토한 수학의 가정·결론, subnormal-only 원 gate fallback, 저장 분모 BE kernel의 범위 및 finite candidate search의 비완전성 지위를 바꾸지 않는다. 새로운 이론 계산, trajectory, 이전 control/benchmark 재실행은 없었다. 본 addendum은 이 세 변경의 계약 범위만 검토하며 구현 C9를 대체하지 않는다.

Continuous nonlinear Grackle response bound=NOT_ESTABLISHED. PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.
