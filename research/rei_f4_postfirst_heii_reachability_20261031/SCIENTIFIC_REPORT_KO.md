# REI F4 Physical Fast: BASS193 source-owned CCC6 post-first energy and He II reachability

2026-10-31, independently constructed bounded new unit

## Authority and immutable baseline

- `PROJECT=cosmosapjw-quantum/rei_bianchi`.
- READ live current PR #313 `47f34ccb68f02262f40cd3dfd198aa97abd35183`; protected parent PR #311 `63052797e382b438ef375e8389f539118a7e2a0c`; PR #312 `ddf0a55b2a5db74e4678aa684444e9d72d4986ab` READ-ONLY. New work does not merge, reset a budget, add IVPs or alter any previous source authority.
- Original source master `REI_F4_CCC6_FIRST_EVENT_20261031_FULL.zip` 3,813,471 bytes, SHA-256 `4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4`, securely downloaded from previously private Google Drive ID `1UfsISS-XJuSnig3vmXdtfdSa_3T5cfAW`. Source-full ZIP is REQUIRED to re-run the new science; it is excluded from the public release.
- Original BASS193: 193 distinct frozen background states, 192 first-photoelectron arrivals, 3840 first absorber × kinetic-energy bands, full 21-species electron bath `ne=nb q^T Y`, original clock and conditional Li II 2E1 primary photon source. The source is not an observed Li II signal lower bound.
- Original atomic numerical six-channel owner: *reduced and resampled* EXHALE Git commit `7388232fac2c3cdadad613515006de008360f1ab`, physical authority Curtin CCC. Original Curtin author ZIP is not byte-identical to the reduced EXHALE snapshot and was NOT locally obtained this run.
- External primary: official Curtin atomic CCC database `https://atom.curtin.edu.au/CCC-WWW/index.html` lists complete May 2026 He II `e-HeII_XSEC_LS.zip` and H I/He I tables. He II original file is publicly accessible on that page but not byte-restored this run. This new calculation does *not* insert a fabricated He II CCC cross section. Original He II CCC reference: Bray et al., J. Phys. B 26 L831 (1993), DOI `10.1088/0953-4075/26/23/006`.
- NIST Atomic Spectra Database 4He II ground-state ionization energy 54.417760 eV; H I ionization energy 13.598434599702 eV. He II `1s->n=2/3` hydrogenic thresholds estimated as `E_ion(1-1/n^2)`, neglecting fine splitting and recoil. Dimensional convention: energies eV, rates s^-1, densities cm^-3, electrons and energy normalized per original baryon.

## First-selected-event postcollision energy and charge

Retain the original six CCC inelastic channels and FS2010 electron-electron Coulomb stopping above `Ec=13.7 eV` on a fixed BASS background. Denote `b(E)=-dE/dt>0`, `nu_a(E)=n_a sigma_a(E) sqrt(2 E eV_to_erg/m_e)`, `h_a(E)=nu_a(E)/b(E) [1/eV]` and `h=sum_a h_a`. For incoming energy `E0>=Ec`, define

```
S(E | E0) = exp[-integral_E^E0 h(u) du]
P_a(E0)  = integral_Ec^E0 h_a(E) S(E|E0) dE
G_a(E0)  = integral_Ec^E0 E h_a(E) S(E|E0) dE
C(E0)    = E0 - sum_a G_a(E0) - Ec S(Ec|E0)
Q(E0)    = sum_a chi_a P_a(E0)
Kout(E0) = sum_a (G_a(E0) - chi_a P_a(E0))
Kcut(E0) = Ec S(Ec|E0)
C + Q + Kout + Kcut = E0.
```

`G_a` uses an additional energy moment; it is not fixed by event probability alone. On each discrete energy cell we hold channel fraction of the *integrated* hazard fixed as in original PR313 and calculate conditional event energy with `f(d)=1/d-1/expm1(d)`. Its small-hazard expansion `1/2-d/12+d^3/720-d^5/30240` was independently verified by Wolfram Language. `P_a` and `G_a` are propagated with the same cell survival. Their final closure is algebraic for the defined partial model. Source spectrum is unknown within stored original band: use exactly the parent piecewise-linear response and convex/concave moment envelopes for mass `N`, mean `M/N` and original energy support. The *mean* ledger is the representative moment-collocation, not the unknown source's exact physical energy decomposition. No joint extrema across the four energy components are implied.

At `E0<Ec`, this **scoped** model puts all incoming energy into unresolved `Kcut=E0`, and does NOT identify it as gas heat. In ionization the output `Kout` is the sum of outgoing electronic kinetic energies; the distribution between primary and secondary electrons is unavailable from total cross section alone. No energy resolved cascade, radiative cascade, electron temperature ODE, excited state occupation, or optical depth solved.

H I ionization binding used by old parent threshold ledger was 13.6058 eV. New energy accounting corrects it to NIST 13.598434599702 eV, without altering the original CCC cross-section, selected event probabilities, or protected parent. Shift in mean ionization binding energy `-1.3583400841738046e-17 eV/b`.

## New actual scientific results (source mean at 2100 energy-grid nodes plus atomic knots)

| Computed quantity | eV / original baryon |
|---|---:|
| Original photoelectron kinetic input | 6.749242464433258e-11 |
| Pre-first continuous Coulomb transfer | 2.293087536858580e-11 |
| Atomic binding/excitation thresholds in selected first CCC6 events | 6.174257050944192e-14 |
| Outgoing electron aggregate kinetic after selected first CCC6 event | 6.585818335407941e-14 |
| Residual 13.7-eV-cutoff electron kinetic without a selected event | 4.443394852188326e-11 |

