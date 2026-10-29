# REI F4 물리 소스 데이터 생성: P19 비평형 UVB × REI 저장 17상태

**실행 단위:** `REI_P19_FROZEN_EVENT_ENERGY_DATA_20261029`  
**연구 위치:** 이미 진행 중이던 `research/rei-bass-event-rate-compat-20261029`의 C5–C10 물리 데이터 보충. 별도 새 IVP 또는 실제 CMB 관측량 계산 없음.  
**상태:** 새 물리 데이터 13 P19 knots / 14 frozen state-scenario / 98 ionization events / 독립 56 high-precision checks. 기존 REI working **33/88**, central **28/88**, physical fast **4/7**, delta **0**, F4 PARTIAL, L4_ready=false, `NO_MORE_IVPS=true`.

## 1. 왜 필요한가

PR268/269가 이미 BASS full21과 P19의 광이온화 **rate-shape 불일치**와 전자 생성 차이를 계산했다. 이를 반복하지 않고, 사용자가 요청한 실제 물리 데이터 우선 과제에 맞춰 (i) Puchwein19 Table D1의 여섯 물리 source moment, (ii) REI PR262의 실제 저장 17상태, (iii) 원 REI model.py가 채택한 H/D/T/He3/He4 전이 7개를 결합해 **사건별 전자·광가열·이온화저장·흡수 에너지 장부**를 생산했다.

선행 PR262의 calibrated beta/kappa 저장상태 총계는 재검산 대상일 뿐 신규 물리 기여로 중복 계상하지 않는다. 새로운 데이터는 **P19 fiducial source-only 원본과 BB13 GLS 교정 시나리오를 동시에, 개별 사건까지 나누어** 보존한 98행 및 13-knots의 실제 rate-derived mean excess energy이다.

## 2. 소스와 적용범위

- Puchwein et al., MNRAS 485 (2019) 47–68, DOI 10.1093/mnras/stz222, Table D1 *non-equilibrium fiducial*이며 equilibrium D2로 대체하지 않는다. 13 source knots z=2.32–4.89만 선택한 기존 PR261 수치 projection을 exact SHA로 복원했다. 13 knots는 published full cosmological source table 전체가 아니다.
- H I, He I, He II의 광이온화 \(\Gamma_i\,[\mathrm{s}^{-1}]\)와 photoheating \(\mathcal H_i\,[\mathrm{eV}\,\mathrm{s}^{-1}/target]\)는 중성/일차 이온 한 입자당 source terms이다. \(\mathcal H_i/\Gamma_i\)는 source-model에서 ionization event당 평균 초과 에너지 [eV]이다.
- REI `ON_refined` 17상태의 선택된 7개 `z_mean` (2.40449–4.70169)와 elapsed_proper_s는 **기존 REI 소스에서 저장**된 것. P19 D1을 통과시켜 다시 얻은 연속해나 공통 initial condition이 아니다.
- 구 REI는 H1/D/T에 같은 H I rate, He3/He4에 같은 He I/II rate를 사용하는 approximate isotope threshold convention을 쓴다. 이 조건만 소스 수준에서 재사용한다. Li7 광전이·Li6·핵광분해·CR·주입·T 약한붕괴·fast reservoir, 실제 21/62 상태 bath coupling, 방향별 redshift, actual K,H,nHref/nb은 **여기에서 결합하지 않는다**.
- 두 시나리오: `P19_D1_fiducial` (beta=kappa=0), `P19_D1_BB13_GLs_nominal` (PR261 a0 beta=-0.04591874303144475, kappa=0.0686617394805907). 두 번째는 model calibration이지 측정 기반 full physical posterior가 아니다.

## 3. 물리량과 에너지 장부

원 REI photoionization seven-column stoichiometric \(S\in\mathbb Z^{17\times7}\). 각 사건 \(j\)의 계수 \(c(j)\in\{\mathrm{HI,HeI,HeII}\}\), 이전 이온 상태 \(s(j)\), 이온화 에너지 문턱 \(I_j\in\{13.6,24.6,54.4\}\,[\mathrm{eV}]\). 프리즈한 \(y_{s(j)}\)에 대해

\[
\lambda_j(z)=y_{s(j)}\,\Gamma_{c(j)}(z),\quad
\dot y^{\rm photo}=S\lambda,\quad
\dot y_e^{\rm photo}=q^TS\lambda=\sum_{j=1}^7\lambda_j,
\]

\[
Q_{\rm heat}=\sum_j y_{s(j)}\mathcal H_{c(j)},\quad
Q_{\rm ion}=\sum_j I_j\lambda_j,\quad
Q_{\rm abs}=Q_{\rm heat}+Q_{\rm ion}.
\]

모두 Href당 proper time source이며, 이온화 저장 에너지를 thermal heat으로 다시 더하지 않는다. 또한 \(a^TS=0\)와 \(\mathbf1^TS=0\)는 각각 핵자수/핵수 보존을 의미한다.

## 4. 실제 생성된 데이터

