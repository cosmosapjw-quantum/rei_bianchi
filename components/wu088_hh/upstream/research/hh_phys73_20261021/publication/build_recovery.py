#!/usr/bin/env python3
"""Build a hash-verified research recovery subset after Git publication.

The result is explicitly not a Git clone. No scientific kernel or upload runs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

UNIT=Path(__file__).resolve().parents[1]
ROOT=UNIT.parents[1]
sys.path.insert(0,str(UNIT/'implementation'))
from ncp_batch import source_binding


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--source-commit',required=True)
    p.add_argument('--metadata-head',required=True)
    p.add_argument('--pr',type=int,required=True)
    a=p.parse_args()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head!=a.metadata_head:raise ValueError('metadata HEAD differs from current real checkout')
    subprocess.run(['git','merge-base','--is-ancestor',a.source_commit,head],cwd=ROOT,check=True)
    binding=source_binding()
    paths=set(binding['files_sha256'])
    tracked=subprocess.check_output(['git','ls-files','-z',str(UNIT.relative_to(ROOT))],cwd=ROOT).split(b'\0')
    paths.update(x.decode() for x in tracked if x)
    p72=ROOT/'research/hh_phys72_20261020'
    paths.update(str(x.relative_to(ROOT)) for x in (p72/'theory').glob('*') if x.is_file())
    for name in ('REPORT_KO.md','NEXT_DAG.json','CONTRACT.json'):
        paths.add(str((p72/name).relative_to(ROOT)))
    tree=subprocess.check_output(['git','ls-tree','-r','-z',head,'--',*sorted(paths)],cwd=ROOT)
    blobs={}
    for item in tree.split(b'\0'):
        if not item:continue
        meta,name=item.split(b'\t',1);mode,typ,oid=meta.decode().split()
        if typ!='blob':raise ValueError('ordinary Git blobs required')
        blobs[name.decode()]=oid
    if set(blobs)!=paths:raise ValueError('recovery member is not tracked at actual HEAD')
    pins={}
    for name in sorted(paths):
        path=ROOT/name
        if path.is_symlink():raise ValueError('recovery source symlink refused')
        data=path.read_bytes()
        oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if oid!=blobs[name]:raise ValueError('working bytes differ from actual Git tree: '+name)
        pins[name]=hashlib.sha256(data).hexdigest()
    manifest=dict(schema='PHYS73_RECOVERY_MANIFEST_V1',created_utc=datetime.now(timezone.utc).isoformat(),
                  repository='cosmosapjw-quantum/WU088_HH',PR=a.pr,source_commit=a.source_commit,
                  metadata_head=head,parent=binding['parent'],full_git_clone=False,
                  files_sha256=pins,git_blob_sha1=blobs,
                  restore='Acquire the pinned full Git clone, then read this subset; no .git is supplied.',
                  no_new_scientific_executions=True,HH_R10='OFF')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.out,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in sorted(paths):archive.write(ROOT/name,name)
        archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    with zipfile.ZipFile(a.out) as archive:
        if set(archive.namelist())!=paths|{'MANIFEST.json'}:raise ValueError('ZIP membership differs')
        for name,expected in pins.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=expected:
                raise ValueError('ZIP content differs: '+name)
    result=dict(status='RECOVERY_ARCHIVED_ALL_PAYLOADS_AND_GIT_BLOBS_VERIFIED',
                archive=str(a.out.resolve()),sha256=hashlib.sha256(a.out.read_bytes()).hexdigest(),
                bytes=a.out.stat().st_size,manifest_payloads=len(paths),metadata_head=head,
                source_commit=a.source_commit,full_git_clone=False)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
