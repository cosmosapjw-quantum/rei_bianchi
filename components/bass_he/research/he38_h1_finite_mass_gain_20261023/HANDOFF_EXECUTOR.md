# HE38 executor / restoration handoff

Workflow1.0.0 / approval0.2.

repo: cosmosapjw-quantum/BASS_HE
branch: research/he38-h1-finite-mass-gain-20261023
PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/91
unit: research/he38_h1_finite_mass_gain_20261023
science pin: 2ce8afd80b7baf430c85ce5ace81a5bd4e9465c0
original C10 acceptance pin: 6790005d5a0b7b0dceedeedd4f3687b94202ed54
science manifest SHA256: 3f007ee7b98ca38ce30968fe6eb9dbd984319186bbd6166c5a021d05ee657ae3
final archive: BASS_HE_HE38_FMG_FINAL_20261023T072909Z.tar.gz
archive SHA256: c0ea401136c8f39df6dfa07e7a2acd6c7cd054d81251c0dd996aaaf5a27e90a0
Dropbox ID: id:BSpOijBcT10AAAAAAD_0pA

Resolve the latest publication through PR91 and the external final Git readback. Restore from the fixed publication and archive, verify archive SHA256 before extraction, and preserve unrelated work.
Read README.md, RESULTS_KO.md, DAG.json, NEXT_DAG.json, RUN_RECORD.json, SCIENCE_MANIFEST.json and delivery/RESUME_KO.md.

Run only the standard-library saved-evidence verifier for restoration:

```bash
python research/he38_h1_finite_mass_gain_20261023/verify_saved.py --require-delivery
```

When all20 HE38 stage archives and the final archive are locally present, add --archives --archive-root /actual/archive/directory. This checks bytes and recorded receipts; it launches no scientific model, IVP, benchmark or render.

Scientific STF consumers use wrapper.J or species.total_J_Pa_s. Nested event_tensor_source.J is a legacy trace-projection audit. Do not promote it to the scientific direct-STF interface.
The portable independent oracle entry evidence/raw_controls/portable/launch.py accepts explicit --implementation-root, --output-root, --attempt and refuses existing attempts. Its portable wrapper is PREPARED_NOT_SCIENCE_EXECUTED. Use it only for a newly justified affected validation after a changed dependency. The original executed oracle and diagnostics remain complete and must not be replayed for restoration.

Executor work is restoration, execution of a specifically authored new plan, and minimal evidenced execution-boundary fixes. Substantive physics and implementation design return to the ChatGPT research author. Preserve masses, energy/frame conventions, census, all original attempts and failures. Record actual command, exit, time, RSS and input/output identities.
Current HE38 source is model-conditional; angular calibration, unequal temperatures/drifts, total-gas closure and coupled IVPs remain gated in NEXT_DAG. Do not merge or claim production completion from saved evidence alone.
