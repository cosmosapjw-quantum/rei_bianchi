# Full-history archive branch

Each archive-only artifact is split into files below 45 MiB. Reassemble one artifact with:

```bash
python scripts/reassemble_artifact.py artifacts/full-history/<artifact>.parts/parts_manifest.json /desired/output/dir
```

`ARCHIVE_INDEX.json` lists all archive-only payloads. The B2C2B0C-R1 full artifact was reconstructed after its original ZIP disappeared from the active artifact store; its 689 manifest-listed files were verified individually by SHA-256.
