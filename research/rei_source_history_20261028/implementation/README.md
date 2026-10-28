# Source-history certificate and finite coupling

`history.py` maps the matched 201 saved eta/H/nHref epochs to elapsed proper
time. Its log-H PCHIP clock uses fixed GL8 versus GL16 validation. The declared
production and capture histories are affine in that elapsed time. Analytic
interval derivative envelopes propagate separate initial and forcing-variation
error bounds for neutron and tritium families. This path solves no physical IVP.

`evaluate.py` writes the 201-row certificate and a dense analytic first-interval
turn-on envelope; `plot.py` displays their stock/error scales and the 1% relative
criterion. Zero initial n/T stocks imply relative initial mismatch one.
Certification is at saved epochs only. Interval-wide certification is NOT_RUN.

`coupled.py` reconstructs actual old photo/RR hazards from saved M4 photons,
temperature, electron abundance, and the pinned angular geometry/provider.
Old n/T atomic and all old beta terms are excluded. Its complete 17-visible-state
operator adds dynamic fast Bn/BT and Un/UT, retaining prescribed hidden Li6.
It compiles the affine event operator and adds the quadratic n/H capture term.
This polynomial RHS supports signed implicit Newton probes without clipping.
The physical diagnostic API separately rejects negative/inconsistent fast stocks;
all transport kinetic power is computed directly as hazard times U.

OFF sets all external amplitudes and thermal/fast escape hazards to zero;
intrinsic decay, capture and selected T exchange remain. ON uses the frozen
illustrative alpha=1 sources. Both share the prescribed old bath.
The saved donor trajectory is a reference, not an exact OFF reproduction target.

One-attempt non-IVP commands, under the root's recorded allocations:

```sh
python research/rei_source_history_20261028/implementation/run_bounded.py tests
python research/rei_source_history_20261028/implementation/run_bounded.py qss_diagnostic
python research/rei_source_history_20261028/implementation/run_bounded.py saved_data_plot
```

Future pilot status: READY_NOT_RUN, subject to targeted test results. The
following three-case commands are prepared, not authorized by the non-IVP budget:

```sh
python research/rei_source_history_20261028/implementation/coupled.py --execute-authorized --case OFF_base
python research/rei_source_history_20261028/implementation/coupled.py --execute-authorized --case ON_base
python research/rei_source_history_20261028/implementation/coupled.py --execute-authorized --case ON_refined
```

Each uses Radau with scaled sparse finite-difference Jacobian, 201 matched times
and dense samples near initial relaxation scales. Base rtol/atol are
1e-7/1e-11; refined values 2e-8/2e-12. The 21 physical variables and accumulated
open-baryon/electron ledgers use the same solver. Runtime/cost is unmeasured.
A proposed maximum is 30 child CPU s / 120 wall s per case, one worker, 3 GiB,
zero retries, total reserve at most100 CPU s; this is not an active allocation.

Future acceptance: finite physical states; minimum scaled stock>=-1e-9 without
clipping; ON base/refined per-isotope normalized difference<=1e-5 including
transients; open baryon/electron balance residual<=1e-8 times the specified
stock/boundary-throughput scale. `postprocess_cases.py` uses the strictly smaller
initial-particle-stock denominator as a sufficient balance test; absolute boundary
throughput is not measured or inferred from net ledgers. Plot all17 states including LiIV;
include hidden Li6 and fast baryons in total-baryon normalization. No pilot
trajectory or calibrated source claim is produced by this unit.

The concrete future execution packet uses the following wrapper commands in
fixed order, stopping at the first error. These commands and the postprocessor
are authored only and have not been executed. `OWNER_IVP_OVERRIDE.json` must be
created by root only after an explicit owner exception to NO_MORE_IVPs; the
current non-IVP budget receipt does not satisfy its required schema.

```sh
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case OFF_base --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case ON_base --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case ON_refined --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
python research/rei_source_history_20261028/implementation/postprocess_cases.py
```

`bounded_case_runner.py` enforces each case's30CPU-second/120wall-second limit,
3GiB, one worker, one exclusive attempt marker and no retries. It records raw
stdout/stderr, childCPU, partial wrapperCPU and unknown overhead. The owner
override receipt must use schema `REI_SOURCE_HISTORY_IVP_OWNER_OVERRIDE_V1`,
status `OWNER_AUTHORIZED`, `explicit_NO_MORE_IVPs_exception:true`, an actual
`owner_authorization_quote`, the three `authorized_cases`,
`cpu_s_per_case_max:30`, `wall_s_per_case_max:120`, `workers:1`, and
`memory_bytes_max:3221225472`. This is a required future receipt definition,
not an authorization record created in this unit.

`postprocess_cases.py` consumes the saved23-row physical/ledger schema from
allthree cases. It checks finite stocks, normalized minima, exact common output
times, inclusion of201knots and initial transients, per-isotope ON refinement,
and conservative accumulated baryon/electron balances. It writes
`PILOT_VALIDATION.json`, `pilot17_populations.csv`, `pilot17_refinement.csv`,
and `pilot17_populations.png`. The CSV retains zero and signed samples; the
figure masks only values outside the logarithmic domain and inserts no floors.
All17states, including LiIV, are drawn. Total-baryon CSV normalization includes
prescribed hiddenLi6 and dynamicBn+3BT. Postprocessing itself requires a separately
recorded finite presentation allocation before future execution; no allocation
or execution is claimed here.
