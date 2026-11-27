# HE_DD_TARGET_FRAME_BIRTH_LEDGER_20261029: 생성 두-D 모멘트와 미해결 물리 소스의 분리

## Authority / scope
BASS_HE PR107 (start HEAD `85e2faeebd777ab3e9b287a0dc1dfd38d9af723c`, draft/open), PR104 frozen masses, 2026-10-29. Reuse without replay: PR105/106 source-conditional envelopes, PR107 reciprocity and later detector-semantic fail-closed adapter. IAEA EXFOR `M0475.x4` raw original blob `c49433293921dbb012d7f1b0387745732a598efa`, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, source revision `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871`. No source replacement. Published literature alone does not confirm the coincidence efficiency, DA event/particle normalization, polarization or matched-s inverse raw DA. This study does not select κ=1/2.

## Formal premises and units
Sign (-,+,+,+). Keep c. Define rest-energy numbers `M=M_alpha c^2=3727.3794118 MeV`, `m=m_d c^2=1875.61294500 MeV`. These values are a frozen PR104 convention, not a new mass evaluation. Photon energy `E=E_gamma` in **alpha-target rest frame**, positive invariant `s=M²+2ME` in MeV². Threshold `E_thr=(4m²-M²)/(2M)>0`; only `E>=E_thr`. `q²=(s-4m²)/4` is CM daughter `(p_D c)²`. For CM cosine `μ` relative to incident photon, `-1<=μ<=1`:

    Δ²=E²(s-4m²)/(4s),       K0=(M+E-2m)/2,
    K_±=K0 ± sqrt(Δ²) μ,
    E_lab,±=m+K_±,
    (p_z,± c)=E/2 ± (M+E)q μ/sqrt(s),
    (p_perp,± c)^2=q²(1-μ²), with opposite transverse vectors.

The z axis is target-rest photon direction. The two outgoing deuterons are always produced as one *correlated pair*, independently of whether experiment publishes an inclusive one-D or one-event angular differential. A single experiment's ``coincidence`` tag does not fix the latter mapping.

## Proposition A (exact event conservation and marginal mean)
For **each** physical two-body event with the stated incoming state:

    K_+ + K_- = M+E-2m = E-Q,  Q=2m-M=23.8464782 MeV.

Hence for *any* probability measure P on CM direction, including anisotropic, non-exchange-symmetric choices of a temporary daughter label:

    (1/2) E_P[K_++K_-] = K0,
    energy_rest_gain + energy_D_kinetic - energy_gamma = Q+(E-Q)-E = 0,
    delta baryon number = -4+2+2=0; delta charge=-2+1+1=0.

Proof: direct target-rest Lorentz boost of opposite equal-CM-energy daughters gives their total energies `M+E`; subtracting each rest energy m yields the identity; all other conservation equalities follow the reaction stoichiometry. No angular symmetry needed because **both daughters are counted**. For only a *designated* daughter, mean K0 would require E_P[μ]=0, which cannot be inferred from the experiment.

### Correlated second moments
Let `a=E_P[μ]`, `b=E_P[μ²]` with `0<=b<=1` and `a²<=b`. Defining the one-D marginal as uniformly drawing one of the two deuterons in each event,

    Var(K_D,marginal)=Δ² b,
    E_P[(K_+-K0)(K_--K0)] = -Δ² b,
    Var(K_+,labeled)=Var(K_-,labeled)=Δ²(b-a²),
    Cov(K_+,K_-)=-Δ²(b-a²).

The cross moment centered at K0 and the true labeled covariance are **different** when a ≠0. The equal-marginal-mean result is not a measured spectrum; b remains unknown. The support is `K0-sqrt(Δ²) <= K_D <= K0+sqrt(Δ²)`. The bounds are kinematic and require no angular DA normalization or photon flux.

