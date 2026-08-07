# Independent review

The result is internally consistent with the sealed input lock.

- Recursive bisection starts at partition 8 and stops at the predeclared 1024.
- Fixed-point failure changes to local-error failure at partition 128, so the
  controller distinguishes solver globalization from truncation error.
- All three lanes produce the same resolved thermochemistry because their
  differences remain confined to the unresolved subgrid allocation, whose
  resolved source is exact zero. This is expected, not evidence of post-hoc
  lane collapse.
- Partition 4096 is a useful feasibility witness but is non-load-bearing.
- The owner hot-path speedup is supported by a comparable legacy benchmark;
  whole-solver speedup is not.
- The stage should remain fail-closed and authorize a second-order
  positivity/conservation preflight rather than silently extending the minimum
  partition.

Recommended verdict:

```text
DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS
```

- Repository-wide verification covers all 150 collected tests in 33 fresh-process file shards. Two monolithic executions timed out without an assertion failure at different boundaries and are preserved as a runtime-isolation issue.
