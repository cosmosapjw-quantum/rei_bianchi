# Runtime governance and host-epoch state

## Historical runtime stop and bounded source repair

The exact standalone runtime bridge stopped at

```text
STOP_INVALID: UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION
RuntimeClosureError: UNDECLARED_IMPORT: ntpath
```

The source repair at PR #37 added exactly `ntpath` to the closed declared-import-root list. The production bridge and numerical physics were unchanged. That repair is source-closed; it is not a native runtime pass.

## Pre-lease import firewall

The runtime-governance line subsequently established that the production bridge must not be imported or executed before both the global and persistent local attempt leases exist.

The allowed sequence is

```text
static byte/Git/package preflight
→ fresh protection readback
→ global create-only lease
→ persistent local O_EXCL lease
→ dispatch intent
→ separate worker
→ one production runtime entry
→ separate result audit
→ first-interval eligibility
→ provider review
```

A production import that can fail is part of the irreversible attempt region. Repeated pre-lease imports cannot be treated as harmless inspection.

## Fixed authority and executing-byte binding

The active governance sources remove caller-selected GitHub authority and bind the final path to

```text
API authority  https://api.github.com
repository     cosmosapjw-quantum/rei_bianchi
```

They bind the executing package and indexed bytes to the verified Git checkout, require a complete successor Section-0 re-attestation immediately before reservation, and bind all authorization receipts to fixed state/output/source paths.

## Canonical runtime paths

The production bridge uses fixed post-lease paths. Source-level path binding requires every preflight witness to equal the strict resolved regular file behind its declared runtime path, not merely an alternate file with the same digest.

Load-bearing paths include

```text
/usr/bin/git
/usr/bin/python3.12
/usr/bin/x86_64-linux-gnu-gcc
/usr/bin/x86_64-linux-gnu-gcc-13
/usr/bin/ld
/usr/bin/ldd
/usr/bin/readelf
ELF interpreter
libc.so.6
libgcc_s.so.1
/usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1
/usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0
```

An exact-hash compiler copied to a different path does not satisfy the path-bound contract.

## Repository ruleset

Fresh direct GitHub readback during this consolidation returned

```text
id                  22240889
name                REI immutable attempt-ledger refs v1
target              branch
enforcement         active
include             refs/heads/attempt-ledger/**
rules               update, deletion, non_fast_forward
bypass actors       []
current bypass      never
```

GitHub normalizes the active update rule in GET responses to `{"type":"update"}`. The locally owned creation payload remains stricter and requires `update_allows_fetch_and_merge=false`. The request-payload and server-GET validators must remain separate.

## Final-attempt ref

The fixed ref is

```text
refs/heads/attempt-ledger/rei-runtime-bridge-ntpath-rebind-20260903-attempt-3
```

Fresh direct readback returned HTTP `404`.

```text
classification      ABSENT_OBSERVED
authority_effect    NONE
reservation         NOT_ACQUIRED
attempt consumption NO
```

A read-only 404 does not authorize execution. The global lease is consumed only by an atomic create-only successful reservation.

## Independent ruleset audit history

The first operator independent audit correctly stopped at

```text
STOP_INVALID: LIVE_RULESET_UPDATE_POLICY_MISMATCH
```

because the independent live validator still expected the request-payload representation after GitHub normalized the GET response. The later source repair accepts omission only on the fixed-authority GET-only surface while continuing to reject explicit `true`, malformed parameters, wrong rules, wrong pattern, disabled enforcement, bypass actors, and creation restriction.

The active runtime line records the later independent ruleset audit as operator evidence. The consolidation directly reverified the live ruleset and ref state but did not recreate the operator audit bundle.

## H1A isolation evidence

PR #59 binds the following operator-produced durable evidence:

```text
PASS_REI_03A4_H1A_DOCKER_ADMISSION
PASS_H1A_DOCKER_ADMISSION_INDEPENDENT_AUDIT
PASS_H1A_DURABLE_AUDIT_CLOSEOUT
```

