# First actual-source screen: incomplete, preserved

`raw/q128_attempt1_receipt.json` is the complete execution receipt. The actual release example stopped with `AXBI_RUNTIME_CAP`, saved a V3 checkpoint, and returned exit1. It reached z=19.97343215826658 rather than the frozen target19.8.

| Observed quantity | Result | Frozen limit |
|---|---:|---:|
| Accepted steps | 20000 | 20000 |
| Tentative starts | 60060 | 65000 |
| Rejections | 20 | — |
| RHS evaluations | 420444 | 5000000 |
| Executor wall seconds | 466.2802 | 600 |
| Output bytes | 189020053 | 268435456 |
| Sampled peak RSS bytes | 2125824 | address-space limit8589934592 |
| Maximum observed native threads | 1 | one initial native thread |

The first cap reached was accepted steps. This was neither a wall/RHS/output-cap failure nor an observed negative-state/domain failure. Accepted timesteps settled near dln(a)=4.8828125e−8, with final metric5.3425262e−6. The exact dominant error-metric component was not instrumented in this run; the data do not establish whether the limiting mechanism is a necessary physical transient or a repairable numerical/comparison artifact.

No ledger row reported FAIL. Maximum absolute photon-number residual was6.8440262e−19/H and augmented-energy residual3.7470027e−15 eV/H. Four checkpoint arrays each contain1024 entries. Source/config readback and source stability during the run all passed. Stored photons include subthreshold stock; both legacy boundary outflow ledgers remain0. These are scoped consistency observations, not interval/refinement admission.

The remaining four cases were not launched, and the first failed attempt was neither overwritten nor resumed. The frozen z20→19.8 empirical screen is incomplete, so its full-history launch transition is not open. No threshold was loosened and no comparison was made between unequal endpoints.

Next executable action is a bounded root-owned diagnosis of the timestep/error-metric components, followed by one specifically authorized repair and its changed-dependent rerun if justified. A further attempt must preserve this one and bind any changed source/config explicitly. This is a numerical dependency, not a new infrastructure or user-permission request.
