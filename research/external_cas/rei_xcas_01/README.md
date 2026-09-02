# REI-XCAS-01 — GNU Octave, JAS, Julia and Wolfram cross-check

This bounded audit is stacked directly on the exact active REI scientific
checkpoint, Draft PR #32 at
`f4eb2c893ce6449f8899ab6f02c83421fc7c7019` / tree
`16d060d45ddfa401e4a5c22f9ca53cf65399ff51`.

It does **not** repair or retry the runtime bridge. The observed stop remains:

```text
STOP_INVALID: UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION
RuntimeClosureError: UNDECLARED_IMPORT: ntpath
NO_PASS_FIRST_CANONICAL_INTERVAL
NO_PROVIDER_EXPORT
```

## Independent axes

- GNU Octave: deterministic numerical properties, limits, allocation
  normalization, redshift-flow telescoping and hostile mutations. Octave is
  intentionally labelled a numerical oracle rather than an exact CAS.
- JAS 2.7.200: exact rational multivariate-polynomial identities for
  redshift-flow conservation, species/state algebra and all chemistry-event
  H/He stoichiometric invariants.
- Julia 1.12.6 + Symbolics 7.31.0: symbolic derivatives and transcendental
  limits, plus independent 256-bit numerical transmission/allocation checks.
- Connected Wolfram evaluator: comparator only, `authority_effect=NONE`.

## Source-derived formulas under test

```text
H(z) = H0 sqrt[Omega_m (1+z)^3 + Omega_Lambda]

n_e = n_H x_HII + n_He (x_HeII + 2 x_HeIII)

x_HII = sigmoid(z_H)
(x_HeI,x_HeII,x_HeIII) = softmax(0,z_HeII,z_HeIII)

redshift-only flow:
  dN_i/dt = -r_i N_i + 1_{i<3} r_{i+1} N_{i+1}
  sum_i dN_i/dt = -r_0 N_0

W_exp = 3 H p

F_g = <exp(-tau)>_phi
A_sg = <(1-exp(-tau)) tau_s/tau>_phi / <1-exp(-tau)>_phi
```

The generic BASS photon drift
`R=-H_geom-sigma_ab e^a e^b` is not replaced by the REI grouped-redshift
control. The latter remains valid only in the declared FLRW or exactly
isotropic angular subspace.

## Acceptance

All three external jobs must execute their own code and terminate successfully.
Package acquisition alone is not a pass. Each job emits a machine-readable
receipt and the aggregate job generates a residual plot from the actual
receipts.

## Claim ceiling

A green workflow supports only the bounded algebraic/numerical formulas above.
It does not establish runtime-bridge closure, first-interval acceptance,
provider admission, generic Bianchi transport, full solver maturity or any
scientific result.
