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
