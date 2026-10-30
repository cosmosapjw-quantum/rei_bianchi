# REI F4 physical-fast: PR299 hybrid source × PR300 FS2010 low-energy electron crosswalk

Date: 2026-10-31 (Asia/Seoul). One bounded theory-and-code scientific unit, no IVP. Owner: `cosmosapjw-quantum/rei_bianchi`. Baseline PR #299 exact HEAD `98b355a352e7aa45c65296e8a986b7de27aafd67`; sibling PR #300 exact HEAD `0e9024f92682bc3b7a0080cc86855cbddca8b0d9`. Source #298 `914eae63681e55cf013208d3fd5357f38fc2fd69`, #297 `0f41c8f0d3ddc7f8af67765f09cd37ae885768bf`. These are distinct origin owners, not implicitly merged.

## Physical construction, source ownership

Inputs are exactly FOUR primary-archive CSV byte identities recorded in `SOURCE_LOCK.json`, including the actual PR297 CSV inside the PR300 parent archive. The 193 BASS21 saved epochs with 192 causal arrival intervals belong to a single original frozen BASS background. PR299 gives the un-evolved H/He hybrid source-substitution tangency defect and binding-energy port; PR300 gives 30 selected Li II singlet source-emission epochs and the FS2010 subthreshold first-generation primary-electron energy. PR297 gives **all-epoch** conditional causal photoelectron energy, counts, proper intervals. PR298 supplies native BASS21 per-baryon heat capacity and background H,T,elapsed seconds.

The source partition in each arrival interval i is

- `E_all,i`: PR297 all-epoch all-species primary photoelectron kinetic energy [eV/baryon].
- `E_sel,i`: PR300 all primary kinetic energy for the 30 selected emission epochs, both low and high energy [eV/baryon].
- `E_low,i`: PR300 energy among those selected first-generation electrons with `E_e < 10.2 eV` [eV/baryon].
- `E_miss,i = E_all,i - E_sel,i >= 0`, **discrete source support only** (not an inferred spectrum).

Thus the energy that can be *initially* in sub-10.2-eV electrons is at least `E_low,i` and at most `E_low,i + E_miss,i`, if an arbitrary proportion of unselected electron energy could lie beneath the cutoff. The 30 **selected** emission epochs have separate above-cutoff electron energy `E_sel,i-E_low,i`; they can produce later secondaries/heat and are **NOT included** in this first-generation upper. It would be **false** to call this upper a bound on all future thermal heating. The much broader total **primary-electron energy budget** `E_all,i` is the all-primary thermal ceiling under energy conservation, provided no extra sources are added. Neither quantity is a physical deposited-heat prediction.

