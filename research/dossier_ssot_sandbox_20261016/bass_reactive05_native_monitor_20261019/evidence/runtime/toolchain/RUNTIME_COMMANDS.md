# BR05 runtime commands

```bash
source /workspace/scratch/996fc62899da/toolchains/rust_1_94_1_env.sh
export CARGO_TARGET_DIR=/workspace/scratch/996fc62899da/br05_work/target
```

After the implementation manifest and frozen source are identified, execute its full tests and strict Clippy with `--offline --locked --all-targets`. Check only new source paths with `rustfmt --check --edition 2024 --config skip_children=true`; do not rewrite inherited physics files. Actual results must be logged and tied to the new source hashes.

Native execution remains blocked on internal coordination until the instrumented driver tests and OFF parity are recorded. The normal positional arguments are `SIGNED_MINUS 121 16 0 8e12 false false 2 4 1e-12 8`. Additional monitor arguments will be recorded verbatim. Execute this history exactly once; preserve normal 54-column stdout, stderr, code/binary identity, elapsed time, final row and separate monitor artifacts.

The prior native cache has no ap_native_driver executable. Compile the selected instrumented driver from the final hash-verified source into an external target directory. Prior numerical outputs and timings are evidence for interpretation/cost only.
