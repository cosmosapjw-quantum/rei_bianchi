# C10 source-entry lane

Stage: implementation/validation complete within the source-plus-redshift scope.
The parent owns durable publication, native gas integration and independent review.
Baseline: C09B `3581a23606499c7a40d6d33f3dcfc75fed0bca4e`.

`source_entry.py` implements positive Gauss time integration of the actual cell
source, its q moment, injected energy, and physical radiation-work integrand.
`advance_source` applies N=N0+dN, Q=U0/R0+dQ, U=R1 Q and preserves the physical
work counter separately from its checked energy residual. A source-free cell
remains exactly empty. No origin Jacobian, floor, clipping or photon seed is used.
`provider_event_times` finds emissivity spectral-knot/source-band cell crossings
and redshift interpolation knots; native/gas events remain the caller's duty.

Five new tests pass. They use independent 70-digit Decimal integrals, zero
source, an explicit discontinuity event, invalid moment rejection, and grey
birth survival at a common endpoint with64/128/256steps. The measured ratios
pass1.97–2.03, as expected for the first-order implicit grey sink. The first
test attempt wrongly bounded the 1/3-limit correction by lambda*h/20; its
independent expansion is -lambda*h/12. Correcting that fixture bound to
lambda*h/10 did not change any scientific or implementation tolerance.
Both the initial import failure and first fixture failure remain in raw logs.

Actual C2 source-only interval evidence:

| Interval h (seconds) | Maximum order16/32 relative discrepancy | Outcome |
|---|---:|---|
| 1e10 | 9.373753e-11 | PASS |
| 5e9 | 2.752257e-10 | REJECT |
| 2.5e9 | 3.139086e-10 | REJECT |
| 1e11 | 1.360779e-11 | PASS |
| 5e10 | 2.083839e-11 | PASS |
| 2.5e10 | 4.638462e-11 | PASS |

Every metric uses that cell's own fine amplitude; a zero fine value requires
exact zero. The local time-quadrature gate is1e-10 and local pairing is1e-12.
At2.5e9 the physical work integral alone fails. Small source-band widths and
subtraction R(t)-R1 are consistent with the observed conditioning limitation;
no rigorous source-provider roundoff bound has been established. In particular,
passing a larger h does not authorize taking that step in the coupled gas
solver. Splitting/time-error admission is a separate required gate.

A new source-only common-endpoint1e11 test with1/2/4steps confirms accumulated
work and moment consistency: maximum own-fine difference is7.012776e-12.
The newly born C2 cell has qleft=50000eV, initial N=0, final per-angle
N=9.4260246853e-21 reference cm^-3 and mean q=50000.143910086eV, obtained from
the integrated source. Its reachable width is0.43172996561eV; the measured
relative mean is0.333333559085, never imposed as a seed.

No RUN002, EVENT003 or Q0 was replayed. Saved C2 IC arrays were reused.
No native calls, gas solve, opacity test or physical full-history run occurred
in this lane. The provider and frozen scientific acceptance criteria were not
changed. Actual source comparisons share the pinned HM12 interpolation and
are numerical consistency checks, not independent physical-data validation.

Evidence and identities are in `SOURCE_ENTRY_ACTUAL.json`, the semigroup NPZ,
all raw logs, and `SOURCE_ENTRY_INDEX.json`. `../reproduce_source_entry.py` was
reconstructed after execution from the actual inline operations. It is an
executable reproduction driver, not the original as-run inline command text.
Only compilation was checked; the completed diagnostics were not repeated.
It verifies the saved input/provider hashes and refuses an existing output
directory. It emits interval diagnostics, semigroup diagnostics and arrays,
and `SOURCE_ENTRY_REPRODUCTION.json` with frozen-gate comparisons and the
expected interval pass pattern `[true,false,false,true,true,true]`.

From the repository root, when a fresh replay is explicitly needed:

```bash
python research/accel02_20261011/q1b/c10/reproduce_source_entry.py --output-dir /tmp/q1b_source_reproduction_NEW
```

The directory suffix must identify a fresh location. Exact binary agreement
with archived floating-point results is not required; the unchanged gates and
explicitly preserved rejection pattern are required.
