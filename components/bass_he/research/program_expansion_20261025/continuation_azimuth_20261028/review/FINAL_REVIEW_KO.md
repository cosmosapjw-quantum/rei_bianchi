# AZIMUTH09 독립 최종 검토 — 같은 pass 1

**판정: `PASS_SCOPED_FINITE_AZIMUTH_REFERENCE`.** 명시한 모델·측도·검출기 범위에서 새 참조 노드를 채택할 수 있다. 정적 항목 **12/12**, 실제 결과 검토 항목 **14/14**가 통과했다. 실행 전 테스트 oracle finding F01 한 건은 승인한 한 assertion의 수정으로 닫혔고, 현재 blocking finding은 **0**이다. 검토자가 추가로 실행한 science·test·plot·Wolfram은 모두 **0회**다.

이 문서는 계약, 코드, 실제 원 로그·JSON 및 원 PNG를 이어 읽은 **하나의 검토 pass 1**의 종결 기록이다. 앞선 `STATIC_REVIEW`, `ACTUAL_RESULTS_PREPLOT`, `SYMBOLIC_REVIEW`는 작성 당시의 상태를 보존한다. 특히 preplot 문서의 NOT_RUN, `PLOT_RESULT.json`의 당시 pending 표시는 후속 실제 결과를 부정하지 않는다.

## 실행 신원과 자원 결과

| 구분 | 실제 Local 실행 commit | Remote same-tree 게시 commit | Exact tree |
|---|---|---|---|
| 검증 S05 | `0529ce44d5fca255befbd6b7e1007b40c768feed` | `920519403c80285174c8154e92c9ae8a1e82f2cb` | `76c88b7feb60d9afe01064a066f41d698f72fd1d` |
| 저장값 plot S07 | `2fbe4657b480149b393c54cac6009feb4fd05ac6` | `4750c693cfb51433060db10ad81c8732382f3f17` | `40c6184a0a4cf5ac04c1a2428015659b3709c3f8` |

검증과 plot의 실제 Local 신원을 Remote 게시 신원과 구분했다. S05 원 blob 6개는 앞선 실제 결과 검토에서 확인했고, S07의 tree 및 6개 원 blob은 이번 읽기 전용 검증에서도 reviewed hash와 전부 일치했다. 상속 KINEMATIC08/APERTURE07 과학 소스는 baseline에서 바뀌지 않았다.

| 실제 작업 | 결과 | Whole CPU / cap | Whole wall / cap | Peak RSS | 시도·repair |
|---|---|---:|---:|---:|---|
| 새 검증 suite | **22/22 PASS** | 0.782465 /12 s | 0.8201407000015024 /40 s | 15,616 KiB | 첫 1회, repair 0, reserve 1 |
| 저장 JSON plot | **PASS** | 2.053974 /8 s | 2.124947346004774 /20 s | 61,512 KiB | 첫 1회, rerun 0, repair 0 |

Whole 측정은 `run_bounded.py`의 Python 시작, waited descendants, 내부 영수증 및 종료를 포함한다. 바깥 metadata 기록의 CPU는 검증 0.004261523 s, plot 0.008875835 s로 따로 보고했다. 주소 공간 제한은 **프로세스당 512 MiB**, single-thread다. 두 실제 실행 모두 exit 0, timeout false다. F01의 수정은 첫 실행 전 테스트 oracle 수정이므로 과학 실행 repair reserve를 쓰지 않았다.

Plot은 기존 font cache가 있는 실제 환경에서 측정했다. cold font scan 측정이나 과거 plot 대비 성능 향상을 주장하지 않는다. 이전 suite 또는 이전 plot을 재실행하거나 기존 예산을 초기화·이전한 사실은 없다.

## 검토 항목

### 정적 12개 항목