Furlanetto & Stoever (2010), *MNRAS* **404**, 1869-1878, DOI [10.1111/j.1365-2966.2010.16401.x](https://doi.org/10.1111/j.1365-2966.2010.16401.x), treats below-10.2-eV electrons as terminal kinetic heat in its collision model, and warns strongly against applying its ~3-keV limiting deposition fractions to low-energy electrons. Actual deposition of `E_e >= 10.2 eV` requires energy/ionization-fraction tables and energy accounting through daughter electrons and photons.

Frozen conversion (cgs, original-metric convention `(-,+,+,+)`; keep c, k_B, hbar when applicable):

```
x_i = ln a_i
Δt_i = t_i+1 - t_i = ∫[x_i,x_i+1] dx/H(x)        (s)
n_b,mid = sqrt(n_b,i n_b,i+1)                     (cm^-3)
C_v,b,mid = midpoint mean of (C_v,21/n_b)        (erg K^-1 baryon^-1)
ε_eV = 1.602176634e-12 erg/eV                   (exact)
Tdot_{E,i} = ε_eV E_i / (C_v,b,mid Δt_i)         (K s^-1)
N_therm/b = C_v,b,mid / (3 k_B/2)                (particles/baryon)
Tdot_{loading,i} = -T_mid/N_therm * (ΔN_e/Δt)   (K s^-1)
```

The electron-loading equation requires a **hypothetical** instantaneous entry of all first-generation H/He photoelectrons into the gas thermal particle pool; no secondary electrons, electron-neutrino or separate thermalization operator is solved. There is no new source ownership contract to add PR300 photon photoionizations to PR299's pre-existing reaction F/J; this document is an **observational/kinematic crosswalk of two frozen source owners**, not a combined kinetic solution. PR299 source replacement cannot be *linearly* combined with PR297 radiative source without photon double-counting and state/IC alignment.

## Numerically checked physical results

Source-grid joins 193/193 original redshift states, 192/192 first-flight arrival intervals. `Δt` archived PR297 versus PR298 saved elapsed-time difference maximum relative mismatch `1.1264835575626943e-14`; midpoint quadrature `max |Hmid Δt / Δx -1|=3.893973292323771e-5`, not zero.

| Quantity | Value | Status |
|---|---:|---|
| selected first-generation low-E photoelectron energy | `8.54068904110878e-12 eV/b` | measured-source kinematic, conditional |
| first-generation low-E + unselected all-E ceiling | `8.87521981091180e-12 eV/b` | conservative only for first-gen component |
| ALL primary photoelectron energy ceiling | `6.749242464433259e-11 eV/b` | cannot apply FS2010 high-energy deposition fractions |
| selected high-E primary energy omitted from narrow upper | `5.861720483342079e-11 eV/b` | explicitly nonzero: forbids whole-heat-upper promotion |
| conditional PR297 H/He primary electron count | `4.374110342256812e-12 /b` | first-flight source only |
| conditional H-secondary count upper incl. missing energy | `2.953299771480339e-12 /b` | energetic ceiling, not rate |
| PR299 signed frozen hybrid electron source exposure | `0.2214528020145159 /b` | `∫ΔF_e dt` on saved trajectory, not evolved Δxe |
| upper first-generation terminal Tdot coefficient | `1.7412091455184073e-23 K/s` | *point source* |
| point-source temperature exposure from narrow upper | `4.9516671941706154e-8 K` | `Σ Tdot Δt` on frozen background only |
| point-source exposure from ALL primary-energy ceiling | `3.750149730799424e-7 K` | broader, still not evolved T |
| signed immediate-electron-loading exposure | `-8.009098732656085e-10 K` | hypothetical instantaneous gas electrons |

Source-scale comparison: `E_firstgen_upper * ε_eV = 1.4219669802656783e-23 erg/b` versus original PR299 *different-owner* signed chemical binding source exposure `5.260417952086776e-12 erg/b`. Ratio is `2.70314449007154e-12`. **This is a scale comparison of distinct operators and cannot justify adding, subtracting or replacing physical sources.**

## Acceptance and independent skeptical checks

1. Byte-source identity of four CSVs checked against parent 298/299/300 originals (PR297 original is nested in PR300 source ZIP); SHA256 enforced at runtime.
2. Source state/arrival z, densities, proper intervals, baryon normalization and H clock match within observed stored-precision limits.
3. Nonnegative 192-element energy decomposition and `E_low <= firstgen_upper <= all_primary`; selected high energy shown explicitly.
4. Derivative-free independent cgs recheck of `Tdot = E*epsilon/(Cv_b*dt)`, positive/negative energy ledger and electron-number coupling.
5. Tampered source SHA and wrong proper-clock negative tests reject their inputs. Half-step `Hdt/dx` is **not** asserted exact.
6. The tests check a conditional source operator, **not** true heating. Same-author adversarial verification only, distinct-author R6/C9 NOT_RUN.

**Scope verdict:** Source-specific auxiliary `1/1_SCOPED` only. Working `33/88`, Central `28/88`, Physical fast `4/7`, canonical delta `0`; F4 PARTIAL, L4 NOT_READY, Production HOLD. NO_MORE_IVPS, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.

**Next genuinely physical node:** state-specific Li I initial-neutral branching; obtain machine-readable FS2010 E×ionized-fraction energy deposition table and valid collision-temperature range; *native* REI17 full F/J plus BASS21 common isotopes, electron bath, H/K proper background, initial conditions and photon source replacement. Do not substitute a static energy budget for self-consistent kinetic evolution, optical depth or CMB.