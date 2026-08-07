# R1B-R2A photon-sink/material-reaction owner split

## Status

This document records the corrective physics lock following the first
R1B-R2 full-matrix attempt. The attempted history is not admissible evidence
for or against fixed-point existence because it assigned the same low-group
absorption both to the `EFFECTIVE_HI_SUBGRID` photon sink and to resolved
material photoionization.

No diagnostic history from that attempt may be promoted.

## State, flux, and ledger taxonomy

Resolved material state:
\[
Y_i=(N_{\rm HI},N_{\rm HII},N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII},U)_i.
\]

Radiation-reaction fluxes are algebraic:
\[
J_{i g o}(t)\ge 0,
\]
where \(o\) is an explicit owner. Cumulative absorbed counts and absorbed
excess energy are interval ledgers, not material states.

The owner set is
\[
\mathcal O=\{
{\rm RESOLVED\_HI},
{\rm RESOLVED\_HeI},
{\rm RESOLVED\_HeII},
{\rm EFFECTIVE\_HI\_SUBGRID},
{\rm BOUNDARY\_REDSHIFT},
{\rm OTHER\_LOCKED}
\}.
\]

## Competing-hazard split

For a group \(g\), let
\[
\kappa_g^{\rm tot}=\sum_{o\in\mathcal O}\kappa_{g o},
\qquad \kappa_{go}\ge0.
\]
For a homogeneous gray segment with common incident flux, the conditional
owner probability for an absorbed photon is
\[
p(o\mid g,{\rm abs})=
\begin{cases}
\kappa_{go}/\kappa_g^{\rm tot},&\kappa_g^{\rm tot}>0,\\
0,&\kappa_g^{\rm tot}=0.
\end{cases}
\]
Hence
\[
N_{\gamma,g,o}^{\rm abs}
=N_{\gamma,g}^{\rm abs,tot}p(o\mid g,{\rm abs}),
\qquad
\sum_oN_{\gamma,g,o}^{\rm abs}=N_{\gamma,g}^{\rm abs,tot}.
\]

At node level the same split is the Radon--Nikodym disintegration with
respect to the owner-labelled physical absorption measure:
\[
q_{igo}=\frac{h_{igo}}{\sum_{j,o'}h_{jgo'}},
\qquad
N_{\gamma,igo}^{\rm abs}=N_{\gamma,g}^{\rm abs,tot}q_{igo}.
\]

## One-owner update matrix

| Owner | Removes group photons | Updates resolved H/He populations | Updates resolved \(U\) | Separate ledger |
|---|---:|---:|---:|---|
| `RESOLVED_HI` | yes | \( {\rm HI}\to{\rm HII}\) | yes, H I excess energy | resolved H photoionization |
| `RESOLVED_HeI` | yes | \( {\rm HeI}\to{\rm HeII}\) | yes, He I excess energy | resolved He I photoionization |
| `RESOLVED_HeII` | yes | \( {\rm HeII}\to{\rm HeIII}\) | yes, He II excess energy | resolved He II photoionization |
| `EFFECTIVE_HI_SUBGRID` | yes | no | no unless a separately locked subgrid-energy reservoir is evolved | unresolved photon/energy sink |
| `BOUNDARY_REDSHIFT` | transfer/storage only | no | no | boundary/group-storage ledger |
| `OTHER_LOCKED` | as registry declares | only if a unique material owner exists | only if the same owner owns energy deposition | owner-specific ledger |

The resolved chemistry source is therefore
\[
N_{\gamma,ig}^{\rm chem}
=\sum_{o\in\{{\rm RESOLVED\_HI,RESOLVED\_HeI,RESOLVED\_HeII}\}}
N_{\gamma,igo}^{\rm abs},
\]
not the total group absorption.

The unresolved sink is
\[
N_{\gamma,ig}^{\rm subgrid}
=N_{\gamma,ig,{\rm EFFECTIVE\_HI\_SUBGRID}}^{\rm abs}.
\]

## Conservation identities

Photon number:
\[
N_{\gamma,g}^{\rm in}
-N_{\gamma,g}^{\rm out}
-\Delta N_{\gamma,g}^{\rm storage}
=
\sum_oN_{\gamma,g,o}^{\rm abs}.
\]

Resolved material chemistry:
\[
\Delta N_{\rm HII}^{\rm photo}
=N_{\gamma,{\rm RESOLVED\_HI}}^{\rm abs},
\]
\[
\Delta N_{\rm HeII}^{\rm photo}
-\Delta N_{\rm HeIII}^{\rm photo}
=N_{\gamma,{\rm RESOLVED\_HeI}}^{\rm abs},
\qquad
\Delta N_{\rm HeIII}^{\rm photo}
=N_{\gamma,{\rm RESOLVED\_HeII}}^{\rm abs},
\]
before recombination, collisional, and transfer terms are added.

Resolved photoheating:
\[
\Delta U_{\rm photo}^{\rm resolved}
=\sum_{g,s\in\{{\rm HI,HeI,HeII}\}}
N_{\gamma,gs}^{\rm abs}\,
\overline{\epsilon}_{gs}(\tau).
\]
Subgrid absorbed energy remains in a distinct unresolved ledger until a
separate state and exchange law are authorized.

## Hard gates

1. `duplicate_owner_count == 0`.
2. `unowned_absorption_count == 0`.
3. `sum_owner_absorption == total_absorption` for every group/slab.
4. `resolved_chemistry_absorption <= resolved neutral capacity + recombination supply`.
5. `EFFECTIVE_HI_SUBGRID` contributes exactly zero to resolved H/He population updates.
6. `EFFECTIVE_HI_SUBGRID` contributes exactly zero to resolved \(U\) unless a separately locked exchange term is present.
7. Exact species/group support zeros remain structural zeros.
8. No clipping, cloud-mass inversion, or post-hoc owner reassignment.
9. The first double-owned full run remains a preserved failed attempt.
10. Only after these gates pass may the four-lane/four-refinement fixed-point matrix be rerun.

## Relation to `rec_bianchi`

`rec_bianchi` PR-04C3 closes a source-conditioned split-domain operator
contract and PR-05A is freezing `BackgroundSnapshot`,
`AtomicRadiationState`, `RadiationFeedback`, and `TrajectoryStepLedger`
together with a one-owner removal/replacement matrix. R1B-R2 imports only
these schema and ownership semantics. It does not import recombination
history values, primitive HyRec rates, or a surrogate atomic operator.

The future adapter must enforce:

- reionization owns post-recombination UV source/absorption chemistry;
- recombination owns primordial atomic/radiation microphysics;
- shared geometry enters through `BackgroundSnapshot`;
- radiation feedback is exchanged exactly once;
- no photoheating, recombination, escape, or boundary packet is counted by
  both projects.
