# Validation matrix

| Area | Required evidence | Initial status |
|---|---|---|
| Software | State/protocol/controller/atomic-resume/failure tests | NOT RUN |
| Regression | Fresh partition-2048 result and endpoint equal predecessor | NOT RUN |
| Determinism | Serial and three-worker canonical hashes match | NOT RUN |
| Scientific gates | Every predecessor gate transported; NaN/Inf rejected | NOT RUN |
| Adaptive | Common commit, bisection, depth-six stop, event parent preservation | NOT RUN |
| Reproducibility | Interrupted/resumed bounded run equals uninterrupted | NOT RUN |
| Performance | Real one-attempt serial versus parallel, BLAS threads one | NOT RUN |
| Scope | Diff only this stage; predecessor/global bytes unchanged | NOT RUN |
| Independent review | Non-implementer diff/scientific review | NOT RUN |
| Full interval | User-owned local computation after pull | DEFERRED BY REQUEST |
| Event rebuild | Certified production callback/topology rebuild | NOT IMPLEMENTED — BLOCKS ON EVENT |
| Whole-history audit | Rank/modes/remainder/containment/global ledgers | DEFERRED |
