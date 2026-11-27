# HE37-H1DG — H1 차등 이온화 모형에서 보존된 net source까지

**workflow1.0.0 / approval0.2.** 단원은 `research/he37_h1_differential_gain_20261023`, 브랜치는 `research/he37-h1-differential-gain-20261023`이다. HE36 게시 pin `6403055c3d574ec0bd1ece80147f9711315902e7`과 science pin `b2336709b9a07dd1db0a7cc9da381c59c8dd6470`에서 이어졌다.

과학 판정은 **PASS_SCOPED**이며 source·theory·bridge·diagnostic·최종 그림의 독립 검토를 통과했다. 최종 게시와 백업의 실제 상태는 [DAG](DAG.json), [단계 장부](STAGE_LEDGER_KO.md), [최종 ACK](delivery/FINAL_ACK.json)가 기록한다. PR은 [#90](https://github.com/cosmosapjw-quantum/BASS_HE/pull/90)이다. 이 문서의 scientific payload는 SCIENCE_MANIFEST.json에 결속하며, 뒤에 생기는 delivery metadata는 별도로 보존한다.

## 1. 이번에 확보한 결과와 원래 목표 사이의 차이

HE37은 **한 개의 H1 ground-state CI 과정** \(e+\mathrm H\rightarrow e+e+p\)에 대해, 원전이 정의한 차등 에너지 분배와 등방 outgoing 각도 근사를 채택하고 입사 loss와 생성 gain을 합한 number·heat·전자 STF source를 구현했다. Maxwellian 원적분은 안정적인 special function과 세 다항식 모멘트로 줄였다. 기존 HE36 tensor attachment와 REI 사건 장부는 코드 바이트를 유지한 채 연결했다.

원래 전체 목표는 원자·핵 반응, 열·광원 진화, 바리온 비등방응력과 metric feedback이 일관되게 결합된 계산이다. 이번 성과는 그중 **source가 명시된 H1 CI reference 구성요소**다. 경험적으로 보정된 H1 각분포, 유한질량 recoil tensor, 종 사이의 열화·stress 분배, RR/DR/CX·추가 종·핵 daughter/stopping을 모두 제공하지 않는다. 두 종류의 완료를 혼동하지 않도록 `GLOBAL_GOAL_DAG.json`에서 B1/B2는 partial, B3→B4→B5는 pending으로 유지한다. 미정인 provider와 종 범위에 공통 분모가 없으므로 전체 목표에 임의의 완료 백분율을 붙이지 않는다.

HE32는 기존 **8핵종21상태, prescribed-UV photo+caseA RR, gas \(\pi_b=0\)** pilot 그대로다. Matter stress는 nonbaryonic sector다. 392 nominal+2 angular guard, 394 NPZ/receipt와 그림6쌍의 이전 완료 근거를 재사용했다. HE37을 추가했다고 모든 불안정 isotope·음이온·분자 또는 fully reactive19채널 핵반응망이 완료되었다고 해석하지 않는다. 이번 새 IVP와 기존 완료 IVP/suite replay는 모두0이다.

## 2. 재개와 변경분 조사

먼저 살아 있는 작업공간과 HE36 저장 근거를 확인하고, 이전 원전·유도·실행 evidence를 재사용했다. 이번 intake의 cutoff는 기존 종합 snapshot인 **2026-10-22T22:26:00Z**다. 상세 기록은 `evidence/intake/INTAKE_REPORT_KO.md`, `INTAKE.json`, `BRANCH_DELTA.json`, `READBACK_BINDINGS.json`에 있다.

| 조사 범위 | 실제 수행·해석 |
|---|---|
| 관련 repo | BASS_HE, WU088_HH, rec_bianchi, rei_bianchi, bass_cr, bass, vigilode의7개 |
| Branch metadata |15페이지,1276→1281행; 새tip5, 이동tip4, 삭제0 |
| PR metadata | repo별 updated-desc 첫 페이지 총665행; 각 마지막행이 cutoff보다 오래되어 이후 updated9개를 포함 |
| 고정 원문 | 선택 Git text19개를 읽고 원 Git blob SHA1과 모두 대조 |
| Repo 대화 | updated9PR의 issue-comment collection9개, cutoff 이후댓글5개 |
| 개인 대화 | Personal Context가 unavailable; 전문 또는 최신 모든 대화 접근을 주장하지 않음 |
| 백업 | dossier ADD event29개/3페이지와 PHYS81/C23A 최종 authority2개; 옛 전체 archive 재복원 없음 |

이는 최신 변경분의 범위를 넓혀 확인한 조사다. 모든 역사 PR927개, 모든 repo 코드, 모든 대화·백업을 다시 전수 열람한 것은 아니다. Dropbox 날짜 검색이 cutoff 이전 행을 반환한 실패는 보존했고, 실제 event API 응답으로 대체했다. 이번 intake 자체의 model/test/IVP/render/benchmark 실행 수는0이다.

재사용할 다음 donor도 구체화했다. PHYS81 PR137 pin `b3ec271a96cb67e583bffa9b61533802838236f9`는 finite H/He/Li CI, 정확한7→3 hazard 좌표, rank≤2 Jacobian과 일부 cold-COM nuclear recoil 장부를 제공한다. C23A PR96 pin `7643af28c671a7473754a3c2cd0c6e523bd61aac`는 명시적 UVB photo subflow와 finite electron-deposition 연산자를 제공한다. REC127 ANGULAR01 pin `5185c396b7e07076565ca2f5044a5ccd193e6ee1`은 line escape-probability 모멘트다. 각각의 scalar heat, spectrum, probability moment와 H1 outgoing electron STF의 소유자는 다르다. 이들의 완료 수를 이번 실행 수에 더하거나 준비된 H1 gain tensor로 선언하지 않았다.

REC125와 REI221의 새 tip은 delivery metadata만 바뀌었음을 확인했다. 기존 source·결과를 재실행하지 않았다. VigilODE의 새 explicit/production-hardening branch도 향후 solver 후보로 기록했지만 현재 source 연구의 solver를 자동 교체하지 않았다.

## 3. 원전 채택과 미채택 자료

선택 원전은 Hai P. Le와 Jean-Luc Cambier, **Modeling of Inelastic Collisions in a Multifluid Plasma: Ionization and Recombination**, *Physics of Plasmas*23,063505(2016), [DOI10.1063/1.4953050](https://doi.org/10.1063/1.4953050), [author manuscript](https://arxiv.org/abs/1605.06545)다. Eq.(7), Eqs.(11)–(12), §III.E, Eq.(49), Eq.(53c), Eq.(85)를 해당 페이지에서 확인했다. Eq.(85)의 하위 인용 서적까지 독립 감사했다고 쓰지 않는다. PDF SHA256은 `5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68`이며 원문 PDF는 공개 repo에 재배포하지 않는다.

원전 §III.E는 작은 electron/heavy mass ratio와 **등방 outgoing** \(G=1/(16\pi^2)\)를 명시적으로 가정한다. Eq.(85)는 semiclassical energy-sharing 법칙이다. 이 두 근사를 함께 채택했다. 원전이 다루는 역과정은 three-body recombination이며, 이 선택으로 radiative recombination까지 구현된 것은 아니다. 외부 저자의 소프트웨어를 복제하지 않고 식에서 독립 구현했다.

CCC author H1 ZIP도 실제로 확인했다.7,010,887바이트·3162member의 README와 대표 header는 integrated transition/total cross section을 정의한다. 그 안의 TICS.1S는 HE36의5754바이트, SHA256 `7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae`와 같았다. **이번에 조사한 ZIP**에서 필요한 outgoing energy-weighted \(l=2\) 자료를 얻지 못했으며, 이를 모든 CCC 계산이나 미공개 자료의 부재 주장으로 확장하지 않는다. 같은 TICS 바이트가 확인되었으므로 이전 모멘트를 재계산하지 않았다.

Exa1질의6결과와 SciSpace1질의10논문은 source 탐색 기록이다. 검색된 논문 수를 전문 독해 수로 세지 않았다. 차등 각도 실험/계산 문헌의 제한된 에너지·geometry만으로 전체 provider를 조립하지 않았다. CCC total에 원전의 분배만 곱하는 hybrid도 이번 선택에 포함하지 않는다.

## 4. 차등 사건에서 number·energy·STF로

공통 bulk rest frame, 비상대론적 stationary heavy-target 극한을 쓴다. \(E=m_ev^2/2\), \(I=13.6\,\mathrm{eV}\), \(\theta=k_BT_e\)다. Source의 반올림된 Bohr radius0.529Å는 HE36에서 고정한 \(a_0=5.29177210544\times10^{-11}\,\mathrm m\)로 정밀화했음을 identity에 기록했다. Threshold13.6eV는 유지했다. Source-native는 동일 functional kernel과 이 명시적 상수 정밀화를 뜻하며 원전 반올림 수의 bitwise 재현이라는 뜻이 아니다.

원전 ground-state 과정에서

\[
\frac{d\sigma}{d\Upsilon}=\frac{4\pi a_0^2I^2}{E\Upsilon^2},\qquad
\sigma(E)=4\pi a_0^2\frac{I(E-I)}{E^2},\qquad E>I.
\]

조건부 분배 \(p(\Upsilon|E)=IE/[(E-I)\Upsilon^2]\)는 \(I\le\Upsilon\le E\)에서1로 정규화된다. 두 outgoing 에너지는 \(E_1=E-\Upsilon\), \(E_2=\Upsilon-I\)이므로 매 사건 \(E_1+E_2=E-I\)다. 사건 단면적은 한 사건을 세고 inclusive outgoing 전자수는2다. 이 차이로 생기는 factor2를 명시적으로 검증했다.

일반적인 회전 공변 outgoing law는 두 모멘트로 표현할 수 있다.

\[
U(E)=\int\epsilon\,d\mu_E=E-I,\qquad
D(E)=\int\epsilon P_2(\cos\chi)\,d\mu_E.
\]

\(\mu_E\)는 두 전자를 함께 세는 measure다. 이때 conditional gain pressure tensor는

\[
B_{\rm gain}=\frac{2U}{3}\mathbf1+
2D\left(\hat n\hat n-\frac{\mathbf1}{3}\right).
\]

입사 Maxwellian에 대한 무한소 Grad STF 방향과 \(\langle(\hat n\hat n-\mathbf1/3)(\pi_e:\hat n\hat n)\rangle=2\pi_e/15\)를 이용하면, \(K=g\sigma\), \(\alpha=\langle K\rangle\), \(\beta=\langle EK\rangle\), \(\gamma=\langle E^2K\rangle\)에서

\[
R_e=-R_H=R_p=n_en_H\alpha,
\quad Q_{\rm gain}=n_en_H(\beta-I\alpha),
\quad \boxed{Q_{\rm net}=-I n_en_H\alpha},
\]

\[
J_{\rm net}=-\nu\pi_e,\qquad
\nu=\frac{4n_H}{15\theta^2}\langle EK(E-D)\rangle.
\]

선택한 등방 outgoing에서는 \(D=0\)이므로 

\[
\boxed{J_{\rm net}=-n_H\kappa_2\pi_e},\qquad
\kappa_2=\frac{4\gamma}{15\theta^2}.
\]

따라서 energy sharing 적분과 outgoing angle 적분을 매번 수행할 필요가 없다. 이 단순화는 선택한 모형 안에서 exact하다. STF 계수가 incoming-only 식과 같아도 scalar gain은0이 아니다. Net heat로 incoming mean energy 전체를 빼면 \(E-I\)의 반환을 누락한다.

양의 outgoing measure는 \( -(E-I)/2\le D\le E-I\)를 준다. 이에 따라

\[
\frac{4n_HI\beta}{15\theta^2}\le\nu\le
\frac{2n_H(3\gamma-I\beta)}{15\theta^2}.
\]

이 envelope는 동일 사건 단면적에서 허용되는 비음수 각도모형의 범위다. 실제 H1 각분포의 보정 오차막대가 아니다. 신규 strong no-go 또는 문헌 전체 최초 성과를 주장하지 않는다.

## 5. 안정적인 analytic moment와 실제 최적화

\(C=\sqrt{8/(\pi m_e)}(4\pi a_0^2I)\theta^{-3/2}\), \(x=I/\theta\)라 하면

\[
\alpha=C\theta E_2(x),\quad
\beta=C\theta^2e^{-x},\quad
\gamma=\beta(I+2\theta),\quad
\delta=\beta(I^2+4I\theta+6\theta^2).
\]

구현은 SciPy `expn(2,x)`를 사용한다. \(E_2=e^{-x}-xE_1\)를 두 큰 항의 차로 계산하지 않고 양의 special function으로 평가한다. \(F=e^xE_2=\int_0^\infty t e^{-t}/(x+t)\,dt\)를 쓰면 \(1/(x+2)\le F\le1/(x+1)\), \(I+\theta\le\beta/\alpha\le I+2\theta\)가 수치 sanity bounds가 된다. Numeric T 계약은2000–200000K이며 그 자체가 물리 정확도 보증은 아니다.

실제129온도에서 source-native 네 모멘트를 계산했다. 아래 값은 저장 CSV의 양 끝과 중앙행이다.

| \(T\)[K] | \(\alpha\)[m³/s] | \(\kappa_2/\alpha\) | 입사 평균[eV] | outgoing 반환[eV] | net 손실[eV/event] |
|---:|---:|---:|---:|---:|---:|
|2000|5.116373210697169e−49|1745.2244560374763|13.940532374935973|0.34053237493597344|13.6|
|20000|9.39264787331677e−18|25.62744167910542|16.745419384350164|3.1454193843501645|13.6|
|200000|1.575911644076433e−14|1.6539695673614858|38.326261184542375|24.726261184542373|13.6|

낮은 T의 큰 \(\kappa_2/\alpha\)는 threshold tail의 energy 가중을 나타낸다. 절대 rate와 밀도를 함께 보기 전에 강한 우주론적 감쇠라고 해석할 수 없다.20,000K에서 \(\kappa_2=2.407095355857991\times10^{-16}\,\mathrm{m^3/s}\)다.

HE36 저장 finite-CCC와 LC의 rate 비는20,000K에서 **3.4227965000657132**,129온도 전체에서 **1.4914460903852345–7.095479155037354**다. CCC는 threshold13.6058eV와13.6058–968.61eV의 양의 PL 유한 표를 적분했고, LC는 threshold13.6eV인 다른 semiclassical kernel의 전 에너지 적분이다. 이 차이는 두 source가 서로 대체 가능한 보정 자료가 아님을 드러낸다. 수치 적분 실패나 calibrated physical uncertainty로 표시하지 않는다. CCC 저장129행을 읽었을 뿐 kernel 재평가는0이다.

## 6. 독립 원적분·비용·그림

동일 LC kernel의 원래 \(\sigma v\) Maxwellian 적분을 별도 양의 GL lane으로 계산했다. \(t=(E-I)/\theta\in[0,64]\), 계획된64→96→128차 refinement와 상대 gate \(3\times10^{-12}\)를 먼저 고정했다.

| 항목 | 실제 결과 |
|---|---:|
|GL64 최대 상대차|9.138023671084738e−12, 계획된 refinement|
|GL96 최대 상대차|2.2426505097428162e−14, PASS|
|GL128|첫 통과 뒤 실행하지 않음|
|잘린 \(t>64\) tail의 최대 상대 상한|4.617226718601215e−24|
|80자리 원적분 oracle의 최대 상대차|2.1974065901747693e−14|

Tail bound는 선택한 analytic 모형의 계산 tail만 제한한다. 실제 H1 단면적의 모델 오차, CCC 표 밖의 tail, outgoing angular calibration을 제한하지 않는다.

같은129온도·4모멘트의 analytic 계산과 통과한 GL96을2warmup/각lane 후5쌍으로 번갈아 측정했다. 각 trial은 lane당64batch다. Node 준비 비용을 분리하고 실제 반환·검증 overhead는 포함했다.

| 비용 측정 | 저장 결과 |
|---|---:|
|쌍별 GL/analytic 비 중앙값|4.4825080029195785×|
|쌍별 비 범위|3.892765018690632–8.538838605855716×|
|중앙 시간의 비|4.41035830843409×|
|analytic batch 중앙 시간|0.21943646875ms|
|GL96 batch 중앙 시간|0.967793453125ms|
|진단 전체 wall time / 최대RSS|0.49922332899586763s /47180KiB|

이는 공유 sandbox의 동일 reference kernel 비교다. 전체 network, IVP 또는 Fortran/HPC 처리량 향상으로 확대하지 않는다. 환경은 Xeon Platinum8573C, CPU affinity9·quota8, memory8GiB, Python3.12.14/NumPy2.3.5/SciPy1.17.0, OMP/BLAS/MKL thread1이다.

`components/diagnostic/plots/h1_gain_diagnostic.png`와 `.svg`에 실제 scientific figure 한 쌍을 저장했다. 첫 render의 footer/x축 겹침을 열어 확인하고 첫 파일을 보존했다. Margin과 주석 위치만 고친 두 번째 render를 다시 검사했다. Scientific CSV, 진단, benchmark는 반복하지 않았다. 최종 PNG SHA256은 `13643f1caff1714ed828f8b4650af27b95d4314c4e2d827094c7a4bd8d470099`다.

## 7. 기존 사건 장부와 연결한 구현

새 adapter는21길이 \(Y=n/n_B\) 중 H0(index1), H+(index2)만 nonzero이고 그 합이1인 pure-H inventory를 받는다. 전하중성으로 \(n_e=n_BY_{H+}\), \(n_H=n_BY_{H0}\)를 정한다. 입력 stress는 **전자 \(\pi_e\)**이며 전체 gas \(\pi_b\)로 바꾸지 않는다. All-retained-thermal과 neutral21-state census를 호출자가 명시해야 한다.

REI donor에는 electron-reactant slot이 없어 현재 상태의 \(n_e\alpha\)를 frozen coefficient로 하는 H0→H+ effective unary event를 만든다. 사건 장부는 \(dI=+I\), \(dE_{\rm th}=-I\)이며 net tensor는

\[
S_{\rm event}=-\frac{2I}{3}\mathbf1-
\frac{\kappa_2}{\alpha}\frac{\pi_e}{n_e}.
\]

기존 HE36 `attach_event_tensor`가 같은 사건률로 이를 volume source에 결속한다. \(Q=\operatorname{tr}S/2=-Ir\), \(J=-n_H\kappa_2\pi_e\)이고, potential \(+Ir\)가 kinetic loss와 장부에서 상쇄된다. Returned Q와 donor dEth는 **같은 energy owner의 두 표현**이므로 더하지 않는다. Net tensor의 음의 고윳값을 covariance처럼 clipping하지 않는다.

Frozen \(n_e\) donor Jacobian을 실제 physical Jacobian으로 쓰지 않았다. 실제 abundance source는 \(F_{H0}=-n_B\alpha Y_{H0}Y_{H+}\), \(F_{H+}=-F_{H0}\)이고 두 abundance 미분을 별도 반환한다. 온도와 밀도는 이 Jacobian에서 고정이다. Pure-H simplex의 허용 tangent도 명시했다. 전자가0이면 source는0이지만 전자 활성화 방향의 Jacobian을 보존한다.

All-retained common-T 해석의 reaction-only 온도항은

\[
\dot T=-\frac{r}{n_{\rm part}}
\left(T+\frac{2I}{3k_B}\right).
\]

이는 energy equation의 입자수 증가 항을 한 번 포함한 결과다. 즉시 열화와 공통 온도가 실제로 성립한다는 검증은 별도다. Vacuum의 온도는 미정으로 반환한다. Underflow를 physical zero로 바꾸지 않고, absent-electron에서 nonzero 전자 stress를 거부한다.

## 8. 검증·review·보존된 수정

| 검증 층 | 실제 저장 근거 |
|---|---|
|Source provider|6논리군 PASS: cross-section/분배/80digit moments/관계식/입력/immutable batch;3.615s,68656KiB|
|독립 유도|직접 Cartesian angle4사례, radial3사례, sharing4사례 PASS; 최대 tensor 상대1.4561819709916926e−15|
|Net bridge|7논리군 PASS; scalar 보존 최대 normalized5.995204332975845e−15, rotation1.1102230246251565e−16|
|Physical Jacobian|analytic 관계0잔차, 독립 tangent difference 최대2.9017643843332053e−10 <3e−9 gate|
|Domain/숫자 경계|잘못된25입력과 nonzero underflow/overflow 거부;3zero-state 의미 구분|
|최종 독립 code/plot review|PASS_SCOPED; 이전 문서 finding2개 closed, 새 중대한 결함 없음|

Source/theory 비저자 검토는 source equation, event/electron count, \(4/15\) contraction, 모멘트와 미분, \(\pi_e\) 범위를 확인했다. 사소한 두 문서 finding도 보존했다. 원전의 정확한 제목으로 bibliographic 표기를 고쳤고, NumPy coercion 때문에 혼합 bool/numeric 입력까지 모두 거부한다는 provider 설명은 실제 보장 범위로 좁혔다. 새 net adapter는 혼합 bool도 별도 검사한다. 이런 문서 정밀화는 기존 과학 계산을 반복할 이유가 되지 않았다.

추가 독립 검토는 원래 suite를 다시 실행하지 않고, transfer quantile의 특정 경계4호출과 tiny-STF bridge1호출을 수행했다. 후자는 provider 온도평가1회를 포함한다. 입력 전자 stress가 \(\operatorname{diag}(10^{-200},-10^{-200},0)\,\mathrm{Pa}\)인 경우 direct J는 \(\operatorname{diag}(-1.684966749100594,1.684966749100594,0)\times10^{-210}\,\mathrm{Pa/s}\)로 남았다. 80자리 Decimal 곱과 상대차2.220446049250313e−16이다. 반면 isotropic 부분이 지배하는 full S를 float로 만든 뒤 다시 투영하면 이 작은 성분은 소실될 수 있다. `components/net_bridge/TINY_STF_USAGE.md`는 반환된 direct J를 쓰도록 명시한다. 과학 코드는 수정하지 않았다.

새 실행 집계는 provider 검증1, 독립 유도검증1, net-bridge 검증1,129T 진단1, benchmark1, render2/최종1쌍이다. Wolfram의 새 exact algebra 확인1회와 독립 검토의 targeted 호출도 `RUN_RECORD.json`에 별도로 기록했다. Benchmark의 반복 batch와 planned quadrature refinement는 각 receipt에 별도로 기록했다. 기존 IVP·suite·그림 replay는0이다. 미래 실행 수는 검증된 receipt가 생기기 전에 더하지 않는다.

## 9. 단계별 DAG·백업·게시

R1→R10→C1→C10의20단계와 과학 전체 목표를 분리한다. 각 단계는 실제 근거, backup ACK, Git commit을 기록한다. 단계별 실제 commit·archive SHA256·Dropbox ID·완료율·다음 단계는 `STAGE_LEDGER_KO.md`와 `delivery/*_ACK.json`에서 읽는다. Logical stage acceptance와 병렬 component의 실제 실행 시각을 같다고 만들지 않는다.

|순서|단계|과학·전달 근거|정확한 게시/백업 기록|
|---:|---|---|---|
|1|R1 연구 위치·계약|[단계 기록](stages/R1.md)|[ACK](delivery/R1_ACK.json)|
|2|R2 근거·재사용|[단계 기록](stages/R2.md)|[ACK](delivery/R2_ACK.json)|
|3|R3 주장·전제 정렬|[단계 기록](stages/R3.md)|[ACK](delivery/R3_ACK.json)|
|4|R4 가설·표현 탐색|[단계 기록](stages/R4.md)|[ACK](delivery/R4_ACK.json)|
|5|R5 구성적 유도|[단계 기록](stages/R5.md)|[ACK](delivery/R5_ACK.json)|
|6|R6 독립 검증|[단계 기록](stages/R6.md)|[ACK](delivery/R6_ACK.json)|
|7|R7 판별 검증|[단계 기록](stages/R7.md)|[ACK](delivery/R7_ACK.json)|
|8|R8 결과 판정|[단계 기록](stages/R8.md)|[ACK](delivery/R8_ACK.json)|
|9|R9 정식 결과·코딩 연결|[단계 기록](stages/R9.md)|[ACK](delivery/R9_ACK.json)|
|10|R10 종료·재개|[단계 기록](stages/R10.md)|[ACK](delivery/R10_ACK.json)|
|11|C1 목표·baseline|[단계 기록](stages/C1.md)|[ACK](delivery/C1_ACK.json)|
|12|C2 식–데이터–코드|[단계 기록](stages/C2.md)|[ACK](delivery/C2_ACK.json)|
|13|C3 수치 설계|[단계 기록](stages/C3.md)|[ACK](delivery/C3_ACK.json)|
|14|C4 실행 DAG·자원|[단계 기록](stages/C4.md)|[ACK](delivery/C4_ACK.json)|
|15|C5 구현|[단계 기록](stages/C5.md)|[ACK](delivery/C5_ACK.json)|
|16|C6 구현 검증|[단계 기록](stages/C6.md)|[ACK](delivery/C6_ACK.json)|
|17|C7 과학 검증|[단계 기록](stages/C7.md)|[ACK](delivery/C7_ACK.json)|
|18|C8 수치·재현성|[단계 기록](stages/C8.md)|[ACK](delivery/C8_ACK.json)|
|19|C9 독립 검토|[단계 기록](stages/C9.md)|[ACK](delivery/C9_ACK.json)|
|20|C10 판정·인계|[단계 기록](stages/C10.md)|[ACK](delivery/C10_ACK.json)|

최종 archive를 provider가 수신한 ACK와 local payload hash 검증은 전체 archive를 원격에서 다시 내려받아 복원한 실행과 다르다. 어떤 검증이 실제로 수행됐는지는 `delivery/FINAL_ACK.json`에서 그대로 읽는다. Moving publication pin과 immutable science pin도 분리한다.

## 10. 남은 과학과 다음 DAG

다음 단원은 단순히21상태를 더 많이 적분하는 작업보다, 이번 approximation을 바꿀 때 필요한 입력의 소유자를 먼저 정해야 한다.

1. **N0 변경분 확인:** 이번 cutoff와 producer pins 이후 변경만 조사한다. Unchanged evidence와 완료한129T/그림은 재사용한다.
2. **N1 source 보강:** H1 differential energy/angular 자료로 \(D(E)\)를 실제 공급하거나, finite-mass에 맞춘 차등 kernel을 별도 source 계약으로 정한다. 총 단면적만 바꿔 기존 isotropic gain을 calibrated라고 부르지 않는다.
3. **N2 net source 확장:** 선택한 source의 number·momentum·heat·STF, target recoil·종별 transfer를 같은 frame과 사건률에서 합한다. \(\pi_e\rightarrow\pi_b\) 분배는 독립 입력이다.
4. **N3 열·광원 및 N5 수송:** 재사용 가능한 PHYS81/C23A/REC provider의 적용 종·T·z·spectrum·에너지 owner를 맞춘다. Finite UVB 범위를 z20까지 자동 외삽하지 않는다. 열화·momentum relaxation을 Hubble·반응 시간과 비교한다.
5. **N4 핵 과정:** daughter isotope/charge, kinetic spectrum, recoil, stopping, thermal/fast **수와 에너지**를 명시한다. Supplied energy partition만으로 thermal 입자 membership을 정하지 않는다.
6. **N6→N7 closure와 reduction:** 공통T/u, 유한 비등방성의 오차 예산을 먼저 정하고 population lift와 heat/STF source의 commute를 검사한다.
7. **N8→N9 새 결합 계산:** 준비된 선택 범위에서 저장 배경 하나에만 bounded population/T/stress IVP를 새로 정의하고, 이후 nonbaryonic matter와 분리한 baryon metric feedback을 검증한다.

RR·DR·CX, 다른 isotope, 음이온·분자는 source별 추가 admission을 통과해야 한다. 이번에 얻은 recoil inequality는 에너지 scale의 조건부 상한이며 finite-mass stress의 오차 인증을 대신하지 않는다. 완료된 HE32–HE36을 재생성할 근거는 없다.

## 11. 재현·인계 원칙

다음 대화에서는 `README.md`, 본문, `DAG.json`, `NEXT_DAG.json`, `GLOBAL_GOAL_DAG.json`, `delivery/FINAL_ACK.json`, 두handoff를 먼저 읽고 immutable science payload를 읽기 전용 검증한다. Source/code/domain identity가 같으면 저장 receipt·CSV·PNG/SVG를 사용한다. 변경이 있을 때만 영향받은 입력·가정·test group을 지정하여 새로운 attempt 경로에서 실행한다. 환경 문제나 문서 수정은 source 물리나 허용오차를 몰래 바꾸는 이유가 아니다.

연구 스레드용 handoff는 원전·유도·미해결 물리 선택을 전달하고, Codex/executor용 handoff는 고정된 revision의 환경 확인·최소 실행 경계 수정과 승인된 DAG node 실행만 전달한다. 최종 복사용 두 문서는 `HANDOFF_CHAT_KO.md`, `HANDOFF_CODEX.md`에 제공한다.
