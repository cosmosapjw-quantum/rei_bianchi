# CI lane

Formatting-only commit `d760b535` changes the current Rust production/example/test paths using cargo fmt. Frozen research source copies and Cargo.lock are preserved.

The five initial commands in COMMANDS.json all returned exit 0. Rust workspace: 247 passed, 0 failed; jobs=1 and test_threads=1. Raw stdout/stderr and measured child CPU and wall times are retained. These are local CI checks; remote CI has not run and they do not admit a physical claim.

Python package verification and fresh-output stored replays perform no new science observer/provider/RHS/history work. Actual BASS verify.py, REC unittest discovery and REC adapter.py output commands also returned exit 0 under CPU900/wall1200 and one-CPU affinity. The workflow uses public repository-relative inputs and fresh mktemp outputs; BASS private --payload is deliberately omitted. The three additional commands and raw outputs are preserved in COMMANDS.json.
