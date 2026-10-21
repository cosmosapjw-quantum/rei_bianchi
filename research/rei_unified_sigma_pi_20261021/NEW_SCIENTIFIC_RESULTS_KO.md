# 저장된 z=20→2 궤적의 물리 해석 — D4 준비, D7 최종 판정 대기

이 보고서는 Lane B의 **175점 matter/radiation 초기조건 격자와 기존 91점 radiation 단면을 z=2까지 연장한 실제 원자료**를 해석한다. 두 집합의 공통 nominal 35점을 중복 제거하면 nominal 231개이고, 서로 다른 refinement control 6개를 더한 고유 history는 237개다. 각 history는 기존 121개 sample을 보존하고 z=4→2의 32개 sample을 덧붙인 153개 epoch를 가진다. 본 보고서의 후처리는 ODE를 실행하지 않았다. 근거는 `NEW_SCIENTIFIC_EVIDENCE.json`, `CANCELLATION_TURNOVER_SAMPLES.csv`, 아래의 원자료·그림 경로다. [E1–E6]

새로운 핵심 결과는 세 가지다. 초기 총 응력이 상쇄되어도 성분별 진화 차이로 shear가 생성된다. 이 shear의 크기는 두 상쇄 사례에서 z≈4.37의 저장 sample에서 최대가 된 뒤 z=2까지 감소한다. 또한 초기 shear가 0.003인 25점 단면에서는 z=4에 모두 양수였던 signed shear 중 4개가 z=2에 음수가 된다. 모두 아래에 지정한 유한 격자와 restricted collisionless LRS 모형의 결과다. [E1–E5]

## 1. 판정과 수치·물리 범위

`z2_extension/results/CHECK.json`은 237/237 완료와 `PASS_SCOPED_PRELIMINARY` numerical gate를 기록한다. 독립 raw 감사 `independent_audit/B2_FINAL_RAW_AUDIT.json`의 판정은 `PASS_SCOPED_NUMERICAL_RAW`다. 이 해석 문서는 별도의 scientific admission을 발행하지 않는다. 그림과 주장까지 포함한 최종 판정은 독립 final-audit 영수증을 따른다. Production scientific admission은 이 결과로 발행되지 않는다. [E2, E7]

고정 모형은 non-tilted, reflection-even LRS Bianchi I이며 massive matter의 fraction은 0.1, 내부 질량 비는 `mass_over_Tref=30`이다. Nominal momentum grid는 24×12 cells, subcell Gauss order 3, massless hierarchy는 L=8, solver는 DOP853, `rtol=3e-11`, `atol=3e-13`이다. 양의 massive 분포의 초기 각도 인자는 `1+A_m P₂(μ)`이고 matter와 radiation의 initial quadrupole을 각각 실현한다. Photons와 exactly massless neutrinos는 같은 초기 brightness와 collisionless operator를 공유한다. 이 실험에서 gamma/nu를 각각 저장한다는 사실은 독립적인 photon/neutrino 초기 사중극이나 collision operator를 시험했다는 뜻이 아니다. [E3, E8]

6개 refinement control의 z=2 endpoint 비교는 모두 PASS이며, CHECK에 기록된 비교량 중 최대 차이는 `3.5701298281608576e-13`이다. 이는 `Sigma_F`의 nominal/refined endpoint 차이이며, 보존되는 gate `2e-6`보다 작다. 이 결과는 해당 6개 조건의 refinement 비교다. 연속 parameter 공간 전체의 오차 상한이나 153개 sample 사이의 극값 위치 오차를 인증하지 않는다. Hamiltonian 검사는 construction consistency, radiation brightness 양성 검사는 64-node angular sample 범위라는 기존 한계도 유지한다. [E2]

