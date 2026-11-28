#!/usr/bin/env python3
"""Restore the complete E13C7 ZIP by actual bytes, independent of its filename."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile

ROOT_NAME = 'BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
EXEC_SHA = 'c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4'

def digest_stream(stream):
    size=0;h=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):
        size+=len(block);h.update(block)
    return {'bytes':size,'sha256':h.hexdigest()}

def digest_file(path):
    with path.open('rb') as f:
        return digest_stream(f)

def require(condition,message):
    if not condition:
        raise ValueError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--bytes',type=int,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--staging',type=Path,required=True)
    a=p.parse_args();archive=a.archive.resolve();stage=a.staging.resolve()
    require(digest_file(archive)=={'bytes':a.bytes,'sha256':a.sha256},'actual archive bytes/SHA mismatch')
    require(not stage.exists(),'staging must be a fresh nonexistent path')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist();names=[i.filename for i in infos]
        require(len(names)==len(set(names)),'duplicate ZIP member')
        for i in infos:
            n=i.filename;q=PurePosixPath(n)
            require(not q.is_absolute() and '\\' not in n and '..' not in q.parts and q.as_posix()==n,'unsafe ZIP path')
            require(q.parts and q.parts[0]==ROOT_NAME and len(q.parts)>1,'wrong package root')
            require(not i.is_dir() and stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG),'nonregular ZIP member')
            require(not (i.flag_bits&1),'encrypted ZIP member')
        manifest_name=ROOT_NAME+'/PACKAGE_MANIFEST.json'
        manifest_bytes=z.read(manifest_name);manifest=json.loads(manifest_bytes)
        require(manifest['schema']=='bass-he-e13c7-package-manifest-v1','manifest schema mismatch')
        files=manifest['files']
        expected={ROOT_NAME+'/'+name for name in files}|{manifest_name}
        require(set(names)==expected,'ZIP and manifest coverage mismatch')
        for name,pin in files.items():
            require(set(pin)=={'bytes','sha256'},'unexpected manifest identity fields')
            with z.open(ROOT_NAME+'/'+name) as f:
                require(digest_stream(f)==pin,'decompressed member identity mismatch: '+name)
        require(files['EXECUTION_LOCK.json']=={'bytes':10078,'sha256':EXEC_SHA},'wrong final execution lock')
        stage.mkdir(parents=True,exist_ok=False)
        root=stage/ROOT_NAME
        for name in names:
            dest=stage.joinpath(*PurePosixPath(name).parts)
            dest.parent.mkdir(parents=True,exist_ok=True)
            with z.open(name) as src,dest.open('xb') as dst:
                for block in iter(lambda:src.read(1024*1024),b''):
                    dst.write(block)
                dst.flush();os.fsync(dst.fileno())
        for name,pin in files.items():
            require(digest_file(root/name)==pin,'restored file identity mismatch: '+name)
        require((root/'PACKAGE_MANIFEST.json').read_bytes()==manifest_bytes,'restored manifest bytes mismatch')
    receipt={'status':'PASS_ACTUAL_ZIP_AND_RESTORED_MEMBER_BYTES','archive':str(archive),
        'archive_identity':{'bytes':a.bytes,'sha256':a.sha256},'root':str(root),
        'payload_files_verified':len(files),'zip_members_verified':len(names),
        'execution_lock_sha256':EXEC_SHA,'scientific_kernel_invocations':0,'MPI_invocations':0,
        'download_filename_not_used_as_identity':True}
    with (stage/'RESTORE_RECEIPT.json').open('x') as f:
        json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(receipt,sort_keys=True),flush=True)

if __name__=='__main__':
    main()
