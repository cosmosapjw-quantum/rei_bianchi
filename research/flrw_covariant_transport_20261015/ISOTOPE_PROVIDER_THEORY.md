# Isotope-native provider contract — 2026-10-15

Status: **READY_FOR_STANDALONE_D_PROVIDER_IMPLEMENTATION**. Selected model: **GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1**. This is a conditional atomic D model, not a precision isotope calculation or a completed D reionization history. Existing H/He production remains a separate lane. No Rust, production state, git, or completed scientific calculation was changed by this research unit.

## 1. Actual acquired sources and choice

The pinned Grackle source is commit `af7939494ce65007887ada7b98d1813df6843346`. Its original `solve_rate_cool_g.F`, lines 2322–2346, directly reuses H `k1` (electron ionization), `k2` (recombination), `k24shield` and `kphHI` (photoionization) for DI/DII. The original file was freshly fetched and its SHA256 equals the already retained source: `0a94542b8b35bcb47ebb1865320c3e37a3831818549eaabcbfeb65aab158fe83`. Source URL:
https://raw.githubusercontent.com/grackle-project/grackle/af7939494ce65007887ada7b98d1813df6843346/src/clib/solve_rate_cool_g.F

The original Glover & Savin (2009) extended Appendix A independently sets CI2=CI1 and PR2=PR1:
http://user.astro.columbia.edu/~savin/papers/MNRAS393_911_fulltables.pdf
This supports the **named H-equality approximation**, not an error bound for D. Its displayed PR1 is not a reason to substitute a new recombination case into the existing Case-A model.

The selected Rust coefficient owner is the already present `igm_rates(T)`, whose H entries preserve Grackle source literals, floors/caps, and Case-A phenomenology. Do not change H/He or the raw provider's 100 K guard. Use the separate `igm_rates` operational domain 1–10^6 K; combined use with the existing Savin CX fit is limited to **2.7–2×10^5 K**. These are operational/domain declarations, not a newly measured physical-accuracy range.

The existing `reHII_rate` formula comes from the original Hui & Gnedin (1997) appendix:
https://arxiv.org/pdf/astro-ph/9612232 .
It is a **thermal recombination cooling coefficient**. It excludes the binding-energy release that the common energy ledger adds to escaped radiation. The original appendix states its fit accuracy over 3–10^9 K, but that claim must not be promoted to all current Grackle rate combinations or to the adopted D approximation at 1–3 K.

## 2. Frozen provider and threshold contract

All public new-state/RHS quantities should be SI. Functions are immutable point evaluators, returning errors on invalid/nonfinite inputs; they must not change caller states or existing guards.

| Output | Concrete source and conversion |
|---|---|
| D electron ionization coefficient | `igm_rates(T).ci_cm3_s[0] × 1e-6` m³/s |
| D Case-A RR coefficient | `igm_rates(T).rr_cm3_s[0] × 1e-6` m³/s |
| D RR thermal cooling coefficient | `igm_rates(T).rr_cooling_erg_cm3_s[0] × 1e-13` J m³/s |
| D electron-excitation cooling coefficient | `igm_rates(T).ce_erg[0] × 1e-13` J m³/s |
| Source numerical effects | carry H CI-floor and CE-cap flags/coefficient diagnostics; never call these measured physical tails |
| D photo cross section | threshold-corrected H-equality model defined below; original Verner H fit |
| D/H CX | existing `Savin2002::rates(T)`; do not recopy or extend its fit |
| Free-free/CMB | common full-network owner only; D changes electron inventory and the Z² ion sum, not the number of independent cooling calls |

Set the model's H binding threshold to the existing owner `χH=13.598434599702 eV`. The chosen **explicit conditional approximation** is `Δχ=0.0037 eV`, hence `χD=13.602134599702 eV`. Savin (2002), ApJ 566, 599, explains the forward CX endothermic threshold as approximately 3.7 meV (~43 K):
https://iopscience.iop.org/article/10.1086/324218/pdf .
The last digits of the derived χD are arithmetic from the H owner, **not measured precision for D**. Store both the approximate defect and its provenance. Do not identify either Savin fit exponent 37.1 K or 33.0 K with this energy defect.

