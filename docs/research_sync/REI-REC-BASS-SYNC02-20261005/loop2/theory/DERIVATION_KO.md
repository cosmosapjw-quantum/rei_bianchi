# REC–REI–BASS 팽창 FLRW 연결 계약

이 루프는 순수 수소, 한 온도, collapsed Peebles 모형의 **지정된 FLRW 배경 위 수치 benchmark**다. 초기 이온화율 0.8은 지정한 초기조건이고 Saha 평형이나 관측 적합값이 아니다. 별도로 진행되는 FT03/F05, EoR 광원 모형, retained n=2의 강성 이력, 일반 Bianchi 진화를 대체하지 않는다.

## 원천과 밀도

실제 `rec_microphysics::hydrogen_peebles`의 `HYREC2_TLA_2020_PEEBLES_FUDGE1` 원천을 새 REI 소비자에서 호출한다. 매 stage에 H, proper nH, T와 현재 x를 넣는다. 표준 collapsed source의 ground fraction은 1−x이며 retained x2를 넣지 않는다. x는 분율이므로 `−3Hx` 항을 추가하지 않는다. proper 밀도 nH=nH0 a⁻³의 희석은 배경이 한 번 소유한다.

모형 식은 dx/dt=−C[nH αB x²−βP(1−x) exp(−E21/kBT)]다. C=(Λ+3Rα)/(Λ+3Rα+βP), Rα∝H/[nH(1−x)]다. cm⁻³↔m⁻³ 변환을 소비자 입력 경계에서 명시하며 원천의 반올림 상수를 보존한다. 이 식의 채택은 source profile 선택이고 원자율의 오차 인증을 새로 주장하지 않는다.

## 지정된 matter-only FLRW 배경

w=1+z, w0=1201, K=Href/w0^(3/2), H=K w^(3/2), a=1/w를 쓴다. Href=5×10⁻¹⁴ s⁻¹, nH0=0.2 m⁻³, T0=2.7255 K다. 수치 적분 구간은 z=1200에서1000까지며 dx/dz=−(dx/dt)/(wH)다.

시작점을 0으로 둔 clock은 다음과 같이 정확히 적분된다.

* t(z)=2/(3K)[w^(−3/2)−w0^(−3/2)] [s]
* η(z)=2/K[w^(−1/2)−w0^(−1/2)] [s]
* χ(z)=cη(z) [m]

전하 밀도는 ne=nH x다. 실제 Peebles trajectory의 midpoint x와 같은 midpoint nH를 HHe snapshot의 순수-H 부분에 담아 기존 BASS density validator를 사용한다. 이 경계에서 HHe thermal state는 지정된 T로부터 u=(3/2)nH(1+x)kBT로 조립한다. HHe/FT03 RHS를 호출하지 않으므로 Peebles 궤적을 Case-A 또는 FT03 궤적으로 재표기하지 않는다.

## Thomson 관측량과 시간좌표

비기울어진 FLRW에서 D=1이고 q_t=cσT ne다. 일반 frame의 D를 처리하는 기존 BASS 함수는 보존한다. 각 cell의 midpoint q_t를 해당 normal-time interval에 상수로 유지한다. 이것이 여기서 검증하는 discrete opacity surrogate다.

각 cell에 a_eff=Δt/Δη를 공급하면 q_η=a_eff q_t, q_χ=a_eff q_t/c이고 q_tΔt=q_ηΔη=q_χΔχ다. a_eff는 단순 midpoint a와 구분된다. 이 변환은 같은 discrete measure의 정확한 재표현이며 실제 연속 q(t)가 cell 안에서 상수라는 물리적 주장은 아니다.

τ_i=τ_tail+Σ(j≥i)q_jΔt_j, S_i=exp(−τ_i), P_i=S_(i+1)[−expm1(−q_iΔt_i)]를 기존 BASS 구현으로 계산한다. 따라서 ΣP_i+S_0=exp(−τ_tail). 여기서 τ_tail=0.2는 지정한 외부 경계조건이며 z<1000의 재이온화 광학깊이를 계산한 값이 아니다.

## 독립 검산과 오차 분리

native RK4와 별도로 쓴 동일 source-profile 식을 SciPy DOP853로 적분한다. 이 독립성은 코드와 적분기에 있으며 원천 계수는 의도적으로 공유한다. x 적분 오차, opacity midpoint quadrature 오차, 동일 셀의 clock 변환 오차, exp/누적합 roundoff를 따로 보고한다. N=400/800/1600의 관측된 refinement는 세 유한 해상도에서의 증거이며 균일 continuum enclosure가 아니다.

추가 analytic fixture에서는 x를 상수로 고정해 Δτ=(2cσT nH0 x/3K)[w_start^(3/2)−w_end^(3/2)]와 비교한다. 이는 배경 희석·clock·적분을 검증하고 화학해를 검증하지 않는다.

Cold-Thomson coefficient의 수치 조립과 probability 계산만 이 루프의 산란 claim에 포함한다. finite-T/KN, 광자 spectrum/tail, 편광 collision generator, full BASS 실행과 일반 Bianchi 및 EoR 예측은 별도 연구 gate로 남는다.
