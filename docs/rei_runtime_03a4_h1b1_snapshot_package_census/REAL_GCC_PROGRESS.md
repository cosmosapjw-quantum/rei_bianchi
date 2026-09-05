# REI H1B1 real GCC provider checkpoint

## Before this slice

User requested one BASS check and then REI-owned work. One BASS recent-PR snapshot, including #131 R1 comments, was read; no further BASS read or mutation is part of this task. The BASS owner work remains in the other session.

REI #68 already implemented and exercised `signed_archive_chain.py` with real GnuPG and synthetic metadata. Do not repeat that implementation. Base is `edec9771c1e725484ec1a7250ba0d340eb13e21b`, tree `d1250dac231688c1a0de7a84c93a15732a9a2660`; donor blob `a530ec095cca5a9347cb419f0ef9cb5632e39ed1` stays unchanged.

Container and separate Python probes in this session both failed before process start. New execution will therefore use bounded GitHub-hosted CI. This does not establish the user's Docker/H1A environment and does not consume a REI production attempt.

## Concrete implementation and acceptance

Extend existing H1B1 with one real provider probe, not a new admission framework. Authenticate Noble-updates at Snapshot `20250115T120000Z` using the existing verifier; locate exact GCC `13.3.0-6ubuntu2~24.04`; check its known DEB SHA-256; inspect its control identity and regular compiler member without extracting a filesystem or executing any package script or binary. Preserve original downloaded bytes, signature details, exact URLs, tool/keyring identities and typed result, including failures.

The public signing fingerprint is sourced from Canonical's SecurityTeam FAQ and Chisel documentation:

- https://wiki.ubuntu.com/SecurityTeam/FAQ
- https://documentation.ubuntu.com/chisel/en/latest/reference/chisel-releases/chisel.yaml/
- https://documentation.ubuntu.com/security/software-integrity/archive-verification/

The runner-installed public keyring is measured and copied; it is a declared probe input, not a retrospectively reconstructed organizational trust approval. OpenPGP verification authenticates metadata under that declared policy. It does not independently prove historical retrieval time or key lifecycle.

Eleven behavioral tests are frozen before implementation. They use real DEB containers with synthetic harmless contents and actual `dpkg-deb` tar output. There is no install or payload execution. Expected implementation-absent RED is 11 assertion failures, zero errors/skips. The subsequent GREEN workflow must remove `--expect-missing` and require successful tests; a missing implementation must never be laundered into GREEN.

After observed software GREEN, attempt the actual network probe once. Record a network/signature/metadata/member failure faithfully instead of weakening pins or changing Snapshot time. Ubuntu metadata authenticity, DEB identity and compiler-member identity must remain distinct evidence fields.

## Claim ceiling

Even a successful real probe establishes one actual authenticated provider/member only. It does not establish all eleven OS/prestart roles, dependency/ELF closure, an installed rootfs, Rust closure, H1A source/daemon re-admission, Section-0, first canonical interval or provider/scientific admission. `authority_effect=NONE`, `full_census_complete=false`, `installed_files_verified=false`.

Historical REI #67 native mathematical evidence and BASS #130 are not rerun or modified. No production ref, lease, controller, worker, host package, rootfs, ready, merge or force push is touched.

## Execution checkpoint

Frozen tests and workflow prepared. No new test or live-archive PASS exists at this checkpoint. Implementation remains absent until exact missing-feature RED is actually observed. Record subsequent exact-source execution identities below without altering the historical RED.
