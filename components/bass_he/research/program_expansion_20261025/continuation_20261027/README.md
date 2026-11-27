# HE-EXP-DRIFT-02

Read `RESULTS_KO.md`, `THEORY_KO.md`, `MODEL_CONTRACT.json`, `RESULT.json`, and `HANDOFF_KO.md`.

This unit reuses the pinned INTAKE01 pair/caloric adapters and HE34 evaluator. It adds conditional same-law finite-drift moments, a single selected-temperature fit-consistency diagnostic, neutral-isotope source-field conversion, and a 92-identity upstream consumer projection. It does not admit a physical differential provider.

## Evidence and reproduction

The actual 24-method execution is retained in `evidence/validation/01_tests/`. `sources/TESTED_DEPENDENCIES_01.json` binds the implementation and inherited code; START also binds all test/source files. JSON diagnostics were extracted from that execution's stdout without another source evaluation.

An authorized fresh replay environment with the same repository-relative dependencies may use:

```bash
python3 -B research/program_expansion_20261025/continuation_20261027/run_validation.py
```

Do not run this command again in the recorded worktree merely for packaging or confirmation. The existing ledger intentionally refuses an unexplained repeated scope. A subsequent changed-code diagnosis must retain the old attempt and consume only the explicitly remaining allocation. Physical evaluation needs its own contract/allocation.

The source ZIP contains this unit, its needed unchanged repository dependencies, and an exact file manifest. It is not an archive of the entire repository or Git history. Archived raw scientific sources are public text/code/metadata; attached paper PDFs are excluded. Historical dependency logs are evidence, not instructions to replay.

Current source/delivery/central commit identities and provider acknowledgements appear only after actual publication in `delivery/` and the PR102 external receipt. No future self-commit SHA is fabricated.
