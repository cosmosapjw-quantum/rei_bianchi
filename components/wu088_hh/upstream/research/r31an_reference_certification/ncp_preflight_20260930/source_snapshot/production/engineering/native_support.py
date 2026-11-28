"""Scoped Linux/GCC radial integration candidate; see CONTRACT.md and REPORT.md.

Only trusted, single-file radial sources with system includes are supported.
Cache and checkpoints are local filesystems with flock + atomic rename + fsync.
Their hashes detect corruption, not malicious modification or authenticity.
"""
from __future__ import annotations
import contextlib
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
FLAGS=('-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off')
BUILD_ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','SOURCE_DATE_EPOCH':'0'}
PREFIX='#define radial_entire original_radial_entire\n#include "source.cpp"\n#undef radial_entire\n'

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def sync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def write_synced(path,data):
    with Path(path).open('wb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())

@contextlib.contextmanager
def locked(path):
    with Path(path).open('a+b') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)

def run(argv,**kw):
    return subprocess.run(argv,check=True,capture_output=True,text=True,
                          env=BUILD_ENV,timeout=120,**kw).stdout.strip()

def runtime_dependencies(library):
    """ldd is only invoked on this builder's trusted compiled library."""
    listing=run(['/usr/bin/ldd',str(library)])
    paths=re.findall(r'(?:=>\s*)?(/[^\s]+)\s+\(',listing)
    if 'not found' in listing or not paths:raise RuntimeError('unresolved runtime dependencies')
    return {str(Path(p).resolve()):sha(p) for p in paths}

def checked_manifest(folder):
    manifest=json.loads((folder/'manifest.json').read_text())
    if hashlib.sha256(canonical(manifest['identity'])).hexdigest()!=folder.name:
        raise RuntimeError('cache identity mismatch')
    if set(manifest['artifacts'])!={'source.cpp','unit.cpp','radial.so','compile.stdout','compile.stderr'}:
        raise RuntimeError('cache artifact registry mismatch')
    for name,expected in manifest['artifacts'].items():
        if Path(name).name!=name or sha(folder/name)!=expected:
            raise RuntimeError('cache artifact corrupt: '+name)
    for name,expected in manifest['runtime_dependencies'].items():
        if sha(name)!=expected:raise RuntimeError('native runtime changed; use new cache scope')
    return manifest

