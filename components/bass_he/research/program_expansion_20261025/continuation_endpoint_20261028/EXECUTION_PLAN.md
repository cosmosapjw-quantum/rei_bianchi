# ENDPOINT14 bounded commands and stopping rule

Do not execute science, tests, Wolfram or plots before root GO after actual S05 source pin publication. No automatic retries. Preserve a failed output directory, logs and FINISH. A single diagnosed repair is root-authorized only and consumes remaining cumulative CPU/wall allocation.

Primary command, from workspace root /workspace/scratch/980916233f52, after GO (the completed execution used absolute paths):

```sh
python work/BASS_HE/research/program_expansion_20261025/continuation_endpoint_20261028/scripts/run_once.py --mode validation --saved work/BASS_HE/research/program_expansion_20261025/continuation_quartic_20261028/evidence/validation/initial/SAVED_PLOT_DATA.json --official work/BASS_HE/official_source/M0475.x4 --output work/BASS_HE/research/program_expansion_20261025/continuation_endpoint_20261028/evidence/validation/initial
```

Whole runner plus waited children cap: CPU120s/wall300s, AS768MiB, thread1. The source mechanism is inherited unchanged from repaired T13. Validate actual code/input compatibility with U/evidence/EXECUTION_PIN.json. Source file hashes are recorded at START and in the saved certificate. Candidate outcome is saved before polytope construction. Primary output is SAVED_PLOT_DATA.json, TEST_REPORT.json, READER_REPORT.json, CANDIDATE_OUTCOME.json, START/FINISH, logs, MONITOR_IDENTITY and RESOURCE_RESULT. A successful command is implementation evidence; admission remains pending root independent review.

Saved-only plot command after root accepts primary outcomes:

```sh
python work/BASS_HE/research/program_expansion_20261025/continuation_endpoint_20261028/scripts/run_once.py --mode plot --saved work/BASS_HE/research/program_expansion_20261025/continuation_endpoint_20261028/evidence/validation/initial/SAVED_PLOT_DATA.json --output work/BASS_HE/research/program_expansion_20261025/continuation_endpoint_20261028/evidence/plot/initial
```

WholeCPU10s/wall30s, AS768MiB, thread1. Inspect the actual PNG and preserve SVG. The plotter converts stored exact values for display; it cannot import the producer or recompute scientific values. One successful rendering only.

Root owns the one Wolfram evaluator, remote resource disclosure, actual stage publication and dual backup receipts. New operational records use operations14/publication14/checkpoints14/delivery_authorities14/final_delivery14. Earlier unit paths and results remain unchanged. Fixed model resolutions are exactly 1,4,16; actual remaining gaps are reported and never trigger an extra mesh.
