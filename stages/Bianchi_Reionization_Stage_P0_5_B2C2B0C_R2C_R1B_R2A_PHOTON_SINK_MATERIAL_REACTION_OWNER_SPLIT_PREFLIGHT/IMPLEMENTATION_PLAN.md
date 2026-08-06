# R1B-R2A implementation plan

1. RED tests: owner sums, exact subgrid zero sources, structural zeros, and unsplit-vs-split regression.
2. GREEN: pure owner-split operator and deterministic component registry.
3. Reconstruct component opacity/current on all 85 BDF forcing rows.
4. Build global and node/macro ledgers; historical subgrid priors remain separate auditor lanes.
5. Build H/He capacity certificates for `dt,dt/2,dt/4,dt/8` without clipping.
6. Run Wolfram and independent high-precision checks.
7. Run targeted, repo, SHA, archive, and clean-clone verification.
8. Promote only the bounded preflight if every hard gate closes.
