# Independent frozen-opacity tail implementation review

2026-10-07. Source reviewed and independently executed: SHA-256 `ecef9e4fcf3937a4df41a1224c4167110b8c79785e391102eee17ea9c3d668e9`.

**Decision: accepted for the declared frozen-opacity, event-split characteristic primitive.** No new gas solver, inverse panel closure, projected multistep cosmological history or production exporter is certified.

## Formula and ownership checks

The code solves dN/ds=q-lambda N and dE/ds=-E at fixed characteristic coordinate. Survivor stock uses the exponential attenuation, with compensated exact-binary64 optical-depth products. Counts and energy owners are formed from independent nonnegative initial-stock and continuous-source contributions. The source time-integral formulas agree with the directly derived J(lambda,h) expressions. Small lambda*h uses convergent analytic series; the positive unit-moment series implements integral_0^1 v^m exp(-hv)dv. Species counts and energies share the same underlying count and energy integrals. Redshift work is calculated from the energy integral rather than a global residual.

All positive values retain an authoritative high/low log pair. Exact emptiness is represented separately. `log_value()` is explicitly a display/readout API; `log_parts()` and `from_log_parts()` carry physical provenance. The readout loss bounds cover represented zero/subnormal conversion, and omitted-addend bounds cover a whole dropped positive addend. The code and receipt explicitly avoid claiming those quantities bound all floating-point error, quadrature error, or physical integration error.

The generic characteristic checks the tracked energy range and rejects a segment crossing a nonzero species cutoff. Boundary export moves existing count and energy owners before clearing active stock. The caller still owns the proof that it ended at the physical cutoff; a future explicit cutoff-anchor API needs its own review. No epsilon band or silently shifted crossing was present in the reviewed source.

## Oracle and reviewer execution

The saved high-precision oracle covers 86 cases and 1118 owners, including 249 positive zero-readout owners. It evaluates exact binary64 input rates, times, initial/source log amplitudes and energy conversion using Decimal160/800 closed formulas. Its target is the physically meaningful relative error from the authoritative pair, not relative error of a large negative log. The maximum reported physical owner error is 5.109726091704207e-14 against 3e-12. Earlier single-log and insufficient-reference-precision failures remain preserved.

The reviewer separately compiled the actual module and ran a four-step source-free semigroup, using exact-binary64 h and lambda in an independent Decimal150 expected logarithm; an input log pair with high part -1e12 and low part -ln2; and a source restart. All six comparisons pass, with maximum error 4.739031053709009e-16. Further assertions cover positive zero-readout export, count/energy transfer equality, a recorded omitted tail after restart, and an unsplit cutoff rejection. Artifacts: `tail_adversarial.rs`, `tail_adversarial.log`, and `TAIL_ADVERSARIAL_RESULT.json`.

These finite checks and source derivation support the declared bounded primitive. They are not a rigorous uniform error proof for all finite IEEE-754 inputs. The primitive must be combined with actual continuous panel integration and exact event ownership before a continuous exported measure can be claimed.
