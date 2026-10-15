# C10 executable handoff contract

This unit recovers the terminal state of one already submitted NCP calculation and packages the evidence needed for the next decision. Its scope ends at recovery, finite-model validation, durable publication, and readiness of the eight subsequent tasks. It adds no Hamiltonian, basis, solver, physical claim, or owner-campaign action.

## Frozen identities

- Unit2 raw archive SHA256: `725cf8bf53d366b179d41708c4efc9477b29c6c6e0a748ac2d3585dbe33709a1`.
- PR151 intake head: `57e6e2d79c1a1ea4786d83b36c871abf581be738` (session intake; historical archive references remain historical).
- Independent PR150 owner head: `fe789b0b13b1883c5a74cbc907f72f6f963a5d66`; full005 deadline `2026-10-16T02:50:17.774070Z`. Never restart, stop, modify, or repurpose this campaign.
- NCP root: `/root/REI_MICROPHYSICS_R9_20261015`.
- Case: `quench_Li_Be_union_aug_TZ_occ_list_v6`; canonical run: `runs/threeelectron_v6/quench_Li_Be_union_aug_TZ_occ_list_v6`.
- Driver `code/microphysics_driver_v6.py`: SHA256 `31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c`.
- Contract `CONTRACT_MICROPHYSICS_V6_THREEE.json`: SHA256 `cf7b06ad72815513e799be253539bdfecfb9102c1fc586589003e8b6fd364e4d`.
- Saved `input.json` bytes: SHA256 `289520d8aed460cdee460f5497762b0c613f003bd6ba43bb505416d945995097`.

Input is all-electron nonrelativistic point-nucleus Li(0) to Be(+1), three electrons `(2,1)`, spin 1, `aug-cc-pvtz` union of Li and Be AOs, the shared canonical AO overlap map, default relative cutoff `1e-10`, original-H residual gate, and occupation-list/RDM-spin V6 backend. Keep these inputs and all earlier failure attempts immutable. The source default FCI tolerance is `1e-11`, residual solver tolerance `5e-8`; final original-H acceptance is `1e-7 Eh`.

## Evidence at handoff

Restored Unit2 has target `input.json`, `launch.json`, `stdout.log`, `stderr.log`, and `case_deck.json`; it has no target final receipt or data archive. It records a running snapshot near 15:00 UTC on 2026-10-15 and a prior observation near 14:56 UTC. Those are historical observations. The current target runtime and scientific outcome are UNKNOWN until actual NCP inspection. The collector failure at 15:24 and later Unit2 publication at 15:48 establish a collection-order problem, not a solver result. Unit2 backup verification is distinct from the missing terminal evidence.

The archived `threeelectron_backend_test.log` records the real small Li/Be union comparison passing (17.768 s). Reuse it when source/input/runtime identities match. Test acceptance was energy difference <= `1e-9 Eh`, projection difference <= `1e-8`, spin difference <= `1e-6`; this does not replace inspection of the full aug-TZ run.

## Required portable package

Package the complete verified Unit2 archive or its complete restored tree, not only an instructions file. Preserve all `code/`, contracts, tests, review, results, bridge inputs, raw runs including failures, logs, reports, lockfile, saved target launch/input/deck. At minimum the self-contained execution subtree must have V6 source, V6 JSON/MD and inherited V2/V3/V4/base contracts, exact saved input/launch/deck, `requirements.lock`, occupied-list test and historical log. Include this contract, a SHA256 manifest, `recover_c10.py`, meaningful fixture tests for its state classification/receipt gates, and a concrete NCP Codex prompt. Ship any required next-task source/intake/review records with the archive rather than relying on chat history.

Implement `recover_c10.py` with Python standard-library inspection/collection and NumPy only for NPZ validation. No credentials embedded; existing authenticated storage context may be reused. No remote session is created by this contract. Primary interface:

```text
python3 recover_c10.py inspect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_RECOVERY_<UTC>
python3 recover_c10.py collect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_RECOVERY_<UTC>
```

`inspect` is read-only with respect to all original files and processes; it writes a new timestamped evidence directory only. `collect` copies the observed evidence without modifying it and rechecks identities. Do not copy a changing NPZ as a terminal result. Detect a source mutation during copy by stat/hash before and after; record the instability and defer acceptance.

### Actual process and artifact inspection

1. Verify root/source/contract/input hashes, save UTC, host, Python/package versions, kernel boot ID, and process snapshot. Inspect `/proc` command lines and cwd against exact driver, input path and output path. Record PID, start ticks, elapsed time and state for matched workers/supervisors. Exclude the inspector itself; a process name match or stale PID alone is insufficient. Read failure/permission errors as unavailable evidence, not absence.
2. Read the canonical run and search bounded project run directories for the exact case ID/input identity and corresponding final receipts, partial `data.tmp.npz`, data, launch logs and manifests. If duplicate/conflicting terminal attempts exist, retain every attempt and mark conflict; no automatic choice or rerun. Allow explicit extra run roots for independently known relocated attempts.
3. Classify once from current evidence using the table below. A final receipt written by a worker while its supervisor still runs remains in progress until the matching process exits and files stabilize. Receipt success requires the validation below. A broken/missing claimed data file is a failed recovery/validation, not evidence to replay the solver.
4. Write `inspection.json` and concise `STATUS.md` with separate `runtime_class`, `claim_verdict`, `validation`, and `durable_storage`. Always record exact observed paths, hashes and reason. A disconnected/denied inspection yields `runtime_class=unknown`, blocked inspection and no launch.

