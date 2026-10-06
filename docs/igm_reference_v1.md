# Independent manufactured FLRW H/He reference

## Status

The independent continuous-time reference reaches the frozen z=12 to z=11.5 endpoint. This verifies one manufactured, closure-conditional point calculation. It is not an observed reionization reconstruction or an interval-certified result. Full Rust/Python and independent birth/energy convergence acceptance is still open: the first coarse Rust timestep and source quadratures miss the predeclared comparison targets.

## Independent construction

`tools/igm_reference.py` does not call Rust or use a Rust trajectory in its right-hand side. Its rates are separately transcribed from the retained literal Grackle C source at commit `af7939494ce65007887ada7b98d1813df6843346`; all tabulated coefficients, including nextafter branch neighbors, agree with the C fixture to the declared relative 2e-12 criterion. The original Grackle CI floors and CE exponent caps remain explicit diagnostics. Gas fractions or temperatures are never clipped or floored.

The reference constructs its own analytically normalized E^-2 Gauss2 energy quadrature, splitting at both binding energies and the distinct Verner support cutoffs. Gauss2 birth epochs use fixed, uniform ln(a) panels and proper-time weights `dln(a)/H`. The first frozen schedule's 640 rows independently match Rust to maximum relative differences 1.76e-16 in epochs, 1.96e-16 in energies, and 1.56e-15 in packet weights. No quadrature weights are renormalized to hide their integration error.

Between births, SciPy Radau integrates the coupled fractions, thermal energy per H, packet optical depths, and cumulative event/energy ledgers. Each packet energy is evaluated analytically as `E_birth exp(ln(a)_birth - ln(a))` inside every RHS call. Proper-time chemistry is converted by `1/H` once. All three absorbers compete. The same owner rates drive photoionizations, binding, heat, and photon depletion. Helium CE's density-cubed channel is retained. Case-A RR/DR capture radiation, excitation, and free-free enter the escape ledger once; signed CMB exchange has its own reservoir. Energy coordinates are internally scaled by one eV only for conditioning; CSV energies are erg/H.

The reference is distinct from Rust's transport-then-BE splitting. Its Jacobian has analytically differentiated optical-depth columns and four finite-difference gas columns. Endpoint admission checks every accepted Radau state, including zero boundaries. Cutoff crossings are prescribed events with a fixed active-channel mask on each integration interval. HI survivors outflow at exactly 13.60 eV. Photons born below that cutoff outflow immediately at their actual birth energy.

## Positive packets and IEEE readouts

Direct binary64 packet-count integration produced negative roundoff in highly opaque gas. Each positive born packet therefore retains an authoritative optical depth and log-count, with `N = exp(log(N_birth)-tau)` used only as the float-facing readout. An empty list represents exactly zero initial photons. There is no physical packet deletion, merging, count floor, or state projection; only physical HI cutoff removes a packet.

Readout subnormals/zeros are explicit numerical effects, not physical extinction. Every packet entering that tail receives a conservative remaining-count bound `MIN_POSITIVE` and energy bound `E_birth * eV_erg * MIN_POSITIVE`. Non-tail photo-product underflow is separately diagnosed. All possible three-owner products are conservatively bounded over `delta_ln(a)/H_end`, including direct energy-product underflow; Gamma readout bounds include `c*nH` amplification. Bounds are required below 1e-20 photons/H and 1e-30 erg/H. The 640-packet reference sees 347 tail packets and accumulated conservative count/energy bounds about 3.14e-290 in their respective units. These bounds concern IEEE underflow only, not ODE discretization error.

`packets_final.csv` retains each surviving identity, birth epoch/energy, tau, log-count, current energy, and float readout, even when that readout is zero.

## Acceptance and current evidence

- The 14 Python tests cover pinned rates, source moments and one proper-time conversion, neutral He growth, the zero-source neutral adiabatic limit, local photo/energy ownership, cutoff outflow, born-subcutoff outflow, retained log-counts, strict parsing, and comparison rejection for missing fields or bad budgets.
- Full Radau rtol=1e-11, atol=1e-14 and rtol=2e-12, atol=2e-15 runs both pass the frozen cumulative number/energy budget tests. Tightening changes the worst reported field by 7.57e-8 of its ordinary comparison allowance, well below the required 0.1.
- The exploratory rtol=1e-9 full run does not pass the budget criterion. It is not used as the accepted reference.
- The first Rust `max_dln_a=2e-4` run closes its budgets but fails the independent field comparison, particularly instantaneous Gamma and surviving radiation. Source schedule disagreement is excluded by direct parity testing. The completed finer Rust and separate source probes below also fail, so acceptance remains incomplete.
- Initial source probes also miss the fixed targets: birth16→32 has strongly phase-dependent instantaneous radiation at the common output times; energy2→4 still changes some Gamma values by more than the 1e-3-relative-plus-absolute criterion. Source amplitudes, closure, output grid, and acceptance limits have not been changed to improve these results.