def build_radial(source,cache):
    """No mtime decisions; freeze source, lock, build then publish whole directory."""
    source=Path(source).resolve();cache=Path(cache).resolve();cache.mkdir(parents=True,exist_ok=True)
    if platform.system()!='Linux':raise RuntimeError('this build profile supports Linux only')
    for variable in ('LD_PRELOAD','LD_LIBRARY_PATH'):
        if os.environ.get(variable):raise RuntimeError(variable+' must be unset for checked loading')
    compiler=Path(shutil.which('g++',path=BUILD_ENV['PATH']) or '').resolve()
    if not compiler.is_file():raise RuntimeError('system g++ unavailable')
    source_bytes=source.read_bytes();bridge=PREFIX.encode()+(HERE/'abi_bridge.cpp').read_bytes()
    # Deliberately serialized including dependency discovery: one CPU build budget.
    with locked(cache/'.build.lock'):
        stage=Path(tempfile.mkdtemp(prefix='.stage-',dir=cache))
        try:
            write_synced(stage/'source.cpp',source_bytes)
            write_synced(stage/'unit.cpp',bridge)
            dep_text=run([str(compiler),'-std=c++17','-M','-MT','unit','unit.cpp'],cwd=stage)
            deps=shlex.split(dep_text.replace('\\\n',' ').split(':',1)[1])
            headers={}
            for dep in deps:
                p=Path(dep)
                if not p.is_absolute():
                    if dep not in ('unit.cpp','source.cpp'):
                        raise RuntimeError('only single-file source/system headers supported')
                    continue
                headers[str(p.resolve())]=sha(p)
            tools={str(compiler):sha(compiler)}
            for program in ('cc1plus','as','ld'):
                path=run([str(compiler),'-print-prog-name='+program])
                resolved=Path(shutil.which(path,path=BUILD_ENV['PATH']) or path).resolve()
                tools[str(resolved)]=sha(resolved)
            identity={'schema':1,'source_sha256':hashlib.sha256(source_bytes).hexdigest(),
                      'bridge_sha256':hashlib.sha256(bridge).hexdigest(),'flags':list(FLAGS),
                      'compiler_version':run([str(compiler),'--version']),
                      'target':run([str(compiler),'-dumpmachine']),'tools':tools,
                      'headers':headers,'build_env':BUILD_ENV,'machine':platform.machine()}
            key=hashlib.sha256(canonical(identity)).hexdigest();dest=cache/key
            if dest.exists():
                checked_manifest(dest)
                return dest
            command=[str(compiler),*FLAGS,'unit.cpp','-o','radial.so']
            completed=subprocess.run(command,cwd=stage,env=BUILD_ENV,capture_output=True,text=True,timeout=120)
            write_synced(stage/'compile.stdout',completed.stdout.encode())
            write_synced(stage/'compile.stderr',completed.stderr.encode())
            if completed.returncode:
                failed=cache/('failed-'+stage.name.removeprefix('.stage-'))
                os.rename(stage,failed);sync_dir(cache)
                raise RuntimeError('compile failed; preserved at '+str(failed))
            manifest={'identity':identity,'command':command,
                      'runtime_dependencies':runtime_dependencies(stage/'radial.so'),
                      'artifacts':{name:sha(stage/name) for name in
                          ('source.cpp','unit.cpp','radial.so','compile.stdout','compile.stderr')}}
            with (stage/'radial.so').open('rb') as stream:os.fsync(stream.fileno())
            write_synced(stage/'manifest.json',canonical(manifest));sync_dir(stage)
            os.rename(stage,dest);sync_dir(cache)
            checked_manifest(dest)
            return dest
        except Exception as exc:
            if stage.exists():
                write_synced(stage/'failure.json',canonical({'error_type':type(exc).__name__,
                    'message':str(exc),'stdout':getattr(exc,'stdout',None),
                    'stderr':getattr(exc,'stderr',None)}))
                failed=cache/('failed-'+stage.name.removeprefix('.stage-'))
                os.rename(stage,failed);sync_dir(cache)
            raise
        finally:
            if stage.exists():shutil.rmtree(stage)

class Radial:
    """Explicit build/load, validated buffers; no last-iterations global state."""
    def __init__(self,source,cache):
        self.folder=build_radial(source,cache)
        self.manifest=checked_manifest(self.folder)
        self.lib=ctypes.CDLL(str(self.folder/'radial.so'))
        lp=ctypes.POINTER(ctypes.c_longdouble);up=ctypes.POINTER(ctypes.c_uint64)
        self.lib.production_probe.argtypes=[up,ctypes.c_size_t];self.lib.production_probe.restype=ctypes.c_int
        self.lib.production_layout.argtypes=[lp,ctypes.c_size_t];self.lib.production_layout.restype=ctypes.c_int
        self.lib.production_radial.argtypes=[ctypes.c_size_t,lp,ctypes.c_size_t,lp,ctypes.c_size_t,
                                            lp,ctypes.c_size_t,ctypes.c_int,lp,ctypes.c_size_t,
                                            ctypes.POINTER(ctypes.c_int)]
        self.lib.production_radial.restype=ctypes.c_int
        probe=np.zeros(10,dtype=np.uint64)
        if self.lib.production_probe(probe.ctypes.data_as(up),10):raise RuntimeError('native ABI probe failed')
        expected=[1,np.dtype(np.longdouble).itemsize,np.dtype(np.longdouble).alignment,
                  np.finfo(np.longdouble).nmant+1,np.finfo(np.longdouble).maxexp,
                  np.dtype(np.uintp).itemsize,8,2,np.dtype(np.clongdouble).itemsize,1]
        if probe.tolist()!=expected or expected[3]<64 or ctypes.sizeof(ctypes.c_longdouble)!=expected[1]:
            raise RuntimeError('ABI or rounding mismatch: '+str((probe.tolist(),expected)))
        self.abi=probe.tolist()
        sentinel=np.empty(2,np.clongdouble)
        if self.lib.production_layout(sentinel.ctypes.data_as(lp),4):raise RuntimeError('native layout probe failed')
        if not np.array_equal(sentinel,np.array([1.25-2.5j,-3.75+4.5j],np.clongdouble)):
            raise RuntimeError('complex interleaving mismatch')
    def radial_moments(self,variance,s,order=2,*,return_info=False):
        if type(order) is not int or order not in (0,1,2):raise ValueError('order must be integer 0, 1 or 2')
        if np.iscomplexobj(variance):raise TypeError('variance must be real')
        v,s=np.broadcast_arrays(np.asarray(variance,dtype=np.longdouble),np.asarray(s,dtype=np.clongdouble))
        if not v.size:raise ValueError('empty inputs are not valid')
        if not np.all(np.isfinite(v)) or not np.all(v>0) or not np.all(np.isfinite(s)):
            raise ValueError('finite inputs and positive variance required')
        shape=v.shape
        # require enforces alignment even when an input view has an odd byte offset.
        v=np.require(v.ravel(),dtype=np.longdouble,requirements=['C','A'])
        sr=np.require(s.real.ravel(),dtype=np.longdouble,requirements=['C','A'])
        si=np.require(s.imag.ravel(),dtype=np.longdouble,requirements=['C','A'])
        out=np.empty((order+1,10,v.size),np.clongdouble);iterations=ctypes.c_int()
        lp=ctypes.POINTER(ctypes.c_longdouble)
        code=self.lib.production_radial(v.size,v.ctypes.data_as(lp),v.size,
             sr.ctypes.data_as(lp),sr.size,si.ctypes.data_as(lp),si.size,order,
             out.ctypes.data_as(lp),out.size*2,ctypes.byref(iterations))
        if code:raise ValueError('native radial failed with status '+str(code))
        values=tuple(a.reshape((10,)+shape) for a in out)
        return (values,{'max_iterations':iterations.value,'build_key':self.folder.name}) if return_info else values

