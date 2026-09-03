# Local Codex prompt — successor-host one-attempt REI runtime bridge

Use only the exact executable release identity published in this Draft PR's closeout receipt.

Required inputs:

```text
fresh full standalone clone
new PASS_EQUIVALENT_SECTION_0_SUCCESSOR receipt
exact Rust 1.94.1 executable locator
persistent attempt-state directory outside /tmp and Git worktrees
new evidence-root path that does not exist
GitHub token able to create one branch ref
```

Run the package tests and independent verifier first. Then invoke:

```bash
python3 handoff/rei_runtime_bridge_successor_host_20260903/successor_runtime_runner.py \
  --repo /ABS/FRESH/rei_bianchi \
  --expected-release-head <TESTED_GREEN_HEAD> \
  --expected-release-tree <TESTED_GREEN_TREE> \
  --successor-section0-receipt /ABS/PERSISTENT/successor-section0.json \
  --rustc /ABS/rust-1.94.1-prefix/bin/rustc \
  --attempt-state-root /ABS/PERSISTENT/attempt-3-state \
  --evidence-root /ABS/NEW/runtime-evidence
```

The runner first validates package/source/release/Section-0 state. It then creates the remote GitHub ref, then the persistent local lease, and only then enters the native dispatch. Never invoke it a second time. Any exit 65 is the preserved first outcome.

Do not start the first canonical interval after this command. Audit the outcome and native artifacts first.
