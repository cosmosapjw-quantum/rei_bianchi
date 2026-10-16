# source006 opt-in Jacobian 열 병렬화

측정된 병목을 바탕으로 Newton Jacobian의 네 독립 residual 열만 기존 shared worker pool에 배정했다. `parallel_jacobian_columns`의 기본값은 false다. delta·양/음 perturbation fallback·열 조립 순서·solve4·line search·허용오차는 유지한다. 잔여 RHS credit이 8보다 작으면 기존 직렬 경로를 사용한다. 실제 시작한 모든 residual을 원자적으로 청구하고, 실패 시에도 나중 열의 실제 작업을 누락하지 않는다. 상태와 에너지 장부의 commit은 coordinator 한 곳에서 성공 시에만 수행한다.

Pinned Rust 1.94.1로 집중 테스트 7/7, release build, 한 번의 진단이 모두 exit0이었다. 별도 source identity는 `abf4ad86bbb969406918eb7eae668efb0d2b36a04f18a3dc7cac82479c09ba55`다. 원 full005의 source·binary·실행 config·campaign epoch 등 117개 보호 기록은 동일했다.

| 고정 fixture chemical stage | 직렬 | 병렬 |
|---|---:|---:|
| warm-up (stage) | 4 | 4 |
| timed (stage) | 32 | 32 |
| timed kernel wall (s) | 0.226000643 | 0.170695102 |
| timed region CPU (s, 10ms 해상도) | 0.55 | 0.54 |

측정 비율은 1.324001921이다. 하나의 Driver·8-worker pool에서 두 모드를 실행했으며 총 72 stage/504 RHS의 상태·장부·control이 비트 단위로 일치했다. 저장된 최종 state 배열은 24,626개 word가 같았다. 실제 프로세스 19개 관측의 affinity는 CPU16–31 안이었고 최대 OS thread는 9개였다.

독립 검토는 PASS_SCOPED_SOURCE006_OPT_IN_JACOBIAN_COLUMNS를 발급하고 이 완료 단위의 게시·백업을 허용했다. 단일 fixture의 stage 측정이며 전구간 속도·time/angular convergence·64코어 활용을 입증하지 않는다. 실행 중인 source005에는 배포·resume하지 않았다. 기존 Q512/Q1024가 실제 종료하면 기존 watcher가 엄격한 binding/전 행 검증 후 후처리를 수행하며, full-pair 과학 검토는 별도다. 현재 Bianchi 및 isotope-native 활성화 gate는 미완료다.

`RESULT.json`은 공개 실측값, `INDEPENDENT_REVIEW.json`은 독립 판정의 coordinator 전사, `public/`은 실제 명령·exit·test/build/diagnostic log다. 원 checkpoint/state·프로세스 관측·운영 스크립트·원 raw archive는 공개 Git에서 제외하고 비공개 백업에 보존한다. 전체 CI green을 주장하지 않으며 이번 7개 집중 검증의 통과만 보고한다.
