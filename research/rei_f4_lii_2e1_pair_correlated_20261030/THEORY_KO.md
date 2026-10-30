# REI F4 | Li II 2E1의 상관된 두 광자와 BASS21 첫 흡수 사건의 정적 결합분포

2026-10-30. **Source-scoped conditional physical result**. Immutable parent REI PR283 HEAD `e6b026757ddceb7fcd227229c0eb71391751e771`, BASS original AtomicNetwork owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. Original 193 BASS21 saved epochs and 21 ion states, no new IVP. All calculations use proper gas rest frame and `Y_i=n_i/n_b`, `n_b [m^-3]`, `H[s^-1]`, `σ_i(E)[m²]`, `E[eV]`, `c=299792458 m/s`. Signature (-,+,+,+). Nuclear/CR/thermal/photonic transport source is not silently bound.

## 1. Input, source status

The complete original PR283 source ZIP is nested byte-for-byte as `source/PR283_FULL.zip`, SHA256 `91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a`. That archive in turn binds PR282, original BASS193 trajectory SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`, original BASS native source and the original PR280 2E1/M1 source. This archive includes PR283's **partially visually unverified OCR transcription** of Drake, Victor & Dalgarno, *Phys. Rev.* 180, 25 (1969), Table II, DOI 10.1103/PhysRev.180.25. The current session also attempted the original Windsor bitstream URL; HTTP 403 prevented direct pixel readback. Therefore the 21 source ordinates remain **conditional on PR283**. The integrated tabular rate 1945.475 s^-1 agrees within 0.2822% with the independent 1997 theoretical Li II singlet rate 1940 s^-1, but this agreement cannot certify every source digit.

The source owner uses the Li II singlet transition energy `E_s=60.922559447552 eV`, two complementary photon energies `E_l=yE_s`, `E_h=(1-y)E_s`, with `0<=y<=1/2` and normalized half-interval density `p(y)=A(y)/∫_0^{1/2}A(u)du`. The source table is interpolated piecewise linearly; its unknown differential interpolation/systematic error is not assigned a false uncertainty band.

## 2. Joint first-absorption law (derived)

At each saved homogeneous frozen gas epoch, fix an artificial proper path of **one Hubble length** `L=c/H` without changing gas composition or emission. For original BASS21 ionic photoionization cross sections `σ_i(E)` define `κ_i(E)=n_bY_i σ_i(E)`, `κ=Σ_i κ_i`, and `T(E)=exp[-κ(E)L]`. A photon outcome `a` takes the five values `ESC,H_I,He_I,He_II,Li_I`; the corresponding conditional outcome law is

`π_ESC(E)=T(E)`, `π_g(E)=[1-T(E)] κ_g(E)/κ(E)` for `g` a gas category, with zero gas probability if `κ=0`. Thus `Σ_a π_a(E)=1` and all entries nonnegative. The **additional conditional modeling assumption** is that given the energy split y, the photons each undergo this frozen-gas Bernoulli absorption independently; any source angular correlation/path differences, opacity feedback, resonant scattering, and time dependence are omitted. After marginalizing the shared y, they are **not independent**:

`J_ab(z)=∫_0^{1/2}dy p(y) π_a(y E_s,z) π_b((1-y)E_s,z)`.

`J` is a 5x5 positive matrix with total sum one, and row/column marginals `L_a=Σ_b J_ab`, `U_b=Σ_a J_ab`. The fictitious independent-after-marginalization law is `J_ind=L⊗U`. The total-variation defect is `TV=1/2 Σ_ab |J_ab−L_a U_b|`. Define absorbed counts `N=0,1,2` per singlet pair:

`P_0=J_ESC,ESC`, `P_1=Σ_g (J_ESC,g+J_g,ESC)`, `P_2=Σ_g,h J_g,h`. Then `P_0+P_1+P_2=1`, `E[N]=P_1+2P_2`, `Var(N)=P_1+4P_2−E[N]^2`. The absorption covariance is `Cov(A_l,A_h)=P_2−(1−L_ESC)(1−U_ESC)`. It is NOT constrained to one sign by the general model. The expected first moment must equal PR283's independently assembled `∫p(y)[P_abs(yE_s)+P_abs((1-y)E_s)]dy` at each epoch.

**Threshold support theorem:** `E_s/2 = 30.461279723776 eV < 54.417765486 eV` (original He II threshold); the low-energy photon cannot photoionize He II, so every `J_HeII,b=0` and in particular two He II absorptions by the same singlet pair are exactly excluded within the owner-native one-electron source. This is independent of the detailed Drake ordinates, but not independent of the original BASS threshold model. Neither `J` nor `N` incorporates a physically evolved photon transport equation.

## 3. Numeric results: original 193x21 saved BASS physical source

Original native 193 epoch gas states and 21 ionic cross sections are evaluated at **both complementary 2E1 energies**, with composite Gauss-Legendre integration split at all 21 Drake tabular nodes, external H/He thresholds, and every original BASS native species threshold. Tested 4/8/16 quadrature orders converge at the claimed relative scale. New physical data: 193 epoch summaries, **193x25=4825** joint channel/escape outcome rows, and three figures. Zero new IVPs.

At z20: `P2=0.72121819033405`, `P1=0.27878180966595`, `P0≈0`, `E[N]=1.72121819033405`; at z2: `P2=0.00111592014700`, `P1=0.12892055012043`, `P0=0.86996352973257`, `E[N]=0.13115239041443`. The source-dependent absorption covariance peaks at `+0.032023654814` (z6.545056795) and reaches minimum `−0.023072919745` (z4.081617522), demonstrating **change of correlation sign along the archived model**. Maximum 5x5 joint-vs-independent total variation is `0.159184541988` (z6.545056795), a nontrivial physical-state/source effect. The covariance values and TV are *not* universal numbers for the universe.

The original conditional source's possible singlet branch rate is `K_s(z)=K_Li1s(z)−K_triplet_forced(z)`. We **set singlet yield 1 only to define a conditional scenario** on this allowed subset, not an experimental yield. A saved-grid numerical integration of `K_s P_N/H` over original `x=ln a` gives `N=2: 2.1745145060967717e-11`, `N=1: 8.405573060498013e-12`, `N=0: 3.5748508260620633e-16` events/baryon. The pair total is `3.0151075606548325e-11`; the expected absorption-produced *initial free-electron count* is `5.189586318243342e-11/baryon`, matching PR283's first absorbed-photon moment (relative roundoff), without any actual evolved chemical model. The independent-marginal approximation would assign `N=2: 2.1745027591912246e-11`, a small integrated but nonzero net defect. The source is prescribed and the integration is **postprocessing of already saved fields**, not a new IVP.

## 4. Boundaries and next physical action

Conditional frozen gas, one artificial proper Hubble length, no actual observed cosmological optical depth/anisotropic photon trajectory. The 2E1 pair angular correlation and time-dependent photon emission positions are not source qualified; the source unknown singlet/triplet branching is not set physically. This computes initial photoelectrons, not thermal electrons after stopping, secondary ionization, heat, optical depth, or CMB. PR283 Drake1969 Table II scan still requires visual row readback. Full REI17↔BASS21 chemistry/source/nuclear/CR/fast/electron/thermal/radiation and common `nHref/nb,H,K` clock remains unbound. No merge/force push; **F4 PARTIAL; L4_ready=false; central28/88 working33/88 fast4/7; original delta0.**

Relevant primary physics: Drake/Victor/Dalgarno (1969) DOI 10.1103/PhysRev.180.25 (unverified scanned row glyphs); Derevianko & Johnson, PRA56 1288 (1997) DOI 10.1103/PhysRevA.56.1288, integrated-rate comparison; Verner et al., ApJ465 487 (1996) DOI 10.1086/177435 for ground-state photoionization cross sections. These are provenance/context, not evidence that the conditional local model is actual photon transport.
