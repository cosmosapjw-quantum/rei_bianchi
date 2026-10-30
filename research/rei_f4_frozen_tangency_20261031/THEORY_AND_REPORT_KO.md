# REI F4: 원본 BASS193 궤적에 대한 혼합 반응망 접선 정합성 및 화학에너지 포트

## 질문 및 원본

PR #298의 원본 source-inclusive ZIP `REI_F4_HYBRID_FJ_WEAK_THERMAL_20261031_FULL.zip` (26,674,534 bytes, SHA256 `012635501cc5d9717ae775e9482b351b239003aa6c7db4dd2035ffa4760b7f2d`)을 불변 source로 사용했다. 내부 BASS21 원본 193개 epoch 및 Python/Rust 비교 기록은 재사용하되 새로운 화학·우주론 IVP는 수행하지 않았다. 193시점의 상태 Y, 배경 T, H, n_b, proper t 및 F_BASS, F_hybrid, J_BASS, J_hybrid는 해당 ZIP에서 정직하게 읽는다.

## 정의/유도

별도 조건부 모델의 소스 결함을 ΔF_i(t_k)=F_i^hybrid[Y_BASS(t_k),t_k]-F_i^BASS[Y_BASS(t_k),t_k]로 정의한다. 동일한 Y_BASS(t)가 두 독립 F의 정확한 해가 되기 위한 필요조건은 모든 t에서 ΔF(t)=0이다. 새 주장은 이미 저장된 193점에서 ΔF가 0이 아니라는 관측이며, 다른 초기조건/배경의 hybrid 해 존재성을 배제하지 않는다.

원본 BASS21의 핵 중입자 수 A와 전하 q에 대해 AᵀΔF=0(보존), Δ\dot x_e=qᵀΔF다. 기존 hybrid에서 중성자 n→H1II+e+νbar 유입의 비어 있지 않은 Jacobian 1/878.4 s⁻¹은 그대로 보존한다. 국소 원본 비교 Δ\dot x_e와 누적 ∫Δ\dot x_e dt는 **고정된 저장 궤적상의 source exposure**이며, 실제 electron fraction 변화가 아니다.

REI 원본 문턱값 χ_H=13.598434599702 eV, χ_HeI=24.587389011 eV, χ_HeII=54.41776 eV를 사용하여 화학적 결합에너지 소스 차이(erg/cm³/s)를 직접 유도한다:

Δ\dot E_binding=(n_b/10^6)(eV→erg)[χ_H ΔF_HII+χ_HeI(ΔF_HeII+ΔF_HeIII)+χ_HeII ΔF_HeIII].

이는 source 변화에 의해 요구되는 binding energy port이다. **외부 복사와 escape 에너지 입력을 같게 유지한다는 counterfactual** 하에서 열원 보상 항은 Q_comp=−Δ\dot E_binding이고, monatomic thermal-bath의 온도 미분 변화는 Δ\dot T_formal=Q_comp/C_V,21−T Δ\dot n_e/n_thermal이다. 이는 closure-required formal term일 뿐 실제 열침적량·evolved temperature가 아니다.

Source clock x=ln(a/a_ini), dt/dx=1/H, n_b proper, H in s⁻¹, t in s. 원본 시간 샘플을 수치미분한 D_tY와 원래/혼합 반응률의 잔차를 비교한다. D_tY는 비균등 저장 간격으로부터 3점 gradient를 계산한 diagnostic이며 ODE 오차에 대한 rigorously converged certificate가 아니다.

## 실제 계산 결과 (193개 원본 상태)

- max |ΔF|/H = 1.2924275292610856 baryon⁻¹ per e-fold, 193/193 state nonzero.
- max |ΔF|=4.961566427478634×10⁻¹⁷ baryon⁻¹ s⁻¹.
- max |qᵀΔF|=5.18649697414562×10⁻¹⁷ baryon⁻¹ s⁻¹.
- Simpson ∫qᵀΔF dt=+0.22141551605625187 per baryon, frozen source exposure, NOT Δx_e.
- ∫ΔE_binding/n_b dt=+5.259618825169427×10⁻¹² erg/baryon, diagnostic, NOT actual deposited energy.
- max |ΔE_binding|=2.8135544090622418×10⁻³¹ erg cm⁻³ s⁻¹.
- max |Δ\dot T_formal|=3.565306466377509×10⁻¹² K/s; counterfactual, NOT observed temperature or predicted temperature derivative.
- max sampled-trajectory |D_tY−F_BASS|=9.178200029601721×10⁻¹⁹ baryon⁻¹ s⁻¹; hybrid counterpart 4.933703487221641×10⁻¹⁷.
- max |AᵀF_hybrid|=4.944886624114512×10⁻³² baryon⁻¹ s⁻¹; max |AᵀJ_hybrid|=1.6543612497579586×10⁻²⁴ s⁻¹.
- max |H_mid Δt/Δx−1|=3.893973292101727×10⁻⁵ (midpoint quadrature clock diagnostic).

193-row CSV, complete source residual NPZ, six original-state scientific plots in results/. Seven algebraic equivalences and hostile negative controls are automated in targeted tests; no original astrophysical input changed.

## 판정

같은 외부 H,T,UV,n_b clock에서 원본 BASS 궤적에 REI/Grackle H/He source를 대체하면 원본 저장 궤적과 접선 일치하지 않음을 수치로 보여준다. 그러나 dynamic hybrid solution이나 self-consistent radiation/electron/thermal state는 미계산이다. 이것은 정준 F4 closure를 의미하지 않는다. Working 33/88, Central 28/88, Physical Fast 4/7, F4 PARTIAL, L4 NOT_READY, Production HOLD, new_IVP=0, auto_next_node=false.

## 1차 문헌

Smith et al., “Grackle: a Chemistry and Cooling Library for Astrophysics,” MNRAS (2017), DOI:10.1093/mnras/stw3291, arXiv:1610.09591 (species chemistry/thermal source ownership). Norman et al., “Fully Coupled Simulation of Cosmic Reionization. I. Numerical Methods and Tests,” ApJS 216:16 (2015), DOI:10.1088/0067-0049/216/1/16 (radiation/chemistry/thermal coupling). 이 문헌들은 본 연구 결과 1.2924를 주장하지 않는다. 수치는 사용자 원본 BASS/REI 연구에서 계산했다.
