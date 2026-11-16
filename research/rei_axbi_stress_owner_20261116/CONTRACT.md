# Original REI IGM: owner consumption of radiation-stress diagnostics

Date: 2026-11-16 Asia/Seoul. Unit: `REI-AXBI-STRESS-OWNER-20261116`.

## Objective and authority

Use the four byte-identified original `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`
histories to quantify the omitted anisotropic radiation stress and its linear
effect on the prescribed expansion clock. This discharges a **scoped part of
AX03/AX08 approximation validity** and informs AX11's geometry error component.
AX10 is the optional observables node, not the name of this stress calculation.
The original 17-node goal and separate 88-node integration DAG are preserved.

This is a new physical consumer of the actual saved ionizing photon quadrupole,
gas temperature, charge census and geometry. The effective background radiation
is the explicitly prescribed initially isotropic, collisionless, massless
Omega_r fluid, evaluated with the BASS characteristic map in the original
variable-H geometry. No source or initial condition is refitted.

The original interval is mean redshift 20 to 4, non-tilted, homogeneous,
axisymmetric Bianchi I, metric signature (-,+,+,+). Case-A escape, primary H/He,
MD14 source, 50,000 K spectrum and original accuracy thresholds remain fixed.
Input q values are 0, +0.005, -0.005, -0.01. The +0.01 full case is missing.

## Concurrent work and owned paths

PR374 was observed advancing from `df72fb686a41c3f047bca1a92df8946482948f82`
to `db77071aedec26c7f2d0bbb41e56298b44b88c97` during this inventory. Its
abundance/clock/milestone/Thomson loop is active in another worktree.
This unit owns only `research/rei_axbi_stress_owner_20261116/` on an isolated
branch. It reads the prior inputs/results and makes no edits in PR374's subtree,
the original worker, main, other repositories, or the user's dirty checkout.

## Outputs and decisions

1. Native-row extrema and sampled time-ordered histories of effective-radiation
   and actual ionizing-photon pressure anisotropy, delta_s/H and extra energy.
2. First-order fixed-density expansion and elapsed-clock corrections, evaluated
   on the unmodified histories. These are perturbative omitted-feedback
   diagnostics, not newly coupled gas/radiation solutions.
3. Actual scalar signed-parity diagnostic with the original abundance floors;
   no missing positive-shear case may be inferred by parity.
4. Source-qualified owner intake, original-goal DAG overlay, explanatory figure,
   ten paired R/C checkpoints, immutable backups, and a runnable handoff.

Keep the original approximation thresholds: max |delta_s/H| < 1e-4 and
extra radiation/thermal energy divided by background energy < 1e-4. Passing
these diagnostics neither establishes AX11 time/energy/angle convergence nor
closes AX12 source/IC robustness. No new strong no-go is proposed.

## Execution and review

One four-history streaming/vectorized consumer, wall cap 120 s; one targeted
independent-formula audit, cap 60 s; one figure render, cap 30 s. A diagnosed
implementation repair is allowed with its first failure retained. No coupled
source ODE run, no heavy build, no historical budget reset. Capture actual wall,
CPU, memory, dependency versions and source hashes. Archive reads and Git
operations are preservation, not a new solver trial allocation.

Use same-author adversarial checks: local-angle versus initial-momentum
radiation moments, SI time integration versus dimensionless ln(a) integration,
zero-shear and small-shear limits, and explicit negative input/normalization
cases. No subagent or distinct-author/blind-review claim.

At each stage the drift watchdog must connect its output to AX03/AX08 validity,
an actual abundance interpretation, or preservation of that result. End this
unit at its acceptance and handoff. Do not replace the remaining AX08/11/12
trajectory work with a further diagnostic atlas.

Baseline progress: central **28/88**; working **33/88** (separate view).
Historical original-goal state at `fef2baf960f57f37b838004fbb8a7d37b3824852`:
**9/17** marked complete, including preparation/report nodes. Current complete
represented source cases: **4/5**; previously reconstructed stress cases: **2/4**.
These denominators are distinct and must not be added.
