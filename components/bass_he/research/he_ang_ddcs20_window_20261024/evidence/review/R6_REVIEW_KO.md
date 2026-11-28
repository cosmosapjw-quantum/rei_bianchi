# HE-ANG-DDCS20-WINDOW — 독립 R6 과학 검토

**판정: PASS. 현재 이론 계약의 구현 실행을 막는 결함은 발견하지 않았다.**

- 검토일: 2026-10-24 UTC.
- 검토자: `/root/angular_source_search`; 이론 작성자 `/root`와 별도의 native child. 검토자는 원전 조사·독립 수치 전사를 맡았으며 이번 THEORY/CONTRACT 및 구현을 작성하지 않았다.
- 범위: `THEORY_KO.md`, `CONTRACT.json`의 물리·수학 유도, 원전 연결, 부호·차원·경계·퇴화 경우. 실제 코드, numerical execution, publication, remote HEAD 또는 backup 성공을 이 검토로 인증하지 않는다.
- 독립성: 별도 검토자의 직접 수학 유도와 원전 대조. CAS/standalone scientific computation/solver/새 fixture 실행은 하지 않았다. 파일 읽기·해시·JSON 구문 확인만 수행했다.
- 고정 입력: THEORY SHA256 `21265d10608c3626002b714f18039af61d31c4bb1b538a1797811f04577e3036`; CONTRACT SHA256 `72972199b9886740f9a9b1ca0275adda59b29fdad005297b9b806b9261b86b8f`.
- 계약의 base SHA는 `bf3c21a39b1111497ed77667d05b8a853ffe6646`이다. 이는 읽은 계약의 identity이며 별도로 원격 HEAD를 조회했다는 뜻은 아니다.

## 1. 원전과 모델의 경계

Childers et al., *Physical Review A* 69, 022709 (2004), DOI https://doi.org/10.1103/PhysRevA.69.022709, Table IV 및 인쇄 p.022709-2/4/6의 convention을 기존 독립 전사와 대조했다. source CSV identity는 `d9889cbf9f330dd195fce9ec78bf8d77f8d35e247c58e705df609efdd9cee8c4`다.

E0=20 eV, 8개 각도와 E1=3,4,5,6 eV의 32개 주 입력, E1=2 eV의 보존용 8개 입력, 원전 단위 10^-19 cm²/(sr eV)와 SI 변환 10^-23 m²/(sr eV)가 일치한다. E1은 E0−EL인 검출 전자의 운동에너지이며 입사 입자의 동일성을 추적하는 label이 아니다. source에 없는 factor 2를 추가하지 않았다.

보고된 row 1σ를 통계적으로 독립인 셀의 Gaussian 오차로 가정하지 않는다. 원전의 continuum fitting과 covariance 미제공, CCC reference DCS 오차 제외, E1=2 eV footnote의 불명확성을 유지한다. 따라서 32개 좌표의 box는 원전이 정한 joint uncertainty region이 아니라 이번 계산에서 선택한 민감도 집합이다. 축대칭 완성, μ/E 보간, 비상대론적 운동량은 명시적으로 채택된 모델 가정이다. 이 분리는 적절하다.

## 2. 독립 수학 확인

### 양의 보간과 정확 적분

한 cell의 두 1차 basis는 각각 비음수이며 합이 1이다. 두 좌표의 곱 basis 네 개 역시 비음수이고 합이 1이므로 f_h는 네 node 값의 convex combination이다. 선택된 모든 값이 양수여서 W 전체의 f_h>0, R00>0이다. 원전 각도 행을 μ 증가 순서로 역정렬하되 행 대응을 유지해야 한다는 조건도 맞다.

유한 사각형 위의 연속 piecewise polynomial을 적분하므로 유한 합과 적분을 분리할 수 있다. 각 segment의 (α+βx)x^s 원시함수는 THEORY의 식과 일치한다. 음의 μ에는 정수 r만 사용하고 E≥3에는 양의 fractional power를 사용하므로 실수 branch 문제가 없다. 각 node의 hat는 양의 길이 지지구간을 가져 A_i^(0)>0, B_j^(0)>0이다.

독립적인 constant control에서 y_ij=c이면

    R_rq = 2π 10^-23 c
           [ (μ_max^(r+1)−μ_min^(r+1))/(r+1) ]
           [ (E_max^(q+1)−E_min^(q+1))/(q+1) ].

또한 Σ μ_i L_i=μ, Σ E_j H_j=E이므로 affine 함수가 정확히 재현된다. 이는 예정된 closed-form controls의 독립 근거다. 값에 가중치를 먼저 곱한 node trapezoid와 실제 가중 연속 적분을 구분한 문구는 정확하다.

R_rq의 차원은 m² eV^q, 고정 에너지의 J_r은 m²/eV다. r=1의 A_i 및 R_1q는 음수가 될 수 있지만 이 부호는 방향 모멘트의 성질이며 보간 양성에 반하지 않는다.

### 비상대론적 momentum tensor와 covariance

축대칭 아래 p_z=√(2m_e ε)√E μ이고 방위각 평균은 ⟨cosφ⟩=⟨sinφ⟩=0, ⟨cos²φ⟩=⟨sin²φ⟩=1/2다. 따라서 THEORY의 P와 S 및 모든 off-diagonal 0이 직접 얻어진다. trace S=2m_e εR01=2m_e U_W와 STF의 trace 0이 성립한다.

