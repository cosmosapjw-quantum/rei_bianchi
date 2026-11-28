# BASS_HE PR137 | Source-authority 17-channel photonuclear opacity and measured-support coherent pion return

**Exploratory, source-conditional, fixed-background Green-response; not production BBN.** Immutable upstream PR136 at `5c24f0fa2c0de0f0e80edd8bde7266c60b264fde`; add-only subtree in BASS_HE. This calculation is a separate experiment and does **not** alter the official ACROPOLIS source, previously published repo code, nuclear source tables, or an active production simulation.

## Published and first-party source hierarchy

1. **Standard executable model:** Depta, Hufnagel & Schmidt-Hoberg, *ACROPOLIS*, arXiv:2011.06518; first-party `hep-mh/acropolis` v1.3.1 (uploaded source ZIP SHA-256 `1d933f8d53c614d379166ada9319b4188ec45c0b74e065ba790034da41f0d9e1`). Code `acropolis/cascade.py` implements the 3-species gamma, e-, e+ source and collision operators; `acropolis/nucl.py` contains the **17** photonuclear reactions and cross sections in inverse MeV squared (mb-to-MeV^-2 factor `2.56819e-6`).
2. **Original physical nuclear model:** R. H. Cyburt, J. Ellis, B. D. Fields, K. A. Olive, *Updated Nucleosynthesis Constraints on Unstable Relic Particles*, Phys. Rev. D **67**, 103521 (2003), DOI `10.1103/PhysRevD.67.103521`, Appendix A. ACROPOLIS `He4(gamma,n)He3` coefficient is **20.7 mb** instead of the historical Cyburt 17.1 mb; the original code comments explicitly cite EXFOR update in K. Jedamzik, *Phys. Rev. D* **74** 103509 (2006), DOI `10.1103/PhysRevD.74.103509`. This is a published *fitted model*, not verified precision evaluation at E=200–250 MeV.
3. **Primary exclusive coherent channel:** F. Rambo et al., *Nucl. Phys. A* **660** 69–83 (1999), DOI `10.1016/S0375-9474(99)00383-8`, original author Table 1 (measured 4pi-incomplete angular bins), Table 2 (full-cross-section reconstruction, 7% shared systematic). EXFOR M0752019 / M0752002-2005 source-specific at 206,216,229,241 MeV.
4. **Primary inclusive alpha sink:** M. MacCormick et al., *Phys. Rev. C* **55** 1033 (1997), DOI `10.1103/PhysRevC.55.1033`. Their Eq. (1) **already counts neutral-pion events**. Published total photoabsorption values above 200 MeV are inclusive **nuclear** absorption, not QED pair production and not a separate loss to be added to coherent pion absorption. Source EXFOR M0520002 (M0546002 is a duplicate release of the same experiment).
5. **Initial composition:** the pinned ACROPOLIS default `acropolis/data/sm.tar.gz` is coupled to an AlterBBN 2.2 (`failsafe=12`) source, as documented in ACROPOLIS first-party `acropolis/data/INFO`. Per-baryon Y_A, gamma/e± rates follow the original implementation, not inferred from later BASS/REI branches.
6. **Alternative evaluated library:** JENDL/PD-2016 and JENDL/PD-2016.1 are useful *independent* evaluations. Published JENDL/PD-2016 only reaches 140 MeV; 2016.1 extends many heavier nuclides to 200 MeV, not a blanket verified coverage of 241 MeV alpha. It is not silently substituted for the ACROPOLIS/Cyburt model or MacCormick primary data.

## Mathematics and implemented physics

Metric `(-,+,+,+)`; local FLRW CMB `T_gamma(z)=T_0(1+z)`; physical units restored when interpreting rates. The code uses ACROPOLIS *native* c=hbar=k_B=1 cross-section/rate conventions internally (`mb -> MeV^-2`), with explicit conversion provenance; no arbitrary factors of c are multiplied into these natural-unit rates.

For species X=gamma,e-,e+ and energy E, ACROPOLIS solves stationary nonthermal cascade

```
G_X(E) F_X(E) = S_X(E) + sum_X' integral_E^Emax dE' K_X<-X'(E,E') F_X'(E')
```

New nuclear photon loss `Gamma_nuc(E,z)` is the **sum of all 17 published ACROPOLIS target-specific photodisintegrations**. For `204 <= E <= min(241,Emax)` the alpha part `sum_{r=6..9} n_alpha sigma_r^Cyburt` is **replaced** by `n_alpha sigma_abs^MacCormick(E)`. Outside this measured inclusive interval the published 17-channel model remains. Replace ≠ add; the inclusive total already contains pion events.

New measured-support coherent-pion photon gain is

```
K_gamma<-gamma^pi(E,E') = n_alpha sigma_pi0^Rambo(E') * dN_gamma(E|E')/dE
```