```text
independent audit receipt SHA-256
5d344fbfc8a68368386dfcc1ef0ef882813c819e8a263f5a589ab41100d7c9b6

post-audit manifest SHA-256
d1054f80c3d6b48918d840b4b0ad479a8df7381350e1ee9cfacbd1086427eb26

seed RepoDigest
ubuntu@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517

seed image ID
sha256:a6f81fb630d51837271b89f8193810a5fc493fa4f30a55d7ebcdb3a66f3cc63a

snapshot
20250115T120000Z
```

H1A establishes the isolation mechanism. It does not establish the historical execution epoch, installed package closure, ELF closure, Rust closure, Section-0, or runtime admission.

## Locked compiler provenance

The operator's read-only Snapshot census identified exactly one matching package:

```text
snapshot          20250115T120000Z
package           gcc-13-x86-64-linux-gnu
version           13.3.0-6ubuntu2~24.04
architecture      amd64
DEB SHA-256       7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
compiler SHA-256  6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
classification    PASS_LOCKED_CC_PACKAGE_IDENTIFIED_PROVENANCE_ONLY
```

The negative-control Snapshot `20240501T120000Z`, package version `13.2.0-23ubuntu4`, produced compiler SHA-256

```text
29d93d06ab60d67ae118dcf1f8ee0ae14f593b0272df58d3d4ee8c12e0243715
```

and did not match.

The current interactive host reports package version `13.3.0-6ubuntu2~24.04.1` and canonical compiler SHA-256

```text
1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26
```

so it is not the locked host epoch.

The downloaded and extracted matching compiler is provenance evidence only:

```text
DO_NOT_USE_EXTRACTED_BINARY_FOR_03A4=true
```

Passing it from an alternate path would violate the canonical path-binding contract.

## Rust boundary

The supplied environment helper sets

```text
RUST_1_94_1_PREFIX=/mnt/data/rust-1.94.1-prefix
PATH=$RUST_1_94_1_PREFIX/bin:$PATH
LD_LIBRARY_PATH=$RUST_1_94_1_PREFIX/lib:$LD_LIBRARY_PATH
```

This is a locator helper only. It does not prove the full Rust driver, LLVM, standard-library, ELF, dynamic-library, or installed-file closure required by H3.

The project runtime core remains Rust 1.94.1 with MPFR 256-bit directed rounding. JAX and `jaxlib` cannot discharge the load-bearing numerical gate.

## H1B/H2/H3 obligations

The next host-epoch package must enforce:

1. the exact H1A durable chain and admitted seed identity;
2. local Unix Docker context and daemon identity;
3. digest-only `linux/amd64` execution with `--pull never`;
4. no host bind mounts, Docker socket, privileged mode, or host namespaces;
5. signed Snapshot `InRelease`, identified archive keyring, `Packages` hashes, and no trust bypass;
6. complete package versions and every DEB SHA-256;
7. canonical symlink map and installed-file manifest;
8. Git, Python, GCC, ld, ldd, readelf, ELF interpreter, libc, libgcc_s, MPFR, and GMP closure;
9. exact Rust driver, LLVM, and standard-library closure;
10. deterministic transport archive with `authority_effect=NONE`;
11. independent revalidation of upstream manifests;
12. strict withholding of Section-0, attempt reservation, runtime, provider, and science claims.

## Updated runtime DAG

```text
ntpath source closure                         PASS
pre-lease import firewall                    PASS_SOURCE_CI
fixed authority/executing-byte binding       PASS_SOURCE_CI
repository ruleset                           ACTIVE
final attempt ref                            ABSENT
canonical runtime path binding               PASS_SOURCE_CI
H1A Docker mechanism                         PASS_OPERATOR_EVIDENCE
H1B1 full signed-Snapshot package census     NEXT
H1B2 fresh isolated root                     BLOCKED_ON_H1B1
H2 installed-byte and ELF closure            BLOCKED_ON_H1B2
H3 Rust closure                              BLOCKED_ON_H2
H4 thirteen-field dry census                 BLOCKED_ON_H3
H5 successor Section-0/static preflight      BLOCKED_ON_H4
independent preflight audit                  BLOCKED_ON_H5
global/local leases and one native dispatch  BLOCKED
runtime-result audit                         BLOCKED
first canonical interval                     NO_PASS
provider                                     NOT_AUTHORIZED
```

## Attempt ceiling

```text
remaining native attempts  1
retry after next outcome    0
```

No task in this consolidation consumes or reserves that attempt.
