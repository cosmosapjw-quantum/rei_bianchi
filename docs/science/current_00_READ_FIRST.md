# Current science state — rei_bianchi

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2A-PHOTON-SINK-MATERIAL-REACTION-OWNER-SPLIT-PREFLIGHT
DURABLE_PASS_R2C_R1B_R2A_OWNER_SPLIT_REMOVES_FALSE_CAPACITY_BLOCKER_OWNER_CORRECT_R1B_R2B_AUTHORIZED
```

The first R1B-R2 full attempt is preserved as invalid because total low-group absorption was assigned both to `EFFECTIVE_HI_SUBGRID` and to resolved material/thermal updates. R1B-R2A splits the canonical group current by mutually exclusive opacity owners before chemistry.

Complete preflight audit:

- 85 canonical forcing rows, 340 group cases, 1,360 owner rows;
- 225/225 owner-correct H/He capacity cases pass;
- 20/20 reachable unsplit first-substep comparisons fail as expected;
- maximum assigned/capacity ratio `0.219974`;
- minimum slack fraction `0.780026`;
- owner opacity/current closure at approximately `2e-16`;
- exact zero resolved H/He/thermal source for the subgrid owner;
- no clipping, owner reassignment or cross-macro transport.

The raw component-opacity amplitude differs from the authoritative total by up to `0.00116979` and is therefore used only for conditional fractions. No chemistry or temperature history was integrated.

Next stage: `P0.5-B2C2B0C-R2C-R1B-R2B-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY`. Production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB and Bianchi feedback remain unauthorized.

`rec_bianchi` is at PR-05B2/v0.60 (`c3d246ca9911b392da8c955ee0cf9a90073f7317`), with causal accepted history locked and PR-05B3 ownership swap next. It is a read-only semantic compatibility reference, not a numerical input.
