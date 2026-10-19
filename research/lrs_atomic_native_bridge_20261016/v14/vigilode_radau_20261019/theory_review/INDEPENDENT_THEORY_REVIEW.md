# 독립 native Radau 결합 이론 검토

검토자: /root/drive_v15_intake — 실제 독립 subagent. 기존 native 소유 함수와 pinned VigilODE를 read-only로 읽고 유도했다. 새 adapter diff·실행 raw의 심사는 아직 하지 않았다.

**판정: 계약의 결합 방정식과 affine stage-ledger 구성은 아래 조건에서 일관된다. 반환 endpoint 잔차를 포함해야 하며, L-stability를 stage 양수성으로 해석할 수 없다.** 이 문서는 이론 검토이지 native 실행 admission이 아니다. source hash는 SOURCE_READ_RECEIPT.json, 실제 검산은 ALGEBRA_CHECK.json과 WOLFRAM_STAGE_POSITIVITY.json에 있다.

## 1. Native 단위와 photon RHS

CovariantTransport::prepare/prepare_legacy_serial은 각 stage의 PhotonState에서 양의 closure quadrature를 만든다. node.number는 **total-H당 photon 수**다. ray_geometry의 scale을 \(r_j\)라 하면 node의 proper energy는
\[
 \epsilon_\ell=r_jq_\ell,\qquad
 E_\gamma=\sum_c r_{j(c)}U_c^{\rm ref}.
\]
등방 기하에서 \(r_j=a_{\rm ref}/a\)다. 일반 ray에서 단순히 \(q/a\)로 대체하지 않는다. inventory가 이 scale을 실제 사용한다. injection은 이미 angular weight를 count에 반영하므로 RHS에서 이를 한 번 더 곱하지 않는다.

\[
 n_{\rm abs}=(n_H(1-x),\,n_{\rm He}(1-y-z),\,n_{\rm He}y),\quad
 \kappa_{\ell s}=c_{\rm physical}n_{{\rm abs},s}\sigma_s(\epsilon_\ell).
\]
Native constants의 \(c=2.99792458\,10^{10}\ {\rm cm\,s^{-1}}\), density \({\rm cm^{-3}}\), cross section \({\rm cm^2}\)로 \(\kappa\)는 \({\rm s^{-1}}\)다. 같은 nodes로
\[
 P_s=\sum_\ell\kappa_{\ell s}n_\ell,\quad
 \dot N_c=-\sum_{\ell\in c,s}\kappa_{\ell s}n_\ell,\quad
 \dot U_c^{\rm ref}=-\sum_{\ell\in c,s}q_\ell\kappa_{\ell s}n_\ell .
\]
\(P_s\)는 events/H/s다. point provider에 들어갈 값은
\[
 \Gamma_s=c\,n_H\sum_\ell\sigma_s(\epsilon_\ell)n_\ell,\quad
 {\cal H}_s=c\,n_H\sum_\ell\sigma_s(\epsilon_\ell)n_\ell
             (\epsilon_\ell-\chi_s)\,{\tt ev\_erg}.
\]
각각 absorber당 \({\rm s^{-1}}\), erg/absorber/s다. 따라서 native photo_events_cm3_s/\(n_H\)=\(P_s\)이며
\[
 Q_{\rm heat}=\sum_{\ell s}\kappa_{\ell s}n_\ell(\epsilon_\ell-\chi_s),\quad
 -\dot E_\gamma=Q_{\rm heat}+\sum_s\chi_s P_s .
\]

Binding/excess에는 HHeModel이 소유한
\(\chi=(13.598434599702,24.587389011,54.41776)\) eV를 사용한다. FIT_THRESHOLDS_EV의 \((13.60,24.59,54.42)\)는 spectral partition/fitting 경계이고 이 binding 상수의 대체물이 아니다. 기존 AtomicProvider/Grackle 계수는 그대로 둔다. controlled_fixture에서는 상수와 EOS만 재사용하며 synthetic rate/sigma를 새 물리 RHS에 넣지 않는다.

Native node moment-fit의 roundoff는 closure 진단으로 남긴다. 같은 nodes의 독립 photo/event/energy 합은 finite quadrature 순간 회계를 검산할 수 있지만, continuum spectrum의 독립 정확도 증명이 아니다.

## 2. 전자·binding·열·escape 소유권

\(Y=n_{\rm He}/n_H=0.2454/[4(1-0.2454)]=1227/15092\)다. \(P_s,C_s,R_s,D_{\rm DR}\)는 모두 total-H당 순간 사건율로 정의한다. Native source에서 DR은 HeII→HeI capture다.

