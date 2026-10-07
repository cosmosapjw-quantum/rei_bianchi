# Panel-only portable replay

Run from this additive crate directory. Rust1.94.1 and Python3.12 suffice; no mpmath/NumPy/SciPy dependency is used. Put generated outputs outside the immutable evidence directory.

```sh
rustc --edition=2021 -D warnings -O --test tests/panel.rs -o /tmp/igm-panel-tests
/tmp/igm-panel-tests --test-threads=1
rustc --edition=2021 -D warnings -O scripts/panel_probe.rs -o /tmp/igm-panel-probe
/tmp/igm-panel-probe > /tmp/igm-panel-values.csv
python scripts/check_panel.py --input /tmp/igm-panel-values.csv --output /tmp/igm-panel-oracle.json
```

The probe prints exact round-trippable binary64 input/output values. The separate checker interprets those exact binary64 inputs using160-digit Decimal and analytic exponential antiderivatives; it does not reuse the candidate Gauss quadrature. The original601 cases cover ordinary/right-front panels, β extrema/zero/β+width≈0, coordinates at the admission extrema, narrow/wide supports, interior/front restrictions, and an adjacent-f64 front sliver. The stable normalized shape is distinct from the rounded stock node: `quadrature_node()` rejects a node not strictly interior to the support.

An additional602nd fixture probes log amplitude−1e12, where a single-f64 restriction update loses a material correction. The authoritative restriction amplitude is the unevaluated `(ln_n, ln_n_lo)` pair, checked with Decimal(hi)+Decimal(lo). All consumers must preserve the pair.

Frozen checks: normalized local mean absolute error≤5e-13; log fraction absolute error≤3e-12; mean-exp relative error≤3e-12; amplitude-log-pair absolute error≤3e-12. The latter two are bounded empirical primitive gates and are not global certified error bounds.

Original logs, failed candidates, setup failures and numerical resource records remain in evidence/panel. Historical source hashes refer to historical paths/bytes; PUBLICATION_SOURCE_IDENTITY.json identifies the current relocated script bytes. Missing /usr/bin/time and mpmath were environment failures, not scientific failures. A stdlib-only measurement helper is retained as historical evidence, but its old task-relative paths do not define the portable replay.

After bounded Loop1 acceptance, Loop2 adds300 LeftFront matrix cases plus one narrow left-front sliver, for903 total cases and3612 independent components. LeftFront uses the independent antiderivative integral y exp(beta*y); ordinary/right-front historical values and the602-case loop1 pair check remain immutable in evidence. Current native tests number12.
