# rei_bianchi SOURCE07 dynamic photo-only closure, 2026-10-15 KST

Status: **DERIVED + NUMERICALLY_CHECKED + LOCAL_IMPLEMENTATION_VERIFIED**, within a tightly scoped homogeneous receiver problem. **NOT** a physically calibrated z=20→4 cosmological reionization history, AX08 replacement, full SOURCE07 spectrum closure, or licensed merger into production. This repository branch is additive to SOURCE07 C9 commit `9a0730c18a43595d3e29a9c03c2c3cf204e253d4`. Original AX08 frozen code/inputs/run data and CPU0 half-minus science process were not mutated.

## 1. Fixed-geometry subproblem and exact event ledger

Signature `(-,+,+,+)`. Axial Bianchi-I geometry is fixed by the frozen SOURCE07 source/clock model
```
ds² = -c²dt² + a²exp(-2b)(dx²+dy²) + a²exp(4b)dz²
d ln E/dt = -H - s(3mu²-1),   dmu/dt = -3s mu(1-mu²),   s=db/dt.
```
Thirty-six source-age moments are originally propagated **collisionlessly to one receiver epoch `a=0.2`** using the C9 frozen model (`q=-0.01,0,+0.01` and additional q=±0.005). The resulting discrete energy/angle photon packet population is then injected ONCE into a static proper-volume gas cell and followed only for an interval `0<=t<=1e12 s`. The injected amplitude `1 photon/H` is a diagnostic setting, *not* a verified source emissivity. Neither the time evolution of a true cosmic UV source nor the `a(t)` drift is integrated during the sink experiment; `HΔt` for this snapshot is recorded to expose its limitation.

Source photon energies 13.6–100 eV; rates `lambda_j(E)=c n_j sigma_j(E)` with proper `n_j` in cm^-3, `c=29979245800 cm/s`, Verner fits (cm²), proper time (s), photo-electron heat (eV). Species j=(HI, HeI, HeII), binding energies (13.598434599702,24.587389011,54.41776) eV. For a photon energy bin with N photons per cm³, the sink event is
```
A_j(E) = N [-expm1(-dt sum_k lambda_k)] lambda_j/(sum_k lambda_k)
N_new(E) = N exp(-dt sum_k lambda_k).
```
All three species update in a single gas midpoint-opacity fixed-point solve. Accepted steps require nonnegative gas inventories/thermal energy, no helium simplex violations, nonnegative photon counts and finite residuals. If a trial fails, the fixed nominal step can be subdivided; for the saved strong runs it did not need subdivision. Photoelectrons raise gas thermal energy `ΔUthermal = sum_{E,j}(E-chi_j) A_j(E)`. The current electron density is computed by charge neutrality; the heat capacity includes nuclei + electrons with `Uthermal=(3/2) k_B T (nH+nHe+ne)` and `k_B=8.617333262145e-5 eV/K`.

**Derived exact discrete reaction invariants**, for the closed photo-only cell:
```
nH = nHI+nHII;   nHe = nHeI+nHeII+nHeIII;
N_photon + n_e = constant;
U_photon + U_thermal + U_binding = constant;
U_binding = chi_H*nHII + chi_HeI*(nHeII+nHeIII) + chi_HeII*nHeIII.
```
All four algebraic identities returned `{0,0,0,0}` in direct Wolfram Language evaluation, and were independently checked numerically. Heating raises gas T but **temperature does not feed back into the photo cross-section; recombinations, temperature-sensitive collisions, cooling, expansion/redshift, source replenishment, stimulated transport, optical depth to the observer and polarization are all OFF**. A later physical model must integrate the original grackle/owner rates and thermal events with explicit separate ledgers. Do not label the static cell a physical reionization curve.

## 2. Independent analytic and algorithm checks

For a single hydrogen photon channel, `N_gamma'= -c sigma N_gamma nHI` and `nHI - N_gamma = d = nHI(0)-N_gamma(0)>0`. The exact positive solution
```
N_gamma(t) = d N0 exp(-c sigma d t) / [d+N0(1-exp(-c sigma d t))]
```
was differentiated and initial-checked in Wolfram, yielding `{0,0}`. A separate unittest evaluates its signed error at step grids 4/8/16/32/64; the observed ratio between the two smallest errors is between 3.2 and 4.8, consistent with second-order finite-step convergence. The direct per-packet scalar event integrator was also independently compared with the vectorized `NumPy` event implementation at three q cases and three step sizes. H/He number, charge and total energy tests include negative and zero-opacity cases and helium's sequential HeI→HeII→HeIII transition when initially `nHeII=0`.

For the full three-absorber test at `1e12 s, 1 photon/H`, fixed time step 8/16/32/64/128 gives measured self-convergence orders for `xHII` and `Tgas` from 2.00005 to 2.00260, both source shapes. Angle-energy GL 12×16, 16×24, 24×32 at q=0 agrees to roughly floating-point tolerance; **that isotropic convergence does not establish signed angular convergence at nonzero q**. Signed nonzero-q diagnostics were separately sampled at 12/24/48/96 Gauss directions; power-law HeII odd/even amplitude ratios are not near the naive analytic q³/q² scaling and vary at the small-signals level, so no universal hard-source signed-parity claim is made. BB50K scalar xHII parity at ±.01 relative to ±.005 is close to 4 for even and 8 for odd, conditional on the five signed-q cases and 36 discrete source ages.

## 3. Executed science and profiling

