# H1B1 authenticated DEB members — progress

Task layers: implement, validate, review, document. Sole source writer: LOCAL_CODEX.

The fixed base and donor/test blobs were verified. The suggested branch and an identical implementation PR were absent. A new clean worktree outside the original checkout was created; existing dirty/untracked work is preserved.

Before RED: 15 behavioral methods are prepared: seven D obligations, four extra functional methods, three resource methods, and one fixture/module integration method. Expected implementation-absence RED is 14 assertion failures plus the independently passing fixture integration, not 15 broken imports or policy errors. The actual donor's ArchivePolicy class is used without weakening its strict type check.

The consumer will reuse the existing verifier and installed dpkg-deb read-only tar output. No direct DEB parser, package installation, maintainer-script execution, compiler execution, ldd or filesystem extraction is introduced. Existing signed-chain source, its 18 tests and broad H1B/H2 RED remain unchanged.

The existing GCC DEB was found at the user-specified path. Its optional format/member readback will be reported separately from real-GnuPG synthetic chain tests, with no Ubuntu trust-root or installed-file admission.

## Observed RED and first implementation

RED source `a264498d50b21a430014c254eb159a3ac38ff387`, tree `ffec48e8e9debd0254a169855274eac1e43db27d`: actual suite exit 1, timeout false, 15 methods, 14 implementation-absence assertion failures, 1 fixture integration PASS, 0 errors/skips/not-run. No POLICY_TYPE integration error was counted as feature RED. Frozen test SHA-256: `caff1db84874217e934063e49487db75b6f71549f0373fa7d4f55c7bb25aec6f`.

The first consumer implementation now calls the actual donor over one immutable payload mapping before dpkg-deb. It compares all authenticated DEB control identities, scans the full tar member sequence, reads unique regular witnesses and records actual content size/hash. Both new tool pipes, decompressed tar outputs, members, total input/output bytes and elapsed time have finite bounds. The unchanged donor retains its own input/decompression/signature timeout implementation; its buffered gpgv output is additionally checked on return, not claimed as a new streaming memory cap.

No new workflow is required for the local acceptance run. Frozen GREEN, original 18-test regression, repository verification and the optional already-present GCC identity smoke are the next executable actions.

## First GREEN and existing DEB smoke

Implementation source `fe5499a451931e88798e5986fd6ac1c59e6131ef`, tree `1393a5819a357814e40569a191422129b1bee2ec`: the unchanged 15-method suite passed on its first implementation run (29 explicitly recorded subcases), with 0 failures/errors/skips/not-run and exit 0. The original donor suite separately passed 18/18, exit 0; repository verifier passed 60 main artifacts. The two suites are not added to a misleading single obligation count.

Installed dpkg-deb 1.22.6 actually built and read none/gzip/xz/zstd fixtures; a made-up compression member was rejected. No host package was installed. Real output-overflow and timeout subcases passed, as did control identity, regular-file/link, duplicate/path and signature-tamper obligations.

The existing GCC DEB smoke ran once against the unchanged consumer: DEB SHA-256 `7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776`; member `usr/bin/x86_64-linux-gnu-gcc-13`, 1,023,032 bytes, SHA-256 `6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234`. Control Package/Version/Architecture match the specified GCC identity. This is `PASS_EXISTING_DEB_MEMBER_IDENTITY_READBACK_ONLY`, not Ubuntu signed-chain or installed-file verification. No synthetic re-signing of the GCC DEB was performed.

A focused GREEN-only workflow was added because the inherited workflow checks only the donor. It pins the protected donor/test blobs and frozen new test digest, checks out the actual head, runs the two suites separately using existing runner tools, and preserves public fixtures/logs/source with an artifact file manifest. It never treats absent implementation as successful historical RED.

## Sequential review and claim boundary

LOCAL_CODEX performed one PHYS-MATH provenance review followed by one PHYS-MATH-CODE review of candidate `42102144a3d8cff4433129e5bd562c17739f96e4` (tree `2b426817fb93de1ea4769297bb96206a606d93cf`), its exact five-file diff and the return candidate ZIP. The 243 actual archive files matched its file manifest. Candidate ZIP SHA-256: `39b9c96ee39486a4be4fa2ccc3624c4e3230e61b41944a65aeded54c7c1c80a2`.

PHYS-MATH: the result establishes member identity conditional on the caller's trust policy and the actual donor signature/index/payload result. Control identity and member content are derived from the same authenticated immutable DEB bytes. Synthetic signing exercises the implementation but establishes no Ubuntu key ownership, Snapshot retrieval, installed-file identity or historical-host completion. The GCC smoke remains a separate existing-file readback. No new physics equation or CAS result is claimed.

PHYS-MATH-CODE: the actual donor call and strict policy class identity, full logical tar scan, unique regular witness rule, control comparison, path rejection, finite archive/tool limits and real negative tests were checked against source and raw results. The frozen test file and protected donor/test blobs remain unchanged. Three workflow shell blocks passed syntax checks; remote workflow execution is a separate publication result. No in-scope P0/P1 finding or implementation repair was required. These are two sequential reviews by the same assistant, not independent review or approval by another WORK_THREAD.

Supported archive formats are those actually demonstrated with installed dpkg-deb: none, gzip, xz and zstd. Unknown compression was rejected. The consumer delegates DEB decoding to dpkg-deb and reads its uncompressed tar stream; it does not claim support for every historical DEB variant. Tool behavior references: [dpkg-deb](https://manpages.debian.org/bookworm/dpkg/dpkg-deb.1.en.html), [deb format](https://manpages.debian.org/bookworm/dpkg-dev/deb.5.en.html).

Limits apply to the added archive path. The protected donor's existing buffered gpgv capture remains inherited; its additional output check is post-return, not an enforced streaming peak-memory cap. This limitation is retained explicitly rather than extending the scope to rewrite the donor. `authority_effect=NONE`, `installed_files_verified=false`, and `full_census_complete=false` remain the claim ceiling; broad H1B/H2 results are unchanged.

The implementation and local acceptance are complete. The single publisher will non-force push this branch and read back its Draft PR, exact remote source and CI artifacts. Final remote identifiers and append-only Atlassian readback belong to the external return manifest so recording them does not create a source-hash cycle. No next host scope is started.
