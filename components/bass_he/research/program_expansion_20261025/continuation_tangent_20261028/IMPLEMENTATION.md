# TANGENT13 implementation checkpoint

Frozen scientific authority: CONTRACT.md. Mechanical implementation consumes only the pinned QUARTIC12 saved JSON and M0475 source bytes. It neither imports predecessor science nor enumerates vertices, evaluates geometry/trigonometry, runs optimization, or mixes energies. Model execution identity is reported by the controller separately from routing requests.

`src/tangent13.py` binds both input hashes and the fixed 258 MeV/free_N16 case, extracts rows/windows/moment intervals and inherited outer vertices, performs exactly 80 rational bisections unless an exact root terminates earlier, solves the prescribed exact 3x3 dual system, constructs the contracted-data feasible square witness, checks all saved outer vertices, derives normalized coefficient bounds and moment error, and writes both minimum brackets as full rational strings with outward binary64 display endpoints and independently outward fixed decimal strings. Fraction arithmetic carries every scientific identity and acceptance check. Display floats do not affect admission.

`src/verify_certificate.py` is an independent algebraic certificate reader. It rebinds the pinned inputs and checks root polynomial/bracket/monotonicity, dual identity/multiplier signs, square identity/scale/all windows, inherited vertices and coefficient envelope, signed moment evaluations, tolerance and predecessor inclusion. It never calls root isolation, elimination, construction, vertex search, or any optimizer. This validates the saved certificate; it is not a second optimizer.

`tests/test_tangent13.py` contains eight actual unittest methods/control groups: rational square/root controls including exact termination and bad brackets/derivative; exact linear-system residual and singular rejection; manufactured cone dual and negative multiplier; independent manual signed-moment reference; source/vertex binding with corrupted vertex rejection; actual dual with sign rejection; actual square with coefficient rejection; both brackets and corrupted bound rejection. The worker constructs actual evidence exactly once before the controls and reports unittest's observed testsRun, failures and errors. No predecessor campaign is executed.

`run_once.py` creates a new output directory exclusively (existing output is an explicit refusal), sets threads=1 and AS=768 MiB, then launches and waits for one complete worker in a fresh process group. It monitors whole runner plus live/waited descendant CPU and wall time, kills the group on a cap, and preserves stdout/stderr/START/RESOURCE_RESULT. Validation caps are CPU120s/wall300s; saved-only plot caps CPU10s/wall30s. Successful and failed campaigns retain artifacts; there is no automatic retry. The parent/controller must authorize any diagnosed targeted repair.

Prepared invocation from repository root:

```
python3 research/program_expansion_20261025/continuation_tangent_20261028/scripts/run_once.py --mode validation --saved research/program_expansion_20261025/continuation_quartic_20261028/evidence/validation/initial/SAVED_PLOT_DATA.json --official official_source/M0475.x4 --output research/program_expansion_20261025/continuation_tangent_20261028/evidence/validation/initial
```

Saved-only rendering, after validation and separate controller GO:

```
python3 research/program_expansion_20261025/continuation_tangent_20261028/scripts/run_once.py --mode plot --saved research/program_expansion_20261025/continuation_tangent_20261028/evidence/validation/initial/SAVED_PLOT_DATA.json --output research/program_expansion_20261025/continuation_tangent_20261028/evidence/plot/initial
```

Current execution checkpoint: implementation prepared; static syntax compilation only; scientific campaign, controls and plot NOT_RUN pending actual S05 publication/execution pin and controller GO. Root owns theory, scientific admission, stage/remote publication and independent review.

Preexecution targeted corrections F1–F3: decimal strings now use exact Fraction floor/ceiling on a 16-place decimal grid and the independent reader checks Fraction(string) containment; whole-runner CPU includes full parent startup CPU plus waited children and final PASS also requires measured wall <= cap; plot approximate width label corrected to “Bracket width ≈”. Scientific execution remains NOT_RUN.
