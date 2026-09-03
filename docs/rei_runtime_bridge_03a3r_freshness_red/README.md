# REI 03A3-R freshness/live-readback intentional RED

PR #47 correctly requires a server-protection receipt, but its validator accepts
that receipt without a time bound. The controller validates the file, performs
toolchain re-attestation, and later creates the global ref without reading the
live ruleset/effective-rule surface again.

Therefore an old receipt can survive deletion or weakening of the ruleset. The
source claim `PASS_AUTHORITY_BINDING_SOURCE` remains useful, but it is not yet a
sufficient precondition for the one final remote lease.

This node is test/docs/workflow only. It creates no ruleset, attempt ref, local
lease, dispatch intent, native outcome, first interval, provider, or scientific
claim.
