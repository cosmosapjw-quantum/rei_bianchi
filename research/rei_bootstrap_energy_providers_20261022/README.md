# REI bootstrap, scalar thermal ledger and through-Li providers

Runtime and local source access have recovered. The thermal supplied-moment ledger has independent PASS; restored conditional RR and new scalar DR evaluation have PASS_SCOPED_SCALAR_PROVIDERS. Bootstrap orchestration has PASS_SCOPED_BOOTSTRAP_ORCHESTRATION after its cumulative-budget repair and independent changed-path review. The reviewed payload is published at 61e08967832363b611a8e5ba4167ba7b06c06b6b; all three C10 stages are COMPLETE_SCOPED through the shared archive delivery in delivery/FINAL_DELIVERY_ACK.json. See LOOP_PROGRESS.json for R1–R10 and C1–C10 separately for each unit.

The existing 83 trajectories, their review/plots/backups, historical 29 JavaScript comparisons, and unchanged historical RR receipt are reused. They were not rerun. Full fresh83 is NOT_RUN. No new NCP allocation, run, budget reset or deadline reset occurred. This unit does not complete a coupled thermal/radiation/isotope/nuclear solver or alter production defaults.

Current evidence:

- Bootstrap: BOOTSTRAP_CONTRACT.md, bootstrap/BOOTSTRAP_REVIEW.json and budget-repair records. The 14-test suite covers the previous source; five affected tests cover the corrected source, with unchanged dependencies reused.
- Thermal: thermal/THERMAL_DERIVATION.md, THERMAL_CODE_CONTRACT.md, THERMAL_SCALAR_RESULT.json and THERMAL_REVIEW.json. Nine test methods, 44 numerical checks, 12 invalid rejections and six discrimination controls; no physical IVP.
- Providers: providers/PROVIDER_REVIEW.md and providers/code/CURRENT_IMPLEMENTATION_RECORD.json. RR historical evidence remains separately in IMPLEMENTATION_RECORD.json. DR has 27 direct Decimal comparisons and 771 representability cases; this validates fit evaluation, not physical fit accuracy.
- Recovery: EXECUTION_INTAKE_20261022.json and evidence/recovery/. Prior task-root recovery claims remain in evidence/recovery/history/.

Run from the repository root. These commands prepare/inspect sources or read the completed inventory; they do not launch fresh83:

```bash
TASK=research/rei_bootstrap_energy_providers_20261022
SOURCE=research/rei_isotope_quotient_pilot_20261022
WORKSPACE=/tmp/rei-bootstrap-source-only-20261022
PYTHONDONTWRITEBYTECODE=1 python3 "$TASK/bootstrap/bootstrap.py" prepare --source "$SOURCE" --workspace "$WORKSPACE"
PYTHONDONTWRITEBYTECODE=1 python3 "$TASK/bootstrap/bootstrap.py" plan --workspace "$WORKSPACE"
PYTHONDONTWRITEBYTECODE=1 python3 "$TASK/bootstrap/bootstrap.py" reuse-existing --source "$SOURCE"
```

Choose a new or empty workspace. Preparation copies immutable source/data/vendor/contracts, not saved results. Plan is inspection. Resume/fresh-reproduce can launch computations and require a separate execution decision; they are not part of this closeout. Completed saved inventories take the no-work path. Partial artifacts without cumulative usage history must stop before launching work; stateful missing-only recovery retains prior budgets and failed artifacts. Bootstrap limits remain 90 attempts, 2400 CPU seconds, 900 wall seconds, at most four workers (current engine serial).

The scientific source and saved results in the original isotope unit are unchanged; only three continuation metadata fields in its NEXT_DAG.json are updated. New source, raw execution logs and independent reviews remain distinct. The combined archive preserves the whole isotope unit (including saved83/results/summary), this task unit and AGENTS.md: 20,634,190 bytes, 380 members, 83 NPZ; SHA256 ec9f59ced42ebaac4cc2d6c2f1d0d5b1b963c9a9acbbec35015900bd4bbc2f75. Local CRC and all embedded hashes passed. Dropbox/Drive/Library acknowledged matching sizes. New remote full GET was NOT_RUN and remote metadata checksums were not exposed; prior full-download verification remains reused. The archive is the frozen pre-final-ACK snapshot, superseded by this later Git metadata ACK for delivery status.