PR198 Lane A의 625개 baseline과 606개 신규 trajectory는 z=20→4의 기존 preliminary 결과로 보존했다. 본 Lane B의 175점 격자를 그 수에 단순 합산하지 않는다. PR199 age-exposure의 `NATIVE_AGE_TIME_CONVERGENCE=HOLD`, `NONLINEAR_GRACKLE_RESPONSE_BOUND=NOT_ESTABLISHED`도 이 보고서로 변경되지 않는다. Lane B 원래 wrapper의 실행 identity는 `UNPUBLISHED_WITH_SHA256`이며, vendor source pin `3b85dedce84d37b3e165da00685a8a984950aafe`와 구별한다. 현재 task가 PR199 계열 디렉터리에 있다는 이유로 원래 실행을 PR199 commit에서 수행한 것으로 바꾸지 않는다. [E8–E10]

## 2. 이 보고서의 signed 변수와 norm

모든 아래 숫자는 full spatial Frobenius convention을 쓴다.

\[
S_F=\sqrt6\,s/H,\qquad \Sigma_F=|S_F|,
\]

\[
P_X=\sqrt6\,Kp_X/H^2,\quad
\Pi_{X,F}=|P_X|,\quad
\Pi_{\mathrm{tot},F}=|P_m+P_r|,\qquad K=8\pi G/c^2.
\]

여기서 `p_X`는 `diag(-p_X,-p_X,2p_X)`의 scalar amplitude이며 J/m³ 단위다. Half-contraction 변수로 바꾸려면 **signed 값과 norm 모두 √2로 나눈다.** 음의 `S_F`는 지정한 LRS 축 방향에 대한 shear의 부호다. Norm `Σ_F`가 음수가 된다는 의미가 아니다. Proper time은 초 단위이고, redshift는 mean scale factor로 정의한 `z̄=1/a−1`이다. 관측 방향별 redshift를 계산한 것이 아니다. [E1, E8]

## 3. 초기 상쇄가 풀리면서 생성되는 shear

다음 두 사례는 실제 175점 격자에 속한다. 초기값은 `(Σ_F,i,P_m,i,P_r,i)` 순서다. C+의 실현 초기 총 stress는 `−1.0842e-19`, C−는 0이며, 양쪽 모두 초기 shear는 0이다. [E1, E3]

| 사례 | 초기값 | case ID |
|---|---|---|
| C+ | `(0,+0.0003,−0.0003)` | `9bad767cd17b0651746fca2bd9c6ad6911a6df067ad58af71ab0872827ccacf9` |
| C− | `(0,−0.0003,+0.0003)` | `85b934bda9234641873454696f22e7cd74c757c944f34820d1e30cd1e1afea3b` |

| 저장 endpoint | C+의 signed `S_F` | C−의 signed `S_F` |
|---|---:|---:|
| z=4 | −3.681005243450802e−5 | +3.6809470587529176e−5 |
| z=2 | −3.145959056164794e−5 | +3.1458662949047326e−5 |

| 사례·epoch | signed `P_m` | signed `P_r` | signed `P_m+P_r` |
|---|---:|---:|---:|
| C+, z=4 | +1.7076727809119897e−5 | −7.052601704888440e−5 | −5.344928923976450e−5 |
| C+, z=2 | +5.796553169574794e−6 | −3.984480758512121e−5 | −3.404825441554641e−5 |
| C−, z=4 | −1.7075820171316826e−5 | +7.052333681211752e−5 | +5.344751664080069e−5 |
| C−, z=2 | −5.796077155794989e−6 | +3.984246839294093e−5 | +3.404639123714594e−5 |

두 species가 다른 속도로 진화하므로 초기 tensor sum이 0이라는 조건은 보존되지 않는다. 이 결과는 Einstein geometry에 실제 `P_m+P_r`를 넣은 coupled trajectory의 결과다. 서로 독립적으로 적분한 두 shear를 나중에 더해 만든 그림이 아니다. [E1, E3, E8]

상쇄 비율을 다음과 같이 정의하면 상대적인 상쇄의 약화를 구분할 수 있다.

\[
C=1-\frac{|P_m+P_r|}{|P_m|+|P_r|}.
\]

