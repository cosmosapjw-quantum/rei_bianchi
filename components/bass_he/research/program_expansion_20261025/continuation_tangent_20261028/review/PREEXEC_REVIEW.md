# TANGENT13 실행 전 독립 검토

**PASS_SCOPED_PREEXEC. 차단 사항 0, F1–F4 모두 실행 전에 닫힘.** Root는 S05를 실제 게시하고 그 source identity를 execution pin으로 저장한 뒤, 고정 계약의 단일 campaign을 승인할 수 있다. 이 판정은 코드·증명·검증 설계의 실행 전 수용이며 실제 실행 성공을 미리 뜻하지 않는다.

이 검토는 앞선 CONTRACT_REVIEW와 같은 한 번의 비작성자 검토다. 검토자는 source 조사만 맡았고 TANGENT13 이론·알고리즘·구현·검증 코드를 작성하지 않았다. 읽은 바이트의 SHA256과 크기는 `PREEXEC_READ_IDENTITIES.json` 및 `PREEXEC_REVIEW.json`에 저장했다. 검토자 과학·test·CAS·plot 실행은0이며 기존 campaign도 재실행하지 않았다.

## 수학과 구성

THEORY 전체와 제조된 유리수 예제를 읽고 직접 식을 대조했다. 양의 data ratio가 h·b>=0를 주고, evaluation functional과 비음수 dual multipliers가 전체 true feasible cone의 하한을 준다. 이 논증은 candidate active-pair의 완전성이나 approximate root가 exact root라는 가정에 의존하지 않는다. Contracted square witness가 네 실제 nominal-angle data window를 모두 만족하면 같은 family의 상한을 제공한다.

기존 containing coefficient box/Dfloor와 complete outer vertex certificate를 재사용하는 경로가 분명하다. Denominator-weighted convex representation으로 M_j를 얻고 signed moment uncertainty를 Delta_k로 제어하는 전이는 타당하다. Compactness와 실제 feasible witness가 minimum의 존재를 보장한다. Genuine event probability의0–1 clipping과 predecessor bracket containment도 일치한다.

R4 예제의 r17/20,L9/25,U9/16,h=(9/25,93/500,561/10000),D=427/600,k=(76/75,543/1000,22133/60000),minimum1/4를 정확한 손계산으로 확인했다. F(4/5)=-999/160000,F(9/10)=1161/160000 및 affine derivative도 맞는다. 이 예제는 독립적인 알려진 답을 가진 구성이고 실제 EXFOR 데이터를 대신하지 않는다.

## 구현·검증·실행 경로

Producer는 두 입력 SHA256과 고정258MeV/free_N16 identity를 확인한다. Exact rational root enclosure,3×3 residual/sign checks,all4contracted windows,coefficient box/Dfloor,이전 정점 membership,M_j,Delta_k,signed witness ratio,최종폭/이전구간 포함을 실제 조건으로 검사한다. Scientific arithmetic은 Fraction이다.

Saved-certificate reader는 producer/search/elimination을 부르지 않고 source-bound rows,root inequalities,dual identity,feasible square,finite M envelope 및 최종 endpoints를 독립적인 algebra/inequality 경로로 검사한다. 정점의 완전성은 기존 pin된 검증의 재사용이며 새 reader가 재열거했다고 쓰지 않는다.

8개 unittest method는 알려진 rational root/linear system,negative/singular controls,손계산 signed moment reference,actual certificate 및 corruption controls를 포함한다. Worker는 actual construction을 한 번 수행한 뒤 저장 결과를 검사한다. C6–C8이 세 개의 재실행을 뜻하지 않는다.

Wrapper는 새 output directory를 독점 생성하고 thread1/AS768MiB를 적용한다. CPU는 전체 누적 parent RUSAGE_SELF와 waited-child CPU를 더하므로 startup을 포함한다. Wall 측정은 명시된 prelaunch checkpoint부터 child completion까지이며 whole-session 시간으로 표현하지 않는다. 최종 PASS는 exitcode·CPU cap·wall cap 모두를 검사한다. Validation120CPU/300wall 및 별도 saved plot10CPU/30wall 계약과 일치한다. Plotter는 저장값만 읽으며 scientific producer를 import하지 않는다.

CAS_SUBMITTED.wl은 generic polynomial identity와 제조된 exact certificate의 별도 검산 코드다. 실제 provider 결과는 이후 같은 pass에서 읽는다.

## 닫힌 지적

- F1: shortest binary64 decimal 대신16자리 exact decimal gridfloor/ceil을 사용한다. Reader가 decimal string을 Fraction으로 읽어 방향을 검사한다.
- F2: runner startup CPU를 포함하고 final wall cap 검사를 추가했다. 측정 wall scope를 명시했다.
- F3: 그림의3자리 width는 `Bracket width ≈`로 표시한다.
- F4: inherited QUARTIC12 evidence7개에 원래 sibling directory prefix를 붙였다. 기존 결정·상태는 보존했다.

## 남은 동일-pass 확인

S05 실제 pin과 START/source hashes의 일치,단일 campaign의 raw output 및 resource receipt,실제 CAS 결과,저장값만 그린 PNG와 plot receipt,최종 source/central 전달의 claim 경계를 확인한다. 추가 과학 실행이나 새 audit layer를 요구하지 않는다.

현재 Local **12/17**, Central **28/88**, HE delta0이다. Scoped 결과 수용 전 TANGENT13 node는 pending이다. 원래 세 물리 입력과 `population_rest_energy_witness`의 단독 binding ownership,지정된 null,global completionnull/L4false/productionNOT_APPROVED/activationfalse를 유지한다.

