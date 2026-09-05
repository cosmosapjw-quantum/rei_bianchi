# H1B1 signed archive-chain implementation checkpoint

## Before implementation

REI runtime frontier remains H1B1, independent of BASS geometry. Current evidence/formula publication is REI #67; the runtime source is the divergent #59 line and is not merged with the formula branch. This bounded child uses #59 commit `00d17c932eb41dbae6467e1e2fdf46818799d6db` / tree `4752300f2715fba6368811204d159a5d4c2f6465`.

The single requested BASS check read PR #131 and its later R1 comment: a 15-file owner patch and software GREEN are recorded, while changed-source native verification remains blocked. That work stays with the other thread. No BASS source or follow-up BASS read is included here.

Local container and Python probes both failed before process start. Rather than issue another runtime-admission handoff, this task implements the first reusable offline cryptographic part of the already approved H1B1 census and tests it through GitHub Actions.

Test-first state: 18 behavioral tests are frozen before the component exists. Tests use actual `gpg`/`gpgv` and synthetic signed metadata. Private fixture keys are temporary, never published. No actual Ubuntu metadata/payload, H1A receipt, Docker daemon, installed executable or REI production execution is admitted by these tests.

The original PR58 eight failures and PR59 eleven failures are intentionally preserved. Completing this component will not be called a full H1B/H2 GREEN. Full live census still needs approved archive keyring provenance, archive retrieval evidence, H1A/Docker binding, provider enumeration, DEBs, canonical member/symlink and installed-file closure.

## Interface and evidence model

`verify_chain` receives immutable byte buffers and an explicit frozen trust policy. It runs `gpgv` with a private copied keyring whose SHA-256 matches the policy, parses machine signature status and extracts only authenticated Release text. The authenticated SHA256 section binds the Packages index; the verified Packages records bind the exact requested name/version/architecture, canonical archive filename, size and SHA-256 of supplied payloads. It never installs or executes payloads.

OpenPGP signature verification does not establish a key's organizational ownership, revocation state or historical retrieval URL. Policy admission and H1A/Snapshot retrieval remain external prerequisites. A signed old Release may be audited historically; this component does not call it current APT freshness or environment admission. Signature timestamps are signer-declared values, not independent trusted timestamps proving that bytes existed at the selected Snapshot time.

The current intentionally narrow input domain is Noble/amd64 with one `component/binary-amd64/Packages.xz` index, exact requested `(package, version, architecture)` tuples, and bytes for exactly those package filenames. Multiple indexes can be verified individually by the subsequent census consumer, which must separately resolve provider completeness and dependency closure. Unsupported compression or paths fail closed; they are not silently normalized.

## Executed test-first lineage

All execution below occurred on GitHub-hosted runners in this work session. No local-container execution is claimed.

| Stage | Exact source | Run / job | Observed result |
|---|---|---|---|
| Frozen RED | `aae9d87aabd7609cb547f9ad602835522f08948e` | `33953237002` / `101271776124` | 18 tests, 18 assertion failures, 0 errors/skips; every failure is `MISSING_H1B1_SIGNED_CHAIN_IMPLEMENTATION` |
| First GREEN | `17393c5f3ef69a183df74d5c97fe63a68b59b2b1` | `33953443067` / `101272355571` | 18/18 actual real-GnuPG tests PASS, 0 errors/skips; frozen test file unchanged |
| Post-review CI repair | `87b7aa3ee7f16b94f90405ce5e511689c6811275` | `33953565450` / `101272683207` | GREEN-only invocation and absent-implementation negative control actually completed successfully; broader 11+8 RED boundary retained |

The full RED and first-GREEN logs were read; the repair job's individual completed steps were read. Repository verification, `git diff --check` and final clean source checks succeeded in these focused jobs. The repair's separate repository-verifier run `33953565410` also reported SUCCESS.

Artifact transport identities reported by upload-artifact (not independently downloaded/rehashed in the blocked local container):

- RED artifact `9965511416`, ZIP SHA-256 `e1471955499daf23d8ed18b1958f029124f1460002c761cf6b313bcfb57c5d56`.
- First GREEN artifact `9965579079`, ZIP SHA-256 `44c2ea9e18df093aa62388dff6ac739634c295b64f138f4401df2241dbac6a0a`.

The final documentation/PR publication must report its own exact-head CI separately instead of reusing the above commits' status as though those commits were the final head.

## What the tests actually exercise

The positive fixture creates a temporary RSA signing key with real GnuPG, exports its public keyring, signs Release metadata, produces an XZ-compressed Packages index, and verifies the supplied opaque payload bytes using the real gpgv executable. Its Ubuntu-shaped labels do not make it an Ubuntu archive signature. Private test keys remain in temporary directories and are removed.

