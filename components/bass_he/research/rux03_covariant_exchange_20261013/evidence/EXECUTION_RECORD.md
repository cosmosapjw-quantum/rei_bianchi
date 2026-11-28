# Actual symbolic execution record — THEORY04

## Final discriminating computations

The final xAct execution is `XACT_COVARIANT_EXECUTED.wl`, with the exact tool
response in `XACT_COVARIANT_RAW_RESULT.json`. `XACT_COVARIANT_RESULT.json` is
parsed from that response's printed JSON string. It contains:

- Wolfram Language **15.0.1 for Linux x86 (64-bit), July 2, 2026**.
- Official xAct bundle **1.3.0, December 29, 2025**, including xTensor 1.3.0
  and xPerm 1.2.4. Source: `https://xact.es/download/xAct_1.3.0.tgz`.
- Archive size **15,613,945 bytes**; SHA256
  `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`.
- Loaded `xTensor.m` SHA256
  `04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36`.
- **24 xAct tensor groups, all True, each residual canonicalized to 0.**
  These include the complete differential gas energy/momentum projections and
  the differential radiation energy projection with four-divergence of flux.
- **5 exact scalar groups, all True**, separately labeled in the same output.
- `xTensorLoaded=true`, `tensorDeclared=true`, `xPermExternalBackend=false`.

The final wrapper checks the archive hash before loading. Actual canonicalization
uses xAct's supported **pure Wolfram xPerm backend**, selected with
`xAct`xPerm`$xpermQ=False`. This is actual xTensor/xPerm computation. The official
package's startup log still announces its external link initialization; the
recorded selector governing the successful calculations is false.

An independently authored and executed scalar/matrix script,
`geometry_exact.wl`, has **16 exact groups, all True**. Its original response
and parsed record are `GEOMETRY_WOLFRAM_RAW_RESULT.json` and
`GEOMETRY_EXACT_RESULT.json`.

The new accepted check groups total **45 = 24 + 5 + 16**. The initial six smoke
checks are a subset of the final tensor groups and are not added again. The
29 groups in a preceding successful run are likewise not counted again.
The previous unit's 47 symbolic groups are reused evidence, not new executions.

## Preserved setup and invocation attempts

These observations concern execution setup or representation. No physical
formula was changed to turn a failed scientific residual into a pass.

| ID | Observed result | Diagnosis / next action |
|---|---|---|
| EX00 | Preinstalled `xAct`xTensor`` could not be found; no xTensor symbols loaded | Package absent in the initial environment. The official download page and archive were then reached successfully. The original probe response is retained; the exact original probe input was not captured in the execution files. |
| EX01 | Official package loaded, but six unqualified smoke expressions returned False, with undefined `Global` function warnings | Functions had been parsed before `Needs`, creating wrong-context symbols. Use qualified xAct calls or parse the program after loading. |
| EX02–EX04 | Qualified declarations worked. A one-vector `ToCanonical` returned that vector, while the contracted expression produced a sandbox-tagged `Throw[Null]`; the native/default path did not yield a science result | Backend/invocation failure. The low-level cause of that throw was not independently resolved. Use the documented pure Wolfram backend. |
| EX05 | Pure-backend smoke calculation: 6/6 True, package and tensor declarations verified | Setup resolved for algebraic contractions. |
| EX06–EX07 | Full program stopped without a final result. Staged diagnostics passed declaration and algebra-call stages, then stopped at construction of differential `MakeRule` rules | Rule-construction invocation failure. Retain the same kinematic assumptions using explicit indexed Wolfram replacement patterns. Partial stages are not counted as accepted groups. |
| EX08 | 24 tensor + 5 scalar groups True; the field named `kernel` accidentally resolved xTensor's `$Version` | Scientific checks succeeded. Qualify `System`$Version` and add runtime hash provenance to the wrapper. |
| Final | 24 tensor + 5 scalar groups True, correct kernel field and checked runtime identities | Accepted symbolic execution. |

Exact inputs and original responses for EX01–EX08 are in `attempts/`. EX00
and the official archive discovery response are also retained there. Initial
root-level EX00/EX01/EX02 captures are kept as historical files.

## What the differential computation assumes and checks

The script defines a four-dimensional Lorentz metric and Levi-Civita derivative,
unit timelike velocity, spatial vectors, symmetric spatial trace-free shear and
anisotropic stress, and spatial antisymmetric vorticity. It supplies
`∇u=-u a/c^2+(Theta h/3+sigma+omega)/c` and differentiated spatiality
`u·∇q=-(∇u)·q`, `u·∇pi=-(∇u)·pi`. xAct expands the stress divergences and
canonicalizes their differences from the proposed projection equations.

The conversion `∇·q=D·q+a·q/c^2` is proved explicitly in the geometry note and
checked independently in local-frame algebra. The adopted atomic fits and their
derivatives are inherited; these new checks do not re-evaluate those fits.

The caller is `Wolfram.wolframlanguageevaluator`, with `timeConstraint:55`
for the root's xAct calls. Each call includes its required package bootstrap;
no persistent kernel definitions are assumed. Native tests/builds, chemical RHS
calls and ODE/history integrations in this unit are **0**.
