# C10 positive absorption

The positive moment-fitted implicit absorption functional is implemented and its four new focused tests pass. The first expected missing-module failure and successive changed-code validation logs are retained. Previous completed campaigns were not rerun.

`prepare_incident` freezes both 64/128 quadratures of the incident power law, fitting positive weights to stored N/U with a 1e-12 moment gate. The existing coordinate indicator and endpoint refusal remain. Actual native cross sections are evaluated at E=R q without energy shifts; quadrature points rounded onto native thresholds are refused without a trace.

`absorb` evaluates the backward-Euler survival and species absorption on this common measure. It checks independent per-component order agreement, number/energy pairing, and each species counter against returned K0/KE. Counter ratios use scaled denominators to avoid h*kappa overflow and avoid subtracting nearly equal incident/surviving moments.

This closes the local operator implementation and manufactured/native binding tests only. Gas coupling, full-grid use, restart integration, physical time convergence, and independent review are owned by the integration lane. No full history or new physics is admitted.
