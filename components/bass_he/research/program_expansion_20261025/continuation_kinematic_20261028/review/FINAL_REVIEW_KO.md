# KINEMATIC08 최종 독립 검토 — pass1 종료

## 판정

**ACCEPT_SCOPED_PHYSICAL_INPUT_REFERENCE_WITH_WORKFLOW_PARTIAL**.

정확하게 선언한 물리 입력에서 full-azimuth polar-window 조건부 경계를 계산하는 참조 구현의 과학 범위는 수용한다. 실제 새 테스트14/14와 검증 예산은 PASS다. 저장값 plot은 생성됐고 시각적으로 일관되지만 **whole-process CPU7.040661s가 고정6s 한도를 초과**했다. 전체 workflow는 **PARTIAL**이며 새 노드를 complete로 계산하지 않는다.

권고 DAG는 **8 complete +1 partial +3 physical open /12**, 완료 표기는 **8/12**다. 중앙 intake28/88에 대한 허용 HE 완료 delta는0이다. Global physical completion=null, L4=false, production=NOT_APPROVED를 유지한다.

## 검토 범위와 정확한 개수

기존 독립 정적 검토의11개 aspect와 이번 실제 결과 검토12개를 같은 review_pass=1에서 마무리했다. 기존 정적 finding2개는 종료했다. 실제 결과 체크는 **11 PASS +1 FAIL**이며 실패1개는 plot 자원 한도다. 미해결 과학·코드 finding은0이다. 실제 체크 수는 preplot 체크리스트의 완료9개를 유지하고 대기 중인 plot 항목을 provenance·visual·resource 세 개로 확인한 결과다.

검토자는 새 과학·테스트·plot·Wolfram을 실행하지 않았다. 새 별도 검토 캠페인이나 과학 재실행을 만들지 않았다.

## 실행 신원과 검증

- 실제 검증 Local S05R: `d004212d560907eb4058d9539eec8e9b262ec406`.
- 같은 tree 게시: `391f1e4c356082c0b5cc693d49fb2aef873a0f2a`.
- plot 실행 Local source: `cc84f0816ba640c97ef05348d8a7fb5c2893b833`.
- 검증·plot START의 코드 SHA2566개는 각각 immutable git blob과 모두 일치하고, 두 실행 사이 과학 코드는 같다.
- APERTURE07 continuation 전체는 D10부터 S05R까지 diff가 비어 있다.

첫 wrapper 실행은 Git threaded-lstat 환경 오류로 과학 child 전에 실패했다. 원 FAIL을 보존했고 command-local Git threading 한 줄을 고친 뒤 과학 suite를 한 번 실행했다. **wrapper2회 / 환경 repair1회 / 실제 과학 suite1회 / 과학 repair0회**다.

두 wrapper의 누적 whole-process 비용은 CPU **0.466246/10s**, wall **0.5354680930031464/30s**다. 별도 outer main-body CPU는0.018585141999999992s이다. 예산 초기화·이전은 없다.

원 stderr 및 보고서는14/14 PASS, failures0,errors0에 일치한다. 다섯 counterfactual witness는 부호 손실, fold strip 누락, 정규화2배, 독립 marginal 곱, 잘못된 에너지 계수를 구분한다. 이를 executed mutation-testing campaign으로 표현하지 않는다.14개 timing 기록은 같은 suite에서 얻었고 짧은 CPU0 관측은 측정 해상도로 해석한다.

## 저장 plot 판정

입력 SHA256은 검증 때 한 번 만든 값과 정확히 같다.

`73a2f33e651ec87890a48e8a4f10ff4a5362efce30555409718ff3d99d19e7ae`

plot script는 과학 모듈을 import하지 않고 scientific function calls0이다. 기존 PNG를 read-only로 보았다. 네 패널의 축·범례·라벨은 잘려 있지 않고 제조 밀도라는 설명을 유지한다. 예제의 HitA와Y 중첩은 저장값과 일치하며 manualδ=1/16이 default epsilon을 초과하는 그림도 정확하다. stopped endpoint를 방향값으로 채우지 않았고 pair-energy/Y는G와 일치한다.

plot child는 exit0으로 SVG·PNG를 만들었지만, inner acceptance와 outer wrapper는 자원 초과를 반영하여 FAIL/exit1이다. whole CPU **7.040661>6s**, wall **7.286283305002144<=15s**, peak RSS64780KiB, timeout없음이다. 별도 outer main-body CPU는0.035214637s다. 생성된 그림은 실패한 자원 시도의 유효한 증거이며 cap PASS로 바뀌지 않는다. 재실행·repair·예산 확장을 하지 않는다.

## Wolfram과 주장 경계

기존1회 Wolfram 출력에서 보존된 값은15잔차 중12개 literal0,3개 미정리 유리식,sign11개 일치다. 미정리 식3개는 독립 직접 통분으로0임을 확인했다. 원 tool envelope는 continuation 전에 디스크에 보존되지 않았으므로 현재 JSON은 명시적인 대화 결과 전사다. 이를 raw receipt로 표현하거나15개 literal0이라고 쓰지 않는다. 실제 원격 CPU는null이며 두 번째 호출은 없다.

새 참조의 수용 범위는 정확 선언A,M,e, 정지 bare target의 같은 질량 두 딸입자, 연속 측도, degree<=8 비음수 Bernstein 밀도, full-azimuth polar windows이다. 물리 입력 측정 불확실성, finite-azimuth geometry, empirical DCS 정규화, 실제 flux/history와 열적 deposition은 수용하지 않았다. Binding owner는 `population_rest_energy_witness` 한 번이며 thermal ports=null,birth_pool=UNASSIGNED를 유지한다.

S06 validation 문서의 `plot_status=NOT_YET_RUN`은 그 생성 시점 snapshot이다. 최종 현재 상태는 S08 실제 plot receipts와 본 검토의 **PARTIAL**을 따른다. Root는 이 판정과 실제 게시·백업 영수증으로 S09/S10을 종료하며 자동 후속 노드나 재실행을 시작하지 않는다.
