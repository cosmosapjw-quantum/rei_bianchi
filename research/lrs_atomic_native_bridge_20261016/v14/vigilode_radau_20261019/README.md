# Opt-in native VigilODE Radau research adapter

This directory contains normal source files, an exact Cargo.lock, native additive payloads, source manifests and a portable preparation/runner script. It applies actual VigilODE Radau IIA3 to the existing native reconstructed photon moments and four gas variables. Production/default/adaptive/native SSPRK code is preserved.

## Restore without compiling or running physics

From the published `research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019` subtree:

```bash
python prepare_and_run.py --output-root /fresh/path/radau_work --prepare-only
```

The script locates the committed sibling `time_centered_ssprk2_20261019/restore_ssprk2_native.py`, invokes its existing V14→SSPRK restoration chain, verifies all 152 baseline files, appends the exact 173-byte transport hook and copies the new native module. It restores only the 477 SHA-bound VigilODE source files needed by the pinned workspace. No clone/worktree or replacement native implementation is used.

For an offline backup or existing source closure:

```bash
python prepare_and_run.py --output-root /fresh/path/radau_work --prepare-only --offline \
  --vigilode-source /path/to/immutable_source_closure
```

`--vigilode-archive /path/to/exact.tar.gz` accepts the full SHA-bound upstream archive instead. Without a local source/archive or bundled `backup/vigilode_source.tar.gz`, online mode downloads only the exact pinned archive URL recorded in `VIGILODE_PIN.json`, verifies its complete SHA256, then safely extracts the exact whitelist. `--input-root` and `--ssprk-restore` override repository layout detection when using a backup arranged differently.

Every output workspace must be fresh. Preparation records commands, stdout/stderr, exit status and hashes, and stops on a source mismatch. `--prepare-only` does not fetch Cargo dependencies, compile, run tests or execute any scientific case.

## Build and run explicitly

Use a Rust toolchain compatible with pinned VigilODE (the measured execution used Rust/Cargo1.94.1). Optional `--cargo /path/to/cargo` selects it; a sibling rustc is selected automatically. Keep Cargo.lock: it preserves an upstream yanked dependency required by the pinned release.

```bash
python prepare_and_run.py --output-root /fresh/path/radau_case \
  --vigilode-source /path/to/immutable_source_closure \
  --cargo /path/to/toolchain/bin/cargo --cargo-home /path/to/cargo_cache \
  --offline --case fixed radau 4
```

The script first performs a locked Cargo fetch (offline when requested), followed by a mandatory offline, locked release build. It records exact source bytes, source hashes, executable hash, command, stdout/stderr and exit status. Raw JSON contains endpoints, stage increments, independently reconstructed stages, common-stage physical events, native call counts and work counters.

`--all` runs the seven focused tests followed by exactly nineteen cases: fixed geometry Radau N2/4/8/16 and SSPRK N8/16/32; source-on GL2 and seeded disabled-source GL2, each with Radau/SSPRK N4/8/16. Both methods cap native RHS attempts at200000 per case. Radau additionally enforces a30s internal wall cap. SSPRK has no internal wall check; all cases use an external process timeout of at most40s and at most the remaining180s total native budget. A failed family is stopped while independent families may continue. Failed/truncated cases remain recorded and are never counted completed. No optional optical-depth probe or extra refinement is included.

## Existing measured evidence

`receipts/MATRIX_RECEIPT.json` records nineteen completed sandbox cases, including reused final-source fixed N4, with zero failed/truncated cases. Total unique work was38840 native RHS attempts and9.146159986s of native case wall; the eighteen new cases used38068 attempts and8.979949891s. Each case has raw structured records and an exact pre-execution source archive. This is sandbox evidence, not a new NCP platform run.

The current C9-corrected FD implementation permits one-sided fallback only for explicitly typed inadmissible perturbations; native internal/arithmetic/provider failures propagate. `receipts/classified_focused` records the classification regression plus six focused native tests. `receipts/final_source_n4` supplies the complete final-source gate snapshot. `IMPLEMENTATION_HANDOFF.md` records earlier failures and limitations.

Scientific acceptance, empirical refinement interpretation and any larger campaign remain with the root scientific owner. The adapter supplies a discrete-system reference; it does not assert a rigorous error bound, universal positivity, universal stiffness success or an accuracy order from conservation alone.


### Portable runner process checks

`python -m unittest discover -s tests -p test_prepare_runner.py -v` exercises only process plumbing with explicitly labelled Python stubs; it executes no native history. The runner returns a nonzero final exit for any failed, truncated, family-blocked or budget-unrun case after preserving MATRIX_RECEIPT. Each process timeout is capped by the remaining total native wall budget. Actual cargo/rustc `-Vv`, executable hashes and host metadata are captured before dependency fetch/build. Source archives include an explicit archive-member-to-original-path mapping.

Tool invocation paths preserve cargo/rustc symlink basenames for rustup multicall dispatch; byte hashing follows the links without changing the invoked path. The process regressions include an actual dispatch-name symlink stub.

The historical raw `config.case_wall_cap_s` describes the Radau internal budget; it does not imply an internal SSPRK wall check. Historical raw records are preserved unchanged.