Photo model:
```text
sigma_D(E) = 0                                      for 0 <= E < chi_D
sigma_D(E) = AtomicProvider.cross_section(HI,E)*1e-4 for chi_D <= E <= 50000 eV
```
This uses the actual existing Verner H fit and converts cm² to m². Reject E<0, E nonfinite, or E>50000 eV. The existing rounded H fit edge is 13.60 eV; it remains visible in provenance. At the selected χD the H fit is already nonzero. The new D cutoff is a **declared threshold correction to the H-equality model**, not verbatim Grackle behavior and not a reduced-mass cross-section calculation. Do not reuse H photoheating unchanged: it would assign the wrong binding energy per D event.

For gas-rest photon number density per energy and solid angle, Nγ(E,Ω) [m^-3 J^-1 sr^-1],
```text
Gamma_D = c ∫ dΩ ∫ dE Nγ sigma_D                         [s^-1]
heat_D  = c ∫ dΩ ∫ dE Nγ sigma_D (E-chi_D)              [J s^-1 per DI]
input_D = chi_D Gamma_D + heat_D
```
E and χ in this equation are joules. A monoenergetic event helper may take E in eV and convert once. The current standalone point API may accept externally bound (Gamma_D, heat_D); require nonnegative finite values and heat_D=0 if Gamma_D=0. This inequality check alone cannot prove a source spectrum: production coupling must bind both to the same absorption events. The transport's competing-absorber allocation must add DI once so a photon cannot ionize H and D simultaneously.

## 3. Point RHS and sole ownership of energy

Let P=nD0 Gamma_D, C=ne nD0 beta_D, R=ne nDp alpha_D. Let X=kf nD0 nHp − kr nDp nH0 be the **net forward** CX event density per second. Let L_R=ne nDp ell_R and L_E=ne nD0 ell_E. All are proper-volume quantities.

```text
dot nD0 = -(P+C-R+X)
dot nDp = +(P+C-R+X)
dot nH0 = +X; dot nHp = -X
dot ne  = P+C-R                           # CX contributes exactly zero

Qthermal = nD0 heat_D - chi_D C - L_R - L_E - DeltaChi X
Qbinding = chi_D (P+C-R) + DeltaChi X
Qescape  = chi_D R + L_R + L_E
Qphoto_input = chi_D P + nD0 heat_D

Qthermal + Qbinding + Qescape - Qphoto_input = 0
```

For a standalone D atomic point evaluator without CX, set X=0 and expose the atomic electron delta. If CX is included in the same RHS, use the existing Savin provider and the **same** energy defect. A caller using `step_frozen_rates` for a split CX map must not also integrate X from this RHS in that substep. No duplicate CI cooling from Grackle `ciHI_rate`: χD C already owns the binding threshold sink.

RR `ell_R/alpha_D` is an effective rate-weighted kinetic energy removed by the chosen coefficient pair; it is not forced to 3 kBT/2. A Case-A escape closure gives escaped RR power χD R+L_R. Electron excitation and free-free are cooling/escape terms without ion-count changes. Full-network free-free is proportional to ne Σ Z_i² n_i, including D+ once; use full ne consistently across H/He/D. Compton exchange also uses the common full ne once.

This point evaluator excludes expansion. For network evolution, proper n obeys n_dot+3Hn=S R; Y_i=n_i/nb removes dilution with nb=Σ A_i n_i. Electrons have A=0. The common EOS uses nthermal=Σheavy n_i+ne; its changing particle count must enter T evolution. No legacy 17-state-to-17-nuclide projection or bypass is allowed.

## 4. Actual inventory choices and conditional initial ion fractions

