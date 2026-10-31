# REI F4 | BASS193 CCC6–Kim92 competing first-event + pre-event Coulomb energy

Date: 2026-10-31. Source-conditioned Physical Fast exploratory result. This is **one** bounded theoretical/coding research execution, not 20 distinct experiments. Scope and protected owners: source PR #311 HEAD `63052797e382b438ef375e8389f539118a7e2a0c`; sibling PR #310 HEAD `6a9343f49da8287616c338de5f853bb1a0b44b5d` and PR #309 HEAD `701add5f6536d091350650f2b6649cded0c0de06` are read-only. Original BASS21 native source/REI17 F/J untouched. No new cosmological IVP, no force push, no merge, no production source switch.

## Primary source and original data

- **Physical source trajectory:** frozen BASS193 original 193 saved chemistry/electron states, first-flight 192 arrival intervals, 3,840 original source first-photoelectron count/kinetic band moments. Four parent input CSVs are byte SHA-256-locked; see `inputs/` and `code/ccc_snapshot_311.py`. Baseline source first photoelectron number `4.374110632809567e-12` per original baryon; primary kinetic `6.749242464433258e-11 eV` per original baryon. Original conditional Li II singlet bound is **not** an observed positive production abundance.
- **Electronic atomic collision physics:** Curtin convergent close-coupling (CCC) H I and He I ground-state scattering, from the pinned independent public EXHALE copy commit `7388232fac2c3cdadad613515006de008360f1ab`, whose original original-author data are at https://atom.curtin.edu.au/ccc-db/index.html. Six channels are H I total ionization, H I `1s→2p`, H I `1s→2s`, He I total ionization, He I `1¹S→2¹P`, He I `1¹S→2³S`. EXHALE preserves original Git blobs `d6bdc1c8`, `e6400e56`, `08e7ed4c`, `ba9e10df`, `f19fe1f6`, `5a4567c3` (full SHAs in input snapshot). H I source units Bohr-area `a0²`, He I source cm². Existing PR311 uses adaptive sampling with specified 0.5% *absolute* error relative to each channel's peak; this is not a uniform relative error at low cross sections. **No CCC He II target channel** is present. The raw full original CCC archives were not independently byte-compared to the EXHALE mirror in this run.
- **Independent ionization comparison:** Y.-K. Kim (1992), *Compact Fitting Formulas for Electron-Impact Cross Sections*, J. Res. NIST **97**, 689–692, DOI `10.6028/jres.097.032`, Eq. (2), Table 1; 
  `σ(E)=10⁻¹⁶ cm² × [A ln x+(B ln x+C(x−1))/(x+D)]/x`, `x=E/I`, with the fitted H I, He I and He II coefficient sets from original source, as retained in PR310's exact code. `Kim2` uses only H I/He I; `Kim3` adds He II; neither is averaged with CCC data. Grackle k1/k3/k5 are Maxwellian rates and are **not** used as individual fast-electron cross sections.
- **Continuous Coulomb stopping:** Furlanetto & Stoever (2010), *MNRAS* **404**, 1869–1878, DOI `10.1111/j.1365-2966.2010.16401.x`, Coulomb energy-loss expressions at **E≥13.7 eV**, as implemented and verified in parent PR309. All live species densities and `n_e` are read from the **frozen original BASS193** state and proper clock. He III's role is its free-electron contribution to `n_e`, not a fictitious bound-electron impact-ionization channel.

## Exact continuum construction and finite-volume implementation

For a chosen set of independent inelastic channels `a` at a frozen source state, let `νₐ(E,t)=nₐ(t)σₐ(E)vₑ(E)` in s⁻¹. Define `b_C(E,t)=|dE/dt|_ee>0` in eV/s for continuous Coulomb energy loss and energy-space hazard `hₐ(E,t)=νₐ/b_C` in eV⁻¹. With first electron energy `E₀` and low-energy cutoff `E_c=13.7 eV`, the *no-first-discrete-event* survival is

`S(E;E₀,t)=exp[-∫_E^E₀ h_tot(ε,t)dε]`, `h_tot=Σₐhₐ`,

and each **first** inelastic channel probability is `Pₐ(E₀,t)=∫_(Ec)^E₀ hₐ(E,t) S(E;E₀,t)dE`. These formulas do not propagate secondaries, scattering angular momentum or background chemistry.

The production form uses energy bins of the genuine published-data sigma interpolation. In cell `[E_i,E_(i+1)]`, set `Δτₐ=∫hₐdE` by per-cell Simpson quadrature and approximate `hₐ` by its cell average. With `τ=ΣΔτₐ`, `s=exp(-τ)`, `wₐ=Δτₐ/τ`, `q=1-s`, first-hit recursion is

`Pₐ(E_(i+1))=s Pₐ(E_i)+q wₐ`, `S(E_(i+1))=sS(E_i)`.

Writing `Qₐ=E[ E_event 1_{first event in a} ]`, the same cell computes a conditional collision energy and updates `Qₐ`. The expected Coulomb kinetic-energy loss **before** first collision or reaching `E_c` satisfies

`L_C(E_(i+1))=s L_C(E_i)+(E_(i+1)-E_i) (1-e^(-τ))/τ`.

All quantities obey the exact cell-model ledger

`E₀ = L_C(E₀)+ΣₐQₐ(E₀)+E_c S(E₀)`;

`ΣₐPₐ(E₀)+S(E₀)=1`.

These identities are **exact for the piecewise-constant-per-cell hazard transport**, not a proof of continuum solver error or of complete electron-degradation energy conservation. The original Boltzmann/Fokker–Planck Coulomb and stochastic ionization secondaries are not fully solved.

