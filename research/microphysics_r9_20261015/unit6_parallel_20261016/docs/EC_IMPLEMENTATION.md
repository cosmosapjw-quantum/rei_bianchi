# Conditional Be7 electron-capture bridge: observed implementation

`code/ec_bridge.py` implements the frozen `spec/EC_CONTRACT.json`: exact
no-shakeoff event counts for prescribed, frozen hazards; the eight permitted
bound/continuum capture maps; signed electron rewards; the nine-population
column generator; and independent compensated Poisson uniformization with
split exposures. Bound capture from bare Be4 is rejected, and continuum
capture from neutral Be0 is rejected as an excluded Li-minus channel. Negative
or nonfinite inputs and inadequate free-electron budgets are rejected. A
permitted roundoff-level negative electron remainder is returned raw rather
than clipped, with the signed event delta retained separately.

The donor adapter preserves the original 17 states and adds five Be charge
states, giving 22 populations. Be7 is moved out of the former excluded
reservoir exactly once; every other excluded nuclide is retained. The original
donor normalization defect, +1.6262546864709293e-12, is reported without repair.
The packaged donor at `inputs/laneC/R5_DONOR_BBN.json` matches frozen SHA256
`47f93645a4c4fbcba0a6c3d1a9f8290adf847f011ab04d29b448633ec8525417`;
the original donor path and source commit are retained in the execution receipt.

The report includes actual-donor bound-Be3 and continuum-Be4 exposure families,
an analytic complete-conversion limit, and the conditional hydrogenic 106.4-
and 212.8-day anchors. The clock assumes prepared Be3 and fixed statistical
hyperfine populations with no charge exchange or continuum capture. It does
not identify a cosmological epoch, reconstruct recombination, or assign one
rate to every charge state. Prescribed continuum density remains separate
from the stoichiometric electron ledger. No native17 evolution or physical
shakeoff kernel is implemented. Actual heat is null with status
`NEEDS_ENERGY_PARTITION`; the energy identity fixture is explicitly synthetic.

## Reproducible commands

From the packaged project root, write a new standalone JSON report using:

```sh
python code/ec_bridge.py --donor inputs/laneC/R5_DONOR_BBN.json --out NEW.json
```

`NEW.json` must not already exist. The bounded validation command is:

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 timeout 29s \
  python -m unittest discover -s tests -p test_ec_bridge.py -v
```

The validation writes `evidence/EC_RESULTS.json`; its raw executed output is
retained in `evidence/EC_TEST_LOG.txt`. These commands document reproducibility;
no further execution was performed when writing this note.

## Observed bounded validation

All six unittest methods passed. The raw unittest runner reported 0.149 s;
the independently recorded internal validation interval was
0.1430517519984278 s. These are distinct timing scopes.

The suite exercised all eight channels separately at unit and donor scale,
zero hazards, competing channels, split uniformization, forbidden channels,
electron-budget failure, raw roundoff-level electron deficits, the complete
donor inventory, exposure families, conditional clock anchors, prescribed
density, and the synthetic energy identity. The largest reported omitted
Poisson-tail bound was 9.72483562957141e-15. The largest absolute cross-method
population gap was 1.2878587085651816e-14 on a unit-scale fixture; it satisfied
the frozen relative-plus-absolute criterion. Donor-scale comparisons used
the separate donor event tolerance and signed deltas, avoiding subtraction of
nearly equal order-one electron backgrounds.

Requested executor model: `gpt-6.1-sol`. Observed runtime model: `UNKNOWN`.
Runtime, input identity and numerical observations are preserved in the JSON
receipt. No physical Hamiltonian action, NCP execution, active-runner change,
or model/tolerance change was performed.

`scientific_admission: PENDING_INDEPENDENT_REVIEW` in the saved
`EC_RESULTS.json` identifies the pre-review execution receipt. The final
independent scientific review supersedes that admission field; the receipt
is retained as the contemporaneous execution record.