| Runtime class | Required evidence | Action |
|---|---|---|
| `complete-success` | No live matched attempt; stable identity-matched final receipt and data pass all gates | Copy exact evidence, record finite-model acceptance, publish result archive |
| `complete-fail` | No live matched attempt; failed/deferred/worker-failed terminal receipt, or invalid final receipt/data/gates | Preserve original receipt/data/logs, record error class and next diagnostic; no replay |
| `in-progress` | A matched active worker/supervisor exists; no contradictory terminal instance | Record current process/resources/artifact snapshot and return; no second launch or termination |
| `stale` | No active matched process, no terminal receipt, but original attempted-run evidence or partial output remains | Preserve evidence; classify missing terminal record; diagnose once, no blind replay |
| `missing` | Actual root search finds no target attempt artifacts, no matching process and no terminal receipt | Record absence and historical launch evidence; recovery first; missing alone does not authorize rerun |

A live process beyond 7200 s is still observed in progress with a wall-supervisor anomaly, not permission to kill it. Unavailable roots/processes must be recorded as inspection gaps. This target is known to have been launched, so absence today cannot by itself establish its outcome. Diagnose the actual missing evidence before selecting a new reconstruction attempt.

### Terminal acceptance

Verify receipt case equals the frozen parsed input (including threads 12, memory 24.0, contract ID/hash); verify input byte hash separately. Receipt `case_sha256` uses `json.dumps(case, sort_keys=True)` hashing and is distinct from launch `case_sha256`, which is the input-file byte hash. Verify receipt runtime source SHA, source file SHA, contract SHA, data SHA, final status `finite_model_computed`, exit code 0, and top-level plus recursive parent/daughter `finite_model_numerics_passed=true`. Top-level driver `run` exit 0 alone is insufficient: it also returns 0 for failed workers.

For both parent/daughter require finite measured energies, `(2,1)`, actual retained rank >=64, common dimensions, backend `unpenalized_direct_spin1_occupied_list_capable_RDM_spin`, norm error <=`1e-10`, orthogonality infinity norm <=`1e-8`, RDM trace error <=`1e-8`, spin error <=`1e-6`, original-H residual <=`1e-7 Eh`, and `fci_converged=true`. Record numerical values and pass/fail per gate, not only booleans.

Load NPZ with `allow_pickle=False`. Require finite arrays `CI_parent`, `CI_daughter_ground`, `CI_complement`, `common_orbital_matrix`, `AO_overlap_eigenvalues`, `rdm1_parent`, `rdm1_daughter`. For retained n, CI shape is `(n*(n-1)/2,n)`; common X shape is `(ao_rank,n)`, AO eigenvalue count is ao_rank, each RDM is `(n,n)`. Independently recompute parent/daughter norms, RDM traces=3, A=<Cf,Ci>, P=|A|², q=Ci-A Cf, and q identity/closure/orthogonality to tolerances `1e-10` (RDM trace `1e-8`). Confirm receipt projection/complement values agree. P and complement must lie within `[0,1]` to the closure tolerance. Record daughter moments/variance as diagnostics and check finiteness; no new energy-moment acceptance tolerance is invented. Original-H residual and orbital metric are recorded solver gates, not independently recomputed by an archive-only check lacking integrals.

Final classification acceptance is finite common-space Li→Be+ sudden ground-state projection and unresolved complement. Basis convergence, exclusive continuum probability, electron capture, recoil/phase-space decay distribution, isotope corrections and all eight physical closure flags remain open. Failed spin or numerical gates are solver/numerical failures, not physical no-go results.

## Checkpoint, limits and subsequent bounded attempt

V6 saves final data/receipt but no iterative restart checkpoint. `data.tmp.npz` is evidence, not a restart state. Never claim resume of its Davidson iteration. Save inspection, original attempt files and every failure before any changed attempt. A diagnosed numerical/backend/environment failure can proceed to the next user-authorized constructive bounded repair, with a new contract/attempt identity, exact changed dependency and targeted verification. Preserve the original failure and keep the owner campaign untouched. This C10 script does not itself invent that repair or automatically replay the failed case.

The executable C10 script exposes `inspect` and `collect` only. There is no `launch-missing` subcommand and no unsupported affirmative-never-completed proof requirement. Recovery results feed Codex's next concrete decision under the user's existing continue authorization.

