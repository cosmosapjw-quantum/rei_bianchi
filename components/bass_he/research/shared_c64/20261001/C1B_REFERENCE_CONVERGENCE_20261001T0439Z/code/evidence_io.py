"""Create-only atomic evidence and exact content identities."""
from pathlib import Path
import json,os,tempfile,hashlib

def atomic_bytes(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)
        dfd=os.open(path.parent,os.O_DIRECTORY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:os.unlink(tmp)

def atomic_json(path,data):atomic_bytes(path,(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
