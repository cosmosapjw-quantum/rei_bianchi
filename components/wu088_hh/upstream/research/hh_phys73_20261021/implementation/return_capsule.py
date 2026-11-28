"""Create and read back an immutable current-host result capsule.

No upload is performed. A capsule contains the bound source subset, all current
result/log files and a complete SHA256 manifest. It is not a full Git clone.
The caller holds the batch lock and has joined all of its scientific children.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import uuid
import zipfile


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def publish_new(path,payload):
    """Atomic no-replace JSON publication, including under interruption."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temp.open('x') as stream:
            json.dump(payload,stream,indent=2,sort_keys=True,allow_nan=False)
            stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.link(temp,path)
    finally:
        temp.unlink(missing_ok=True)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def verify_capsule(path):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):
            raise ValueError('duplicate ZIP member')
        manifest=json.loads(archive.read('MANIFEST.json'))
        pins=manifest['files_sha256']
        if manifest.get('schema')!='PHYS73_CURRENT_HOST_RETURN_MANIFEST_V1':
            raise ValueError('unexpected capsule schema')
        if set(names)!=set(pins)|{'MANIFEST.json'}:
            raise ValueError('capsule membership differs')
        for name,expected in pins.items():
            part=PurePosixPath(name)
            if part.is_absolute() or '..' in part.parts or '\\' in name:
                raise ValueError('unsafe capsule member')
            h=hashlib.sha256()
            with archive.open(name) as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''):
                    h.update(chunk)
            if h.hexdigest()!=expected:
                raise ValueError('capsule payload hash differs: '+name)
    return manifest


def pack_return(out,repository,identity,invocation_id,result_path):
    if Path(out).is_symlink():raise ValueError('capsule output symlink refused')
    out,repository=Path(out).resolve(),Path(repository).resolve()
    if not invocation_id or any(c not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-' for c in invocation_id):
        raise ValueError('safe invocation ID required')
    if not Path(result_path).resolve().is_relative_to(out) or not Path(result_path).is_file():
        raise ValueError('completed local result receipt required')
    payloads={};excluded=[]
    for relative,expected in identity['files_sha256'].items():
        source=repository/relative
        if source.is_symlink() or not source.resolve().is_relative_to(repository) or sha(source)!=expected:
            raise ValueError('bound source changed before packing: '+relative)
        payloads['source/'+relative]=source
    # Enumerate only these owned locations; never recursively include old ZIPs.
    candidates=[out/'IDENTITY.json']
    for directory in ('work','jobs','invocations'):
        base=out/directory
        if base.is_symlink():raise ValueError('result directory symlink refused')
        if base.exists():candidates.extend(sorted(base.rglob('*')))
    for path in candidates:
        if path.is_symlink():raise ValueError('result symlink refused')
        if not path.is_file():continue
        relative=str(path.relative_to(out))
        if path.suffix in ('.lock','.tmp') or '__pycache__' in path.parts:
            excluded.append(relative);continue
        payloads['results/'+relative]=path
    pins={name:sha(path) for name,path in sorted(payloads.items())}
    manifest=dict(schema='PHYS73_CURRENT_HOST_RETURN_MANIFEST_V1',
                  created_utc=datetime.now(timezone.utc).isoformat(),invocation_id=invocation_id,
                  source_head=identity['source_head'],parent=identity['parent'],
                  full_git_clone=False,files_sha256=pins,excluded_transient_files=excluded,
                  scientific_status='READ_RESULT_RECEIPT_EACH_JOB_SEPARATELY',
                  external_upload_performed=False,HH_R10='OFF')
    folder=out/'archives'
    if folder.is_symlink() or not folder.resolve().is_relative_to(out):
        raise ValueError('archive directory symlink or escape refused')
    folder.mkdir(exist_ok=True)
    target=folder/('PHYS73_NCP_RETURN_'+invocation_id+'.zip')
    temporary=target.with_name('.'+target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with zipfile.ZipFile(temporary,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for name,path in sorted(payloads.items()):archive.write(path,name)
            archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        checked=verify_capsule(temporary)
        with temporary.open('rb') as stream:os.fsync(stream.fileno())
        os.link(temporary,target)
    finally:
        temporary.unlink(missing_ok=True)
    receipt=dict(schema='PHYS73_CURRENT_HOST_RETURN_ACK_V1',status='LOCAL_ARCHIVED_VERIFIED',
                 archive=str(target),sha256=sha(target),bytes=target.stat().st_size,
                 manifest_payloads=len(checked['files_sha256']),invocation_id=invocation_id,
                 result_receipt=str(result_path),result_sha256=sha(result_path),
                 external_upload_performed=False,full_git_clone=False,HH_R10='OFF')
    publish_new(folder/(target.stem+'_ACK.json'),receipt)
    return receipt
