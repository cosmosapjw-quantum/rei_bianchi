# SCIENTIFIC CONTRACT — LCV-ODE N SHADOW

## Identity and authority

- Stage identity: `LCV_ODE_CORRECTED_SCIENCE_V2_CANDIDATE`.
- Operational type: `ARITHMETIC_SHADOW_V2` plus fail-closed contract tests.
- Repository binding at creation: HEAD
  `111b6ace750e36e218df7fc9626c6bad2ec19971`.
- This stage is additive and is not routed into the active adaptive-history,
  parity, package, BDF, endpoint, or publication path.
- A passing test authorizes only the named primitive or state transition. It
  does not authorize a corrected trajectory or scientific endpoint.

## Mathematical and representation conventions

### Exact finite algebra

Finite binary64 values are decoded by `float.as_integer_ratio()` or its exact
equivalent. Decimal text is parsed separately; the intended decimal `0.079`
and the binary64 value produced by `float("0.079")` therefore retain different
provenance even when displayed alike.

For an exact rational endpoint `q`, outward export compares the nearest
binary64 value `f` with `q` exactly. The lower endpoint is moved toward
`-infinity` iff `f > q`; the upper endpoint is moved toward `+infinity` iff
`f < q`. A finite exact result outside the finite binary64 range is a typed
overflow, not a usable infinite enclosure.

The algebraic scope includes interval add, subtract, multiply, divide away
from zero, integer power, and signed sum under fixed term/bit ceilings.
Transcendentals (`exp`, `log`, non-integer power, and similar operations) are
`UNSUPPORTED_TRANSCENDENTAL` until a version-qualified outward backend is
owner-approved. There is no NumPy fallback after that status.

### Exact point-linear certificate

The certificate adapter accepts only point intervals, dimensions at most
three, and finite exact coefficients. It establishes a nonzero exact
determinant, solves by exact rational elimination, recomputes `A x - b = 0`
exactly, exports each coordinate outward, and binds a canonical input digest.
An independent validator recomputes determinant, residual, bounds, and digest
without importing candidate arithmetic code.

This is not an interval Krawczyk implementation. Any nonpoint matrix or right
hand side is explicitly unsupported, so the active interval map remains
blocked from using this certificate as a general replacement.

## Physics convention and dimensional audit

For species `s`, define the absorber inventory per hydrogen nucleus

`r_s = N_s / N_H`, with `N_H > 0`.

The N-shadow raw opacity measure is

`kappa_s = scale * sigma_s * r_s`.

`N_s` and `N_H` are counts in the same cell/volume, `sigma_s` is the bound
cross section, and `scale` carries whatever common path-length/physical-density
conversion is required so that every `kappa_s` has the same declared opacity
unit. The helper does not infer units; the caller must bind them.

For He II, if `x_HeII` is explicitly the fraction within helium and
`Y_He = N_He/N_H`, then

`N_HeII/N_H = Y_He * x_HeII`.

Consequently the abundance conversion occurs exactly once. In the pure-He II
limit (`x_HeII=1`) with decimal `Y_He=0.079` and unit cross-section/scale, the
coefficient is `0.079`, not `0.079^2 = 0.006241`. This conclusion is
`DERIVED` under the declared per-H number-density convention; selecting that
convention for an active corrected lane still requires model-owner authority.

For positive total opacity `K = sum_s kappa_s`, every absorber share is formed
directly:

`p_s = kappa_s / K`.

No share is obtained as a floating complement and no `1e-300` floor is added.
Nonnegative measures imply `p_s >= 0` and exact rational arithmetic gives
`sum_s p_s = 1`. If `K=0`, shares are undefined and a typed vacuum outcome is
returned. This stage does not silently choose whether vacuum photons escape,
are retained, or block a step.

### Boundary and limiting cases

- `N_H=0`: per-H normalization is undefined and fails typed.
- Negative or nonfinite populations/cross sections: typed failure.
- Exact-zero unsupported species: legal exact zero.
- Positive total opacity with one species present: direct share exactly one for
  that species and zero for absent species.
- Zero total opacity and zero current: typed vacuum with `shares=None`, not a
  normalized zero vector.
- Zero total opacity and nonzero current: typed inconsistency.
- Trace positive absorbers remain exact rationals even below binary64 normal or
  subnormal range; outward export may include zero but cannot erase the exact
  internal value.

## Typed solver admission

A worker outcome is never itself admitted success. Corrected admission requires
the expected solved outcome and every mandatory predicate to be explicitly
`PASS`: finite state, physical domain, residual, enclosure, expected terminal,
event completeness, independent physical invariants, complete diagnostics,
complete source/runtime/input/output identity, and corrected-lineage identity.

Any `FAIL` yields rejection or quarantine according to outcome. Any `MISSING`,
`UNRESOLVED`, or unsupported evidence yields a blocked result. Unknown fields,
unknown enum values, duplicate predicates, and partial identity cannot be
coerced to admission.

## Controller finite-state semantics

The successor state machine separates resumable pauses from terminals.
Terminal states are absorbing and every action on a terminal returns a no-write
self-loop. `RESUME` is legal only from a paused state. Event restart and a new
generation are distinct explicit actions; neither is inferred from `run()`.
An illegal or unresolved transition is typed and cannot publish state.

## Evidence and literature applicability

- S. M. Rump, “Verification methods: rigorous results using floating-point
  arithmetic,” *Acta Numerica* 19 (2010), DOI
  `10.1017/S096249291000005X`, motivates theorem-matched verified operations;
  it does not validate this code automatically.
- SciPy 1.17 `solve_ivp` documents that events are detected by sign changes
  over steps and multiple crossings in one step may be missed; its `success`
  Boolean means interval-end or terminal-event algorithmic completion, not the
  application admission predicates above:
  `https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html`.
- Python 3.12 documents that `communicate()` buffers captured data in memory
  and should not be used for large/unlimited output, and recommends a fully
  qualified executable path:
  `https://docs.python.org/3.12/library/subprocess.html`.

Sources were refreshed on 2026-08-23. Their role is specification
reconciliation only.

## Explicit non-claims and remaining D-gates

This stage does not establish:

- a qualified transcendental or general interval backend;
- a nonlinear/interval Krawczyk theorem implementation;
- continuous defect, global trajectory error, event-time error, or QoI budget;
- all-root/grazing/simultaneous event completeness or conservative restart;
- an independent corrected BDF/reference trajectory;
- exact pinned-runtime parity, active-controller routing, package security,
  performance, production history, endpoint authority, or publication science.

Those surfaces remain blocked by D-01--D-07 and their mapped 32-item
dispositions. A successor primitive can be `IMPLEMENTED` and locally
`VALIDATED` while the ODE solver/science remains `FORBIDDEN` from promotion.

