# Native HI finite atom source

Status: C1–C5 prepared; no scientific import, fixture, or runner execution yet.
The frozen contract and derivation are in `authority/`. The exact full donor CSV
and unchanged historical source card are in `inputs/`. Existing source APIs,
admissions and raw outputs are unchanged.

`native_source.py` exports the five contracted functions:

- `load_selected_atoms(path=None, channel='HI', redshift=2.479)` verifies pinned
  bytes and returns the 4,368 ordered `(kinetic, weight)` represented Fractions.
- `native_moments(atoms, threshold_eV=13.6)` returns immutable A/K/B/P moments.
- `source_per_href_native(moment, X_HI, a=1)` applies exact `a*X_HI` once.
- `source_jvp_native(moment, X_HI, dX_HI, a=1, da=0)` uses signed exact
  `a*dX_HI + X_HI*da` for fixed atoms.
- `rounding_decomposition(atoms, source_card, threshold_eV=13.6, moment=None)` reports the
  four exact summary deltas, provider RN stages, finite fsum certificates,
  unchanged donor residual, and the original bin selectors. The fixture passes
  its already computed immutable moment to reuse the real-atom exact sums;
  direct callers can omit this optional same-atom moment.

Optional function arguments after `*` are keyword-only. API numerical inputs
accept finite int/float/Fraction and refuse bool, nonfinite values and invalid
signs. Synthetic atoms are explicit callers' inputs, distinct from the pinned
loader. Sources contain exact and rounded vectors, per-component exact rounding
errors and half-adjacent-gap budgets, exact ledger residuals, and zero/subnormal
or underflow tags. Rationals serialize with numerator/denominator strings via
`jsonable`. Energy and particle order is fixed in the module constants.

`focused_check.py` plans one fixture group over the real finite atoms, with an
independent integer-dyadic moment accumulator, actual provider arithmetic
decomposition, bins, hand two-atom case, normalization, signed JVP, exact tiny
underflow, subnormal behavior and explicit input guards. No donor quadrature,
historical suite or historical admitted fixture is invoked.

After independent static review, root freezes `PROPOSED_EXECUTION.json` and
writes leaf `ROOT_GO.json` containing `{"authorized": true,
"proposal_sha256": "<exact proposal sha256>"}`. The only released command is
`python3 run_focused_once.py` from this leaf. It permits one child with CPU
RLIMIT=2 seconds, wall timeout=10 seconds and no automatic retries. Any result
returns to root; the runner reports execution and never scientific admission.
Raw attempt/stdout/stderr/resource receipts are preserved under `raw/`.

This represents a finite per-target source at the pinned redshift and declared
isotropic closure. Density/time/IC/geometry/transport and actual secondary heat
remain separate physical inputs; no evolution solution is implemented.
