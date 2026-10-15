# REI × BASS 유질량 radial hierarchy와 gamma/neutrino Einstein–Thomson 결합

2026-10-15 KST. 실제 Ubuntu 로컬 유도·코딩·테스트·실행. 출발점: REI PR137 HEAD 5d41df647c4fd624d8a1b574f67fdd0b82ff5102. 원본 공급원: BASS PR160 HEAD 9e50f936f3289cb0c7c8127772cf9fb8d172d7a8; sigma_matter.py SHA256 1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790. 물리적으로 다른 원본 REI production checkpoint와 PR137 upstream 수정 없음.

## 1. 원래 BASS hierarchy의 구성적 이식

Metric signature (-,+,+,+) and LRS axes: ds²=-c²dt²+a² exp(-2b)(dx²+dy²)+a² exp(4b)dz², s=db/dt, shear eigenvalues (-s,-s,2s). 사용자 정의 Σ=sqrt(3)|s|/H, orientation=sign(s) 별도 보존.

Lewis–Challinor (2002), 실제 BASS original hierarchy.py의 정의는 ρ=J^(0), p=J^(1)/3, π_ab=J_ab^(0). Nonzero finite mass이면 속도가중 radial index i의 다극이 다르다. Original BASS PR160의 96개 Fermi–Dirac radial Gauss node와 축대칭 구적에 대응하는 실제 기능을 이번 REI 모듈에 독립 구현하고, 원본 BASS160 MassiveMoments.evaluate 및 BASS hierarchy.J_moment / hierarchy_rhs에 대해 직접 비교했다.

x=ln(a/a_ref), r=exp(-x), dimensionless mass µ=m/(k_B T_ref), source direction ξ=cosθ_*, and W_m=1+A_m P₂(ξ), -1≤A_m≤2. Define

R²=exp(2b)(1-ξ²)+exp(-4b)ξ²,
E=sqrt(µ²+r²q²R²), v²=1-µ²/E²,
ξ_phys²=exp(-4b)ξ²/R²,

with positive source measure dν = r³ q² f_FD(q) dq dξ W_m(ξ)/(2 N_ref), N_ref = integral q² f_FD(q) sqrt(µ²+q²)dq. Velocity-weighted scalar moments:

J0_i = integral dν E (v²)^i,
A2_i = integral dν E (v²)^(1+i) P₂(ξ_phys),
A4_i = integral dν E (v²)^(2+i) P₄(ξ_phys).

Tensor normalization: J_ab^(i)=A2_i STF(z_a z_b), J_zz^(i)=2 A2_i/3, J_zzzz^(i)=8 A4_i/35. Pressure p_m=F_m J0_1/3 and difference Δp_m = F_m A2_0. The original REI PR137 Pi_matter field convention is tensor amplitude π_s=Δp_m/3, π^i_j=diag(-π_s,-π_s,2π_s), while our earlier PR135 prose used Π=p_parallel-p_perp. The factor of three must not be dropped:

dot s+3Hs = (8πG/c²) ∑ π_s = (8πG/(3c²))∑Δp.

Matter energy coefficient F_m=ρ_crit,0 Ω_m f_m/a_ref³ is taken strictly from an original nonbaryonic Ω_m fraction, and original pressureless dust becomes (1-f_m)Ω_m/a³. The frozen source Ω_b remains in dust. This avoids doubling the mass energy. The effective massless ν in the original Ω_r and the massive model are declared distinct test populations, not a neutrino mass inference.

## 2. Exact LRS reduction of original BASS Eq.12 and active hierarchy

Wolfram analytic STF(z^4):σ contraction returned (36/35)s STF(z²) exactly. With physical time t and signed shear s, the original mass-dependent hierarchy reduces to

dot J0_i = -H[(3+2i)J0_i+(1-2i)J0_(i+1)] +2s[-2i A2_(i-1)+(2i-1)A2_i],

dot A2_i = -H[(5+2i)A2_i-(1+2i)A2_(i+1)]
           -(2s/7)[(7+4i)A2_i-(2+4i)A2_(i+1)]
           +(36s/35)[-2i A4_(i-1)+(1+2i)A4_i]
           +(2s/5)[(1+2i)J0_(i+2)-(5+2i)J0_(i+1)].

For i=0 coefficients of i-1 vanish. The time-evolved numerical state is J0_i and A2_i for i=0..2. The missing i>2 / l=4 moments are supplied by exact BASS source-pinned Killing-momentum quadrature each RHS evaluation, NOT a silent zero truncation. This is a source-assisted and non-autonomous high-index closure, not a fully autonomous infinite kinetic hierarchy. Separate exact-source gravity owner remains available as control. The DEFAULT Einstein Hamiltonian and shear now use the time-INTEGRATED J0_0,J0_1,A2_0 as gravitational energy, pressure and anisotropic stress, rather than an inert observer diagnostic.

Required exact energy identity: dJ0_0/dx = -3(J0_0+J0_1/3)-2(s/H)A2_0. Raychaudhuri, positive momentum pressure cone |A2_0|≤J0_1, baryon Ω_m budget, and gamma/nu number integrals are implemented as checks. The radiation gamma/nu Boltzmann hierarchy (L=8 nominal) and real saved AX08 HHe electron-density Thomson source from PR137 are retained without modification. Matter collisionless, gamma receives elastic unpolarized E2=0 Thomson angular damping; neutrinos do not directly Thomson scatter.

