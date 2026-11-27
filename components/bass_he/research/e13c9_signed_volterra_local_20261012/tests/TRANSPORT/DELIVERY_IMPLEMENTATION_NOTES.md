# E13C9 complete-backup implementation handoff

## Status and owned files

This directory contains the requested transport implementation drafts:

- `restore_transfer.py`: standalone standard-library restore entry point.
- `build_delivery.py`: standard-library build entry point; requires its sibling
  `restore_transfer.py`.
- `test_transfer_controls.py` and `FIXTURE_CONTROLS_AFTER_DOT_FIX/`: the current
  tiny actual-ZIP transport control and its preserved evidence.
- `FIXTURE_CONTROLS/` and `PRE_DOT_PATH_REPAIR/`: the initial control, first
  observed standalone-dot path diagnostic, and pre-repair helper bytes.

No scientific implementation was changed. The actual E13C9 package was not
touched. No production complete archive was built and no E13C8 hydration was
executed by this task. The 170,991,376-byte E13C8 complete ZIP was not repacked.

The current fixture control passed 12 checks in 0.045382042 s. It wrote a 521-byte
ZIP, reconstructed its exact bytes from `.part001` and `.part002.bin`, and
verified its actual extracted payload. The real restore CLI's missing-part
negative control exited **1**, preserving `FIRST_FAILURE.json`; it performed no
extraction, scientific invocation, MPI invocation, or prior-helper invocation.
Unsafe ZIP traversal and standalone `.` paths were rejected. The initial 11
checks passed before an additional source-review diagnostic found that
`PurePosixPath('.')` has empty `parts`; the standalone-dot explicit rejection was
then added and the bounded fixture was run into a new output. Original helper
bytes, the first diagnostic, and both sets of results remain preserved. This is
transport evidence, not production hydration or scientific admission.

## Owner integration and build CLI

After the final scientific review and reports are finished, copy the two helper
files unchanged to the real package's `code/` directory. Its basename must be
exactly:

`BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1`

The package must already include these two dependencies with the stated actual
identities:

| Relative payload path | Bytes | SHA-256 |
|---|---:|---|
| `dependencies/E13C8_COMPLETE.zip` | 170991376 | `ba4b1ace541f52bae5dd096d3da75ca9f0bf2d1894d0c3cba40375e40b1eca80` |
| `dependencies/E13C8_RECOVERY_KIT.zip` | 10727 | `cf25ae33079f21189472cafc40403f066651883b7803c44a6d9e56c6f2f73ed3` |

With `BASS_E13C9_PACKAGE` set to that actual package directory and
`BASS_E13C9_DELIVERY` set to a fresh directory outside it, run once:

```bash
python3 -B "$BASS_E13C9_PACKAGE/code/build_delivery.py" \
  --package "$BASS_E13C9_PACKAGE" \
  --output-dir "$BASS_E13C9_DELIVERY"
```

The command creates the package's `PACKAGE_MANIFEST.json`, a complete ZIP named
from its actual SHA, 64 MiB pieces plus a final smaller piece, the external
`BASS_HE_E13C9_TRANSFER_MANIFEST.json`, and `BUILD_RECEIPT.json`. It checks every
archived payload, including the actual embedded package manifest, before
reporting success. ZIP dependencies are stored without recompression. Generated
`__pycache__` directories and `.pyc`/`.pyo` files are excluded. Other payloads are
included from the actual package tree; symlinks and nonregular files are rejected.

The build refuses an existing root `PACKAGE_MANIFEST.json` or an existing
delivery output. If an attempted build fails after sealing, preserve its
`FIRST_FAILURE.json` and partially produced artifacts; do not silently overwrite
or automatically retry the same package.

## Recovery-kit assembly

The owner's later recovery kit should contain the unchanged new
`restore_transfer.py`, the actual generated external transfer manifest,
`BUILD_RECEIPT.json`, this task's `TRANSPORT_CONTROL_RECEIPT.json`, a concise
`README_KO.md`, the actual uploaded backup locations, and a `KIT_MANIFEST.json`
pinning those kit payloads. A kit archive is intentionally not built here,
because actual complete-archive and part locations are available only after the
owner builds and uploads the completed evidence.

