# S07 — 독립 판별 검산과 물리 해석

새 exact finite-sector 구현의 science suite22/22와 독립 same-pass preplot10/10 확인을 통과했다. 실행신원은S05이며S06/S07게시commit은그실행후기록이다. Root의새Wolfram evaluator호출은1회,timeConstraint15s이고 원 tool envelope를 `evidence/WOLFRAM_RAW.json`에즉시보존했다. ParsedJSON과입력코드SHA를연결했으며원격CPU측정은제공되지않아null이다. `WolframContext` 검색1회는분리된contextretrieval이며무관한query결과를과학근거로채택하지않았다.

## 실제 상징 출력

| 검산 그룹 | 잔차 수 | 실제 결과 |
|---|---:|---|
| transverse halfturn sin/cos | 2 | literal0 |
| 4개membership bit의16조합에서6개event/count/subset/교환identity | 96 | literal0 |
| label energy합과교환 | 2 | literal0 |
| 제조mixedpolar의Y,hit,ratio,count,energy정확값 | 8 | literal0 |
| quarter-sector균일상대회전평균 | 1 | literal0 |
| 합계 | **109** | **109literal0** |

추가worstcase이분비교2개는True다. 이번109잔차는유한Booleanlaw와새phase/observable연결의검산이며일반포함정리의증명은THEORY_KO.md §4에있다. 이전KINEMATIC08의12literal0+3직접통분기록을이번109개로덮어쓰지않는다. 원code/evidence회수없이이전실행을재현했다고주장하지않는다.

## 회전 그래프 좌표와 평균화 조건

저장scan의x축α는Bsector의**절대시작turn**이다. A=[0,1/4), B=[α,α+1/4)에서

\[
Y(\alpha)=2\max(0,\tfrac14-|\alpha-\tfrac12|),\quad0\le\alpha\le1.
\]

중앙α1/2의반대배치에서Y1/2이고α0/1에서는0이다. CAS입력은반대배치에서의상대shift `d=(α−1/2) mod1`을썼으므로peak가d0에있다. 두표현은원주의동일함수이며 x좌표의원점을구분한다.

고정배치의independentmarginal값1/8은일반coincidence값이아니다. 반면B의상대방향까지별도로균일하게평균하면 `∫_0^1Y(α)dα=1/8`이되어그곱과일치한다. 이일치는추가orientation평균의결과다. 실제저장17점은함수값검증이며사다리꼴수치적분으로일반법칙을증명하지않았다.

## 검증이 지지하는 범위

정확선언A,M,e,openchannel,evenBernsteinρ,UNIFORM_DECLAREDφ,유리수직사각형patchunion에서shared-event포함경계를수용할근거를확보했다. 중복patch·detectoroverlap·seam과conditionalzero/unresolvedstatus를포함한다. Counterfactualcontrols는특정잘못된모델의출력차이를보존한다.

Count2Y,rest를포함한pairGY,labelGY2는선택된coincidence의관측량이다. 실제핵반응률·Cv·deposition을제공하지않는다. 실험적편광/φ-law,실제telescope곡선기하·efficiency,parameter불확실성,원M0475002정규화,flux/history와nonthermal입력은기존열린의무다. 분모가작은조건부확률에는반환ratio폭만적용한다.

## 다음 실제 실행

S07게시후그Local source에서 `scripts/measure_execution.py --mode plot`을한번실행한다. 입력은이미저장된JSONSHA `8d37a7cb3bc3ac69f06f80c4c5a1a4bc0341275fe95523cbe76c3ac2fb0ddb0e`; solver/science import와호출0,새test0. 새plot CPU8s/wall20s/AS512MiB는사전계약값이고이전FAIL은그대로다. 생성PNG를root/독립reviewer가실제로읽은후R8/C8과최종판정을진행한다.
