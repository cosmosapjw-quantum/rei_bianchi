# AZIMUTH09 정적 독립 검토 — pass 1

시각: 2026-10-27 21:00:34 UTC. 검토자 `/root/he09_code_review`. 이전 `PRECONTRACT_REVIEW_KO.md`의 같은 pass를 실제 source·tests·runner·plot 준비로 이어갔다. Science/test/plot/Wolfram 실행은 모두 **0회**다.

## 판정

**PASS_SCOPED_STATIC**. 최초 판정은 HOLD_TARGETED_TEST_ORACLE_CORRECTION이었고, 테스트 oracle 오류 **F01 한 건을 같은 pass 1에서 종료**했다. 과학 API의 정확 구간·사건·오차 알고리즘 및 변경된 assertion에 미해결 지적이 없다. 이는 사전 정적 교정이며 관측된 실행 실패나 실행 repair reserve 소비가 아니다.

## F01: 원주 각도 비교의 seam — CLOSED_PREEXECUTION

대상은 `tests/test_azimuth.py::test_19_fold_stopped_and_direct_lorentz_geometry`다. 현재 코드는 두 `atan2` 결과를 각각 `% (2*pi)`로 줄인 뒤 ordinary-real `assertAlmostEqual`로 비교한다. 이 테스트가 실제 구성하는 strip에는 `t=1/2`가 들어간다. 그 근처에서 동등한 방향이 `0`과 `2*pi`의 양쪽 값으로 표현될 수 있어, 원주상 같은 방향에 대해 잘못된 FAIL을 낼 수 있다.

최소 교정은 기존 정확도 `places=12`를 유지하고

```python
math.remainder(math.atan2(-y, -x) - math.atan2(y, x) - math.pi, 2*math.pi)
```

를 0과 비교하는 것이다. 과학 API, 물리 모형, 허용오차, 예산은 바꾸지 않는다.

**종료 확인(2026-10-27 21:17:06 UTC):** 실제 수정된 assertion을 읽었다. 새 test 파일 SHA256은 `5a8b4f8cec55723e4aa2f10d7c496a3d645fefa62a6a52de4b7bf17a9cbecc2e`다. 해당 한 assertion만 원래 표현으로 되돌린 바이트의 hash가 기존 `cd7ab85b69d60535c871b2b5c682b1ea539c150958f5921addc545b15c3ee851`와 일치하여 승인된 변경만 들어갔음을 확인했다. main 과학 source hash `3230b6ec029b5eb2b40acd3f2dfc603930b470e59e85e6693fd326fb01335ccf`는 유지됐다. Science/test/plot/Wolfram 실행은 여전히 모두0회다.

## 수학 → 코드 확인

1. **운동학·측도:** 선언한 A,M,e와 inherited F를 사용하며 minus는 `F(-mu)`, azimuth는 반회전이다. `UNIFORM_DECLARED`를 필수로 받고 짝 Bernstein density를 검사한다. empirical DCS에 임의 2π 또는 동일입자 계수를 적용하지 않는다.
2. **원주와 strip:** 유리수 `(start,width)`의 empty/full/seam이 분리된다. 모든 원래·반회전 arc endpoint를 수집하므로 열린 strip에서 azimuth mask는 상수다. midpoint 사용은 정확 mask 선택이며 μ quadrature가 아니다.
3. **집합·사건:** `SetBounds`의 inner/outer union/intersection으로 duplicate/overlap을 합성한다. coincidence OR, assignment 합, both-detector hit, inclusive daughter count를 분리한 구현은 고정 계약과 일치한다.
4. **폭:** 서로 다른 N개 polar window의 uncertainty와 reflection 합집합 밖에서는 모든 Boolean 결과가 결정된다. 따라서 area≤10Nδ, measure width≤B area≤10NBδ다. default와 N≤8, degree≤8에서 최대50회 root bisection 유도도 맞다. Inclusive/assignment 합과 에너지 출력은 각 구성 bound를 scale하며 동일 epsilon을 일괄 적용하지 않는다.
5. **에너지·조건부:** J(mu,t)=(-mu,t+1/2) 아래 C와 measure가 보존되므로 ∫C μ dm=0이다. 이에 따른 2Y, GY, GY/2가 구현됐다. 양의 denominator lower에서만 조건부 비율을 계산하며 zero/unresolved를 분리한다.
6. **독립 기준값:** `direct_grid`는 생산 preimage/integrator를 호출하지 않는 exact cell enumeration이다. 반대 quarter-sector Y=1/2, full-overlap C1/assignments2, 같은 half-sector C0/both-hit1, mixed-polar Y11/204·hitA91/204·pair-energy11/36 등의 기준값이 구현을 구별한다. F01을 제외한 테스트 계약은 필요한 새 의존성을 대상으로 한다.

## 실행·산출물 경계

`run_bounded.py`와 `measure_execution.py`는 HEAD/source tree·현재 hash·tracked clean을 확인한다. 새 validation12CPU/40wall, plot8CPU/20wall, AS512MiB **각 process**, singlethread를 기록한다. 완전한 runner subprocess와 기다린 descendants 비용을 측정하고 outer bookkeeping을 따로 기록한다. 최종 외부 metadata serialization을 재귀적으로 포함한다는 주장은 없다. 선제 CPU limit은 각각의 process limit이며 aggregate CPU 판정은 관측된 합계로 한다.

`validate_once.py`는 같은 한 suite에서 plot JSON·test timings·native rows·counterfactual diagnostic controls를 저장한다. 별도 mutation campaign을 수행했다고 쓰지 않는다. `plot_saved.py`는 저장 JSON만 읽고 과학 모듈을 import하지 않는다. 실제 그림의 가독성/의미와 resource 판정은 아직 실행되지 않아 후속 같은 pass에 남는다.

읽은 code hash와 12개 정적 aspect는 `STATIC_REVIEW.json`에 있다. inherited KINEMATIC08/APERTURE07 두 디렉터리는 baseline `b3ac835c3fa0b1aa09606ab6e8cfdc08699bab25` 대비 Git diff가 비어 있다. 선행 KINEMATIC08 과학14/14 PASS, plot **7.040661/6 FAIL**, workflow PARTIAL, reserve0을 그대로 보존한다.

## 다음 행동

F01은 종료됐다. 다음 행동은 root가 검토된 source를 고정한 새 validation이다. 실제 결과가 나오기 전 수치 검증이나 plot PASS를 주장하지 않는다. 새 검토 pass나 기존 suite 재실행은 요구하지 않는다.

