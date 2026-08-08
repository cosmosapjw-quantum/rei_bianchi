# Results and verdict — R2B-R2A-R2-R1A

## Verdict

```text
DURABLE_FAIL_CLOSED_R2_R1A_CORNERS_NARROW_BUT_CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED
```

This is a durable fail-closed preflight with a positive result on every numerical and ownership gate. It is not a production-history pass.

## Science matrix

- Shape lanes: `3`.
- Branch policies per shape: `8`.
- Total policy realizations: `24`.
- Load-bearing strict-corner realizations: `12`.
- Named log-linear adapter auditors: `12`.
- Full/two-half local-error gate: `<2e-4`.
- Source-model width gate: `<2e-3`.
- Hard numerical/ledger pass: `24/24`.

Maximum residuals:

```text
local error:          0.000112228944415094
H nuclei:             5.07658094662885e-16
He nuclei:            6.64559350355345e-16
owner closure:        2.05584512086091e-16
photon closure:       1.45873361987372e-16
thermal residual:     9.99980051500399e-13
PDS reconstruction:   0
OTS energy residual:  1.1060060096106e-16
minimum species:      1.40818455146094e-154
```

Maximum strict-corner endpoint widths:

```text
x_HII:    2.38896467164018e-06
x_HeII:   7.31201493386902e-06
x_HeIII:  5.37277474593756e-09
log T:    3.39994195339699e-05
```

Every width is much smaller than `2e-3`.

## Why the verdict remains fail-closed

The instantaneous branch coefficients are multi-affine in `(v,f)`, so their extrema on a fixed rectangle occur at the four corners. The integrated thermochemistry map is nonlinear and state-dependent: `v` changes with temperature-cell membership, owner fractions depend on the evolving state, and the thermal equation feeds back into later event rates. Four endpoint trajectories therefore do not by themselves prove that every admissible continuous branch history lies inside their endpoint envelope.

No monotonicity cone or validated interval/Taylor-model enclosure has yet been proved for the full coupled map. The correct durable conclusion is therefore:

```text
corners narrow: true
all numerical gates pass: true
continuous-parameter enclosure certified: false
production history authorized: false
```

## Authorization

```text
R2C_R1B_R2B_R2A_R2_R1A_completed = true
R2C_R1B_R2B_R2A_R2_R1A_R1_authorized = true
production_history_authorized = false
production_node_chemistry_authorized = false
R2C_R2_authorized = false
B2C2B_authorized = false
```

## Next bounded stage

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-VALIDATED-CONTINUOUS-BRANCH-DIFFERENTIAL-INCLUSION-ENCLOSURE-LOCK
```
