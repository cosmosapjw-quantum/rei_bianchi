"""Executable exact witnesses for T5, not a production certificate adapter.

Only synthetic Fraction matrices are constructed by this module/test driver.
The immutable old Gram engine is imported by verified source SHA. No array,
native backend, source callback, comparator or scientific producer is loaded.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import importlib.util
import sys

GRAM_PATH=Path(__file__).resolve().parents[2]/'gap_closure_20261001_g0_g6_v1/exact_gram/engine.py'
GRAM_SHA256='e10f206d63be1a99a441780108619574605014a9b01b3b327e21fecb18c5b9cc'
if hashlib.sha256(GRAM_PATH.read_bytes()).hexdigest()!=GRAM_SHA256:
    raise RuntimeError('immutable exact-Gram source SHA mismatch')
spec=importlib.util.spec_from_file_location('_t5_exact_gram',GRAM_PATH)
gram=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=gram
old_bytecode_setting=sys.dont_write_bytecode
try:
    sys.dont_write_bytecode=True
    spec.loader.exec_module(gram)
finally:
    sys.dont_write_bytecode=old_bytecode_setting


def exact(q):
    if type(q) not in (int,Q):raise TypeError('synthetic exact rational or integer required')
    return Q(q)


def matrix(rows):
    return [[(exact(x),Q(0)) for x in row] for row in rows]


def interval(lo,hi):
    return gram.Interval(exact(lo),exact(hi))


def subtract(a,b):
    if len(a)!=len(b) or any(len(x)!=len(y) for x,y in zip(a,b)):
        raise ValueError('shape mismatch')
    return [[(x[0]-y[0],x[1]-y[1]) for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def rectangular_disk(xlo,xhi,ylo,yhi,precision=128):
    xlo,xhi,ylo,yhi=map(exact,(xlo,xhi,ylo,yhi))
    if xlo>xhi or ylo>yhi:raise ValueError('reversed rectangular interval')
    center=((xlo+xhi)/2,(ylo+yhi)/2)
    q=((xhi-xlo)/2)**2+((yhi-ylo)/2)**2
    return gram.ComplexDisk(center,gram.sqrt_interval(q,precision=precision).hi)


def sharp(raw,disks,precision=128):
    if len(raw)!=len(disks) or any(len(x)!=len(y) for x,y in zip(raw,disks)):
        raise ValueError('shape mismatch')
    if any(not isinstance(d,gram.ComplexDisk) for row in disks for d in row):
        raise TypeError('explicit complex disks required')
    center=[[d.center for d in row] for row in disks]
    rho=gram.sqrt_interval(sum((d.radius*d.radius for row in disks for d in row),Q(0)),precision=precision).hi
    s=gram.spectral_norm(subtract(raw,center),precision=precision)
    return {'interval':interval(max(Q(0),s.lo-rho),s.hi+rho),'center_norm':s,'rho_upper':rho}


def k_disks(c,r):
    if not c or any(len(row)!=2 for row in c) or len(r)!=2 or any(len(row)!=len(c) for row in r):
        raise ValueError('C must be n by 2 and R must be 2 by n')
    out=[]
    for i,row in enumerate(c):
        line=[]
        for j,x in enumerate(row):
            y=r[j][i]
            line.append(gram.ComplexDisk(((x.center[0]-y.center[0])/2,
                                         (x.center[1]+y.center[1])/2),
                                        (x.radius+y.radius)/2))
        out.append(line)
    return out


def gap(local,other):
    return interval(other.lo-local.hi,other.hi-local.lo)


def raw_gap_tube(rawgap,epsilon):
    epsilon=exact(epsilon)
    if epsilon<0:raise ValueError('negative epsilon')
    return interval(rawgap.lo-2*epsilon,rawgap.hi+2*epsilon)


def intersect(a,b):
    lo,hi=max(a.lo,b.lo),min(a.hi,b.hi)
    if lo>hi:raise ValueError('inconsistent enclosures; no certificate')
    return interval(lo,hi)


def fixed94_radius_bound(radius):
    """Exact rational bound sqrt(94)*r <= 10*r; no radical rounding floor."""
    radius=exact(radius)
    if radius<0:raise ValueError('negative radius')
    return 10*radius
