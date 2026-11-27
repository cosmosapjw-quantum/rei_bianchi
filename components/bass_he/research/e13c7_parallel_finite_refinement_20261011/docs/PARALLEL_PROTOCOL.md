# E13C7 parallel execution protocol

## Bounded implementation contract

This module schedules already defined, independent OFF path enclosures. It does
not change an interval kernel, source row, stage, mask, weight, seam, numerical
resolution or precision. The frozen `WORK_PLAN.json` selects the work. The root
research owner supplies `off_path_worker.Context.run` and
`off_path_worker.validate_completed`; this protocol delegates scientific
admission to that validator and does not infer correctness from MPI completion.

The latest user instruction puts short calculations in ChatGPT and reserves the
64 CPU / 128 GB NCP machine for the finite batch. Production transport is Open
MPI, with one Python process and one thread per rank. Every rank computes paths.
No mpi4py, floating point rewrite, network service, package installation,
automatic retry, or fallback transport is part of this implementation. Local
transport exercises the same rank protocol on only the plan's local pilot set.
It does not establish that MPI has executed or that 64 CPU scaling was measured.

## Identity, scheduling and resources

The caller supplies the external SHA-256 of `EXECUTION_LOCK.json`. Before launch
and after collection the launcher verifies every locked file and the complete
scientific `SOURCE_LOCK.json` closure. All Python files under `code/`, both locks,
and the work plan must be covered. Each rank verifies the manifest, execution
lock and runtime Python bytes before it imports the scientific worker.

LPT scheduling orders tasks by descending, pinned estimated path cost and then
node number. It assigns each task to the rank with the smallest accumulated
cost, breaking ties by rank number. The manifest records every assignment and
cost. Pilot-derived `estimated_cost_seconds` is preferred; active species count
is an explicitly identified heuristic when no measured cost exists. Scheduling
changes neither path identity nor the final ascending-node collection order.

CPU affinity, visible cgroup v1/v2 CPU quotas, logical and physical topology,
host and cgroup memory availability, and inherited address-space limits are
observed before launch. Distinct allowed OS CPU IDs are assigned to ranks,
spreading over physical cores before sibling hardware threads where topology is
available. Rank count cannot exceed the requested plan cap, available CPU quota,
number of pending tasks or the memory budget. The memory calculation preserves
at least the plan's 20% reserve, includes a controller allowance, and uses the
per-process address-space cap, not an optimistic observed RSS. Actual RSS is
reported separately. A missing or incompatible Open MPI environment is an
explicit preflight failure; local transport is never selected automatically.
The actual NCP return showed root-level limit files absent while its CPU set was
visible. `/proc/self/cgroup` and `mountinfo` locate visible v1/v2 hierarchies and
ancestors. When limit files remain absent, the receipt says `UNOBSERVED` and uses
the observed affinity, host memory and declared resource caps. It does not infer
an unlimited quota or attest a 64 CPU allocation. A visible finite quota or
insufficient memory still reduces the permitted rank count or blocks launch.

## Durable execution and recovery

Each attempt uses a fresh output directory. Immutable files are installed with
create-only hard links after write and fsync, followed by a directory fsync.
Every rank has separate reservation, progress and receipt files. Each path has a
unique `paths/node_NNNNNN` directory. Successful worker output is revalidated
before a path is counted complete. Partial results and the first failure remain
in place. One rank failure terminates outstanding processes without retrying a
path. Timeout or an external interruption may leave an unresolved reservation;
the receipt distinguishes this from a validated completed kernel invocation.

An explicit `--resume-from PRIOR` may copy only validated, identity-matching
complete paths into the fresh attempt. The work identity, lock, node set, N and
precision must match. Retrying any prior incomplete or attempted path additionally
requires its explicit inclusion in `--retry-incomplete-nodes`. This is not an
automatic resume loop. Invalid completed evidence is a hard failure and is never
silently treated as missing work. A successful new attempt remains self-contained.

All expected paths must be present exactly once, validate, and belong to the
same work. A deterministic ascending-node index is written only after every
rank exits successfully and post-run lock verification succeeds. The separate
exact-Fraction reducer consumes `BATCH_COMPLETE.json`; collection itself does
not assert a global numerical or physical PASS. Physical, continuum, production
and receiver claims remain HOLD.

## Commands

```sh
python3 code/parallel_batch.py launch --package /absolute/package \
  --output-dir /absolute/fresh-run --execution-lock-sha256 EXTERNAL_HEX \
  --transport mpi --scope ncp --ranks 64

python3 code/parallel_batch.py launch --package /absolute/package \
  --output-dir /absolute/fresh-local-pilot --execution-lock-sha256 EXTERNAL_HEX \
  --transport local --scope local --nodes 105,106 --ranks 2
```

The Open MPI launcher is checked by its actual executable, SHA and version
output. A single-host hostfile fixes the approved number of slots, with
oversubscription disabled and OS CPU affinity pinned inside each rank. The
launcher does not add a root override by default. A
deployment on the user's authorized compute host may explicitly pass
`--allow-openmpi-root` when its actual effective uid is 0. The option is recorded
in the manifest/receipt and passed as Open MPI's documented
`--allow-run-as-root` argument. It is rejected for a nonroot uid or local
transport. No global environment variable is mutated to select this override.

Primary command reference: Open MPI 4.1 `mpirun(1)`,
https://www.open-mpi.org/doc/v4.1/man1/mpirun.1.php , and Open MPI 5.0.10
`mpirun / mpiexec`,
https://docs.open-mpi.org/en/v5.0.10/man-openmpi/man1/mpirun.1.html . These specify
hostfiles/slots, no-oversubscription, and `--bind-to none`. Runtime compatibility
on the NCP machine remains to be observed there.

## Verification scope

Protocol tests use an explicitly identified synthetic worker in isolated test
packages. They exercise completion, deterministic partition/collection,
failure preservation, tamper rejection, local-only scope, resource caps,
identity-bound resume and explicit incomplete-path retries. They make zero
scientific kernel calls. Any actual short-path calculation and its scientific
review are recorded separately by the research owner. An eligible independent
reviewer, not this protocol's author, makes the final acceptance decision.
