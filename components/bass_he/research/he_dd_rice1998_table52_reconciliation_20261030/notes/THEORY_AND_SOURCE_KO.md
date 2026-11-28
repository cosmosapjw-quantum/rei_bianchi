# BASS_HE PR127: Rice(1998) Table 5.2 source reconciliation and nonthermal D multiplicity

## Source authority and immutable inputs

This auxiliary branch continues BASS_HE PR126 at `3305c4579221edde36c14f941b3530375aca4f7a`, itself a child of PR125 at `b7a3f7e7f3eb2461ff75039797c085296e575acb`. PR125's Rice(2000) Table I is immutable canonical source: Git blob `9cdec4449b22bdba2797bbdfb815e98901b85636`. The older Rice(1998) Table 5.1 is reused **byte-for-byte** from PR125 blob `266859bb62ef0929b098928b686f945aca600cb9`. The newly supplied image of Rice(1998) Table 5.2 is an **excerpt**, not a complete-disssertation PDF. Original image SHA256 is `103022f4d890519ee9273e8ddc5d7a632a93ada30ab4a5259216f600b2e10de2`; 6 high-bin measured rows and telescope yields are transcribed with the published statistical errors. The private source image is not committed to GitHub.

The thesis Table 5.2 has 6 rows: at θ_CM=45.4,63.6,91.4,108.4,124.4,139.7 deg, DCS=(0.118,0.486,1.170,0.921,0.566,0.594) nb/sr, pure statistical SD=(0.091,0.122,0.144,0.131,0.097,0.107) nb/sr, telescope yield=(249,951,1977,1394,771,735), yield SD=(192,239,242,198,133,133). Their reflected angles=(134.6,116.4,88.6,71.6,55.6,40.3) deg. Reflection about θ_CM=90 deg identifies the **same identical-daughter event**; it does not give 6 new independent measurements. The thesis previously supplied 139-page PDF lacks Table 5.2. This new excerpt closes that **specific source excerpt** gap, not the missing full dissertation pages or detector-response gap.

## Direct source-version comparison

Matched by laboratory and CM angles against Rice et al. *Phys Rev C* 61, 064612 (2000) Table I. Across the 12 source rows, the 2000/1998 published/preliminary *central-value ratios* are:

`[1.212598425197, 1.211538461538, 1.208333333333, 1.209790209790, 1.209677419355, 1.206088992974, 1.186440677966, 1.213991769547, 1.213675213675, 1.205211726384, 1.201413427562, 0.723905723906]`.

The first 11 have descriptive, unweighted mean 1.207159968848 and range [1.18644068,1.21399177], while the sixth high-bin CM 139.7-degree row has 0.72390572. This fails the **exact single-global-rescaling central-value hypothesis**, even when respecting the last row's printed rounding: last ratio ∈[0.71488646,0.73294019] with last row published at 2 decimals and preliminary at 3 decimals, below the first high row's minimum rounding ratio 0.135/0.1185=1.13924. This is a **deterministic descriptive source-version finding**, NOT a statistical hypothesis rejection, author-error finding, corrected measurement, or erratum. Same experimental campaign ⇒ 1998 and 2000 row errors correlated to unknown extent; their cross-version joint covariance is not provided. No χ², p-value, confidence interval or inverse covariance is justified.

Telescope reported yields and relative DCS statistical errors agree in fractional size within 0.0012 (rounding) at all 6 high-bin angles. Their ratio Y/(dσ/dΩ) is an experimentally combined *reported yield-to-DCS response proxy*; without the original yield definition, photon flux, solid-angle and coincidence efficiencies, this ratio is **not** a separately measured detector acceptance, efficiency or photon-energy response. The yield and cross-section errors are dependent, not 12 separate measurements.

## Energy-multiplicity bridge (new physics-to-computation contract)

Metric (-,+,+,+), frozen rest energies `M_alpha c²=3727.3794118 MeV`, `m_d c²=1875.61294500 MeV`, `Q=23.84647820 MeV`. For alpha-comoving incident photon energy E and CM angle θ, PR126's exact identical-daughter two-body kinematics give

\[ K_\pm(E,\theta)=\frac{E-Q}{2}\pm\frac E2\sqrt{1-\frac{4m_d^2 c^4}{s_E}}\cos\theta,\quad s_E=M_\alpha^2c^4+2M_\alpha c^2E,\quad K_++K_-=E-Q. \]

