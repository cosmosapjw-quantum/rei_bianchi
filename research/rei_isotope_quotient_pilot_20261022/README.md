# REI isotope quotient atomic test-fluid pilot

This self-contained offline directory executes the inherited z=20→2 LRS Bianchi I pilot. The nine elemental charge fractions reconstruct all 21 requested n/H1/D/T/He3/He4/Li6/Li7 heavy-particle outputs. Neutron and tritium states have zero initial inventory and remain absent in this selected atomic network. `ElementalElectronicEquality` is the explicit isotope-rate approximation; nuclear reactions and a thermal/radiation energy equation are not supplied.

Run from this directory with installed NumPy, SciPy, Matplotlib and Python:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python pilot/code/run.py all --workers 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python pilot/code/run.py audit-existing
```

The recovered `all` command validates the retained point checks, profile, reference, 82 quotient receipts and three controls. On this complete tree it returns without running an IVP or rewriting the saved summary, receipts or figures. It can resume missing quotient cases within the frozen limits when the retained prerequisite evidence is present; a clean empty bootstrap is outside this recovery. The `audit-existing` command verifies source and saved NPZ hashes without an IVP. `checks`, `profile`, `controls`, `sweep`, `reanalyze-profile`, and `summarize` remain separate finite actions. Do not invoke `checks` or `profile` on this completed result tree: immutable receipt paths already exist.

`pilot/summary.json` requires 82/82 saved quotient histories, 3/3 L24 controls, passed point checks and all trajectory gates for its scoped numerical PASS. `pilot/summary.csv` contains actual signed initial/final axes and execution counters. The 83rd IVP is the independent 18-fraction isotropic reference. Raw arrays and immutable case receipts are in `pilot/results`; the profile's original raw pair was independently reanalyzed over all 18 fractions in `profile_existing_reanalysis.json`, with no repeat IVP. Historical final expected hashes remain in `SOURCE_MANIFEST.json`; current recovered runner and source hashes are in `delivery/RUNTIME_RECOVERY_CURRENT_MANIFEST.json`.

The summed 83 per-case CPU receipts are 211.72 seconds; the bulk stage elapsed 46.82 seconds. Import/check/plot overhead was not separately metered, so the CPU sum is not an overall job CPU total or a general speedup claim. Independent review admits the scoped preliminary atomic test-fluid result. The full 19-channel target (3 atomic, 16 nuclear/capture/decay) is a separate unresolved obligation.

## Nuclear-source continuation

The historical T census is structurally zero and must not be read as a computed nuclear-production prediction. The continuation in `../rei_tritium_production_audit_20261022/HANDOFF.json` evaluates all16 dossier nuclear labels plus five declared closure families under a separate conditional model; historical atomic outputs and their admission remain preserved.
