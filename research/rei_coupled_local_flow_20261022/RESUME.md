# Resume: supplied-input coupled local flows

Unit date/name: 20261022. Starting PR221 head:
`2f9ebff30c7505e425179862819f212ddbd07542`. New owned path only:
`research/rei_coupled_local_flow_20261022/`.

## Completed scientific work

Two retained-process local models were derived and implemented: pure-H
Case-A RR with evolving T and escaped-energy ledger, and prescribed-T
neutron beta+RR. Exact thermal first integral and stable VF primitive,
dimensionless time reuse, full/reduced Jacobians, positive exact subflows,
second-order splitting, Bessel reference and trace bound are in THEORY.md.

One scientific invocation:103/103PASS,exit0,82arrays. Body after imports
wall40.260782102s/CPU38.323068887s,processRSS113576KiB. One separately
authorized paired-timing invocation:96/96 repeated output checks,exit0,
12representativearrays,bodywall4.362194691s/CPU4.358364734s. Do not combine
the check counts or relabel previous units as rerun. There were no scientific
repairs; the standalone input/helper defect was fixed and prepare-only checked.

Scientific local_flows.py SHA256 remains
`e32069af2f1e6178a62878bd77031f68b23379100ea74aaf83f2b67923df0c19`.
First-run code is preserved in results/first_run_source.zip; exact delivery
changes and input copies are recorded. Independent decision and any final
claim limits are authoritative in INDEPENDENT_REVIEW.md.

Final recommendation/admission:
**PASS_SCOPED_LOCAL_THERMAL_AND_BETA_FLOWS**. No current-unit correctness
finding remains open; optional numerical/timing testing has ended.

## Adopted computational path

Use direct two-state DOP853 as the precision thermal baseline; exact scalar
orbit remains a reference and density/amplitude rescaling construction.
Use DOP853 as the precision beta-population baseline. Exact Strang stages
remain the finite-domain positive conservative construction. Timing ranges
overlap and achieved errors differ; no universal performance ratio is claimed.
No more optional timing sweeps are needed for this unit.

## Next physical dependency and executable continuation

Thermally coupled beta+RR needs a named electron/neutrino/recoil energy
partition, a thermalization/stopping choice and any retained radiation
reservoir/escape convention. Existing Q_bare is total release; in the neutral
reference Q0=Q_bare+dI. Use the new convention check before mapping new event
inputs. Do not assign total beta Q to heat by default.

Resume R2–R3/C2–C3 when those physical inputs are selected: bind source and
units, derive the combined energy/particle equations, then preserve these
two limiting cases as fixed references for a new bounded coupled run.
For full isotope generalization, provider-consistent RR/DR heat, daughter
charge branching and any directional photon operator retain their explicit
input obligations recorded in SOURCE_INTAKE.md.

The present exact expressions can be reused without rerunning source
extraction, algebra review or historical C1/C2/atomic diagnostics. Their
domain is the stated fixed-density/fixed-input local model, not a claim about
an unprovided cosmological/radiative closure.

## Delivery

Preserve this additive unit on existing PR221 and the already authorized
backup destinations, keeping the branch draft/unmerged. Remote publication
and archive receipts are recorded separately after successful operations in
DELIVERY.json; numerical evidence does not substitute for a storage receipt.
