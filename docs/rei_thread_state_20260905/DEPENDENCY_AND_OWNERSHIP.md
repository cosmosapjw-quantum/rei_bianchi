# Dependency and ownership contract

## Purpose

This document records only cross-repository facts that directly constrain `rei_bianchi`. It is not a substitute for the source repositories' own state ledgers.

## Authority ownership

### REI-owned

```text
late reionization history
opacity and thermochemistry values
H/He chemistry event graph
finite-optical-depth transmission and allocation
OTS event logic
first-canonical-interval evidence
REI provider values and export decision
```

### BASS-owned

```text
common Bianchi conventions
homogeneous geometry and background dynamics
global matter-frame tilt
photon geodesic and polarized transport formulas
kinetic representation and projection certificates
cosmic-frame output bundle
```

### REC-owned

```text
primordial recombination history
atomic rates and source kernels
source-identical recombination boundary/face physics
REC provider artifact and export decision
```

### HTT-owned

```text
local-observer sky pullback
mask/beam/filter/nuisance processing
observable Q/O morphology
response-limited identification
observation-side covariance and likelihood
```

## REI formula-oracle rule

REI PR #62 derives common spatial curvature independently from the locked commutator. This is a strong executable oracle, but it does not create a second common-geometry owner.

```text
owner              BASS
REI relation       INDEPENDENT_ORACLE
replay target      BASS common spatial-curvature formula family
authority effect   NONE over ownership
```

BASS should exact-pin the REI oracle when closing its native four-dimensional Gauss-Codazzi bridge. REI must not silently fork the common background formula registry.

## Current BASS dependencies

The thread's fresh four-repository survey recorded:

```text
BASS PR #124
head ac3186939ffe1e37ea1af15faa910df1e320277d
status component/scalar BG-02 oracle only
blocker actual xTensor E_ab projection and Gauss-Codazzi bridge

BASS PR #126
head 662f682654f80281a4afd56a28be1ff0d535e2ac
status bounded local scalar constant-source grid/harmonic parity through L=8
claim not physical REC/REI source parity

BASS PR #127
head 9d1c702ddf58549a06b29965a3d1b790a0c23159
status projection-authority expected-RED source
remote disposition PRESTART_NO_EXECUTION at the surveyed head
```

Consequences for REI:

1. REI M1 can serve as a comparator for the future BASS native tensor bridge.
2. BASS background evolution and constraint propagation are not yet available as an admitted provider input.
3. Bounded scalar parity cannot authorize a REI physical source splice.
4. Production PSTF/Wigner layout, continuous positivity, anisotropic source products, and arbitrary-high-rank authority remain gated.

## Current REC dependency

The thread survey recorded:

```text
REC PR #55
head 29c01cec6f0e1fe02a738df0fe317ea2772d4c88
status trusted RF-00 local gate PASS
exact-head workflow first blocker receipt README trailing whitespace
physical source/provider absent
```

The exact frequency-preserving representation pair is

```math
f(q,e)\longleftrightarrow F_{A_\ell}(q).
```

Integrated surfaces

```math
J^{(i)}_{A_\ell},\qquad G(e)
```

require certified source projection or spectral closure. REI must not accept an integrated REC/BASS summary as if it retained a general frequency-dependent source.

The REI splice remains blocked until REC supplies an admitted representation-neutral source/provider artifact with exact provenance and compatible frame/measure semantics.

## Current HTT dependency

The thread survey recorded:

```text
HTT PR #449
head 409ad49a341870f49694b9a57e0baa19ddf841c4
status K1 core source; K1R repair required before K2

HTT PR #451
head 9f7d06dec0fce1c3a8a53fa5372c84d9c679c037
status Q/O packet-image and STF3 decoder local source-equivalent repair
exact-head execution withheld at surveyed head
```

HTT's exact local-observer pullback is a useful downstream oracle. It is not a global matter-frame tilt, electron-frame tilt, Bianchi background, opacity provider, or cosmic transport model.

Required separation:

```text
BASS/REI cosmic-frame output
→ HTT local-observer pullback
→ processed observational response
```

Forbidden identification:

```math
\beta_{RO}=\beta_{RM}
```

unless separately proved and admitted. Local boost must not substitute for global background tilt or electron tilt.

## Join gates

### Shared mathematics join

```text
REI M1 spatial-curvature oracle
+ BASS native four-dimensional E_ab/Gauss-Codazzi bridge
+ explicit positive-K/ADM adapter
→ Hamiltonian and momentum constraints
→ constraint propagation
→ background numerical admission
```

### Source and transport join

```text
REC primordial source/provider
+ REI late thermochemistry/opacity/provider
+ BASS authority-hardened f(q,e) <-> F_Aell(q) bridge
+ certified integrated J/G projections
→ coupled cosmic-frame transport
```

### Observable join

```text
admitted BASS background and transport
+ admitted REC and REI providers
→ deterministic cosmic-frame output
→ HTT local-observer/processed response
→ physical identification and likelihood
```

## Hard firewalls

The following substitutions are forbidden:

- REI grouped-redshift FLRW control for generic Bianchi photon transport;
- REI M1 oracle for BASS common-geometry ownership;
- bounded BASS scalar parity for physical REC/REI source parity;
- integrated `J` or `G` state for frequency-resolved source data without closure;
- cold normal-frame Thomson scattering for finite-electron-tilt collision physics;
- HTT local-observer boost for global matter or electron tilt;
- a registry entry for a genuine numerical family provider;
- local or source-equivalent execution for exact-head runtime admission.

## Current integration status

```text
BASS native background provider      NOT_ADMITTED
REC primordial provider              NOT_ADMITTED
REI first interval/provider          NOT_ADMITTED
HTT physical Bianchi consumer join   BLOCKED
cross-repository science promotion   NOT_AUTHORIZED
```
