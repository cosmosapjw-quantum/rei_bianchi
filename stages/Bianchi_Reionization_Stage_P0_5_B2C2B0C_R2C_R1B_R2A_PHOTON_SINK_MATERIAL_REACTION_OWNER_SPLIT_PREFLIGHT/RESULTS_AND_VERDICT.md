# Results and verdict

## Durable verdict

```text
DURABLE_PASS_R2C_R1B_R2A_OWNER_SPLIT_REMOVES_FALSE_CAPACITY_BLOCKER_OWNER_CORRECT_R1B_R2B_AUTHORIZED
```

This pass removes the false resolved-neutral capacity blocker caused by assigning `EFFECTIVE_HI_SUBGRID` absorption to resolved H/He chemistry and resolved thermal energy. It authorizes only the owner-correct fixed-point-history stage `P0.5-B2C2B0C-R2C-R1B-R2B-OWNER-CORRECT-PHOTON-CONSERVING-NONAUTONOMOUS-FIXED-POINT-HISTORY`. Production node chemistry, `R2C-R2`, and `B2C2B` remain unauthorized.

## Complete numerical audit

- canonical forcing rows: 85
- group cases: 340
- owner-component rows: 1360
- owner-correct H/He capacity cases: 225
- owner-correct capacity failures: 0
- invalid unsplit reachable failures: 20/20
- maximum assigned/capacity ratio: 0.21997424616431271
- minimum capacity slack fraction: 0.78002575383568729
- maximum conditioned opacity-sum residual: 2.1362207401786884e-16
- maximum conditioned current-sum residual: 2.1988830676279693e-16
- maximum refinement-additivity residual: 2.6884117717741755e-16
- midpoint node disintegration cases: 100
- midpoint macro rows: 1800
- negative node allocations: 0
- zero-support allocation violations: 0
- historical subgrid-prior TV envelope: 0.2034692346855006 to 0.61267354495363524

The independently reconstructed owner sums close at `1.6415e-13` for opacity and `3.6095e-16` for current; the more stringent Decimal-90 replay gives exact zero opacity residual and maximum current residual `9.13432412973256913429386500893367035579272707820754511052680275896972550268177903544278323E-90`.

## Interpretation

The invalid unsplit lane fails because a photon removed by the unresolved subgrid sink was counted a second time as a resolved material ionization. Under the one-owner map, subgrid absorption remains in the photon-removal ledger but contributes the exact source vector `(0,0,0)` to resolved H, resolved He, and resolved thermal energy.

The raw component-opacity reconstruction differs from the inherited authoritative total by at most 0.00116979. Therefore only the conditional owner fractions are load-bearing; the canonical total opacity/current amplitude remains inherited. The canonical interval-component comparison is an auditor only and differs by at most 0.00080425.

## Scope exclusions

No H/He chemistry history, temperature history, unresolved energy reservoir, source/escape-fraction fit, recombination surrogate, CAMB transfer, or Bianchi feedback was integrated in this preflight.
