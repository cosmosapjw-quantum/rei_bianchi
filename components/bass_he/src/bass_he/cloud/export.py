"""Transport-neutral create-only checkpoint segments."""
from dataclasses import dataclass
from typing import Protocol
from pathlib import Path
import hashlib, json, os, tarfile, uuid
@dataclass(frozen=True)
class ProviderReceipt:
    provider: str
    object_id: str
    size: int
    sha256: str
    acknowledged: bool
    restore_verified: bool=False

class ProviderAdapter(Protocol):
    def upload_segment(self,path:Path,expected_digest:str) -> ProviderReceipt: ...

@dataclass(frozen=True)
class ExportReceipt:
    segment: str
    sha256: str
    size: int
    artifacts: int
    provider_uploads: str='NOT_RUN'
    restore: str='NOT_RUN'

def export_checkpoint(store,dest:Path):
    store.reconcile();dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    name='checkpoint-'+uuid.uuid4().hex;stage=dest/(name+'.staging');stage.mkdir()
    snapshot=stage/'controller.sqlite';store.snapshot(snapshot)
    files=[(store.root/'RUN_BINDING.json','RUN_BINDING.json',hashlib.sha256((store.root/'RUN_BINDING.json').read_bytes()).hexdigest())]
    for filename in ('RUN_PROFILE.json','EVENTS.jsonl'):
        path=store.root/filename
        if path.exists():files.append((path,filename,hashlib.sha256(path.read_bytes()).hexdigest()))
    for tid,sha in store.db.execute("SELECT task_id,sha256 FROM tasks WHERE state='COMMITTED' ORDER BY task_id"):
        path=store.root/'results'/tid/'result.json';data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('checkpoint source changed')
        files.append((path,f'results/{tid}/result.json',sha))
    manifest={'schema':'bass_he.checkpoint.v1','binding':store.binding.identity(),'artifacts':[{'path':'controller.sqlite','sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest()},*({'path':arc,'sha256':sha} for _,arc,sha in files)]}
    (stage/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True)+'\n')
    archive=dest/(name+'.tar.gz');partial=dest/(name+'.partial')
    with partial.open('xb') as raw:
        with tarfile.open(fileobj=raw,mode='w:gz') as tar:
            tar.add(snapshot,arcname='controller.sqlite');tar.add(stage/'MANIFEST.json',arcname='MANIFEST.json')
            for path,arc,_ in files:tar.add(path,arcname=arc)
        raw.flush();os.fsync(raw.fileno())
    os.link(partial,archive);partial.unlink()
    fd=os.open(dest,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    data=archive.read_bytes();receipt=ExportReceipt(str(archive),hashlib.sha256(data).hexdigest(),len(data),sum(1 for _,arc,_ in files if arc.startswith('results/')))
    with (dest/(name+'.receipt.json')).open('xb') as f:
        f.write((json.dumps(receipt.__dict__,sort_keys=True)+'\n').encode());f.flush();os.fsync(f.fileno())
    fd=os.open(dest,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    snapshot.unlink();(stage/'MANIFEST.json').unlink();stage.rmdir()
    return receipt
