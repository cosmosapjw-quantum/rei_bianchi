# Validation report

## Physics and data validation

- state rows audited: 1,382,400;
- active group rows audited: 2,764,800;
- macro cases: 540;
- endpoint state/sign/finiteness failures: zero;
- current–Gamma maximum relative residual: `9.14346125991477526e-16`;
- locked-moment maximum relative residual: `3.54050745805448292e-14`;
- convex endpoint/cap segment failures: zero of 540;
- six mass Farkas endpoint/cap audits: six of six pass;
- inherited Farkas partition: 491 radiative plus 6 mass, total 497;
- independent validator: `TRUE`;
- exact/high-precision fallback: `TRUE`.

## Tool status

- Native Wolfram executable/plugin: unavailable in this runtime. A complete
  `.wl` validation script is retained; no native execution claim is made.
- Precise Special Functions plugin: not exposed in this turn. mpmath at 100
  decimal digits is retained as an explicit fallback.
- GitHub read-only native probes: attempted for both private repositories;
  both failed at DNS resolution. No push was attempted.
- Coding harness: deliberately not applied.
- Research harness: contract, evidence ledger, claim audit, hypothesis graph,
  adversarial review, negative-result preservation, decision, and closeout
  were all completed.

## Fresh command set

```bash
python stages/.../analysis/run_node_local_physics_audit.py \\
  --repo . --state /mnt/data/node_state_lift.csv.gz \\
  --groups /mnt/data/node_group_lift.csv.gz \\
  --output stages/.../data

python stages/.../analysis/audit_convex_endpoint_segments.py
python stages/.../validation/exact_symbolic_fallback.py
python stages/.../validation/independent_validate_stage.py
python scripts/verify_repo.py
sha256sum -c stages/.../SHA256SUMS
```

The final durable receipt logs retain the exact expanded paths and exit codes.
