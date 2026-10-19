#!/usr/bin/env python3
"""Restore the exact reactive01 artifact from either recorded cloud backup.
No network calls or source execution. The caller supplies the downloaded ZIP.
"""
import argparse, hashlib, zipfile
from pathlib import Path, PurePosixPath
EXPECTED='84805302269e729bf38d674cdf77f373cb78c8b31125536c2aa7281f9f7a45fd'
def restore(archive: Path, destination: Path) -> None:
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError('wrong parent archive; do not substitute similarly named S10 or intake')
    if destination.exists(): raise FileExistsError(destination)
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist())!=174: raise ValueError('member count')
        for member in z.infolist():
            p=PurePosixPath(member.filename)
            if p.is_absolute() or '..' in p.parts: raise ValueError('unsafe member')
            if (member.external_attr >> 16) & 0o170000 == 0o120000: raise ValueError('symlink')
        z.extractall(destination)
    root=destination/'REI_BASS_REACTIVE01_NATIVE_20261018'
    checked=0
    for line in (root/'manifest.sha256').read_text().splitlines():
        if not line.strip(): continue
        sha, name=line.split(maxsplit=1); name=name.lstrip('*')
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts: raise ValueError('unsafe manifest path')
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha: raise ValueError(name)
        checked+=1
    if checked!=173: raise ValueError('manifest count')
    print('EXACT_PARENT_RESTORED',root,'payloads',checked)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('destination',type=Path)
    a=p.parse_args();restore(a.archive,a.destination)
