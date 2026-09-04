# 03A4 host-epoch reconstitution plan

## Objective

Create an isolated Ubuntu Noble execution root in which the exact canonical paths used by the unchanged REI production bridge resolve to the locked toolchain bytes. Do not alter the interactive workstation's packages, alternatives or symlinks.

## Source authority

Compiler provenance is now identified as:

```text
Ubuntu Snapshot           20250115T120000Z
package                   gcc-13-x86-64-linux-gnu
version                   13.3.0-6ubuntu2~24.04
architecture              amd64
DEB SHA-256               7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
compiler SHA-256          6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
```

The identified extracted compiler must not be supplied from an alternate host path. Inside the isolated root, `/usr/bin/x86_64-linux-gnu-gcc` itself must resolve to the locked regular file.

## Required reconstruction phases

### H0 — immutable inputs

Preserve and checksum:

- the Ubuntu Snapshot APT metadata and downloaded DEB;
- the Rust 1.94.1 archive, signature and installed prefix;
- the exact REI release head/tree;
- the semantic toolchain lock;
- the existing ruleset/audit evidence hashes.

### H1 — isolated filesystem

Build a new persistent root outside all Git worktrees and outside the attempt-state root. Acceptable mechanisms are a dedicated chroot, systemd-nspawn root, or an equivalent mount-namespace container. The root must expose canonical absolute paths internally and must not bind the host `/usr` read-write.

### H2 — snapshot package epoch

Configure the isolated APT state to Ubuntu Snapshot `20250115T120000Z`. Install packages only inside the isolated root. At minimum, reconstruct the owners of the locked compiler, linker, Python, Git, MPFR, GMP, C runtime and required binary-inspection tools. Record package names, versions, `.deb` hashes and installed-file hashes.

### H3 — Rust closure

Install the signed Rust 1.94.1 distribution inside the isolated root and verify:

```text
rustc SHA-256
rustc --version
librustc_driver SHA-256
bundled LLVM SHA-256
stdlib closure SHA-256
target triple
```

### H4 — complete Section-0 dry census

Before invoking the repository preflight, compare all thirteen semantic fields and the canonical path map. This phase is read-only and emits a host-epoch candidate receipt. Any mismatch is a typed stop.

### H5 — exact standalone clone and static preflight

Only after H4 passes:

1. make a fresh standalone clone of the final path-binding GREEN release;
2. verify exact head, tree, ancestry, package indexes and executing-package binding;
3. run the production-import-free successor Section-0 emitter;
4. perform two GET-only observations of the global attempt ref;
5. emit the path-bound read-only static-preflight receipt;
6. stop for a separate audit.

## Forbidden operations

```text
modify or downgrade the interactive host
change update-alternatives or host symlinks
use the extracted compiler from an alternate path
mount host /usr read-write into the isolated root
create the global attempt ref
create a local lease or dispatch intent
invoke the controller or native worker
claim first-interval, provider or scientific readiness
```

## Required terminal state

```text
isolated host epoch                 PASS candidate
canonical runtime paths             exact and hash-matched
successor Section-0                 PASS
read-only static preflight          PASS
global attempt ref                  absent observed only
persistent local lease              absent
remaining native attempts           1
native runtime                       not run
next                                 stop and independently audit preflight
```
