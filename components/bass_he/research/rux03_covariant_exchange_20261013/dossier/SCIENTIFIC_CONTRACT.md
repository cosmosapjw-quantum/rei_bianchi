# HERE_RUX03_COVARIANT_EXCHANGE_04 — theory contract

Date: 2026-10-13 KST (execution date may be 2026-10-12 UTC).
Route: `physmath-research-loop` built-in THEORY R1–R10, skill 1.0.0 / design v0.2.

## Target

Extend the adopted H/He scalar event and energy ledger to a local covariant
energy–momentum exchange construction. Derive its gas and radiation projections,
identify precisely how the implemented axisymmetric shear work follows, and
construct a nonempty photon family with zero absorbed momentum and nonzero
anisotropic work. Use SciSpace and Exa for primary-source discovery and actual
Wolfram Language plus xAct computations for discriminating checks.

The input is BASS_HE PR31 at `be96b0011772b47af4bd3c8e420f73153a745508` and the
unchanged receiver rei_bianchi PR114 at `a5c958c414dea41216b445c05f58df837f05cacb`.
The source map records exact trees, source hashes and the bounded successor search.

## Retained physical assumptions

- Signature `(-+++)`; dimensionless common gas velocity `u.u=-1`, physical
  velocity `U=c u`, and explicit `c`, `hbar`, `k_B`.
- Charge-neutral, one-temperature, nonrelativistic H/He gas with conserved
  H and He nuclei, `n_H>0`, fixed `f=n_He/n_H>0`, and physical fractions
  `0<=x<=1`, `a>=0`, `b>=0`, `a+b<=1`. The neutral-composition reference mass
  is constant per H. Moment fields and the metric are differentiable as needed;
  each local node sum is finite.
- The adopted warm FT03 Case A event and captured-kinetic-moment provider in
  `30000 <= T <= 110000 K`; existing CI, RR, DR and primary photoabsorption
  channels and thresholds are retained. Cooling here is the adopted RR/DR
  captured-kinetic loss. CR/RCT/HH stay off.
- Local photon energy and absorption rates are evaluated in this common gas
  rest frame; rates are per proper volume and proper time.
- The full projection identities are local continuum identities. The selected
  current application is prescribed LRS Bianchi I with normal geodesic gas,
  homogeneous pressure, isotropic absorbers, and an axisymmetric angular model.
- Escape radiation is assigned a comoving-isotropic *emission moment* closure.
  The existing scalar escape counter supplies its power. This is an explicit
  additional angular closure, not a reconstructed escape spectrum or evolved
  escape stress tensor.

## Reuse and new obligations

R00 reuses PRIMARY_THEORY_03 event cancellation, binding polynomial, coefficient
normalization, exact endpoint-energy finite work, and the associated 47 symbolic
groups. It also reuses the current source's existing `2 s DeltaP` term. These
results are not rerun or counted as new calculations.

| ID | New obligation | Completion evidence |
|---|---|---|
| C01 | Positive photon-event four-force and isotropic escape moment construction; total exchange cancellation | Written construction and tensor projections |
| C02 | Perfect-fluid gas energy/momentum projection with binding energy and neutral reference mass; recovery of the old thermal source | Derivation, independent review, exact algebra |
| C03 | Full radiation energy projection including physical-c acceleration/flux terms | Derivation and xAct tensor contraction plus independent local-frame algebra |
| C04 | Connect `sigma:pi` and directional redshift to the implemented Bianchi `2 s DeltaP` and reused finite work | Explicit normalization map and exact examples |
| C05 | Preserve antipodal/ring-reflection equality under geometry, source and absorption; retain nonzero anisotropic work | Invariant-family proof and exact two/six-beam examples |
| C06 | Distinguish vanishing energy flux from vanishing opacity-weighted absorption force | Explicit positive spectral counterexample |
| C07 | Exact observer projection of the local four-force and comoving-isotropic emission | Tensor identity and stated frame domain |

The deliverable consists of derivations, actual inputs and raw outputs, a single
claim/evidence registry, independent review, a Korean report, and a coding
contract with an updated next-step DAG overlay.

## Scope of the implementation handoff

The current code evolves scalar gas/radiation energies and anisotropic stress
moments, while the selected state/source APIs do not evolve gas bulk momentum,
photon flux or escape angular moments. The new contract specifies those local
moments and the fixed-frame compatibility test. It preserves
`HERE_RUX03_PRIMARY_PROVIDER_03` as the existing coding successor.

The independent all-Bianchi D2.3 abundance/reference-current/class-B task is
outside this unit. New Rust/native builds, RHS evaluations and ODE/history runs
are not part of this THEORY unit. Actual Wolfram/xAct symbolic calculations and
a static comparison of the selected initial angular data are in scope.

## Decision rules

Adopt each C result under its stated assumptions after its proof and independent
check are complete. An environment or invocation failure changes the execution
record, not the truth status of a formula. Preserve failed inputs and use a
documented supported alternative when the diagnosis calls for it. The target is
a constructive extension; no new strong no-go claim is proposed.

Reopen only dependencies affected by a changed assumption or concrete finding.
The original `RUX02 + RUX03 -> RUX04 -> RUX05` owner DAG and implementation
completion states are retained.
