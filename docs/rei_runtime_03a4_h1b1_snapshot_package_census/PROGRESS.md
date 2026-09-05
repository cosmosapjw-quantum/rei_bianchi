# H1B1 signed archive-chain implementation checkpoint

## Before implementation

REI runtime frontier remains H1B1, independent of BASS geometry. Current evidence/formula publication is REI #67; the runtime source is the divergent #59 line and is not merged with the formula branch. This bounded child uses #59 commit `00d17c932eb41dbae6467e1e2fdf46818799d6db` / tree `4752300f2715fba6368811204d159a5d4c2f6465`.

The single requested BASS check read PR #131 and its later R1 comment: a 15-file owner patch and software GREEN are recorded, while changed-source native verification remains blocked. That work stays with the other thread. No BASS source or follow-up BASS read is included here.

Local container and Python probes both failed before process start. Rather than issue another runtime-admission handoff, this task implements the first reusable offline cryptographic part of the already approved H1B1 census and tests it through GitHub Actions.

Test-first state: 18 behavioral tests are frozen before the component exists. Tests use actual `gpg`/`gpgv` and synthetic signed metadata. Private fixture keys are temporary, never published. No actual Ubuntu metadata/payload, H1A receipt, Docker daemon, installed executable or REI production execution is admitted by these tests.

The original PR58 eight failures and PR59 eleven failures are intentionally preserved. Completing this component will not be called a full H1B/H2 GREEN. Full live census still needs approved archive keyring provenance, archive retrieval evidence, H1A/Docker binding, provider enumeration, DEBs, canonical member/symlink and installed-file closure.

## Intended interface and evidence model

`verify_chain` receives immutable byte buffers and an explicit frozen trust policy. It runs `gpgv` with a private copied keyring whose SHA-256 matches the policy, parses machine signature status and extracts only authenticated Release text. The authenticated SHA256 section binds the Packages index; the verified Packages records bind the exact requested name/version/architecture, canonical archive filename, size and SHA-256 of supplied payloads. It never installs or executes payloads.

OpenPGP signature verification does not establish a key's organizational ownership, revocation state or historical retrieval URL. Policy admission and H1A/Snapshot retrieval remain external prerequisites. A signed old Release may be audited historically; this component does not call it current APT freshness or environment admission.

## Primary format references

- Debian Repository Format: https://wiki.debian.org/DebianRepository/Format
- GnuPG gpgv manual: https://www.gnupg.org/documentation/manuals/gnupg/gpgv.html
- Ubuntu Snapshot Service: https://snapshot.ubuntu.com/

Important manual constraints: `gpgv` trusts supplied keys and does not itself assess expiration/revocation; `--output` can obtain authenticated cleartext. Release SHA256/size binds index bytes; Packages SHA256/size binds archive bytes. Package filenames are canonical repository-relative paths. The snapshot selector is an input provenance label, not a field authenticated merely by the Release signature.

## Non-actions

No new physics, geometry oracle, Wolfram calibration, BASS import/repair, host downgrade, Docker build, rootfs, Section-0, attempt ref, local lease, REI production import/worker, first interval or provider. No new full-DAG proof or decorative plot. A byte-verification table and actual mutation tests are the appropriate evidence for this implementation.