The 17 rejection tests cover unsigned/tampered Release text, wrong keyring pin, wrong primary signer, wrong signed origin/suite, Release/signature time after the selected epoch, index hash/size tampering, duplicate signed index entries, case-insensitive duplicate Deb822 fields, duplicate providers, wrong exact version, payload hash/size mismatch, noncanonical archive paths, missing/extra payload sets, bounded decompression and duplicate Release fields. Several tests contain multiple subcases.

The broader original 19 expected failures still describe missing H1A/Docker/rootfs/full-runtime integration. Passing this component does not erase or reinterpret them.

## PHYS-MATH review — same-assistant sequential review

There is no physical equation, metric convention, unit, numerical tolerance, radiation/matter law or native numerical backend change. The evidence implication is conditional: an admitted public-key policy and trusted signature verifier authenticate Release text; signed hash/size entries bind index bytes; authenticated package metadata binds the exact supplied payload bytes, subject to the cryptographic assumptions of those primitives.

This implication does not prove semantic equivalence of compilers, dependency completeness, an installed ELF closure, numerical reproducibility, or a Snapshot retrieval event. A package version label alone is insufficient, and equality of a downloaded DEB hash does not certify the filesystem that a future runtime actually executes.

No CAS replay or physics plot was requested or claimed for this byte-provenance component. The appropriate evidence is the actual signature/hash acceptance and mutation-rejection matrix.

## PHYS-MATH-CODE review — same-assistant sequential review

Genuinely implemented: isolated copied keyring, keyring byte pin, actual gpgv status and signer allowlist, SHA-2 signature requirement, extraction of authenticated cleartext, signed metadata identity, raw compressed-index hashing before bounded XZ decoding, optional signed uncompressed-hash cross-check, strict unique Deb822 fields/providers, canonical repository-relative filenames, exact requested payload set and payload hash/size checks. Reports separately identify all input hashes and the declared policy hash, signature status/stderr, and the gpgv binary's observed path/hash.

A post-GREEN P1 was found in the initial workflow: its absence-triggered `--expect-red` mode could normalize deletion of the implementation as a successful historical RED. The single bounded post-review repair removes that branch from descendant CI. The historical RED commit remains unchanged. Current CI requires an existing implementation, exactly 18 successful tests with no skips, and independently executes a disposable missing-implementation control that must exit nonzero. No production code or test assertion was weakened for this repair.

The implementation/test run has no package installation, subprocess execution of package payloads, Docker access, network retrieval, production imports, global ref, lease or runtime authority surface. The only component subprocess is the explicitly supplied gpgv executable; the test fixture additionally uses gpg/gpgconf locally on the hosted runner.

Remaining limits are deliberate prerequisites, not closed findings:

- Caller must admit Ubuntu keyring origin, allowed fingerprints and the gpgv toolchain; recording a hash does not make that input trustworthy by itself.
- gpgv does not itself assess key expiration/revocation. Organizational key ownership and lifecycle remain external.
- A returned dictionary is a bounded computed report, not an unforgeable admission capability. A later consumer must bind/revalidate source, inputs, policy and output rather than trust a supplied PASS string.
- No actual Ubuntu archive bytes, real package provider inventory, H1A local receipt chain, Docker authority, member extraction, canonical symlink resolution, ELF/stdlib closure or first interval were verified here.
- The caller already supplies payloads as bytes; streaming/downloading very large DEBs belongs to the later intake layer. The metadata input sizes and XZ decompression are bounded here.

## After this work and next action

The executable signed-chain component exists and its frozen real-signature test suite ran GREEN. The task remains an implementation slice of H1B1, not another governance gate and not full H1B1 completion.

Next: use this component in the approved H1A/Snapshot census path, first obtaining the real admitted archive-keyring policy and signed metadata, then resolving exact provider/DEB/member identities for the existing required runtime files. Reuse the established successful GCC package evidence; do not reconstruct it as a fresh run. Preserve unknown providers and actual byte mismatches. Do not build a rootfs or invoke REI Section-0/production while doing that census.

Do not repeat BASS calibration, add a competing geometry owner, re-run the completed H1A Docker probe as ritual, or widen the cryptographic component into an installation/runtime runner.

## Primary format references

- Debian Repository Format: https://wiki.debian.org/DebianRepository/Format
- GnuPG gpgv manual: https://www.gnupg.org/documentation/manuals/gnupg/gpgv.html
- Ubuntu Snapshot Service: https://snapshot.ubuntu.com/

## Non-actions

No BASS source or second BASS read, new physics, geometry oracle, Wolfram calibration, host downgrade, Docker build, rootfs, Section-0, attempt ref, local lease, REI production import/worker, first interval or provider. No merge, ready transition or history rewrite. The prior native xAct component calibration and warning disposition remain historical REI #67 evidence, not a new run in this task.