C+에서 `C`는 초기 약 1, z=4에 0.3898674, z=2에 0.2540044다. C−도 각각 1, 0.3898627, 0.2539992다. 따라서 endpoint의 상대적인 상쇄는 점차 약해진다. 동시에 z=4→2에서 **총 signed stress의 절댓값 자체는 감소**한다. 상쇄 비율의 감소를 응력 절댓값의 증가로 읽어서는 안 된다. [E1]

그림 근거는 `opposite_component_histories.png/.pdf`다. 상단에는 signed matter/radiation/total stress, 하단에는 signed shear와 Frobenius 및 half-contraction norm이 함께 표시된다. 세로 점선은 저장된 z=4 접합점이다. 연결선은 저장된 epoch들을 연결하며, 그 자체를 추가 적분이나 연속 극값 인증으로 해석하지 않는다. [E4]

## 4. 완료한 다음 read-only 노드: 상쇄 사례의 turnover

이번 결과 해석에서 선택하여 완료한 단일 후속 노드는 `cancellation_turnover_on_saved_histories`다. 기존 153개 sample에서 `|S_F|`의 최대를 찾고, 같은 저장 state에 대한 원래 source 식으로 `S_F′`를 평가했다. 새 IVP는 0개다. 이 작업은 D4의 해석 준비이며, D5/D6 이전에 D7의 최종 과학 판정을 발행한 것이 아니다. [E1, E6]

| 양 | C+ | C− |
|---|---:|---:|
| 저장 sample의 최대 `|S_F|` | 3.690192005181101e−5 | 3.690140273141657e−5 |
| 해당 sample의 index | 114 | 114 |
| 해당 `z̄` | 4.371956272299825 | 4.371956272299825 |
| `|S_F(z=2)| / 저장 최대` | 0.8525190699 | 0.8525058838 |
| `|S_F(z=2)| / |S_F(z=4)|` | 0.8546467196 | 0.8546350286 |

양쪽 모두 저장된 최대점은 z=4 접합보다 조금 이른 시점에 있다. C+에서 `S_F′`는 index 114의 `−1.62605e−7`에서 index 115의 `+3.29000e−7`로 부호가 바뀐다. 두 sample의 redshift는 각각 4.3719562723과 4.3080954627이다. C−에서는 같은 구간에서 반대 방향으로 부호가 바뀐다. 원래 ODE의 매끄러운 진화를 전제로 이 두 sample은 극값 전환을 포함하는 구간을 제공하지만, 여기서 별도의 dense-output root나 연속 극값 위치를 계산하지 않았다. [E1, E6]

감쇠가 가능한 이유는 instantaneous total stress의 부호와 shear의 변화율 부호가 같은 양이 아니기 때문이다. `x=ln(a/a_i)`, `h=H′/H`라 하면 검증된 shear 식은

\[
S_F'=-(3+h)S_F+P_m+P_r
\]

이다. C+의 z=2에서는 `P_m+P_r<0`이 유지되지만 `S_F<0`인 상태에서 팽창 감쇠항이 반대 부호로 작용하여 `S_F′=+1.6644303e−5`다. 따라서 signed shear는 0을 향해 이동하며 norm은 줄어든다. C−에서는 부호를 바꾼 대응 현상이 나타난다. 이것이 “응력 상쇄가 풀렸으므로 shear norm이 계속 커져야 한다”는 해석이 성립하지 않는 구체적인 이유다. [E1, E6, E8]

## 5. 초기 국소 유도와 수치 결과의 연결

초기 geometry가 isotropic하고 `S_F=0`, `P_m+P_r=0`일 때 massive anisotropic stress와 massless stress의 초기 dilution rate는

\[
p_m'=(-5+B_m)p_m,\qquad p_r'=-4p_r
\]

이다. 여기서

\[
B_m=\frac{\int q^6F(q)/(M^2+q^2)^{3/2}\,dq}
{\int q^4F(q)/(M^2+q^2)^{1/2}\,dq}
\]

