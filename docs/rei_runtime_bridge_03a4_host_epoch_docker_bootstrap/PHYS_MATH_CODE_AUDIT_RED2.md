# PHYS–MATH–CODE hostile audit — H1A to H1B/H2

## Steelman

The current chain has strong separation of concerns: protected GitHub attempt
namespace, fixed authority, no production import before both leases, exact
runtime-path snapshots, immutable Docker seed identity, no-bind/read-only H1A
isolation, append-only receipts, and a final one-attempt/no-retry boundary.
PR #58 also correctly rejects host package downgrade and demands an isolated
Snapshot-root candidate.

## Ranked findings

### P0 — H1A durable lineage is absent from the H1B contract

**Current claim.** PR #58 is the successor of the admitted Docker mechanism.

**Actual evidence.** The RED pins PR #57, the Snapshot and five hashes, but not
the actual H1A audit receipt, post-audit manifest, seed RepoDigest or image ID.

**Strongest failure mode.** A GREEN can use a different tag resolution or a
different H1A run and still satisfy the original eight tests.

**Minimal condition for support.** Bind the exact H1A durable chain and execute
only the admitted digest/image ID.

### P0 — Docker daemon authority/locality is not bound

**Current claim.** H1A is described as a workstation Docker admission.

**Actual evidence.** The CLI/daemon metadata was recorded, but the active
Docker context endpoint and `DOCKER_HOST` authority were not bound.

**Strongest failure mode.** A remote TCP/SSH daemon builds the candidate while
being described as the local workstation isolation boundary.

**Minimal condition for support.** Record `docker context show/inspect`, endpoint
scheme, daemon ID/name/kernel/OS/architecture; admit only local Unix endpoints
unless a separate remote-daemon authority node exists.

### P0 — signed Snapshot provenance is under-specified

**Current claim.** H1B fetches Noble at Snapshot `20250115T120000Z`.

**Actual evidence.** PR #58 asks for the Snapshot URL but does not require
identified archive-keyring bytes, signed `InRelease`, `Packages` hashes or
forbid trust-bypass flags.

**Strongest failure mode.** A reachable but unauthenticated or mixed package
index supplies a plausible rootfs.

**Minimal condition for support.** `gpgv` verification against an identified
Ubuntu archive keyring, exact metadata hashes and all DEB hashes; reject
`trusted=yes` and `--no-check-gpg`.

### P0 — H2 is weaker than the production pre-start/runtime closure

**Current claim.** Five hashes characterize the host-epoch candidate.

**Actual evidence.** The production bridge authenticates Git, `ldd`, `readelf`,
the ELF interpreter, libc and `libgcc_s` in addition to compiler, linker, MPFR
and GMP.

**Strongest failure mode.** H2 passes, Section-0 or the post-lease worker later
fails after the one global attempt is consumed.

**Minimal condition for support.** Pin and verify the full OS/pre-start closure
before H3, H4 or Section-0.

### P1 — H1A external-verifier identity is not transitive

The append-only audit record binds its result and the original receipt chain,
but does not include the verifier source/package identity.  This cannot be
silently repaired retroactively.  Type the limitation, keep H1A's authority
effect at `NONE`, and revalidate all upstream manifests in H1B.

### P1 — rootfs archive identity can be confused with installed-file identity

A tar SHA is transport provenance.  Use a deterministic archive for stable
transport, but make the canonical installed-file/path manifest the authority.

### P1 — builder escape surface is under-specified

The future builder must forbid privileged mode, host bind mounts, Docker-socket
mounts and host namespace sharing.  The download phase may use a non-host
network; final verification must use `network=none`, read-only rootfs,
capability drop and no-new-privileges.

### P2 — package-version closure and mixed epoch risk

Do not downgrade the admitted seed in place.  Construct a fresh root from
signed Snapshot metadata, record every package version/DEB hash, and reject
packages from a different epoch unless explicitly included in a typed closure.

## Corrections applied in this child RED

The new eleven-test contract adds the exact H1A lineage, Docker-context
locality, exact seed execution, signed Snapshot metadata, full runtime closure,
package/installed-file provenance, deterministic transport archive and strict
non-authority boundaries.  It preserves and re-runs the original eight-test
PR #58 RED.

## Residual claim ceiling

```text
H1A durable closeout        PASS
H1B/H2 specification       ADVERSARIALLY STRENGTHENED RED
H1B/H2 implementation      ABSENT
historical rootfs          NOT_BUILT
H3 Rust closure            NOT_RUN
Section-0                  NOT_RUN
global attempt ref         ABSENT
native runtime             NOT_RUN
remaining attempts         1
```