\[
 \dot x=P_H+C_H-R_H ,
\]
\[
 Y\dot y=P_{\rm HeI}+C_{\rm HeI}-R_{\rm HeI}-D_{\rm DR}
       -(P_{\rm HeII}+C_{\rm HeII}-R_{\rm HeII}),\quad
 Y\dot z=P_{\rm HeII}+C_{\rm HeII}-R_{\rm HeII}.
\]
따라서
\[
 e=x+Y(y+2z),\quad
 \dot e=\sum_s(P_s+C_s-R_s)-D_{\rm DR},
\]
\[
 B=\chi_Hx+Y[\chi_{\rm HeI}y+(\chi_{\rm HeI}+\chi_{\rm HeII})z],
\quad
 \dot B=\sum_s\chi_s(P_s+C_s-R_s)-\chi_{\rm HeI}D_{\rm DR}.
\]

IgmGasState의 저장 에너지는 erg/H이므로 adapter의 eV/H RHS는 w_dt_erg_per_h_s/ev_erg다. 이미 /H인 w_dt를 \(n_H\)로 다시 나누지 않는다. 반면 point event율은 cm^-3/s, cooling은 erg/cm^3/s라 각각 \(n_H\), \(n_H\,{\tt ev\_erg}\)로 나눈다.

\(Q_{\rm rad}\)를 native RR kinetic + DR kinetic + CE 세 항 + FF의 합이라고 쓰면 igm_point_rhs는
\[
 \dot w=Q_{\rm heat}-\sum_s\chi_s C_s-Q_{\rm rad}
          +Q_{\rm CMB}-W_{\rm gas},
\]
\[
 \dot E_{\rm esc}=\sum_s\chi_sR_s+\chi_{\rm HeI}D_{\rm DR}+Q_{\rm rad}
\]
를 소유한다. CI는 thermal→binding 전달이다. RR/DR의 kinetic cooling과 capture binding은 다른 항이다. CE/FF는 escape에 포함되므로 energy ledger에 이들을 독립 total loss로 다시 더하면 중복이다. CE의 밀도 prefactor도 native 코드의 세 서로 다른 표현을 그대로 유지한다.

CMB는 INTO gas가 양인 signed 값이다. \(T>T_{\rm CMB}\)이면 음수다. CI floor/CE cap/excluded-DR 진단은 기존 rate 소유권의 설명값이며 총 사건이나 cooling에 추가하는 별도 반응이 아니다.

이로부터
\[
 \dot w+\dot B+\dot E_{\rm esc}+W_{\rm gas}-Q_{\rm CMB}
       =Q_{\rm heat}+\sum_s\chi_sP_s,
\]
\[
 \frac{d}{dt}(E_\gamma+w+B)+\dot E_{\rm esc}
       +W_{\rm gas}-Q_{\rm CMB}=0
\]
를 얻는다. 정확 Fraction 계수 검산에서 photon number, electron, binding, total-energy의 각 독립 사건계수 잔차가 모두 0이었다. 제조 이력이나 새 시험 수로 세지 않는다.

## 3. Affine 좌표와 공통 stage ledger

폭이 양인 occupied cell에 대해 frozen \(S>0\), \(\Delta q=q_R-q_L>0\)를 정하고
\[
 u=N/S,\quad v=(U^{\rm ref}-q_LN)/(\Delta q S),\qquad
 N=Su,\quad U^{\rm ref}=S(q_Lu+\Delta q v).
\]
허용 cone은 \(u\ge0,\ 0\le v\le u\)다. Offset RHS는 차감 \(\dot U-q_L\dot N\)을 복원하지 말고
\[
 \dot v=-\frac{\sum_{\ell,s}(q_\ell-q_L)\kappa_{\ell s}n_\ell}
                       {\Delta q S}
\]
를 직접 더한다. Number와 offset 사이의 이 lower-triangular affine decoder를 에너지 residual에도 그대로 적용한다. 두 physical moment를 독립 diagonal scales로 오인하면 안 된다.

Point support는 \(U^{\rm ref}=q_*N\)이므로 number 하나만 둔다. Initially empty cell은 source-free segment에서 정확히 empty다. 새 GL2 birth 뒤에는 occupied set/support/layout/scales를 새 segment에 다시 만든다. 첫 birth 이전 gas-only 4변수 layout을 macrostep 전체에 재사용할 수 없다. Positive occupied cell이 underflow로 정확 0이 되면서 support가 남으면 native empty-support gate가 거절한다. 이를 몰래 floor/clip으로 숨기지 않는다.