는 초기 pressure weight에 따른 `v²/c²` 평균이다. 실제 source의 number/quadrature weight를 사용한 nominal 값은 `B_m=0.031700764390593536`이다. `F(q)`는 구현의 decoupled momentum profile이고 `M=30`이다. 이 식은 초기 isotropic geometry에서 적용되는 국소 식이며, b≠0의 전체 진화를 등방적 dilution law로 대체하는 처방이 아니다. [E8]

따라서 초기 상쇄점에서

\[
S_F'(0)=0,\qquad
S_F''(0)=-(1-B_m)P_{m,i}.
\]

C+의 curvature는 `−2.904897706828219e−4`, C−는 `+2.904897706828219e−4`다. 이는 실제로 생성되는 초기 shear 방향과 일치한다. PR198 half-contraction 식과도 모순되지 않는다. `S_F=√2 S_{1/2}`, `P_F=√2 P_{1/2}`이므로 두 변수를 함께 변환하면 식의 계수는 그대로다. 여기서 `S_F≈½S_F″(0)x²`는 초기 국소 전개이며, z=2 endpoint를 예측하는 보편적인 fitting law가 아니다. [E1, E8]

## 6. 175점 fixed-Σ 단면의 endpoint 비교

실제로 계산한 초기 축은 다음과 같다. [E3, E5]

\[
\Sigma_{F,i}\in\{0,0.0003,0.001,0.003,0.01,0.03,0.1\},
\]

\[
P_{m,i}\in\{-0.0003,-0.0001,0,0.0001,0.0003\},
\]

\[
P_{r,i}\in\{-0.001,-0.0003,0,0.0003,0.001\}.
\]

양의 초기 Σ에는 `s_i>0`의 방향을 부여했다. 각 Σ 단면은 25개의 실제 discrete point다. 아래의 음/양 판정은 `|S_F|≤5e−12`를 zero bin으로 둔다. [E1]

| 초기 `Σ_F` | z=4 음/0/양 개수 | z=2 음/0/양 개수 | z=2 signed `S_F` 최솟값 | z=2 signed `S_F` 최댓값 |
|---:|---:|---:|---:|---:|
| 0 | 12 / 1 / 12 | 12 / 1 / 12 | −1.8944616715e−4 | +1.8937787091e−4 |
| 0.0003 | 11 / 0 / 14 | 11 / 0 / 14 | −1.7406528297e−4 | +2.0472575594e−4 |
| 0.001 | 5 / 0 / 20 | 7 / 0 / 18 | −1.3817647785e−4 | +2.4053762109e−4 |
| 0.003 | 0 / 0 / 25 | 4 / 0 / 21 | −3.5636382495e−5 | +3.4285831934e−4 |
| 0.01 | 0 / 0 / 25 | 0 / 0 / 25 | +3.2326418479e−4 | +7.0099603849e−4 |
| 0.03 | 0 / 0 / 25 | 0 / 0 / 25 | +1.3488492059e−3 | +1.7244444421e−3 |
| 0.1 | 0 / 0 / 25 | 0 / 0 / 25 | +4.9428270111e−3 | +5.3114320971e−3 |

특히 `Σ_F,i=0.003`의 4개 조건은 z=4 이후 endpoint 사이에서 signed shear의 방향이 바뀐 사례다. z=4 그림만으로 z=2의 부호를 판정하면 이 사례를 놓친다. 반면 위 표만으로 임계 Σ 값이나 연속적인 zero contour를 제시할 수는 없다. `0.003<Σ<0.01` 내부를 계산하지 않았고, 양의 초기 shear 방향만을 사용한 지정 격자라는 한계가 있다. [E1, E5]

