# F4: BASS21 원본 저장상태의 Li6/Li7 off-manifold 화학 감소 정리

2026-10-30. BASS source 내부의 정확한 정리다. REI가 사용하는 별도 17상태 또는 ON_refined 300 K bath를 교체하거나 동등하다고 주장하지 않는다. 새 IVP 없음.

## Source 및 정의

BASS 원본 21상태 Y_i=n_i/n_b. n_b: proper baryon number density (m^-3), n_e=n_b q21^T Y (m^-3), x=ln(a/a_ref), H=dx/dt>0 (s^-1). Original BASS finite chemistry (signed Newton extension):

F21(Y;t) = [G0(t)+Dweak+n_b(t)(q21^T Y) Gne(t)] Y.

G0,Dweak [s^-1], Gne [m^3/s]. 원본 source 계수는 129개 binary64 숫자 투영본 (원본 Git blob `2eba600a9...`)으로, 원본 AtomicNetwork method 자체는 바꾸지 않고 loader만 인증된 투영본에 연결했다. 21 상태의 Li6는 indices 13..16, Li7은 indices 17..20 (0-based). 두 lithium isotope는 (Z,q)에 따른 광전리/재결합 전이율이 같고 Dweak 및 nuclear/capture 차원이 Li6/Li7를 변환하지 않는다. 이것은 이 BASS source에 한정된 model premise다.

원본 isotopic inventory ν6,ν7>0, γ=ν6/ν7, retain I=(0..12,17..20), P:R21→R17, Eγ:R17→R21 with PE=I17, (Ey)Li6,q=γ yLi7,q. D= [select Li6]−γ[select Li7], δ=DY (4-vector). Change coordinates Y↦(y=P Y, δ=D Y), inverse Y=E y+S6 δ is globally linear/invertible. qLi=(0,1,2,3)^T.

## 정확한 off-manifold 분해 (신규)

Let A=G0+Dweak; R=P Gne E; f(y)=P F21(Ey), and n_e^E=n_b(q21^T E y). Because all elementary active lithium transitions stay within each isotope's four-state block and Li6/Li7 rates agree, the 21-source is exactly equivalent to

  dot y = f(y) + n_b (qLi^T δ) R y,
  dot δ = [G0,Li+n_e(Y) Gne,Li] δ = MLi(Y;t) δ,
  n_e(Y)=n_e^E+n_b qLi^T δ.

These are algebraic relations for all permitted Y, not a local linearization or model transfer. At δ=0 the invariant manifold holds. For nonzero δ, retained forcing g=n_b(qLi^Tδ)R y, with ||g||1 ≤ 3 n_b ||δ||1 ||R y||1. The row qLi bounds |qLi^Tδ|≤3||δ||1. The full Jacobian conjugated into (y,δ) at δ=0 is EXACTLY block triangular:

  T J21(Ey) T^{-1} = [[J17, n_b(Ry)qLi^T], [0_4x17, MLi(Ey)]].

J17=P J21(Ey) E. Hence det(λI21-J21)=det(λI17-J17)det(λI4-MLi) and the transverse spectrum is exactly the finite lithium four-state generator spectrum. The cross-forcing Jacobian block has rank≤1, without assuming global 21→REI17 lumpability.

## 변분과 물리적 안정성 조건

For nonnegative physical charge states and n_e≥0, MLi has nonnegative off-diagonal entries and column sums exactly zero (a four-state Markov population generator). Thus μ1(MLi)=0 and any solution to dot δ=MLi(t,Y(t))δ obeys ||δ(t)||1≤||δ(t0)||1 whenever the active BASS source stays valid. The δ-isotope-total sum is preserved. This contraction does NOT prove globally uniform exponential decay without positive lower bounds on rates throughout a time interval. At a fixed positive-rate saved endpoint, the birth–death four-state chain is reversible: with πq+1/πq = Γup(q)/Γdown(q+1), diag(π)^(-1/2) MLi diag(π)^(1/2) is symmetric, so λ={0, three strictly negative reals}. For original BASS z=2 saved T≈11999.956 K, ν6/ν7≈2e-5 and n_e≈6.002924 m^-3, the nonzero mode with smallest |λ| is -3.63774969737e-15 s^-1; frozen-rate characteristic time 1/|λ|≈8.710904×10^6 Julian years. This is a **local** frozen-coefficient rate, NOT evolving cosmic chemistry timescale or observational inference.

At same positive H and source-defined K (m³/s), only a pointwise BASS native optical-depth RHS difference is authorized:

  [dτ/dx](Y)-[dτ/dx](Ey) = (K n_b/H) qLi^Tδ.

It implies |Δ(dτ/dx)|≤(3 K n_b/H)||δ||1. It is not a history-integrated τ, CMB transfer, τ parameter sensitivity, or physical connection to REI's separate isotope inventory. Computing n_e−n_e^E by directly subtracting close floating-point totals can lose all significant digits: evaluate qLi^Tδ directly and use the factored expression.

## 원본 실제 source 수치 검산

VigilODE PR118 original SOURCE ZIP SHA256 `ba3f07a4f881ae8b02fd7b9690242ee29cfd1ae9f2b885b2601487010408508b`, 2,131,267 bytes. Five actual stored BASS pilot z=2 endpoint 21-state vectors (`SELECTED_BASS_ENDPOINTS.json`, original CSV Git blob `a49aa5276b4256d6bf0ad443b6b830effe2ab738`) and actual saved full21 RHS+Jacobian NPZ are read unchanged. Re-evaluate the original BASS 21-state rates, verify the 21×21 source matrix, block triangular structure, Li generator Markov properties and pointwise forcing on all five endpoints. On source original represented Y, ||δ||1/ν6=1.42e-17..1.304e-16, at or below binary64 representation uncertainty, so the computed residual ~1e-47 s^-1 must NEVER be promoted as a resolved physical residual. An explicitly constructed 5% Li6 q3→q2 physical-positive isotope-total-preserving perturbation gives ||δ||1≈7.549543987593153e-16 per baryon, qLi^Tδ≈-3.774771993796613e-16, forcing ||g||1≈2.04554e-33 s^-1; the largest individual forcing component 7.16677117e-34 s^-1. An independent 85-digit direct 21-state F minus lifted F calculation of the same *represented binary64 matrices and perturbed floats* yields max component residual ≈1.16e-105 and δ-ODE residual ≈1.05e-131. This is not source parameter accuracy, physical solver error control or independent-author review.

## Scientific boundaries

The theorem is true for this declared BASS electronic source with exact identical Li6/Li7 coefficients and no Li isotope-specific birth/sink or extra reaction. Isotope-resolved rates, source-owned nuclear Li events, different radiation exposure across isotopes, or external sink/source terms introduce an additional defect source term into dot δ and invalidate simple contraction. Original REI17 contains 300K bath, nuclear/CR/fast/escape channels and different H1/He4/T source inventory; its full source and normalization/clock are NOT the one computed here. Thus `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`, original physical fast **4/7**, working **33/88**, central **28/88**, delta0. Independent different-author R6/C9 NOT_RUN. The next actual physical question is owner-approved matching of the full REI17 chemistry/source/clock to BASS21, not silent identity by species names.

Background only: Tóth et al. SIAM J Appl Math 57 (1997), DOI 10.1137/S0036139995293294 on nonlinear kinetic lumping; prior direct source theorem in REI PR266; VIGILODE PR118 owns original endpoint archive. Our off-manifold forcing and actual frozen-mode computation are independently derived conditional results, not quoted claims of those papers.
