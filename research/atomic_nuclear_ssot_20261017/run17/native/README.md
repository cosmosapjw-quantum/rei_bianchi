# RUN17 first-birth native coupled control

This unit advances the unchanged original M2 gas/optical-depth equations only
from code-z `0.004989333151072248` to `0.02371416180174271`. Code-z means
`(X - 0.7)/(0.7004 - 0.7)`; it is an integration coordinate. The left state is
outgoing immediately after the first photon birth, and the right state is
incoming immediately before the second photon birth. No threshold root lies
inside this interval. There is no full-history rerun or reconstruction of a
historical full transport checkpoint.

## Preserved physical inputs and exact restriction

`INPUT_IDENTITY.json` records the original M2 packet, event file, original
source manifest and 112 source/input hashes, plus the frozen RUN16 prefix-C
receipt. Prefix-C's five gas coordinates reproduce its stored physical gas
state exactly. Its accuracy is numerical evidence; it supplies no rigorous
initial-state enclosure.

The first birth contains 504 original physical rows. The original checked
`coalesce_reflections` function combines their exact +/-mu pairs into 252
positive populations, with **all 48 spectral cells retained**. Future source
rows have not been born. Their optical-depth coordinates have zero derivative
in this interval, and their omitted values remain exactly zero.

The physical gas coordinates are the original affine invariant chart
`(x_HII, x_DII, x_HeII, x_HeIII, U/U0)`, with H/D/He totals inherited from the
original initial state. Inactive Li/Be densities remain at their original
zeros. The gas RHS depends only on gas and active photon depths; the original
escape, CMB, event and work accumulators do not feed back into these
derivatives. They can therefore be omitted without changing this restricted
gas/depth vector field. This is a claim about the vector field and initial
physical data, not equivalence of the solvers' weighted error norms.

Four new local absorption integrals and four local heating integrals start
at zero immediately after the first birth. Their order is H I, He I, He II,
D I. They are fresh interval ledgers, with no inferred historical ledger
values. The final state dimension is `5 + 252 + 4 + 4 = 265`.

`SpectralModel.section_sigma`, the original native gas executable, prescribed
BASS geometry, gas normalizations, all four absorber channels and their heat
deposition are retained. In particular, H's 13.6 eV fitting edge is distinct
from its 13.598434599702 eV binding energy. D retains the original
threshold-gated H-equality approximation at 13.602134599702 eV; no new
isotope-specific cross section is introduced.

Writing `p_i=B_i exp(-tau_i)`, the original equations on this interval are

\[
\tau_i'=\sum_a h_{ia}(q,z),\qquad
A_a'=\sum_i h_{ia}(q,z)p_i,\qquad
Q_a'=\sum_i h_{ia}(q,z)p_i(E_i-\chi_a).
\]

The four absorption rates enter the original gas stoichiometry, and
`sum(Q_a')` enters the original comoving thermal-energy equation, alongside
native gas cooling/heating and expansion. Consequently the continuous local
photon identity is `P(z)-P(left)+sum(A_a(z))=0`: there are no additional
births in the selected interval. The measured signed residual is saved at
each accepted state. It measures this ledger consistency, not spectral or
gas-trajectory convergence.

## Actual bounded calculations

Both calculations use DOP853 with nominal `rtol=6e-12`, divided by `sqrt(265)`.
Before that division, absolute tolerances are `1e-15` for each invariant gas
coordinate, `1e-11` for each depth, and `1e-19` for each of the eight local
ledger coordinates. This defines a component-scaled L2 norm in the new
265-coordinate chart. It is explicitly different from the archived
40357-coordinate error norm, even though the physical vector field is the
same restricted one.

| Control | Configured maximum step | Accepted steps | Actual native calls | Process-measured total wall time |
|---|---:|---:|---:|---:|
| A | panel width / 4 | 15 | 229 | 1.035997522 s |
| B | panel width / 20 | 23 | 349 | 1.060348364 s |

A's largest accepted step was `0.0020302375569376113`, already smaller than
its configured maximum. B's configured maximum is
`0.0009362414325335232`, less than half that actually accepted largest A
step. B therefore supplies a distinct smaller-step control. The configured
maximum changes by a factor of five; no precise halving of every accepted
step or asymptotic convergence order is claimed. The measured A cost led to
one bounded budget adjustment before B: A's call cap was 250 and B's was 360,
with a twenty-second cap on each native session. There were **578 actual
native calls in total**, including four counted endpoint evaluations used
for compatibility replay, and no further integrations.

