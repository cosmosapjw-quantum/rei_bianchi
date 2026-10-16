#!/usr/bin/env python3
"""Validate actual immutable owner-source Git blobs, no Git repository required."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'contracts/SOURCE_IDENTITY.json').read_text())
for row in d['files']:
    file=row['file']
    base='source_metadata' if file == 'deuterium_thermal_coupling.rs' else 'rust/rei_iso_eos_reference/owner_src'
    data=(root/base/file).read_bytes()
    git=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    assert git==row['owner_git_blob_sha'] and hashlib.sha256(data).hexdigest()==row['sha256'], file
print(f'SOURCE_IDENTITY_VERIFIED {len(d["files"])} owner blobs')
