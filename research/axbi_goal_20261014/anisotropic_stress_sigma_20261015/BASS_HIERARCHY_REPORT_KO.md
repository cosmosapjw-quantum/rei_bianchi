# REI Σ–π_ab · BASS 원전 Boltzmann 다극의 실제 이식과 수치 연구

연구 시각: 2026-10-15 KST. 연결 기준 rei_bianchi Draft PR135 SHA 7b6b4bd0aa3ab9efabcb7d49744b431c0ecf2e78. 새 코드는 고정 생산 AX08/화학/광자 solver와 분리된 연구 worktree에만 있다. 과거 완료 이력, 기존 checkpoint, 원래 source config/clock은 변경하지 않았다. local Codex를 사용하지 않았다.

## 1. 원래 BASS 공식이 실제로 확인된 위치와 identity

1. BASS 저장소 ~/bass/bianchi/matter/hierarchy.py, SHA256 27f81acd681acc34537ad59ad2bec923d95c0adb7ac6d52413c4e3b2e0980aa6. 원전 Lewis–Challinor (astro-ph/0203507) 식 (10)–(12)의 무충돌 동차 PSTF kinetic hierarchy. ρ=J^(0), p=J^(1)/3, π_ab=J^(0)_ab; collisionless l=2,i=0 source = (2/15)[J^(2)−5J^(1)]σ_ab. Pseudocode가 아니라 이 모듈의 실제 J_moment와 hierarchy_rhs를 import해 RHS를 평가했다.
2. BASS ~/bass/bianchi/matter/freestream.py, SHA256 b03aeed2cfcdaa5baf45fdab626941905674e2385bc06d1173a4b8c39ebf8bb4: exact spatial Killing momentum f(q_i) and direct-momentum quadrature. BASS viscous_derived.py SHA256 48f39a2266272e20b5a1a26f6ffedc1813e300d2b1f00a24a415c7e6902413bf (massless 4H damping and -8/15 source).
3. htt_base/htt/bass/hierarchy/pstf_radiation.py SHA256 332da19ccd5a949ab712b29f3d0e8634bff1aa71f0385f26f952a922fd6d73f2: RadiationNormalization I0_to_rho_gamma=1, I2_to_pi_gamma=1, normalization and closure-promotion metadata.
4. BASS Dossier_II_Kinetic_Transport.pdf dated 2026-10-14 SHA256 8e4a20c228cb4f6760d258b9ecafb142423a7140698d45871b0151593feef075: homogeneous massive characteristic, normal-frame matter stress and source Q_r; the dossier distinguishes physical time t, normal length time s=ct, and conserves ∑_r Q^a_r=0 only when the complete event ensemble is included.
5. Independent source-seeded massless radiation BASS PR159: https://github.com/cosmosapjw-quantum/bass/pull/159. 기존 REI Einstein collisionless source PR135: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/135.
6. 사용자 REI 시나리오 SHA256 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696. 원시 재결합 결과를 전달하는 REI donor Git blob SHA1 1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4. Donor는 원래와 동일하게 opt-in 비활성, astrophysical ionizing photon 초기값도 재설정하지 않았다.

## 2. 물리적 변수와 정확한 Liouville 모멘트

Metric sign (-,+,+,+):

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,\quad
s=\dot b,\quad \sigma^i{}_j=\mathrm{diag}(-s,-s,2s),
\]
\[
\boxed{\Sigma=|\sigma|/H=\sqrt3|s|/H},\quad\epsilon_s=\operatorname{sgn}(s).
\]

Σ만으로 전단 방향이 복원되지 않으므로 orientation∈{-1,0,+1}은 별도의 동적 label이다. 과거 native code의 signed q_ref는 정확하게 이전 stress-free physical H constraint에 대응하는 compatibility adapter에서만 허용하고 새 실험 입력에서는 Σ와 orientation을 쓴다.

Radiation과 matter에 처음부터 독립적인 Boltzmann rank-2 multipole을 구성한다:

\[
W_r(\mu_*)=1+A_rP_2(\mu_*),\qquad
W_m(\mu_*)=1+A_mP_2(\mu_*),\qquad -1\le A_r,A_m\le2.
\]

두 W는 입자수 및 초기 에너지 ⟨W⟩=1을 지키는 **positive** angular source다. Initial quadrupole is no longer a post-hoc shear-generated defect:

