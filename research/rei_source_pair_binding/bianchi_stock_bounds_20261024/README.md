# Conditional Bianchi I cohort stock bounds — static preparation

This unit implements the frozen `authority/IMPLEMENTATION_CONTRACT.json` and
`authority/THEORY_KO.md` for a supplied finite positive cohort with moments
`N,U`, energy support `[0,L]`, rest energy `M>0`, and three prescribed positive
axis ratios `a_i(s)/a_i(t)`. Inputs are represented exactly as `Fraction` values.
Finite floats retain their represented values; this does not recover prior
rounding or physical precision. There is no provider fetch or unit conversion.

`kinetic_map_interval(k,M,r,bits=128)` encloses the transformed kinetic energy
using an integer `isqrt` grid and the cancellation-free rationalized formula.
`bits` is an integer in 1..4096, an absolute square-root grid resolution in the
input energy unit. It is not a physical tolerance or a bit-exact energy-unit
scaling guarantee. Exact zero and identity-ratio cases remain exact.

`stock_bounds(N,U,L,M,ratios,bits=128)` returns the frozen `StockBounds` fields:
`number_density`, `dilution`, `energy_interval`, `support_upper_enclosure`,
`lower_energy_bound_enclosure`, `upper_energy_bound_enclosure`,
`pressure_trace_interval`, `sqrt_bits`, and `claim`. All numerical endpoints are
Fractions. The lower/upper sharp-energy endpoint enclosures preserve arithmetic
width separately from the interval due to unavailable distribution information.
The actual outer energy upper endpoint also respects density times upper support.
Zero moments bypass divisions while support is still mapped.

Energy sharpness is conditional on unrestricted angular positive measures;
the pressure-trace interval is conservative and has no sharpness assertion.
Pressure means `Tr(P)/3`; it does not assert `P_ij=Pi delta_ij`. No actual HI
history, cosmological scale history, initial stock, stopping, heat deposition,
Einstein closure, or L4 admission is supplied. Background ratios are caller data.

## Current execution boundary

**STATIC_PREPARED_UNEXECUTED.** Candidate, fixture and runner imports,
compilations, tests and scientific executions during preparation are zero.
The previous pressure one-child release is consumed and does not release this
new candidate. `PROPOSED_EXECUTION.json` remains `PROPOSED_NOT_RELEASED`.
Separate root authorization and independent review are required before the
future command in that proposal is executed. A future fixture pass would only
validate its finite prescribed cases, not every valid input or physical model.

One future fixture group covers exact identity, expansion/contraction/mixed-axis
radical enclosures through independently written rational squared inequalities,
tiny positive kinetic energy, zero boundaries, named invalid cases, and common
weight scaling. Fraction values in its future stdout use numerator/denominator
strings. It does not import the private production square-root helper.

The prepared runner follows the existing one-child pattern: child CPU soft=hard
1 second, launch-inclusive wall 5 seconds, no automatic retry. An exclusive
`raw/attempt.json` records even a failed launch. It prevents accidental reruns
for reproducibility; it is not an authorization token or security mechanism.
Actual raw output and resource accounting are written only upon a separately
released execution. Historical CPU usage is not reset, transferred or assumed
zero; parent/model/I/O/remote costs remain separate and unmeasured.

Requested executor: `/root/pressure_coding`, `gpt-6.1-sol/high`. Actual backend
model and reasoning effort are unknown. Scientific admission belongs to root.
