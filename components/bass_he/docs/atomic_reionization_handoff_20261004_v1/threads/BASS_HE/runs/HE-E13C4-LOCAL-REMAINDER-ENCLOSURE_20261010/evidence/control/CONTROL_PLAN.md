# E13C4 independent numerical control plan

Role: independent numerical contributor; this is not the final scientific decision review.

## Fixed scope

The owner supplies `code/directed_interval.py` and `code/local_enclosure.py`.
This contributor owns only `evidence/control/`. Checks concern directed arithmetic,
translation of the pinned coefficient definitions, and concrete domain boundaries.
No collocation, old continuous reference, Gaussian rule, new first-variation solver,
or coupled gas history is executed here. No promotion decision is made here.

## Reference construction, fixed before owner-code evaluation

Elementary references use exact `fractions.Fraction` operations. Exponentials use
a positive Taylor sum after binary range reduction and an explicit geometric
tail. Intermediate repeated squaring rounds exact rationals outward onto a fixed
decimal rational grid. Logarithms use the odd atanh series after reduction to
`[1,2)`, with a positive geometric tail and an independently bounded `log(2)`.
Square roots use integer square-root bracketing with exact inequalities.
Reference precision is 110 decimal fractional digits plus 20 guard digits.
No Decimal exp, log, square root, or noninteger power is used in these references.

Owner intervals must contain both endpoints of the independently proved rational
reference interval, a stronger finite test than checking a central approximation.
Arithmetic intervals are compared with exact rational endpoint images, including
sign changes, cancellation, small denominators excluding zero, binary64 lifts,
and low ambient Decimal precision. Invalid domains must fail explicitly.

Before evaluating the newly supplied derivative API, extend the same bounded
control to `Jet2`: compare actual first and second derivatives with independent
closed formulas for a cubic, a reciprocal quadratic, exp of a quadratic, log and
sqrt of a positive quadratic, and a positive-base noninteger power. Test `J`
against its independent exponential formula and derivatives, including the
zero-rate limit. This is needed because the owner uses interval second
derivatives to bound integration error; it does not change any physical model.

Representative physical arguments span photon attenuation near zero, density
exponents, log cross sections, `1e-18` conversion constants, square roots near zero,
and positive bases with the pinned noninteger fit exponents. These finite tests
are implementation diagnostics. Whole-interval validity still rests on the
arithmetic inclusion proof and the coefficient expression/domain proof.

Coefficient diagnostics use only `Coefficients` and its evaluator from the saved
E13C2 Decimal helper at 110-digit precision. They evaluate exactly the six captured
rows at normalized dyadic points `0, 1/4, 1/2, 3/4, 1`, compare energy/source/all
species rates with owner point intervals and containing dyadic cell intervals,
and verify inactive masks return exact zero. Shared constants, fits, gas
interpolation, and analytic FLRW definitions are explicitly disclosed. Finite
high-precision point agreement is not a proof over a continuum.

## Evidence and failures

Each actual run records contributor and owner source SHA256 values before import,
UTC start/end, Python version, command, stdout/stderr, actual process exit code,
evaluated check IDs, and first failure if any. A failed attempt is retained and
never overwritten. Repairs within this scope get a new attempt directory.

## Primary arithmetic contracts inspected

- Python 3.12 Decimal documentation:
  https://docs.python.org/3.12/library/decimal.html
  `exp` and `ln` are correctly rounded with HALF_EVEN; `from_float` preserves the
  binary64 value; quiet `copy_abs`/`copy_negate` do not round; `next_minus` and
  `next_plus` return adjacent representable values. General noninteger C-module
  `power` is only almost always correctly rounded.
- General Decimal Arithmetic specification, square-root and arithmetic rules:
  https://speleotrove.com/decimal/daops.html
  Square-root is rounded HALF_EVEN irrespective of context rounding. Basic
  operations use the exact mathematical result followed by the selected rounding.

The generic specification permits a 1-ulp error for exp/ln; their stronger
correct-rounding premise here is the Python implementation contract, not that
generic allowance. The concrete runtime and libmpdec version are recorded by the
actual run. The independence claim covers reference arithmetic, not a second
physical cross-section dataset.