\[
\Pi_{r,*}=\tfrac15 A_r\varepsilon_{r,*},\qquad
\Pi_{m,*}=\tfrac35 A_mp_{m,*};
\quad \pi^i{}_{j,A}=\mathrm{diag}(-\Pi_A/3,-\Pi_A/3,2\Pi_A/3).
\]

따라서 Σ_ref=0라도 \Pi_{r,*} 또는 \Pi_{m,*}가 nonzero라면 Einstein source가 새로운 전단을 생성한다.

Killing momentum 및 collisionless f preservation에서 정확한 무질량 source:

\[
R(\mu,b)=\sqrt{e^{2b}(1-\mu^2)+e^{-4b}\mu^2},
\quad
\varepsilon_r=\varepsilon_{r,*}e^{-4\eta}\int_0^1 W_rR\,d\mu,
\]
\[
\Pi_r=\varepsilon_{r,*}e^{-4\eta}
\int_0^1W_r\frac{e^{-4b}\mu^2-\frac12e^{2b}(1-\mu^2)}R\,d\mu.
\]

p_parallel/perpendicular positive-sector integrals use only 32 Gauss-Legendre nodes on the positive μ half of the original 64-node symmetric rule; angular weights precomputed and shared. Matter는 지정한 **비상대론적 Maxwellian kinetic radial limit**에서 p_*=(n_H+n_He+n_e)k_BT_*로 소유한다:

\[
p_{\perp,m}=p_*e^{-5\eta+2b}(1-A_m/5),\quad
p_{\parallel,m}=p_*e^{-5\eta-4b}(1+2A_m/5),
\]
\[
u_m=(2p_{\perp,m}+p_{\parallel,m})/2,\quad
\Pi_m=p_{\parallel,m}-p_{\perp,m}.
\]

정확한 방정식은 ∂_b ε_r=-2Π_r, ∂_b u_m=-2Π_m, radiation trace, shear Einstein, Hamiltonian, mean Raychaudhuri, positive distribution을 만족한다. Low-rank BASS STF correspondence: π_zz=2Π/3, Π=(3/2)J^(0)_{zz}; photon I2_to_pi=1.

Original BASS massless l=2 source가 -8ρ σ_ab/15이라는 것은 원본 소스 직접 실행으로 확인했다. 유질량은 l=2,i=0 source=(2/15)[J^(2)−5J^(1)]σ_ab이고 J^(1)=3p, J^(2)→0 비상대론 극한에서 -2p σ_ab, scalar Π̇_m≈−6ps다. 이는 사용한 exact cold matter angular source의 선형 한계와 일치한다. **유질량 radial hierarchy 전체를 시간적분했다고 주장하지 않는다.**

Small-anisotropy linear l=2 diagnostic-only expressions:

\[
\Pi_r^{(2)}=\varepsilon_{r,\mathrm{iso}}(A_r/5-8b/5),\qquad
\Pi_m^{(2)}=p_{m,\mathrm{iso}}(3A_m/5-6b).
\]

실제 Einstein ODE에는 단축된 식이 아니라 위의 **exact** 양의 분포 source를 넣는다. Linear model에서 빠진 A_r b, A_m b coupling과 l>=4 생성은 수치 오차로 취급하지 않는다. Polarized Thomson hierarchy와 collision Q_r source는 별도 물리 integration 의무로 보존한다.

## 3. 실제 source 코드 평가와 독립 유도

- BASS 직접 J_moment masses 0,1,4,20,100; l=2,i=0 hierarchy_rhs를 손으로 구성한 source tensor와 비교; 원소 단위 relative 계산 통과.
- m=0, A_r=.2; m/T=4, A_m=.25의 nontrivial anisotropic f0에 대해 original BASS full l2 RHS와 **독립적인 exact Vlasov finite-difference** 비교. Normalized residual 각각 7.00077860e-10과 6.517364997e-10. 계산 결과는 BASS_DIRECT_HIERARCHY_RECEIPT.json에 source file SHA, 수치값 및 limits와 함께 있음.
- Wolfram symbolic: <W>=1, <W P2>=A/5, ∂_b u_m+2Π_m=0, radiation expansion \varepsilon_r/\varepsilon_iso=1-(2A_r/5)b+(8/5+2A_r/7)b²+... . 첫 계수는 BASS quadrupole normalization과 정확하게 일치한다.

## 4. 실제 Einstein coupled 수치 실행과 결과

