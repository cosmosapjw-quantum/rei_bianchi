# Joint-moment conditional transfer

The new stdlib-only adapter retains shared affine generators between the three
per-absorber photoionization rates and three incident-energy rate moments. At
one exact fixed gas state, each projected output has exact marginal extrema
`center ± sum(abs(projected_generator))`. Projected generators remain in the
return value so downstream users need not discard output correlations.

The external family must declare its source, provider, state, clock and exact
`ln a` epoch, the exact positive threshold tuple, an ID, its meaning (`finite_rule_envelope` or
`supplied_uncertainty`), and nonempty premises. Rates must be instantaneous
`absorber^-1 s^-1` and `eV absorber^-1 s^-1`; integrated owner counts or energies
are rejected. Every family vertex must satisfy Gamma ≥ 0, Ecal ≥ chi Gamma,
and Gamma = 0 ⇒ Ecal = 0. These are necessary marginal checks; a common
nonnegative spectral realization is **not established**.

Independent review added fixed-context threshold binding and an explicit,
unique ID for every shared generator. IDs preserve the association between
projected coefficients when results are combined downstream. They identify
supplied generators, not a proof that two separately supplied families share
physical uncertainty. Original unit and three-mutant evidence is preserved;
the corrected source is recorded in `tests/evidence/unit_after_review.json`.

Physical-time output derivatives are divided by the fixed positive H exactly
once for the `ln a` view. `photo_q_ell_source` already has its `H^-2` factor
and is retained unchanged. Gas energy, particle-number and temperature terms
come from the verbatim R11 projection; the vendor SHA and origin are in
`vendor/SOURCE_PROVENANCE.json`.

Validation covers an independent 64-vertex direct-equation oracle, a separate
theory author's five synthetic cases, correlated threshold photons with
exactly zero heating width, positive heating with negative temperature response,
signed differences with the reverse sign relation, neutral/pure-H/zero-absorber
limits, exact clock conversion, and failed input/context contracts. Three
temporary-copy fault injections verify detection of a dropped particle term,
independentized rate/energy generators, and an extra H division on q_ell.

Run from the package root:

```sh
python3 -m unittest discover -s tests -p 'test_joint_moment.py' -v
python3 tests/check_mutants.py --output /tmp/igm-moment-mutants.json
```

No production source, provider, rate, closure, solver or default is changed.
No history is integrated. Returned scientific status remains `HOLD`, and
external uncertainty truth remains unverified. A finite-rule envelope is
not a continuum-error bound or an observed temporal jump. Exact arithmetic
certifies this conditional linear algebra, not the truth of its premises.
