# BASS_HE PR138: Published EXFOR Barnett-2008 near-threshold pion source and coupled light-nuclear Green response

**Status:** EXPLORATORY_SOURCE_CONDITIONAL | **Immutable parent** PR137 HEAD `efadfdea605664a5cfc829a912456a0b7142d12e` | **DAG** central **28/88**; HE physical **14/18**; canonical physical delta **0**.

## What is new in physics?

The predecessor PR137 had coherent pion measured total cross sections only at 206–241 MeV. The already-acquired original source `X4sShowData.txt` contains **EXFOR `L0138002`**, an authoritative 216-row experimental table for Barnett, Igarashi, Pywell & Bergstrom, *Near threshold (γ,π0) reactions for 4He and 12C*, PRC 77, 064601 (2008), DOI 10.1103/PhysRevC.77.064601. It covers 128.54–159.88 MeV, reporting raw microbarn values, individual statistical errors and common 2% systematic. The reaction is EXFOR-coded `(2-HE-4(G,X)0-P0-0,,SIG)`; this is **not by itself an exclusive-coherent notation**. Below the first additional breakup threshold, however, coherent alpha recoil is the only kinematically open pi0 nuclear final state. Raw subthreshold noisy measurements remain raw observations, **not positive physical pion production**.

### Exact source-domain thresholds, alpha initially at rest

With rest energies expressed in MeV, `E_th=((M_final+M_pi)^2-M_alpha^2)/(2 M_alpha)`. A separate physical calculation found:

| Final state | E_gamma threshold (MeV) |
|---|---:|
| gamma+alpha -> alpha+pi0 | 137.4207069015 |
| gamma+alpha -> p+T+pi0 | 158.0046814927 |
| gamma+alpha -> n+He3+pi0 | 158.8002859301 |
| gamma+alpha -> D+D+pi0 | 162.2069954364 |
| gamma+alpha -> n+p+D+pi0 | 164.5270139217 |

The selected *actual EXFOR measurements* are E=139.80, 144.02, 148.04, 152.03, 156.13 MeV with σ=0.9266, 3.2427, 7.5233, 11.9979, 18.7546 **microbarn**. These are **five observations from one experiment**, not independent new experiments. Source lines and 1σ statistical uncertainties are preserved in `data/EXFOR_BARNETT_L0138002_216.csv`; the 2% systematic is **common-mode**, not reduced by repeated raw rows.

The maximum photon energy from coherent `pi0->2gamma` reaches the coherent pion threshold only when the original incident gamma reaches **171.1649069015 MeV**. Therefore at every selected experimental point the prompt daughters are strictly subthreshold and recursive pion production from them is **kinematically impossible**. This is a selected-scope exact physical statement, not a broad no-go for higher-energy cascades.

### Source-to-cascade computation

The first-event pion probability in the instantaneous cold-FLRW plasma is

`P_pi^first = Γ_pi/[Γ_EM,ACROPOLIS + Γ_nuclear,17 + Γ_pi]`, `Γ_pi=n_alpha * sigma_pi,EXFOR` in natural-energy rates, using `1mb=2.56819e-6 MeV^-2` and ACROPOLIS `n_b(T), Y_alpha`. Rates are directly calculated, not fitted to a cosmological injection history. Source statistical and 2% systematic errors are linearly propagated through `dP/dσ=P(1-P)/σ`; ACROPOLIS and angular-law uncertainties are **not** included in that reported source-error budget.

For each exact incident E, pion four-momentum is calculated with full alpha recoil. A `sin²(theta_cm)` **p-wave MODEL ANGULAR SHAPE** (supported by spin0 coherent photoproduction but NOT a measured Barnett angular table) and a separately calculated isotropic countermodel are normalized over all CM angles. The resulting isotropic `pi0->2gamma` decay in the pion rest frame defines the continuous electromagnetic injection source. Daughter photon *number* is exactly `2 B_2gamma = 1.97646` with `B=0.98823` from the inherited pinned PDG choice. Energy is conserved in the two-body reaction and daughter decay at the level of the specified branching fraction; other pion decay branches are not treated as `2gamma`.

`ACROPOLIS v1.3.1` is imported from the user's pinned original ZIP SHA-256 `1d933f8d53c614d379166ada9319b4188ec45c0b74e065ba790034da41f0d9e1`; **its source is not edited**. The three-species gamma/e-/e+ transport includes original QED kernels and **all 17 nuclear photodisintegration rates as additional gamma opacity**. These 17 photodisintegration cross sections originate in ACROPOLIS's published Cyburt2003/Jedamzik2006 implementation, not newly measured 150–250 MeV excitation data. Born/depleted nuclides are treated in a perturbative fixed-abundance afterburner. The unspecified Li6(gamma,X) daughters are not invented.

Fast-D birth-energy **ledger**, not heat rate:

`E_kin[alpha(gamma,DD)] = ∫ dE_gamma F_gamma(E) n_alpha sigma_DD(E) [E_gamma - Q_DD]` (sum of both deuteron lab kinetic energies by exact energy conservation for alpha at rest).