| ID | 검토 대상 | 판정 |
|---|---|---|
| S01 | A,M,e physical model, transverse antipode, F(-mu) | PASS |
| S02 | Declared uniform azimuth, even Bernstein density, measure normalization | PASS |
| S03 | Rational arc full/empty/seam and halfturn | PASS |
| S04 | Exact azimuth sweep and inner/outer union/intersection | PASS |
| S05 | Distinct daughters, hit vs count, OR vs assignments | PASS |
| S06 | Event uncertainty area,10NBdelta,default epsilon,max50 | PASS |
| S07 | Count/energy scaling and label exchange symmetry | PASS |
| S08 | Conditional denominator statuses and subset ratio | PASS |
| S09 | Independent exact grid/analytic oracles and invariance tests | PASS |
| S10 | Source pin, identity and protected prior sources | PASS |
| S11 | New bounded execution and honest resource scope | PASS |
| S12 | Same-run saved payload, diagnostic controls and saved-only plot | PASS |

F01은 주기적 방위각 두 값을 각각 [0,2π)로 줄인 뒤 실수 거리로 비교하던 테스트 표현 문제였다. 승인된 수정은 `math.remainder(atan2(-y,-x)-atan2(y,x)-pi, 2*pi)`를 기존 `places=12`로 0과 비교하는 것뿐이다. 수정 테스트 SHA256은 `5a8b4f8cec55723e4aa2f10d7c496a3d645fefa62a6a52de4b7bf17a9cbecc2e`이며, 이 assertion을 되돌리면 원래 파일 hash가 재현됨을 확인했다. 과학 알고리즘·허용오차·예산 변경은 없었다.

### 실제 결과 14개 항목

| ID | 검토 대상 | 판정 |
|---|---|---|
| V01 | Local execution identity vs remote same-tree publication | PASS_SCOPED |
| V02 | One actual suite22/22; corrected seam oracle | PASS_SCOPED |
| V03 | Frozen validation resource gates | PASS_SCOPED |
| V04 | Finite-azimuth rotation and counterfactuals | PASS_SCOPED |
| V05 | Analytic mixed polar and energy/count closure | PASS_SCOPED |
| V06 | Conditional ratios and denominator statuses | PASS_SCOPED |
| V07 | Default/manual actual bounds | PASS_SCOPED |
| V08 | Three declared native mass/energy finite-sector rows | PASS_SCOPED |
| V09 | Degree8/N8 iteration scope | PASS_SCOPED_WITH_STATED_TEST_LIMIT |
| V10 | Same-run saved data and timing/provenance | PASS_SCOPED |
| W01 | One actual Wolfram result, original envelope and formula scope | PASS_SCOPED |
| P01 | Saved input, exact plot source and output identity | PASS_SCOPED |
| P02 | One actual plot resource outcome | PASS_SCOPED |
| P03 | Original PNG scientific meaning and visual legibility | PASS_SCOPED |

14개는 검토 범주의 수다. 실제 Python 테스트 방법은 22개이고, symbolic 잔차는 아래 109개이므로 이 세 수를 섞지 않는다.

## 실제 결과 해석

유리수 17개 방위각 위치에서 exact triangular coincidence oracle과 저장된 certified C가 일치했다. 네 counterfactual witness는 halfturn 누락(0.5 대 0), 독립 사건 가정(0.5 대 0.125), assignment 합을 사건으로 셈(1 대 2), 두 검출기의 hit를 서로 다른 두 daughter의 coincidence로 셈(0 대 1)을 각각 구별한다. 이는 저장된 진단 witness이며 별도의 mutation campaign을 실행한 기록이 아니다.

독립적인 manufactured mixed-polar oracle은 C=11/204, HitA=91/204, pair energy=11/36, 각 label energy=11/72를 준다. 실제 suite의 test06은 이 목표값의 enclosure를 확인했고, 조건부 목표값 11/91 및 1도 반환 구간에 포함됐다. test18은 denominator의 positive/zero/unresolved 상태를 확인했다. 조건부 반환 구간의 exact endpoint는 plot JSON에 별도로 저장되지 않았으므로 목표 분수 자체를 저장된 반환 점값으로 부르지 않는다.

