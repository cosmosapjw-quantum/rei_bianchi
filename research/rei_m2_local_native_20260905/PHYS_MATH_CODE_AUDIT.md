# PHYS-MATH-CODE review: first native execution

Second sequential review by the same Host Codex, after PHYS_MATH_AUDIT.md.
No independent reviewer, source repair, replacement implementation or retry.

## Verdict

The existing launcher executed real native xCoba and emitted both declared
PASS statuses. Its exact receipt predicates pass, including 12/12 booleans,
416 evaluated exact-zero entries, exit 0, no timeout, and unchanged clean
source/input bytes. One message-reporting limitation was found in the raw log.
This preserves the observed component-calibration result while withholding
any claim that the complete kernel invocation was message-free.

## First finding: NATIVE_API_OR_MESSAGE

`native/stdout.log`, line 19, contains:

```text
Verbose::shdw: Symbol Verbose appears in multiple contexts {xAct`xCore`, System`}; definitions in context xAct`xCore` may shadow or be shadowed by other definitions.
```

The warning precedes the first `DefManifold` output. It is absent from the
native receipt's `messages=[]`. In the pinned calibrate.wls, activation,
`Get[xcobaFile]` (line 58), and the definition of nativeBody (lines 63-157)
occur before `Block[{$MessageList={}}, ...]` (lines 158-162). The receipt
therefore reports messages from the nativeBody evaluation interval, not all
setup/definition/loading messages. The exact point within that earlier phase
that emits the warning was not separately rerun or instrumented.

This is an observed native message and a scope limitation of message evidence,
not `RUNTIME_UNAVAILABLE`, a nonzero mathematical residual, an archive mismatch,
or proof of invalid curvature. The two original PASS status strings are not
edited. The empty stderr and zero exit code do not erase a stdout warning.
No additional mandatory execution gate is introduced by this review.

Minimal BASS-owner follow-up: make the existing diagnostic's message scope
explicit and retain relevant setup/definition warnings in its receipt; resolve
or explicitly adjudicate this namespace-shadow warning before claiming a
message-free run. Do not merely silence messages to obtain an empty list.
Any changed-source run needs a separately authorized version; this task has
already used its single invocation and made zero BASS patches.

## Execution and data-flow review

| Item | Observed evidence and scope |
|---|---|
| Exact checkout | Detached BASS HEAD/tree match the handoff; full porcelain empty before and after. |
| Runtime | `/usr/bin/wolframscript`, real path `/opt/Wolfram/WolframScript/bin/wolframscript`; Wolfram Engine 15.0.0. |
| Archive | Existing Downloads copy has the frozen SHA-256; extracted copy and source copy still match. No download. |
| Native engine | DefMetric, MetricInBasis, MetricCompute, ComponentArray and ToValues are in the executed path; actual package/metric/connection output is retained. |
| Packages | xTensor 1.3.0 and xCoba 0.8.6; xCoba resolves under the verified temporary extraction. |
| Independent carrier | Reference Christoffel/Riemann/Ricci and spatial K/divergence are assembled separately in the same Wolfram kernel. Independence is algorithmic, not a separate CAS/reviewer. |
| No target replacement | Native Riemann/Ricci come from xCoba. eNative uses native Ricci and declared stress; mReference is constructed afterward. Neither an expected target nor a negated physical Ricci replaces the native tensor. |
| Full checks | Independent H1,H2,H3,a0 remain symbolic in full Riemann/Gauss/Codazzi checks. Sentinel replacement appears only in two counterexamples and the discrepancy report. |
| Exact results | SameQ to integer zero in the source; separate readback parsed only zero/list syntax, checked dimensions and every scalar leaf. No approximate zero or unevaluated expression was admitted. |
| Messages | Native computation interval reports []; one pre-evaluation `Verbose::shdw` warning remains in raw stdout as explained above. |
| Timeouts | Launcher default 360 s retained; native body budget 180 s and activation budget 90 s unchanged. Actual launcher elapsed 8.520384 s; timeout false. |
| Preservation | CHECKPOINT, PROCESS_RECEIPT, native JSON, native stdout/stderr, wrapper stdout/stderr and wrapper exit code preserved byte-for-byte. OUT did not exist before launch. |
| Postcheck | Source blobs/SHA-256, archive, HEAD/tree and full porcelain independently reread; clean and unchanged. |

Source/readback JSON identifies the precise paths and digests. No BASS full
init, optional CAS fallback, REI production worker, native attempt ref, lease,
Section-0, registry amendment or provider operation was invoked.

## Publication boundary

Only evidence and audits are added to a new REI child of handoff PR #66.
REI #64/#65 algebra and their historical receipts remain intact. Publication
verification is a repository check, not a second native run or a physics proof.
The first run is sufficient to preserve the native result and the observed
message limitation; there is no repair-until-green loop.