`component_planes_all175` 및 7개의 `component_plane_sigma_*` 그림은 endpoint의 matter와 radiation stress를 각각 보여준다. 서로 다른 성분과 epoch의 colorbar 단위를 읽어야 한다. 초기 stress 간격은 균일하지 않아 그림은 categorical axes를 쓰며, 빈 공간을 보간된 해로 채우지 않았다. 선택한 `Σ_F,i=0.003` 단면의 `signed_shear_joint_sigma_0p003.png/.pdf`는 위의 4/25 late reversal을 나타내는 그림이다. 상단은 z=4와 z=2의 signed `S_F`, 하단은 같은 시점의 total norm `|P_m+P_r|`를 표시한다. 각 quantity는 두 epoch에서 공통 color scale을 쓴다. 해당 4개는 모두 `P_r,i=−0.001`이고 `P_m,i∈{−0.0003,−0.0001,0,+0.0001}`이다. 나머지 `P_m,i=+0.0003` 조건은 z=2에도 양수다. 최종 figure manifest의 실제 생성·감사 상태와 함께 읽어야 한다. [E4–E5]

## 7. 초기 matter/radiation에 대한 유한 차분 응답

Σ를 고정하고 다른 성분의 초기 stress를 0으로 둔 실제 네 endpoint에서 central secant를 계산했다.

\[
R_m=\frac{S_F(\Sigma_i,+d,0)-S_F(\Sigma_i,-d,0)}{2d},\quad
R_r=\frac{S_F(\Sigma_i,0,+d)-S_F(\Sigma_i,0,-d)}{2d},
\quad d=0.0003.
\]

초기 `Σ_F=0`의 결과는 다음과 같다. [E1]

| endpoint | matter secant `R_m` | radiation secant `R_r` | `R_r/R_m` |
|---|---:|---:|---:|
| z=4 | 0.11914688240072484 | 0.24184607845589268 | 2.029814574942008 |
| z=2 | 0.06503712008911774 | 0.1699008720617596 | 2.6123677036890824 |

양쪽 성분의 endpoint 응답 크기는 z=4→2에서 작아지지만 이 비는 커진다. 이 범위에서는 matter에 대한 endpoint 응답이 radiation보다 더 빠르게 줄어드는 경향을 보여준다. 비는 순간 pressure ratio가 아니라 **유한 초기 perturbation에 대한 최종 shear 차이의 비**다. 7개 고정 Σ 단면에서 같은 방식으로 구한 z=2 비는 2.61237–2.61995 범위이며, 입력 case ID는 evidence JSON에 남겼다. [E1]

이 secant는 실제 네 점의 비교이며 universal derivative, linear superposition, global response fit, continuous interpolation certificate를 의미하지 않는다. PR198의 별도 1,225개 training point descriptive fit과 수치가 가깝더라도 학습 집합·norm·source wrapper·표본 범위를 지우고 같은 fit으로 취급하지 않는다. 여기서는 norm 변환에 공통 √2가 적용되어 계수 비가 유지된다는 사실과, 각각의 지정 finite data 결과를 구분한다. [E1, E8–E10]

## 8. 근거 파일과 재현 경로

아래에서 `B/`는 repository 상대 경로 `research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/`이다. 본 보고서·evidence·analysis script는 통합 task 산출물이며, 게시 시에도 상대적인 scientific identity는 아래 경로와 hash를 기준으로 유지한다.

