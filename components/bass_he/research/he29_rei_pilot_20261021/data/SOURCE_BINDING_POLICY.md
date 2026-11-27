# Reviewed source binding

The external reviewed_source_manifest.json binds the four frozen upstream files and the reviewed coordinates.py/pilot.py adapter. Runtime verifies these bytes before result reuse or launch. A mismatch raises SourceBindingError and must never trigger automatic science reruns. This is minimal accidental-edit and reproducibility control.

The reviewed recovery adapter retains frobenius-v1 and existing case identities because its scientific body and contract are unchanged. Future scientific changes require a new case/version and review; regenerating the manifest alone is not scientific approval. Metadata, runner and plot edits do not automatically force case reruns. Original upstream source provenance remains in source_identity.json.

An existing failed or incomplete result is copied byte-for-byte into attempts/case_id.attempt_NNNN.json before its result path can be replaced.
