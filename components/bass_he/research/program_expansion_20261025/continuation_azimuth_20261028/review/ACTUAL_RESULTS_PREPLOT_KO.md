# AZIMUTH09 실제 검증 결과 검토 — plot 전, pass 1

시각: 2026-10-27 21:24:11 UTC. 검토자 `/root/he09_code_review`.

## 판정

**PASS_SCOPED_VALIDATION_PREPLOT**, 실제 결과 aspect **10/10 PASS_SCOPED**, 미해결 finding0. 정적 F01은 같은 pass에서 교정·종료됐고 실제 suite에서는 해당 test19도 PASS다. 검토자가 추가 science/test/plot/Wolfram을 실행하지 않았다. 기존 로그·결과·Git source bytes만 읽었다.

## 실제 실행과 신원

실제 Local S05 `0529ce44d5fca255befbd6b7e1007b40c768feed`, remote same-tree `920519403c80285174c8154e92c9ae8a1e82f2cb`, exact tree `76c88b7feb60d9afe01064a066f41d698f72fd1d`를 구분했다. START에 적힌 코드6개의 SHA256이 immutable S05 blob과 모두 일치했다.

원 stderr에는 새22개 test method가 각각 ok로 기록돼 있다. TEST_REPORT는 tests_run22, failures0, errors0, scientific_suite_runs1이다. Inner/outer exit0, timeoutfalse, bootstrap stderr0bytes다. 실행 repair0, reserve1이며 이전 suite 재실행0을 유지한다.

| 계측 | 실제 결과 | 고정 기준 |
|---|---:|---:|
| Whole runner CPU | 0.782465 s |12 s |
| Whole runner wall |0.8201407000015024 s|40 s|
| 별도 outer bookkeeping CPU|0.004261523000000003 s|별도 범위|
| 관측 peak subprocess RSS|15,616 KiB|AS limit512MiB/process|
| Suite 내부 CPU/wall|0.5423855750000001 /0.5440729290130548 s|whole에 포함|

계측 경계는 전체 runner subprocess와 기다린 descendants이며 outer bookkeeping은 따로다. AS와 선제 CPU limit은 process별이고 aggregate CPU 수용은 실제 합계 관측값으로 판단한다.

## 수치·의미 확인

- **회전:** 17개 rational offset의 full-polar quarter-sector coincidence가 정확 삼각형 기준과 일치했다. 중심 offset1/2에서Y1/2, offset≤1/4 또는≥3/4에서0이다. 공통 회전 불변성도 같은 suite의 test10에서 확인됐다.
- **사건과 계수:** 반회전누락 `1/2 vs0`, 독립 marginal곱 `1/2 vs1/8`(hit곱1/4), assignment단순합 `1 vs2`, both-hit를서로다른딸 coincidence로치환 `0 vs1`의 네 저장 counterfactual witness가 실제 출력과 구별된다. 별도 mutatedimplementation 실행 campaign으로 부르지 않는다.
- **혼합 극각 기준:** raw interval은Y11/204,hitA91/204,hitB11/204,pairenergy11/36,labelenergy11/72를 포함한다. Y의 저장 폭은 `1/70368744177664`다. Full-overlap은C1,assignment2,overlap1을 정확 반환했다.
- **조건부:** test06은11/91및1이 반환 ratio enclosure에 포함됨을, test18은positive/zero/unresolved분모 상태를 확인해PASS다. 실제 ratio rational endpoint는 saved plot JSON에 별도 직렬화되지 않았으므로 위 값은 정확 해석 기준값과 성공한 포함 검사로 표현한다.
- **수동 δ:** hitA default폭은 `1/26388279066624`. 수동δ1/16의hitA는 `[17/48,19/48]`, actualwidth와width_bound 모두 **1/24**다. 이 사례의 coincidence는 양쪽δ에서0이므로 hitA의 비영폭을 명시한다. 기본epsilon을 이 수동δ결과나조건부ratio에확대하지 않는다.
- **Native scalar 예:** NIST 고정바이트 SHA `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`와 선언 rest energy를 test21에서 확인했다. rho[0,3/2,0]·sigma1·유한sector는 제조한 입력이며 empiricalDCS가 아니다. 213/258/330MeV의C는 각각 약0.045491541538235,0.043129334654724,0.039851145991340이고 actualwidth는6.45665e-15,6.31476e-15,6.10827e-15다. 에너지/count출력은 저장된bounds를 정확한G와2로scale했다.

## Degree8/N8 관측의 범위

저장 관측은 **boundary_bisections0, max boundary iterations0, fold_bisections392, comparisons48, windows8, strips32**다. 따라서 test20의50회 assertion은 비영 boundary-root workload에 대한 worst-case stress 근거로 표현하지 않는다. 이 구성에서fold격리와N/δ정의역 및 guard가 실행된 것은 사실이다.

최대50회 결론은 정적·이론 증명에 근거한다. `B/sigma≤9/2`, `N≤8`이므로 `delta≥1/(360*2^40)`; 길이≤2 bracket의 이분이50회면 충분하다. 별도 native3행에서는 각각 boundary_bisections92가 관측되어 새 연결 안의 비영 boundary 계산도 수행됐다. 현재 정확성 위험이나 미해결 지적을 만들지 않으므로 이 사유만으로 추가 실행을 권고하지 않는다.

## 저장값과 다음 행동

같은 suite에서 생성한 `SAVED_PLOT_DATA.json` SHA256은 `8d37a7cb3bc3ac69f06f80c4c5a1a4bc0341275fe95523cbe76c3ac2fb0ddb0e`다. 회전17행,native3행,control4개,timing22행,stripprovenance6행이 있다. CPU0의 짧은 timing은 timer해상도이며zero-cost근거가아니다.

이 검토시점에서 plot은NOT_RUN, Wolfram은root실행중이며아직검토하지않았다. 다음행동은고정된saved-onlyplot1회와그실제resource/이미지판정이다. 검증suite재실행없이같은pass에서이어간다. 기존KINEMATIC08plot7.040661/6FAIL및partial,APERTURE07PASS,PHOTON05FAIL,HE101상태는변경하지않는다.

