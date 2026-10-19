# Lossless Git transport for the two historical archive files

The GitHub connector rejects request bodies larger than 16 MiB. The original
RUN09 and RUN11 ZIP files are therefore carried as five raw parts of at most
8 MiB each. This is byte transport only: no source, numerical result, ZIP member,
compression stream or archived manifest is reconstructed or changed.

`MANIFEST.json` identifies each part by byte offset, byte count, SHA-256 and Git
blob SHA-1, and records the same identities for each complete original ZIP.

| Restored target under `run13/recovered/` | Original bytes | Parts |
|---|---:|---:|
| `provenance/RUN09.zip` | 14,407,737 | 2 |
| `provenance/RUN11.zip` | 17,968,344 | 3 |

From a Git checkout containing this transport directory, restore the two files:

```bash
python3 research/atomic_nuclear_ssot_20261017/run13/git_transport/restore.py \
  --destination-root research/atomic_nuclear_ssot_20261017/run13/recovered
```

The helper validates every part, the concatenated complete SHA-256 and Git blob
SHA-1, and all existing targets before creating any file. A matching target is
accepted without rewriting it. A differing file, symlink target, unsafe path,
missing/corrupt part or noncontiguous part order is rejected. New files are
published atomically with an add-only hard link; an existing destination is never
replaced. `--verify-only` also requires the final target files to exist and match.

The same helper can be reused with another `rei.lossless.git.byte_chunks.v1`
manifest, for example for large RUN14 source packets. Supply `--manifest` and
`--destination-root` explicitly for that use.

## Identity boundary

The physical Git checkout contains 331 original RUN13 files plus this lossless
transport representation of the two large ZIPs. After the helper completes, the
full original 333-file inventory and its 332-entry internal SHA-256 manifest can
be checked byte for byte. A different Git tree layout does not imply changed
scientific bytes; conversely, the presence of parts alone does not establish
successful restoration. The final delivery receipt records actual remote
retrieval, part verification, restoration, original-manifest verification and
rebuild as separate steps.

The raw source ZIP files in the local recovered directory and their historical
commits remain intact. No earlier source or failure record is overwritten.
