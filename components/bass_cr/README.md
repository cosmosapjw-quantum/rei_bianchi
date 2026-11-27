# Cosmic rays in the REI IGM calculation

The installed interface is `rei_bianchi.microphysics.cr`. It owns the optional proton source, collisionless propagation and thin-target primary H I and He I ionizations. Each collision registers a fast electron. The central REI receiver owns abundances, gas energy, expansion, free-electron conventions and chemistry evolution.

| Code or evidence | Scope and authority |
|---|---|
| `src/rei_bianchi/microphysics/cr.py` (project root) | Qualified PHYS02 readback and conditional primary-collision source for native AXBI gas |
| `analysis/AXBI_PRIMARY_SOURCE.json` | Source, clocks, elemental channels, two accumulation measures, source-off control and quadrature refinement across five native snapshots |
| `analysis/PHYS02_REPRODUCTION.json` | Archived two-band proper electron injection at the PHYS02 reference gas, including the cutoff atom and total |
| `terminal_reference/` | Separate 100 K, 1% H/He ionized FS10 terminal-response calculation and its data. This gas composition restricts where its heat and secondary-ionization coefficients apply |
| `charge_exchange/` | Timescale-independent single-impact-parameter TDL and AOCC solvers and their tests. The 100 keV/u refinement shifts of 10.47% and 9.07% leave the integrated cross section open |
| `f05_materiality/` | Four previously computed critical source thresholds on F05. Source regeneration requires the identified restricted high-field-count inputs |
| `proper_injection_reference/` | Original source event, normalization, batch controls, contracts, clock identity, and side-by-side donor results |
| `upstream_pr167/` | Source snapshot for all 15 research units, solvers, scripts, inputs, published derivatives and results at the November 15 head |

## Physical experiment

Model parameters follow Leite et al. (2017, equations 23–24) and Madau & Dickinson (2014, equations 15–16). Published-source links and values are recorded in `cr_sources/injection.py`. A constant comoving source luminosity at the selected redshift is converted to a proper injection rate once. The proton birth-energy density is normalized over 10 keV–1 PeV. In the donor Rudd port the H I coefficients use the atomic Williams limit and the He I coefficients use the Rudd fit. The calculation resolves the 1–4 MeV final-projectile band. It retains kinetic energy in both outside-band populations. At this order the propagated proton distribution is collisionless and the collision debit is a first-order diagnostic.

The packaged original REI abundance table sample comes from `56dc609ea9b801c88d3364aed3eee140b3a20d46`, blob `ce22a6b6d94aabf1bffcc3b5c472316cac1983d4`. All five cases use the largest saved mean redshift at or below 8, namely 7.992469305860332. In every case the hypothetical cosmic-ray source turns on with an empty proton inventory and runs for a proper interval of $T=10^{10}$ s. Source luminosity, gas densities, expansion $H$ and shear $s$ remain fixed during this local experiment. The owner defines $a_\perp=a\exp(-b)$ and $a_\parallel=a\exp(2b)$ with $s=\dot b$. For source age $u$, collisionless proper momenta acquire the factors $\exp[-(H-s)u]$ transverse and $\exp[-(H+2s)u]$ longitudinal. With isotropic injection the quadrature uses the birth angle measure $d\mu_0/2$ and volume dilution $\exp(-3Hu)$. Projectiles contribute to a collision channel only when the propagated kinetic energy falls in its support.

For target $j$, define the primary rate age kernel $K_j(u)$ as the integral of $n_j v\sigma_j$ over the injected distribution of that age per unit source time and propagated into today's collision domain. The initially empty CR population then gives

$$
R_j(T)=\int_0^T K_j(u)\,du,\qquad
\int_0^T R_j(t)\,dt=\int_0^T (T-u)K_j(u)\,du .
$$

The latter measures the time integral of reactions per local proper volume. Following a comoving parcel gives births per **final** proper volume,

$$
N_{j,f}=\int_0^T e^{-3H(T-t)}R_j(t)\,dt
=\int_0^T\frac{1-e^{-3H(T-u)}}{3H}K_j(u)\,du .
$$

The two weights also apply to kinetic and binding energy **at the event**. Subsequent losses, work, or thermalization of the produced electron require a recipient dynamics. The numerical experiment independently reintegrates endpoint rates in proper time. Using $T R_j(T)$ for an initially empty source would almost double this window's reaction count.

At zero shear the endpoint primary rates are $2.2048840053\times10^{-25}$ and $2.7614216429\times10^{-26}$ m⁻³ s⁻¹ for H I and He I. The corresponding comoving-parcel counts are $1.1024418930\times10^{-15}$ and $1.3807106841\times10^{-16}$ m⁻³ per final proper volume. The endpoint proton debit is $2.3566798978\times10^{-42}$ J m⁻³ s⁻¹. It partitions into native binding at $5.8916177680\times10^{-43}$, fast-electron kinetic birth at $1.7672501537\times10^{-42}$, and a threshold-model difference at $2.6796734352\times10^{-46}$ in the same units. The difference per collision is $I_{\rm Rudd}-I_{\rm REI}$ and is carried as a distinct energy accounting term. The sampled fractional primary loss is $1.25\times10^{-6}$; it measures the thin-channel size on the quadrature nodes. The five-case refinement changes the primary rates by at most $1.89\times10^{-15}$ relative. These checks constrain numerical integration under the chosen model. Astrophysical source normalization, secondary deposition at this composition, and backreaction remain open. The saved CR component calls return null for prompt heat and thermal electron production in the AXBI gas. The PHYS02 electron yield has a different source and gas identity and cannot be added to the AXBI fast births.

## Reproduce

Run from the REI project root with the project dependencies installed.

```sh
PYTHONPATH=src python components/bass_cr/analysis/reproduce_sources.py
PYTHONPATH=src python -m pytest -q components/bass_cr/analysis/test_cr_integration.py components/bass_cr/f05_materiality/test_materiality.py components/bass_cr/charge_exchange/tests
PYTHONPATH=src/rei_bianchi/microphysics/cr_sources python components/bass_cr/proper_injection_reference/implementation/controls.py
python components/bass_cr/terminal_reference/tests/test_injection.py
OPENBLAS_NUM_THREADS=1 python components/bass_cr/terminal_reference/src/provider.py
OPENBLAS_NUM_THREADS=1 python components/bass_cr/terminal_reference/tests/check_provider.py
```

`SOURCE_MAP.json` identifies the upstream commits and verified bytes of the active sources and supplemental data, including the donor's Oct 27 integration branch. `UPSTREAM_PR167_INVENTORY.json` lists every blob of `3d6d671474382a019c4aca1c5f331f8a3eabe31f` (549 paths, with 512 imported). Its exclusions are generated Python and pytest caches. An external 930,236,215-byte release bundle carries six historical TDL checkpoints. Its published object identities are in `upstream_pr167/provenance/RELEASE_ASSETS.json`. The 246 upstream branch pointers observed on 2026-11-27 are in `HISTORICAL_BRANCH_REFS.tsv`; the import covers the identified head and active sibling sources. Upstream instructions that require original private source material retain that prerequisite. The active CR source numerical experiments run from this project checkout.

The Rudd kernel is GPL-3.0-only and the active combined CR implementation has the same identifier. Its upstream notice and license text accompany the source. The FS10 x=0.01 table retains the upstream 21cmFAST license under `terminal_reference/vendor/fs10/21cmfast/LICENSE`. Native code, published derivative datasets and external data remain under their original provenance and terms. The snapshot grants no new redistribution rights for private reconstruction packages or publisher material.
