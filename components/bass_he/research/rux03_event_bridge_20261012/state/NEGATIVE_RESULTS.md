# First failures and limits

1. `LOCAL_RUST_TOOLCHAIN_ABSENT`: environment observation, not a scientific
   failure. Resolved for this task through a source-bound clean CI build.
2. V1 `cargo fmt --check` exit 1: software-formatting failure. Native release
   build and affected 11+8 tests passed in the same captured run. The exact
   formatter output was applied and rebuilt as a new commit; the first failure
   is preserved under evidence/build_v1.
3. A linear conservation test alone cannot distinguish one from two copies of
   a conservative event bundle. This is a mathematical limit of that proposed
   discriminator, resolved here by a separate injected-event witness.
4. The initial warm stage has extremely small net rates after cancellation.
   Tiny-net relative errors are not used as numerical admission criteria.
   Componentwise and absolute-gross normalizations were declared before runs.
5. This source change does not complete the separate reused implicit primary,
   root or interval-bound routes. Their same-provider obligation remains a
   successor with its own affected evidence.

6. The first local probe lacked the original sources/acquisition.json auxiliary
   metadata in the materialized selected provider directory. This failed after
   BIND1 and before any RHS/EVENTS call. Exact PR97 bytes were restored; no
   source/rate/guard/threshold/binary change or hash bypass. Original failure
   and INPUT_MATERIALIZATION_REPAIR.json are retained. The CI seven-input
   capture was not a complete standalone provider snapshot.
7. The existing interval JSON is emitted before native close and does not
   instrument the outer process exit. The actual terminal exit0 is therefore
   recorded explicitly as a post-execution owner observation, with raw
   stdout/stderr hashes; it is not inferred from numerical PASS alone.
