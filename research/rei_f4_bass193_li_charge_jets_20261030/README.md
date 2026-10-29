# REI physical fast F4: BASS193 Li6 source-jet observability

Scoped physical-data/theory/code research, no new IVP, no source modifications, no REI↔BASS forward-model identity claim. Source files live under `source/` (including exact-byte original PR275 and PR121 masters, original 193 trajectory, native BASS network + model + numeric projection). See `THEORY_KO.md`, `REPORT_KO.md`, `RESULT.json` and `HANDOFF_NEXT_THREAD_KO.md`.

After extracting archive run `bash VERIFY.sh`. This only replays 193 saved *static* source evaluations, all source checks, targeted Python tests and MP80 determinant arithmetic. It does not integrate the time-dependent chemical system.

Original REI DAG working 33/88; central 28/88; physical fast 4/7. R6/C9 different author not run. Preserve NO_MORE_IVPs, NO_MERGE, NO_FORCE_PUSH.