Reionization 시계 범위를 벗어나지 않고 zbar=20→4. 두 중성 가스 IC (REI original approximate vs source-original HyRec full donor) × 다섯 signed Σ cases (0, 양·음 small, 양·음 large) × radiation A_r∈{-0.2,0,0.2} × matter A_m∈{0,0.4}에서 **60개 독립 실행, 7,260개 상태 행**을 계산했다. 모든 initial distributions positive, photon/kinetic source 각각 stress tensor을 구성해 Einstein 전단을 구동했다. 과거 원본 astro MD14/BB50kK가 물리 source로 공급된 **native H/He reionization trajectory는 다시 돌리지 않았다**.

중요한 physical 판별:

| Σ_ref | A_r | A_m | zbar4 b | zbar4 Σ | 의미 |
|---:|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | 0 | isotropic control |
| 0 | +.2 | 0 | +8.41189056934e-5 | 1.02070322334e-4 | radiation initial J2가 shear 생성 |
| 0 | −.2 | 0 | −8.41234909374e-5 | 1.02082740895e-4 | opposite signed branch |
| 0 | 0 | +.4 | +6.11483265e-15 | 5.314737959e-15 | nonrel matter seed alone |
| 0 | +.2 | +.4 | +8.41189056995e-5 | 1.02070322339e-4 | independently seeded r+m |

이 물리 조건은 기존 BASS PR159의 A_r=+.2, Σ_ref=0, A_m=0 결과 (b≈8.41189e-5, s/H≈5.89303e-5)와 명시적으로 비교 PASS; 이번 계산 s/H=5.89303280756e-5. 이번 연구의 원래 과제는 이 독립 원시 quadrupole 예제를 radiation+massive matter 복합 stress 및 BASS rank-2 source와 연결해 REI로 전달하는 것이다.

## 5. 실제 실행·수치 수렴·최적화

New source-specific Python unit tests: 15 PASS, 기존 PR135 science tests 별도 실행 예정. 새 local independent source check passes in its own actual invocation. Five cases GL32/64/128 and tighter DOP853 step/rtol/atol: final Sigma or b GL64 vs GL128 deviations <=2.4e-17; this is **local numerical method consistency**, not absolute observational error. 60 cases scalar serial vs 2-process source-separated run finished and produced identical end \Sigma/b within threshold. Median from one run: 2.2767236769s serial sum, 1.2134097189s two-worker wall, speedup **1.8763x**, not native REI physical solver performance. For 8192 initial-seeded b angular tasks GL64: source-weighted NumPy batch speedup **43.7073x** vs scalar reference, maximum absolute difference 2.22044604925e-16; within 1024×32 memory-bounded chunks, not the full Boltzmann collision operator.

Reproducible sources: BASS_HIERARCHY_CAMPAIGN.json, BASS_HIERARCHY_SIGMA_PI_HISTORY.csv, BASS_HIERARCHY_ENDPOINTS.csv, BASS_DIRECT_HIERARCHY_RECEIPT.json, BASS_CONVERGENCE.json, 5 PNG figures, test_bass_hierarchy_transport.py and scripts. All original source/manifests preserved by SHA; no unverified constant was substituted.

## 6. Scientific claim and remaining real obligations

**DERIVED/LITERATURE SUPPORTED**: moment convention ρ, p, J2, initial shear source, PSTF projection, collisionless kinetic angular evolution and component energy conservation. Original actual BASS code, source PDF/dossier, recent BASS PR159 provide lineage.

**NUMERICALLY CHECKED/LOCAL IMPLEMENTATION VERIFIED**: source direct massless and massive l2 RHS, actual 60 distinct Einstein+kinetic initial-value trajectories, sigma sign, finite mass source limit, source file byte lock, limited convergences and performance. The linearly reduced l2 model is **diagnostic**; exact collisionless f is the numerical closure used in Einstein.

**NOT YET PERFORMED**: dynamic finite-mass i-direction radial hierarchy, full polarized Thomson collision tensor and redistribution, actual H/He inelastic chemical source Q_r and exchanged momentum, viscosity/relaxation times from source collision physics, replacing effective Omega_r with disjoint CMB/neutrino/star photons when separate kinetic sectors are resolved, genuine native REI complete H/He/RT Einstein recoupling and AX11 absolute convergence. No proper primordial nonzero Sigma recombination or observed CMB spectrum is claimed.

Next concrete scope: take original BASS photon I/E/B and massive J_{A_l}^{(i)} source, import LRS l2/l4 with exact collision moments, co-evolve species energy and momentum; enforce sum Q_r=0 in Dossier II physical-time convention. Only then promote to a new native Einstein+REI solver branch and fresh source-stamped initial state. Preserve historical native checkpoints as immutable.
