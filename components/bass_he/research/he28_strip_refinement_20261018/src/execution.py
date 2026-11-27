"""Bounded process execution and immutable evidence, no remote access or auth."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def _json_default(value):
    """Convert NumPy scalar receipts to built-in JSON scalar types."""
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None and isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def atomic_json(path, value):
    path = Path(path)
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False,
                      default=_json_default)+'\n'
    temp = path.with_name(path.name+'.partial')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    with temp.open('x') as out:
        out.write(text);out.flush();os.fsync(out.fileno())
    try:
        os.link(temp,path)
    finally:
        temp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def manifest(paths, root):
    root=Path(root).resolve()
    return {str(Path(p).resolve().relative_to(root)):digest(p) for p in paths}


def verify_manifest(expected, root):
    root=Path(root).resolve()
    for relative, value in expected.items():
        p=(root/relative).resolve()
        if not p.is_relative_to(root) or not p.is_file() or digest(p)!=value:
            raise ValueError('HE28_SOURCE_IDENTITY '+relative)


def run_process(argv, destination, timeout_s):
    """Timeout the entire POSIX process group, including the native child."""
    if not (timeout_s>0):raise ValueError('HE28_TIMEOUT_DOMAIN')
    dst=Path(destination);dst.mkdir(parents=True,exist_ok=False)
    atomic_json(dst/'COMMAND.json',{'argv':list(map(str,argv)),'timeout_s':timeout_s})
    start=time.monotonic();timed_out=False
    env=os.environ.copy()
    # Case-level concurrency is the only parallel layer in HE28. Pin numerical
    # libraries to one thread so six cases cannot each create a host-sized pool.
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                 'NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
        env[name]='1'
    env.update(OMP_DYNAMIC='FALSE',OMP_PLACES='cores',OMP_PROC_BIND='close')
    with (dst/'stdout.log').open('xb') as stdout, (dst/'stderr.log').open('xb') as stderr:
        p=subprocess.Popen(list(map(str,argv)),stdout=stdout,stderr=stderr,
                           start_new_session=True,env=env)
        try:
            code=p.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out=True
            os.killpg(p.pid,signal.SIGTERM)
            try:code=p.wait(timeout=3.)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL);code=p.wait()
        stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
    receipt={'returncode':code,'timed_out':timed_out,'wall_s':time.monotonic()-start,
             'stdout_sha256':digest(dst/'stdout.log'),
             'stderr_sha256':digest(dst/'stderr.log')}
    atomic_json(dst/'RECEIPT.json',receipt)
    return receipt
