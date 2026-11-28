"""Single-writer, hash-chained immutable snapshots on a local POSIX filesystem.

Checksums detect accidental damage, not malicious rewriting or authentication.
A file becomes visible by atomic rename; directory fsync precedes acknowledgement.
The lock is advisory. Power-loss, NFS and noncooperating writers are not certified.
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Callable

class JournalError(RuntimeError):
    """A journal cannot safely be continued without external intervention."""


def canonical(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False).encode('utf-8')


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class Journal:
    def __init__(self, root: Path | str, binding: str):
        if not re.fullmatch(r'[0-9a-f]{64}',binding):
            raise JournalError('INVALID_BINDING')
        self.root=Path(root);self.binding=binding;self.lock=None
        self.seq=-1;self.tip='0'*64;self.last=None;self.poisoned=False
    def __enter__(self):
        if self.root.is_symlink(): raise JournalError('SYMLINK_ROOT')
        self.root.mkdir(parents=True,exist_ok=True)
        fd=os.open(self.root/'writer.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(fd);raise JournalError('WRITER_BUSY') from exc
        self.lock=fd
        try:self.recover()
        except BaseException:
            self.__exit__(None,None,None);raise
        return self
    def __exit__(self,*_):
        if self.lock is not None:
            os.close(self.lock);self.lock=None
    def recover(self) -> dict | None:
        if self.lock is None:raise JournalError('LOCK_REQUIRED')
        self.seq=-1;self.tip='0'*64;self.last=None
        names=sorted(self.root.glob('checkpoint-*.json'))
        for index,path in enumerate(names):
            if path.name!=f'checkpoint-{index:09d}.json':raise JournalError('CHAIN_GAP_OR_NAME')
            if path.is_symlink() or path.stat().st_size>1_048_576:raise JournalError('UNSAFE_RECORD')
            try: envelope=json.loads(path.read_text(encoding='utf-8'))
            except (ValueError,UnicodeError) as exc:raise JournalError('CORRUPT_RECORD') from exc
            if not isinstance(envelope,dict):raise JournalError('CORRUPT_SCHEMA')
            stored=envelope.pop('sha256',None)
            if digest(envelope)!=stored:raise JournalError('CHECKSUM_MISMATCH')
            if (envelope.get('schema')!='bass-he.snapshot.v1'
                or envelope.get('seq')!=index or envelope.get('previous')!=self.tip):
                raise JournalError('CHAIN_MISMATCH')
            if envelope.get('binding')!=self.binding:raise JournalError('BINDING_MISMATCH')
            if not isinstance(envelope.get('payload'),dict):raise JournalError('BAD_PAYLOAD')
            self.seq=index;self.tip=stored;self.last=envelope['payload']
        return self.last
    def commit(self, payload: dict, hook: Callable[[str],None]=lambda _:None) -> str:
        if self.lock is None:raise JournalError('LOCK_REQUIRED')
        if self.poisoned:raise JournalError('REOPEN_AFTER_WRITE_FAILURE')
        if not isinstance(payload,dict):raise JournalError('BAD_PAYLOAD')
        seq=self.seq+1
        obj={'schema':'bass-he.snapshot.v1','seq':seq,'previous':self.tip,
             'binding':self.binding,'payload':payload}
        sha=digest(obj);wire=canonical({**obj,'sha256':sha})+b'\n'
        if len(wire)>1_048_576:raise JournalError('RECORD_TOO_LARGE')
        dest=self.root/f'checkpoint-{seq:09d}.json'
        if dest.exists() or dest.is_symlink():raise JournalError('NO_OVERWRITE')
        try:
            hook('before_write')
            fd,tmp=tempfile.mkstemp(prefix=f'.pending-{seq:09d}-',dir=self.root)
            with os.fdopen(fd,'wb') as f:
                f.write(wire);f.flush();os.fsync(f.fileno())
            hook('after_file_fsync')
            os.replace(tmp,dest)
            hook('after_rename')
            dfd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
            hook('after_dir_fsync')
        except BaseException:
            self.poisoned=True
            raise
        self.seq=seq;self.tip=sha;self.last=payload
        return sha
