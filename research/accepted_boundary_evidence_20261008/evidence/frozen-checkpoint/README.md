# Actual frozen continuous receiver: durable k3→k4 continuation

The selected actual caller is `vendor/frozen-panel-fixed-j32-final-interval-v1/src/continuation_driver.rs::run`, with its existing `load_checkpoint3`, `step`, `physics::Frame::replay` and `stock_density_control`. This isolated derivative adds an explicit disk checkpoint seam to **that caller**. Its original `step` and scientific gates, physics, source, stock rule, N/M inverse, canonical thirteen-owner ordering and original coefficient/provenance loss ledger are unchanged byte-for-byte. No hot monoenergetic substitute is used. The exact source/data identities and changed/new file hashes are in `evidence/IMMUTABILITY_AND_SOURCE_PROOF.json`, `BUILD_IDENTITY.json`, `BASE_PINS.json` and `ACTUAL_CALLER_CHANGE.patch`.

Source provenance is the accepted fixed-J32 frozen-panel archive SHA256 `dfd1e2642243d87b922c219cad990ef57fa4eaf376b0c5fd859a2c2cb6667adb` plus optimization compact SHA256 `fbeca7f433637e2a638185190f356c1d213d51d3302ffb99b4336dd190324d28`. The optimized caller/lib/worker source copies were verified against the compact local intake. The accepted native solver/physics, config, oracle and k3 panel/increment/charge assets are copied read-only as dependencies from task-3; every original remains unchanged. The previous live receiver package `5a46b8b676d8dba9957cecbaa900895e47df401437e09ced2374cf7472f74694` remains immutable. No dirty checkout was modified. MODEL_UNRESOLVED; the previously read code-work skill and physmath router apply without selecting an unsupported harness. No applicable AGENTS.md was found.

## Supported scientific boundary and precise BE blocker

The actual fixture is cold: frozen gas fractions[2e-4,0,0] at30K;13.7–100eV broadband source1e-15photons/H/s; original manufactured background; absolute ln(a) lattice17epochs with base width.0002 and all original transformed source/species edges. The receiver preserves its fixed-m1 midpoint-staged characteristic integrator and original physical source `q_s = C / [(1/Emin−1/Emax) E H]`. Stored canonical panels carry Wide N/M, closure beta, the original frontier tag, provenance and incoming-loss metadata. Original named owner order is N,U,QN,QE,red,outN,outE,A_HI,A_HeI,A_HeII,B_HI,B_HeI,B_HeII; only the existing eleven flow owners accumulate.

The previous point/BE receiver cannot consume this state while keeping its solver/assumptions unchanged:

| Contract | Canonical frozen receiver | Point/BE path | Result |
|---|---|---|---|
| Material | Identical frozen cold gas throughout | Evolves coupled gas/thermal state | Different physical closure |
| Clock/staging | Absolute ln(a), midpoint, source/cutoff/wake cuts, redshifted characteristic E | Frozen proper-time context with full/two-half BE trials | Different temporal operator |
| Propagation | Existing exponential characteristic segment with continuous source and redshift owners | Rational BE update of discrete photon counts | Not the same semigroup; exp(−λh) differs from1/(1+λh) for nonzeroλh |
| Spectrum/lineage | Continuous closure N/M+beta+front+provenance and persistent mesh | Finite SourceState photon vector | No lossless spectrum/lineage representation |
| Owners/loss | Canonical13/retained11 and original occurrence/coefficient/history ledger | Native six-species A/B diagnostics | Insufficient to synthesize the canonical physical request |

`REI_NATIVE_BE_HANDOFF=1` now refuses explicitly **inside the actual caller before Frame/science work**. It does not replace the midpoint integrator, invent proper-time inversion, compress panels into a hot node, or infer physical increments. The prior supplied LeftFront y·exp(beta·y) restriction/wake control is not reinterpreted as the canonical bool frontier tag (the latter is the existing right-front closure). Its unsupported inverse/refit stays unsupported. Canonical paired N/M and wake/cut machinery are reused unchanged; no duplicate PARENT_FIT or new LeftFront fit is introduced. These are mathematical/data-contract blockers, not permission or network blockers.

## Opt-in checkpoint contract

Unset `REI_CONTINUOUS_DURABLE` keeps the original OFF caller. Explicit modes are `prime`, `live`, `resume`, `probe` and test-only `pending-control`; an unknown mode refuses before Frame/science. An explicit `REI_CONTINUOUS_RUN_ROOT` is required. The reused local namespace authority binds random identity to host, boot, canonical root and inode under one kernel writer lock. Copied roots, other hosts/reboots and inherited fork handles are unsupported. No distributed/global identity service is claimed.