각 RHS·FD perturbation은 현재 photon moments를 decode하고 다시 prepare해야 한다. 초기 PreparedAbsorption의 nodes를 photon stage/FD 전체에 고정하면 contract의 fully coupled reconstructed-moment 방정식이 아니다. Fixed geometry와 fixed support는 fixed photon reconstruction을 뜻하지 않는다.

일반 decoder를 \(Z=Z_*+\mathcal D\theta\)라 쓰자. Point/empty 축 제거 때문에 \(\mathcal D\)가 직사각형일 수도 있다. 핵심은 physical subspace에서 \(F(Z)=\mathcal D f(\theta)\)인 것이다. \(\mathcal D\), gas thermal scale, geometry의 ray-energy coefficients는 chemical step 안에서 고정한다.

OdeProblem::new의 mass_matrix는 None 또는 identity여야 아래 식을 그대로 쓸 수 있다. Library kernel은 일반적으로 mass*K−h*f를 푼다. 여기서는 affine 좌표 RHS에 이미 scaling을 적용했으므로 mass를 다시 scale 행렬로 넣지 않는다.

Pinned Radau의 반환 stage_increments는 \(K_i\), stage는
\[
 \Theta_i=\theta_0+\sum_j a_{ij}K_j,\qquad
 r_i=K_i-hf(\Theta_i).
\]
K는 stage displacement \(Z_i-Z_0\)가 아니다. Ledger unknown을 Newton 차원에 추가할 필요는 없지만, \(\Theta_i\)의 native RHS를 실제 다시 평가해 **같은 accepted \(h,b_i\)**로 모든 ledger를 누적해야 한다. Stiffly accurate 마지막 stage의 RHS만으로 누적하면 다른 quadrature다.

\(I=LZ+J\), \(\dot J=g\), \(\eta_i=L\mathcal Df_i+g_i\), 반환 endpoint defect
\[
 \rho=\theta_{\rm new}-\theta_0-\sum_i b_iK_i
\]
를 정의하면 실제 대수식은
\[
 \boxed{\Delta I=L\mathcal D\rho
 +\sum_i b_iL\mathcal D(K_i-hf_i)+h\sum_i b_i\eta_i.}
\]
Root의 식은 \(\rho=0\)에서 맞다. 실제 binary64 출력에서는 decoder·weighted sums·invariant evaluation의 floating error도 별도로 남긴다. 작은 WRMS만으로 각 physical ledger 오차가 작다고 판단하지 않고 maximum scaled component residual과 \(L\mathcal D r_i\)를 함께 기록한다. 이 항등식은 endpoint 적분 정확도 증명이 아니다.

## 4. GL2 source와 geometry clock

기존 tentative_ssprk2는
\[
 a_m=\sqrt{a_{\rm old}a_{\rm to}},\quad
 \Delta t={\log1p[(a_{\rm to}-a_{\rm old})/a_{\rm old}]\over H(a_m)}
\]
를 실제 사용하고 geometry_map→chemical→geometry_map을 수행한다. 이는 기존 segment의 시간 근사이며 exact cosmological proper-time integral이라고 주장하지 않는다. 가까운 endpoint에서 이미 수정된 log1p clock을 재사용하고, 보고서에는 실제 받아 사용한 dt를 넣는다.

GL2 birth는 \(a_b=a_0\exp(c_b\Delta\ln a)\)의 엄격히 증가하는 실제 endpoint에서 멈추고
\[
 \Delta t_b^{\rm src}=\Delta\ln a\,w_b/H(a_b)
\]
로 그 geometry와 \(z_{\rm cosm}=1/a_b-1\)에서 native inject를 호출한다. Radau stage는 source jump를 가로지르지 않는다.

Chemical call은 AxbiProvider.point(..., mean_h=0, ...)다. Geometry map이 이미 \(w\propto a^{-2}\)와 thermal_work, ray inventory 차이와 photon_work를 기록하므로 microphysical h에 H를 다시 넣으면 expansion work가 중복된다. Source N/U는 native inject의 실제 반환량을 기록한다. inactive_hi_split=false인 현재 계약은 passive-boundary coverage를 갖지 않는다.

MD14 dt_seed=1e16 s는 초기 photon packet을 만드는 source 적분 weight다. 그 시간을 native gas·cosmology가 실제 진화했다는 뜻이 아니다. Source-on/seeded-disabled 각 history와 이 제작기를 분리한다.

## 5. Radau의 positivity 및 FD 제한