`igm_compare.py` requires all fractions, temperatures, electron abundance, Gamma values, packet totals, event counts, energy ledgers and floor/cap/excluded diagnostics. It reports absolute error near zero and allowance-normalized error. Both candidate and reference must also close their own number/energy budgets; matching two bad budgets cannot pass.

## Reproduction

From the repository root, with Python, NumPy, SciPy and optional Matplotlib installed:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tools/tests -p 'test_igm_*.py' -v
OPENBLAS_NUM_THREADS=1 python tools/igm_reference.py \
  --config configs/igm_manufactured_v1.cfg --output <new-reference-directory>
python tools/igm_compare.py --candidate <rust-directory>/history.csv \
  --reference <reference-directory>/history.csv --output <comparison.json> \
  --plot <history.png>
```

The tested environment is SciPy 1.17.0, NumPy 2.3.5. Reference CLI defaults are rtol=1e-11 and atol=1e-14; use explicit tighter tolerances for the independent tolerance check. `--times-csv` reads only common output coordinates, never gas or radiation values. Output directories must be new. A failed integration writes a nonzero-status record; a completed integration with failed budgets exits with code 2 and `ledger_valid=false`.

The current CLI records exact config, source-input and implementation hashes, provider source identity, solver/tolerance metadata, statistics, independent births, history, and final log-packet state. Earlier numerical artifacts in this snapshot record config hashes and dependency versions but lack the exact producing-script and source-input hashes. Their historical script provenance cannot be retroactively certified: the delivered scripts include subsequent validation, metadata, and presentation corrections. Artifact inventories certify the delivered bytes, not a missing historical execution hash. The reference is a verification dependency, not a production dependency of the Rust solver.

## Frozen finite-slice outcome

Numerical accuracy status: **FAIL / NOT YET CONVERGED**. No combined refinement or larger campaign was started after the independent axis gates failed. The source and closure were not changed.

The accepted fixed-schedule reference endpoint (birth16, energy2, Radau rtol=2e-12) is xHII=0.59638374355, xHeII=0.57360723233, xHeIII=0.39751451535, T=14672.836996 K. The finest completed Rust time probe (`max_dln_a=3.125e-6`, a factor 64 below the initial step bound) still misses the comparison target: Gamma_HI's worst allowance ratio is about 361.69. Budget closure alone does not establish temporal accuracy.

At fixed energy2, endpoint Gamma values in s^-1 are:

| Birth panels | HI | HeI | HeII |
|---:|---:|---:|---:|
| 16 | 1.3747774e-17 | 2.5193594e-16 | 1.7664208e-16 |
| 32 | 7.7230415e-17 | 1.2201411e-15 | 6.2811332e-16 |
| 64 | 2.4260234e-16 | 3.3362262e-15 | 1.2238211e-15 |

Birth32→64 changes xHII by up to 0.0050473 and T by up to 507.741 K over the shared output grid. Maximum absolute Gamma changes are 2.14617e-14, 9.52031e-14, and 1.07334e-14 s^-1 for HI, HeI, and HeII. Cumulative emitted photons differ by up to 0.00570393 per H at those outputs, despite endpoint emitted totals agreeing to a few 1e-15: discrete impulse placement creates a source-phase error, not an emissivity-normalization change. Birth64's exploratory rtol=1e-10 solve itself has number/energy budget allowance ratios 2.615 and 1.446; it is not an accepted reference. No tighter replacement was run after the finite-slice stop.

At fixed birth16, energy2→4→8 improves the energy axis substantially, but energy4→8 still fails: active radiation energy has worst allowance ratio 2.133; Gamma_HeI and Gamma_HeII have ratios 1.565 and 1.316. Maximum absolute Gamma changes for that pair are 2.37457e-18, 1.56581e-17, and 1.05475e-18 s^-1; maximum xHII change is 2.36674e-5 and T change is 0.260436 K. Both energy4 and energy8 runs pass their own budgets. These energy probes use a fixed birth schedule that is not itself converged; they do not establish the full source integral's accuracy.

### Why merely increasing birth panels is expensive

An illustrative scalar calculation freezes the initial background and the HI opacity of a 13.7 eV packet. It gives d(tau)/dln(a)=1.3662731e6 and an absorption e-fold width 7.31918e-7 in ln(a). For a constant-opacity steady source, the exact panel-end Gauss2 approximation-to-continuous-solution ratio is

`R(p) = (p/2) [exp(-p(1+1/sqrt(3))/2) + exp(-p(1-1/sqrt(3))/2)] / (1-exp(-p))`,

where p is opacity times panel width. R reaches 0.999 at p≈1.46593074. Applied to this interval, that scalar illustration suggests roughly 36,555 birth panels: 1,462,200 packets at energy2 or 5,848,800 at energy8, exceeding the declared 20,000-packet bound. This is not a proven lower bound for the nonlinear coupled problem; it explains why the present impulse quadrature can leave instantaneous Gamma unresolved even while integrated fractions and ledgers improve. A different source-time representation would require a separately reviewed implementation step, not silently altered physics or loosened thresholds.
