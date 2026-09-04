# PHYS-MATH audit

## Audit scope

This audit covers only the consolidated REI formula, runtime-boundary, and dependency claims. It does not claim a fresh derivation of every historical REI equation or a native runtime replay.

## Conventions and notation

| Check | Result | Evidence | Disposition |
|---|---|---|---|
| Metric signature `(-,+,+,+)` | PASS | formula line and project SSOT | fixed |
| Spatial orientation `epsilon_123=+1` | PASS | formula line and project SSOT | fixed |
| `c` retained explicitly | PASS | project scope | fixed |
| Bianchi `a^B_a` distinct from four-acceleration | PASS | project convention | fixed |
| Triad rotation distinct from physical vorticity | PASS | project convention | fixed |
| Photon `e^a` distinct from outward sky `n=-e` | PASS | ownership/interface firewall | fixed |
| `K^+_ab=H h_ab+sigma_ab` explicitly typed | PASS_WITH_OPEN_ADAPTER | thread derivation | M1B |

## Spatial-curvature formula

The exact-head oracle derives the Levi-Civita connection from the commutator and tests the Ricci tensor modulo the Jacobi ideal. This is stronger than a finite branch substitution.

Checks:

```text
Ricci symmetry                             PASS
Ricci residuals modulo n^{ab}a_b=0        9/9 exact zero
Ricci scalar residual                      exact zero
homogeneous STF-divergence residuals       3/3 exact zero
class-A structural negative controls       4/4
class-B mixed-sign detections              4/4
```

### Dimensions

```text
[a^B] = [n] = L^-1
[3R_ab] = [3R] = L^-2
```

Every term in the Ricci tensor and scalar has dimension `L^-2`.

### Limits

```text
I   a=0,n=0        -> 3R_ab=0, 3R=0
V   n=0,a^2=A^2    -> 3R_ab=-2A^2 h_ab, 3R=-6A^2
IX  a=0,n=N h      -> 3R_ab=(N^2/2)h_ab, 3R=3N^2/2
```

These are consistent with the declared spatial loci.

## Positive-expansion tensor

For

```math
K^+_{ab}=Hh_{ab}+\sigma_{ab},\qquad \sigma^a{}_a=0,
```

one obtains

```math
K^+=3H,
```

```math
K^+_{ab}K_+^{ab}=3H^2+\sigma_{ab}\sigma^{ab},
```

and

```math
(K^+)^2-K^+_{ab}K_+^{ab}=6H^2-\sigma_{ab}\sigma^{ab}.
```

Dimension: `L^-2`. The expression is even under `K -> -K`.

The momentum/Codazzi combination is odd under this transformation. Therefore the current spatial formula cannot decide the spacetime momentum sign by itself.

Disposition:

```text
Hamiltonian extrinsic algebra      PASS_DERIVATION
ADM/positive-K adapter             OPEN
momentum and matter-flux sign      OPEN
constraint propagation             NOT_RUN
```

## Source and transport boundaries

### Cold electron-rest Thomson

The formula SSOT assumes cold, non-tilted electrons at rest in the normal frame. It does not support finite electron tilt, recoil, thermal Comptonization, or Klein-Nishina terms.

Disposition:

```text
cold normal-frame Thomson formula  IN_DOMAIN
finite-electron-tilt collision      OUT_OF_DOMAIN / NOT_IMPLEMENTED
```

### REI grouped redshift

The current grouped-redshift identities are isotropic/FLRW controls. In a generic anisotropic field, shear couples to angular moments. Treating the scalar group flow as generic Bianchi transport would omit those channels.

Disposition:

```text
FLRW/isotropic control    ALLOWED
full Bianchi replacement REJECTED
```

### Frequency-resolved versus integrated states

The exact primary pair is

```math
f(q,e)\leftrightarrow F_{A_\ell}(q).
```

Integrated `J` and `G` states lose spectral information and require a source-projection or closure certificate. The physical dimensions and representation roles are not interchangeable.

Disposition: PASS dependency firewall.

## Frame and tilt separation

```text
global matter-frame tilt   BASS forward-model domain
finite electron tilt       collision/source extension, not present here
local observer boost       HTT output-side domain
```

No equality among these velocities is assumed.

Disposition: PASS firewall; physical join remains open.

## Runtime evidence and physics authority

- A compiler package hash has provenance authority, not physics authority.
- A Docker-isolation PASS has mechanism authority, not epoch or numerical authority.
- A ruleset 404 observation has no execution authority.
- Source tests cannot establish a native interval result.

Disposition: PASS evidence separation.

## Adversarial checks

### Sign mutation

Reversing the mixed `epsilon*n*a` term:

- must be invisible for class A because `a=0`;
- must be visible for generic class B.

Observed signature matches this prediction.

### ADM-sign shortcut

Attempted shortcut: infer the momentum sign from the Hamiltonian quadratic term.

Result: invalid, because the quadratic term is even under `K -> -K` while the momentum term is odd.

### Integrated-source shortcut

Attempted shortcut: use `G(e)` alone for a general frequency-dependent source.

Result: invalid without an invariant source subspace or spectral closure.

### Runtime shortcut

Attempted shortcut: execute with the matching extracted compiler at an alternate path.

Result: invalid under the canonical path-binding contract.

## Ranked findings

### P0

None newly found within the M1 spatial formula. Promotion to spacetime/background readiness remains blocked by missing work rather than a newly demonstrated contradiction.

### P1

1. Four-dimensional Gauss-Codazzi sign adapter absent.
2. Momentum constraint and matter-flux sign absent.
3. Constraint propagation absent.
4. Historical host epoch and complete runtime closure absent.
5. Finite-electron-tilt collision absent.
6. REC provider and BASS admitted background absent.

### P2

1. Multiple divergent Draft branches require exact-pin discipline.
2. Operator evidence could be overread as repository execution without the evidence-class labels.
3. Formula branch and runtime branch remain uncomposed by design.

### P3

Fresh Wolfram replay was unavailable due upstream HTTP 502. This is not a formula failure.

## What is genuinely closed

```text
generic spatial Ricci tensor and scalar
homogeneous STF divergence
I/V/IX spatial sentinels
class-B mixed-sign adversarial sensitivity
formula/runtime/ownership evidence separation
```

## What remains uncertain or open

```text
four-dimensional sign adapter
Hamiltonian/momentum projections
constraint propagation
background numerical stability
finite-electron-tilt collision
full source/provider splice
native runtime and first interval
```

## Verdict

```text
PASS_REI_M1_SPATIAL_FORMULA_SCOPE
HOLD_SPACETIME_BACKGROUND_AND_PROVIDER_PROMOTION
```
