# Restore and resume from the published unit

The C10 archive is a self-contained **focused verification payload**, including the 67 frozen source/input files, `build_focused.py`, selected coefficient rows, tests and evidence. It is not a full active-driver checkout. Publication/backup receipts outside the archive identify the final archive and actual cloud readback. A restore does not authorize scientific replay or replenish any old allocation.

## Existing Git checkout

Use the owner's existing `rei_bianchi` checkout. Inspect `git status`, HEAD and origin first; preserve dirty/untracked work. Fetch the integration branch without resetting, cleaning, checking out another branch, or creating a clone/worktree:

```sh
git fetch origin research/flrw-production-integration-20261015
rate_resume_ref=$(git rev-parse FETCH_HEAD)
git show "$rate_resume_ref:research/flrw_rate_table_acceleration_20261016/HANDOFF.json"
git show "$rate_resume_ref:research/flrw_rate_table_acceleration_20261016/NEXT_DAG.json"
```

Read the current final publication and backup receipt at that resolved immutable ref. Record the ref actually read. If the task files are absent or old locally, use `git show <immutable-ref>:<path>` to recover the task-owned documents into a temporary staging directory inside the existing workspace. Compare local owned paths before adopting updates; preserve unrelated and dirty files. All eight runtime/test files were source-matched at resume intake; a later branch advance must be classified by its actual diff instead of assuming it invalidates old numerical evidence.

## Existing workspace without Git metadata

Do not create a new clone. Obtain the same source archive using the owner's authenticated GitHub access (connector or existing `gh` session). Resolve the integration branch to one immutable commit, then download that **exact commit** archive. An example with existing GitHub CLI authentication is:

```sh
rate_resume_ref=$(gh api repos/cosmosapjw-quantum/rei_bianchi/commits/research/flrw-production-integration-20261015 --jq .sha)
gh api "repos/cosmosapjw-quantum/rei_bianchi/zipball/$rate_resume_ref" > /tmp/rei_rate_resume_source.zip
```

Extract the `research/flrw_rate_table_acceleration_20261016/` subtree into a temporary staging directory in the existing workspace, preserving its relative layout. Read its `HANDOFF.json`, `NEXT_DAG.json` and final publication/backup receipts before copying any task-owned updates. Do not extract over the owner's working tree indiscriminately. The source archive has one GitHub-generated outer directory; the unit paths are beneath it.

If restoring from the published C10 checkpoint ZIP instead, its entries start at `research/flrw_rate_table_acceleration_20261016/`. Extract into the existing workspace staging area with relative paths intact; no upstream source downloads are needed for the focused bundle. Use the exact provider object identified by final publication/backup receipts, not a similarly named older C07 file.

## Focused build instructions, only if later execution is explicitly needed

The completed numerical checks are reusable and should not be repeated just to resume. If a concrete changed-code risk requires a new authorized focused check, enter the recovered unit directory and run:

```sh
python3 build_focused.py --rustc /path/to/compatible/rustc --output /tmp/rei_rate_focused
/tmp/rei_rate_focused/rate_table_tests --test-threads=1 --nocapture
/tmp/rei_rate_focused/lithium_rates_tests --test-threads=1 --nocapture
```

These commands build the frozen focused sources. Rust 1.85.1 intentionally omits the unrelated `joint_affine` exports; this is not a full production-crate or current active-driver validation. The old raw outputs and ledger remain preserved, with any newly authorized run recorded separately under its actual budget.

## Selecting the next scientific task

After the current unit is closed, follow the root-admitted `NEXT_DAG.json`, selecting one exact source/receiver lineage before execution. Completed HHeD mixture EOS/CX derivations are reused. The PR193 receiver/guard path and RUN09 spectral-edge reference path are distinct; restoring this unit does not itself launch either path. Follow already authorized bounded research with matching dependencies/source and a valid budget; do not add a fresh permission gate for work already authorized. Keep expired historical native campaign allocations separate. Full Li photothermal/BBN-reservoir/LiBe nuclear and coupled 21-state work require their remaining source/closure dependencies. Preserve the existing NCP deadline, budget, observer and running/checkpoint state.
