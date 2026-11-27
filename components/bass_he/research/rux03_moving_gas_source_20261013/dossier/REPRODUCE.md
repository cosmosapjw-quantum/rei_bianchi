# Reuse and reproduction

Unit: HERE_RUX03_MOVING_GAS_SOURCE_05.

## Read the completed construction

Start with `REPORT_KO.md`, then the two derivations and the independent
decision. `CLAIMS.json` maps M01–M07 to definitions, assumptions, proofs and
actual evidence. `CODING_CONTRACT.md` gives the implementation consequence.
`NEXT_DAG.json` records the retained and new owners.

The final science manifest is a content manifest, not a new scientific
result. It excludes its own hash to avoid self-reference. A candidate
manifest binds the exact author's files examined by the reviewer; the
final manifest additionally binds the independent decision and final
status record. Publication and delivery receipts are outer records.

## Actual scientific input records

| Purpose | Exact input | Actual output |
|---|---|---|
| Final xAct tensor calculation | `evidence/XACT_MOVING_SOURCE_EXECUTED_v3.wl` | `evidence/XACT_MOVING_SOURCE_RAW_v3.json`, normalized tensor result |
| Primitive inverse and warm fixtures | `evidence/primitive_exact.wl` | primitive raw result, normalized result and execution context |
| Finite stage and full Jacobian | `evidence/MOVING_SOURCE_CALL_INPUT.json`, its extracted executed `.wl` | original raw and `_v1.json` |
| Targeted positive Jacobian certificate | `evidence/MOVING_JACOBIAN_POSITIVITY_CALL_INPUT.json`, its extracted executed `.wl` | targeted raw and normalized result |

`MOVING_SOURCE_EXACT_RESULT.json` records which assertion comes from which
actual run. The first finite-source batch has eleven successes and an
undecided inequality; the supplemental run closes that one assertion.
The first two xAct raw failures are diagnostic evidence, not successful
validations. The canonical source files in `derivations/` are for reading;
the call-input JSON fields preserve the exact submitted code strings,
including their final-newline convention.

The actual Wolfram kernel was version 15.0.1 on Linux-x86-64. The xAct
wrapper downloads the named official xAct 1.3.0 archive, verifies its
recorded hash and loads the real package. It uses pure Wolfram xPerm.
No third-party archive or full paper PDF is redistributed in this dossier.

In a separately supplied Wolfram installation with the required network
access, an owner can print the result of a standalone exact input with,
from the unit directory:

```sh
wolframscript -code 'Print[Get["evidence/XACT_MOVING_SOURCE_EXECUTED_v3.wl"]]'
wolframscript -code 'Print[Get["evidence/primitive_exact.wl"]]'
wolframscript -code 'Print[Get["evidence/MOVING_SOURCE_WOLFRAM_EXECUTED.wl"]]'
wolframscript -code 'Print[Get["evidence/MOVING_JACOBIAN_POSITIVITY_EXECUTED.wl"]]'
```

These commands describe optional reproduction; the saved evidence was
actually produced through the Wolfram evaluator, not these local CLI
commands. A kernel that prints the same conditional inequality in the first
finite-source batch is reproducing the documented observation. Compare the
supplemental positivity certificate as well.

## Valid reuse and recomputation triggers

Reuse the parents' common-gas four-force, neutral reference/binding/escape
ownership and accepted rate/provider identities while their recorded
source identities and assumptions are unchanged. Current exact identities
are in `source_map/VALID_REUSE_IDENTITY.json` and `CURRENT_SOURCE.json`.
Their previous 45 and 47 successful groups were not rerun or counted as
new evidence here.

A changed EOS or reference mass invalidates the affected primitive proof;
a changed rate or event normalization invalidates its source adapter and
thermal-budget correspondence; a changed angular measure affects the
ring/directional map; a changed time foliation affects the finite scheme.
Resume at the earliest affected derivation, preserving unaffected results.

## Numerical implementation remains its own unit

The THEORY result includes a global constitutive inverse at each fixed
composition and a constructive local full-stage branch on a specified
smooth interior. It does not contain a production nonlinear solve, certified
numerical bounds for an actual rate box, native/ODE results or a cosmological
history. Those exact obligations are handed off in the coding contract and
continuation-certificate node. The positive single-beam/pair formulas are
channel-isolated references and must be labeled as such in future tests.
