# REI F4: BASS193 original-source × FS2010 energy-band deposition envelopes

2026-10-31 | PROJECT=`cosmosapjw-quantum/rei_bianchi` | Scope: auxiliary, conditional, no IVP | **Do not merge into native REI17 source**.

## 1. Live source provenance and scientific question (R1–R3)

Input source authority: immutable PR #302 HEAD `3a213db3b1fed40e0348e724579e8d73653f3634` (private master SHA256 `603b7eaacec1e8f0e3afe17c5c37ea9c4aee23890e969b1f121bf2b6f4f77192`), PR #303 HEAD `f593534869989aa7cb08fd8df47699bc33c46ed7` (private master `5b904c0019109d21ef88ff1610057010cd1b5bd6e446f9ac13188f60fb9fadd6`). Identical source CSV bytes are included in private full bundle for standalone replay, but public parent branch already contains these two exact source files. Frozen original PR287 16-node paired photon spectrum and four constant-hazard steps, BASS193 193 original chemistry states, 18,528 emission-to-arrival pairs, 192 arrived bins. Parent and siblings 296, 298, 299, 300, 301, 302, 303 not edited.

Furlanetto & Stoever (2010, MNRAS **404**, 1869–1878, DOI 10.1111/j.1365-2966.2010.16401.x) supplies a one-dimensional primordial target composition `xHII=xHeII=xi, xHeIII=0` at 14 xi values and 258 energies (10–9937.21 eV). Official author's raw `https://cosmicdawn.astro.ucla.edu/elec_interp.tar` exists at the group site but direct TAR bytes were **not acquired**. We used only independently retrievable 21cmFAST Git mirror commit `2a51aa316e216a1eb60650f9e7fbe35fe9e62040` (14 exact Git blob IDs in `fst_model_envelope_mirror.json`, verified via authenticated repository API). Original UCLA TAR byte identity remains `UNVERIFIED`. The source table values have decimal roundoff: up to ~3.9e-5 deviation in `fheat+fion+fexc` from 1. Some table descriptive headers are not the canonical interpolation grid; xi knots are those hardcoded by original C interpolation.

The present question is not to pretend that single-xi reproduces the original BASS multi-ion chemistry. It is: **what total first-generation photoelectron energy is permitted in each FS2010 deposition channel, conditional on a forced single-xi projection, without fabricating the unknown within-band electron energy spectrum?** A second electron-pool-equivalent xi projection provides a sensitivity diagnostic. We do not assert bounds on the real native BASS cascade.

## 2. Explicit derivation of the bounded table projection (R4–R5)

For arrival cell j, absorber a ∈ {H I, He I, He II, Li I}, electron-energy bin b, define original first-flight moment:

    A_{jab}=∫_{E∈B_b} E dN_{ja}(E)       [eV per original baryon].

Here `A_{jab}` is precisely the immutable PR302 CSV column for this species and band and is already integrated over all original emission epochs, paired 2E1 spectral quadrature, redshift and survival. The five electron bins are `[0,10.2)`, `[10.2,13.598434599702)`, `[13.598434599702,24.587389011)`, `[24.587389011,54.41776)`, and `[54.41776,60.922559447552]` eV. The last upper bound is the original pair transition energy `E_SINGLET_EV=60.922559447552` eV: no first-generation photoelectron has more kinetic energy than its parent photon.

Let `f_q(E,xi)` denote FS2010 tabulated **energy fraction** for channel q ∈ {heat, ion, exc}, using piecewise-linear interpolation in energy and xi (author C behavior). At each tabulated xi_k and bin B_b, compute extrema `m_{qkb} ≤ f_q(E,xi_k) ≤ M_{qkb}` over the interval by checking both bin endpoints and every interior tabulated energy; extrema of linear segments occur there. Round outward to 1e-7 before preservation. For xi between neighboring knots k,k+1 with linear weight t, an enclosure valid for that *model interpolation* is

    ell_qb(xi)=(1-t)m_qkb+t m_q,k+1,b
    u_qb(xi)  =(1-t)M_qkb+t M_q,k+1,b.