정규화한 p_z의 second moment에서 mean²를 빼면 보고된 covariance의 z 성분이 된다. 유한 양의 측도 dν=D_h dE dΩ에 대해 Cauchy–Schwarz를 1과 √E μ에 적용하면 R_(1,1/2)²≤R00 R21이다. transverse 성분은 E(1−μ²)/2의 평균이므로 비음수다. 따라서 covariance PSD 주장은 현재 가정 아래 증명된다. 이 관계는 outgoing detected-electron window의 관계이며 순 충돌 momentum source나 ion recoil 보존법칙을 제공하지 않는다.

### 선형 box 극값과 정규화 ratio 극값

직사각형 집합에서 w·z의 항들은 별도 좌표에 의존하므로 coefficient의 부호별 endpoint 선택이 전역 극값이다. 대칭 halfwidth를 사용한 Σ|w_k|δ_k bound는 달성 가능하다.

Ratio에서는 a_k>0와 l_k>0 때문에 분모가 box 전체에서 양수다. 최소값 r*에 대해 F(z)≥r*와 (b−r*a)·z≥0는 동치다. 선형식의 최소 endpoint를 선택하면 q_k=b_k/a_k<r*인 좌표는 h, q_k>r*인 좌표는 l이다. q의 증가 정렬 후 하나의 threshold를 이루므로 n+1개 후보에 전역 최소를 실현하는 vertex가 반드시 포함된다. q_k=r*인 tie 좌표는 목적값을 바꾸지 않으며 한쪽 endpoint로 통일할 수 있다. 최대의 반대 endpoint 선택도 같은 논증으로 성립한다.

이 검토는 signed b, 상수 q, tie, 일부 l=h의 퇴화 경우에도 유지된다. 양의 동일 scale은 ratio와 그 box extrema에서 소거된다. 그러나 source의 각도 의존 reference 오차가 그 조건에 해당한다는 근거는 없으므로 source uncertainty cancellation은 주장할 수 없다. THEORY는 이 구분을 유지한다.

Ratio 증명이 직접 인증하는 대상은 **하나의 linear-fractional functional**이다. Nominal covariance PSD는 위의 별도 증명으로 성립하지만 covariance의 nonlinear variance에 대한 exact box extrema는 이 threshold 증명의 결과가 아니다. 현재 문서에는 그러한 추가 주장이 없으며 범위를 넓힐 필요가 없다. 서로 다른 ratio의 개별 extrema witness 또한 하나의 동시 extremizing state로 합쳐 해석하지 않는다.

## 3. 보간 비교와 경계 확인

동일 에너지 보간·node·window를 유지하며 μ-linear와 θ-linear를 한 번 비교하는 계획은 보간 표현의 민감도를 판별한다. θ 적분에서 sinθ dθ의 θ는 radian 좌표다. Source 각도와 figure의 degree 표시는 이에 대한 단위 변환이며, 예정된 독립 quadrature 및 C9에서 확인하면 된다. 새 scientific assumption 또는 추가 문서 gate는 필요 없다.

Node에서 0인 양의 interior bump를 더하면 원전 node 값과 양성을 보존하면서 window 적분이 바뀐다. THEORY의 구체적 bump는 경계에서 연속적으로 0이 되고 내부에서 양수이므로 이 관찰은 성립한다. 따라서 exact integration은 선언된 interpolant의 exactness이고, 실험의 미지 연속 함수에 대한 error bound 또는 convergence order가 아니다. 본문은 이를 새로운 strong no-go로 과장하지 않는다.

## 4. 판정과 다음 실행

| 대상 | 판정 | 증거 수준 |
|---|---|---|
| Table IV 범위·단위·count/오차 convention | PASS | 실제 원문 및 독립 전사 |
| Positive bilinear hats 및 R_rq | PASS | 독립 해석 유도 |
| Momentum/tensor/covariance/PSD | PASS | 축대칭 평균과 Cauchy–Schwarz |
| Linear box 및 ratio threshold 증명 | PASS | compactness와 선형 endpoint 환원 |
| 단일 θ 대조 및 bump 해석 | PASS | 선언한 근사/주장 범위 점검 |
| 실제 binary64 구현·허용오차·성능 | NOT_RUN | 다음 C6–C9의 기존 계약 |

현재 blocking finding 0건. THEORY/CONTRACT 수정 요구 0건. 본 검토자가 승인·수용 기준·물리 범위·예산을 변경하지 않았다. **기존 계약에 따른 구현 실행으로 진행할 수 있다.** R6 PASS만으로 numerical acceptance나 과학 게시가 완료되지는 않으며 CONTRACT의 C9 및 root admission이 남는다. HE-ANG parent의 SOURCE_INPUT_PENDING도 그대로다.

Skill context: physmath-research-loop 1.3.0의 SKILL.md, references/THEORY_LOOP.md R6, POLICY_INTEGRATION.md, SUBAGENT_MODE.md. 현재 요청에 맞춘 1회 독립 검토만 수행하고 recursive review, 추가 solver 및 문서층을 만들지 않았다.
