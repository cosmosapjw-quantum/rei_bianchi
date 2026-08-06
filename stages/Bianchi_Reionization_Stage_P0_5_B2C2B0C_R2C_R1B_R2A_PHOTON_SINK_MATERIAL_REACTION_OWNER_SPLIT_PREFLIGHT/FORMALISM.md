# Owner-split formalism

## Conventions

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, and `k_B` remain explicit. The owner split is a local scalar absorption operation, so no metric factor enters the algebra below. Opacity has dimension `cMpc^-1`; absorbed current has dimension `s^-1 cMpc^-3`; integrated absorbed photon number has dimension `cMpc^-3`.

## Competing-hazard split

For group `g`, let the authoritative total opacity and absorbed current be `kappa_g` and `J_g`. Let `r_{g,o}>=0` be the raw component opacity response assigned to mutually exclusive owner `o`. Only its conditional ratio is used:

\[
p_{g,o}=\frac{r_{g,o}}{\sum_{o'}r_{g,o'}},\qquad
\kappa_{g,o}=\kappa_g p_{g,o},\qquad
J_{g,o}=J_g p_{g,o}.
\]

For positive total support,

\[
\sum_o\kappa_{g,o}=\kappa_g,\qquad
\sum_oJ_{g,o}=J_g,\qquad
\frac{J_{g,o}}{\kappa_{g,o}}=\frac{J_g}{\kappa_g}.
\]

Thus the same incident flux is inherited by every positive-support owner. If the authoritative total is zero, every owner contribution is exactly zero. Negative or nonfinite hazards fail closed.

## One-owner reaction map

| Component | Owner | Photon removal | Resolved H source | Resolved He source | Resolved thermal source |
|---|---|---:|---:|---:|---:|
| `EFFECTIVE_HI_SUBGRID` | unresolved subgrid | yes | 0 | 0 | 0 |
| `EXPLICIT_HI_ATOMIC` | resolved H I | yes | 1 | 0 | 1 |
| `EXPLICIT_HEI_ATOMIC` | resolved He I | yes | 0 | 1 | 1 |
| `EXPLICIT_HEII_ATOMIC` | resolved He II | yes | 0 | 1 | 1 |

The exact zeros are ownership statements, not small-number approximations. Subgrid absorbed energy is recorded separately and is not deposited into the resolved thermal variable until a separately locked subgrid energy reservoir and exchange law exist.

## Material-capacity certificates

For resolved species `s`, the interval capacity is

\[
C_s=N_{s,0}+N_{s,\mathrm{rec}}+N_{s,\mathrm{in}}-N_{s,\mathrm{out}}.
\]

The owner-correct necessary condition is

\[
N_{\gamma,s}^{\mathrm{abs}}\le C_s.
\]

No clipping is permitted. A failed certificate terminates that comparison trajectory; later states are unreachable, not negative reservoirs to be propagated.

## Node disintegration

Within an owner and macro, let `h_i>=0` be the locked material/geometry absorption measure. Then

\[
q_i=\frac{h_i}{\sum_jh_j},\qquad
J_i=J_{g,o}q_i.
\]

This preserves the owner current exactly, assigns no current to zero support, and prevents cross-owner or cross-macro transport. Historical shape priors are retained only as TV-envelope auditors.

## Timestep refinement

The 17-node canonical BDF forcing is integrated exactly on each PCHIP segment. Partitioning an interval into `1,2,4,8` subintervals changes neither the integrated owner current nor the owner total, up to floating-point summation. Refinement in this stage is therefore a budget-additivity test, not a chemistry convergence claim.