For alpha(gamma,np)D there is no source-constrained D momentum spectrum. Use only `0 <= K_D <= E_gamma-Q_npD`, leading to a rigorous **channel-scoped upper bound**. Other deuteron-producing targets (He3 etc.) do not belong to these two-channel fastD brackets. No ion stopping, Coulomb heat deposition, or true `heat_rate` is asserted.

### Actually computed (not planned)

- 216 original Barnett raw source points classified; five exact measured values admitted to coherent-only below-breakup window;
- **15 three-species ACROPOLIS coupled physical Green-response cases** (5 source energies × z=10^4,10^5,10^6), with 17 nuclear photoabsorptions as photon sink;
- **255 nuclear reaction events**, **135 signed nine-nuclide response rows**, **2622 species/source/opacity spectrum rows**, **8 grid-and-angular-model diagnostic rows**;
- **3035 new calculated physics rows**, not counting 216 reused measured source rows, plus **5 PNG + 5 SVG** actual scientific plots;
- saved-data audit and Wolfram independently reproduce exact five threshold values and 171.1649069 MeV daughter-pion reopening.

Representative point E=156.13 MeV, z=100000:

- measured pi0 source `18.7546 ± 0.2351(stat) μb`, additional shared 2% systematic;
- `P_pi^first=4.934088e-5`, source conditional;
- signed `D_net/pi0=9.266543e-4`, `D_net/primary gamma first-hit pi0=4.572194e-8`;
- DD deuteron total **birth** kinetic `7.196482e-5 MeV/pi0`; additional npD deuteron **kinetic upper** `3.426024e-2 MeV/pi0`; no deposited energy estimate;
- prompt daughter gamma maximum `<116.1 MeV < pion threshold`.

At high z=10^6, `P_pi^first~10^-13–10^-12` and derived D response is strongly suppressed; small signed differences there should not be promoted as high-precision cosmological predictions.

### Blind-referee caveats and actual acceptance

**Critical constraint**: The original EXFOR `(G,X)π0` data do not specify alpha recoil. The coherent interpretation is *derived solely for E<158.0047 MeV*, below first allowed pion plus breakup final state. It is not extrapolated into 158–206 MeV. p-wave angular shape is a model assumption; the isotropic alternative and grid 64 versus 96 are compared at two selected energy-redshift pairs. Cross section systematics are correlated; nuclear/cascade model uncertainties are independent of those two measurement-error fields. Gamma creation after primary Compton scattering and later pion production from high-energy parents are outside this *first-hit* scoped experiment. FastD birth kinetic is not plasma heating. Full background IVP, BASS high-energy gamma emissivity, cosmic event `R_event`, `heat_rate`, and `kappa` remain **null**. No claim of new experimental data, exhaustive branching, or project canonical DAG completion.

**STOP/claim gate:** Local source-backed coherent near-threshold micro unit 1/1 **scoped complete**; Central DAG 28/88, HE Physical DAG 14/18, canonical physical delta 0. `L4=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false`. Independent different-author R6/C9 and native subagents NOT_RUN.

## Code and reproduction

Requires Python 3, numpy, scipy, matplotlib, numba, original **ACROPOLIS v1.3.1** installed or `PYTHONPATH` pointing to the user-provided `acropolis-main.zip` extracted code. Original ACROPOLIS itself is **not re-published in the public Git PR**. The user may privately restore the complete external originals from the separate source-preserving ZIP.

```bash
export PYTHONPATH=/path/to/acropolis-main:${PWD}/src
bash REPRODUCE.sh
python verify_manifest.py
```

The complete `data/EXFOR_BARNETT_L0138002_216.csv` is a source-tied derivative of the original uploaded EXFOR fixed-column text; raw EXFOR source is preserved only in the private ZIP with its SHA-256 and DOI. File manifest and source identities are byte-locked. Only one model-independent known-pion incoherent-channel threshold assumption is required for the coherent domain; no unpublished source or corresponding-author contact is a blocker.

### Primary sources

1. M. G. Barnett et al., *Near threshold (γ,π0) reactions for 4He and 12C*, Phys. Rev. C 77, 064601 (2008), https://doi.org/10.1103/PhysRevC.77.064601 ; EXFOR original `L0138002` (IAEA-NDS data) https://www-nds.iaea.org/exfor/exfor.htm.
2. P. F. Depta, M. Hufnagel, K. Schmidt-Hoberg, *ACROPOLIS*, original 2020/21 manuscript https://arxiv.org/abs/2011.06518 and primary upstream https://github.com/hep-mh/acropolis (v1.3.1 archive pinned).
3. R. H. Cyburt, J. Ellis, B. D. Fields, K. A. Olive, PRD 67, 103521 (2003), https://doi.org/10.1103/PhysRevD.67.103521 ; K. Jedamzik PRD 74, 103509 (2006), https://doi.org/10.1103/PhysRevD.74.103509 (reaction formula and correction as implemented in ACROPOLIS).
4. F. Rambo et al., Nucl. Phys. A 660, 69–83 (1999), https://doi.org/10.1016/S0375-9474(99)00383-8 (high-E angular source; **not transplanted** to low-energy measured angular distribution).
5. M. MacCormick et al., PRC 55, 1033 (1997), https://doi.org/10.1103/PhysRevC.55.1033 (total inclusive absorption **begins near 200 MeV**, not used as low-energy anchor).
