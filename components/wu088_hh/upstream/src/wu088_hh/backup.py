"""Parallel provider transport, strict two-provider raw readback before any ACK."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,subprocess,tempfile,time
from pathlib import Path


def digest(path:Path)->tuple[str,int]:
    h=hashlib.sha256();size=0
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
    return h.hexdigest(),size


def dual_backup(source:Path,destinations:dict,receipt_path:Path,*,rclone_bin:str='rclone')->dict:
    source=Path(source).resolve();receipt_path=Path(receipt_path)
    if not source.is_file():raise FileNotFoundError(source)
    if receipt_path.exists():raise FileExistsError('use a new detached receipt path')
    if set(destinations)!={'google_drive','dropbox'}:raise ValueError('two named providers required')
    listing=subprocess.run([rclone_bin,'listremotes','--long'],capture_output=True,text=True,timeout=30)
    if listing.returncode:raise RuntimeError('cannot verify rclone provider types')
    types={fields[0].rstrip(':'):fields[1] for line in listing.stdout.splitlines() if len(fields:=line.split())>=2}
    for provider,kind in [('google_drive','drive'),('dropbox','dropbox')]:
        remote=destinations[provider]
        if ':' not in remote or types.get(remote.split(':',1)[0])!=kind:
            raise ValueError(f'wrong or unresolved provider type: {provider}')
    sha,size=digest(source);start=time.monotonic()
    def transfer(item):
        provider,target=item;begin=time.monotonic()
        entry=dict(destination=target,provider_type='drive' if provider=='google_drive' else 'dropbox',
                   status='FAILED_OR_UNVERIFIED',new_object_creation_claimed=False)
        try:
            cpstart=time.monotonic()
            cp=subprocess.run([rclone_bin,'copyto','--immutable',str(source),target],capture_output=True,text=True,timeout=300)
            entry.update(copy_returncode=cp.returncode,copy_wall_s=time.monotonic()-cpstart)
            if cp.returncode:raise RuntimeError(f'copyto exit={cp.returncode}: {cp.stderr[-1500:]}')
            rbstart=time.monotonic()
            with tempfile.TemporaryFile() as raw:
                result=subprocess.run([rclone_bin,'cat',target],stdout=raw,stderr=subprocess.PIPE,timeout=300)
                if result.returncode:raise RuntimeError(f'cat exit={result.returncode}: {result.stderr[-1500:].decode(errors="replace")}')
                raw.seek(0);h=hashlib.sha256();n=0
                for block in iter(lambda:raw.read(1024*1024),b''):h.update(block);n+=len(block)
            entry.update(readback_wall_s=time.monotonic()-rbstart,sha256=h.hexdigest(),bytes=n)
            if (h.hexdigest(),n)!=(sha,size):raise RuntimeError('raw SHA-256/size mismatch')
            entry['status']='REMOTE_OBJECT_PRESENT_RAW_READBACK_VERIFIED'
        except Exception as exc:
            entry.update(status='FAILED_OR_UNVERIFIED',error=str(exc))
        entry['provider_wall_s']=time.monotonic()-begin
        return provider,entry
    with ThreadPoolExecutor(max_workers=2) as pool:
        providers=dict(pool.map(transfer,destinations.items()))
    unchanged=digest(source)==(sha,size)
    ok=unchanged and all(x['status']=='REMOTE_OBJECT_PRESENT_RAW_READBACK_VERIFIED' for x in providers.values())
    receipt=dict(schema='WU088_PARALLEL_DUAL_RAW_BACKUP_V1',source_name=source.name,source_sha256=sha,
        source_bytes=size,source_unchanged=unchanged,providers=providers,wall_s=time.monotonic()-start,
        dual_raw_readback_verified=ok,status='DUAL_RAW_READBACK_VERIFIED' if ok else 'BLOCKED_BACKUP_INCOMPLETE',
        scientific_validation_performed=False,ack_recorded=False)
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    with receipt_path.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n');f.flush()
    return receipt
