# HE36-RMB: reactive pressure-moment bridge

**Workflow1.0.0 / approval0.2.** HE34 parent publication pin `fd11542ea8236e3c17eeb798bcafa8956e0eb248`; separate branch `research/he36-reactive-moment-bridge-20261023`, [draft PR89](https://github.com/cosmosapjw-quantum/BASS_HE/pull/89).

Common-bulk/common-T infinitesimal reactive incoming loss is implemented using three Maxwellian moments and one finite-mass2×2 block per STF component. A supplied net-event tensor is attached to the unchanged REI scalar event ledger with explicit energy/frame/thermal-inventory contracts. Actual CCC data supply finite-domain incoming moments; a129-temperature diagnostic and same-kernel batching measurement are saved.

Read [RESULTS_KO.md](RESULTS_KO.md), [theory/THEORY_KO.md](theory/THEORY_KO.md), [CONTRACT.json](CONTRACT.json), [EQUATION_CODE_MAP.md](EQUATION_CODE_MAP.md) and [SOURCES.md](SOURCES.md). Actual source, commands, failures, checks, outputs and plots are preserved under components/ and evidence/. [DAG.json](DAG.json) and [STAGE_LEDGER_KO.md](STAGE_LEDGER_KO.md) show every stage's actual backup/publication. [delivery/FINAL_ACK.json](delivery/FINAL_ACK.json) binds the final science pin and archive acknowledgement.

## Resume without replay

From this directory run:

```bash
python verify_saved.py --require-delivery
```

This reads hashes, saved rows and delivery records using the standard library. It performs zero model evaluations, tests, IVPs, benchmarks and renders. `SCIENCE_MANIFEST.json` pins immutable scientific payloads; moving delivery metadata and the self-referential manifest are outside that list. Their archive payload hashes and Git objects are recorded separately.

Public source interfaces are in `components/event_bridge` (NumPy required) and its byte-identical moment/pair modules. With this directory on Python's module search path:

```python
from components.event_bridge import attach_event_tensor, from_finite_evaluation, validate_source_lift
from components.event_bridge.reactive_moments import RawMoments, binary_loss
from components.event_bridge.maxwellian_moments import PreparedMaxwellianMoments
```

See [component API and manufactured examples](components/event_bridge/README_KO.md). Importing modules runs no research case. Do not bypass finite-source mapping or underflow guards by stripping provenance. Original test receipts are the default completion evidence; a named changed dependency is required for an affected new execution.

## Results and boundary

- Finite-mass incoming number/energy/STF formulas: independent exact algebra plus six Cartesian6D controls, max relative7.4623e-14 at gate2e-11.
- Moment verification:9 unique groups /10 group attempts, including one preserved failure and affected correction. Pair10/10; new bridge7/7.
- CCC diagnostic:129 unique T in2000–200000K, finite13.6058–968.61eV support, heavy fixed target. At20000K alpha_partial=2.7441444073979985e-18m³/s, kappa2/alpha=27.3178690016.
- Same-kernel batching: five pairs, median paired ratio6.02697×, range1.72796–10.88043×. This is a local batching measurement with preserved shared-host variability.
- New IVPs0; old donor IVP/suite replays0. One new diagnostic, one benchmark experiment, two render attempts / one final scientific PNG+SVG pair, two render cache-hit checks.

The physical gain tensor, isotope-matched differential processes, nuclear daughter charge/spectrum and stopping, fast-particle census, finite-anisotropy closure and coupled gas/metric evolution remain explicit dependencies. HE32 stays8nuclides21states prescribed-UV photo+caseA RR with gas pi_b=0; its matter stress is nonbaryonic. [GLOBAL_GOAL_DAG.json](GLOBAL_GOAL_DAG.json) keeps B1/B2 partial and B3→B4→B5 pending. [NEXT_DAG.json](NEXT_DAG.json) specifies the next source-qualified gain unit and wider dependencies.

Two resumable handoffs: [research thread](HANDOFF_CHAT_KO.md), [Codex/executor](HANDOFF_CODEX.md). Complete scientific code and data are Git-backed; external provider acknowledgements identify the separately saved archives. A successful archive upload is not described as an independent full restore unless that restore actually ran.
