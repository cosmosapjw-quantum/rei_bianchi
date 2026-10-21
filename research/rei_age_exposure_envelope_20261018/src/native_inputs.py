"""Reconstruct the unchanged input manifest from its byte-pinned donor archive.

This keeps the Git handoff directly runnable without an additional opaque source
packet. It does not fetch data or change native source or scientific acceptance.
"""
from pathlib import Path
import hashlib
import json
import zipfile

NATIVE='35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
ARCHIVE_SHA='535a4fce4b52660bc3025fdab8e4159cd9a41173f9c1cf1fa0dc524a099de83a'
MANIFEST_SHA='ab90ff29ec8b13b1bf6b31aa075be563d4ceab68f34b7255f107306fc750e4d3'

def load_manifest(root:Path,archive:Path|None=None)->dict:
    existing=root/'contracts/NATIVE_INPUTS.json'
    if existing.is_file():
        raw=existing.read_bytes()
    else:
        archive=archive or root/'donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip'
        data=archive.read_bytes()
        if hashlib.sha256(data).hexdigest()!=ARCHIVE_SHA:
            raise ValueError('ARCHIVE_SHA_MISMATCH')
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:raise ValueError('ARCHIVE_CRC')
            names=sorted(n for n in z.namelist() if n.startswith('native_source/') and not n.endswith('/'))
            files={n[len('native_source/'):]:dict(sha256=hashlib.sha256(z.read(n)).hexdigest(),size=len(z.read(n))) for n in names}
        obj=dict(native_sha=NATIVE,archive_sha256=ARCHIVE_SHA,files=files)
        raw=(json.dumps(obj,indent=2)+'\n').encode()
    if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA:
        raise ValueError('NATIVE_MANIFEST_IDENTITY_MISMATCH')
    return json.loads(raw)
