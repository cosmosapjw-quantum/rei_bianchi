# Reproduce the new physical consumer

Checkout the published owner branch at the exact handoff commit; this unit is
`research/rei_ax11_owner_delta_20261116`. The final handoff also records the central
pin, public/local commit distinction and exact identical tree.

Python used:3.12.14, NumPy2.3.5, SciPy1.17.0. The existing owner helper additionally
imports pandas. The file manifest binds all actual physical inputs, including
the two T1 native-bracket files, eight cumulative T1 checkpoints, T0 terminal
checkpoint/ledger/history files, prior two gas-response tables and milestone table.
No new integration or sparse-history extrapolation is performed.

From repository root, choose a new output directory:

```bash
python3 research/rei_ax11_owner_delta_20261116/harness/analyze_owner_physics.py /tmp/rei_owner_physics_reproduction
python3 research/rei_ax11_owner_delta_20261116/harness/audit_owner_physics.py /tmp/rei_owner_physics_audit.json
python3 research/rei_ax11_owner_delta_20261116/harness/localize_milestones.py /tmp/rei_owner_milestone_reproduction
```

The producer writes immutable new output paths. Scientific tables are deterministic;
`SUMMARY.json` also records runtime, so whole-file summary equality is not expected
across executions. The audit independently reads the committed results and raw
inputs without importing producer functions. Its256-binary64-epsilon scaled check
is a representation check only. Original photon/energy tolerances remain1e-8 times
the native source inventory. Reaction-integral residuals are measured without
inventing a new admission threshold.

The two failed audit attempts in `audit_v1/ATTEMPTS.json` are preserved: a mixed
Decimal/float comparison, then conversion of binary64 interpolation operands via
short decimal strings. Exact `Decimal.from_float` corrected the latter without
changing the tolerance or physical outputs. The Wolfram JSON-symbol export failure
and corrected exact stoichiometric result are both in the receipt. These are
consumer/checker implementation issues; no native evolution failed in this unit.

T2 package generation and native input validation are separate from this consumer.
`harness/prepare_t2_package.py` constructs the exact proposed wrapper/executor from
hash-locked prior T1 code. `audit_t2_package.py` additionally needs the previously
restored full native prefix files at `../ax11_work/native_prefix_v1/` and intentionally
does not claim a Rust compile. The20 prefix byte hashes were checked both on the
native device and on these restored files, including complete state record4096.
See `T2_RUNBOOK.md` before any native work. The final physical-analysis download
contains the small reproducible physical-consumer inputs; the large original
prefix source/trace archives remain in the previously verified durable backup.

Every stage ZIP is an archive of its exact local committed subtree; all ZIP members
were compared with Git blob bytes. Remote publication creates a different commit
identity because the publication service sets its own commit metadata. Each receipt
verifies that the **entire Git tree** is identical, not just the file count. Neither
identity nor the scope of the original central pin is silently replaced.
