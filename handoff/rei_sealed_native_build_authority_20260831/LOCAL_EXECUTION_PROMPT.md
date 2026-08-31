# Sealed native build-authority supplement handoff

This package is an **opaque byte-identity supplement**, not a runnable SDK and
not a scientific result.  Its only admissible success claim is that the
externally pinned manifest and every declared regular-file/symbolic-link member
match.  It does not by itself establish a complete native closure or discharge
the fresh-process boundary.

## Preconditions

1. Continue from the exact draft-PR head and tree named by the active handoff.
   A user-reported local checkpoint that is unavailable here is not
   byte-identically reconstructed.
2. Complete the immutable Git checks and verify the five separately supplied
   `project_sources` bytes against `INPUT_LOCK.json` before using this
   supplement.
3. Obtain the supplement archive SHA-256 and the extracted
   `AUTHORITY_MANIFEST.json` SHA-256 from an external delivery receipt.  Values
   stored only inside the archive are self-attested and cannot pin the archive.
4. Extract into a new, empty, non-symlink directory with the supplied safe
   extractor.  Do not use `tar -x`, an archive-manager GUI, or any generic
   unpacker, and do not execute any member.

## Safe archive extraction

The archive SHA-256 is an external argument, never a value read from inside the
archive.  Use a destination that is absent or an empty real directory:

```bash
/usr/bin/python3 -I -S -B \
  handoff/rei_sealed_native_build_authority_20260831/extract_bundle.py \
  --archive /absolute/delivery/REI_SEALED_BUILD_DRIVER_AUTHORITY_20260831.v2.tar.xz \
  --destination /absolute/new/extraction-container \
  --expected-archive-sha256 EXTERNALLY_RECORDED_ARCHIVE_SHA256 \
  > /absolute/evidence/native-authority-extraction-receipt.json
```

`extract_bundle.py` is standard-library-only.  Before creating the destination
it validates every TAR member and rejects absolute/member-traversal paths,
extra roots, duplicate members, undeclared parents, hard links, sparse or
unknown types, devices, FIFOs, and any member with a symbolic-link ancestor.
It accepts only directories, ordinary regular files, and symbolic links whose
custom logical-rootfs resolution terminates at a declared member.  Directories
and files are created with descriptor-relative, no-follow, create-only calls;
links are created last and are never followed.  The same already-open archive
descriptor is SHA-256 rehashed after extraction and its inode/size/timestamp
fingerprint is compared before and after, so in-place archive mutation fails
closed.

Absolute link target text such as `/usr/bin/gcc` is authority topology and is
therefore preserved.  The extractor interprets it as rooted at the packaged
logical `rootfs` only for graph validation.  On the host filesystem that link
text can resolve outside the extraction directory.  Consequently no process
may traverse, import, dynamically load, or execute extracted members at this
stage; use only `lstat`, `readlink`, and the supplied logical verifier.

An extraction I/O failure can leave a partial destination deliberately for
forensic inspection.  Do not overwrite or reuse it; preserve it and retry with
a different absent or empty destination.

## Opaque intake verification

Run the verifier as a non-load-bearing intake action.  It imports no repository
package and executes no bundled member:

```bash
/usr/bin/python3 -I -S -B \
  handoff/rei_sealed_native_build_authority_20260831/verify_bundle.py \
  --bundle-root /absolute/new/extraction-container/REI_SEALED_NATIVE_BUILD_AUTHORITY_20260831 \
  --expected-manifest-sha256 EXTERNALLY_RECORDED_SHA256
```

It fails closed on manifest drift, missing/extra members, special files,
symlink parents, link cycles, undeclared link terminals, wrong modes or sizes,
and byte mismatches.  Preserve its single-line JSON output as an intake
receipt.  A PASS has classification
`BYTE_IDENTITY_NON_SCIENTIFIC_AUTHORITY_SUPPLEMENT`.
`AUTHORITY_MANIFEST.schema.json` is an informational structural reference;
the dependency-free checks in `verify_bundle.py` are the normative admission
logic and the script pins the canonical `CONTRACT.json` digest internally.
The result is point-in-time evidence. Run in an exclusive tree with no
concurrent writer. The verifier detects mutation of an opened inode while it
is hashed, but it does not provide kernel-enforced pathname immutability after
that descriptor closes.

## Non-executable mount plan

After opaque verification, the following command may render a JSON argv
fragment.  It **does not invoke `bwrap`**:

```bash
/usr/bin/python3 -I -S -B \
  handoff/rei_sealed_native_build_authority_20260831/render_bwrap_mount_plan.py \
  --bundle-root /absolute/new/extraction-container/REI_SEALED_NATIVE_BUILD_AUTHORITY_20260831 \
  --expected-manifest-sha256 EXTERNALLY_RECORDED_SHA256 \
  > /absolute/evidence/native-authority-bwrap-fragment.json
```

The fragment starts from an empty tmpfs root, creates only declared parent
directories, read-only binds regular members at their original absolute
rootfs paths, and recreates literal symbolic links.  Do not concatenate this
fragment into a command until all `required_external_plan_fields` are replaced
with exact byte-pinned mounts and policies.  In particular, pin `bwrap` itself,
the child executable and ELF interpreter, all dynamic libraries, repository
and input roots, output root, and `/proc`/`/dev` policy.  Never bind the host
root or a broad host `/usr`, `/lib`, `/etc`, or workspace into the empty root.
Before any launch, the future policy must remove writer access to every source
tree, repeat final verification under that kernel policy, and preserve the
read-only binding through child exit.

## Gate boundary

This handoff deliberately leaves all execution gates unchanged:

```text
runtime_boundary   NOT_RUN
build              NOT_RUN
native_tests       NOT_RUN
adapter            STOP_INVALID
canonical_pilot    NOT_RUN
first_interval     NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass    NOT_CLAIMED
scientific_publication NOT_RUN
```

Only after an independently reviewed complete mount plan installs its
kernel-mediated allowlist before the child starts may the existing Section 5
fresh-process gate be attempted.  A verifier PASS, a rendered plan, matching
`cc`/`ld` hashes, or a successful dynamic load cannot be promoted to a runtime,
operator, canonical, or scientific claim.
