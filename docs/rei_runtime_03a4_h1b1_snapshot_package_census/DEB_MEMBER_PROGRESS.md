# H1B1 authenticated DEB members — progress

Task layers: implement, validate, review, document. Sole source writer: LOCAL_CODEX.

The fixed base and donor/test blobs were verified. The suggested branch and an identical implementation PR were absent. A new clean worktree outside the original checkout was created; existing dirty/untracked work is preserved.

Before RED: 15 behavioral methods are prepared: seven D obligations, four extra functional methods, three resource methods, and one fixture/module integration method. Expected implementation-absence RED is 14 assertion failures plus the independently passing fixture integration, not 15 broken imports or policy errors. The actual donor's ArchivePolicy class is used without weakening its strict type check.

The consumer will reuse the existing verifier and installed dpkg-deb read-only tar output. No direct DEB parser, package installation, maintainer-script execution, compiler execution, ldd or filesystem extraction is introduced. Existing signed-chain source, its 18 tests and broad H1B/H2 RED remain unchanged.

The existing GCC DEB was found at the user-specified path. Its optional format/member readback will be reported separately from real-GnuPG synthetic chain tests, with no Ubuntu trust-root or installed-file admission.
