# Actual execution record — MOVING_GAS_SOURCE_05

Date: 2026-10-13 KST. Scientific execution was light exact Wolfram Language
and actual xAct tensor algebra. Six evaluator calls were made: three xAct
attempts, one primitive batch, one finite-source batch and one targeted
positivity supplement. Prior units' successful groups were reused rather
than rerun. Native builds, chemical RHS evaluations, ODE/history integrations
and parameter scans were not run in this THEORY unit.

## Final evidence, by batch

| Batch | Final named assertions | Actual final result | Evidence |
|---|---:|---|---|
| Actual xTensor/xPerm | 25 | 25 True; each tensor residual is exactly 0 | `XACT_MOVING_SOURCE_RESULT.json`, raw v3 and executed v3 input |
| Primitive inverse and exact warm fixtures | 18 | 18 True | `PRIMITIVE_EXACT_RESULT.json`, primitive raw/input/context |
| Finite source, thermal projection, clock and Jacobian | 12 | 12 True in per-assertion aggregation: 11 from first batch plus one targeted certificate | `MOVING_SOURCE_EXACT_RESULT.json` and its two explicit source results |

These are names in actual result records, not 55 independent theorems or
55 independent physical scenarios. Some identities are intentionally
cross-checked between scalar and tensor representations. In particular,
the primitive author's positive-factor formula and the root's full
Jacobian/positivity calculation overlap mathematically. The prior 45
THEORY04 and 47 THEORY03 groups are not added to these new batch counts.

## Actual xAct, package provenance and index correction

The successful kernel reports Wolfram 15.0.1 for Linux x86 (64-bit),
July 2, 2026. It actually loaded xTensor 1.3.0 and xPerm 1.2.4. Tensor and
metric definitions, projections, derivatives and `ToCanonical` were
executed with xPerm's pure Wolfram backend (`$xpermQ=False`). This is an
actual xAct execution; the external xPerm executable was not used.

The standalone wrapper fetched the official archive
<https://xact.es/download/xAct_1.3.0.tgz>, checked its SHA256 before loading,
and parsed the tensor program after `Needs` established the package context.
Archive size: 15,613,945 bytes. Archive SHA256:
`7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`.
xTensor source SHA256:
`04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36`.
The evidence retains the input and provenance, without redistributing the
third-party package archive.

The first xAct attempt returned `Hold[Throw[Null]]`. A diagnostic second
attempt added phase and assertion-name prints and located the interruption
at `M03_conservative_momentum`. It also returned `Hold[Throw[Null]]` and
produced no completed PASS JSON.

The original helper `Cp[i_]:=-Tp[i,b]normal[-b]` used a fixed internal dummy
index `b`. Calling `Cp[b]` from a projector duplicated the free/dummy index,
producing an invalid Einstein expression. This was an **implementation
index-hygiene error**. The third input replaced the helper by its equivalent
expanded current,

```wl
Cp[i_] := (rhop[] + pp[]) gp[] up[i] - pp[] normal[i];
Cm[i_] := (rhom[] + pm[]) gm[] um[i] - pm[] normal[i];
```

and added the independent assertion
`-Tp[a,b]normal[-b]-Cp[a]` to check that definition against the stress tensor.
The physics, signature, source equations and claimed projection were
unchanged. The final 25 assertions all passed. Both earlier exact inputs
and raw failures remain in this dossier and are not counted as successful
runs. The independent reviewer compared the actual raw and normalized
results and the embedded final input.

## Primitive exact batch

One evaluator call executed the preserved `primitive_exact.wl`, identical
to the contribution's executable input. Runtime: 0.169961 kernel seconds;
Wolfram 15.0.1 / Linux-x86-64. The 18 groups comprise exact algebra,
derivatives, inverse/forward substitutions and one exact warm-fixture
inequality group. Decimal physical constants were represented as exact
rationals; no fitted trajectory or floating-point scan was used.

For the 23 eV HI reference, the actual output contains

\[
T_{\rm exc}=72733.757372464264931\ldots\ {\rm K},\quad
23-\chi_H-{3k_BT_0\over2\epsilon_{\rm eV}}
=2.938565453689116924752\ldots\ {\rm eV}>0.
\]

The full retained atomic model is distinguished from these isolated
absorption fixtures in the proof and contract.

## Root finite-source batch and targeted inequality certificate

The actual first scalar call used `MOVING_SOURCE_CALL_INPUT.json`
(`timeConstraint: 90`). Its exact code bytes are
`MOVING_SOURCE_WOLFRAM_EXECUTED.wl`. Kernel runtime: 1.961573 seconds.
Eleven of twelve named assertions returned True. The full 4×4 primitive
Jacobian was differentiated before setting the velocity axis, and its
formula matched exactly.

The remaining `primitive_jacobian_positive` assertion used `FullSimplify`
with real-domain assumptions. The output retained a conditional radical
inequality instead of returning the literal `True`. The Boolean wrapper
`TrueQ` therefore recorded False. The raw inequality was not a negative
value, a counterexample, or a proof of failure. Its correct classification
is **CAS-undecided inequality under the supplied simplification method**.

Only that unresolved assertion was supplemented. The preserved
`MOVING_JACOBIAN_POSITIVITY_CALL_INPUT.json` (`timeConstraint: 30`) uses
\(\alpha=2+a\), \(a\ge0\), in the unchanged determinant factor. Exact
expansion returns 22 nonnegative coefficients and the strictly positive
monomial \(a_r^3\gamma^5\) with coefficient 1. On
\(a_r>0,\gamma\ge1,p\ge0,a\ge0\), every monomial is nonnegative and that
one is positive. This is an exact positivity certificate.

The targeted call returned True in 0.008758 kernel seconds. Its raw and
normalized results are preserved. `MOVING_SOURCE_EXACT_RESULT.json` is
explicitly an aggregation of the original eleven successes and the one
supplemented success, with the input result filenames recorded. The
eleven resolved assertions were not rerun, and the first raw result was
not rewritten.

Two local orchestration expressions also needed syntax/API correction
while preparing files (a JavaScript template-literal backtick and an
unavailable `structuredClone`). Neither invoked a scientific evaluator or
generated a scientific result; subsequent file preparation used the actual
preserved code/result strings. These are separate from the xAct and CAS
scientific execution records.

## Reproduction and stop condition

Run the exact saved evaluator inputs in a compatible Wolfram kernel, with
the official package available for the xAct wrapper. The current request
already performed these checks. Reproduction is a user/next-owner option,
not an instruction to rerun unchanged successful groups on every resume.

The algebraic count does not validate a native solver or a finite atomic
trajectory. The constitutive theorem and the local source-branch theorem
are proved analytically; their computational checks target the nontrivial
transitions. Independent review and the coding contract carry the remaining
implementation and rate-dependent continuation obligations. No further
optional scientific execution is needed for this unit after the listed
findings are closed.