The typed checkpoint binds covered source/data BUILD_PIN, exact original config bytes, cold gas bits, all17 clock bits, persistent mesh, epoch3/4, every panel's canonical N/M components and logs, closure/front/epoch provenance and historical-loss metadata, retained increments, ordered charge occurrences/coefficients/units and accumulated source audit rows. It rebuilds the canonical ledger/registry through its unchanged committed operations and checks exact typed state. No fabricated in-memory Snapshot or numerical replay of the first three epochs is needed. Only original recorded epoch lineage is preserved; no absent genealogy is invented.

Encoder preflights the exact decoder before publication. HEAD reads are bounded to a regular nonsymlink file≤16MiB both at restore and stale-check. A fresh checkpoint lease and synced pending image precede atomic HEAD rename; memory transaction publication follows it. No rollback-shaped error is returned after rename; directory sync status is explicit. Resume reads HEAD only and retains pending files/consumed leases. The pending-control fault serializes the **same real committed k3 state**, exits73 before rename and adds no scientific trial: it proves checkpoint storage semantics, not a new numerical candidate. Exact clock, panel, gas/source/build context, schema and lease mismatches refuse. Epoch4 cannot silently extend beyond the original frozen window.

## Fresh evidence and commands

Final saved campaign passes14 focused controls, with two actual original k3→k4 acceptances. Each acceptance performs61550characteristic segments,194endpoint fits,70862opacity calls and70863zero-photo point-RHS admissions. These are original frozen-frame work counts, **not BASS BE solver calls**. The uninterrupted OFF and disk-restored path have identical counts and byte-identical final canonical oracle/precommit high-precision output. The accepted194-panel k4 state and source/loss audit restore byte-for-byte. All original gates—including Q8/Q16 and H16/H32 tightening, projection, N/M/energy reconstruction, residual/loss caps and independent precommit oracle—remain required. No default/rate/tolerance/floor/clipping/HH/RCT/CR changes occurred.

`ALL_EXECUTION_CAMPAIGNS.json` accounts for both iterations (four total final-interval acceptances); raw logs retain all loader/probe admissions separately. No old36performance cases, earlier native ledger tests, long redshift extension or new convergence campaign was run. Actual observed runtime RSS remained below256MiB; compile AS2GiB and runtime AS512MiB apply. One-core scalar ordered execution is used; inherited validated optimization code is unchanged.

From task-4, with existing installed Rust/Python/mpmath1.3.0/sha256sum (no installs):

```bash
python3 implementation/rei-continuous-checkpoint-v1/run_limited.py --core 0 --as-mib 512 --cpu-slice 10 --wall-slice 15 prepare-new -- python3 implementation/rei-continuous-checkpoint-v1/prepare_build.py
python3 implementation/rei-continuous-checkpoint-v1/run_limited.py --core 0 --as-mib 2048 --cpu-slice 25 --wall-slice 45 build-new -- cargo build --offline --manifest-path implementation/rei-continuous-checkpoint-v1/Cargo.toml --bin continuous_receiver
python3 implementation/rei-continuous-checkpoint-v1/run_limited.py --core 0 --as-mib 512 --cpu-slice 60 --wall-slice 90 runtime-new -- python3 implementation/rei-continuous-checkpoint-v1/tests/process_bridge.py
```

Use fresh command labels so prior receipts remain intact. Each test creates fresh isolated runtime directories. Archived runtime directories are forensic evidence; relocation/host reuse is intentionally refused. The code/data pin is not a cross-toolchain binary authentication certificate. Same pinned source, compiler contract and scalar controls are required; no hostile-disk or power-loss certificate is claimed.

This work consumes only the previous live slice's remaining139.20437CPU/242.088932wall, with a new10CPU/20wall review/admin reserve inside that remainder. The separate older52.918577CPU/66.006943wall is untouched. Packaging adds a measured receipt; final totals are outside the immutable archive. No resets, publication or uploads.

**Claim ceiling:** actual frozen-panel k3→k4 acceptance and restart only. General evolving `igm_continuous::ContinuousHistory` state/clock handling, lossless native BE adoption, LeftFront physical admission, full evolving gas/history, full-Wide and export authority remain unsupported/HOLD. This checkpoint does not claim a complete evolving cosmological history.
