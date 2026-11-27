# HE-ANG-SOURCE-HEX-INTAKE final scoped science review

Reviewer: `/root/source_physics`. Date: 2026-10-24 KST.

## Decision

**PASS_SCOPED for source intake qualification, represented-coefficient mathematics, and the actual A2 dataset conclusion. This scoped scientific intake is COMPLETE_SCOPED; physical HE-ANG-SOURCE remains SOURCE_INPUT_PENDING.** No empirical angular correction, finite-mass physical provider, general source no-go or paper-level novelty is approved. Final publication identity and execution gates remain the C9/delivery owner's responsibility.

This review adds no scientific execution. It reuses the completed independent R6 report, reads the actual A2 output and finish receipt, and inspects the limited A1/A2 read-path diffs. The original R6 document remains unchanged at SHA256 `4f2f56dec101c2d5139f7075bbc386d2102565de89ca27d9de7970aef7c17ce3`.

## Identities and mathematical dependency reuse

The historical regenerated module review was performed at SHA256 `8c2a510e9d34f4a54a6035d851b32aa629b77c8ebd89c35eb331abeedb87c4c8`. That review is retained as a historical record rather than relabelled as a review of later bytes.

The A2 executed/read module is SHA256 `2196134dbfd7b757eaef3a83618af86c66332a550d9008166d13ac88e8b4935d`, matching `evidence/execution/A2/source_freeze.json`. The A2 source-manifest SHA256 is `72208681854e40aadbdfccb25d517daebd827572f291ac600d71b141523f687d`.

The inspected `A1_code.diff`, `A1_postexecution_guard.diff` and `A2_code.diff` change SQL record delimitation, literal validation/compiled patterns, catalogue record dispatch and dialect selection. A1 adds an explicit newline-record dialect backed by `hex-db/src/db.cpp::hex_import_`; A2 bulk-validates numeric-only literal rows with the same number grammar. The initial semicolon default and source/memory-size caps remain. These changes do not modify `IonfRow.normalized_coordinate`, generic `decode_ionf_row`, coefficient decoding, `exact_tail`, `select_terms` or `evaluate`.

Accordingly the previously established mathematics remains applicable:

- source `C0/2` convention and the normalized interval map;
- exact entire-suffix L1 bound for the represented finite binary64 coefficients;
- minimum prefix selected by an explicit absolute tolerance;
- separation of finite-polynomial omission from floating evaluation, source fit/convergence and physical error;
- generic raw decoding separated from H1-only availability;
- no silent reconciliation of the ionf/ionamp versus TDCS radial-factor difference;
- fixed-proton source separated from finite-proton-mass event dynamics.

The final publication CORE identity, A3 word-boundary guards and execution-accounting review belong to C9. This science report pins the A2 evidence actually read and does not pretend to certify unseen later bytes. The coefficient theorem and data interpretation are reusable only while those dependencies remain unchanged.

## Actual dataset evidence and conclusion

The reviewer read `evidence/execution/A2/04_catalogue.stdout.txt` and `04_catalogue.FINISH.json`. The finish receipt reports successful process completion, empty stderr and a 902-byte stdout with SHA256 `9e8b8a1e77a1b230153f7b403318c92c66e2751da431ce829ff8ebce3137be92`.

| Evidence item | Observed value |
|---|---|
| Input file | `Hex-170210.sql.xz` |
| Compressed bytes | 7,880,672 |
| Compressed SHA256 | `afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101` |
| Decompressed bytes | 69,441,007 |
| Decompressed SHA256 | `82def29890bba56bb31f31524dcbea58bd0a0f5b39441ee7b6594bd28fc54896` |
| Explicit dialect | `hex-lines` |
| All tmat INSERT rows | 948,557 |
| H1 initial `(1,0,0)` tmat rows | 86,457 |
| H1 tmat incident energy extrema | `1e-7` to `0.9374` Ry |
| All ionf / H1 ionf rows | 0 / 0 |
| SQL executed | false |
| Physical provider values inferred | false |

The extrema describe recorded rows, not continuous energy coverage or calibrated accuracy. They lie below the fixed-nucleus H1 ionization threshold of 1 Ry. This exact dataset contains no numerical ionf rows from which to admit the selected H1 angular-ionization source. **SOURCE_INPUT_PENDING is therefore the correct physical gate.** Absent ionf rows are not substituted with zero cross sections, manufactured coefficients, a mismatched CCC total or an empirical correction.

The earlier statement-cap failure remains preserved. Before successful A2 completion the appropriate data status was unknown, and no absence inference was licensed. The final conclusion uses the complete A2 catalogue, not the bounded prefix diagnosis. No other source family or uninspected release is ruled out by this file-specific finding.

## Remaining physical obligations

Actual above-threshold H1 ionization coefficients/joint data remain needed, together with producer ABI, source normalization/channel reconciliation, spin and indistinguishable-event counting, slow-electron/full-domain support, source convergence and model uncertainty. A finite-mass source or explicitly named finite-mass approximation must still satisfy the reused HE-ANG common-law/frame/event contract. The fixed-proton code and synthetic polynomial controls do not discharge these obligations.

The next-source contract must preserve this input gate. Missing coefficients do not authorize a full Hex scattering solve within this intake's existing budget; that computation would require a distinct frozen source/execution contract.

## Scope of execution review

This reviewer ran no tests, quadrature, catalogue, physical scan, collision solver or IVP. The A2 finish receipt records CPU `8.144438999999998` seconds and wall `8.193171290004102` seconds under a nominal per-invocation 8-second CPU setting. Those measured values are preserved rather than rounded into compliance. Resource accounting, operating-system limit granularity and cumulative approval gates require the separate execution/C9 ledger decision; this scientific PASS_SCOPED is not a claim of full resource-cap certification.

The authored `theory/SOURCE_QUALIFICATION_KO.md` now states the observed catalogue result while preserving the first failure and its limited diagnosis. The independent R6 report is reused unchanged. No completed X1/HE38/HE-ANG science has been rerun or promoted.
