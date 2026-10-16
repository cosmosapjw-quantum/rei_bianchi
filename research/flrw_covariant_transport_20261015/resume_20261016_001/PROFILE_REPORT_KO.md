# source005 유지 및 post-cache 진단 재개

2026-10-16 KST. 기존 source005 Q512/Q1024와 후처리 watcher가 실제 실행 중임을 확인했다. campaign epoch 1792075817.77407, deadline 1792119017.77407을 유지했다. 최종 renderer 실제 파일은 게시된 SHA d62a95f8…와 일치했다. 완료된 검산·short screen·cache benchmark는 재실행하지 않았다.

허용된 literal backslash-n 한 곳만 실제 개행으로 수정했다. pinned Rust 1.94.1 빌드는 exit0/0.565410초, 단 한 번의 진단은 exit0/0.439393초/70 RHS/peak RSS 28,983,296 bytes였다. source005의 115개 정적 source·binary·epoch 기록과 입력 fixture는 전후 동일했다. 실제 진단의 20개 thread-affinity 관측은 모두 CPU16–31이었다. 시작 직전 taskset의 inherited affinity 관측을 실제 과학 프로세스와 구분해 보존했다.

| 측정된 성분 | 호출당 ms |
|---|---:|
| prepare, 8 workers | 2.840187 |
| prepare, 16 workers | 1.947564 |
| prepared absorption evaluate | 0.603036 |
| inject (fixture clone 포함) | 1.805430 |
| partition | 0.161540 |
| whole chemical stage (7 RHS) | 7.463651 |

8/16 worker의 ordered cache와 dt=0/finite 결과 bit-word 파일은 동일했다. prepare의 측정 비율은 1.458328이지만 단일 고정 fixture의 성분 측정이며 이력 전체의 속도 향상이 아니다. 성분별 반복 횟수가 달라 총 시간을 production 비율로 해석할 수 없다. 64코어 활용·전구간 time/angular 정확도는 미완료다. 독립 검토는 PASS_SCOPED_FINITE_POSTCACHE_PROFILE을 발급했다. 기존 profile의 추가 build/run allowance는 각각 0이다.

다음 별도 source006에서는 opt-in Jacobian 네 열의 병렬화를 제한된 시험·진단으로 검증한다. 현재 source005를 배포 변경하거나 재시작하는 권한은 없다. 실제 full pair 종료 후 bound source/config, 전 행 장부 및 endpoint를 검증하고 기존 watcher의 결과를 독립 검토해야 한다. Q512/Q1024 쌍은 energy grid 비교이며 whole-history time/angular convergence를 대신하지 않는다. signed Bianchi와 isotope-native 활성화는 기존 backend/provider 및 단일 에너지 소유권 조건을 따른다.

공개 Git 산출물은 public/의 코드·명령·실측 JSON·log와 독립 검토 기록이다. 원 fixture/checkpoint·전체 프로세스 관측·원격 연결 script는 공개 Git에 포함하지 않는다. 이 공개 묶음만으로 raw checkpoint를 복원할 수 있다고 주장하지 않는다.
