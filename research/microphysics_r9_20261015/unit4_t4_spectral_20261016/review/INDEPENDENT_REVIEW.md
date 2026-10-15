# Independent C9 review of Unit4 T4

Decision: **PASS_LOCAL_IMPLEMENTATION_AND_SAVED_STATE_DIAGNOSTIC**. No concrete blocking finding or targeted repair is required. The complete runner is ready for its single bounded NCP execution. This decision does not admit an unexecuted 92-orbital spectrum.

The reviewer independently read the derivation, final contract, all 624 runner lines, all 166 test lines, actual summary and execution receipts, and NCP/report instructions. Review was read-only for implementation and frozen inputs. The current PhysMath 1.3.0 C9 and repository tier/finite-review policies were applied in one coherent pass; no recursive reviewer or repair episode was used.

| Scope | Decision |
|---|---|
| Recovered Unit3 finite-model result | PASS; reuse existing independent review and current 86/86 gates/array checks |
| Compressed operator and residual-aware moment bounds | PASS |
| Actual saved-state scalar calculation | PASS |
| Dense Hermitian/supervisor implementation checks | PASS, 9/9 |
| Complete runner ready for bounded NCP execution | PASS |
| Actual NCP Hamiltonian reconstruction | NOT_RUN_REMOTE_UNAVAILABLE |
| Actual 92-orbital spectral/refinement admission | HOLD pending NCP evidence |
| Physical exclusive continuum or electron capture | Not established; outside this finite diagnostic |

The derivation correctly defines K=Q(H−E0)Q on Ran(Q) for approximate g. The mean bound retains both the diagonal residual term and the interference term. The second-moment bound removes the component parallel to g, and the variance enclosure and Cantelli upper bounds require no positive-support assumption. Normalization corrections and the reliance on archived Hamiltonian moments/residual are explicit. The reported intervals are not directed-rounding certificates or basis-error bounds.

The runner rebuilds Be+ from the actual expanded shells and saved X and imports the immutable V6 raw_action, including its triangular occupation-list links. Reconstruction tests check orbital metric, daughter energy/residual, parent moments and pairwise Hermiticity before extending the basis. It performs no SCF, FCI ground-state replay, new orbital metric eigensolve, or spin-2RDM computation. Each K action projects on both sides of H−E0.

The numerical path retains V and KV, uses two reorthogonalization passes, diagonalizes the Hermitian part of the actual V†KV compression, and checks mass/direct moments separately from broadened refinement. It retains raw nodes, records negative-node flags and Ritz residuals, preserves analytic CDF tails without window renormalization, and follows the nested 16→32→64→128 budget rule. Happy breakdown has recurrence and direct cached-action evidence. Weighted central second moment and conditional variance use the final contract's distinct definitions. Checkpoints preserve valid basis/actions without advertising a resume interface.

The public run command supervises its own worker with the fixed wall, address-space/RSS, host-headroom and action caps. The cheap timeout fixture confirms retained partial output. These tests do not exercise PySCF reconstruction or prove full-size runtime feasibility; those are intentionally left to the actual NCP command and measured reconstruction gates.

The reviewer reran the nine focused tests with one-thread BLAS/OpenMP. They passed with exit 0 in 0.271 seconds. They cover exact spectral weights/resolvents, an approximate ground with nonzero diagonal residual, repeated eigenvalues/happy breakdown, complex rotated-basis invariance, nested milestones/checkpoints, failed reconstruction diagnostics, actual parser shape requirements, refinement/tails, and timeout/action-limit preservation. The saved-input summarize receipt independently records exit 0 and the current source-produced summary: P=0.5756391820077925, W=0.42436081799220793; conditional mean interval [2.6682102257664715, 2.6682104609101644] Eh; conditional variance interval [17.096454487726767, 17.096456473830614] Eh². The recorded aug-TZ−aug-DZ probability difference −1.007328026281229e−5 is a measured basis sensitivity only.

Reviewed contract JSON SHA256: `f870d006f3220a85c017813cbde21df7263f8c277435f438b9e01c2f172efb36`.
Reviewed runner SHA256: `3778cbd03dcd08ba7039141e8fd1c70b135062aa369afaad3f358b7219c46c90`.
All reviewed source/contract identities and the exact verification command are in `INDEPENDENT_REVIEW.json`.

The positive transition is to inspect actual host resources/duplicate runs and execute the concrete NCP command once. Passing reconstruction starts the spectral chain. Preserve a partial result if resource or refinement limits are reached; do not replay the saved ground-state solve. Actual spectral numerical admission requires its resulting receipt and milestone evidence. The fixed point-nucleus, nonrelativistic finite-basis model, outgoing-channel construction and basis closure remain separate scientific obligations.
