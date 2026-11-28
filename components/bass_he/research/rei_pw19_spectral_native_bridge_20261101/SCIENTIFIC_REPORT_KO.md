# BASS_HE → REI Bianchi IGM | Original PW19 spectral H/He source donor on accepted REI tick160

2026-11-01 | One physical donor unit, not one new canonical REI DAG node. **EXPLORATORY SOURCE-CONDITIONAL, PRODUCTION HOLD**.

## 1. Exact question and prior evidence

Does an actually published frequency-resolved PW19 UV background provide a nonnegative H I/He I/He II photoionization-plus-heat *donor* which can be evaluated on the exact original REI 46,080-cell accepted tick160 neutral inventory at z=5.95? Can the resulting 6 physical moments be represented **without changing the original REI four-group absorber allocation/heat coefficients**, by reweighting only its photon currents? Preserve the source owner and do not start another cosmological IVP.

Original BASS_HE parent PR #146 HEAD `b3b4d95e93999e86a26a3c9719adb739d5865ce4`. REI original source array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01` (accepted `160/131072`), native 4-group photon artifact SHA256 `4f332c7a9c21f93dcfadb0d7e4e40ef4ec7ec7f150f6d4b8b39f309560155e17`. Reuses exactly the source-pinned 46,080-site neutral counts in BASS_HE PR #142, and the original fixed four-group allocation from PR #143, not the unaccepted F05 tick161.

Latest central progress: original owner PR #354 true three-shape 46k shadow gate PASS; PR #355 proves 3-moment coupling/conditional continuum representation; PR #356 source-scoped V2 acceptance **does not admit official tick161**. CENTRAL 28/88, WORKING 33/88, PHYSICAL-FAST 4/7, BASS_HE PHYSICAL 14/18. These are reported owning-ledger counts, not self-incremented from this source packet.

## 2. Published physical inputs, units and domain

- Original PW19 metagalactic UVB spectrum as **reformatted** by Taira, Kopenhafer & O'Shea (2025), DOI https://doi.org/10.5281/zenodo.15367103 ; archived CC0 v1.0.0 source ZIP `source_original_v1.zip`, SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`. Two exactly pinned 626-point energy spectra at z=5.807 and 6.141. This is a **public released background**, not an observational local source. Published transformation code defines `I(E)=4*pi*nu*J_nu`, energy-integrated per `d ln E`, in erg cm^-2 s^-1.
- Atomic cross sections: Verner, Ferland, Korista & Yakovlev (1996), ApJ 465, 487, https://www.pa.uky.edu/~verner/photo.html ; original author Table 1 `photo.dat` first three rows, thresholds 13.60,24.59,54.42 eV and upper fit support 50,000 eV. Parameters copied **exactly** from these original three rows (not inferred from D1 effective rates). Physical ionization potentials are distinct: 13.598434599702,24.587389011,54.41776 eV. One eV = 1.602176634e-12 erg.
- Accepted native HI/HeI/HeII **neutral nuclei counts** are from the original 46,080-cell tick160 source at the same original z=5.95: 6.797721760048389e62, 4.099344954291012e61, and 4.350710840439974e65. Native group photon projection, original 12-row excess-energy table, state array identity and source JSON are validated against frozen Git SHA/blob by the unchanged `source_cone_verifier.py`.
- Spectral source interpolation at z=5.95: log-intensity and linear-intensity variants; one exactly zero sample at 48.355849560166504 eV is preserved as zero in both. Spatially uniform, isotropic UVB in the chosen gas orthonormal tetrad is an explicitly **counterfactual external boundary assumption**. No source emissivity, direction-dependent radiance, cosmological boundary history, or local attenuation is invented.

## 3. Derived continuum-to-group map

Let `I(E)=4*pi*nu*Jnu` for isotropic radiation, with `E` in eV and `eps=1.602176634e-12 erg/eV`. For each species s (HI, HeI, HeII) and spectral band g,

`Gamma_sg = integral_g [I(E)*sigma_s(E)/(eps*E)] d ln E` [s^-1],

`H_sg = integral_g I(E)*sigma_s(E)*[1-chi_s/E] d ln E` [erg neutral^-1 s^-1],

`n_gamma_g^proper = (1/c) integral_g [I(E)/(eps*E)] d ln E` [cm^-3],

`sigma_eff_sg = Gamma_sg/(c*n_gamma_g)` [cm^2], and `E_excess_sg = H_sg/(Gamma_sg*eps)` [eV/event] when Gamma>0.

With original accepted neutral counts `N_s`, `P_sg=N_s*Gamma_sg` [events/s], `Q_sg=N_s*H_sg` [erg/s]. Exact photoevent energy identity:

`sum_sg P_sg*(chi_s+E_excess_sg)*eps = sum_sg [P_sg*chi_s*eps + Q_sg]`.

This is photoionization-only bookkeeping. It does **not** determine net gas heating after recombination/collisional/OTS transport, and is not a claim of photon conservation in the spatially finite native box unless a source/emissivity, boundary flux and optical-depth history are supplied.

The physical bands are **new threshold-resolved donor bands**, not the original REI G1/G2a/G2b/G3 group definitions:
A=13.60–24.59 eV (HI only), B=24.59–54.42 eV (HI+HeI), C=54.42–50,000 eV (HI+HeI+HeII). No original group ownership mutation.

## 4. Original-source physical numerical output (z=5.95)

