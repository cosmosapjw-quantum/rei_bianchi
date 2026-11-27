"""Explicit content-verified reuse across runner-only bindings."""
import hashlib, json, sqlite3
from pathlib import Path
from .contracts import (Attempt, CaseSpec, ExecutionBinding, outcome_document,
                        task_id, validate_document)
from .runtime import SCIENCE_FILES


def _old_science_id(binding):
    if binding.scientific_source_id:return binding.scientific_source_id
    hashes=binding.packages.get('hashes',{})
    closure={name:hashes.get(name.removeprefix('src/')) for name in SCIENCE_FILES}
    if any(v is None for v in closure.values()):raise ValueError('scientific dependency closure missing')
    return hashlib.sha256(json.dumps(closure,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def import_completed(source_root,target):
    """Admit old results only by explicit call; each new result carries provenance."""
    root=Path(source_root)
    if root.resolve()==target.root.resolve() or root.is_symlink():raise ValueError('source run must be distinct')
    old=ExecutionBinding(**json.loads((root/'RUN_BINDING.json').read_text()))
    if _old_science_id(old)!=target.binding.scientific_source_id:
        raise ValueError('scientific dependency identity mismatch')
    db=sqlite3.connect(f'file:{root/"controller.sqlite"}?mode=ro',uri=True)
    imported=0
    try:
        rows=db.execute("SELECT task_id,spec,number,sha256,epoch FROM tasks WHERE state='COMMITTED' ORDER BY task_id").fetchall()
        if target.epoch is None:target.begin_epoch()
        for old_tid,raw,number,sha,epoch in rows:
            original=CaseSpec(**json.loads(raw))
            if original.science_fields['source'] not in (old.scientific_source_id,old.source_commit+':'+old.source_tree,old.source_commit):
                raise ValueError('old case source does not match binding')
            path=root/'results'/old_tid/'result.json'
            if path.is_symlink() or not path.is_file():raise ValueError('old result missing or symlink')
            data=path.read_bytes()
            if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('old result tampered')
            outcome=validate_document(json.loads(data),original,old,Attempt(old_tid,epoch,number))
            new_fields={**original.science_fields,'source':target.binding.scientific_source_id}
            spec=CaseSpec(original.kind,new_fields);tid=task_id(spec)
            if target.load(tid) is not None:continue
            att=target.claim(spec)
            doc=outcome_document(spec,outcome,target.binding,att)
            doc['provenance']={'classification':'IMPORTED_EVIDENCE','source_binding':old.identity(),
                               'source_task_id':old_tid,'source_result_sha256':sha}
            prepared=target.attempt_path(att)
            target._write_exclusive(prepared,(json.dumps(doc,sort_keys=True,allow_nan=False)+'\n').encode())
            target.commit(att,prepared)
            target._event('IMPORTED_EVIDENCE',task_id=tid,source_task_id=old_tid,source_result_sha256=sha)
            imported+=1
    finally:db.close()
    return imported
