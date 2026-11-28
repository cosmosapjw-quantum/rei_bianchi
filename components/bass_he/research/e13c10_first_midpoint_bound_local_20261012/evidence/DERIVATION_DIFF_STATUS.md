# Derivation diff status

`FIRST_PATH_DERIVATION.diff` (SHA256 e4f6c7b785d450a365ac70ce4599780e7e111ad653c907208080cde0c620d3dd) is preserved history of the initial uncached assembly. It is not the final diff. It predates the corrected source-output comment even in locked INITIAL_N32; the comment there incorrectly retained an E13C9 byte-equivalence claim. Executed INITIAL_N32 already corrects the comment and its pinned source, not this draft diff, defines that execution.

`FINAL_FIRST_PATH_DERIVATION.diff` is the actual final source comparison against the pinned E13C9 signed_volterra.py. It shows first-integral replacement and cache/provenance wiring, removal of locally duplicated Volterra helpers in favor of unchanged imports, and retained path/segment output assembly. Final SOURCE_LOCK.json is authoritative for the executed candidate. No old source or diff was overwritten.