At q=0, `nsteps=64`, initial `xHII=0.4`, `xHeII=0.5`, `xHeIII=0.3`, `T0=12000 K`:
- BB50K dense 36 ages: `xHII=0.7513324146160287`, `xHeII=0.5553486654940863`, `xHeIII=0.30010165874484723`, `Tgas=15154.112402637733 K`. Energy residual `5.02e-16`.
- Power-law diagnostic `phi(E)∝E^-1.5` dense: `xHII=0.6693982576768264`, `xHeII=0.5812313837381339`, `xHeIII=0.3456195497842865`, `Tgas=18680.167624641483 K`. Energy residual `5.59e-16`.
- Original C9 five-state source-specific positive LP, evaluated dynamically without reweighting: BB50K **11 ages**, max across history `|ΔxHII|=3.69e-10`, `|ΔT|=1.55e-5 K`; hard source **12 ages**, max `|ΔxHeII|=2.67e-9`, `|ΔT|=1.83e-4 K`. These are finite tested trajectories, not uniform error bounds.
- **Negative control**: BB-trained 11-node weights re-used for hard source give `max |ΔxHeII|=2.04e-4`, `max |ΔT|=0.0946 K` and `max |ΔxHII|=5.52e-6`. Spectrally refitting hard reduces HeII to `2.67e-9`. Thus a fixed spectrum-blind compression fails this actual evolving-gas test, though positive source-specific compression remains viable.
- For 32-step BB dynamic integration of already-constructed packets, nine warm repeats: 36-age median **0.09924 s**, 11-age median **0.04000 s** (**2.481×**); photon-packet array storage **1,486,848 → 479,232 bytes** (**3.103× reduction**). Entire solver/source preparation and other cosmological data excluded.
- Three-worker processing of six independent q×spectrum jobs (BLAS 1 thread/worker, CPU0 left untouched): 3 samples each; median whole-batch wall time serial **1.6873 s**, parallel **0.7332 s**, speedup **2.301×**, science outputs identical.
- Local two-half-step adaptive controller on the same photo model: 41 accepted+2 rejected (BB), 32+2 (hard), photon/total-energy closure maintained. Compared with 256 nominal fixed steps, final adaptive temperature differences `0.0282 K` BB and `0.0720 K` hard. This is an *empirical controller with chosen local per-component tolerances*, not a rigorous global error enclosure; single-run wall speed factors roughly 1.5–2.3 on these cases only.

The tested absolute model accuracy is limited primarily by the time integrator and source/chemistry physics, not the 11–12 age compressed representation; e.g. BB 64→128 grid xHII difference `3.822e-6` greatly exceeds C9 dynamic compression xHII difference `3.69e-10`. Neither is an observational uncertainty or continuum-solver certificate.

## 4. Local execution

From the *repo root*, after `git checkout research/rei-source07-dynamic-photo-20261015`:
```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -m unittest discover -s research/source07_c10_dynamic_20261015 -p 'test_*.py' -v
python3 research/source07_c10_dynamic_20261015/study.py
python3 research/source07_c10_dynamic_20261015/adaptive.py --spectrum bb50k
python3 research/source07_c10_dynamic_20261015/adaptive.py --spectrum hard
python3 research/source07_c10_dynamic_20261015/signed.py
python3 research/source07_c10_dynamic_20261015/angular.py
```
Requires Python 3, NumPy, SciPy and matplotlib for figure generation; no `pandas`. `study.py` produces `PILOT_HISTORY.csv`, `PILOT_HISTORY.png`, `study_results.json`. `angular.py` is optional high-order stress and is the most costly. All human-readable files and small computed outcomes may be published; no raw AX08 private transport history is included.

2026-10-15 Ubuntu observed: original C9 five tests PASS; new C10 **8/8 unit tests PASS**; Python compile PASS; standalone study, adaptive and signed/angular sweeps completed. Local native delegation unavailable (`native_subagent: NOT_RUN`); CPU multiprocessing is real independent-q numerical concurrency, not a native subagent. AX08 CPU0 `SHEAR_HALF_MINUS` scientific owner process was actively running at preflight and was not touched.

## 5. Literature relevance, limits and next concrete objective

- Pawlik & Schaye, *Multi-frequency, thermally coupled radiative transfer with TRAPHIC: Method and tests*, https://arxiv.org/abs/1008.1071 , supports physically resolving H/He photon sinks and heating; does **not** establish this age-node compression.
- Petkova & Springel, *A novel approach for accurate radiative transfer in cosmological hydrodynamic simulations*, https://arxiv.org/abs/1012.1017 , motivates strict finite-step photon accounting and local stiff-chemistry updates.
- Leong, Meiksin, Lai & To, *A comparison of numerical methods for computing the reionization of intergalactic hydrogen and helium by a central radiating source*, https://arxiv.org/abs/2301.00450 , highlights the importance of correct time-dependent temperature and photon transport; this frozen stationary-receiver test cannot replace those finite light-speed calculations.
- Related user-owned `bass_cr` PR71's adaptive true-child photon q-moments are **not** assumed derivable from only parent coarse N/U. BASS_HE PR64's warm 16-cell source differs from the AX08 cold source.

**Next objective**: retain positive ages while integrating a *source-backed* continuous emission history and genuinely coupled H/He/electron/T with owner `igm_rates` recombination/cooling and collisionless Bianchi redshift, and compare against an independent uncompressed short physical interval at specified step/angular/energy tolerances. Keep recombination-photon ownership and energy ledger explicit, then assess whether SOURCE07 C10 is admissible in AX08 or only a numerical diagnostic. Do not grant physical provenance, calibrated observable conclusions, source-free transport certificates, AX11 dt convergence or `GOAL_DONE` from this pilot.
