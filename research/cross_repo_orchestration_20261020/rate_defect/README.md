# Rate-edge defect reference kernel

This standard-library-only Python kernel implements section 5 of
`../theory/RATE_DEFECT_CONTRACT.md`. Its checks are **manufactured mathematical
controls**, not physical Li, RUN19, or cosmological trajectories. It reads no
tables, substitutes no physical provider, and evolves no physical state.

## Interfaces

`assemble_rate_defect(n, pairs, population, ...)` takes explicit state count and
one ordered representation `(i,j)` of each unordered physical pair. Forward
means `i -> j`; backward means `j -> i`. Inputs `delta_forward` and
`delta_backward` mean approximate minus exact rates. Each rate is already a
hazard in the selected time coordinate. Aggregate distinct physical subchannels
before passing a pair.

The returned immutable result contains:

| Field | Meaning |
| --- | --- |
| `exact_defect` | State vector `(K_hat-K)p_hat`, or `None` in a bounds-only call |
| `exact_l1` | Its floating-point l1 norm |
| `signed_pair_defects` | `delta_f*p_i-delta_b*p_j`, preserving pair orientation |
| `pair_triangle_bound` | Twice the sum of absolute signed pair defects |
| `independent_rate_majorant` | Twice the sum `eta_f*abs(p_i)+eta_b*abs(p_j)` |
| `negative_population_indices` | Every reconstructed population below zero |
| `source_difference` / `source_mass_difference` / `source_l1` | Supplied `b_hat-b`, its signed sum and l1 norm |
| `combined_defect` / `combined_l1` / `combined_majorant` | Edge-plus-source vector, norm and triangle majorant |

Supply both signed delta arrays, both nonnegative absolute bound arrays, or
both sets. A signed-only call uses `abs(delta)` as its independent absolute
bound. A bounds-only call cannot report an exact vector. When both are supplied,
absolute bounds must enclose the signed deltas. Negative populations are retained
and reported. Inputs reject nonfinite numbers, invalid indices, self edges,
duplicate unordered pairs, length mismatches, negative bounds and nonfinite
arithmetic results. Assembly uses O(E+N) time and memory, including contributions
at isolated states; no dense matrix is built by the kernel.

`declared_common_relative_defect(...)` separately accepts baseline nonnegative
forward/backward rates and an explicit epsilon per pair shared by both directions.
It constructs both deltas from that declaration; it never infers correlation
from independent bounds or from temperature. Epsilon below -1 is rejected because
it would create negative reconstructed rates. Its near-balance result is subject
to ordinary floating-point cancellation. No higher-precision enclosure is claimed.

`observable_mixed_bound(weights, E, mass_error_bound=M)` computes
`(max(w)-min(w))/2*E + abs((max(w)+min(w))/2)*M`. `M=0` is an explicit caller
assertion requiring matched total mass. Omitting M returns the general
`max(abs(w))*E`. The caller must account for initial mass discrepancy and source
and event mass differences when establishing M. An empty observable has bound 0.

## Integration status and clocks

`panel_supremum_integral_bound(widths, supremum_bounds=..., clock=...,
supremum_provenance=..., event_l1_bounds=...)` returns
`status="conditional_certificate"` and the sum of width times continuous
supremum, plus independently bounded event defects. A provenance string is an
explicit record of the caller's premise; this function does not prove that premise.
Widths must be nonnegative and expressed in the named clock. Clock reversal
requires reordering the physical integration interval. Integrands must already
be in that clock: include `dt/dx` exactly once when changing coordinates. The API
does not infer units, density factors, Hubble factors or Jacobians.

Calling that API with only `samples` returns `status="unresolved_samples_only"`
and `total=None`. No suprema and no samples returns `unresolved_no_suprema`.
The different `sampled_trapezoid_diagnostic(...)` API always returns
`status="sampled_diagnostic"`; its total is a sampled diagnostic without a
continuous certificate. Event inputs are l1 bounds on jumps in the error, so
approximation resets also need accounting. Add the initial l1 error separately
and integrate solver residual, edge-rate error and source errors with their own
justified bounds. Do not count a source or clock factor twice.

All results use floating-point arithmetic, without outward rounding. Conditional
certificates here are mathematical bound evaluations under supplied premises;
they are not machine-checked interval certificates. The contract applies to a
prescribed bath. State-dependent temperature, electron-density, opacity and
source feedback require the separate nonlinear tube analysis.

## Verification

From this directory:

```bash
timeout 20s python3 run_verification.py
```

The single process writes `test_output.txt` and `results_receipt.json`, including
the actual test count, exit status, elapsed test-run time, CPU time, Linux peak
resident memory and source hashes. It needs no NumPy, network, ODE solver or NCP.
The tests independently assemble dense column generators for 2, 4 and 17 states;
check orientation, conservation and adjacent-pair cancellation; distinguish a
declared shared perturbation from independent uncertainty near balance; verify
an analytic two-state ODE error against its analytic residual integral and panel
suprema; retain source mass and negative populations; exhibit a mass-mismatch
observable counterexample and a jump; demonstrate a hidden intersample bump;
and reject invalid inputs. Inspect the receipt for the actual outcome.

Existing failed BDF evidence is outside this directory and is neither read nor
modified. Independent review is required before adoption or publication.
