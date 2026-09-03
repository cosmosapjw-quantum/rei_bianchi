# REI runtime bridge successor-host executable handoff

Status:

```text
HANDOFF_SOURCE        IMPLEMENTED_AND_PORTABLY_TESTED
SUCCESSOR_SECTION0    NOT_CREATED
GLOBAL_LEASE          NOT_ACQUIRED
LOCAL_LEASE           NOT_CREATED
NATIVE_RUNTIME        NOT_RUN
FIRST_INTERVAL        NO_PASS
PROVIDER_EXPORT       NOT_AUTHORIZED
```

This package composes the governance policy from PR #41 with the unchanged PR #38 base runner and production bridge. A target host must:

1. check out the exact published executable release in a fresh full standalone clone;
2. create a new successor Section-0 receipt with exact semantic-lock equality;
3. atomically create the fixed GitHub attempt ref with the executable release HEAD as target;
4. create a persistent local O_EXCL lease outside `/tmp` and outside every Git worktree;
5. invoke the native bridge exactly once;
6. preserve the first result and open a separate runtime-result audit.

The historical Section-0 raw receipt is never accepted or reconstructed on this route.

Hosted CI validates only the handoff code and contract. It has read-only repository permission and sets `REI_NATIVE_DISPATCH_FORBIDDEN=1`.
