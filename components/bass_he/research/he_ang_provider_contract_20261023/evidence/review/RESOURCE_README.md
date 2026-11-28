# HE-ANG resource tools — authoring delivery

These stdlib-only helpers were authored without executing either helper or any
scientific command. The controller chooses the already authorized R7/C6 command.

## Bounded execution

Install run_bounded.py and verify_saved.py in the unit's code/ directory, or
provide --unit. The default is the nearest parent containing BUDGET.json.

    python code/run_bounded.py --label R7 -- python theory/check_witness.py
    python code/run_bounded.py --label C6 -- python code/check_controls.py

The child cwd is the unit directory. HEANG_ATTEMPT_DIR identifies its fresh
output directory. stdout.txt and stderr.txt are always retained there; child
outputs placed there are hashed. Other child-created output paths are outside
this automatic output-hash scope and need an explicit manifest.

BUDGET.json and CONTRACT.json remain unchanged. RESOURCE_LEDGER.json stores
append-only START/FINISH events referencing immutable attempt receipts.
The file is replaced atomically to append an event; earlier event entries and
receipts are preserved. A nonblocking exclusive flock serializes invocations.
A missing ledger with prior STARTs, unmatched START, unknown cost, changed
frozen identity, or insufficient remaining budget prevents another child.

The actual child limits come from the frozen budget: CPU2 s, wall5 s and
RLIMIT_AS256 MiB for this unit. CPU limits are rounded downward to integer
RLIMIT_CPU seconds when the remaining allocation is smaller. Timeout kills
the process group and waits for the direct child. There is no automatic retry.
Failures and interrupted attempts retain their raw files. A START without a
completed measured FINISH needs explicit reconciliation before another run.

The parent measures the whole reaped child using RUSAGE_CHILDREN across
Popen/startup/wait/exit. It also records RUSAGE_SELF through the receipt's
measurement endpoint and conservatively debits that known wrapper CPU.
Cumulative wall debit uses the wrapper module monotonic clock through the
same endpoint; the child lifetime is additionally recorded separately.
The wrapper wall clock starts after its imports, so interpreter/import wall
before that clock is not represented. Child interpreter startup is included.

The later FINISH/ledger persistence and wrapper exit are expressly outside the
measured interval, as non-scientific bookkeeping. A receipt does not claim to
time the entire wrapper through process exit. Linux peak RSS is reported in
KiB; RLIMIT_AS is an address-space cap, not a peak-RSS cap.

The authorized commands are single-process exact/validator controls.
RLIMIT_CPU is per process, not a process-tree cgroup quota. RUSAGE_CHILDREN
includes descendants only when their accounting is returned through waited
children. A descendant that outlives the direct child is killed and marks the
attempt cost unknown, blocking further execution. This helper does not provide
a general arbitrary-process-tree resource sandbox.

## Saved evidence verification

    python code/verify_saved.py --archive-dir /path/to/stage_archives --allow-incomplete --output /path/to/reports/C8.json
    python code/verify_saved.py --archive-dir /path/to/stage_archives --output /path/to/reports/FINAL.json

This helper reads saved bytes/JSON only. It does not import scientific code,
replay tests, rerun IVPs, render, access a network, or remeasure science.
It verifies available SCIENCE_MANIFEST.json and LOCAL_FILE_MANIFEST.json
files, DAG order/counts/holds, twenty stage Dropbox/Drive ACK identities and
sizes, resource event/receipt/output hashes and cumulative debit arithmetic.
Without --allow-incomplete, missing final manifests or incomplete stages
produce a nonzero exit. --allow-incomplete reports IN_PROGRESS explicitly.

Historical stage hashes are checked against current bytes when identical,
then against the corresponding stage archive. Exact unit/<relative> tar members
are supported; --archive-dir resolves ACK basenames after old absolute paths
become unavailable. Available stage archives are checked by outer SHA256/size,
root MANIFEST inventory and every listed payload SHA256/size. An available
archive with missing or mismatched historical evidence is an error. Missing
required historical archive bytes remain pending and prevent final_complete;
--allow-incomplete may still return an explicitly interim report.
Provider ACK checks use saved records only and do not imply new remote-byte
verification. Archive payloads are read without extracting files to disk.

Both manifests must exclude their own file, and they may not hash each other
in a cycle. LOCAL_FILE_MANIFEST may include SCIENCE_MANIFEST in one direction.
The verifier refuses --output pointing at any verified input or referenced
artifact, so it cannot invalidate a manifest by replacing an included report.

For final assembly: freeze immutable science code/results first, create the
science manifest excluding delivery metadata, then finish staged delivery and
make a local manifest of the declared current snapshot. Put the fresh final
verification report outside that manifest scope (for example a capsule-level
verification/ directory). Archive metadata and its uploaded ACK cannot be
inside an archive whose own final hash/ID they state. Git expected-SHA push
readback and the containing delivery commit identity remain separate receipts;
this offline verifier never infers that publication occurred.

The helpers target the Linux/POSIX runtime used by this unit. Relocation of
paths is supported; operating-system/runtime compatibility or fresh scientific
reproduction is not certified by a saved-byte check.

Manifest schema: {"files":[{"path":"unit-relative path","size":123,
"sha256":"..."}]}; bytes is also accepted as the size field. Files mappings
from relative path to a digest/metadata record are also accepted.