Rice's author convention for ordered final two-d angular density is `σ_event(E)=(1/2)∫dΩ_CM dσ_photo^ordered/dΩ_CM`. For one monoenergetic photon at E, the unnormalized **daughter injection measure** over birth kinetic energy is

\[ \mathcal K_D(E,K)=\frac12\int_{4\pi}d\Omega_{\rm CM}\frac{d\sigma_{\rm photo}^{\rm ordered}}{d\Omega_{\rm CM}}(E,\theta)\left[\delta(K-K_+(E,\theta))+\delta(K-K_-(E,\theta))\right]. \]

The first two moment identities are exact:

\[ \int dK\,\mathcal K_D=2\sigma_{\rm event},\qquad \int dK\,K\,\mathcal K_D=(E-Q)\sigma_{\rm event}. \]

Therefore `(gamma,dd)` events and D-production counts differ by a multiplicity of 2. Protheroe, Stanev & Berezinsky (Phys. Rev. D 51 4134, 1995) Eq. (21) explicitly use effective D production `σ_D^eff = σ(gamma,pnD)+2 σ(gamma,DD)`; this is an independent literature consistency check on the **factor of 2**, not a complete BASS_HE event calibration. In the He proper frame, with `nγ^(alpha)(E,Ω;x,t)` units m^-3 MeV^-1 sr^-1 and local `n_alpha`, the **still-uninstantiated** gamma-dd event rate density is

\[ \mathcal R_{\rm event}(x,t)=n_\alpha c\int dE\,d\Omega_\gamma\, n_\gamma^{(\alpha)}(E,\Omega_\gamma;x,t)\,\sigma_{\rm event}(E). \]

The daughter source follows the same convolution with `\mathcal K_D` and integrates to `2R_event`. This is a DEFINITION/DERIVED operator, not a computed source-target history. A source-version-specific conditional energy-weighted differential cross-section envelope at each angle is `barD_i (E_min-Q) ≤ ∫ w_i(E) D_i(E)(E-Q)dE ≤ barD_i(E_max-Q)`, **only** for the same nonnegative normalized experiment weight/acceptance and fixed effective angle. These tabulated lower/upper values [nb MeV/sr] are not measured heat or an astrophysical rate; the 1998 and 2000 published bins are not monoenergetic points.

## Research literature scope

- Protheroe et al. PRD51 4134 (1995): full photon/electron cascade transfer, Eq.21 explicitly counts 2 D from gamma+He→dd; historical cosmology, not a source-owned BASS_HE photon history.
- Poulin & Serpico PRD91 103007 (2015): below background pair-production threshold, nonthermal spectra are nonuniversal. Eq. (2) photon loss/source, Eq. (8) redistribution source kernel; the spectrum must be derived for a specified injection history and target epoch, not silently equated with a universal function.
- Casas, Barriga-Carrasco & Rubio PRE88 033102 (2013): free/bound electron stopping and experiments in LiH, CH₂ and Al plasmas. Their analyzed D beam in aluminum is around 1 MeV and plasma-specific; no direct calibrated 100-MeV-class D stopping or thermal deposition in the target BASS_HE He/H plasma is provided. Reuse formalism, not numeric stopping as an astrophysical fact.
- User-provided `HD.Rovibration.805a7aa5(1).radex` is molecular hydrogen-deuteride rovibrational data, **not** a source for gamma+He nuclear photodisintegration nor a high-energy deuteron slowing kernel. Its identity is recorded without importing it into nuclear rates.

## Boundaries and DAG

`SOURCE_RECONCILIATION=2/2` is new auxiliary source-evidence progress only. Canonical `CENTRAL_DAG=28/88`, `HE_PHYSICAL_DAG=14/18`, `RICE_BIRTH_AUXILIARY=1/2`, `canonical_physical_delta=0` unchanged. `kappa=null; R_event=null; heat_rate=null; L4=false; PRODUCTION=HOLD` unchanged. Missing authentic He-rest gamma source history, experimental energy-angle response, target `n_alpha,U_alpha`, D-fast stopping/escape/deposition/thermal capacity mean that no astrophysical event rate, thermal power or production result can be admitted.
