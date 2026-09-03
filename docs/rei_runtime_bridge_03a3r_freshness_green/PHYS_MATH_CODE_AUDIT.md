# PHYS-MATH-CODE audit

## Closed by this source candidate

- structurally valid but stale source protection receipts are rejected;
- live protection is re-read after the thirteen-field toolchain re-attestation;
- live revalidation finishes before the reservation-indeterminate flag is set;
- the live observer is fixed-authority and GET-only;
- active rules, contributing active rulesets, empty bypass actors, absence of a
  creation rule, and exact global-ref absence are checked;
- raw server-response hashes and the source protection hash are preserved;
- source and live protection hashes are bound into the global receipt;
- the post-lease worker revalidates the same files and hashes before production
  runtime entry.

## Still open

- exact-head CI and independent package-verifier readback;
- actual repository ruleset creation and prospective-branch readback;
- target-host static preflight;
- crash-injection at the global-reservation boundary;
- the one native worker execution and result audit.

## Claim ceiling

```text
PASS_FRESHNESS_LIVE_READBACK_SOURCE     candidate until exact-head GREEN
PASS_ATTEMPT_REF_SERVER_PROTECTION      not claimed
PASS_FINAL_ATTEMPT_AUTHORIZATION        not claimed
PASS_NATIVE_RUNTIME                     not claimed
PASS_FIRST_CANONICAL_INTERVAL           not claimed
PASS_REI_PROVIDER                       not claimed
```
