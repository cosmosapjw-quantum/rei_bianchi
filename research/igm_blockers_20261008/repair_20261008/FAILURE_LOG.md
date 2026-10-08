# Failure log

1. The historical coarse k12 failure rejected a positive subnormal HI heat term. The local photoheat repair resolved it without changing source, provider, closure or tolerances.
2. Weighted owner accumulation then preserved N while U projected to zero. Paired canonical density/owner/checkpoint storage resolved that boundary through the common k14/28/14 state.
3. Coarse k15 exposed unresolved subnormal A/B heat subtraction. A direct positive excess-energy owner resolved it while preserving the ordinary NORMAL operation order.
4. Coarse k17 then failed because scalar N/U were zero although canonical `lnN=-748.5203313766382` and `lnU=-773.0631346468055` remained finite. Attempts `repair-coarse-tracked-stock-k17` through `...k17m` are preserved. The final tracked-stock repair `...k17n` accepted without deleting the tail or changing tolerances.
5. The first final comparison `repair-comparison-48` failed because the checker treated cumulative `source_simpson128` as a phase increment. The corrected checker subtracts the two endpoint integrals; `repair-comparison-48b` passes. No state was recomputed for this checker repair.
6. The first live accepted-record replay `repair-record-replay-live` failed `CANONICAL_OBSERVATION_MISMATCH`. The durable scalar order is `[N,U,QN,QE,red,...]`, while `OwnerLedger` uses `[N,U,red,QN,QE,...]`. An explicit permutation plus final canonical-pair restoration fixed replay; `repair-record-replay-live-b` passes.

All failed receipts/logs and rejected states remain preserved. None is folded into a successful cost or claim.
