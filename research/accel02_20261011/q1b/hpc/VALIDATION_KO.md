# HPC 구현 검증 범위

2026-10-11 동결 구현의 새 테스트 suite는 `48 passed, 4 subtests passed`로 종료했다. shell launcher와 Slurm 예시의 구문 검사, benchmark CLI 확인도 통과했다.

제조 상태 테스트는 worker 순서·resident 재사용·실패/timeout 정리, serial 함수와의 일치, checkpoint hash chain·원자적 게시·journal 복구, resource admission, private seed 복구, 공개 이력 검사를 다룬다. 원래 과학 검산 suite는 반복하지 않았다.

별도의 제한된 private 입력 실행에서는 다음 연결을 확인했다. 원시 입력·출력·receipt는 private handoff에서만 제공한다.

- 새 serial/parallel map의 물리 상태, 원래 진단, refinement, RHS 입력 및 호출 수가 정확히 일치했다.
- 새 controller trial 하나의 3-map 승인과 accepted pair checkpoint/journal 게시가 일치했다.
- 별도 프로세스의 cold resume는 추가 map 없이 같은 cursor/checkpoint를 복구했다.
- benchmark는 완료된 serial baseline을 재실행하지 않으며 외부 RESULT·LAUNCH SHA를 모두 인증한다. NCP 후보 측정은 아직 실행하지 않았다.

독립 검토자는 source/opacity, gas solver, controller, 합산 순서와 누적 예산 보존 및 위 실행 receipt를 확인했다. 복구 사전 검사, resource admission, baseline provenance의 지적을 해소한 최종 범위에 미해결 blocker는 없다. 검토자는 코드 수정이나 계산 재실행을 하지 않았다.

이 검증은 전구간 완료, 과학적 수렴 또는 64-core 성능 보장이 아니다. 빠른 restart의 검증 범위는 과거 모든 payload의 byte 재검증과 다르다. 배포 시에는 PUBLIC_SOURCE_FILES.json의 정확한 allowlist로 새 Git 이력을 별도 감사한다.
