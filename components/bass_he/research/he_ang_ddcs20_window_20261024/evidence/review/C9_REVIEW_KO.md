# C9 독립 과학·구현 검토

2026-10-24 UTC · 검토자 `/root/cross_repo_survey` · 대상 `HE-ANG-DDCS20-WINDOW`

## 판정

**PASS_SCOPED. 현재 고정된 입력·window의 과학적 수용을 막는 finding은 없다.**
E0=20 eV, 검출 전자 E=3–6 eV, θ=15–120°에서 선언한 축대칭·linear-μ/linear-E 보간의 모멘트와 각 scalar의 deterministic box 극값을 수용할 수 있다. 저장된 실제 출력, 구현의 식 대응, 독립 GL 적분 경로, 작은 box의 exhaustive vertex 검증, 원표 전사, 실행 비용을 대조했다.

이 판정은 다음 C10/게시 준비로 진행할 수 있는 검토 결과다. 전체 HE-ANG의 source/frame/joint-event provider 상태는 **SOURCE_INPUT_PENDING**이다. Event cross section, 두 전자의 공동 분포, recoil, finite-mass provider, thermal coupling 또는 HE-X1의 경험적 각분포 보정을 수용한 것이 아니다. C9가 Git 게시나 Dropbox/Drive ACK를 수행하거나 대신하지 않는다.

## 독립성과 실제 검토 방법

검토자는 이 unit의 THEORY/CONTRACT/source 전사/code/수치 실행을 작성하지 않았다. 앞선 cross-repository R1/R2 조사만 맡았다. 이번에는 원전 Table IV 이미지, 원전의 관련 본문, source JSON/CSV, THEORY/CONTRACT, R6 검토와 R7 원출력, 다섯 Python script, 결과 JSON, START/FINISH/ledger/stdout/stderr 및 PNG를 읽었다. 역할 지정은 Astra scientific/code reviewer이며 런타임 모델의 identity를 별도로 측정했다고 주장하지 않는다.

공식의 직접 유도, 작은 손계산, 코드 경로 분석 및 파일/JSON/해시 대조를 사용했다. 과학 코드 import, solver·test·analysis·plot 재실행, 추가 CAS 호출은 **0회**다. 이전 HE-X1 32 fixtures와 Hex의 과학 실행을 반복하지 않았다. 검토 산출물은 이 문서와 `C9_REVIEW.json`뿐이다.

적용한 skill은 `physmath-research-loop` 1.3.0의 C9, POLICY_INTEGRATION 및 SUBAGENT_MODE다. 이 검토가 독립 검토 한 번이며, 아래 비차단 사항으로 새 gate나 재귀 검토를 만들지 않는다.

## 원전과 입력

