# ATTEMPT 5 — cumulative sandbox CPU budget

Classification: `HOST_EXECUTION_BUDGET_NOT_SCIENCE_FAILURE`.

The fresh-process parent completed and SHA-sealed the first two shape workers, but the third worker was throttled when all three were launched under one sandbox command. The third lane completed normally in a separate top-level command in 17.26 s.

Resolution: retain one worker artifact per shape lane and split execution from merge. `--lane-worker` performs exactly one heavy lane; `--merge-workers` performs only deterministic validation and aggregation. This mirrors the repository's established file-isolated scientific-test policy.
