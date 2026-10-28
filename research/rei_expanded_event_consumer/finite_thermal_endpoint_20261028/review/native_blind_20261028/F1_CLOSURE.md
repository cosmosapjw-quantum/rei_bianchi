# F1 closure: represented source-temperature bridge

Project `cosmosapjw-quantum/rei_bianchi`; unit `finite_thermal_endpoint_20261028`; branch `research/rei-causal-prefix-consumer-20261027`; original review pin `b77c7b8d45c48a7e4722e733309430d5ba668b0d`. This closure concerns only the local F1 documentation correction and its single recorded targeted check. It reuses the unchanged Phase 1 and Phase 2 findings.

## Decision

**F1 is closed for the inspected corrected document.** The actual diff repairs the omitted multiplication residual, and the exact saved-data control validates both the corrected identity and the failure of the old unqualified identity. No further scientific repair or execution is required for F1.

| Stage | Final assessment | Scope |
|---|---|---|
| R6 | `pass_scoped` for the reviewed packet incorporating this correction | The original core derivations remain valid; the sole reason for the complete written packet's Phase 2 `partial` assessment is resolved by the corrected document identified below. |
| C9 | `pass_scoped`, retained | The prior implementation, preserved execution, source-binding and numerical conclusions remain unchanged. This documentation control introduces neither a new production algorithm nor a second numerical-study stage. |

The reviewed corrected file is `repair/R6_SOURCE_BATH_RECONCILIATION_20261028.md`, SHA256 `f97420be2426467fb7cf902e6fdd0b2fbae5cc3fa4e8acd718ce0a00e0e86be6`. The judgment applies to this repaired packet; it does not rewrite the historical review pin or assert that a Git publication has occurred.

## 1. The actual change closes the mathematical issue

I compared the complete original and corrected files with `diff -u`. The only change is the displayed bridge discussion around original lines 72–76, now corrected lines 72–80, including a dated provenance paragraph. The supplied `F1_MINIMAL.diff` agrees with that actual comparison. The original file has Git blob `9c4cb7aa481f63197fd61eff6c52c4b40be1a7da`, independently checked using `git hash-object`.

Corrected line 72 defines the separately decoded represented quantities theta, k and t, and

\[
\rho_\theta=\theta-kt.
\]

With the already established SI bridge \(T_a^E=\theta\,\mathrm{EV}/k_B^{SI}\), substitution gives, for the stated positive t,

\[
\frac{T_a^E}{t}
=\frac{(kt+\rho_\theta)\mathrm{EV}}{k_B^{SI}t}
=\frac{k\mathrm{EV}}{k_B^{SI}}
+\frac{\rho_\theta\mathrm{EV}}{k_B^{SI}t}.
\]

This is the identity now printed at corrected line 74. Corrected line 76 restricts the shorter relation to rho_theta=0. It therefore distinguishes the unrounded-model relation from the actual separately represented source values, as F1 required. The correction does not alter gas-energy ownership, the common reference volume, the particle denominator, the finite caloric formula, or the already correct production bridge residual.

The issue was a low-severity error in one written exact equality. Its closure does not erase the historical finding: Phase 1 proved the omission, Phase 2 confirmed the nonzero source residual, and the present change repairs the text.

## 2. The targeted control is appropriate and passes on the recorded evidence

I read all of `verify_f1_saved_bridge.py` and its raw output. The script imports only standard-library hashing, JSON, Fraction and path facilities; it neither imports `finite_thermal` nor evaluates the source. It reads the preserved C7 stdout identified in the scope file, verifies that input's SHA256, verifies the corrected document's SHA256, and requires the corrected displayed equation to be present (script lines 7–16).

The control then decodes the existing numerator/denominator strings as exact Fractions. It checks three necessary premises independently of the new displayed equality: the saved residual equals theta-k*t, that residual equals the frozen nonzero fraction, and the saved energy temperature equals theta*EV/kB_SI (lines 20–40). It uses the exact SI constant kB_SI=1.380649e-23 and the preserved represented EV conversion. These are the same conventions previously reviewed, not newly substituted decimal interpretations.

The nonzero residual in raw output lines 31–34 is

\[
\rho_\theta=-\frac{393372660608921}{40564819207303340847894502572032}.
\]

Raw output lines 39–54 preserve equal exact numerator/denominator pairs for the corrected left and right sides, and a nonzero correction to the old ratio. The positive t, EV and kB_SI imply that this nonzero rho gives a nonzero ratio correction. Thus the negative control has scientific content: omitting the term would fail for these actual represented source values.

Script lines 41–42 check the corrected equality and inequality with the old expression; lines 62–64 make any failed condition terminate unsuccessfully. The raw checks are true, `F1_EXIT_CODE.txt` is 0, and stderr is empty. This is exact rational acceptance, with no tolerance or rounded decimal comparison.

The five Boolean conditions belong to one targeted check of this identity. They are not five new stage completions. The arithmetic control is not an independent revalidation of the upstream source; its input provenance and original field binding were already established in Phase 2. The general identity follows from the written derivation above, while the recorded check binds that identity to the actual frozen values. This satisfies the recorded-rational-fields alternative in Phase 2 section 8, lines 286–299; editing or rerunning the original fixture is not an additional outstanding obligation.