## Proposition B (event rate and fast-D source as a separate operator)
Let `n_alpha^rest` be target proper density [m^-3]. In a local tetrad normal frame let `n_gamma^n(E,n,t)` be the number density per **physical local volume, energy and solid angle** [m^-3 J^-1 sr^-1]. For a cold moving target with beta (v/c) in that frame,

    E' = gamma_alpha E (1-beta_alpha · n),
    R_event^n = n_alpha^rest c ∫ dE dΩ n_gamma^n(E,n) gamma_alpha(1-beta_alpha·n) σ_event(E', polarization-transformed, nuclear convention).

Here R_event^n is a rate per normal-frame proper physical volume and local normal time [m^-3 s^-1] in the local inertial approximation. The gamma and flux factors follow from `n_alpha^n = gamma n_alpha^rest` and relative beam speed `c(1-beta·n)`. This assumes a monokinetic target population; a thermal/tilted target needs an integral over its distribution. The photon polarization, frame Jacobians, and source-qualified **total event** nuclear cross section must be actually supplied. A target-rest photon density representation instead yields `n_alpha c ∫n_gamma^(alpha) σ_event`; these are alternate frame representations, never to be combined without transforming the distributions.

Let `r(E,n;t)` denote this still-unknown differential event density with respect to target-rest energy and incident direction. If `P(dμ dφ|E,n)` is the *event-normalized* CM angular law and `K±` the daughters then the birth spectrum is

    B_D(K,t) = ∫ dE dΩ r(E,n;t) ∫P(dμ dφ|E,n)
                    [δ(K-K_+(E,μ))+δ(K-K_-(E,μ))].

Therefore

    ∫dK B_D = 2 ∫dE dΩ r,        ∫dK K B_D = ∫dE dΩ (E-Q) r.

Both are identities **conditional on existence of r and P**; no numerical physical rate follows. For an actual spectrum `F_D(K,t)` in a selected material rest frame, a schematic stopping operator is

    ∂_t F_D + ∂_K(\dot K_stop F_D) = B_D - loss_D + transport/expansion,
    Q_to_other_channels = -∫dK \dot K_stop F_D + boundary/secondary terms,
    C_V ∂_t T = Q_heat - Q_cool + other work.

`Q_to_other_channels` is **not** necessarily thermal heat. Stopping can create escaping secondaries or excite/ionize material, and the appropriate reprocessing and C_V ownership must be supplied. Thermal-time deposition cannot be substituted for birth energy.

### Constructive counterexample to an overclaim
If an artificial stopping fraction is `η(K)=K/Kmax`, with Kmax at least both daughter kinetic energies, its per-event energy deposit is `[K_+²+K_-²]/Kmax=2(K0²+Δ² μ²)/Kmax`. This depends on `E_P[μ²]` even though the total birth energy `2K0` does not. This is a **manufactured example**, not a D_fast stopping model. Thus the missing angular distribution does not block the birth-energy moment identity, but it does block the shape-dependent deposition integral.

## Other repo intake, scoped relevance
- BASS PR244 CE1-G immutable-current-input derivative/energy certificate: learn input-binding discipline; no nuclear σ provider.
- bass_cr PR122 exact marginal He high-low source flow: **atomic** He combinatorial event flow, not ^4He photonuclear exclusive event kernel.
- rei_bianchi PR263 frozen UVB optical-depth source sensitivity: no 213/330 MeV resolved photon bath; do not import UVB rate.
- rec_bianchi PR156 HD line frequency energy ledger: useful dual-ledger concept; HD rotational photons are not nuclear He disintegration.
- WU088_HH PR158 owner-consumer time/units 105K preflight: reuse typed units/clock caution; 105 K HD reaction not nuclear D_fast stopping.
- vigilode PR108 same-physics synthetic matrix error and performance: independent norm/certificate policy, no physical provider.

## Source and admission verdict
Original Arends1976/Silverman1984 full papers and calibrated detector/polarization corrections not obtained in this run; EXFOR compiled M0475 offers COINC/TOF and DA/SIG metadata but not event/inclusive normalization. The Silverman published 376 MeV deuteron experiment maps to Egamma213.1255176098 MeV and is **not** a source-qualified 330 MeV inverse DA point. Primary 330 MeV event SIG is not in M0475. `R_event=null`, `kappa=null`, `physical_activation=false`, `L4=false`, `production=HOLD`. Independent native distinct-author R6/C9 `NOT_RUN`.
