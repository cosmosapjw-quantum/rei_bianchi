# SciSpace methodology role lock

Search question:

> What peer-reviewed workflow-provenance and runtime-verification methods
> support revalidating a mutable external authorization policy immediately
> before an irreversible exactly-once scientific computation, rather than
> trusting a previously generated static receipt?

Relevant methodology returned by SciSpace includes:

1. Dubey et al. (2009), *Using Runtime Verification to Design a Reliable
   Execution Framework for Scientific Workflows*, DOI
   `10.1109/EASE.2009.13`.  Role: online monitoring of workflow execution
   against specified invariants.
2. Munir and McClatchey, *Cloud Infrastructure Provenance Collection and
   Management to Reproduce Scientific Workflow Execution*, arXiv
   `1803.06867`.  Role: infrastructure state is part of execution provenance.
3. Fernando et al. (2019), *SciBlock*, DOI
   `10.1109/CIC48465.2019.00019`.  Role: tamper-resistant, non-repudiable
   provenance and explicit invalidation of stale records.
4. The scientific-workflow provenance access-control framework, DOI
   `10.1109/TSC.2019.2921586`.  Role: evolving provenance policies should
   preserve consistency and completeness.

Project inference:

```text
prospective/static protection assertion
!=
retrospective evidence that protection was active
at the irreversible reservation boundary
```

These papers do not determine REI source bytes, GitHub ruleset IDs, attempt
count, toolchain hashes, native result, first interval, or provider status.

```text
authority_effect = NONE
```
