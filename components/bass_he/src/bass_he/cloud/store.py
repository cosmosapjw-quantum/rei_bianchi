"""Single-controller immutable result publication and reconciliation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import fcntl, hashlib, json, os, sqlite3, uuid
from .contracts import Attempt, CaseSpec, CaseOutcome, ExecutionBinding, task_id, validate_document

@dataclass(frozen=True)
class CommitReceipt:
    task_id: str
    sha256: str
    path: str

@dataclass(frozen=True)
class RecoveryReport:
    recovered: int
    committed: int

class ResultStore:
    def __init__(self, root: Path, binding: ExecutionBinding):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self._fsync_dir(self.root.parent)
        self.binding=binding
        self._lock=(self.root/'.controller.lock').open('a+b')
        try: fcntl.flock(self._lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('controller already owns run')
        self.db=sqlite3.connect(self.root/'controller.sqlite')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, spec TEXT NOT NULL, state TEXT NOT NULL, number INTEGER NOT NULL, sha256 TEXT, epoch TEXT)')
        self.db.commit()
        bp=self.root/'RUN_BINDING.json'; value=json.dumps(binding.__dict__,sort_keys=True,allow_nan=False)
        if bp.exists():
            if bp.read_text()!=value: raise ValueError('binding mismatch')
        else:
            self._write_exclusive(bp,value.encode())
        self.epoch=None
    @staticmethod
    def _fsync_dir(path):
        fd=os.open(path,os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    def _ensure_dir_durable(self,path):
        missing=[];current=path
        while not current.exists():missing.append(current);current=current.parent
        if current.is_symlink():raise ValueError('symlink directory')
        for directory in reversed(missing):
            directory.mkdir()
            self._fsync_dir(directory.parent)
    def _event(self,typ,**kw):
        with (self.root/'EVENTS.jsonl').open('ab') as f:
            f.write((json.dumps({'type':typ,**kw},sort_keys=True)+'\n').encode());f.flush();os.fsync(f.fileno())
    def _write_exclusive(self,path,data):
        self._ensure_dir_durable(path.parent)
        with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        fd=os.open(path.parent,os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    def begin_epoch(self):
        self.epoch=uuid.uuid4().hex; self._event('EPOCH',epoch=self.epoch);return self.epoch
    def claim(self,spec:CaseSpec,retry_failed=False):
        if not self.epoch: raise RuntimeError('begin_epoch required')
        tid=task_id(spec); self.load(tid)
        row=self.db.execute('SELECT number,state FROM tasks WHERE task_id=?',(tid,)).fetchone()
        if row and row[1]=='COMMITTED': raise FileExistsError(tid)
        if row and row[1]=='FAILED':
            failure=self.failure(tid)
            if not retry_failed or row[0]>=2 or failure.get('status') not in ('TIME_BUDGET_EXCEEDED','WORKER_CRASH','ENVIRONMENT_ERROR'):
                raise RuntimeError('failed case requires explicit operator retry or retry limit reached')
        number=(row[0]+1) if row else 1
        self.db.execute('INSERT OR REPLACE INTO tasks VALUES (?,?,?,?,?,?)',(tid,json.dumps(spec.__dict__,sort_keys=True,allow_nan=False),'STARTED',number,None,self.epoch));self.db.commit()
        self._event('STARTED',task_id=tid,epoch=self.epoch,number=number)
        return Attempt(tid,self.epoch,number)
    def attempt_path(self,attempt):
        p=self.root/'tasks'/attempt.task_id/f'attempt-{attempt.number:04d}'/'prepared.json';self._ensure_dir_durable(p.parent);return p
    def _final(self,tid):return self.root/'results'/tid/'result.json'
    def _validate_file(self,path,spec,attempt):
        if path.is_symlink() or not path.is_file(): raise ValueError('missing or symlink result')
        data=path.read_bytes(); doc=json.loads(data); out=validate_document(doc,spec,self.binding,attempt)
        return out,hashlib.sha256(data).hexdigest()
    def commit(self,attempt:Attempt,prepared_path:Path):
        if attempt.run_epoch!=self.epoch: raise ValueError('stale epoch')
        row=self.db.execute('SELECT spec,state,number,epoch FROM tasks WHERE task_id=?',(attempt.task_id,)).fetchone()
        if not row or row[1]!='STARTED' or row[2]!=attempt.number or row[3]!=attempt.run_epoch: raise ValueError('stale attempt')
        spec=CaseSpec(**json.loads(row[0])); expected=self.attempt_path(attempt).resolve(strict=False); src=Path(prepared_path)
        if src.is_symlink() or any(p.is_symlink() for p in (src.parent,*src.parents)) or src.resolve(strict=True)!=expected or not src.is_file(): raise ValueError('unowned prepared path')
        outcome,sha=self._validate_file(src,spec,attempt)
        dest=self._final(attempt.task_id);self._ensure_dir_durable(dest.parent)
        if dest.exists():
            _,oldsha=self._validate_file(dest,spec,attempt)
            if oldsha!=sha: raise ValueError('conflicting final')
        else:
            if os.stat(src).st_dev!=os.stat(dest.parent).st_dev: raise ValueError('cross-device publication')
            staged=dest.parent/('.publish-'+uuid.uuid4().hex)
            self._write_exclusive(staged,src.read_bytes())
            try: os.link(staged,dest) # create-only atomic publication
            finally: staged.unlink()
            fd=os.open(dest.parent,os.O_DIRECTORY)
            try: os.fsync(fd)
            finally: os.close(fd)
        self.db.execute('UPDATE tasks SET state=?,sha256=? WHERE task_id=?',('COMMITTED',sha,attempt.task_id));self.db.commit()
        self._event('COMMITTED',task_id=attempt.task_id,sha256=sha)
        return CommitReceipt(attempt.task_id,sha,str(dest))
    def load(self,tid):
        row=self.db.execute('SELECT spec,state,sha256,number,epoch FROM tasks WHERE task_id=?',(tid,)).fetchone(); dest=self._final(tid)
        if not row:
            if dest.exists(): raise ValueError('orphan final without specification')
            return None
        spec=CaseSpec(**json.loads(row[0]))
        if not dest.exists():
            if row[1]=='COMMITTED': raise ValueError('committed result missing')
            return None
        outcome,sha=self._validate_file(dest,spec,Attempt(tid,row[4],row[3]))
        if row[2] and row[2]!=sha: raise ValueError('tampered payload')
        if row[1]!='COMMITTED':
            self.db.execute('UPDATE tasks SET state=?,sha256=? WHERE task_id=?',('COMMITTED',sha,tid));self.db.commit();self._event('RECOVERED',task_id=tid,sha256=sha)
        return outcome
    def reconcile(self):
        recovered=0;committed=0
        for tid,state in self.db.execute('SELECT task_id,state FROM tasks').fetchall():
            self.load(tid)
            if state=='COMMITTED': committed+=1
            elif self._final(tid).exists(): recovered+=1
        return RecoveryReport(recovered,committed)
    def failure(self,tid):
        row=self.db.execute('SELECT state FROM tasks WHERE task_id=?',(tid,)).fetchone()
        if not row or row[0]!='FAILED':return None
        for line in reversed((self.root/'EVENTS.jsonl').read_text().splitlines()):
            event=json.loads(line)
            if event.get('type')=='FAILED' and event.get('task_id')==tid:return event['evidence']
        return {'status':'FAILED','reason':'failure event missing'}
    def record_failure(self,attempt:Attempt,evidence:dict):
        if attempt.run_epoch!=self.epoch: raise ValueError('stale epoch')
        self.db.execute('UPDATE tasks SET state=? WHERE task_id=? AND epoch=?',('FAILED',attempt.task_id,attempt.run_epoch));self.db.commit()
        self._event('FAILED',task_id=attempt.task_id,epoch=attempt.run_epoch,evidence=evidence)
    def snapshot(self,dest:Path):
        target=sqlite3.connect(dest)
        try:self.db.backup(target)
        finally:target.close()
    def close(self):
        self.db.close();fcntl.flock(self._lock,fcntl.LOCK_UN);self._lock.close()