def array_schema(arrays):
    result={}
    for name,value in arrays.items():
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',name):raise ValueError('invalid array name')
        a=np.asarray(value)
        if a.dtype.kind not in 'biufc' or not a.size or not np.all(np.isfinite(a)):
            raise ValueError('checkpoint arrays must be nonempty finite numeric arrays')
        result[name]={'shape':list(a.shape),'dtype':a.dtype.str}
    if not result:raise ValueError('empty checkpoint')
    return result

def save_checkpoint(folder,identity,arrays):
    """Create-only. Identity must include data/grid/source AND build/runtime keys."""
    folder=Path(folder).resolve();folder.parent.mkdir(parents=True,exist_ok=True)
    schema=array_schema(arrays)
    with locked(folder.parent/'.checkpoint.lock'):
        if folder.exists():raise FileExistsError('immutable checkpoint already exists')
        stage=Path(tempfile.mkdtemp(prefix='.checkpoint-',dir=folder.parent))
        try:
            with (stage/'arrays.npz').open('wb') as stream:
                np.savez_compressed(stream,**arrays);stream.flush();os.fsync(stream.fileno())
            manifest={'schema_version':1,'identity':identity,'array_schema':schema,
                      'arrays_sha256':sha(stage/'arrays.npz')}
            write_synced(stage/'manifest.json',canonical(manifest));sync_dir(stage)
            os.rename(stage,folder);sync_dir(folder.parent)
        finally:
            if stage.exists():shutil.rmtree(stage)
    return sha(folder/'manifest.json')

def load_checkpoint(folder,identity,expected_schema,*,manifest_sha256=None):
    folder=Path(folder)
    if manifest_sha256 is not None and sha(folder/'manifest.json')!=manifest_sha256:
        raise RuntimeError('checkpoint manifest hash mismatch')
    m=json.loads((folder/'manifest.json').read_text())
    if m.get('schema_version')!=1 or canonical(m['identity'])!=canonical(identity):
        raise RuntimeError('checkpoint identity mismatch')
    if m['array_schema']!=expected_schema:raise RuntimeError('checkpoint schema mismatch')
    if sha(folder/'arrays.npz')!=m['arrays_sha256']:raise RuntimeError('checkpoint data hash mismatch')
    with np.load(folder/'arrays.npz',allow_pickle=False) as data:
        arrays={name:data[name] for name in data.files}
    if array_schema(arrays)!=expected_schema:raise RuntimeError('checkpoint actual array schema mismatch')
    return arrays
