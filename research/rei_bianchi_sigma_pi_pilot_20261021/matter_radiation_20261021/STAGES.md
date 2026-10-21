# Matter/radiation extension: implementation ledger

| Stage | Actual evidence/status |
|---|---|
| R1–R3 | User component-split request, attachment intake, controller frozen CONTRACT_KO.md/THEORY_KO.md and independent contract review supplied. |
| R4 | Existing625/40,625samples decomposed without ODE. Sum-reconstruction maxabs4.336808689942018e-19. |
| R5 | Actual source-helper inversion, physical component axes and positivity bracket implemented. |
| R6 | Four new source/reduced comparisons and two signed-A directional energy checks passed; old suite not replayed. |
| R7 | Actual606 new coupled trajectories complete:600matter+6mixed,zero failures;25 neutral controls retain REFERENCE_REUSE provenance. |
| R8 | Three actual-data figures and complete plot CSVs generated and visually inspected. |
| R9 | Completed independent final source/raw/component review and response-fit addendum: **PASS_SCOPED_PRELIMINARY**, no blocking findings. See [FINAL_REVIEW](evidence/FINAL_REVIEW.md) and [RESPONSE_FIT_ADDENDUM](evidence/RESPONSE_FIT_ADDENDUM.md), plus their JSON records. Old625 PASS unchanged. |
| R10 | Source/validation checkpoint published at 34f93a48778a2d8a36b058e33de5302732752bae. Controller owns final delivery/publication metadata and backups; production NOT_ISSUED. |
| C1–C3 | Additive component_pilot.py reuses immutable parent helpers, RHS, matrix/basis and resource observer;8states. |
| C4 | Bracketed actual-helper A_m inversion and separate initial Pi_m/Pi_r realization; maxaxiserror4.336808689942018e-19. |
| C5 | Three targeted tests pass;2,506 parent/model/oldraw byte checks pass. |
| C6 | Finite resource pool observes host/cgroup CPU/memory between batches;actual6–8workers,BLAS1,nice10. Worker matrix/basis 재사용;각A trial의 canonical quadrature는 다시 구성하며 caching/speedup 주장은 없음. |
| C7 | New identity/checkpoints/raw/logs and component CSV/NPZ saved;failed/unfinished automatic retries prohibited. |
| C8 | Actual matter heatmap, old-history decomposition and mixed signed-component/Sigma figures with CSVs complete. |
| C9 | Independent source/raw review plus response-fit addendum completed PASS_SCOPED_PRELIMINARY; numerical gate closed. component_pilot.py SHA256 e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e. |
| C10 | NCP finite606+plot command prepared;published reference/endpoint and old representative tables remove need for old625 NPZ on NCP. Remote execution NOT_RUN. |

Dependency order: frozen split contract → old625 no-ODE decomposition/reference tables → actual matter inversion/new source comparisons → bounded606 new coupled trajectories → component tables/plots → completed independent final review + response-fit addendum PASS_SCOPED_PRELIMINARY → controller final delivery/publication/backups. Canonical DAG is controller-owned.

Execution-time PENDING_INDEPENDENT_REVIEW values in run.json/summary.json are preserved as historical receipts, not overwritten with the later admission decision.


## C10 — final component publication and complete dual backup

The reviewed code, response fit, raw-derived tables, plots, report and handoffs were published at `b140170ce0c58159368b6b81be49ac35ca764851` with an expected-head fast-forward from `34f93a48778a2d8a36b058e33de5302732752bae`. Six new code/contract/reference files were fetched from that commit and matched their staged text exactly.

The full parent-plus-extension archive has 5,747 payload files and one manifest. Every local member passed size/SHA256 and complete-membership verification. Both Drive and Dropbox whole GETs returned HTTP200/exit0 and exactly 37,945,383 bytes with SHA256 `2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d`. See `FINAL_BACKUP_ACK.json`, `PACKAGE_RECEIPT.json` and `FINAL_DELIVERY.json`. Archive documents retain their packaging-point state; this later Git metadata closes delivery without rewriting that archive. No recovered-archive numerical rerun was performed.

Source commit b140170 has two workspace cargo fmt failures and skipped workspace tests; this is separate from the actual Python scoped PASS. Final metadata publication keeps PR198 open/draft. The science gate remains closed, NCP remains NOT_RUN, and production remains NOT_ISSUED.
