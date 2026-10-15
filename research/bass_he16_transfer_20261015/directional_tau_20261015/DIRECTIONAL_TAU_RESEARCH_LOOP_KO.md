# HE18 → rei_bianchi: 방향별 상대 적색편이와 Thomson 광학깊이 연구 (2026-10-15 KST)

## 결과와 근거 상태

- DERIVED: non-tilted normal-frame LRS Bianchi I의 방향별 상대 적색편이 정확식, 방향별 광학깊이의 첫 번째 전단 응답, 단조 root solver의 조각별 조건.
- NUMERICALLY_CHECKED: 실제 AXBI cold 다섯 signed prefix의 본래 \(a(t),b(t),n_e(t)\)와 저장 누적 \(\tau(t)\)로 방향별 발광 시점 역산 및 적분. ZERO, \(q=\pm0.005,\pm0.01\), 각 200001행. 이전 original signed source-epoch SHA256: d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185.
- IMPLEMENTATION_VERIFIED: Ubuntu NumPy/Python 직접 실행, 독립 Python scalar root parity, 등방 및 상수 b 해석적 극한, 부호/방향 반사대칭, 저장행/각구적의 민감도, 회귀 테스트.
- NOT CERTIFIED: 원 native ODE 전역 오차, 실제 polarized Thomson transfer, 방향별 현재 시점 CMB optical depth, BASS_HE 16셀 warm 모델과 cold AXBI의 물리학적 동등성. 원 native solver를 실행·변경하지 않았다.

## 고정 계량·컨벤션·경계

원래 Rust AXBI의 LRS Bianchi I metric은
\[
 ds^2=-c^2dt^2+a(t)^2e^{-2b(t)}(dx^2+dy^2)+a(t)^2e^{4b(t)}dz^2,\quad (-,+,+,+).
\]
Electron flow는 non-tilted, normal-comoving이고 공간 균질이다. 관측자는 공통 prefix 종점 \(a_o=0.08873654701704167,\ \bar z_o=10.269313869154184\)에 놓인다. 방출 시점은 그 이전이며, \(z_{\rm rel}\)은 *이 관측자를 기준으로 측정한 방향별 상대 적색편이*이다. 오늘날의 \(z=0\) 관측자와 CMB 전체 광학깊이가 아니다.

\(p_i\)는 Bianchi I 공간 Killing 방향의 보존 공변운동량이다. 관측자의 실제 orthonormal sky direction cosine \(\mu_o\)를 기준으로
\[
1+z_{\mathrm{dir}}(t,\mu_o)={a_o\over a(t)}
[(1-\mu_o^2)e^{2(b(t)-b_o)}+\mu_o^2e^{-4(b(t)-b_o)}]^{1/2}.
\]
\(\Delta b=b(t)-b_o\)가 작은 극한에서
\[
\delta\ln(1+z_{\rm dir})=(1-3\mu_o^2)\Delta b+O(\Delta b^2).
\]
전자 proper density는 \(n_e=n_H(x_{\mathrm HII}+f_{\mathrm He}(x_{\mathrm HeII}+2x_{\mathrm HeIII}))\), \(f_{\rm He}=1227/15092\). 고정된 광선의 observer-emission proper 구간에서 \(\tau_{\rm dir}(\mu_o,z_{\rm rel})=\sigma_Tc\int_{t_e(\mu_o,z_{\rm rel})}^{t_o}n_e(t)dt\). 서로 다른 방향에 대해 \(t_e\)가 달라진다. \(\sigma_T=6.6524587321\times10^{-29}\,\mathrm{m^2}\), \(c=299792458\,\mathrm{m/s}\); \(n_e\)[cm⁻³]→[m⁻³]에는 10⁶을 곱한다.

스칼라 평균 \(\tau_0=\frac12\int_{-1}^{1}\tau_{\rm dir}d\mu_o\); angular Legendre 계수는 \(\tau_2=\frac52\int_{-1}^{1}P_2(\mu_o)\tau_{\rm dir}d\mu_o\), \(P_2=(3\mu_o^2-1)/2\). \(E_{\tau_0}(q)=\frac12[\tau_0(+q)+\tau_0(-q)]-\tau_0(0)\), \(O_{\tau_2}(q)=\frac12[\tau_2(+q)-\tau_2(-q)]\).

