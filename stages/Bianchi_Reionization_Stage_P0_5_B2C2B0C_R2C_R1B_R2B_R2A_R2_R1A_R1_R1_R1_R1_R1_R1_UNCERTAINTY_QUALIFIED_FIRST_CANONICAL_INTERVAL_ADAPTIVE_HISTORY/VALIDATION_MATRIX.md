# Validation matrix

| Area | Required evidence | Initial status |
|---|---|---|
| Software | State/protocol/controller/atomic-resume/failure tests | PASS — 49 unittest cases |
| Regression | Fresh partition-2048 result and endpoint equal predecessor | PASS — 22 exact checks |
| Determinism | Serial and three-worker canonical hashes match | PASS — record and 3 state hashes |
| Scientific gates | Every predecessor gate transported; NaN/Inf rejected | PASS for one endpoint and unit corruption cases |
| Adaptive | Common commit, bisection, depth-six stop, event parent preservation | PASS — pure policy + fake-process integration |
| Reproducibility | Interrupted/resumed bounded run equals uninterrupted | PASS — record/state hashes equal; transition journal replayed |
| Concurrency | Runner/resume/package share one persistent nonblocking run lock | PASS — active peer refused; lock persists and is not worker-inherited |
| Runtime closure | Exact dependency/JAX/worker/source/environment contract | PASS — direct and transitive pins; JAX absent; worker SHA bound |
| Packaging | Stable validate-only snapshot, evidence completeness, no clobber | PASS — journal/receipts/snapshots selected; active run refused |
| Performance | Real one-attempt serial versus parallel, BLAS threads one | PASS — 46.153 s vs 16.984 s, 2.72x |
| Scope | Diff only this stage; predecessor/global bytes unchanged | PASS — base diff path guard and predecessor hashes |
| Independent review | Frozen non-implementer runtime/scientific/operations review | PASS — no remaining P0/P1/P2/P3 finding |
| Full interval | User-owned local computation after pull | DEFERRED BY REQUEST |
| Event rebuild | Certified production callback/topology rebuild | NOT IMPLEMENTED — BLOCKS ON EVENT |
| Whole-history audit | Rank/modes/remainder/containment/global ledgers | DEFERRED |