| 근거 | 경로·범위 |
|---|---|
| E1 | `NEW_SCIENTIFIC_EVIDENCE.json`: 두 cancellation case의 원자료/input/receipt SHA256, endpoint, sampled peak, derivative bracket, fixed-Σ counts, secant input IDs |
| E2 | `B/z2_extension/results/CHECK.json`: 237개 완료, 6개 refinement 비교, scoped numerical gate |
| E3 | `B/z2_extension/results/cases/<case-ID>/{INPUT.json,RESULT.json,raw.npz}`: 실제 initial axes, full saved states, joined diagnostics |
| E4 | `B/z2_extension/figures/{opposite_component_histories,component_planes_all175,component_plane_sigma_*,signed_shear_joint_sigma_0p003}.{png,pdf}`; `PLOT_MANIFEST.json` |
| E5 | `B/z2_extension/figures/component_endpoints_175_z4_z2.csv`: 175×2 endpoint row와 ID |
| E6 | `analyze_cancellation_turnover.py`, `CANCELLATION_TURNOVER_SAMPLES.csv`: 실행 적분 없는 재현 후처리, 두 사례 총 306개 sample |
| E7 | `independent_audit/B2_FINAL_RAW_AUDIT.json`: 원자료의 독립 감사; 최종 그림·과학 판정은 후속 독립 감사 영수증 참조 |
| E8 | `PHYSICAL_CONVENTION_DRAFT.md` 및 `PHYSICS_EVIDENCE.json`의 보존 사본, `cancellation_curvature_check.json`: 방정식/코드 adapter, pressure weight와 국소 유도; original recovery source는 `../recovery_physics/` |
| E9 | `PHYS_MATH_CONTRACT_REVIEW.json`, `UNIFIED_EXECUTION_CONTRACT.md`: 새 B1/B2 실행의 사전 범위와 승인된 계보 |
| E10 | `UNIFIED_STATUS.md`, `CASE_PROVENANCE_LEDGER.*`: Lane A/B/C의 identity·실행·게시·검증 분리; 독립 연구 상태의 최종 정리는 해당 파일을 따른다 |

C+의 joined raw SHA256은 `bcbac8d5b1601611038d44c866109445c08049d099be86aa8f98676f740551ca`, C−는 `5c1a88890332a71c9e18c0794131359fdae4b67a7c5587343126aace2a84ca6a`다. 분석 시점의 CHECK SHA256은 `cb73197cbf9a5ea76e6f3a8d1e5d7b495b0a2f5a62a1d75f4e73992e0c8d8428`이다. 이후 publication receipt나 판정 문서 추가가 원자료의 실행 시점을 소급 변경하지 않는다. [E1]

문헌에 기반한 collisionless momentum/moment 정식화는 Heinzle & Uggla, *Classical and Quantum Gravity* 23 (2006), DOI [10.1088/0264-9381/23/10/016](https://doi.org/10.1088/0264-9381/23/10/016), [arXiv:gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031), 및 Rendall & Uggla, *Classical and Quantum Gravity* 17 (2000), DOI [10.1088/0264-9381/17/22/310](https://doi.org/10.1088/0264-9381/17/22/310), [arXiv:gr-qc/0005116](https://arxiv.org/abs/gr-qc/0005116)에 근거한다. 문헌의 single-species 또는 특정 asymptotic theorem을 이 multisector finite pilot의 수치 인증으로 사용하지 않는다. 본 보고서의 새 수치는 외부 논문에서 인용한 값이 아니라 위 저장 원자료에서 직접 계산한 값이다.

## 9. 연구 판정과 이어갈 단일 노드

현재 보존해야 할 판정은 `derived`인 norm·shear·초기 curvature 식, `implementation-verified`인 source mapping, `numerically checked`인 유한 격자의 endpoint와 turnover이며, continuous parameter theorem이나 관측 likelihood는 `unresolved`다. 선택한 read-only scientific node의 D4 해석 준비는 완료했다. D7의 최종 판정은 D5 독립 감사와 D6 게시·백업을 충족한 뒤 기록한다. 현재의 후처리 completion은 신규 수치 격자에 대한 권한이나 다른 lane의 HOLD 해소를 뜻하지 않는다.

다음 노드는 새 solver 실행이 아니라, **독립 감사가 승인한 그림·이 보고서·evidence·source hash를 같은 publication manifest와 이중 백업 receipt에 묶는 D6/D7 종료 절차**다. Source와 raw를 보존한 채 외부 게시·백업의 실제 ACK 및 전체 readback을 기록하면, 다음 대화에서는 같은 계산을 재실행하지 않고 이 결과의 과학적 범위를 유지하여 이어갈 수 있다.