## 3. Actual science results

Seven actual Einstein+radiation+massive hierarchy DOP853 ODE runs, mean redshift 20→4, 161 sample states each, total 1,127 rows.

At initial Σ_ref=0, κ_gamma=κ_masslessnu=.2, massive energy fraction f_m=.1, m/(k_B T_ref)=30, the final Σ at zbar4 is:
- No massive: 1.014917009501816×10^-4.
- Massive seed A_m=+.5, actual frozen-HHe Thomson: 1.3032405716097782×10^-4.
- Massive seed A_m=-.5, same Thomson: 7.273826815908597×10^-5.
- Massive A_m=+.5 without Thomson: 1.309027040671767×10^-4.
- Colder mass parameter m/T_ref=300, A_m=+.5: 1.0178380778141509×10^-4.
- Σ_ref=.01731964211523 with signed orientation ±: final Σ+=.00211080208586, Σ-=.0018500104308.
Positive massive case final tensor-amplitude stress π_s,m=+8.116831288375678×10^-14 J/m³.

Strict independent original BASS160 collisionless full radiation limit was RECOMPUTED with identical matter fraction, mass, seed amplitudes, and photon/neutrino equal κ with gamma scattering off: endpoint b and Σ differ from actual new **hierarchy gravity owner** by approximately 1e-14–3e-14; massive stress relative difference ~1e-9 at finite ODE tolerances. This verifies the source-dependent shared physical limit, not new experimental observational evidence.

The source original REI HHe ne(a) has exact recorded 312238-row history SHA256 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f; its positive C2 interpolant was validated upstream with max relative source approximation ~1.9755×10^-4. This source uncertainty is separate from the numerical ODE error and from missing two-way chemistry feedback. Its chemistry was NOT recalculated with changed geometry.

## 4. Numerical and implementation verification

32 scoped local tests PASS including original BASS160 source MassiveMoments original-Copy parity, original BASS Lewis–Challinor hierarchy RHS scalar contraction at finite mass and nontrivial shear, direct finite derivative of Vlasov phase space, positive velocity-pressure cone, actual active Einstein source perturbation negative control, zero-fraction PR137 reduction, full collisionless BASS160 limit, external gamma-only Thomson species firewall, gamma and nu conserved number, and independent Raychaudhuri identity.

The maximum integrated J-tower versus exact Killing moments absolute difference among seven source cases is 1.5035839240340465e-10. Three models were rerun with radial 64/96/128, angular 16/32/64, radiation L=4/8/12, i_max=0/2/4 and tighter DOP853 controls. Nominal 96x32/L8/i2 vs strict 128x64/L12/i4 absolute final Σ errors were respectively 1.2002e-14, 2.37874e-14, 2.00487e-15; massive Pi relative deviations 1.96e-9, 2.25e-9, 5.42e-9. These are combined local convergence probes, not an AX11 bound.

**Corrected performance**: initial preliminary scalar benchmark accidentally recomputed the three moments three times and the 7.04× number was WITHDRAWN. Source-correct scalar once-per-complete-owner comparison on 1,024 original 96×32 cases gave optimized chunk=16 NumPy batch **2.34312×** faster; all three output towers had the matched numerical parity. One 16-row x 96 x 32 float64 tensor contains 393,216 bytes, but the entire allocated-memory peak is not assumed equal to that one tensor.

Nine independent 81-step research Einstein IVPs: serial wall 0.6846565s, two-process 0.4404346s (1.5545×), four-process 0.2733712s (2.50449×) with zero measured final Sigma/b/J0 difference under same inputs. This is not performance of native full H/He photoionization/RT production.

## 5. Admission and remaining physics

**SCOPED_PASS**: derived scalar source equations, original actual finite-mass BASS source parity, active coupled source-assisted massive velocity-index hierarchy with existing PR137 unpolarized Thomson gamma/nu, actual local numerical convergence and optimizations. **NOT_ADMITTED**: full autonomous massive i,l Boltzmann closure; finite-mass collision; E/B polarized Thomson with E2 source; two-way changed-geometry HHe chemistry; physical ionizing photon stress and source-wise ∑_r Q_r^a=0 energy exchange; absolute AX11 observational errors; measured neutrino masses or an observed Bianchi signal. Do not resume original PR137 AX08 old production checkpoints under this new science identity.

Next constructive code step: source-verified polarized Thomson collision owner and complete reaction event ledger, or a positivity-preserving autonomous radial-momentum distribution solver, then independent native HHe+RT Einstein source-controlled fresh-run branch. Native subagents unavailable in this host: NOT_RUN. Local Codex not used.

Reproduction: run the shell commands in TEST_RECEIPT.json after exact source checkout (this branch PR, BASS160 PR), with external original HHe source SHA. Physical output and charts in RESULTS.json, CONVERGENCE.json, BENCHMARK.json, COUPLED_MASSIVE_HISTORY.csv and three PNGs.