**Selected available D inventory candidate:** Cooke, Pettini & Steidel (2018), ApJ 855,102, DOI10.3847/1538-4357/aaab53, §V Eq.(10):
`rD=nD/n1H=(2.527 ± 0.030)×10^-5`, quoted 68% confidence interval.
https://ar5iv.labs.arxiv.org/html/1710.11129
This is a published observational inference from seven low-metallicity absorbers. It is **not** a freshly run BBN result, a matched REC donor, or a D neutral fraction. Store `inventory_kind=OBSERVATION_CONDITIONED_PRIMORDIAL_RATIO`, source, central value, uncertainty definition, and normalization. A configurable conditional scenario can adopt it without inventing a donor.

The REC donor supplies an H ion fraction and T, but does not supply a D ion fraction. One concrete autonomous conditional initialization, for the initially zero-ionizing-photon state, is frozen H/D CX balance:
`xDplus = kf nHp / (kf nHp + kr nH0)`.
It follows by setting the CX net X to zero and is a model IC, not recovered cosmological D recombination. Require an explicit IC mode or explicit xDplus. State which processes were neglected for that initialization. If denominator=0, reject missing information instead of inventing a fraction.

Do not append D at fixed nH and silently keep the same baryon density. For an H1/D/He4 inventory with fixed nb and fHe=nHe4/n1H, use
`n1H=nb/(1+2 rD+4 fHe)`, `nD=rD n1H`, `nHe4=fHe n1H`.
Alternatively a fixed-nH standalone fixture is valid if identified as such; no cosmology admission follows.

**Separate BBN comparison candidate, not merged with the selected measurement:** Pitrou et al. (2018), Physics Reports, Tables VII–VIII:
D/H=(2.459±0.036)×10^-5; 3He/H=(1.074±0.026)×10^-5; 7Li/H=(5.623±0.247)×10^-10, at Ω_b h²=0.02225, Nν=3, τn=879.5 s.
https://www2.iap.fr/users/pitrou/publi/PhysReptBBN.pdf
These published predictions provide an actual multi-nuclide candidate. They are not a new PRIMAT execution or matching current cosmological donor. A future matched donor must identify code/version and all cosmological/nuclear inputs or explicitly adopt this published conditional inventory.

## 5. 3He and Li: acquired tables and bounded next implementation

The public original Verner tables were actually downloaded; SHA256 and exact URLs are in the companion JSON. They are keyed by atomic Z and electron count N, not isotope A.

* 3He: a concrete first electronic-model extension can reuse the existing HeI/HeII/HeIII coefficients and photo cross sections with **element-equality isotope approximation**, track A=3 independently, and avoid counting the same helium nucleus in both He3 and He4. Adopt an explicit 3He inventory, e.g. the separately labelled Pitrou table, and preserve total baryons. This is source-backed elemental electronic physics with a stated isotope approximation, not isotope-resolved accuracy. Neutral-helium many-electron physics cannot be justified by the simple one-electron reduced-mass law.
* Li: original Verner et al. (1996) photo table has Li I edge/Emax **5.392/64.39 eV**, Li II edge75.64eV and Li III122.5eV. The Li I outer-shell single fit must not be extended above64.39eV without the actual inner-shell/branching provider. Original implementation: https://www.pa.uky.edu/~verner/dima/photo/phfit2.f . Li is not enabled by acquiring a single outer-shell fit.
* Original Verner & Ferland (1996) RR Eq.(4):
  `alpha(T)=a/[sqrt(T/T0)*(1+sqrt(T/T0))^(1-b)*(1+sqrt(T/T1))^(1+b)]`.
  Li I destination (Li+→Li0): a=1.036e-11 cm³/s, b=.3880,T0=107.7K,T1=1.177e7K.
  Li II destination: a=1.112e-10,b=.6926,T0=24.37K,T1=8.323e6K.
  Li III destination: a=3.039e-10,b=.7539,T0=18.71K,T1=6.209e6K.
  The original low-Z fit range is 3–10^9K. These are RR rates, not kinetic cooling moments, DR, CI or CX. No Li thermal coefficient is invented.
  https://arxiv.org/pdf/astro-ph/9509083
