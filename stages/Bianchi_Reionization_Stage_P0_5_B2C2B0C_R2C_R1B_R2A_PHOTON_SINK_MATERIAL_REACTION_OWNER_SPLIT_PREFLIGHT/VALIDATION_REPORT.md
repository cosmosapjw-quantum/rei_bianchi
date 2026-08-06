# Validation report

- targeted stage tests: `15 passed`
- independent validator: `PASS`
- Decimal-90 owner replay: `PASS`
- Wolfram symbolic owner sums, common flux, structural zeros, capacity implication, and interval additivity: `PASS`
- Precise Special Functions 100-digit Gamma and hypergeometric auditor: `PASS` (non-load-bearing)

Independent maximum residuals:

```text
opacity closure:   1.6414771017406256e-13
current closure:   3.6094251999382898e-16
refinement total:  2.8425831845542032e-16
node sum:          1.9697631035994148e-16
```

The full repository suite, stage SHA audit, compact-ZIP CRC, Git integrity, and clean-clone bundle test are executed after final packaging and recorded in delivery receipts.

## Repository regression before immutable packaging

- `python scripts/verify_repo.py`: PASS; 48 in-main artifacts
- `pytest -q`: 80 passed

Final stage SHA, compact-ZIP CRC, Git integrity and clean-clone bundle checks are performed after the last manifest build and recorded outside the compact artifact to avoid self-referential mutation.