For each actual 3,840 source band, original electron count `N` and energy moment `M` are conserved. We evaluate collocation at `Ebar=M/N` and separate marginal lower/upper values from the one-moment two-point extremizers over each band's exact physical electron-energy support. The enclosures are mathematical bounds for the **piecewise-linearly interpolated computed first-event response curve**, not for raw CCC data uncertainty, missing H/He lines or cosmological source amplitude.

## Physical numerical result, actually computed

At 193 original BASS plasma states we calculated `16,598` independent state × initial energy first-event responses. At 192 original first-flight arrival intervals we generated `3,840` bandwise source-conditioned first-event responses and `192` arrival summaries. Source number and kinetic energy equal the unmodified parent to machine accuracy.

**Source-weighted integrated first-event model, counts per original baryon:**

| Model/channel | Lower | Mean-E collocation | Upper |
|---|---:|---:|---:|
| CCC6 first event total | 5.398802838e-15 | 5.409810215e-15 | 6.500353338e-15 |
| CCC6 H I ionization first | 1.840672755e-15 | 1.844227426e-15 | 2.408259460e-15 |
| CCC6 He I ionization first | 8.635377859e-18 | 8.640208453e-18 | 3.030660452e-17 |
| CCC6 H I n=2 excitation first | 3.532768256e-15 | 3.541622680e-15 | 4.039143875e-15 |
| CCC6 He I excitation first | 1.530931469e-17 | 1.531990053e-17 | 2.402279449e-17 |
| CCC2 ionization-only (no excitation competition) | 1.878229613e-15 | 1.881129626e-15 | 2.491732640e-15 |
| Kim2 H I+He I ionization-only | 1.882198002e-15 | 1.885071999e-15 | 2.515267729e-15 |
| Kim3 H I+He I+He II ionization-only | 1.882198002e-15 | 1.885071999e-15 | 2.515267729e-15 |

**CCC6 expected energy budget**, source integrated (eV/original baryon): continuous pre-event Coulomb transfer `[2.288843344e-11, 2.299254056e-11]`; at source mean `2.293087507e-11`. Kinetic energy carried by the primary electron at its first event (only this event, not ionization binding or secondaries) source mean `1.276013059e-13`. Residual kinetic energy at the `13.7 eV` cutoff in surviving electrons is **unresolved**, not claimed as deposited heat.

At monochromatic initial energy `E₀=60.922559447552 eV`, the direct source BASS plasma `z=20` yields `P_CCC6≈1`, with H I excitation fraction `≈0.5161`, H I ionization `≈0.4616`; at `z≈9.978`, `P_CCC6≈0.102302`, Kim2 ion-only `≈0.047883`; at `z=2`, `P_CCC6=7.75303e-8`, Kim3 `3.54979e-8`. Different model outcomes MUST NOT be summed. These are response functions at fixed source state, not global universe ionization fractions.

**Competition monotonicity lemma:** for the same continuous Coulomb stopping and original source, adding nonnegative first-event hazards cannot decrease the **total** probability of a first event (`1−exp[−∫h_tot]`), but can decrease the probability that any **specified channel** is the first one. This is tested with a strict two-channel counterexample. Neither claim makes this 6-channel model the full cascade.

**Science consequence:** on this exact set of original source trajectories and selected CCC channels, HI `n=2` excitation alone is a larger first-event count than H I ionization. Treating `first collision = first ionization` therefore misses a leading process. CCC2 and Kim2 ionization-only are numerically close for the same source, but that comparison does not imply source-operator identity; the ionization competition in CCC6 changes H I event counts.

## Tests, hostile self-audit, and remaining gates

- Physics tests: `31/31 PASS`; analytic constant-rate hazard, large and zero hazard, energy balance, shell thresholds, He III electron bath and source byte locks; seeded 300 random point-pair distributions for moment bounds. **Same-author verification**, not a distinct blind referee.
- Cell energy ledger `max abs residual=5.684e-13 eV`, probability normalization `max abs=2.054e-14`; original source count and energy identities preserved. NIST original benchmark from PR310 at `z=2` and `E0=60.92256` agrees within relative `~2.7e-5` (different grids, same physical equations).
- Three energy grids (300/600/1200 uniform nodes plus published CCC knots): source-weighted CCC6 first-event mean differs by `≤1.1e-5` relative between 300 and 600, `≤3.0e-6` between 600 and 1200. He I smaller source event exhibits slightly higher relative grid sensitivity (<6.5e-5 between 300 and 600). This is **numerical convergence**, not overall physical uncertainty.
- One diagnosed caveat: hidden cutoff: E<13.7 eV still allows H I 2s/2p excitation but not included by FS2010 Coulomb formula; the remaining 13.7 eV per survivor and sub-threshold source energy cannot be declared entirely heat. Missing CCC H I/He I excited states, CCC He II cross section, elastic momentum-transfer and post-event secondaries mean no full cascade or REI17 production.
- Original FS2010 single-x_i helium chemical manifold matches 0/192 source states, hence the old FS2010 full heat fraction cannot be silently imposed on this result.

**This unit remains source-scoped exploratory auxiliary 1/1**. Working DAG `33/88`; central `28/88`; physical F4 fast `4/7`; canonical delta 0; F4 partial, L4 not ready, production HOLD, no new IVPs, no merge, no force push, no auto-next node. No unpublished measurements or correspondent reply is a blocker. Native subagents NOT_RUN due current callable tool inventory, browser Chrome tabs unavailable in this chat origin; primary GitHub and published paper tools used directly.

Next science: extend E<13.7 eV stopping with physically justified e-e thermalization, add CCC He II and all relevant H/He excitation and differential ionization energy sharing, then include exact native BASS21↔REI17 energy/particle source replacement, independent reviewer gate before canonical DAG promotion.
