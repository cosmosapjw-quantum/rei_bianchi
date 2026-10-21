# Final independent review — PASS_SCOPED_PRELIMINARY

Reviewer: `/root/pilot_independent_review`, nonimplementing. Requested Astra role; developer context identifies GPT-6 Astra Pro, without additional runtime telemetry. No solver code was written or modified by this reviewer. Review-only files include an auditable read-only raw checker and its results.

**The implementation and actual local results pass for scoped preliminary publication. There are no blocking findings and no required code repairs.** This decision admits the reported finite-model pilot, with the limits below; it does not admit production physics.

## Evidence examined

Read `pilot.py`, `plot_pilot.py`, `record_command.py`, `test_pilot.py`, source attribution and the exact vendored source, all six full/reduced comparison archives, L12/tolerance evidence and metrics, execution receipts, and all 625 case JSON/NPZ histories plus the endpoint CSV. Independently checked every vendored source against original intake bytes and every model hash against the executed run identity.

The reduced RHS implements the specified self-gravitating energy constraint, shear source and five even energy moments. Physical Sigma/Pi conversion includes the correct half-contraction factor and SI coupling. Initial fields compensate for finite-quadrature stress offsets. Shared collisionless gamma/nu, parity and nonfeedback of number moments justify the reduction; tiny floating-point matrix leakage is correctly handled by numerical tolerances rather than an exact-bit claim.

## Independent raw checks

| Check | Actual result |
|---|---:|
| Complete unique signed cases | 625 |
| Saved history samples | 40,625 |
| Finite arrays and positive H / E0 | All pass |
| Recomputed physical observables versus saved histories | Max absolute difference 0 |
| Endpoint JSON versus raw histories and CSV | Exact agreement |
| Maximum physical-axis realization error | 6.505213034913027e-19 |
| Maximum required absolute k | 0.473665761527515 |
| Independent energy exponential identity, 4 times in every case | Max absolute error 6.348166350228501e-15 |
| Six full/reduced raw comparisons | Max absolute error 2.172504320538393e-11 |
| Full source gamma/neutrino energy difference | 0 |
| Full source number-monopole error | 0 |
| Maximum full source odd energy magnitude | 3.425680593847215e-20 |
| Minimum sampled angular brightness | 0.5217217396319594 |
| Minimum E0 over all histories | 0.9997083438965781 |

The exponential identity uses the original source even matrix: `E(x)=expm(b(x)*M_even) E(0)`. This independent check was evaluated at four saved times in each of the 625 cases, without integrating a second solver.

The source Hamiltonian relative residual is at most `2.220446049250313e-16`. The two L8/L12 endpoint checks differ by at most `6.096861839173517e-14`; the tightened-tolerance corner differs by at most `3.2668095659160734e-13`. Massive directional finite-difference energy checks have maximum relative residual `1.5509306774380683e-10`. All meet the frozen thresholds. The isotropic control remains far below its `1e-12` shear/metric limits.

## Plots and execution

Both `plots_v2` PNGs were visually inspected. The four heatmaps use physical nonnegative Sigma0/Pi0 axes with independent signs and a shared color scale. Reused zero-axis controls are correct. All 676 panel data rows bind to the correct cases and endpoint table. The evolution plot displays tensor magnitudes and identifies the restricted physical model.

The actual local run completed **625 cases, zero failures**, with observed worker choices of six or seven, under the cap of eight. Recorded aggregate child wall time is `12.676384943981247 s`; cumulative run wall is `15.150453537004068 s`, including the recorded completed-resume invocation. These are execution receipts, not performance comparisons. All recorded command receipts exit zero.

Read-only resource/resume inspection confirms affinity/quota and host/cgroup memory accounting, reserve, idle sampling between batches, lower-priority workers, single-thread numerical libraries, finite remaining batch waits, preservation of failed rows, and refusal to silently retry unfinished rows. Completed resume has an actual receipt. NCP cap64 is a code path only: no authenticated NCP run or 64-core behavior has been demonstrated.

## Publication limits

The result is a preliminary self-gravitating collisionless LRS slice with fixed canonical massive quadrature and L8 massless closure. Positive canonical cell populations and positive sampled brightness do not prove global massless positivity. Two angular corner comparisons do not establish full quadrature or distribution convergence. The imposed Hamiltonian residual is a consistency check, with reference comparisons and tolerance checks providing additional accuracy evidence.

No native H/He coupling, general non-LRS Bianchi closure, observational admissibility, production admission or speedup claim follows. Those broader targets do not block publication of this completed bounded pilot. No optional benchmark or larger convergence gate is requested.

Handoff documentation was still being prepared at completion of this core review. A final documentation claim check may be appended without reopening the passed numerical acceptance.
