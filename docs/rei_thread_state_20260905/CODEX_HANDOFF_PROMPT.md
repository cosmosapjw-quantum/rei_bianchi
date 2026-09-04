# Local Codex handoff — REI 03A4 H1B1 only

## Authority

Repository:

```text
cosmosapjw-quantum/rei_bianchi
```

Read first:

```text
docs/rei_thread_state_20260905/README.md
docs/rei_thread_state_20260905/CURRENT_STATE.json
docs/rei_thread_state_20260905/RUNTIME_GOVERNANCE_AND_HOST_EPOCH.md
docs/rei_thread_state_20260905/AUDIT_COMPILED_WORK_UNIT.json
```

Use the exact publication head of the Draft PR containing this handoff. Do not infer authority from a local branch with different bytes.

## Task

Execute exactly one bounded node:

```text
REI-RUNTIME-03A4-H1B1-
FULL-SIGNED-SNAPSHOT-PACKAGE-PROVENANCE-CENSUS
```

The objective is to identify and cryptographically bind the complete Ubuntu Snapshot package set required to reconstruct the locked pre-start runtime environment. This node is census and provenance only. It must not build the final root, emit Section-0, reserve the attempt, or invoke native code.

## Fixed input identities

```text
Snapshot
20250115T120000Z

seed RepoDigest
ubuntu@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517

seed image ID
sha256:a6f81fb630d51837271b89f8193810a5fc493fa4f30a55d7ebcdb3a66f3cc63a

locked compiler package
gcc-13-x86-64-linux-gnu=13.3.0-6ubuntu2~24.04 amd64

locked compiler DEB SHA-256
7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776

locked compiler binary SHA-256
6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
```

## Required runtime-file surface

Identify the provider package and exact Snapshot version for every canonical runtime file or symlink chain:

```text
/usr/bin/git
/usr/bin/python3.12
/usr/bin/x86_64-linux-gnu-gcc
/usr/bin/x86_64-linux-gnu-gcc-13
/usr/bin/ld
/usr/bin/ldd
/usr/bin/readelf
ELF interpreter used by the locked executables
libc.so.6
libgcc_s.so.1
/usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1
/usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0
```

Also enumerate package-manager and extraction dependencies needed to construct the later root reproducibly. Do not silently take them from the interactive host.

## Mandatory provenance checks

1. Verify the Snapshot `InRelease` signature using an identified Ubuntu archive keyring.
2. Record the keyring package/version and its byte identity.
3. Record `InRelease`, `Release`, and relevant `Packages`/`Packages.xz` SHA-256 values.
4. Resolve every required binary/library to exactly one package/version/architecture.
5. Download every required DEB without installing it on the host.
6. Record every DEB SHA-256.
7. Extract into a disposable census root without host bind mounts in the future execution container.
8. Record canonical symlink chains and target-file SHA-256 values.
9. Record an installed-file manifest for the required dependency cone.
10. Reject mixed Snapshot epochs, unresolved providers, duplicate incompatible providers, trust-bypass flags, unsigned metadata, or mutable latest mirrors.
11. Revalidate the H1A seed identities and upstream manifests independently.
12. Emit a deterministic transport archive and checksum manifest with `authority_effect=NONE`.

## Docker authority

Use only a local Unix Docker context and bind the daemon/context identity into the receipt. Reject:

```text
DOCKER_HOST TCP/SSH authority
remote contexts
host Docker-socket mounts
host bind mounts
--privileged
host PID/network/IPC namespaces
unbounded capability sets
```

Any future container command must use:

```text
--pull never
--platform linux/amd64
```

and the exact admitted seed digest.

## Hard prohibitions

Do not:

- run the successor Section-0 emitter;
- run the target-host static preflight;
- create or update any `attempt-ledger/**` ref;
- create a persistent local lease or dispatch intent;
- import or invoke the production runtime bridge;
- invoke Rust native code;
- use the extracted matching compiler at an alternate path as an execution witness;
- install or downgrade packages on the interactive workstation;
- mutate alternatives or host symlinks;
- merge, mark ready, force-push, or rewrite history;
- change physics, thermochemistry, runtime locks, tolerances, or the attempt budget;
- claim a first interval, provider, or scientific pass.

## Required outputs

Create a new bounded child branch and Draft PR containing only source/receipt tooling and normalized text evidence under a new path such as:

```text
docs/rei_runtime_03a4_h1b1_snapshot_package_census/
```

Required files:

```text
CONTRACT.json
PACKAGE_CENSUS.json
SNAPSHOT_METADATA.json
KEYRING_PROVENANCE.json
DEB_MANIFEST.json
SYMLINK_MAP.json
REQUIRED_FILE_HASHES.json
INSTALLED_FILE_MANIFEST.json
DOCKER_AUTHORITY.json
UPSTREAM_REVALIDATION.json
TRANSPORT_ARCHIVE_RECEIPT.json
PHYS_MATH_AUDIT.md
PHYS_MATH_CODE_AUDIT.md
SOURCE_INDEX.json
validate_package.py
CODEX_CLOSEOUT.md
```

Large DEBs, rootfs trees, and transport archives stay outside Git. Git contains their exact descriptors and hashes only.

## Expected terminal states

### PASS

Use only when all providers and signed metadata are complete and all manifests independently revalidate:

```text
PASS_REI_03A4_H1B1_FULL_SIGNED_SNAPSHOT_PACKAGE_PROVENANCE_CENSUS
```

This opens only H1B2 fresh isolated root construction.

### STOP

Stop at the first load-bearing failure, preserve it durably, and do not improvise around it. Examples:

```text
STOP_INVALID_UNSIGNED_SNAPSHOT_METADATA
STOP_INVALID_ARCHIVE_KEYRING_UNIDENTIFIED
STOP_INVALID_PACKAGE_PROVIDER_UNRESOLVED:<path>
STOP_INVALID_MIXED_SNAPSHOT_EPOCH
STOP_INVALID_DEB_HASH_MISMATCH:<package>
STOP_INVALID_SYMLINK_TARGET_UNRESOLVED:<path>
STOP_INVALID_DOCKER_AUTHORITY
STOP_INVALID_UPSTREAM_MANIFEST_MISMATCH
```

## Required verification order

```text
source identity
→ H1A lineage and seed revalidation
→ Docker authority
→ signed Snapshot metadata
→ provider resolution
→ DEB hash closure
→ extracted file and symlink closure
→ deterministic manifests
→ PHYS-MATH audit
→ PHYS-MATH-CODE audit
→ independent clean replay
→ Draft PR publication/readback
```

## Claim ceiling after PASS

```text
historical package provenance  COMPLETE
fresh isolated root            NOT_BUILT
installed executable epoch     NOT_ADMITTED
Rust closure                   NOT_RUN
successor Section-0            NOT_RUN
target-host static preflight   NOT_RUN
global attempt ref             ABSENT
remaining native attempts      1
native runtime                 NOT_RUN
first canonical interval       NO_PASS_FIRST_CANONICAL_INTERVAL
provider export                NOT_AUTHORIZED
scientific pass                NOT_CLAIMED
```

One-line objective: close the signed package-provenance census without crossing any execution or attempt boundary.
