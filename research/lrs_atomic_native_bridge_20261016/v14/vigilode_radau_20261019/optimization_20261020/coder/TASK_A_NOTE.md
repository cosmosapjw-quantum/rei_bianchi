# Optimization loop task A: unchanged baseline preparation

Scope: C2/C4 preparation supporting root-owned C5/C6/C8 decisions. No scientific cases, unit tests, model/tolerance edits, Git changes, uploads, network fetches, or scientific admissions are authorized in this task. Root scientific source identity: d87ba9ca25acb8a2a032154fa23057b45acd6207. Delivery reference: 5cccbcfb28a2cec57997493160b49b79954fe8f3.

## Instructions actually used

Read repository policy `/workspace/scratch/6af5e9e6c737/resume_20261020/github/AGENTS.md` and PhysMath Research Loop 1.3.0 `SKILL.md`, `STAGE_SELECTION.md`, `references/POLICY_INTEGRATION.md`, `references/CODING_LOOP.md`, and `references/SUBAGENT_MODE.md` under `/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop`. This is a mechanical child with root retaining scientific criteria and interpretation. No recursive delegation/review.

## Host and preparation observations

Host Linux x86_64, AMD EPYC 9V74, visible CPUs 0–8, quota 800000/100000 (8 CPUs), memory.max=8589934592, no swap, initial disk free 5.7 GiB. taskset and C/C++ compiler available; rustc, cargo, perf absent on PATH. No executable files found in restored baseline or prior prepared source. `03-rust_1_94_1_env.sh` points at an absent /mnt/data prefix.

Read the supplied Rust archive installer before use. It accepts `--disable-ldconfig`; this is the actual spelling corresponding to the parent task's no-ldconfig intent. Selected only rustc/cargo/rust-std, installed into this task's `rust_prefix`, without system or profile changes. Toolchain extraction/install and build are executed by `task_a.py`; raw argv, environment subset, stdout, stderr and outcome are in `receipts/`.

Verified normal `prepare_and_run.py --offline --prepare-only` restore created `baseline/` from the read-only baseline archive. Its PREPARE_RECEIPT records 152 native baseline files and 477 pinned VigilODE files, with source pin 8a8bd409b1d96c7b7421f496d229e119fd3d284e and adapter source identities. Offline cache is copied to task-owned `cargo_home/`. Build is one locked/offline release attempt, jobs=2, timeout=420 seconds, target directory `target_baseline/`.

## Code-derived profiling plan (unmeasured)

The CLI accepts `output.json fixed|birth|disabled radau|ssprk N`. Frozen baseline uses 8 transport cells, 8 angular cells, one transport thread, 128 background panels, Newton atol=1e-13 and rtol=0. Native RHS cap=200000 and wall cap=30 seconds. Task A did not execute this CLI.

`Coordinates::new` (adapter/src/lib.rs) has dimension 4 + one/two coordinates per occupied photon cell; an empty birth segment begins with dimension4. `Context::jacobian` attempts one base evaluation plus two perturbations per coordinate. Each admissible perturbation decodes and validates state, prepares transport, integrates node rates, runs AxbiProvider.point and generates Events/affine diagnostics. Budget's native RHS attempt counter includes finite-difference replay; library WorkCounters RHS counters alone do not count those callback-internal evaluations.

`CovariantTransport::prepare` routes the frozen single-thread configuration to `prepare_legacy_serial`. That reconstructs every occupied cell through `cell_quadrature`, including `positive_reconstruct`, threshold splitting, positive quadrature, node cross sections, and ray geometry. Gas-only FD perturbations still rebuild photon quadrature. Photon perturbations can change the reconstruction; no cross-perturbation cache was introduced.

VigilODE `radau_step_kernel` constructs a dense 3*d stage matrix, uses modified Newton with bounded Jacobian refresh, and factors through the existing dense LU. Existing WorkCounters record RHS, Jacobian builds, nonlinear iterations/residuals, direct factorizations and solves. Adapter reports counters per chemical segment. Its three replayed stage evaluations preserve physical residual/affine checks.

Feasible later profiling, pending root contract: additive timers/counters for admissibility/decode, prepare, native_rates/provider, FD Jacobian, Radau solve and report construction. Instrumented timing must be kept distinct from uninstrumented matched-accuracy speed measurements. Use one fixed allowed CPU for timing repeats, record dimension/nodes/work counts, preserve native exceptions and frozen numerical tolerances. No measured hotspot dominance or speedup claim has yet been made.

## Stop boundary

After the single build finishes, record actual outcome and executable hash in `receipts/BUILD_RESULT.json` if successful, then return to root. No native cases until root supplies target-matched performance contract. Substantive semantic repair returns to root.

## Actual task A closeout

The single release build exited 0 in 150.89343555199957 seconds. stdout was empty; stderr was 5876 bytes and ends with Finished release profile. Executable: `target_baseline/release/rei-vigilode-radau-research`, 4,286,376 bytes; SHA256 `28dfc8dbfe627acd7c7d2f77c08746db6d5f67f620b6e6a38a1b658c52eebc2d`. Rust compiler reports 1.94.1; raw verbose compiler/Cargo identities are in receipts. Scientific cases and tests remain NOT_RUN. Stopped at the requested boundary; next executable action requires root-owned performance contract.