If actual inspection diagnoses a failed calculation or missing/unrecoverable artifacts, Codex may write a new bounded repair/reconstruction identity describing the observed evidence, changed dependency or reason reconstruction is required, input/source identities, original acceptance gates and one-attempt resource budget. Preserve all original attempts. An accepted complete result is collected rather than replayed; an active run is observed rather than duplicated. A repeated same-state failure is diagnosed before another execution. No further blanket permission step is introduced.

The following is a manual supervised **new-attempt template**, to be instantiated by Codex only after that diagnosis and bounded identity are written. It is not an automatic C10 action. Use a new attempt ID via `--label`, a never-existing output root, and the chosen frozen repair/reconstruction contract/source. For reconstruction with unchanged science the saved V6 source/contract shown here are reused; any numerical repair substitutes its explicitly versioned source/contract paths. Recheck matching processes and available resources immediately before launch and hold a local exclusive case lock to avoid concurrent duplicates.

```text
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python /root/REI_MICROPHYSICS_R9_20261015/code/microphysics_driver_v6.py run --contract /root/REI_MICROPHYSICS_R9_20261015/CONTRACT_MICROPHYSICS_V6_THREEE.json --out <never-existing-new-attempt-out> --label <new-bounded-attempt-id> --threads 12 --memory-gib 24 --workers 1 --cpu-cap 48 --memory-cap-gib 96 --wall-s 7200 --family-wall-s 7200 --only quench_Li_Be_union_aug_TZ_occ_list_v6
```

Set `OMP_NUM_THREADS=12`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`. The same driver then generates the exact case input and supervises wall/RSS/host headroom. Preserve its original 10-million determinant, ERI/RSS prediction guards, 24 GiB address-space limit, 20 GiB host-headroom guard and aggregate 48-thread/96-GiB caps. Check available resources against other host work including the untouched owner campaign; these are upper bounds, not reserved capacity. Record actual wall/RSS/command/exit and run the same terminal inspection after exit. The bounded identity permits one supervised attempt; a further attempt requires a concrete new diagnosis or changed dependency, not an automatic retry loop.

## Return and publication acceptance

Return an evidence directory containing `inspection.json`, `STATUS.md`, process snapshot, runtime/dependency identity, copied original target artifacts and parent manifest if present, `validation.json`, SHA256 manifest, collector command/stdout/stderr/exit, and a compressed Unit3 recovery archive. Include complete failure evidence as readily as successful arrays. For in-progress status, clearly label the collection a nonterminal snapshot. Build no success receipt on behalf of the solver.

Durable publication is complete only when the final archive bytes and size/checksum are tied to actual provider acknowledgements/object IDs (or committed repository identities for source). Preserve the complete Unit2 package and publish the additional recovery unit; neither an instruction file nor an upload plan substitutes for those files. Record each destination independently; retain the second-destination failure if only one succeeds. Source review/implementation completion, runtime completion, numerical acceptance and durable save are separate fields.

## Eight-task readiness DAG

This table freezes only the next dependency handoff. The current work does not execute the eight tasks or call them physically closed.

| ID | Existing reusable input | Next physical work / dependencies | Readiness |
|---|---|---|---|
| T1 Li bound | Core DZ/TZ/QZ CI/RDM/ionization series | Basis-error convergence; finite-mass and relativistic terms at requested accuracy | Existing finite-model data ready; physical target open |
| T2 Li continuum | T1 states, projected response/moments | Energy-normalized outgoing Coulomb/exchange channels, thresholds and exclusive cross sections; depends T1 | Boundary/provider construction needed |
| T3 molecular low-T | LiH/LiHe counterpoise curves/dipoles | Long-range/basis convergence, ionic/excited channel couplings, nuclear scattering/radiative association | Curves ready; rate calculation needed |
| T4 daughters | 2e and DZ/aug-DZ 3e projections; recovered V6 result if accepted | Resolve excited/continuum daughters and recoil/phase space; separate EC annihilation/contact operator; depends T1/T2 where used | V6 receipt recovery first; physical closure open |
| T5 nuclear precision | Native np kernel, calibration sensitivity/quadrature evidence | Joint likelihood/covariance and truncation uncertainties | Kernel ready; inference inputs needed |
| T6 charge cascades | E1 line tables and mixture/residual ledger | State-resolved injection, 2s two-photon and collisional/charge channels; depends T1/T2 and T4 where relevant | E1 tables ready; injection/provider work needed |
| T7 BBN→17 | Conservative donor inventory/residual and conditional charge map | Be7 conversion and charge-history evolution; shared electrons/EOS; depends T4/T5/T6 as used | Inventory ready; coupled evolution needed |
| T8 transport | Conditional source moments, existing provider interfaces | Couple accepted providers/network and radiation; actual cosmological refinement; depends T1–T7 as required | PR150 owner campaign continues independently; new integration is separate |

The next decision consumes actual recovered receipt/data and this DAG; it selects one newly defined physical calculation only after C10 completion. It does not restart the independent owner campaign or run every task by default.
