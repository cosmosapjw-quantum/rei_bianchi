# Lane B execution (independent scientific review pending)

The frozen three-state trace-kinetic equations were implemented in `code/laneB/run_kinetics.py`. The production and refinement runs use independent positive reward accumulation; the two Radau runs use the full three-state differential generator and analytic Jacobian, without the production propagator. No clipping or renormalization occurs. All 59 donor species enter the charge sum.

The immutable donor was copied mechanically to `inputs/laneB/R5_DONOR_BBN.json`, with SHA256 `47f93645a4c4fbcba0a6c3d1a9f8290adf847f011ab04d29b448633ec8525417` equal to the original frozen Unit6 input. The portable input is preferred, with original-path fallback. Unit6 and external runners were not edited. Original/copy path mapping is in the result JSON.

Commands (from the Unit7 root; Python itself enforces the 30-second alarm):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests/laneB -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/laneB/run_kinetics.py > code/laneB/raw/run_stdout.json 2> code/laneB/raw/run_stderr.txt
```

Requested executor: gpt-6.1-sol; observed runtime identity: UNKNOWN. Authority requested: Astra; observed identity UNKNOWN. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0; internal environment also sets MKL and NumExpr to one thread.

Numerical wall time: 0.840481499 s (production 0.064165351, refinement 0.030302629, Radau starts 100000/200000 0.327698673/0.376388998). The combined test and run shell process took 1.602995527 s. No 60-second extension was needed. Saved raw arrays include production, refinement, both reference grids and internal reference steps, and both closure reductions.

All frozen numerical checks pass. z10/z50/z90=31203.45894/29307.17654/28211.33004; Ye=0.8765521883879055; N0=9.3837938560062941e-17 cm^-3. Maximum F/Be3 differences versus Radau are 7.6392376e-08/3.02141318e-06; refinement differences 2.29215446e-07/3.01779804e-06. Start-test F difference 2.6981587e-10, donor-to-start analytic combined bound 1.21253253e-09, QSS F error 2.92635392e-07, simple-closure F error 2.46083527e-07.

The final separately propagated survival a+b underflows to zero. Raw F_end=0.99999999999978506, so 1-F_end=2.14939178e-13 is floating accumulation/closure residue, not a resolved surviving physical fraction. The maximum population-sum residual is 2.15938378e-13; no endpoint replacement was made. The prescribed trace-bath fractional bound is B/Ye=4.31804779e-10. No claim of self-consistent bath closure, atomic-model uncertainty certification, continuum capture, second electron, late history, physical heat or H/NCP follows.

Two targeted tests pass. Before independent authority review, the initial donor-count test fixture assumed 64 species and failed against the actual immutable donor's 59; that unsupported test integer was corrected to 59. The original failure is preserved in `code/laneB/raw/test_first_failure.txt`. This was a test-fixture correction, not a model/solver/tolerance change and was not pre-approved by authority. No production/reference run failed or was repeated. The final two-test log was captured again without rerunning production/reference kinetics; that shell process took 0.300857126 s. This report is observed execution evidence, not scientific admission.
