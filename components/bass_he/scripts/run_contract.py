"""Exclusive run ownership and immutable restart identity (Linux/POSIX)."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import fcntl,json,time,uuid
from bass_he.geometry import atomic_json,jsonable


def bind_run(out,spec,*,resume):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);p=out/'RUN_BINDING.json'
    value=jsonable(spec)
    if p.exists():
        if not resume:raise FileExistsError(f'{out} already contains a run; use --resume or a new directory')
        if json.loads(p.read_text())!=value:raise ValueError('resume identity mismatch: source/environment/parameters changed')
    elif resume:raise FileNotFoundError(f'no restart binding in {out}')
    else:atomic_json(p,value)


@contextmanager
def run_lock(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Never unlink the lock inode; flock releases ownership on exit or process loss.
    with (out/'.RUN.lock').open('a+b') as f:
        try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise RuntimeError('another process owns this run directory') from exc
        try:yield
        finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)


def snapshot_geometry(out,rows,*,attempt=None):
    """Preserve attempt history and materialize cache hits in every run export."""
    out=Path(out)
    if attempt is not None:
        atomic_json(out/'attempts'/f'{time.time_ns()}_{uuid.uuid4().hex}.json',attempt)
    atomic_json(out/'GEOMETRY_RESULTS.json',rows)