Pinned radau_iia3_tableau는 **3-stage, formal order5**의 IIA다. Negative tableau entries가 있어 SSPRK2의 convex-FE 증명을 이식할 수 없다. Chemical Radau의 formal order5도 outer geometry/source wrapper의 전체5차를 뜻하지 않는다.

Scalar absorption \(y'=-ky\), \(\tau=hk\)의 실제 tableau를 대입하면
\[
 {Y_2\over y_0}
 =\frac{6[50+(10-5\sqrt6)\tau+(1-\sqrt6)\tau^2]}
        {5(60+36\tau+9\tau^2+\tau^3)},
\]
\[
 {y_{\rm new}\over y_0}
 =\frac{3(20-8\tau+\tau^2)}{60+36\tau+9\tau^2+\tau^3}.
\]
Endpoint는 모든 \(\tau>0\)에서 \(0<R(-\tau)<1\)인데 두 번째 stage는
\[
 \tau>5.148925653766939956\ldots
\]
에서 음수다. \(\tau=10\)의 stages는
\((0.3193569628021431,-0.0607362731469707,0.0517241379310345)y_0\).
실제 Wolfram evaluator와 Decimal closed-form 계산이 일치했다. 이 scalar 값은 새 native run이 아니며 nonlinear coupled system의 보편 CFL 수치도 아니다.

따라서 모든 native trial/converged stage가 양수여야 하는 계약에서는 이 scalar step도 받아들일 수 없다. 이를 Newton tolerance 완화나 clipping으로 해결할 수 없다. Native 실험의 large-optical-depth 실패가 이 조건인지, 유효한 stage 해가 있지만 Newton 경로가 domain 밖으로 나간 것인지 구별해야 한다.

Pinned nonlinear.rs는 trial residual callback의 Err를 받으면 즉시 반환한다. 유효한 residual이 나왔으나 norm이 감소하지 않는 경우의 backtracking과 다르다. Negative trial/domain failure를 보존하고 실패 후보의 state/physical ledgers를 commit하지 않되 FD·trial·stage replay의 실제 호출 비용과 attempt를 기록한다.

FD에서도 \(0\le v\le u\), \(0\le x\le1\), \(y,z\ge0,\ y+z\le1\), \(w>0\), EOS의 strict [1,1e6] K를 매번 만족해야 한다. 한쪽 perturbation이 domain 밖일 때만 다른 쪽을 시도한다. Resource cap나 다른 failure를 domain rejection으로 바꾸지 않는다.

One-sided 방향이 항상 존재하는 것도 아니다. 예를 들어 \(x=0,T=1\) K이고 w를 고정하면 x−ε는 음수, x+ε는 입자수 증가로 \(T=(1+Y)/(1+Y+\epsilon)<1\) K가 되어 둘 다 native domain 밖이다. 이 경계에서 zero Jacobian column이나 clipping은 정당한 대체가 아니다. 현재 15,000 K 내부 초기값이 이 실패를 실제 보였다는 뜻은 아니다.

## 6. Admission 경계

이론상 필요한 구현 조건은 명확하다: current-stage 재구성, native proper 단위, 공통 stage-ledger weights, frozen affine decoder, endpoint residual 포함, 모든 native domain gate, source jump 뒤 layout 갱신, geometry work 단일 소유권이다.

이 agent는 새 adapter를 작성·수정하지 않았고 native binary를 실행하지 않았다. 다음 diff/raw 심사는 실제 source+binary SHA, command/exit, endpoint/stage rows, independent eta와 residual identity를 읽은 뒤 수행한다. 보존 또는 residual 합의만으로 source-on 전체2차·uniform stiff·fullEoR·CaseB·signed Bianchi를 승격하지 않는다.

### 읽은 1차 근거

- 기존 rei native: axbi_covariant_transport.rs의 ray_geometry/inventory/inject/prepare/validate_state/cell_quadrature, igm_state.rs의 EOS/energy adapters, igm_thermal.rs의 igm_point_rhs, axbi_rates.rs의 provider domain, axbi_driver.rs의 binding/total_energy/geometry_map, axbi_ssprk_driver.rs의 actual birth/clock.
- Pinned VigilODE 8a8bd409b1d96c7b7421f496d229e119fd3d284e: rodas5p-integrators/src/radau.rs와 nonlinear.rs. API 행동은 이 실제 source 범위다.
- Stoichiometry/affine-ledger 유도는 본 검토자의 독립 유도다. Root의 별도 Wolfram 검산 결과를 이 agent의 검산으로 재명명하지 않았다.
