"""Hash-bound per-channel Coulomb cache for nested grids, with process locks.

Only analytic F/G evaluations are reused. Source quadrature and Green sweeps
retain their own requests. Values serialize with guard digits and must round
back to the exact mpmath value at the recorded working precision.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import uuid

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(value):return hashlib.sha256(canonical(value)).hexdigest()

@contextmanager
def channel_cache(root,binding,ell,m):
    if root is None:
        yield {},None
        return
    import fcntl
    directory=Path(root)/digest(binding)
    if directory.is_symlink():raise ValueError('cache directory symlink refused')
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/f'ell_{ell:04d}.json'
    lockpath=directory/f'ell_{ell:04d}.lock'
    if path.is_symlink() or lockpath.is_symlink():raise ValueError('cache symlink refused')
    with lockpath.open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        values={}
        if path.exists():
            saved=json.loads(path.read_text())
            payload=saved['payload']
            if (saved.get('payload_sha256')!=digest(payload) or payload.get('binding')!=binding
                    or payload.get('ell')!=ell or payload.get('schema')!='PHYS73_COULOMB_CACHE_V1'):
                raise ValueError('Coulomb cache binding or hash mismatch')
            for radius,entry in payload['values'].items():
                rr=float.fromhex(radius)
                if not 27<=rr<=65 or float(rr).hex()!=radius or not isinstance(entry,list) or len(entry)!=2:
                    raise ValueError('invalid cached Coulomb radius/value')
                fg=[m.mpf(x) for x in entry]
                if not all(m.isfinite(x) for x in fg):raise ValueError('nonfinite cached value')
                values[radius]=fg
        old_keys=set(values)
        yield values,str(path)
        if set(values)!=old_keys:
            encoded={}
            for radius,fg in sorted(values.items()):
                entry=[m.nstr(x,n=m.mp.dps+12) for x in fg]
                if any(m.mpf(s)!=x for s,x in zip(entry,fg)):
                    raise ArithmeticError('Coulomb cache serialization failed exact roundtrip')
                encoded[radius]=entry
            payload=dict(schema='PHYS73_COULOMB_CACHE_V1',binding=binding,ell=ell,values=encoded)
            tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
            with tmp.open('x') as stream:
                json.dump(dict(payload=payload,payload_sha256=digest(payload)),stream,sort_keys=True)
                stream.write('\n')
            os.replace(tmp,path)
