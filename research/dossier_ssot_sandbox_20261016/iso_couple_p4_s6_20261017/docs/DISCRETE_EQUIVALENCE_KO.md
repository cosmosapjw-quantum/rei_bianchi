# P4/S6: scalar trace 동일성과 결합된 이산 응답

## 정의와 전제

Metric (-,+,+,+), 고유시간 t[s], dimensionless a_i. ds²=-c²dt²+Σa_i²dx_i². 광자 보존 Killing 성분을 K_i=c p_i=a_i(t_b)E_b n_bi로 정의하면 E(t)²=ΣK_i²/a_i(t)²이다. E는 코드에서 eV, number는 reference-comoving m^-3, gas thermal은 J m^-3이며 EV_J=1.602176634e-19 J/eV를 한 번 적용한다.

대각 균질 기하, 비틸트 기체, 에너지만의 scalar cross section κ_j(t)=c n_j(t) σ_j(E(t))를 가정한다. Birth time, energy, geometry, current photon number가 같고 n_bi'=s_i n_bi, s_i∈{-1,+1}이면 모든 t에서 E'=E 및 κ_j'=κ_j다. 문턱 crossing time과 positive attenuation/heat/binding 기여도 같다. 이 부호 대칭은 임의 대각 a_i(t)에서 유효하지만 현재 Rust background adapter는 inherited constant-axisymmetric prescribed geometry로 제한한다.

기존 출생·원자 source와 단면적을 바꾸지 않는다. Ground-state Verner edges13.60/24.59/54.42eV와 D provider의 explicit threshold를 그대로 사용한다. Hydrogen binding energy 및 manufactured isotope energy difference를 photo-fit edge와 혼동하지 않는다.

## Computational form

각 cohort q와 각 threshold-split slab l에 대해 n_{l+1}=n_l exp(-κ_l Δt_l), A_{jl}=n_l[-expm1(-κ_lΔt_l)]κ_{jl}/κ_l이다. 동일한 scalar input에서 slab별 A_{jl}, heat_{jl}, photon energy, geometric work 및 surviving n을 재사용한다. κ=0 극한은 원본 photon_slab이 처리한다.

서로 다른 cohort를 합치거나 ray total을 먼저 합산하면 IEEE addition order가 달라질 수 있다. 구현은 원래 cohort 순서, slab 순서, species 순서로 **각 가산항**을 재생한다. Photon number까지 exact key에 포함하므로 서로 다른 weight로부터 linear scaling을 가정하지 않는다. 원래 방향 record는 그대로 유지되어 odd moment를 손실하지 않는다.

Cache lifetime은 한 gas-midpoint step이며 gas, source, κ provider 및 geometry가 바뀐 뒤 재사용하지 않는다. Key는13개 u64 exact bits이며 approximate hash matching을 하지 않는다. FIFO limit 부족은 재계산을 유도할 뿐 입력·오차허용치·광자수를 바꾸지 않는다.

## 결합계에 대한 귀납 논증

고정된 구현/실행환경과 위 signature 동치를 전제로, n번째 step의 전체 state가 두 경로에서 동일하다고 하자. Source birth, drift는 변경되지 않는다. 모든 scalar trace 재사용은 같은 값의 가산항을 원래 순서대로 전달하므로 photo event budget과 surviving photon bits가 같다. 변경하지 않은 deterministic gas step은 같은 photo-updated state를 받으므로 CI/RR/CX/CE/freefree/CMB 및 EOS 결과가 같다. 후속 drift 역시 같아 n+1 state가 같다.

따라서 이 정확한 이산 map 재사용에는 제거된 광자에 대한 새로운 Gronwall/adjoint error amplification bound가 필요하지 않다. 이는 원본 이산 map이 연속 물리의 참해라는 뜻이 아니며, arbitrary pruning의 nonlinear sensitivity를 인증한 것도 아니다. 실제 적용 gate는 전체 state/budget/cohort bit regression이다.

## 반례와 유효범위

Tilt가 있으면 E_gas=γE(1-β·n)이다. ±μ pair 차이는2γEβμ로 일반적으로0이 아니므로 cache symmetry를 사용할 수 없다. Off-diagonal metric은 n_i n_j cross term을 가질 수 있어 개별 component reflection을 동일하게 취급할 수 없다. Polarization/scattering 및 공간적으로 변하는 medium도 별도 대칭 증명이 필요하다.

같은 시작 에너지뿐 아니라 전체 trajectory scalar signature가 같아야 한다. 서로 다른 birth time의 광자를 동일하다고 합치지 않는다. 현재 storage O(N_t)와 전체 history propagation의 worst-case O(N_t²)는 바뀌지 않는다.

## Evidence and literature

Wolfram symbol calculation: 8 sign-reflection energy-squared differences all0; tilt difference2βEγμ. Independent Python closed form96points compares native Killing rays, max energy/direction difference2.220446049250313e-16. New Rust tests12 and inherited100 PASS, full540step pair bit comparison PASS, full thermochemistry and source fesc finite responses included.

Fleury, Pitrou & Uzan, Phys.Rev.D91,043511(2015), DOI10.1103/PhysRevD.91.043511, arXiv1410.8473v3, supports the diagonal Bianchi-I Killing-geodesic framework. The reflection-cache proof and this Rust implementation's verification are our direct derivation/measurement, not an attribution to that paper. SciSpace repository-index dates were not adopted as paper publication dates.
