# Tritium source audit and finite nuclear-network extension

The original atomic pilot's T=0 was imposed by zero initial inventory, no nuclear source variable, and a literal-zero census lift. It is not a physical finding of forbidden tritium production.

This unit preserves that old result and provides two separate runnable calculations:

- `postprocess.py`: DII-selected direct DDp/DDn tracer with exact source/decay convolution.
- `nuclear_network.py`: all 16 dossier nuclear labels, deduplicated into 13 families, plus five declared D/Li closure families. T and neutrons evolve together; all forward/inverse event extents are retained.

The second calculation is an **all-bare, instantaneous-thermalization, passive-reservoir sensitivity**, not an isotope/ion/temperature-coupled production model. All 82 saved quotient histories are reused; zero background IVPs are added. Primary anchors are continued as constant S factors or thermal 1/v laws under explicit model assumptions.

Read `REPORT_KO.md`, `NUCLEAR_NETWORK_REPORT.json`, `review/NUCLEAR_NETWORK_DECISION.json`, and `NEXT_DAG.json` for the result and actual admission. `NUCLEAR_NETWORK_CONTRACT.json` is the machine-readable 18-family rate and stoichiometry registry. `NUCLEAR_PROVIDER_INVENTORY.md` binds its sources and limits.

Execution from the repository root (only when a new computation is intentionally needed and output files are absent):

```bash
python research/rei_tritium_production_audit_20261022/postprocess.py --run
python research/rei_tritium_production_audit_20261022/nuclear_network.py --run
```

These commands use NumPy, SciPy and Matplotlib. Recorded environment: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8. Completed artifacts should be reused, not automatically replayed. The nuclear executable refuses to overwrite saved results.

The standalone delivery archive includes repository AGENTS.md, the preceding isotope-pilot code/data/results, this entire unit, and the cross-repository provider intake. No private NCP raw or telemetry is included. Delivery receipts distinguish interim size acknowledgments from final whole-download SHA256/CRC verification.

The failed linear-flux trapezoid run is retained in `numerical_repair_001/before/`. It failed the all-channel convergence check; the repaired analytic log-linear event integration retains the original 0.02 dex criterion. Event-ledger subtraction is explicitly distinguished from authoritative T/n populations, because cancellation of much larger production and decay totals cannot resolve the very small residual reliably.

