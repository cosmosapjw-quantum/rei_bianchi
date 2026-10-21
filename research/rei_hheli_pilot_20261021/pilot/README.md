# Primordial H/He/Li isotope–charge and LRS sandbox pilot

This self-contained package computes a declared atomic test-fluid model from z=20 to z=2, with independently initialized signed massive-matter and radiation stresses. Dynamic electrons from the complete selected 21-state isotope/charge census actually enter photon Thomson scattering in the pinned LRS transport. Photons and massless neutrinos evolve separate energy/number towers.

The original campaign completed **79 nominal cases + 3 combined L24/tighter-tolerance controls**, with 257 stored samples per case. No completed older B/AGE/D8/D9/HE32 trajectory was rerun. Actual source runtime was this sandbox, not a Git checkout: execution identities are SHA256, and any later publication commit is a separate provenance event.

## Run one command

Dependencies observed in the sandbox: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8. The supported target is Linux/POSIX with Python 3.12. The runner uses POSIX process accounting and Linux resource probes. The extracted package must be writable because offline auditing regenerates summaries, provenance and figures.

For a fresh environment, run these commands from this package directory (`research/rei_hheli_pilot_20261021/pilot` in the delivered repository):

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The installation command requires access to the package index or equivalent local wheels. Historical `--audit-existing` requires the exact recorded NumPy 2.3.5 and SciPy 1.17.0 versions; another version is intentionally rejected as `CORE_OR_ENVIRONMENT_CHANGED`. Matplotlib 3.10.8 is pinned for rendering consistency. Once dependencies are installed, execution needs no network fetch, Rust build, external repository checkout or absolute neighboring path.

From the delivered repository root, rebuild all saved-data summaries, provenance and figures with **zero new IVPs**:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B \
  research/rei_hheli_pilot_20261021/pilot/code/run_pilot.py --audit-existing
```

From this package directory the equivalent command is:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B code/run_pilot.py --audit-existing
```