## 새로운 첫 번째 전단-사중극 유도

평균 방출 scale \(a_e^{(0)}=a_o/(1+z_{\rm rel})\)에서 정상 전자밀도와 평균 팽창률 \(H=\dot a/a\)를 고정한 선형 변동은
\[
\delta\ln a_e=(1-3\mu_o^2)(b_e-b_o),\qquad
\delta\tau_{\rm dir}=-{\sigma_Tcn_e\over H}\delta\ln a_e.
\]
따라서
\[
\boxed{\tau_2^{(1)}(q,z_{\rm rel})
=2\bigg({\sigma_T c n_e\over H}\bigg)_{a_e^{(0)}}(b_e-b_o)+O(q^2).}
\]
이 식은 원래 coupled source의 native global error를 증명하지 않는다. 실제 \(q\)-의존 background와 기체의 상호작용을 제거한 국소 선형식이다. Wolfram은 방향별 \(\delta\ln(1+z)\)의 \(\mu\)선형항 \(1-3\mu^2\)과 평균 0을 확인했다.

## 원본 다섯 cold 이력의 실행 결과

동일한 관측자 mean \(a_o\)에서, 서로 다른 방향의 발광 사건은 각 이력의 방향별 redshift로 역산한다. 다음은 실제 저장된 source에 대한 높은 해상도 숫자이다.

| relative directional z | ZERO \(\tau_0\) | \(E_{\tau_0}(0.005)\) | \(E_{\tau_0}(0.01)/E_{\tau_0}(0.005)\) | \(O_{\tau_2}(0.005)\) | \(O_{\tau_2}(0.01)/O_{\tau_2}(0.005)\) |
|---|---:|---:|---:|---:|---:|
| 0.20 | 0.00173870684549 | -8.35674836e-9 | 3.99993011 | -5.74145356e-6 | 1.99996126 |
| 0.50 | 0.00278345855850 | -2.49195558e-8 | 3.99997185 | -6.03751093e-6 | 1.99982021 |
| 0.75 | 0.00304695696467 | -3.86954544e-8 | 4.00003761 | -2.59315644e-6 | 1.99908465 |

총 scalar \(\tau_0\)의 leading even \(q^2\)와 방향별 optical-depth quadrupole의 leading odd \(q\)을 확인했다. Native AX08의 photon-energy moment \(J_2=\sum N_{ki}E_iP_2(\mu_k)\)와는 **다른 정의**다. \(J_2\)의 예전 parity 계산은 SHA 맞춤 재사용만 했고 본 연구의 새 성과로 중복 청구하지 않았다.

## 독립 계산 및 반사실적 구별

기하학적 \(b_q(a)\)만 각 signed case에서 받고 ZERO \(n_e(t),\tau(t),t(a)\)를 고정한 계산을 수행했다. 이 **비자기일관적 frozen-source counterfactual**에서 \(O_{\tau_2}\)는 원래 coupled case의 값과 다음 범위로 일치했다: \(q=0.005\)에서 상대차이 8.37e-6~2.08e-5, \(q=0.01\)에서 3.35e-5~8.33e-5 (세 상대 적색편이 전체). 비율 근접성은 기하학적 redshift mapping의 효용을 지지하지만 실제 물리적 기여의 원인별 엄밀한 분할은 아니다.

별도의 FIRST-ORDER endpoint \(\tau_2\) 해석식과 실수치 odd 차분의 상대 차이는 \(q=0.005,0.01\), \(z_{\rm rel}=0.2,0.5,0.75\) 여섯 비교에서 5.72e-6~5.86e-4 이다. Frozen-source와 선형식 두 검사는 상호 독립적 결과를 요구하지만 원래 input histories는 공유하므로 독립 ODE 검증이 아니다.

## 알고리즘·정밀도·최적화·자원