## 3. Execution and identity limitations

The receipt records one invocation of the command in `PROPOSED_COMMAND.txt`, with the script and document hashes matching the files I inspected. The command uses a 10-second timeout with a one-second kill grace, a one-second CPU limit, and a 268,435,456-byte address-space limit. Its raw Bash timing is `wall_s=0.037 user_cpu_s=0.037 system_cpu_s=0.000`. These are displayed millisecond values for the timed command including timeout/prlimit/interpreter; they are not exact whole-session CPU accounting or a measurement of zero system CPU. No global budget-compliance conclusion is drawn.

`F1_SCOPE_AUTHORITY.json` is the preserved preparation snapshot and still labels itself `PREPARED_NOT_EXECUTED_NOT_PUBLISHED`. The separate actual execution receipt and raw files supply the later execution state. I do not treat the preparation status as evidence that the check was not run, nor rewrite it after the fact.

The parent identifies the executor as `/root/acquire_preserved_evidence`. I inspected its recorded command and outputs, not a new live execution or independently exposed runtime model identifier. The observable native reviewer task remains `/root/finite_thermal_blind_reviewer`; the instruction-level label is GPT-6 Astra Pro, with no independently verified backend model or launch-override telemetry. The filesystem is shared. This closure is a disclosed repair review, not an isolated blind phase.

The correction's provenance paragraph identifies this native review, and the supplied records contain acceptance and accounting labels. I used the actual diff, script, rational fields and exit evidence to decide closure rather than treating those labels as a verdict. The original controller self-review and operational handoffs remain outside scope.

This reviewer performed only file reads/comparisons, hashes, and report writing. No scientific code, test, CAS, provider, source replay, IVP, or additional review task was executed or delegated during closure. The parent reports production code and tests unchanged; no production change occurs in the inspected repair diff, and I did not reopen the unaffected code.

## 4. Bounded read and integrity ledger

All repair paths below are relative to `/workspace/scratch/cc0531120bc9/finite_thermal_native_review/repair/`.

| File | Content inspected |
|---|---|
| `R6_SOURCE_BATH_RECONCILIATION_20261028.original.md` | Lines 65–86; complete-file diff, SHA256 and Git blob checked. Other unchanged paragraphs were not scientifically reread. |
| `R6_SOURCE_BATH_RECONCILIATION_20261028.md` | Lines 65–90; complete-file diff and SHA256 checked. |
| `F1_MINIMAL.diff` | Lines 1–18, complete. |
| `verify_f1_saved_bridge.py` | Lines 1–64, complete; SHA256 checked. |
| `F1_SCOPE_AUTHORITY.json` | Lines 1–54, complete; SHA256 checked against receipt. |
| `F1_ACTUAL_EXECUTION_RECEIPT.json` | Lines 1–73, complete. |
| `F1_STDOUT.json` | Lines 1–61, complete; SHA256 checked against receipt. |
| `F1_STDERR.txt` | Verified zero bytes and empty-file SHA256. |
| `F1_EXIT_CODE.txt` | Line 1, complete; SHA256 checked against receipt. |
| `F1_ACCOUNTING.txt` | Line 1, complete; SHA256 checked against receipt. |
| `PROPOSED_COMMAND.txt` | Line 1, complete. |

I additionally reread only `reviewer/PHASE2_POST_EVIDENCE.md` lines 286–299 for the targeted-validation scope. The saved C7 input `evidence_phase2/extracted/C7/attempt_01/stdout.txt` was byte-hashed again, matching `2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948`; its scientific content and original source bindings are reused from Phase 2 rather than reread. The check script's observed SHA256 is `e6af55906339f89d895f9e0619d2b5d180bbdc5427cd82f7061cffeb28a13ff5`; raw check stdout is `9497c4a49f3f31e728997bd198d2f7e3b90a81dd3c45c1d589240e8610a14f05`.

Both prior reports were byte-hashed and remain unchanged:

- Phase 1: `a225c208903de9bedb69406c112c1556791b3ac4acadf4a5c57d49b4e2eba792`.
- Phase 2: `e50b833bb833cee8a8bb73ac366ad307817fd2cb4a263dcbedffbe9563800376`.

No new source census, broad numerical-study read, upstream solver revalidation, or read of unrelated repair material was needed. The original read/exposure ledgers and numerical limitations remain in the frozen reports.

## 5. Remaining obligations and return boundary

There is no remaining scientific obligation for F1. Any delivery of this repair should carry the inspected corrected bytes and preserve the prior reports and raw check evidence; this is a provenance condition, not a request for another computation. Actual REI recipient temperatures/native25 activation, physical error radii, self-consistent thermal feedback, and upstream solver validation retain their previously stated scope boundaries.

The repaired written R6 packet is `pass_scoped`; C9 remains `pass_scoped`. This closure supplies no additional stage count and authorizes no new node. Review complete.