The ordinary command admits only missing authorized cases and then emits the same summaries/plots:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B code/run_pilot.py --workers 4
```

Existing completed inputs/results remain hash-bound and are reused. A fresh package with no `results/` computes the 82-case plan. The package-relative default output is `pilot/results/`, independent of the invoking directory. Optional `--out NEW_OUTPUT_DIRECTORY` selects another campaign directory, and `--no-plots` suppresses figure generation.

The controller uses at most four processes with one inner thread each, reducing against observed CPU/memory availability. Its campaign ceilings are 900 wall seconds, 2400 aggregate child CPU seconds and 90 IVP attempts. An unresolved existing `ATTEMPT.json` without `RESULT.json` blocks all new admissions until explicit reconciliation of its unknown CPU debit. Attempts/inputs are create-only. No automatic reset, unrelated process action or backend installation occurs.

## Exact physical model

Read `evidence/PHYSICAL_CONTRACT.md` for the complete frozen conventions and scope. Production uses Radau, rtol=2e-8, atol=2e-11 for normalized states, max_step=0.04 in x, L=16 and 257 uniform x samples. Three controls use L=24, rtol=2e-9 and atol=2e-12. The 39-state even LRS transport plus 21 census states and optical depth gives 61 production states.

The census is n; H1 I/II; D I/II; T I/II; He3 I/II/III; He4 I/II/III; Li6 I/II/III/IV; Li7 I/II/III/IV. Electrons follow full charge neutrality once. Each populated isotope evolves normalized charge fractions, keeping trace Li6 above the solver's population-scale issue. Nuclei are then weighted by explicitly published per-baryon abundances. n and T are absent with zero state/source; no nuclear synthesis, decay, photodisintegration or positive-n/T experiment is represented.

Verner photo rows and Verner–Ferland **total** RR are preserved exactly. The He I **a** row is explicit. Same-element isotope coefficients follow the declared `ElementalElectronicEquality` approximation; H1/D, He3/He4 and Li6/Li7 conditional fraction curves therefore overlap to numerical precision, while their abundances differ. This is not isotope-resolved spectroscopy.

The prescribed source has finite UV support 5–60 eV. Li II/III photo rates are analytically zero under that support. High Li charge fractions have analytic zero solutions from the chosen initial state; the un-clipped dense implicit solver retains floating residues with magnitude below 5e-28. These values are preserved in raw arrays and census summaries. The high-charge RR operator is tested separately at a positive-population point. No low-temperature Li collisional-ionization bundle is used.

UV intensity and temperature follow declared tanh inputs. They are not fitted reionization histories. The finite atomic model includes photoionization and total RR only; CI, DR, charge exchange, molecules, negative ions, multilevel trapping and stimulated recombination remain omitted terms. The diagram's nuclear 19-reaction target is a separate unresolved obligation, not a completed part of this atomic pilot.

## What the figures show

`results/figures/` contains ten actual PNG/PDF families and source CSVs:

1. `realized_initial_plane_final_signed_shear`: all actual 79 nominal cases; colors show absolute final signed shear, using realized initial P_m/P_r axes.
2. `component_driven_final_shear_response`: the 75 grid endpoints minus each actual A_m=A_r=0 endpoint at the same initial Sigma. The shared symmetric difference scale exposes the component response. Baseline case IDs are in its CSV; no fit, interpolation or trajectory-superposition claim is made.
3. `shear_and_stress_norm_histories`: Sigma, Pi_m, Pi_r and the norm of the signed total stress.
4. `photon_neutrino_signed_stress`: separate photon/neutrino evolution and dynamic electron scattering.
5. `initially_cancelling_histories`: two actually cancelling initial matter/radiation seeds; later cancellation is not imposed.
6. `isotope_charge_histories`: all six populated isotope charge ladders, including Li IV and explicit analytic-zero/roundoff notes.
7. `complete_21_state_abundance_census`: all selected states and their actual abundances; absent states and numerical zeros are retained.
8. `prescribed_energy_ledger`: thermal, positive ionization binding and UV energy diagnostics; required powers and the combined bath-minus-escaped requirement.
9. `positivity_conservation_refinement`: sampled brightness, number/isotope conservation and the three combined controls.
10. `electron_optical_depth_and_forcing`: proper electron density, integrated optical depth, prescribed temperature and Gamma_HI/H. Source midpoint z=7.5 is not an ionization midpoint; the finite photo rate can exceed H at earlier redshift.

Lines connect 257 stored samples as visual guides. Scatter maps contain actual cases only. Symlog axes preserve zero and signed tiny residues without epsilon replacement. Figures are intended for full-width/double-column use; reducing dense multi-panel composites to 90 mm risks small labels.

## Energy interpretation

Atomic thermal/positive ionization binding/UV energies are test-fluid contributions omitted from the inherited Einstein source. Baryon rest mass is already in inherited dust and is not added again. `epsilon_background` in the diagnostic is inherited massive+dust+radiation energy, excluding Lambda. The largest observed omitted-energy ratio is about 3.72e-9; this is an approximation diagnostic, not a bound on trajectory error.

`Q_gas_required - P_photo` denotes the combined bath-minus-escaped-recombination requirement. It is not actual recombination cooling or an independently inferred thermostat heating term. No invented emitted energy per RR event is used.

## Actual validation and provenance

`evidence/LIGHT_CHECKS.json` records independent Decimal RR, 64/128 spectral integrals, generator conservation/positivity, high-charge RR direction, abundance normalization and initial physical axes. The accepted prior HE32 parity evidence is reused; no old parity campaign is repeated.

`results/SUMMARY.json` records the actual per-case gates and combined controls. `results/SAVED_DATA_SCIENCE_SUMMARY.json` supplies nominal initial/final physical ranges, both cancellation vectors, baseline fractions at nearest explicitly identified saved redshifts, energy/charge/number extrema and all 21 species. `CASE_PROVENANCE_LEDGER.json/.csv` has 82 rows, exact configuration/raw/input/receipt hashes, physical source files, actual axes, solver counters, CPU/wall and the original execution runner identity. Execution source was not a Git commit; subsequent publication is bound separately.

The completed production used 66.031348 wall seconds and 250.578735 aggregate child CPU seconds. These are execution receipts, not speedup measurements. All 82 trajectories satisfy the frozen sample/solver gates. The largest combined difference was about 2.52e-9, below the fixed 2e-5 criterion. Algebraic Friedmann and charge closure precision are labelled separately from angular/refinement evidence.

The independent review found a controller-only interrupted-attempt accounting issue after completion. Its exact executed runner is preserved at `evidence/controller_repair/run_pilot.executed.py` (SHA256 `723156188ef43dbc36a8f949c07759ca81c34c2cccb5c1bd6c0f6f73b9a3a123`). The repair refuses unresolved attempts, preserves debit/history and permits only an explicit recorded runner relation with unchanged physical core/configuration/environment for offline auditing. Its targeted test used no IVP. Original plot-layout artifacts are also preserved; their repairs used saved data only.

A passing finite pilot can support at most the controller's scoped preliminary atomic test-fluid admission. Nuclear 19-target completion, native production, general nonlinear convergence and full closed thermal/radiation evolution remain unestablished. PR198, prior B/D9, AGE/Grackle and V12 statuses remain separate.
