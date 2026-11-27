# E13C7 implementation choices and source precedence

## MPI computing rank count

The independent theory contribution is an advisory design analysis, not the
execution manifest. Its suggestion of a rank0 dynamic controller with63workers
was considered. The owner selected deterministic cost-weighted static LPT shards
and an external standard-library launcher. Every MPI rank computes. Thus64MPI
ranks means64computing workers in the delivered execution contract. The external
launcher performs lightweight progress collection and post-run checks; it is not
an additional scientific worker or an MPI rank.

The actual repository HPC policy requires independent task distribution with
OpenMPI and requires reporting N−1workers when a rank0-controller arrangement is
used. It does not require that controller arrangement. The adopted design satisfies
the task-parallel requirement and avoids reserving an idle scientific rank. LPT
uses measured per-mask path costs and spreads the expensive three-species paths.
The local four-process rank protocol is an implementation test, not an MPI
performance measurement. There is no MPI backend fallback in the NCP command.

The normative order is current user instruction, source scientific definitions,
RESEARCH_CONTRACT/SCIENTIFIC_CONTRACT, sealed WORK_PLAN, then EXECUTION_LOCK and
the exact delivered code. Advisory theory reports retain their original proposals
as evidence and must not override the actual sealed launcher design.

## Validated arithmetic and the native-HPC policy

This change distributes unchanged directed-Decimal reference kernels. It does not
replace them with binary64 arithmetic. A native certificate implementation would
need its own directed-rounding and inclusion proof; a Fortran real64 rewrite is
not an accuracy-preserving shortcut for this node. The relevant policy is applied
to independent tasks, explicit backends, thread limits, actual host limits,
deterministic reduction and measurements. Future native numerical development is
separate from the present fixed-kernel enclosure batch.

## No short replay in the next NCP task

Two actual E13C6 returns have been verified. The 64-affinity recorded host used
one scientific CPU and48.764258135s for four N512 HI paths. The existing replay
is consumed. Its measured time may anchor a clearly labelled workload estimate;
it must not be repeated merely to benchmark the new scheduler. Short source,
precision, event and refinement controls run here. On NCP only host-specific
preflight and durable return packaging surround the heavy new2331-path batch.
The global exact Fraction reduction and final scientific admission are performed
here after the NCP archive returns.

## Missing cgroup limit files

The latest recorded NCP environment did not expose root `cpu.max` or
`memory.max/current` files. Absence is not proof of an incompatible host, and
must not be reported as an observed unlimited quota. The launcher must record
which hierarchy and limits are visible, use actual affinity and available memory,
apply every observed tighter limit, and distinguish an unobserved quota from a
measured64-CPU allowance. A64-affinity machine is not provider attestation.

## Capture events

Small threshold discrepancies in binary64-realified event endpoints do not license
reselection of captured source/mask. The current scope is the inherited fixed
capture. The eight local pilots include the two remaining events explicitly.
The heavy ordinary-path set separately passes strict whole-branch checks.
