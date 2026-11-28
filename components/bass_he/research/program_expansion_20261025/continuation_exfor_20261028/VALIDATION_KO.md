# S06 — 단일 실제 검증과 원시 결과

실행 소스는 실제 게시 commit `fc9fc9c2590ff52af247353c29e04c15162b3ae7`이다. 공식 EXFOR 원문과 11개 실행 의존 파일의 SHA-256을 S05 pin으로 고정했다. 복원한 부분 소스 mirror에 가상의 local Git commit을 부여하지 않았다.

## 실제 결과

새 초기 과학 캠페인 1회가 exit 0/PASS로 종료됐다. 새 제어 6개가 모두 PASS였으며, 저장 certificate reader가 12개 경우의 inner/outer 정점 총 274개를 정확 유리수로 검산했다. 후보 수는 에너지별 RHS를 합쳐 11,952, singular 360, feasible active bases 274이다. 행렬 역산은 에너지 3개 사이에서 재사용했으므로 이 후보 수를 독립 행렬 역산 횟수로 부르지 않는다.

9개 경우는 inner/outer가 모두 비어 있지 않고 FULL 수용률은 정확히 1이다. 330 MeV에서 n=4 endpoint-free, n=4 endpoint-zero, n=8 endpoint-zero의 outer가 비었다. 이 세 경우의 목적값은 0이 아니라 null이다. 이는 고정한 비음수 Bernstein 차수/끝점 가정과 literal ±ERR-S 창의 양립 불가능성이다. 일반적인 양의 각분포, 실제 반응의 부재 또는 자료 오류를 증명하지 않는다. n=8 endpoint-free, 330 MeV는 inner/outer 각 12개 정점으로 구성적 가능성을 보인다.

검증은 원문 행/정확 decimal, 기저·대칭·적분·끝점, 별도 Decimal cosine 포함, 알려진 다면체와 비율 극값, manufactured 기하 적분과 물리 경계, 저장된 모든 부등식·양의 분모·증인·FULL=1을 다룬다. 별도 최적화기를 재실행한 것은 아니며 전 정점 목록의 완전성은 검토된 exhaustive enumeration 증명과 알려진 제어 사례에 근거한다.

## 실제 자원과 이력

전체 bounded-runner subprocess 및 기다린 자식의 CPU 2.416516 s, wall 2.47206964 s, peak RSS 17,200 KiB였다. 내부 scientific process 측정은 CPU 2.366214013 s, wall 2.372851532 s이다. 두 CPU 값을 합산하면 중복이므로 합산하지 않는다. 외부 orchestration body의 CPU 0.006502392 s는 별도 범위이며, 모델·provider·최종 metadata serialization까지 포괄하는 총비용으로 주장하지 않는다.

CPU 60 s / wall 180 s / address space 768 MiB / threads 1 계약을 충족했다. 초기 실패·재시도·repair는 0이다. 요청 executor는 gpt-6.1-sol, 관측 모델 식별값은 runtime 미노출로 null이다.

원시 stdout/stderr/START/TEST_REPORT/RESOURCE_RESULT/SAVED_PLOT_DATA와 전체 subprocess 영수증을 보존한다. HARMONIC10의 24 PASS+1 FAIL 및 targeted 1 PASS 이력, reserve 0은 변경하지 않는다. 선행 science/test/CAS/plot/ACK된 백업을 재실행하지 않았다.

S06 현재 Local 10/15, Central 28/88, HE delta 0. 새 노드의 최종 승인은 그림과 동일 독립 심사의 나머지 항목 이후 판단한다.

