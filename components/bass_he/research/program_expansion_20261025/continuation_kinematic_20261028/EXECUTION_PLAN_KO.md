# R4/C4 선택·구성과 실행 DAG

## 실제 비교한 후보
1. 물리 입력 A,M,e에서 p+q√R exact sign으로 연결: 기존 gamma/a 반올림을 제거하고 native photon energies와 mass-shell/threshold를 직접 검증한다. 선택했다.
2. 유한 phi acceptance: 2D density와 phi+pi 공유사건을 명시해야 실제 telescope를 다룬다. 입력과 기하 범위가 더 필요해 이번 단위 이후 후보로 보존한다.
3. moving-target invariant encounter: 상대운동 flux와 rest-frame incident energy를 연결할 수 있으나 target distribution·실제 flux/history와 DCS 정규화가 남는다. 기존 null을 임의로 채우지 않고 후속 과제로 유지한다.

## 계산 설계와 순서
A,M,e의 유리수 입력→s,H,G,R→exact original-sign comparator→rational fold bracket→단조 branch별lab-window endpoint bracket→SetBounds→기존 Bernstein 적분→shared event count·G*Y. 정의역과widthproof는THEORY_KO.md. 이분법의 bracket 불변식으로 정당화하며 γ,a의 수치근사를 oracle로 쓰지 않는다.

R5/C5에서 source를 고정한다. R6/C6에서 새 exact/Decimal80/control tests를 한 번 실행하고 plot용 값을 함께 저장한다. R7/C7에서 해당 물리보존·극한과 새 Wolfram대수를 판정한다. R8/C8에서 saved-only plot과 같은실행의timing을 읽는다. R9/C9에서 하나의 독립 검토pass를 실제 결과까지 완결한다. R10/C10에서 scope와actualACK를 인계한다. 각S단계의source및두providerACK를 외부STAGE_ACKS에 남긴다.

코딩은 complete root scientific contract를 받은gpt-6.1-sol requested executor에게 위임했다. runtime model identity는 도구가 독립적으로 확인해주지 않았으므로 observed=null이다. Root는식/범위/판정, 독립Astra reviewer는 실제diff와원자료의판정을 담당한다.

신규validationCPU10s,wall30s,AS512MiB,threads1; initialrun1 및 진단에 따른targetedrepair reserve1. 새plotCPU6s,wall15s,scientificcalls0. Wolframevaluator1call,timeConstraint15s. 기존APERTURE/PHOTON/HE101 budget reset/transfer없음. 무리수 slope의 detector-specific daughterenergy는이번API범위밖이며 pairenergy와coincidence-labelenergy의exact값은구현한다.