where the pion source angular *shape* is interpolated **only for 206 <= E' <= 241 MeV**, using Rambo measured-angle support distributions and isotropic pi0 -> 2 gamma decay kinematics. Columns are normalized to `2 B(pi0 -> 2gamma) = 1.97646`, while the kinematic energy moment is checked independently against `B E_pi`. The measured inclusive gamma loss includes this pion subchannel, so the gamma gain adds no additional absorption loss. Unsupported 137.4–206 MeV coherent-pion regeneration is **set to zero only in the restricted experiment**; it is **not** a physical prediction of zero. Nuclear disintegration generally also produces other secondary particles not yet returned into the 3-species spectrum.

For each of 17 ACROPOLIS nuclear reactions, target-number-density-aware response `epsilon_r = integral F_gamma(E) n_target sigma_r(E) dE` is computed. For the 16 channels with explicit final-state nucleons, the signed isotope vector is `Delta Y_A=sum_r (nu_{Ar}^{out}-delta_{A,target}) epsilon_r`. This exactly respects baryon and charge sum rules. Reaction 11 `Li6(gamma,X)` has unspecified final-state species and is **excluded from the known-particle signed-vector closure** but its total event number remains in a separate unassigned ledger. The signed D response is

```
Delta Y_D = (epsilon_T->nD + epsilon_He3->pD + 2 epsilon_He4->dd + epsilon_He4->npD) - epsilon_D->np
```

This is linear first-order *per injected coherent pi0* Green-response and not time-integrated primordial D/H or physical `heat_rate`.

## Computed evidence and interpretation

Four original source energies 206,216,229,241 MeV and three fixed redshifts 1e4,1e5,1e6, each under 3 strictly paired models (`em_only`,`nuclear_loss`,`measured_pi_gain`): **36 physics rows**. Distinct derived data: **612** 17-channel reaction responses, **324** signed isotope responses, **3048** 3-species spectral rows, **5** paired grid-sensitivity responses, and **4** primary cross-section comparisons. Total **4029 new derived/source-comparison rows**, **0 new observed experimental measurements**. Six original scientific figures in PNG and SVG. Explicit output files in `data/`.

At E_primary=241 MeV,z=1e5, baseline signed DeltaD 7.931955767615159e-4 / initial pi0; including nuclear opacity 7.901612524243994e-4; with measured-support pion return 7.901734462594737e-4. Relative nuclear-opacity change ~-0.3825%; restricted-pion gain is 1.54e-5 relative to the loss-only D response. **Numerical concern:** the tiny pion gain depends on only ~3–6 grid points in measured-domain slice at ordinary resolution, so it is not admitted as a precision point estimate. The photonuclear loss effect is more stable across redshift/energy compared with grid error but remains model-conditional.

If `E_primary<=216` the original pion daughter's upper endpoint lies below the measured 206-MeV pion-injection range: the measured-only pion feedback term vanishes by construction. At E_primary=229 or 241 only the measured-domain part above 206 can produce a second pion. This is a **minimum explicitly modeled support**, not a bound on physical full-pion cascades without assumptions about omitted cross-sections.

## Evidence status and scope

- `established/literature-supported`: source papers, standard public ACROPOLIS reaction channels/parameters and AlterBBN 2.2 prior, Rambo/MacCormick measured data identities; no duplicate nuclear-loss.
- `derived + numerically checked`: full 3-species gamma/e± plus 17-channel gamma-nuclear sink and measured-support pi0 gain; all target nuclides, baryon and charge closure; actual original code executed unmodified.
- `unresolved`: 137.4–206-MeV pion cross section; 206–241 angular interpolation covariance; gamma-nuclear secondaries other than pi0; 1.5-MeV lower cutoff; high-z grid; sub-241 energy support; low-energy standard modeled cross-section uncertainties; full BASS gamma emission and fast-D stopping; no observational D/H constraint.
- `native_subagent NOT_RUN`, same-context adversarial review only; GitHub CI not claimed unless independently returned by CI tool.

Central DAG `28/88`, HE Physical DAG `14/18`, canonical physical delta `0`, new scoped local micro `1/1` when tests & preservation pass. `kappa=null; R_event=null; heat_rate=null; L4=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false`.

## Reproduction and published owner

Run from a checkout of Draft PR #137 (which inherits prior source-owned PR #134). The prior PR #136 source is archived in `research/he_dd_acropolis_pi0_20261031/archive/`; unpack its published archive into the checkout to reconstitute PR136 `src` and PR135 `pi0_physics.py` as required. Or restore the privately backed-up source-complete ZIP with the exact parent dependencies. The original ACROPOLIS 1.3.1 source is **not vendored into the public PR**; extract its byte-pinned ZIP locally and set `ACROPOLIS_SOURCE_DIR` to that directory.

```
ACROPOLIS_SOURCE_DIR=/absolute/path/to/acropolis-main bash research/he_dd_pion_feedback_20261031/REPRODUCE.sh
```

No modified/rebranded third-party research code is presented as the original author's version. Rambo and MacCormick PDFs remain in privately backed-up sources, not public PR. Use SOURCE_INPUT_HASHES.json to verify source identity. The post-run manifest verifies all new code, data, figures, stages and test evidence. Publication is only an add-only Draft PR; no merge.
