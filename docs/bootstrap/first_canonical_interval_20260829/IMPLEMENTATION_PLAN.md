# First canonical interval implementation plan

1. Create an isolated worktree from the immutable package commit, which is a
   descendant of audit commit `ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e` and contains reviewed stage tree
   `213c29c4b9d6bf4a626111c105bc2d7979507c49`.
2. Validate package, exact rec monitoring lock, stage manifest/preflight and the
   runtime review. Do not run or import the historical corrected-ODE candidate.
3. Reproduce one partition-2048 endpoint in all three lanes. Match predecessor
   classification, widths, local error, table summary, ledgers and endpoint
   arrays. Match serial/parallel canonical payload after excluding telemetry.
4. If and only if endpoint parity passes, compose the complete first canonical
   interval. Every attempt computes full, half, dependent half; all lanes accept
   together. Bisect only a failed attempt to depth six. Stop and preserve parent
   at a table event lacking a certified callback/rebuild.
5. Preserve atomic journal → LATEST → CONTROL publication and restart identity.
   No rejection becomes resumable state.
6. Run the independent whole-history audit: sparse rank, named owner modes,
   remainder growth, table-event distance, point-trajectory containment and
   seven ledgers.
7. One scientific and one code review, at most one reproduced P0/P1 repair,
   ordinary push and one draft PR. Do not merge or mark ready.
8. Hydrogen-frame/primordial splice remains deferred until the rec provider gate
   and adapter semantics are earned.