- \(u=\ln a\)에서 \(b(u)\) 조각별 선형 보간; source \(t(u)\)와 \(n_e\)를 보간하여 observer 쪽부터 backward emission root를 58회 양분법으로 계산. Native signed prefix에서 \(\max|db/du|=0.009999512\) 수준이므로 \(2|db/du|<1\)이며 해당 구간별 interpolation redshift root가 모든 \(\mu_o\)에서 유일함을 확인했다.
- Angular Gauss-Legendre nodes 16,32,64,128; 최대 저장된 root \(|\delta\ln(1+z)|\) ≈5.55e-16. 64와 128 노드의 quadrupole 차이는 실제 검사의 크기 범위에서 약 1e-15 이하였으며, zero case quadrupole은 ~1e-16 크기다.
- 원래 저장된 full-resolution source 노드를 2~32 간격으로 추리는 별도 시험에서 q=+.01, z_rel=.5 optical-depth quadrupole의 **상대 재구성 변화**는 대략 9.87e-11~9.30e-9 수준. 이것은 단순 sampling/projection 민감도이지 source solver 전역 오차 한계가 아니다.
- Ubuntu에서 독립 stdlib math+bisect scalar root vs vectorized NumPy 128 방향, 7회 측정: scalar median 0.0181989s, vector median 0.00236746s, **7.6871x** speedup, 발광 \(u\) 차이 0 (표시 정밀도).
- 다섯 cached case × 3 targets × 4 angular grids: ThreadPool 1-worker median 0.241475s, 2-worker 0.209096s, 4-worker 0.210840s, 따라서 이 규모에서는 2 workers 최선 (약 1.155x vs 1). NumPy thread/process를 native model subagent라 부르지 않는다.
- Original source 5개 raw signed prefix와 이전 \(\tau\) cache SHA를 보존했고 \(b(a)\)만 별도 geometry-cache에 저장. 각 geometry cache는 parent manifest, raw history 및 source epoch SHA에 결박되며, 반복 실행 시 코드가 integrity 검사.
- 등방 이력, \(b={\rm const}\) 순수 좌표 rescaling, 축/횡 방향 power-law 해석해, reference scalar root 검산, \(\mu\to-\mu\) parity, monotonicity gate, source/scale identity 실패, 전 시간원인 조건을 회귀 테스트.
- 실제 long-history source re-simulation, collision closure 변경, full-reionization \(\bar z=20\to0\) 시뮬레이션 및 polarized CMB transfer는 수행하지 않았다.

## 실험의 정확한 요구조건

현재 결과는 "SOURCE_SCOPED_NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED"; published physical limit가 아니다. Native coupled ODE 전역오차, \(t(a)\), \(b(a)\)과 원자 반응률의 모형오차, piecewise interpolation과 source discretization의 오차를 분리해야 한다. 더 나아가 \(t_o\)를 오늘날로 확장할 때는 전체 실제 history와 Thomson collision polarization hierarchy가 필요하다.

재현에는 원래 사용자 Ubuntu의 source histories와 이전 parent NPZ cache가 필요하다. 기존 solver owner branch는 건드리지 않고 /tmp/BASS_HE_REI_ADAPTER_20261015 분리 worktree에서 작성했다.

Primary references: Fleury, Pitrou & Uzan, Phys. Rev. D 91, 043511 (2015), https://doi.org/10.1103/PhysRevD.91.043511 (Bianchi I null-geodesic propagation); Friedrich et al., MNRAS 421 2232 (2012), https://academic.oup.com/mnras/article/421/3/2232/1077406 (non-equilibrium H/He radiative transfer).

## 다음 하나의 과학적 검증

현 원본 scalar native solver owner와 충돌하지 않는 독립 minimal convergence experiment (ZERO, q=±0.005)에서 \(a(t),b(t),n_e(t)\)의 시간적/각도적 적분오차를 목적함수 \(\tau_0(z_{\rm rel}),\tau_2(z_{\rm rel})\)까지 전파한다. 기초 조건에서는 signed \(\tau_2\)와 derived linear test를 native accuracy/closure와 연결해야 한다. 먼저 short shared prefix나 reduced-volume pilot으로 convergence를 확인하고 프로덕션 전체 native 5-run 재실행은 요구하지 않는다.