| 저장 mean z | P19 fiducial 전자 생성 [Href^-1 s^-1] | P19 fiducial 광가열 [eV Href^-1 s^-1] | BB13 GLS 전자 생성 [Href^-1 s^-1] | BB13 GLS 광가열 [eV Href^-1 s^-1] |
|---:|---:|---:|---:|---:|
| 2.40449 | 1.76872e-16 | 8.47128e-16 | 1.31721e-16 | 6.30877e-16 |
| 2.78907 | 2.22979e-16 | 1.01135e-15 | 1.76468e-16 | 8.00396e-16 |
| 3.21710 | 2.93273e-16 | 1.32595e-15 | 2.48349e-16 | 1.12284e-15 |
| 3.60302 | 3.81046e-16 | 1.77777e-15 | 3.42977e-16 | 1.60016e-15 |
| 4.02426 | 5.10782e-16 | 2.47059e-15 | 4.91414e-16 | 2.37691e-15 |
| 4.37837 | 6.54147e-16 | 3.23253e-15 | 6.65581e-16 | 3.28903e-15 |
| 4.70169 | 8.17678e-16 | 4.10852e-15 | 8.75604e-16 | 4.39957e-15 |

새로운 사건별 기여 분해 (P19 fiducial)에서 H1_0 전자 생성 기여율은 z=2.40449에서 78.1524%, z=4.70169에서 33.3780%; He4_0 기여율은 각각 18.7547%, 66.6036%. 직접 저장된 두 epoch 사이의 선후만 알 수 있으며 연속적으로 dominance가 전환되는 정확한 z나 새 진화 경로를 유도했다고 주장하지 않는다. 동일 source × frozen state에서 He4_0 광가열 비중은 z=3.60302에서 58.9445%. 누락 이벤트 비중 및 계통오차를 물리적 posterior로 해석하지 않는다.

CSV: `P19_FIDUCIAL_13_KNOT_PHYSICAL_RATES.csv` (13×six + channel excess energy), `REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv` (14 rows), `REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv` (98 rows), `REI_FROZEN_EVENT_SOURCE_FRACTIONS.csv` (98 rows), `REI_FROZEN_PHOTO_SOURCE_CHECKS.csv` (14 checks).

## 5. 실제 실행 및 검증

- Python 19/19 `unittest` PASS (source SHA, source rate positivity, 98 event decomposition, no extrapolation, physical unit/energy, negative tamper input, no fake tau).
- 원 코드 `source17.run_saved()`에서 이전 PR262 전체 7개 source-only 저장값을 실제 재생하고, BB13 중심 총량/에너지 28개를 fresh 비교하여 PASS (relative tolerance 5e-14; tolerance 변경 없음).
- 신규 mpmath 85자리 **독립 보조 계산**: P19 13-knots를 자체 log interpolation, 원 saved y를 독립적으로 읽어 14×4 = **56개 물리 source value**를 계산. Python float CSV와 최대 상대 차이 \(2.33748\times10^{-15}\) (허용 <3e-14). 사용한 수치 projection은 published Table D1 원원본의 완전한 표가 아닌 기존 SHA-pinned selected rows다.
- 원 ST as sparse integer로 \(q^TS=\mathbf1^T\), \(A^TS=0\) 검산. 최대 전하 residual \(9.86\times10^{-32}\), 핵자 residual \(9.86\times10^{-32}\), 흡수 장부 residual \(3.16\times10^{-30}\) in native units. Wolfram arbitrary-symbolic heat+ionization-source residual \(\{0,0,0\}\) 확인.
- 그래프 3개를 생성하고 그림 축, 단위, 데이터 범위 및 legend를 확인했다. 시각화는 snapshot 인덱스를 있는 그대로 연결하는 guide일 뿐 IVP 선이 아니다.
- **새 IVP 0**, full chemistry/tau/CMB/BAO posterior/production 미생성. Native different-author R6/C9 review 도구 미노출로 NOT_RUN; 자가 검사/CAS/mpmath은 그것을 대신하지 않는다.

## 6. 연구 DAG 진척 판정

현재 작업은 기존 R1–R10/C1–C4가 게시된 `REI_BASS_FULL_EVENT_RATE_COMPAT_20261029` 내에서 **물리 데이터 산출 C5–C8의 실제 검증 가능한 완성**이다. 외부 R6/C9 미수행을 제외한 scoped 단계 완료 수만 18/20로 셀 수 있다. canonical working 33/88, central 28/88, physical fast 4/7은 그대로이며 **새 canonical 물리 완료 node는 0**이다. 별도의 한정 데이터 deliverable `REI_P19_FROZEN_EVENT_ENERGY_DATA=1/1 (PASS_SCOPED_SOURCE_DERIVED_DATA)`는 생성 데이터를 의미하는 내부 보조 완료이며 DAG88 node 번호를 늘리지 않는다.

다음 실제 물리 DAG를 진전시키려면 동일 bath·동일 inventory 초기조건에서 실제 화학식 또는 실제 photon-spectrum 재구성의 source-qualified 연결, H(z)와 nHref/nb, 실제 Thomson K 및 방향별 redshift가 필요하다. P19 D1 rate 입력이 원 REI 외부 source model과 일치하지 않는 것을 무시하고 physical tau나 L4 승격하는 것은 금지한다.
