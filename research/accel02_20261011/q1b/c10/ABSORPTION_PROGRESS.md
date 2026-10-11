# C10 positive absorption

The positive moment-fitted implicit absorption functional is implemented and its four new focused tests pass. The first expected missing-module failure and successive changed-code validation logs are retained. Previous completed campaigns were not rerun.

`prepare_incident` freezes both 64/128 quadratures of the incident power law, fitting positive weights to stored N/U with a 1e-12 moment gate. The existing coordinate indicator and endpoint refusal remain. Actual native cross sections are evaluated at E=R q without energy shifts; quadrature points rounded onto native thresholds are refused without a trace.

`absorb` evaluates the backward-Euler survival and species absorption on this common measure. It checks independent per-component order agreement, number/energy pairing, and each species counter against returned K0/KE. Counter ratios use scaled denominators to avoid h*kappa overflow and avoid subtracting nearly equal incident/surviving moments.

This closes the local operator implementation and manufactured/native binding tests only. Gas coupling, full-grid use, restart integration, physical time convergence, and independent review are owned by the integration lane. No full history or new physics is admitted.

## Independent review repair

The reviewer identified an incomplete numerical gate: separate K0 and KE agreement did not control the smaller photoheat difference. A new positive HI-only manufactured kernel on 13.60–13.62 eV confirms K0 error 0, KE error 2.8750e-8, but photoheat error 3.3833e-5. The RED test records the formerly accepted candidate. Both incident and attenuated comparisons now include each KE−chi*K0 on its own fine scale at the unchanged 1e-7 criterion; chemical thresholds retain their original distinction from cross-section thresholds and no clamp is used. Five focused tests pass. The pre-repair source/tests/status are preserved under evidence/ABSORPTION_AS_RUN_PRE_PHOTOHEAT; previous coupled evidence remains bound to that source.

The same review repair now also computes direct photoheat `c sum((E-chi) sigma P)` before subtracting large summed rates. Direct and ABI-subtraction heat each receive the own-fine-scale order gate, and each coarse/fine representation must agree between the two calculations within the unchanged 1e-7 budget. Physical native kernels enforce nonnegative heat; artificial low-energy grey fixtures retain explicitly mathematical signed heat with no native physics claim. Two new RED checks showed the missing direct output and acceptance of deliberately inconsistent ABI subtraction. Seven focused checks now pass; exact final source identities and both intermediate source snapshots are retained.
