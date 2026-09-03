# REI pre-lease production-import firewall

This package is the GREEN successor to Draft PR #44's intentional RED contract.
It preserves the historical PR #42 and PR #43 packages as evidence and adds a
new execution boundary rather than rewriting them.

## Enforced order

```text
closed package and static Git/source verification
  -> fresh successor Section-0 receipt
  -> two read-only global-ref observations
  -> static preflight receipt
  -> atomic global attempt reservation
  -> persistent local O_EXCL lease
  -> create-only dispatch intent
  -> separate worker process
  -> receipt validation inside the worker
  -> first and only entry into the locked production runtime
  -> separate runtime-result audit
```

The static preflight and lease controller never import the production bridge.
The worker does not accept a preloaded module object. It dynamically loads the
locked successor runner only after validating the global, local and dispatch
receipts; the locked runner then reaches the unchanged production bridge inside
its existing one-shot runtime function.

## Current claim boundary

This branch establishes source and governance readiness only. It does not run
the target-host static preflight, create the global ref, create a local lease,
start the worker, execute native code, pass the first canonical interval, admit
a provider, or promote a scientific result.

The global reservation operation is create-only and never updates or deletes
the attempt ref. Once the POST may have reached GitHub, any ambiguous transport
or local failure is treated as attempt-consuming and is never retried.

## Source validation

Hosted CI is read-only and sets `REI_NATIVE_DISPATCH_FORBIDDEN=1`. It runs the
GREEN unit contract and the closed-package verifier but cannot execute the
controller or worker. Target-host execution requires a fresh standalone clone,
exact release head/tree, the pinned Git executable and source bytes, the fresh
successor Section-0 receipt, and persistent state/evidence roots outside `/tmp`
and Git worktrees.