Because a convex combination of two functions is bounded below by the convex combination of their minima and above by that of their maxima, for all unknown energy-distribution measures dN_{ja}(E)≥0:

    D_q,j^lo = 1_{q=heat} A_{j,b<10.2} + Σ_{a,b≥10.2} A_{jab} ell_qb(xi_j)
    D_q,j^hi = 1_{q=heat} A_{j,b<10.2} + Σ_{a,b≥10.2} A_{jab}   u_qb(xi_j).

This is a **mathematically enclosed energy deposition integral of the specified FS model** even without the individual electron energies, not a Monte Carlo statistical confidence interval. There is no claim that all three extreme channels can occur simultaneously. It also does not constrain a true species-resolved plasma response when xHII≠xHeII or xHeIII≠0. The sub-10.2-eV terminal-to-heat assignment follows the FS model convention and does not establish instantaneous gas thermalization in tenuous IGM.

Two non-native xi projection definitions:

    (A) xi^H_j = xHII(z_{j+1})
    (B) xi^e_j = [xHII+yHe(xHeII+2 xHeIII)]/(1+yHe), yHe=nHe/nHref.

The latter preserves the H+He free-electron count per H nucleus when restricted to the FS no-HeIII family, but **does not preserve any specific H/He collision species population**. For xi outside [1e-4,0.999], the ordinary `projected` columns explicitly clip xi to the closest table knot as a scenario convention and flag `*_in_xgrid=false`. Also report `strict_xsupport` sensitivity by leaving all high-energy out-of-support bins as *unassigned* (`0≤D_q≤E_high,out`) while preserving the independent sub-10.2-eV terminal energy. `strict_xsupport` is strict only with respect to this xi grid, not native species physics.

## 3. Actually computed physical-source results (R7, C5–C8)

Input-sourced original conditional primary energy = `6.749242464433259e-11 eV/baryon`; sub-10.2 terminal convention `8.581099847924098e-12 eV/baryon`; high-energy fraction `5.891132479640848e-11 eV/baryon`.

For projected xi=xHII and clipped out-of-support cases:

| Channel | Lower eV/original baryon | Upper eV/original baryon | As % of primary energy |
|---|---:|---:|---:|
| heat | 6.71746696651259e-11 | 6.741336653447181e-11 | 99.529199–99.882864 |
| ionization (secondary kinetic budget) | 1.753188226350159e-14 | 1.3290708022461526e-13 | 0.025976–0.196921 |
| excitation photon energy budget | 5.764875364936643e-14 | 1.903054505793778e-13 | 0.085415–0.281966 |

For the electron-pool-matched projection, the heating interval is `[6.716490451964643e-11,6.741046761893137e-11] eV/b`; secondary ionization `[1.8243872064518816e-14,1.3673551228750805e-13] eV/b`; excitation `[5.978863179946389e-14,1.9613674498272204e-13] eV/b`.

**Projection support is nontrivial**. `xi=xHII` is outside the FS grid in 105 of 192 arrival intervals but holds just 0.7835756% of primary source energy. The electron-pool-matched projection is outside in 113/192 intervals holding 13.9740513% of primary energy. The xHII scenario's xi-support-strict heating envelope, with all out-of-grid high-energy source left free, is `[6.669441319069709e-11, 6.741336428887079e-11] eV/b`; for electron-matched it widens to `[5.892847153440825e-11,6.741042543214725e-11] eV/b`. These remain **off-manifold conditional FS-family estimates**, not admissible native heating.

The source-weighted saved endpoint helium mismatch from PR303 is ~0.165879 in absolute helium-vs-hydrogen ionization fraction; the original FS assumptions fail on positive-energy arrival bins. This conceptual error is much larger than the 1e-7 rounding of table envelopes and cannot be repaired by increasing floating-point precision. Li II source amplitude is itself a **conditional upper** from unresolved Ferrett/Langer production denominator. Even the conditional source energy is not an independently established cosmic Li II heating signal. No electron population or gas temperature was evolved; no new cosmic IVP, no Bianchi directional transport, no optical depth or CMB transfer.

## 4. Self-adversarial referee / implementation limitations (R6, C9)

