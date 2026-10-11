# C08C: conditional single G2 continuation

The root selects one additional operational phase of at most 600 seconds **only if** the original `GAUSS2_FINE` ends with `TimeoutError: DECLARED_WALL_BUDGET_EXCEEDED`. This decision is recorded before any continuation. The original 5400-second phase, raw result, first failure, and numerical acceptance criteria remain unchanged.

Required order: original terminal raw dual backup → actual terminal manifest validation → one new output directory and one additional BDF initialization → terminal raw dual backup → actual-chain independent review → diagnostic postprocessing/comparison. The prospective code review is `../review/WALL_RESUME_CODE_REVIEW.json`; it does not establish actual restart parity.

Do not continue a live process, a complete trajectory, a solver minimum-step failure, or a physical-domain failure. In particular `GAUSS1_TIGHT` is excluded. Do not repeat a prior phase or add a second continuation. One BDF step and serialization may extend past the loop's wall-clock check, as in the original driver.

The new phase must carry all original state/counters, ledger origins, extrema, source/grid/operator identities and saved epochs. The extra restart boundary is measured and included in conservation maxima. The original failure stays preserved. This is a fresh BDF initialization at a saved state, not restoration of BDF internal history.

Any resumed history remains diagnostic and cannot inherit time convergence or scientific admission. The G1 number-ledger failure and independently established source-pair spectral failure already prevent Q1A admission. The purpose of finishing G2 is to measure its coupled response over the requested whole interval, not to waive those failures.

RUN002, EVENT003 and Q0 replay count remains zero. BASS native reception and the Bianchi comparison stay on HOLD.
