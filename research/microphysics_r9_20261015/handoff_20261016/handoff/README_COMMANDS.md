# C10 recovery commands

Run these commands **locally in the existing NCP environment**, from the directory containing `recover_c10.py`. Replace `YYYYMMDDTHHMMSSZ` with the current UTC timestamp and use a new output directory for each invocation.

```bash
python3 recover_c10.py --help
python3 recover_c10.py inspect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_INSPECT_YYYYMMDDTHHMMSSZ
python3 recover_c10.py collect --root /root/REI_MICROPHYSICS_R9_20261015 --out /root/REI_C10_COLLECTION_YYYYMMDDTHHMMSSZ
```

`inspect` reads original artifacts/processes and writes a new evidence directory. `collect` additionally copies observed target artifacts and parent deck/manifest if present, then re-inspects source identities and runtime state. Both create a sibling `.tar.gz` and `.archive.json` with its actual size/hash. They never start or stop a solver. Add `--extra-run-root /absolute/known/relocated/runs` for an independently known relocated attempt; a denied, missing explicit root or truncated search yields `unknown`.

The script uses Python 3.9+ standard library; NumPy is required for terminal NPZ validation. Use the existing NCP Python environment with NumPy, or `/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python` in place of `python3`. A missing NumPy installation blocks terminal acceptance without hiding the original receipt. Solver runtime dependencies are preserved in Unit2 `ncp_results/requirements.lock`: `h5py==3.16.0`, `mpmath==1.4.1`, `numpy==2.5.4`, `pyscf==2.14.0`, `scipy==1.18.1`, `setuptools==84.0.0`. Recovery does not install or import PySCF.

Read `inspection.json` and `STATUS.md`. Collector exit 0 means inspection/collection completed; the runtime may be `complete-fail`, `stale`, `missing`, or `in-progress`. Numerical acceptance requires `runtime_class=complete-success` plus `validation.passed=true`. Exit 2 means unavailable/conflicting/unstable inspection or a command/file error. Each receipt gate includes its measured value and pass/fail in `validation.json`; NPZ loading uses `allow_pickle=False`.

`complete-success` admits only the finite common-space Li→Be+ sudden ground projection and unresolved complement. Parent/daughter original-H residual and orbital metric are recorded solver gates; archive-only validation cannot recompute them without integrals. Basis convergence and all eight physical closure flags stay open. A failed worker can still leave driver `run` exit 0, so run exit alone is never a success criterion.

An active worker/supervisor, including one beyond 7200 seconds, remains in progress. Its NPZ files are not copied as terminal evidence. Partial `data.tmp.npz` from a stopped attempt is preserved as failure evidence; V6 has no iterative restart checkpoint. Duplicate terminal attempts produce `conflict` and are all retained. Source changes during copying yield `unknown`; original files, failures, and processes remain untouched.

There is no automatic launch/retry command. Actual failure or unrecoverable absence requires the separate Codex diagnosis and bounded new-attempt template in `C10_HANDOFF_CONTRACT.md`. A new manual attempt, if justified there, uses the existing `run` supervisor, one worker, 12 threads, 24 GiB, 7200 seconds, aggregate 48-thread/96-GiB caps and the original determinant/ERI/RSS/headroom guards. The NCP host is recorded as 64 CPUs and 125 GiB; inspect current available resources before any such decision. Never alter the independent PR150 owner campaign (head `fe789b0b13b1883c5a74cbc907f72f6f963a5d66`, deadline `2026-10-16T02:50:17.774070Z`).

The output archive is local evidence, not a durable publication receipt. `durable_storage` stays `not-published` until the controller records real provider/object acknowledgements for each destination. Complete Unit2 remains a separate required package. Historical Unit2 logs/source tests and its backups do not establish the current NCP target outcome.

## Local fixture verification

From the portable package parent containing `handoff/` and `unit2/`:

```bash
python3 -m unittest discover -s handoff/tests -v
```

Alternatively set `C10_PAYLOAD` to the complete restored NCP subtree containing `code/`, the V6 contract and `runs/threeelectron_v6/.../input.json`. The tests generate small synthetic CI/RDM archives with retained rank 64. They execute no Hamiltonian/solver calculation and make no NCP connection. `TEST_RECEIPT.json` records the actual local test/help/restored-snapshot command outcomes. Fixture success is implementation evidence, separate from scientific acceptance and NCP execution.
