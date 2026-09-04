# REI 03A4 Host-Epoch Adversarial RED-2

## Exact parent

```text
repository  cosmosapjw-quantum/rei_bianchi
parent PR   #58
parent head 673083e59b4c869421847cb750093f564d00fa03
parent tree f14d29a7c327972ee9f7ca83755b5a811683e21c
```

PR #58 correctly requires a Docker-backed isolated Snapshot root instead of
mutating the interactive host.  This second RED preserves that contract and
adds the missing evidence and runtime-closure predicates found by a hostile
review after H1A actually passed.

## Newly available H1A evidence

```text
operation status
PASS_REI_03A4_H1A_DOCKER_ADMISSION

independent audit status
PASS_H1A_DOCKER_ADMISSION_INDEPENDENT_AUDIT

durable closeout status
PASS_H1A_DURABLE_AUDIT_CLOSEOUT

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

These records admit Docker as an isolation mechanism only.  They do not prove
a historical package epoch, Section-0 equality, or runtime authorization.
The external verifier source was not itself transitively hashed into the
operator's audit JSON; the successor must type this limitation and independently
revalidate the upstream manifests rather than pretending it does not exist.

## Strongest newly exposed failure modes

### P0 — unbound H1A successor

A future H1B script could satisfy PR #58 while using a different `ubuntu:24.04`
tag resolution, a different Docker daemon, or an unaudited H1A run.  It must
bind the exact durable H1A audit and exact seed digest/image ID.

### P0 — remote Docker daemon masquerading as workstation isolation

`docker` CLI availability does not prove that the daemon is local.  `DOCKER_HOST`
or the active Docker context may select TCP or SSH authority.  H1B must record
and validate the active context, endpoint, daemon identity, operating system,
architecture and kernel, and reject remote-daemon schemes unless a separate
explicit authority node admits them.

### P0 — unsigned or under-recorded Snapshot construction

Snapshot reachability is not archive trust.  H1B/H2 must verify signed
`InRelease` metadata with an identified Ubuntu archive keyring, record the
relevant `Packages` hashes and every downloaded DEB SHA-256, and forbid
`trusted=yes` and `--no-check-gpg` shortcuts.

### P0 — incomplete runtime closure

The PR #58 lock covers only compiler, linker, Python, MPFR and GMP.  The actual
production bridge additionally authenticates Git, `ldd`, `readelf`, the ELF
interpreter, libc and `libgcc_s`.  A candidate root cannot be called a runtime
host epoch until all of these canonical paths and bytes match.

### P1 — transport archive confused with installed-file authority

A rootfs tar hash is useful transport identity but does not replace a canonical
installed-file manifest.  H1B must make its transport archive deterministic,
give that archive `authority_effect=NONE`, and use canonical path plus
installed-file SHA-256 records as the load-bearing evidence.

## Required GREEN additions

The future package under

```text
handoff/rei_runtime_host_epoch_docker_bootstrap_20260904/
```

must satisfy both the original eight PR #58 obligations and the eleven new
obligations in

```text
tests/governance/
test_rei_runtime_03a4_host_epoch_lineage_closure_red.py
```

The combined minimum includes:

1. exact H1A durable chain and exact immutable seed;
2. local Unix Docker context/daemon attestation;
3. exact digest execution with `--pull never` and `linux/amd64`;
4. no host bind, Docker socket, privileged mode or host namespaces;
5. signed Snapshot metadata and package-index provenance;
6. deterministic transport archive plus authoritative installed-file manifest;
7. full OS/pre-start runtime closure;
8. no Rust H3, Section-0, lease, controller, native or scientific promotion.

## Claim ceiling

```text
PR57 path-binding source                PASS
PR58 Docker-bootstrap contract          PASS_EXPECTED_RED
H1A Docker admission                    PASS
H1A durable independent-audit closeout  PASS
H1B/H2 implementation                   ABSENT
historical rootfs                       NOT_BUILT
full runtime closure                    NOT_ATTESTED
H3 Rust closure                         NOT_RUN
successor Section-0                     NOT_RUN
global attempt ref                      ABSENT
remaining native attempts               1
native runtime                           NOT_RUN
scientific pass                          NOT_CLAIMED
```