Source-mean closed energy ledger roundoff residual `0.0 eV/b`; max mono residual `7.105e-15 eV`, max source-band mean residual `1.421e-14 eV`. First selected-ionization electron and ion production `1.852857622277025e-15 / baryon` and `Delta n_e=Delta n_HII+Delta n_HeII` for those six channels; aggregate charge residual `8.1391e-32 /b`.

The original PR #312's *related* pre-first Coulomb value was `2.293087507e-11 eV/b`, our relative difference ~`1.3e-8`, independent energy moment method. No first-event novelty over #312 is claimed.

## He II channel reachability on ORIGINAL source support, not a cross-section result

The original Li II 2E1 photon pair has max photon energy `Epair=60.922559447552 eV`. Primary electron kinetic upper support from a first absorber X is `Epair-chi_X`. In frozen source bands, H I first absorber has max ~47.324 eV, He I max ~36.335 eV, He II max ~6.505 eV, Li I max ~55.533 eV. Therefore, for primary electrons, He II 1s->n=2 excitation at about 40.81332 eV may occur from H I and Li I first absorber, but n=3 threshold 48.37134 eV and ionization threshold 54.41776 eV can be reached only by Li I first-absorber electrons. This is *kinematic source support*, not a statement that the He II collision happens.

For source band energy support `[l,u]`, mass `N`, mean `m=M/N`, and threshold `t` inside `(l,u)`, the mathematically sharp lower and upper **possible initial-energy-above-threshold mass** are

```
N_lower = N * max(0, (m-t)/(u-t))
N_upper = N * min(1, (m-l)/(t-l)).
```

Boundary/tie equality only modifies whether an endpoint atom counts; for physical σ(t)=0 it does not create a finite collision rate. For `u<=t`, both are zero; for `l>t`, both are N. These bounds do not use any fabricated He II cross-section or select an arbitrary sub-band spectrum.

| He II channel | threshold (eV) | source eligible lower /b | source eligible upper /b |
|---|---:|---:|---:|
| 1s -> n=2 | 40.8133200 (hydrogenic) | 6.9795313e-26 | 3.1712127569e-13 |
| 1s -> n=3 | 48.3713422 (hydrogenic) | 6.9795313e-26 | 4.7493893612e-23 |
| ionization | 54.417760 (NIST) | 2.2477742891e-26 | 6.9795312998e-26 |

The actual original He II target number density spans `7.6530609e-17` through `1.1890652e-05 cm^-3`, and the He II fractional abundance is not uniformly small. The large *upper bound* for n=2 is a kinematic capacity, not an event yield; He II cross-section times target density must be evaluated from the author ZIP to get such a yield. Note that after a first CCC6 collision the leftover kinetic energy is never *greater* than the incoming primary electron kinetic energy, so threshold exclusion for these **secondary electrons from the same selected event** persists. Photons or other external energetic particles would be a distinct source.

## Numerics, tests, and adversarial check

- Both source-inclusive original master ZIP and original PR311 parent source files passed source-byte checks. Re-executed original PR313 32/32 tests, 15/15 output hashes and 79/79 manifest hashes.
- New source-provenance, energy/charge, positive probability, threshold support, exact 300 random two-point moment measures, quantum threshold, and independent piecewise-linear hazard Gauss-Legendre tests: 24/24 passed at local scope. No distinct-author blind-referee available, native subagent NOT_RUN. Original #312 is an independent sibling numerical comparison, not an independent review of this new code.
- The first independent endpoint-trapezoid quadrature spuriously produced P>1 by ~0.00112 in an optically thick representative case. Replaced verifier, not physics, with within-cell 48-point Gauss-Legendre quadrature using exact survival for piecewise linear h. The corrected direct first-event normalisation agrees within ~`5.3e-15` for the thick example; energy moment relative deviations below `5e-8` in five representative epochs. This was a **numerical checker failure**, diagnosed and repaired, not a CCC collision model failure.
- Recomputed full source at energy grid 900 and 2100 (plus all original atomic knots); relative differences for mean Coulomb `4.99e-9`, atomic threshold `2.23e-6`, postevent electrons `1.95e-6`, cutoff residual `3.42e-9`. He II source reachability bounds exactly unchanged (the bounds are source-moment algebraic). 2100-node run is authoritative new scope.
- Physical energy closure uses an incomplete **partial** six-channel first-event model, not full physical plasma energy closure. Parent outputs and Git protected ancestors unchanged; new external He II σ(E) numeric archive `NOT_FETCHED`, He II collision probabilities `NOT_COMPUTED`. Physical claim `SOURCE_CONDITIONAL` only.

## Positive next research action

Read the public official Curtin author archives from `https://atom.curtin.edu.au/CCC-WWW/index.html`: select the He II `e-HeII_XSEC_LS.zip` May 2026 plus full H I `e-H_XSEC_LS.zip` and He I `e-He_sig.zip` (2026 versions), preserve original source byte SHA and channel/energy/units/threshold metadata, compare to existing reduced EXHALE tables, add He II `1s->n=2` and additional H/He n>=3 excitation/elastic then integrate competing physical first events and post-event daughter spectrum. Keep NIST ionization energy distinct from an author table's interpolated σ threshold. Published rate libraries such as CHIANTI hold Maxwellian averaged effective collision strengths, NOT the required monoenergetic σ(E); never equate them. With original CCC samples, propagate new source into complete native REI17 F/J *replacement*, not additive source, in a separately authorized production node. Unpublished Li measurements, author replies and cosmological IVPs are not prerequisites for this bounded path.

**DAG remains Working `33/88`, Central `28/88`, Physical Fast `4/7`, canonical delta `0`; F4 PARTIAL, L4 false, production HOLD, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.**
