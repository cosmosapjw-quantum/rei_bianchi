# E13C7 scientific contract

The machine-readable `RESEARCH_CONTRACT.json` fixed the objective, input target,
allowed local work units, proposed heavy scope, protected invariants and admission
rules before execution. This document develops those same definitions. It does not
change an acceptance threshold after observing a result.

## Objective and source authority

Continue the finite captured OFF refinement from PR22 at
`019dc4f6451b3076eb6c21f8836a6040b232e945`. The current user asks that short jobs
finish in ChatGPT, and only useful heavy parallel jobs be handed to a 64-core,
128-GB NCP host. The approved fixed-capture model and inherited interval kernels
remain the scientific reference. An archive hash binds bytes; it does not establish
the scientific correctness or provider provenance of those bytes.

The complete OFF target has 2,440 paths and 4,884 captured segments. Keep the six
already admitted N512 paths. Prove and retain the 95 exact-zero source-off paths.
Execute eight local pilots covering ordinary HI, HI/HeI, HI/HeI/HeII and the two
remaining three-segment events. This leaves 2,331 independent ordinary two-segment
paths for one sealed NCP batch. KF/GM are not combined with OFF.

## Definition, units and carry

On each captured segment use local coordinate \(u=s-a_j\),
\(s=\log a\), and the same finite interval \(0\le u\le h_j\).
The fixed-source, fixed-mask linear problem is

\[
 P'(u)=q(u)-\Lambda(u)P(u),\qquad
 \Lambda(u)=\sum_i\lambda_i(u)\ge0,\qquad
 E(u)=E_{0j}\exp(-u).
\]

Gas stages are the same captured affine interpolation. Every captured binary64
input is lifted to its exact real value. The exported decimal text is transport
text, not a new decimal physical initial condition. Energy moments use eV; native
erg fields are divided once by the exact binary64 lift of `1.602176634e-12`.
Binding energies CHI remain distinct from branch selection cutoffs.

The first photon stock and incoming correction are zero. At every seam the next
incoming correction is the outgoing true-minus-captured correction plus the exact
captured stock stitch residual. No extra frozen-minus-captured term is added:
the inherited segment output already includes it. Cumulative moments are summed
without damping; the final photon stock is only the final endpoint.

The signed seam energy is
\(J_j=(E_{0,j+1}-E_j(h_j))P_j(h_j)\). Sum the actual signed intervals and subtract
their sum in the global energy ledger. The captured `anchored` flag does not license
discarding a finite binary64 energy seam. Positive captured path weights are applied
exactly once. Both old and new totals A/B/H use sums of the same species intervals.

## Frozen branch and exact zero

The two new event pilots preserve captured masks and source switches. The exact
realification of an endpoint can differ slightly from a natural threshold. In
particular, node1620's HeII event and node2344's source-on event are not claims of
strict whole-segment agreement with a freshly selected natural branch. Do not clamp
their energy or reselect their mask/source. They remain the same originally
declared captured branch target. The 2,331 ordinary bulk paths pass a separate
strict whole-branch static audit.

For nodes2345–2439 the source flag is false throughout, so \(q=0\). With
\(P(0)=0\), uniqueness of the finite linear ODE gives \(P\equiv0\). The source,
absorption, heat, redshift moments and all signed seam contributions are then zero.
Both captured values and all 34 old interval endpoint pairs have been checked
to be exactly zero. These paths must not enter the quadrature worker.

## Numerical route and independence

Reuse `directed_interval.py`, `local_enclosure.py`, `path_enclosure.py` unchanged.
The first variation uses midpoint integration with whole-cell Jet2 second
derivative bounds. Directed Decimal contexts include rounding enclosures and the
inherited incoming/coupling remainder. The ODE is linear; the field named
`nonlinear_upper` is a coupling-remainder bound, not a nonlinear governing equation.
No new global \(N^{-2}\) convergence theorem is asserted for the complete radius.

The source/selection/parallel wrappers are new. Agreement between those wrappers
and inherited kernels is a reproducibility or mapping check, not an independent
coefficient oracle. The static theory audit, exact source and budget identities,
saved Fraction relation checks and independent decision review have distinct roles.
The earlier independent derivations and kernel evidence are reused at matching
byte identities; unchanged scientific suites are not rerun.

## Declared short runs and admission

Before any heavy batch, complete locally:

- N512/P60 for105,106,409,414,1162,1620,1976,2344.
- N1024/P60 for105,409,1162,1976 as resolution/cost diagnostics.
- N128/P60 and N32/P60/P80 for1162,1620,1976,2344 as branch, precision and same-N controls.

Every path has a 180-second wall limit and a 1-GiB address-space cap. Local runners
use at most four concurrent single-thread workers. The primary NCP N is selected
from512/1024 using actual local results, then sealed in WORK_PLAN and EXECUTION_LOCK.
Only that one bulk resolution may run. These are computational resolution choices,
not a physical error tolerance chosen on the user's behalf.

Every result compares raw old/new endpoints for 17 absolute and17 correction
observables. No interval intersection is used. A full-path replacement is eligible
only if all34 pairs overlap, nest and have nonincreasing width, followed by an
independent scoped decision. Low-resolution controls may be wider and remain
diagnostic. Direct endpoint sums of disjoint node sets reconstruct each of the34
predecessor full intervals exactly; no general interval subtraction is performed.

## Parallel and memory policy

Each path is independent after input capture. All segments within it remain serial
and preserve their carry. NCP uses OpenMPI to launch independent computing ranks;
all ranks compute, so64ranks can mean64workers in this implementation. Weighted
static LPT assignment uses local per-mask timing, not contiguous node ranges. The
final reduction reads sorted nodes and uses exact rational arithmetic; MPI completion
order cannot change it. There is no threaded scientific reduction.

The original native-HPC policy is applied to task parallelism and resource auditing.
Replacing validated Decimal interval arithmetic with a binary64 Fortran hot kernel
would be a separate numerical-method change, so it is outside this fixed-kernel
batch. No hidden backend fallback is permitted. Local process transport exercises
the rank protocol; actual OpenMPI host compatibility and64-rank scaling remain
unmeasured until NCP executes. Host CPU topology, affinity, quota and memory caps
must be read. Leave at least20% of actual available memory; distinguish the1-GiB
address-space cap from actual RSS. Allocating unused RAM has no scientific benefit.

## Failure and claim ceiling

Persist fresh per-path outputs with create-only atomic publication and fsync.
Record failed/partial outputs and do not automatically retry. An explicit new
resume invocation may reuse only complete results whose source/input/N/P and
actual output bytes and semantic projections validate. A failed or partial path
cannot masquerade as a completed path. Changed source or input cannot reuse a
stale result. A failed admission is not repaired by clipping, intersection or a
looser scientific tolerance.

Execution success, exact mapping checks, independent scientific admission and
publication are separate. This loop may promote a conditional finite captured-path
refinement and prepare a heavy batch. Physical, continuum, production and receiver
claims remain HOLD. Full2331-path refinement and64-rank performance remain NOT_RUN
until actual complete evidence returns.
