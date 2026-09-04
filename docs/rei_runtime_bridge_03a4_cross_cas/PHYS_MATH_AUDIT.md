# PHYS-MATH audit — REI 03A4 cross-CAS sidecar

Status: `PASS_NO_PHYSICS_DELTA_METHOD_ONLY`.

## Definitions and scope

The checked object is a finite directed chain of governance predicates.  It is
not a photon hierarchy, background equation, collision operator, numerical
integrator, or observable.

```text
IndependentAudit
→ TargetHostStaticPreflight
→ FreshProtectionReadback
→ GlobalLease
→ LocalLease
→ DispatchIntent
→ NativeWorker
→ RuntimeResultAudit
→ FirstIntervalEligibility
→ ProviderReview
```

Each arrow is interpreted as a prerequisite relation: the target may be
admitted only if the source has been admitted.  The cross-CAS checks establish
properties of this declared relation only.

## Exact mathematical checks

- The ten-by-ten adjacent-chain matrix is strictly upper triangular.
- Its tenth power vanishes and its ninth power has one nonzero entry.
- Its transitive reachability matrix is the strict total order.
- Under adjacent Boolean implications, `ProviderReview=true` with any earlier
  predicate false is inconsistent.
- Under the same contract, `NativeWorker=true` with any pre-lease predecessor
  false is inconsistent.
- Adding a direct `IndependentAudit -> NativeWorker` edge is detected as a
  forbidden shortcut rather than absorbed into the chain.

## Physics conventions

No metric, orientation, unit, sign, gauge, energy variable, multipole,
collision coefficient, or background state is modified.  The locked project
conventions remain external to this sidecar:

```text
metric signature       (-,+,+,+)
spatial orientation    epsilon_123=+1
speed of light         explicit
native precision       256 bits when the native runtime is eventually used
rounding               MPFR_RNDD / MPFR_RNDU
```

## Counterexample boundary

Acyclicity alone would not imply the required order: a graph containing a
shortcut can remain acyclic.  Nilpotence alone is likewise insufficient.  The
sidecar therefore checks exact adjacency, transitive order, Boolean predecessor
implications, and an explicit shortcut mutation separately.

## Claim ceiling

```text
DAG finite-chain consistency       candidate for independent CAS verification
target-host static preflight       NOT_RUN
global attempt ref                 ABSENT_REQUIRED
native runtime                     NOT_RUN
first canonical interval           NO_PASS
provider/scientific claim          NOT_AUTHORIZED
```