| Quantity | Log intensity z-interpolation | Linear intensity z-interpolation |
|---|---:|---:|
| All H/He photoionizations [s^-1] | 4.6449651691447255e50 | 4.659223437826395e50 |
| Sum of excess photoheating [erg/s] | 3.193418253311335e39 | 3.2078432302173995e39 |
| HeI/HI **event** ratio at exact tick160 neutral counts | 0.029994201463001136 | 0.030035408209732207 |
| Native fixed-current-only min HeI/HI ratio | 0.695234932510958 | 0.695234932510958 |
| Positive-current rate-pair normalized minimax lower bound | 0.9172835175590777 | 0.9171745857416796 |

For the log-intensity case, separate species photoevents [s^-1] are approximately HI 4.46189910e50, HeI 1.33831101e49, HeII 4.92349659e48; excess heat [erg/s] approximately HI 2.73417e39, HeI 1.2143e38, HeII 3.3782e38. Original HI-only energy band supplies ~93.3% of HI photoionization in this particular spectral donor.

**Key constructive numerical result:** the original four-group fixed absorber shares obey `P_HeI >= r P_HI` for all nonnegative native currents, where `r=min_g(p_HeI,g/p_HI,g)=0.695234932510958` over supported HI groups. The PW19 frequency-resolved donor requires `P_HeI/P_HI≈0.0300`. This **specific current-only native interface** therefore cannot reproduce even the two rate moments. In addition its HI per-event native excess-energy cone begins at ~31.26 eV while the donor mean is ~3.825 eV. These are quantitative conditional incompatibilities, NOT a universal no-go on PW19, reionization, or other source/opacity groupings.

The donor is *closer to the missing source data* than the previous P19 D1 six effective rates: actual `Jnu`, fit cross sections and candidate group extinction/thermal coefficients are all numerically available. The **still missing central owner** is a physically admitted, causal local source-plus-opacity/transport relationship (position, direction, epoch and proper-frame clock) mapping donor moments to the original/revised REI photon state. Neither arbitrary group-current replacement nor a fabricated G3 current is permitted.

## 5. Actual verification and adversarial classification

- Source ZIP exact byte SHA and first three Verner Table 1 parameter rows; original native REI accepted-state SHA, group shares, frozen tables and 46,080 count all pinned.
- `spectral_physics.py`: original 626-sample frequency grids, zero-preserving interpolation, physical thresholds, and two 8-vs-16-substep Simpson quadratures. The initial implementation caught an **actual threshold boundary support defect** near 24.59 eV, repaired by explicitly keeping inactive species out of the preceding band, without changing original input or loosening physical policy.
- `independent_audit.py`: separate 120,000-subinterval uniform-dlnE midpoint integration (same author), maximum rate/heat relative disagreement 2.911121840879893e-5 for HeI heating and smaller for other channels; no independent-author referee.
- `audit_native_independent.py`: separate group Fraction dual plus independently computed 3-species native-matter counts, total energy identity; max HeI heat disagreement ~2.02513e-5; verdict `PASS_SAME_AUTHOR_DIFFERENT_SPECTRAL_MIDPOINT_AND_NATIVE_DUAL`.
- `tests/test_native_bridge.py`: 14/14 normal Python and 14/14 `python -O` PASS, including tampered spectral SHA, original group support mismatch, energy identities and 18-row unit contract.
- Wolfram exact algebra gave absorbed photon energy = binding increment + excess heat (residual zero) and a positive fixed-group dual deficit; one initial symbolic evaluation reported unassigned-symbol messages, so this is symbolic algebra not source-provenance or executable RT verification.
- No new original cosmological IVP, no native solver/source/accepted-history edit, no fit extrapolation beyond 50 keV, no invented observed CMB/IGM photons. Three science shapes or 18 derived donor rows do not count as 18 independent physical realizations.

## 6. Drift watchdog, actual DAG and next owner action

**Verdict:** single bounded source-donor bridge is constructive but does not itself advance the owning REI accepted canonical graph. Freeze adjacent P19 source-only rate atlases now. Necessary next contribution is **REI-owned RUX03/04 source scenario binding**: choose and verify a true local photon emissivity/incident spectrum as a function of proper spacetime position, tetrad direction and epoch, plus absorber fractions, OTS/thermal energy ownership and proper/comoving conversions; *then* match a FLRW and finite-shear Bianchi-I physical integration. Original REI F05 V2 tick161 official acceptance and exact predecessor parity remain a separate original-owner blocker.

CANONICAL=28/88_REPORTED; WORKING=33/88_REPORTED; FAST=4/7_REPORTED; BASS_HE=14/18_REPORTED; PHYSICAL_DELTA=0; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; NO_NEW_IVP=true; AUTO_NEXT=false. Source candidate remains `NONAUTHORITATIVE`.

## 7. Reproduce one physical unit

From this directory: `python3 spectral_physics.py`, `python3 independent_audit.py`, `python3 spectral_native_bridge.py`, `python3 tests/test_native_bridge.py`, `python3 -O tests/test_native_bridge.py`, and `python3 audit_native_independent.py`. Scripts use standard Python library only, original frozen BASS_HE repository source files, and bundled source ZIP. Rerunning generates exactly one physical JSON, one 18-row CSV and two same-author auditor records, not a new accepted state.

Primary external literature: Taira et al. 2025 https://doi.org/10.3847/2515-5172/adddae ; Puchwein et al. 2019 https://doi.org/10.1093/mnras/stz222 §3.1 neutral-weighted effective vs spectral/background rates; Verner et al. 1996 https://doi.org/10.1086/177435 ; Friedrich et al. 2012 https://doi.org/10.1111/j.1365-2966.2012.20449.x for coupled H/He OTS photon and heating ownership.
