# R2B-R1 results and verdict

## Result

Both missing inputs identified by the merged R1B-R2B fail-closed audit are now
locked under explicit, predeclared assumptions.

### Initial state

- nodes: `46,080`;
- source: exact `CANONICAL_DIRECT_REEVOLVED` row at `z=6`;
- H nuclei residual: `0`;
- He nuclei residual: `0`;
- total resolved-energy residual: `0`;
- largest initial species-fraction residual: `4.603e-12` (`x_HeI`, cancellation-sensitive);
- minimum species count: `1.462e-154 cMpc^-3`;
- minimum temperature: `2096.739 K`;
- one global thermal normalization: `0.8332361108740668`;
- clipping/per-node fitting: not used.

### Full forcing and owner-law audit

- canonical forcing rows: `85`;
- owner rows: `1,360`;
- owner/node allocation cases: `1,360`;
- maximum owner-opacity residual: `2.136e-16`;
- maximum owner-current residual: `2.372e-16`;
- maximum node-allocation residual: `0`;
- maximum snapshot closure residual: `6.421e-12`;
- negative allocations: `0`;
- zero-support nonzero allocations: `0`;
- structural-zero violations: `0`.

All 15 predeclared state perturbations changed the corresponding supported owner
fraction and deterministic node hash in the expected direction. The two
non-production subgrid auditors differ substantially from the primary lane:

`0.2020 <= TV <= 0.6089`.

They therefore remain systematic auditors and are not selected post hoc.

## Independent verification

Decimal-90 replay closes owner opacity/current and structural zeros below the
predeclared `1e-11` gate. Wolfram returns exact zero owner-sum, thermal-closure,
and structural-zero residuals and confirms nonnegative allocation and supported
state sensitivity. The adversarial audit rejects negative material state,
negative authoritative opacity, and nonzero targets on zero support.

## Claim boundary

The global canonical opacity/current amplitudes remain inherited. The explicit
atomic responses and node measures are state-derived; the global effective-HI
subgrid amplitude remains externally locked. The initial thermal field uses a
fixed hierarchy shape and one global normalization. No time history, fixed
point, cooling history, or production node chemistry is integrated here.

## Verdict and authorization

```text
DURABLE_PASS_R2C_R1B_R2B_R1_CANONICAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK_R2B_R2_AUTHORIZED
```

`R2C_R1B_R2B_R1_completed=true` and `R2C_R1B_R2B_R2_authorized=true`.
Production node chemistry, R2C-R2, B2C2B, recombination splice, CAMB transfer,
and Bianchi feedback remain unauthorized.