- **Finding A: provenance typo (FIXED).** First local metadata copy omitted the terminal `c` in the Git SHA1 of `log_xi_-1.3.dat`. The 14 original remote files were re-fetched by commit and all 336 extrema were compared exactly against the local preserved envelope. All 336 extrema agreed, and the missing SHA character was corrected. This was a metadata identity failure, not a change to scientific output values.
- **Finding B: source transfer (CLOSED SCOPED).** Local extracted original source CSVs `155c70c1...84df6df`, `dd0b2ba5...7c1a09` were rehashed against original PR302/PR303 ZIP contents. The resulting 192-row data reproduce all original source energy sums and exact original zero-energy first arrival cell. No new source injections or normalization changes.
- **Finding C: terminal rule (RETAINED ASSUMPTION).** Author's C interpolation between 10 and 10.2 eV and FS theoretical sub-10.2 terminal convention can disagree near threshold. This unit adopts precisely the earlier parent terminal convention below 10.2 eV and uses mirror data only at ≥10.2 eV; reported as a model seam, not hidden.
- **Finding D: multiple species (BLOCKS NATIVE ADMISSION).** No positive-energy arrival bin satisfies exact original FS 1-xi chemical state at both endpoints; the tables cannot certify real native BASS deposition, independent of how narrow the internal model interval becomes. The `strict_xsupport` number only checks table *support*, not actual species or collision chronology.
- **Finding E: first moment insufficiency (CLOSED SCOPED).** No fabricated `f(E_mean)` approximation. Nonnegative measures supported in five physical bands obey an inequality generated by actual table extrema, so the interval remains valid without knowledge of higher moments. Tightening requires source-owner spectral redistribution, not a cosmetic solver tolerance change.
- **Finding F: linear table, not true cascade (BLOCKS F4).** The FS2010 raw Monte Carlo seed and data provenance are author-defined; the 21cmFAST mirror's Git identity was verified, but not original UCLA TAR byte identity; no new species-resolved cascade Monte Carlo or thermal relaxation check was run.

Primary verification: 17/17 unittest PASS (including perturbed source SHA negative controls), normal and Python `-O` deterministic CSV replay, 14/14 Git SHA identity and 336/336 envelope extrema exact source-to-model comparison, 192/192 original arrival record matches and no negative original energy. Distinct-author blind review and native subagent NOT_RUN (same-author adversarial review only).

## 5. DAG and future admission (R8–R10/C10)

- Working DAG **33/88**; central/canonical DAG **28/88**; F4-fast DAG **4/7**; canonical physical delta **0**. This finite auxiliary computation is **1/1_SCOPED**. No promotion. `F4=PARTIAL`, `L4_READY=false`, `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `AUTO_NEXT_NODE=false`.
- Positive next task: replace off-manifold table projection with species-resolved kinetic electron cascade on original BASS193 chemistry, including HeIII target, true electron energy deposition kinetics and no source double counting; preserve PR296/298/299 as read-only comparators. In parallel, original Li 1s 1S/3P and Ferrett n2+n3 vs native K denominator must be proven with isotope-complete source owner before any true-amplitude claim.
- Literature requested if privately available: (1) Ferrett et al., *Lithium 1s main-line and satellite photoemission: Resonant and nonresonant behavior*, Phys. Rev. A **36**, 3172 (1987), DOI `10.1103/PhysRevA.36.3172`, Tables II–IV and all supplementary numeric branching/covariance; (2) Langer et al., *High-resolution photoelectron spectrometry study of conjugate shakeup processes in the Li 1s threshold region*, Phys. Rev. A **43**, 1652(R) (1991), DOI `10.1103/PhysRevA.43.1652`, state-resolved channel markers and measurement covariance; (3) Furlanetto & Stoever, MNRAS **404** 1869–1878, DOI `10.1111/j.1365-2966.2010.16401.x` and original `https://cosmicdawn.astro.ucla.edu/elec_interp.tar` TAR (the only means to prove exact original source bytes).

## 6. Reproduction

`python -m unittest discover -s tests -v` then `python build_envelope.py` then `python plot_physics.py` from the extracted complete bundle. To substitute public Git ancestral source files when `inputs/` omitted, run code from the nested `research/rei_f4_fs2010_banded_proxy_20261031/` Git location. `python VERIFY.sh` is invalid; use `bash VERIFY.sh`. The original source CSVs are included exactly once in the private compact ZIP; original 75MB parent master is deliberately **not** repackaged.