Publish the final kit's actual bytes/SHA and the transfer manifest's actual SHA
in the external NCP handoff. A recipient needs the new kit plus either the
complete ZIP or all matching parts. The new complete ZIP embeds both old E13C8
artifacts, so hydration requires no additional scientific attachment or download.

## Restore CLI

From an extracted new kit, choose one source mode. Supply the manifest SHA from
the published handoff, and choose a fresh output directory.

```bash
python3 -B "$BASS_E13C9_KIT/restore_transfer.py" \
  --manifest "$BASS_E13C9_KIT/BASS_HE_E13C9_TRANSFER_MANIFEST.json" \
  --manifest-sha256 "$BASS_E13C9_PUBLISHED_MANIFEST_SHA256" \
  --archive "$BASS_E13C9_COMPLETE_ZIP" \
  --output-dir "$BASS_E13C9_FRESH_RESTORE" \
  --hydrate
```

Alternatively replace `--archive` with:

```bash
--parts-dir "$BASS_E13C9_DOWNLOADED_PARTS"
```

The parts directory is scanned at one level. Actual size/SHA chooses each part;
`.bin` suffixes and other download-name changes are harmless. Original files
are not renamed, deleted, or overwritten. Identical duplicate downloads are
resolved deterministically and recorded. Manifest order determines concatenation,
and the complete archive hash independently checks the reconstruction.

After restoration:

- New package: `<output>/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1`.
- Nested E13C8 output: `<output>/runtime/E13C8`.
- Old original input and completed heavy return: under that nested output's
  `runtime/E13C7_INPUT` and `runtime/E13C7_NCP_RETURN` directories.
- New success receipt: `<output>/RESTORE_RECEIPT.json`.
- The one old-helper invocation's stdout/stderr are preserved at the new output
  root, with its actual return code and nested receipt recorded.

Omitting `--hydrate` verifies/extracts every new outer payload but leaves the old
ZIP dependencies unexpanded. It does not skip their payload identity checks.

## Verification and provenance constraints

The new helper fixes the E13C9 package root/schema and both old dependency
identities. It verifies the external transfer manifest and its own actual bytes,
then verifies complete archive identity before extraction. Embedded manifests
must match the exact ZIP member set; duplicate JSON keys, duplicate ZIP members,
traversal, noncanonical paths, symlinks/nonregular members, encryption, excessive
member counts, and unexpected expansion are rejected. Limits are 50,000 members,
2 GiB expanded bytes per extraction, and 16 MiB per embedded manifest.

`--hydrate` safely extracts the byte-verified old kit and then verifies:

- old helper: 9,177 bytes,
  `d061629aa3c689b0f7fd0d70cd14c01946ec688bc0ed8e91c48eaaffee6f1343`;
- old transfer manifest: 2,170 bytes,
  `dd62793a79f35aa4b8358cece38ac02517e75db4b32c45f26b890210b19594b1`.

It invokes that helper once through the current Python executable with `-B`,
`--archive` pointing at the actual embedded E13C8 complete ZIP, a new nested
output, and `--hydrate`. It requires the returned receipt's success status and
zero scientific/MPI/retry counts. It does not import numerical project modules
or invoke any NCP execution entry point.

The caller must obtain the expected helper/kit and manifest hashes through the
published handoff. Recomputing a hash from an untrusted download alone does not
establish its authority. Matching hashes establish byte identity; they do not
establish NCP provider attestation, execution-host provenance, scientific validity,
or new-job authorization. The builder leaves scientific admission to the
independent decision included in the package; it does not fabricate a PROMOTE
status.

All outputs require fresh destinations and all actual restore failures preserve
`FIRST_FAILURE.json`. There is no automatic retry. The expected missing-part
failure retained in the fixture directory is a deliberate negative control,
not a failed production restoration.
