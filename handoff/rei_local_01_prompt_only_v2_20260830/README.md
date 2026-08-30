# REI-LOCAL-01 prompt-only bootstrap V2

This additive package fixes the handoff usability gap that remained in PR #19:
the original local prompt required a terminal commit and PR URL from a separate
publishing response. `LOCAL_EXECUTION_PROMPT_V2.md` embeds those values plus the
exact locator path, Git blob, and raw SHA-256, so the prompt can be attached by
itself.

The sealed PR #19 package is unchanged. V2 is stacked on its exact terminal
commit `04a353339c0fe517ac5209a78bc57b49b8006f77` and treats its branch only as a
transport fallback. The prompt performs an unconditional Git 2.43-compatible
full-closure fetch before any authenticated object read, uses an empty refmap,
does not write `FETCH_HEAD`, verifies terminal/payload trees and ancestry, and
atomically publishes only the exact locator bytes into a private external
directory.

## Use

Attach only `LOCAL_EXECUTION_PROMPT_V2.md` to the local executor. The executor
must supply environment-specific absolute paths for the existing repository
and a new private external pin root, then follow the prompt verbatim.

The prompt does not authorize REI-LOCAL-02, the 46,080-node three-lane pilot, a
first-interval pass, merge, ready transition, auto-merge, or modification of
any existing branch or worktree.

## Test

```bash
python3 -m unittest -v \
  handoff/rei_local_01_prompt_only_v2_20260830/tests/test_prompt_only_bootstrap_v2.py
```

The nine stdlib tests execute the actual sentinel-delimited Bash bootstrap with
a strict deterministic Git process boundary. They cover exact locator
materialization, byte-mutation rejection before publication, post-fetch object
growth rejection, exact identity mismatch rejection, signal-safe cleanup,
atomic no-overwrite behavior, exact-SHA transport fallback, hostile Git
environment scrubbing, and removal of the two unbound publication placeholders.

## Claim boundary

```text
current_claim       NO_PASS_FIRST_CANONICAL_INTERVAL
canonical_pilot     NOT_RUN
scientific_pass     NOT_CLAIMED
merge_or_ready      NOT_AUTHORIZED
```