* Switzer & Hirata (2005), §§II–III, directly computes the effect of H recombination photons above χLi=5.3917191eV, including Lyα and two-photon emission up to10.1988eV:
  https://ar5iv.labs.arxiv.org/html/astro-ph/0507106 .
  Therefore an H-ionizing-only source beginning at13.6eV cannot supply a complete Li I ionization calculation. Next Li unit must extend the actual emissivity/spectral transport below the H edge, with explicit source support, and acquire CI/DR/CX plus rate-weighted thermal ownership before a full Li history claim. This does not block D or FLRW.

## 6. New checks and lower-tier coding acceptance

The new Wolfram evaluator record `ISOTOPE_PROVIDER_WOLFRAM.json` reports event residuals {0,0,0,0} for PI/RR/CI/CX. Dimension exponent vectors (kg,m,s,K) are alpha=(0,3,-1,0), cooling coefficient=(1,5,-3,0), volumetric cooling=(1,-1,-3,0), heat/absorber=(1,2,-3,0). This checks algebra and dimensions, not physical rate accuracy.

The optional Coulomb/Milne derivation is retained as **NOT_SELECTED_RESEARCH_ONLY**: with λ=μD/μH, one-electron Coulomb lengths scale λ^-1 and energies λ; in the E1/nonrelativistic/common-relative-temperature/no-recoil model, σD(E)=λ^-2 σH(E/λ), alphaD(T)=λ^-2 alphaH(T/λ), and ellD(T)=λ^-1 ellH(T/λ). The Maxwell velocity density is unchanged between (λμ,T) and (μ,T/λ); Milne's Eγ²/(μ²v²) factor plus the photo scale gives the two rate scalings. Nahar & Pradhan's original Milne Eq.(9), https://ar5iv.labs.arxiv.org/html/astro-ph/0310624 , and Gurian et al. §2.2 Eq.(2.11), https://arxiv.org/pdf/2110.11964 , were read. Replacing electron mass by the atomic reduced mass and applying it to fitted thermal pairs is an additional model step, not an independently validated D provider. **Do not implement this alternative in this unit or make it a gate to the chosen H-equality model.**

Implement only a new standalone isotope-native provider/RHS and focused tests in root-assigned new Rust paths. Preserve all existing modules except root-authorized export. Required new tests:

1. Exact source-wrapper equality and SI conversion at 3,10,100,10^4,10^5K; retain source floors/caps and operational1/10^6K boundaries.
2. Photo cutoff at below/at/above χD; same original H cross section above cutoff; reject invalid/>50000eV inputs. Monoenergetic threshold event has zero heat; above-threshold input=heat+binding.
3. Point atomic ion count and electron count; H/D/charge/baryon identities with an included CX RHS or the existing exact split CX map. D=0 is a genuine no-op.
4. Pure PI, CI, RR, CE and combined energy residual, with **same χD and Δχ**; test signed CX heating/cooling and unchanged CX electron count.
5. Negative/nonfinite input and inconsistent Gamma=0/heat>0 fail transactionally. No silent rate extrapolation, state clipping, or guard widening.
6. Conditional inventory metadata distinguishes observation/BBN/REC; no hidden abundance or ionic IC. Fixed-nb normalization includes 2nD.
7. Do not wire the legacy projector around its rejection, or activate D in production until the common extended network/transport/EOS solver owns all D electron, photon, binding and thermal terms.

No old tests or scientific production runs were executed for this note. New standalone code/test receipts belong to the lower-tier implementation worker, not this research receipt.

## 7. Research-loop record and next action

R1 scope fixed to first atomic D extension; R2 SciSpace+Exa search and actual original code/paper/table reads; R3 assumptions recorded above; R4 H-equality model selected; R5 common event/RHS/normalization derived; R6 new Wolfram symbolic/dimensional checks observed; R7 actual source-byte equality and numeric table transcription observed (no new physical trajectory); R8 scoped model choice frozen; R9 concrete implementation/tests supplied; R10 this MD/JSON/provenance records next native-provider unit. Earlier Savin/CX calculations and seven passing tests are reused, not replayed.

Next action: lower-tier worker implements the selected standalone provider and targeted tests; root reviews the changed seam. Then connect it to the isotope-native coupled solver with a declared conditional inventory and source contract. No new permission loop is required for those already authorized tasks.

