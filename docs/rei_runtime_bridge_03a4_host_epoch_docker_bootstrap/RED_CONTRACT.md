# REI-RUNTIME-BRIDGE-03A4-HOST-EPOCH-DOCKER-BOOTSTRAP RED

## Observed H0 state

The operator's read-only H0 census produced the following exact state:

```text
release head                 ab1ea23fd8e3ebe17f46d13d5496bb1db3eba08b
release tree                 779c06d1e4bf9c54292ad22030cb1b47906af988
locked GCC DEB SHA-256       7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
locked compiler SHA-256      6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
Rust 1.94.1 SHA-256          ef6d716e5d1c6c93def277c0afa037c21e7a74f7de3aed4ee0700646c3301b1d
H0 manifest                  PASS
host mmdebstrap              ABSENT
host debootstrap             ABSENT
Docker                       AVAILABLE
global attempt ref           NOT_CREATED
persistent local lease       NOT_CREATED
native runtime               NOT_RUN
remaining native attempts    1
```

`STOP_HOST_EPOCH_H0_PREREQUISITE_INCOMPLETE` therefore identifies one
missing host-side bootstrap program. It does not invalidate the immutable
inputs and does not prove that isolated reconstruction is impossible.

## P0 failure mode

Installing or downgrading host packages would violate the frozen safety
boundary. Treating an extracted GCC at an alternate host path as the runtime
witness would violate the path-binding GREEN. Conversely, stopping solely
because host `debootstrap` is absent ignores the already available Docker
isolation backend.

## Required successor

The smallest admissible successor must:

1. run `debootstrap` only inside a disposable builder container;
2. fetch Ubuntu Noble from Snapshot `20250115T120000Z`;
3. persist a rootfs archive outside every Git worktree and attempt-state root;
4. import that archive as a temporary image;
5. verify it with no network, a read-only root filesystem, all capabilities
   dropped, and `no-new-privileges`;
6. require exact canonical-path resolution and H2 file hashes;
7. record the builder image identity but give it `authority_effect=NONE`;
8. remove the temporary verification image;
9. create no Section-0 receipt, global ref, lease, dispatch, outcome, native
   result, provider state, or scientific claim.

## Intentional RED

`tests/governance/test_rei_runtime_03a4_host_epoch_docker_bootstrap_red.py`
contains eight obligations. At this RED head all eight fail by assertion and
none may execute Docker or the REI runtime.

```text
expected tests       8
expected failures    8
expected errors      0
claim ceiling        PASS_EXPECTED_RED_ONLY
```
