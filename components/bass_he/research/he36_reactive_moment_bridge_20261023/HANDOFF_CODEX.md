# HE36 Codex / executor handoff

## Goal, source and execution state

Consume the delivered HE36-RMB revision. Workflow1.0.0 / approval0.2. The branch is `research/he36-reactive-moment-bridge-20261023`, draft PR89 in `cosmosapjw-quantum/BASS_HE`; final immutable science pin and archive identities are in `delivery/FINAL_ACK.json`. The final metadata commit is the commit containing that ACK. Do not infer that the transient author's local detached Git HEAD equals the published branch head; inspect the intended remote pin in an isolated checkout.

Current task for an executor is saved-payload verification. All planned bounded scientific checks are completed. No heavy job, cosmological IVP, old test replay or new benchmark is pending. Substantive changed-science design remains with the research thread; apply only a minimal environment or boundary fix when required, preserve its evidence, and return scientific assumption/tolerance/provider changes to that thread.

## Restore and read-only command

Retrieve the exact pinned Git unit. If working from the archive, verify its SHA256 before extracting into an empty directory; keep its `research/he36_reactive_moment_bridge_20261023` hierarchy. Overlay only newer Git delivery metadata at the supplied publication pin. Do not overwrite unrelated live work or existing attempts. The final archive's payload manifest binds the actual archived bytes; the manifest excludes its own file and ACKs that only exist after upload.

From the unit directory:

```bash
python verify_saved.py --require-delivery
```

Expected result: `REUSED_COMPLETE_VERIFIED_PAYLOAD`,20 completed stages,20 delivered stages,20 stage ACKs and129 saved CCC rows; all science payload SHA256/byte counts match. The command uses the Python standard library and performs zero model evaluations, scientific tests, IVPs, benchmarks or renders. Send back command/environment, stdout/stderr, exit status, exact archive/pin identity and any missing/hash-mismatched path. Do not regenerate a missing scientific output before checking Git and the archive.

## Runtime and interfaces

Runtime witness: Python3.12.14, NumPy2.3.5, Linux x86_64. SciPy and mpmath were used only for the existing independent reference checks; Matplotlib only for the saved plot. Exact versions/environment and measured host limits are in component receipts. Public computation modules require NumPy and use binary64, no fast-math. Imports are portable and execute no case:

```python
from components.event_bridge import attach_event_tensor, from_finite_evaluation, validate_source_lift
from components.event_bridge.reactive_moments import RawMoments, binary_loss
from components.event_bridge.maxwellian_moments import PreparedMaxwellianMoments
```

Required units: event tensor J/event, S and J Pa/s, Q W/m³, R_n m^-3s^-1, alpha m³/s, beta Jm³/s, gamma J²m³/s, common T in K, masses kg. Required tensor frame: common bulk central. Current event adapter requires charge-neutral21-state census without positrons/negative ions and all retained nuclei/free electrons thermal; nonzero dEfast is unresolved here. A fast population needs its own number source. Q and donor dEth are one energy owner. RawMoments are incoming-loss input; a supplied net event tensor includes gain and removal.

## Changed-dependency execution only

Name the changed code/input/assumption and original gate before running an affected check. Preserve its old receipt and create a fresh output folder; never overwrite a completed attempt. Exact original commands and code hashes are retained in component receipts. Portable bridge check command for a genuinely changed bridge is:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python components/event_bridge/check_bridge.py --output /tmp/he36_changed_bridge_attempt
```

The affected moment check accepts explicit `--table`, `--output` and `--groups`; choose only affected groups. The preserved independent Cartesian script contains its original absolute target `/tmp/he36_pair_implementation/reactive_moments.py`: restore the intended target bytes in an isolated path or make and record a path-only wrapper before a changed-source run. Its existing completed receipt remains valid for the unchanged module. Do not rerun it merely to move files.

Current diagnostic/render runners reuse complete identity-matched outputs, but saved verification above is the default. Actual initial costs: pair groups0.0372s after imports; six Cartesian controls0.1609s; bridge7groups0.3231s; diagnostic+benchmark body0.3488s. They are bounded local costs, not whole-session or future-domain predictions. No external heavy execution is required by this handoff.

## Return contract and next science node

Return a fresh receipt containing source/input hashes, command, environment/thread settings, UTC start/end, wall/CPU/RSS where measured, stdout/stderr, exit code, outputs/hash manifest, fixed acceptance gates and actual new execution counts. Preserve failures and classify theory/numerics/implementation/environment/input dependency. A passing structure/hash check is packaging evidence, not new scientific validation.

Next science is `NEXT_DAG.json`: N0 delta intake and N1 qualified differential H1 gain source. Nuclear daughters/stopping, thermal/UV evolution, physical pair transport and finite-anisotropy closure are explicit other dependencies. New gas IVP N8 requires those selected-domain dependencies first. HE32–HE35 and donor completed IVPs/tests are evidence to reuse, including the394 HE32 trajectories; they are not scheduled work.

## Final delivery identifiers

- Immutable science commit: `b2336709b9a07dd1db0a7cc9da381c59c8dd6470`
- Science tree: `6444bbec7a96cbc3496f46655ff72610a7fbceae`
- Final HE36 archive: `BASS_HE_HE36_RMB_FINAL_20261022T225602Z.tar.gz`
- Archive SHA256: `b754afd41dffe916f4b7b13f080089a7021a3ad1fae0ca6f7a3dbd4c7dab3874`
- Dropbox ID: `id:BSpOijBcT10AAAAAAD_swQ`
- Archive bytes: 842860; 186 payloads plus the payload manifest;116 immutable scientific files.
- All20 stage commits and separate archive ACKs are complete. The latest publication pin is the Git commit containing delivery/FINAL_ACK.json; it adds post-upload metadata to the science commit. The final chat handoff also supplies that exact publication pin.
- Local tar member hashes and all116 published scientific Git blob identities were checked. The provider acknowledged the same archive byte count; no remote re-download restore is claimed.
