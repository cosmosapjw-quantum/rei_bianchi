# S06 — 새 구현 실제 검증

고정 Local S05 `0529ce44d5fca255befbd6b7e1007b40c768feed`, remote same-tree `920519403c80285174c8154e92c9ae8a1e82f2cb`, tree `76c88b7feb60d9afe01064a066f41d698f72fd1d`에서 첫 새 suite를 실행했다. 결과는 **22/22 PASS, failures0/errors0, exit0**다. 검증 source와 이후 evidence/채택/publication commit을 혼동하지 않는다.

전체 runner 및 waiteddescendants CPU **0.782465/12s**, wall **0.8201407000015024/40s**, peak RSS15,616KiB, 별도 outerCPU0.004261523000000003s다. Suite 자체 CPU0.5423855750000001s/wall0.5440729290130548s. Wrapper1/sciencesuite1/repair0이며 reserve1은 사용하지 않았다. 그 잔량을 새 노드나 재실행에 자동 배정하지 않는다. 원 stdout/stderr, START, wholeprocessreceipt, TEST_REPORT가 evidence/에 있다.

22method는 원주 empty/full/seam, oppositequarters, overlappingassignmentOR, same-daughterfalsecoincidence,wrappedgeometry,mixedpolar11/204,fullazimuth동일manualδ회귀,patchunion,sectorrotation17점,detectorswap,zero/invalid/overlimit,manualδ,denominatorstatus,fold/stopped,degree8/8windows,native3energyrows,stripcountclosure를 판별했다. 기대값은 독립exactgrid/해석값이며 smoke만으로판정하지않았다.

Four diagnostic controls의 actual C / 잘못된 값은 halfturn누락1/2대0,independentmarginal1/2대1/8,assignments합1대2,bothhits대입0대1이다. 추가hitproduct1/4도보존했다. 이는 동일실행에저장된counterfactualdiagnostic이며별도mutatedimplementation campaign을실행했다는뜻은아니다.

Manualδ1/16의HitA폭은 **1/24**, 반환width_bound도1/24다. 같은선언geometry의default폭은 **1/26388279066624 ≈3.78956e-14**. 이예의C는두경우모두정확0이므로폭비교그림은HitA를표시한다. 이를coincidence폭변화로오표기하지않는다. Ratio는자체반환폭/status로판정한다.

Degree8/8windows case는32strips,48comparisons,foldbisections392,**boundarybisections0**을기록했다. 따라서그case는positiveboundary-root iteration을empiricallystress한시험이아니다. 최대50회의일반상계는THEORY의정확유도에서온다. Native3개case는각boundarybisections92를기록했다. 타이머0 CPU관측은해상도값이지zero-cost주장이아니다.

NIST정확선언mass와제조ρ=[0,3/2,0],explicitfinitesectors에서표시midpointY는213MeV0.04549154153823495,258MeV0.04312933465472360,330MeV0.03985114599133981이다. 실제exactbounds는savedJSON에있고각폭은약6.45665e-15,6.31476e-15,6.10827e-15이다. 원DCS12점을적분하거나물리rate를인증한값이아니다.

저장plot입력SHA256은 `8d37a7cb3bc3ac69f06f80c4c5a1a4bc0341275fe95523cbe76c3ac2fb0ddb0e`. 17rotationrows,4controls,22timingrecords및native/bounds/closure를같은suite에서저장했다. Plot은이S06시점에아직실행전이며 별도S07sourcepin후저장값만읽는다. 현재로컬8complete+1partial+1pending+3open/13,중앙28/88HEdelta0이다.