원전은 Childers et al., *Physical Review A* **69**, 022709 (2004), [DOI:10.1103/PhysRevA.69.022709](https://doi.org/10.1103/PhysRevA.69.022709), Table IV다. 로컬 읽기 전용 PDF의 SHA256은 `efcb2f849162b31425f2e609c6d563171b6bba1068b8eefd4dc1465f54213941`로 계약과 일치한다. 원문·이미지는 검토 입력이며 공개 배포 대상에 추가하지 않았다.

원표 이미지에서 8개 각도 × 5개 에너지의 **40값과 8개 uncertainty %**를 source JSON/CSV와 직접 대조했다. θ 순서는 15,20,25,30,40,60,90,120°이고 E 열은 2,3,4,5,6 eV다. `load_source`는 모든 셀·printed value·행 uncertainty를 두 전사 형식 사이에서 비교하고 immutable CSV 해시를 확인한다. μ를 증가 순서로 뒤집을 때 DDCS와 uncertainty 행도 같이 뒤집으며, 주 분석은 E=3,4,5,6의 **32값**만 사용한다. E=2의 8값은 추가 uncertainty footnote의 해석을 강제하지 않고 보존된다.

E1은 검출된 outgoing/scattered 전자의 잔여 운동에너지다. Source의 DDCS는 `10^-19 cm²/(sr eV)`이고, cm²→m² 변환으로 **10^-23**이 된다. φ 적분의 **2π**를 정확히 한 번 적용한다. 두 outgoing 전자의 event normalization에 관한 추가 factor 2를 넣지 않았고, 부분 window의 N을 total event cross section으로 바꾸지 않았다. Source의 quoted 1σ는 covariance를 제공하지 않으며 reference-DCS 오차를 포함하지 않는다. 따라서 구현의 cellwise box를 선택한 deterministic sensitivity 집합으로만 해석한 것은 적절하다.

## 식–코드 검토

### Analytic hats와 units

각 segment [a,b]에서 왼쪽 hat은 (b−x)/(b−a), 오른쪽은 (x−a)/(b−a)다. `hat_integral_weights`의 두 항은 각각

\[
\frac{b\Delta_s-\Delta_{s+1}}{b-a},\qquad
\frac{\Delta_{s+1}-a\Delta_s}{b-a},\quad
\Delta_s=\frac{d^{s+1}-c^{s+1}}{s+1}
\]

이며 [c,d]는 window로 잘린 segment다. 이는 직접 적분과 일치한다. q=0의 양쪽 가중치는 온전한 segment에서 (b−a)/2이고, q=1은 각각 (b−a)(2a+b)/6 및 (b−a)(a+2b)/6이다. q=1/2는 양의 E에서 2x^(3/2)/3 및 2x^(5/2)/5 primitive를 쓴다. 음수 μ에는 정수 r=0,1,2만 적용하므로 잘못된 fractional power가 생기지 않는다.

R_rq=2π·10^-23 Σ y_ij A_i^(r)B_j^(q)의 단위는 m² eV^q이고, J_r(E)의 단위는 m²/eV다. Energy-to-joule 상수 ε는 U와 momentum scale을 만들 때 적용한다. 물리적 단위와 수치 단위를 중복 환산하지 않는다. 독립적인 손계산으로 q=0 energy 가중치 (1/2,1,1,1/2)를 적용하면 increasing-μ 행의 energy integral은 9.74,10.60,13.91,36.70,52.25,53.70,116.00,126.65다. 이를 μ segment의 trapezoid로 적분하면 native N≈30.54, SI N≈1.919×10^-21 m²로 저장 결과의 크기와 순서에 일치한다. 이 손계산은 별도 실행이나 고정밀 재계산을 주장하지 않는다.

### Ratio 극값과 witness

F(z)=(b·z)/(a·z), a>0 및 0<l≤z≤h에서 분모는 양수다. 최소값 r*에 대해 (b−r*a)·z의 최소가 0이므로 b_i/a_i<r*인 좌표는 high, >r*인 좌표는 low를 택한다. 정렬된 ratio의 threshold를 0부터 n까지 모두 보면 최소점의 한 vertex가 포함된다. 최대는 반대 endpoint 선택이다. 동률에서는 계수가 0이므로 같은 값의 좌표를 threshold 한쪽에 모두 배치해도 최적성이 유지된다. Signed numerator와 collapsed bounds도 이 논증에 포함된다.

`ratio_box_extrema`는 이 구성과 일치하는 stable sort 및 prefix sum을 사용한다. 결과에는 scalar마다 **33개 후보**, 실제 32좌표 witness, threshold index, equality residual 및 sign-optimal supporting linear functional과의 stationarity gap이 있다. 실제 μ 평균의 min/max threshold=12, P2의 min=12/max=16, E 평균의 min/max=16, sqrt(E)μ의 min=11/max=12이며 저장된 endpoint 배열과 그 방향이 일치한다. 공통 multiplicative scale의 상쇄는 수학적 조건부 성질로만 검증한다. 실제 source의 angle-dependent reference error가 그런 공통 scale이라는 주장으로 넓히지 않는다.

각각의 scalar extrema가 exact라는 이론적 표현은 실수 산술의 box 문제에 대한 것이다. 저장값은 binary64 계산과 고정 residual 기준으로 검증되었다. 서로 다른 scalar의 witness를 한 simultaneous physical vector로 합치지 않았고, nonlinear covariance의 exact box extrema도 주장하지 않는다.

### 독립 oracle와 θ 모델

`quadrature_moments`는 analytic hat 함수를 호출하지 않는다. 각 cell의 네 corner에서 local bilinear 값을 직접 만들고 GL16/32로 적분하므로 analytic primitive 경로와 구별되는 oracle다. 공유하는 입력과 library는 명시된 같은 데이터·NumPy이며 완전히 별개 실험을 주장하지 않는다. Constant/affine의 독립 closed form, n≤6 모든 vertex 비교와 함께 formula error를 검출할 구성이 있다.

θ 대조는 `arccos`로 만든 **radian** 좌표에서 cell 길이를 곱하고 **sin(θ)**를 적분 integrand에 넣는다. Data/figure의 degree를 적분 미분량으로 사용하지 않는다. θ와 μ 보간 차이는 같은 knot에서 다른 보간을 택한 representation sensitivity다. 원전 미측정 구간의 error bound나 continuum convergence로 해석하지 않은 것이 적절하다.

### Tensor와 PSD

φ 평균으로 transverse component는 (R_01−R_21)/2, longitudinal component는 R_21이 된다. 이로부터 tr(S)=2m_e U가 나오며 코드의 trace/STF 계산과 일치한다. 정규화 longitudinal covariance는 Var(sqrt(E)μ), transverse variance는 ⟨E(1−μ²)⟩/2이므로 양의 measure에서 PSD다. 코드가 ⟨μ⟩²나 ⟨E⟩⟨μ⟩²를 잘못 대입하지 않고 ⟨sqrt(E)μ⟩²를 사용한다.

## 실제 저장 결과와 검증 근거

| 양 | Nominal | Scalar box minimum | Scalar box maximum |
|---|---:|---:|---:|
| N_W [m²] | 1.918935932462322e-21 | 1.5244334017931465e-21 | 2.3134384631314976e-21 |
| ⟨μ⟩ | 0.5215950231699314 | 0.4463277016561826 | 0.5963051462262531 |
| ⟨P2⟩ | 0.17998469013448556 | 0.0922143276271729 | 0.26715267497657014 |
| ⟨E⟩ [eV] | 4.581073268756349 | 4.431612712651814 | 4.725062230463735 |
| ⟨sqrt(E)μ⟩ [eV^(1/2)] | 1.1113254574359155 | 0.9496644189267021 | 1.2710185564983016 |

Source error와 선택한 box는 통계적 confidence interval이 아니다. covariance/(2m_e ε)의 diagonal은 `[1.2487902633867187, 1.2487902633867187, 0.8484484696377634]`이며 최소값은 PSD tolerance 4.581073268756349e-12보다 충분히 큰 양수다.

- 저장된 unittest 8개는 모두 PASS이고 raw stderr의 8개 test 이름/OK와 일치한다. 실패 0, 오류 0이다.
- 실제 analysis의 11 checks는 모두 true다. 최대 analytic-vs-GL scaled error는 1.8841299079382534e-15로 5e-13 이내다.
- θ GL16–32의 최대 scaled difference는 3.9513796892540674e-16이다. Ratio witness의 최대 equality residual은 1.1149537821941694e-16이고 저장된 stationarity gap은 모두 0이다.
- PNG를 직접 보았다. Physical degree θ, source 단위, energy/angular window, quoted source errors, scalar deterministic ranges, linear-μ와 linear-θ marker를 구별할 수 있다. Footer에 covariance/reference-DCS 한계와 scalar별 다른 extremizer를 명시한다. 현재 표시에서 잘림/겹침을 발견하지 않았다. Root의 별도 figure review도 PASS_SCOPED로 보존되어 있다.

## 실행·실패·누적 비용 보존

세 invocation의 START/FINISH/source freeze, raw stdout/stderr 해시 및 ledger entry를 대조했다. 각 FINISH record는 ledger entry와 content identity가 같고, 세 실행의 입력/코드 freeze는 현재 파일 해시와 모두 일치한다. THEORY/CONTRACT는 R6 reviewed identity와 같다.

| Run | Accounted CPU s | Wall s | 실제 상태 |
|---|---:|---:|---|
| 01_tests | 0.120977 | 0.16668615100206807 | FINISH, returncode 0 |
| 02_actual_analysis | 0.115877 | 0.16660642299393658 | FINISH, returncode 0 |
| 03_plot | 1.7201509999999998 | 1.7714657789911143 | FINISH, returncode 0 |
| 누적 | 1.9570049999999997 | 2.104758352987119 | 3/4 scientific invocations |

누적 CPU는 child와 측정 구간 parent delta를 더한 값이다. 20 CPU s/60 wall s allocation과 6 CPU s/20 wall s per-child cap 안에 있다. 1회 repair reserve는 사용하지 않았다. Runner는 기존 run ID, 미종결 START, 실패·관측 overshoot를 자동 재실행하지 않도록 보존한다. 실제 plot stderr에는 Matplotlib cache 경로 fallback 경고가 남아 있으나 returncode 0이고 이미지 산출을 확인했으므로 현재 과학적 실패로 분류하지 않는다.

이전 Hex ledger의 실제 SHA256은 `b1eb4cf0e367f46260997f1e4cebf33228d5e9b7376329370bd91d323ef52450`로 계약의 기존 identity와 같다. Hex CPU18.434312000000002/wall18.739398924000852, HEANG_CONTRACT 기존 비용 및 nontransferable 잔여, HE-X1/HE38/D10 unknown 비용을 새 allocation으로 reset하거나 이전하지 않았다. R7의 실제 Wolfram 호출은 하나이며 원출력의 symbolic residual은 모두 0이다. 관측 tool wall 13.307 s와 remote CPU **UNKNOWN_NOT_ZERO**를 구별하고 local ledger의 complete grand total이라고 하지 않는다.

## Finding과 최소 후속 조치

**C9-NB-01 — BACKLOG, 현재 고정 window에 비차단.**

- 대상: `code/ddcs_window.py`, `window_moments`, theta metadata 구성(234–239행).
- 근거: `mu_window`를 사용해 적분과 `window.mu`를 정해도 `theta_degrees`는 전체 source μ의 양끝에서 계산한다. 예를 들어 모든 hat support가 아직 남는 μ_window=(-0.4,0.95)를 후속 사용하면 선택 window의 각도 경계는 `[acos(0.95),acos(-0.4)]`인데 metadata는 기존 15–120°를 반환하는 코드 경로다. 이번에 그 경로를 추가 실행하지 않았다.
- 영향: 미래의 부분 window API 재사용 시 support label이 실제 적분 구간과 어긋날 수 있다. 현재 계약과 실제 invocation은 기본 full source window이므로 저장 수치·그림·입력 또는 위 판정에는 영향이 없다.
- 최소 교정: 향후 부분 window 사용 전 `interval(mu, mu_window)`의 실제 양끝을 뒤집어 arccos/degree로 변환해 metadata에 사용한다. 현재 unit의 admission을 위해 repair invocation, 새 test campaign, 새 gate를 요구하지 않는다.

**현재-task blocker 0개, 요구되는 repair 0개.** Parent는 수용한 window 결과와 claim limit을 유지하여 C10·expected-SHA 게시·백업·DAG 반영으로 진행할 수 있다. Full-provider admission은 별도 source/frame/event 입력이 도착할 때 이어간다.
