# Historical base-closure audit prompt

This document preserves the narrow read-only diagnostic that established the
prior reported aggregate. It is not the continuation prompt.

Use [LOCAL_CODEX_REPAIR_PROMPT.md](LOCAL_CODEX_REPAIR_PROMPT.md) for the
current bounded workflow. It begins with this audit, then permits only the two
exact, create-only supplemental members declared in `REPAIR_CONTRACT.json`.

The historical audit still has one purpose: given the exact admitted archive
and the original direct stdlib directory, it must establish all three facts
before materialization:

```text
archive/base member comparison                  PASS (62 versus 62)
Python and shell legacy closure                 7aae7f6cffe33365096e9f837378c9a26de46efd7d109eccd446d45703eee6c0
first result                                    RUST_STDLIB_CLOSURE_SHA256_MISMATCH_CONFIRMED
```

Any other outcome is `STOP_INVALID`; preserve its receipt and do not use the
repair path. The bounded continuation never changes the locked driver or
digest and requires a fresh full Section 0 process after materialization.
