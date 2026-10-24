# Pressure continuation: reattached-input recovery review

## Decision

**UNCHANGED / RECOVERED.** All 20 numbered attachments are now present in
`/workspace/scratch/03a65a604d4c/project_sources`. Every retained byte count
matches. All 13 previously recorded SHA-256 values match exactly: the five
text inputs 01, 04, 05, 07 and 08; archives 10, 11, 12, 14, 17, 18 and 19;
and standalone PDF 20. No changed input or new pressure-specific defect was
established by this bounded recovery check.

The prior semantic review is reusable for those identical inputs at its
original inspection depth. This is not a new full-content audit of every
archive or PDF. This attachment decision makes no numerical admission for
the prepared pressure child; independent review of the actual implementation,
authorization and raw outcome is a separate next task.

Reviewer: `/root/pressure_review`. Requested role: independent Astra read-only
reviewer, separate from `pressure_coding`. No cross-family independence claim
is made. The current live policy and fixed scientific authorities are relayed
by root; this attachment subtask does not claim a fresh live Git verification.

## Evidence and recovered availability

The comparison uses these retained records without editing them:

- `/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/survey/attachments/ATTACHMENTS_MANIFEST.json`
- `/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/survey/attachments/ATTACHMENTS_REVIEW.md`

The new `ATTACHMENT_RECOVERY_MANIFEST.json` records the actual source paths,
retained and observed sizes/hashes, inherited semantic inspection levels,
recovered inventory paths, and the selected member texts recovered here.
Hashing establishes the stated byte identity; it does not establish semantic
review of previously unread material. For attachments 02, 03, 06, 09, 13, 15
and 16, no retained hash exists, so the finding is presence and matching size
only. Their payloads remain outside this finite pressure review.

The seven historical inventory JSON files and selected-member extracts named
in the retained manifest were absent locally. Their data was recovered from
the identical attached archives under this new `attachments/` directory.

| Attachment | Recovered members | Retained count | Identity basis |
|---|---:|---:|---|
| 10, Rustcore R-DAG | 23 | 23 | Archive SHA-256 and count match |
| 11, low-ell automation kit | 38 | 38 | Archive SHA-256 and count match |
| 12, background/high-ell harness | 103 | 103 | Archive SHA-256 and count match |
| 14, bianchireview87 | 470 | 470 | Archive SHA-256 and count match |
| 17, offline Rustcore | 8,451 | 8,451 | Archive SHA-256 and count match |
| 18, literature collection | 7 | 7 | Archive SHA-256 and count match |
| 19, paper collection | 8 | 8 | Archive SHA-256 and count match |

Because the old inventory files themselves were missing, this is not a direct
byte comparison between old and new inventory JSON serializations. The
identical parent archive and matching retained count support recovery of the
same archive membership. These inventories include directory entries where
the archive contains them. Nested archives were not recursively expanded.

Ten previously selected member texts were recovered into `selected_text/`:
the two members from archive 11, three from archive 12, four from archive 14,
and the README from archive 17, exactly as named in the retained manifest.
Recovery of the full report source from archive 14 does not upgrade the old
partial semantic read to a full read. No original attachment or old artifact
was modified. Large binary payloads were not copied into this new package.

The report PDF 20 also matches its retained hash. Its prior excerpt-based
semantic review remains usable. The missing extracted text was not recreated
because this attachment check found no specific unresolved PDF question.
There was no rendering, visual inspection or figure acceptance. PDFs enclosed
in archives 18 and 19 remain inventoried only, with no new content claim.

## Relevance to the finite pressure unit

The unchanged text presets and archived workflow documents preserve their
previously reviewed scope. The old solver-wide, build, dual-audit and plotting
presets do not introduce an additional whole-suite run or unrelated figure
into the current one-child pressure check. The figure-specific inputs 07 and
08 apply to figure deliverables when such deliverables are actually selected.

The retained archive-14 review distinguishes an externally consumed local
source/history from self-consistent atomic evolution and cosmological
transport. The retained report-20 review distinguishes algebraic realizability
and kinetic stress bookkeeping from dynamical or thermalization claims.
Those distinctions remain applicable when interpreting a finite pressure
moment interval. They do not, by themselves, establish a time-evolved pressure
stock, a redshift law, a thermalization/deposition model, or a completed REI
transport closure.

The inspected attachment content has not changed and does not establish a
replacement for the root-pinned scientific source contract. This is a bounded
statement about actual inspected evidence, not a claim that every unread
archive/PDF member lacks relevant material. Any newly selected redshift-stock
theory must be assessed on its own assumptions and equations when supplied.

## Execution and stopping boundary

This subtask performed only filesystem discovery, retained-record reading,
streamed hashing, archive metadata parsing, selected text recovery, and writing
small recovery evidence. It did not source or run an attachment, import the
scientific implementation, install a toolchain or CAS, run Rust/Cargo/builds,
render figures/PDFs, execute science/tests, access the network, or mutate Git
or cloud state.

The original scratch inputs were used directly as instructed. The approved
one-child CPU 1 s / wall 5 s / no-retry allowance remains solely the root's
execution allowance; this recovery creates no additional allowance. There is
no further attachment gate. Stop this recovery review here and inspect the
actual pressure outcome only when root supplies it.
