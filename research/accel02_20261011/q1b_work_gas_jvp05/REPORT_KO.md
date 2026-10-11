# Work 분리 및 gas 방향 흡수 미분

독립 판정은 `PASS_WORK_SPLIT_GAS_ABSORPTION_JVP_SCOPED`이다. 실제 native work 7개 사례, 제조 광학두께 약1의 60개 검사, 실제 source-entry의 104개 precision 검사를 합성했다. 물리 adapter와 허용오차는 변경하지 않았다.

최초 binary64 유한차분은 `HOLD_FD_ORACLE_PRECISION`으로 보존했다. HeI count/binding/heat에서 관측할 plus-minus 차이가 약 2 ULP에 불과했다. 독립 Decimal80 직접 rational-map 값의 차분으로 검증 산술만 수정했고, 기존 `1e-7` 기준에 대한 최대 미분 오차는 6.202597652811205e-16이다. 기존 성공한 work·manufactured 검사는 반복하지 않았다. 원 최초 FD vector는 기록 결함으로 누락되었으며 복원했다고 주장하지 않는다.

승인 범위는 radiation/gas work 소유권과 고정 photon node에서의 photo-absorption gas 방향미분이다. 실제 경우의 차분 수렴 차수는 `ORDER_NOT_RESOLVED`이며, full gas RHS Jacobian·nonlinear solve·history 수렴이 아니다. Entry04의 개별 흡수 채널 상대 시간 변화 약60%→33%도 여전히 남는다.

이번 unit은 최초 실패·독립 continuation·단일 repair를 합쳐 native4, SIGMA8/768energies, CELL7, FP64map61, Decimal80map76을 사용했다. 전체 누적 wall50.56217987200944s, 알려진 CPU48.941116s이며 미계측 overhead는 UNKNOWN_NOT_ZERO이다. 다음 실행은 single-endpoint residual와 admissible trial이고 global admission은 HOLD이다.
