# Implementation and recovery record

The controller contract fixes the scientific model and gates. Requested worker:
gpt-6.1-sol/high. Observed runtime model identity is not exposed by tools.

This is the reconstructed candidate after two observed scratch filesystem losses.
Model, Jacobians, ten-case schedule, support measure and gates retain the original
recorded equations; code layout/comments were compacted. Actual reconstructed
files require independent review; byte identity to lost unpublished code is
not asserted. All reconstructed file texts were put in functions.store before
the first filesystem write of this recovery.

The first preflight failed NumPy-bool JSON serialization. Its raw logs and
actual timing were lost. The known command was timeout90s with CPU60s,
address-space1GiB, one BLAS thread. Controller now debits its 60CPU/90wall
command caps conservatively while keeping actual usage unknown. A later
recovered preflight failed MappingProxyType source-row serialization:
measured1.896731CPU/1.921681751999131wall. The earlier clean-directory smoke
passed with .051862CPU/.06518746700021438wall. Those logs were also lost in
the second scratch loss; these are observed tool-history facts, not preserved
raw logs.

Authorized repairs are NumPy scalar item conversion, Mapping-to-dict reporting,
tuple/list numeric-row comparison, and creating results before log access.
No physics or tolerance was changed. Rebuilding the lost bath drivers from
original accepted-state RHS evaluations is authorized recovery, charged anew;
it does not repeat an original coupled trajectory.

The new ledgers represent event transfer to/from a prescribed thermal bath.
They do not update temperature and are never pasted into old gas/photon ledgers.
Native fractions are retained without floor, clipping or renormalization.

## Completed execution and diagnosed presentation repairs

All ten frozen conditional cases completed once with all local invariant gates.
The saved-only analysis initially imported the donor case table because donor
code was first on sys.path; it was repaired to load this unit's exact run_cases.py
by explicit file location. The failed analysis log is preserved and charged;
no chemistry case was rerun. Root then authorized Figure01 fraction axes to use
actual values in the displayed crossing interval with modest padding. Only
saved analysis/plot regeneration was performed; raw data and all gates remained
unchanged. Exact final resource categories and case dimensions/costs are in
results/execution_summary.json, with the known60CPU/90wall original command-cap
debit clearly separated from measured current and lost-history receipts.