Native scalar 세 사례(213, 258, 330 MeV)는 선언된 NIST scalar mass와 manufactured rho=[0,3/2,0], sigma=1, uniform azimuth를 쓴다. C의 저장 구간은 각각 약 [0.045491541538231726,0.04549154153823818], [0.04312933465472044,0.04312933465472676], [0.03985114599133675,0.039851145991342866]이다. 선택한 검출기 기하에서는 C와 HitA가 같고 HitB는 다르다. 이는 empirical DCS 정규화나 실제 물리 사건률 결과가 아니다.

Degree-8/N=8 사례의 관측은 boundary bisections **0**, 최대 root iteration **0**, fold bisections **392**, comparisons **48**, strips **32**다. 해당 사례는 허용 구성과 guard를 확인하지만 양의 경계 반복을 쓰는 worst-case stress는 아니다. 길이 2 이하의 bracket과 delta≥1/(360·2^40)를 쓰는 **50회 상한은 해석적 증명**이며, CAS의 두 정수 비교가 이를 지원한다. 세 native 사례는 각각 boundary bisections 92회를 실제로 기록했다. 이 제한을 명시하면 남은 correctness risk 때문에 추가 실행할 사유는 없다.

## Wolfram 원 응답

실제 evaluator 호출은 한 번, 설정 time constraint는 15 s였다. 원 envelope의 Out[1]을 이중 JSON decode한 값이 parsed 결과와 같음을 확인했다. **109개 literal integer residual이 모두 0**이다: transverse phase 2개, 16 Boolean vertex ×6 identity=96개, energy algebra 2개, manufactured exact-oracle difference 8개, continuous rotation-average 1개. 이분 반복 상한의 두 비교도 True다. 실제 원격 CPU는 제공되지 않아 **null**을 유지한다.

Wolfram은 opposite 배치로부터의 상대 offset d를 쓰고 저장 scan은 B-sector 시작점 alpha를 쓴다. d=(alpha−1/2) mod1이므로 각각 peak d=0과 alpha=1/2는 같은 배치다. 회전 평균은 1/8이다. Label energy GY/2는 두 algebra 잔차만으로 증명되는 것이 아니라 J(mu,t)=(-mu,t+1/2)에 대한 C의 불변성, even rho 및 첫 mu moment 소거를 함께 사용한다.

## 원 PNG 시각 검토

원본 `evidence/plot_attempt1/AZIMUTH09.png`(990×660)를 직접 열어 네 패널을 확인했다. 재렌더링·재계산은 하지 않았다. 제목·축·legend·scope footnote가 읽히며 clipping이나 의미를 바꾸는 겹침은 없다.

| 패널 | 실제 확인 |
|---|---|
| 좌상단 | 검은 exact triangle과 certified C의 17개 위치가 맞는다. alpha=1/2에서 peak 1/2다. |
| 우상단 | 네 manufactured event/count counterfactual 쌍이 저장값과 일치하며 서로 다른 오류를 구분한다. |
| 좌하단 | Native 3개 에너지의 C와 HitA overlay는 선택한 기하의 동일 측도를 반영한다. HitB가 별도 곡선으로 구별된다. |
| 우하단 | **HitA**의 default/manual 실제 폭과 returned bound가 표시된다. 조건부 ratio에 epsilon을 약속하는 그림이 아니다. |

우하단의 default HitA width=bound는 1/26388279066624 ≈3.78956e−14다. 수동 delta=1/16에서는 HitA=[17/48,19/48], width=bound=1/24다. 같은 두 비교 사례에서 C는 exact 0이지만, 그림은 의도대로 HitA의 폭을 그린다. default sigma/2^40 기준선을 수동 delta나 ratio의 일괄 보장으로 해석하지 않는다.

실제 읽은 파일의 SHA256과 크기가 `PLOT_RESULT.json`의 10개 파일 기록에 모두 일치했다. 핵심 hash는 다음과 같다.

| 파일 | SHA256 |
|---|---|
| 같은 검증 실행의 저장 JSON | `8d37a7cb3bc3ac69f06f80c4c5a1a4bc0341275fe95523cbe76c3ac2fb0ddb0e` |
| 원 PNG, 114698 B | `7a6aad304342a72dc97d267c18e70c880c834345fafaa623dc5e6d0f9d455440` |
| 원 SVG, 59918 B | `305cba8f9c243639f84152756a1d21da9841782ff1ef43337f26a8889c746add` |

