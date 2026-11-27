# Rice2000 constrained-P2 fast-D pair covariance certificate | BASS_HE independent child

Research parent PR127 `b1733cc18180eeffc90a5ce5eac9ff2feab90d36` -> isolated add-only child. **New output is conditional nuclear-birth physics, not a source-owned target-epoch high-energy photon history**. No production, merge or ancestor changes.

**New numerical physical results:** one-daughter mono-E PDF, exact two-daughter covariance theorem for arbitrary unknown nonnegative source-bin energy weights, 2 sharp negative covariance upper bounds (MeV²), 2 angular moment thresholds Acrit, 10 source-bin fast-D above-threshold daughter multiplicity ranges for thresholds 60/80/100/120/140 MeV, each conditioned on original Rice2000 `constrained P0+P2` bin angular shape holding at every E. Source Paper Table I and II original Git blobs byte-exact copied from PR125. No new independent experiment claimed.

Reproduce from package root:

```bash
bash REPRODUCE.sh
```

Expected outputs: `results/CONDITIONAL_PAIR_CORRELATION.json`, `results/PAIR_COVARIANCE_2BINS.csv`, `results/DFAST_TAIL_10.csv`. Verification includes baseline PR127 source restore 19/19 reused in evidence log, current Python targeted 13/13, Wolfram second independent symbolic and numeric checks. All results inherit `model_conditional` scope. GitHub stage-file commits and provider backup verification in `notes/DELIVERY_RECEIPT_KO.md` only if actually executed.

**Protected DAG:** Central 28/88; HE physical 14/18; Rice birth 1/2; Rice 1998 Table5.2 source reconciliation 2/2; new local auxiliary conditional covariance unit 1/1 (when tests pass), canonical physical delta 0; `kappa=null, R_event=null, heat_rate=null, L4=false, PRODUCTION=HOLD`.
