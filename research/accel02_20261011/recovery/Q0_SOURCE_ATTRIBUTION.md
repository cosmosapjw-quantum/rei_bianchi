# Q0 source/initial-field quadrature attribution

Status: computed without ODE or native RHS/SIGMA calls. The source is unchanged. Both saved grids use the same pinned HM12 tables and the same actual source function. All129 epochs and the original65 subset are retained in the companion JSON.

The analytic reference is exact up to floating-point roundoff for the declared piecewise-linear HM12 interpolation, not for a physical continuum model. It uses `HM12Table.moment`; FLRW source reference density is a_rel^3 times proper density. No native cross section is replaced.

## Instantaneous full-band source errors

Errors below are max|sampled-exact| / max|exact| across the129 epochs. They are attribution diagnostics, not replacements for the formal spectral pair test.

| Energy bins | Number, reference | Energy, reference | Number, proper | Energy, proper |
|---|---:|---:|---:|---:|
| 128 | 0.1031555 | 0.078948203 | 0.0606195367 | 0.0365879532 |
| 256 | 0.0508063888 | 0.0396376175 | 0.033261913 | 0.0209086851 |

## Initial UVB errors

The initial radiation is independently discretized. These are signed relative errors against the exact declared interpolation at z=15.9.

| Energy bins | Full-band N | Full-band energy | HI-ionizing N | HeI-ionizing N | HeII-ionizing N |
|---|---:|---:|---:|---:|---:|
| 128 | 0.00081327217 | 0.0169017896 | -0.0488387291 | -0.0961878644 | 0.000290906727 |
| 256 | 0.173214717 | 0.165465267 | -0.00359073714 | -0.0262001954 | 0.000184078462 |

## Arithmetic and interpretation

Both tables have zero positive decimal literals silently parsed as zero. The complete UVB table includes subnormal ordinates outside the relevant rows/initial-redshift columns. The relevant UVB inputs have minimum positive native ordinate7.965e-34; native zeros remain zeros. The source inputs over the relevant band and redshift columns have minimum positive native ordinate1.686e18. No relevant underflow or floor is used; interpolation is linear in ordinates, including zeros, and native jumps have zero integration measure. All source sums reproduce the prior event-aware saved-state postprocessing within the recorded roundoff check.

A nonzero source-only error is established independently of gas feedback. Initial UVB discretization also has directly measured error. These findings do not uniquely explain the evolved Gamma, temperature or ion-fraction discrepancy. The next patch must propagate any improved quadrature through the common photon/gas/counter operator; changing only a plot, Gamma diagnostic, or source counter is not allowed. The Q0 results do not relax any scientific gate or admit CR/RCT/secondary physics.

See `Q0_SOURCE_ATTRIBUTION.json` for threshold-selected source moments, signed errors, locations,129/65 epoch summaries, input hashes and full histories.