Plot은 저장 JSON만 읽었으며 scientific imports와 scientific function calls는 모두 0이다. SVG는 hash/원 기록을 확인했고 별도로 렌더링하지 않았다.

## 채택 범위와 DAG

채택 가능 범위는 선언된 exact scalar A,M,e, stationary bare-alpha/equal-daughter 모델, **연속 even 비음수 degree≤8 Bernstein 측도와 명시적 uniform azimuth**, 유리 polar-window × azimuth-arc 직사각형들의 유한 합집합이다. 반환 대상은 certified inner/outer event measure, 서로 다른 두 daughter의 coincidence, hit, inclusive count, assignment/overlap, denominator 상태를 반영한 conditional ratio enclosure, 2Y·GY·GY/2 관계다.

경계는 사건에 대해 10NBdelta이며 default delta는 sigma/(10NB·2^40)다. 합산 count/energy 출력은 해당 scale factor를 적용한다. 분모 하한이 양수인 경우 조건부 구간을 인증하지만 사건 epsilon을 ratio에 그대로 약속하지 않는다. 실제 parameter uncertainty, empirical DCS 정규화, encounter flux/history·실제 사건률 및 nonthermal deposition/thermalization은 이 참조 노드가 닫는 범위에 들어가지 않는다.

Root가 새 참조 노드를 채택하면 Local은 **9 complete +1 partial +3 physical open /13**, 즉 **9/13**이 된다. 중앙은 **28/88**, HE delta **0**이다. KINEMATIC08은 기존 plot CPU 7.040661/6 s FAIL에 따른 PARTIAL, reserve 0으로 보존한다. APERTURE07의 32/32 PASS 및 plot PASS, PHOTON05의 24/24 PASS 및 plot 4.40726504/4 s FAIL·PARTIAL, HE101의 C8 PARTIAL_EXPORT 19/20·reserve 0·원 PASS/FAIL/FAIL도 변하지 않는다.

열린 물리 입력 3개는 M0475002 정규화와 liquid-He 전자/target motion/response projection, 실제 전체 angular law와 photon encounter flux/history, named nonthermal birth/deposition/thermalization과 global species binding이다. Binding 소유자는 `population_rest_energy_witness` 하나다. Independent binding RHS, Gamma_thermal, Cv, species_heating, thermal_deposition은 null, birth_pool은 UNASSIGNED다. Global physical completion=null, L4=false, production=NOT_APPROVED를 유지한다.

## 종료 조건

현재 범위의 구체적인 미해결 correctness finding은 **0**이다. 추가 science·test·plot·Wolfram 실행이나 별도 검토 pass는 필요하지 않다. 이 보고서는 독립 과학·코드·실제 결과 및 시각 검토 gate를 닫는다. 최종 채택, source/backup/central publication ACK와 외부 handoff는 root의 후속 기록으로 확정한다. 검토자가 보지 않은 최종 게시·백업 ACK를 이 문서에서 완료로 주장하지 않는다.

원근거: 같은 디렉터리의 `STATIC_REVIEW.json`, `ACTUAL_RESULTS_PREPLOT.json`, `SYMBOLIC_REVIEW.json`; unit의 `CONTRACT_KO.md`, `CODING_CONTRACT.md`, `evidence/VALIDATION_WHOLE_PROCESS_ATTEMPT1.json`, `evidence/validation_attempt1/`, `SYMBOLIC_CHECK.wl`, `evidence/WOLFRAM_RAW.json`, `evidence/WOLFRAM_RESULT.json`, `evidence/PLOT_WHOLE_PROCESS_ATTEMPT1.json`, `evidence/plot_attempt1/`, `evidence/PLOT_RESULT.json`. 세부 원 파일 hash, identity, 26개 검토 항목과 F01 closure는 `FINAL_REVIEW.json`에 보존했다.
