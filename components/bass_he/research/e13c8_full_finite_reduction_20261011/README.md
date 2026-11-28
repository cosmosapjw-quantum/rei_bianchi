# BASS_HE E13C8 full finite reduction

The actual 2,331-path E13C7 MPI return has been verified, exactly reduced in ChatGPT,
and independently admitted for the fixed captured OFF finite target.

Read [REPORT_KO.md](REPORT_KO.md), [CURRENT_STATE.json](CURRENT_STATE.json),
[the independent decision](review/INDEPENDENT_DECISION.json), and
[the next work graph](NEXT_DAG.json).

**New NCP heavy tasks: 0.** The current [handoff](NCP_HANDOFF_INTERNAL_KO.md) closes
the completed batch. No repeated N1024, automatic N2048, or benchmark replay is
authorized by this handoff. The next method is a ChatGPT-side theory/short-pilot
candidate, not an implemented replacement enclosure.

Physical, continuum, production and receiver remain HOLD. Actual 64-rank activity
is established; CPU utilization and a same-work serial speedup were not measured.

## Complete evidence package

The complete archive includes two immutable dependency ZIPs:

- `dependencies/E13C7_INPUT.zip`: original source, captured inputs, local evidence,
  scientific and execution locks, and inherited documentation.
- `dependencies/E13C7_NCP_RETURN.zip`: actual full 2,331-path MPI return.

It also includes this loop's exact reduction, saved-data radius decomposition,
derived observables, telemetry, independent reviews, analysis code and handoff.
The Git publication is a compact review projection; large dependency ZIPs and
per-path rational data are archive-only.

Use the externally hash-pinned transfer manifest and `code/restore_transfer.py`
only when restoration is needed. Part filenames are not identities; actual bytes
and SHA-256 select pieces and the manifest defines their order. Optional hydration
restores both dependencies without invoking scientific computation.

## Optional local analysis reproduction

Reproduction commands are documented in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
They are archive/ChatGPT-side analysis procedures, not a new NCP task list. All
actual outputs already exist. Use fresh output directories and preserve failures.

## This Git projection

This checked-in directory is the compact review projection described in
[GIT_PROJECTION_README.md](GIT_PROJECTION_README.md). It is not a complete runtime
package. [ARCHIVE_ONLY_FILES.json](ARCHIVE_ONLY_FILES.json) lists every omitted
source file with exact byte and content identities. Actual backup pointers belong
in [BACKUP_LOCATIONS.json](BACKUP_LOCATIONS.json); they must be filled from real
upload/readback evidence before publication. Reports copied from the archive keep
their original archive-relative evidence links.
