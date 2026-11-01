# Actual first GitHub Actions attempt failure (preserved)

- PR #336 first posted HEAD `6891e5d51a29c5d9cdcd9f28e840d2cd0c665c2e`.
- GitHub Actions run `41273886764` FAIL (three lane jobs), each failed in setup before nonlinear map execution.
- Exact exception `ValueError: ORIGINAL_PARENT_STATE_DRIFT`.
- Cause: a **63-character** assistant-transcribed `ORIGINAL_ARRAY_SHA`, not the genuine 64-character source SHA-256. The authentic original PR #327 source has `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.
- Repair: change only the wrong code constant and README, introduce test for all three 64-character source locks and exact expected array SHA. Do not change original archive/owner, source, map, numeric tolerance or source-state data.
- Classification: IMPLEMENTATION_PROVENANCE_REFERENCE_ERROR. Not original input mutation, mathematical counterexample or 26-event solver failure.
- Initial GitHub job outputs and failed head are durable; targeted correction uses one non-force fast-forward commit on the same isolated Draft PR.
- CENTRAL_DAG=28/88; WORKING=33/88; FAST=4/7; CANONICAL_DELTA=0; FIRST_INTERVAL=BLOCKED_MINIMUM_STEP.