Each endpoint compatibility check replays its one actually evaluated native
payload through the original `SpectralModel.section_rhs`; replay performs no
additional native call. All 265 packed derivatives match exactly at both
endpoints of both controls. The gas tangent reconstruction also matches
these physical gas derivatives exactly in these checked samples.

Across the 17 shared dense-output sample times, B minus A has maximum absolute
differences of `4.440892098500626e-16` in q and
`6.572520305780927e-14` in depth. Maximum HI relative difference is
`1.1102230246251565e-16`, temperature difference is
`7.275957614183426e-12 K`, and survivor difference divided by the initial
birth is `6.103070901531086e-15`. These are actual sampled comparisons, not
supremum bounds. Scalar and batched temperature evaluation can differ by
floating-point summation roundoff; all raw gas states are preserved.

A's maximum accepted photon residual divided by the initial birth is
`1.256260435129319e-13`; B's is `4.968871884432388e-15`. The common initial
birth is `3.920760736030605e-6` photons per initial H. B's scalar endpoint
temperature is `9999.735053555296 K`. Full source, gas, optical depth,
absorption and heat values remain in the JSON/NPZ evidence.

## Reusable interface and dense evidence

`native_context.load_context(source_root, run16_root)` is read-only and starts
no native process. `source_root` must point at the unchanged
`run13/recovered`; `run16_root` must contain the frozen RUN16 feedback
receipts. The returned context exposes:

- `initial`, `left`, `right`, `dimension`, `depth_slice`, `absorption_slice`,
  `heat_slice`, `source_population` and physical `model` geometry.
- `gas_from_q(q)` and `temperature(gas)` with sample axes supported.
- `photo_parts(z, q, depths)` for the exact four-channel photon assembly.
- `rhs_parts(z, state, native_callable)` for one counted native evaluation;
  the callback signature is `(proper_state_14, tcmb_K, mask=7)` and returns
  the original 28-float payload. Its returned mapping includes `rhs`,
  `native_gas_rate_14`, `photo_gas_rate_14`, `gas_rate_14`, `tau_rate`,
  `net_absorption_rate`, `net_heat_rate`, `population`, energy and geometry.
- `TracedNative` supplies explicit binary identity, a fresh JSONL value trace
  and bounded counters. Its `callable(z, purpose)` can be passed directly
  into `rhs_parts`. A later residual diagnostic owns its own trace/counters.

Every accepted DOP853 dense piece is saved without conversion in
`ACCEPTED_AND_DENSE_STATE.npz`: `dense_t_old`, `dense_h`, `dense_y_old`, and
`dense_F` with shape `(steps, 7, 265)`. `accepted_z`, `accepted_y`,
`accepted_gas_14`, the 17 sample states, the original active cohort columns
and section mask are also preserved. These coefficients permit analytic
value/derivative reconstruction without another IVP. The seven-row recurrence
is the actual installed SciPy 1.17.0 `Dop853DenseOutput` representation.

Exact CLI argument vectors, Python/NumPy/SciPy versions, source and binary
hashes, complete parsed-value native traces and standard streams are saved.
Original source/input hashes were checked before and after each control.

## Reproduction and next dependency

For a new output directory, invoke:

```bash
python -B first_birth_control.py \
  --source-root /absolute/checkout/research/atomic_nuclear_ssot_20261017/run13/recovered \
  --run16-root /absolute/checkout/research/atomic_nuclear_ssot_20261017/run16 \
  --gas-binary /absolute/bin/gas_rhs_server \
  --output-dir /absolute/new/control_A \
  --max-step-divisor 4 --native-call-cap 250 --wall-cap-seconds 20
```

The B command uses `--max-step-divisor 20 --native-call-cap 360` and
`--reference-result /absolute/new/control_A/FIRST_BIRTH_CONTROL.json`.
No result directory or source is overwritten. An interrupted control saves
its partial accepted states, dense coefficients and explicit failure report.

The next calculation consumes the saved B dense polynomials to evaluate the
full gas-plus-photo residual and optical-depth residual, and compares an
invariant checkpoint-path reconstruction with depth integrated along that
same reconstructed gas. Continuous physical-domain margins, numerical
quadrature errors, a rigorous prefix initial enclosure, residual suprema and
feedback log-norm bounds remain separate requirements for a uniform gas tube.
This local unit does not establish continuous spectral refinement, angular
or birth-time continuum, whole donor coverage, full EoR or Einstein feedback.
