"""Read-only binary64-source photoelectron and observer alias diagnostics.

Never mixes a live owner Gamma measure with a fixed-history endpoint Gamma
without an explicit comparison label. All arithmetic over stored f64 payload
uses exact Fractions; neither output is a certified true physical rate.
"""
from __future__ import annotations
import csv
import math
import struct
from fractions import Fraction as F
from pathlib import Path


def f64(s: str | float) -> F:
    f=float(s)
    if not math.isfinite(f):
        raise ValueError('NONFINITE_SOURCE_FLOAT')
    return F.from_float(f)


def assert_same_bits(a: str | float, b: str | float, name: str) -> None:
    if not math.isfinite(float(a)) or not math.isfinite(float(b)):
        raise ValueError(f'NONFINITE_IDENTITY_{name}')
    if struct.pack('!d',float(a)) != struct.pack('!d',float(b)):
        raise ValueError(f'SOURCE_BINARY64_MISMATCH_{name}: {a} != {b}')


def photo_weights(fhe: F, x: F, y: F, z: F) -> tuple[F,F,F]:
    if not F(0)<fhe<F(1) or not all(F(0)<=v<=F(1) for v in (x,y,z)) or y+z>1:
        raise ValueError('INVALID_HE_ABSORBER_FRACTIONS')
    return 1-x, fhe*(1-y-z), fhe*y


def source(weights, gamma) -> F:
    if len(weights)!=3 or len(gamma)!=3 or any(v<0 for v in (*weights,*gamma)):
        raise ValueError('INVALID_POSITIVE_PHOTO_SOURCE')
    return sum((a*b for a,b in zip(weights,gamma)),F(0))


def symmetric_pair(w0, w1, g0, g1) -> dict[str,F]:
    # delta(w*g) = mean(w)*delta(g) + mean(g)*delta(w)
    rate=sum(((w0[i]+w1[i])*(g1[i]-g0[i])/2 for i in range(3)),F(0))
    occupancy=sum(((g0[i]+g1[i])*(w1[i]-w0[i])/2 for i in range(3)),F(0))
    total=sum((w1[i]*g1[i]-w0[i]*g0[i] for i in range(3)),F(0))
    if rate+occupancy!=total:
        raise ArithmeticError('EXACT_SYMMETRIC_IDENTITY_FAILURE')
    return {'rate':rate,'occupancy':occupancy,'delta':total}


def paired_alias_decomposition(w0,w1,gl0,gl1,ge0,ge1):
    # delta_m[(source_live-source_endpoint)] versus OFF
    a0=tuple(gl0[i]-ge0[i] for i in range(3))
    a1=tuple(gl1[i]-ge1[i] for i in range(3))
    r=symmetric_pair(w0,w1,a0,a1)
    if r['delta'] != (source(w1,gl1)-source(w0,gl0))-(source(w1,ge1)-source(w0,ge0)):
        raise ArithmeticError('ALIAS_COMMUTATOR_IDENTITY_FAILED')
    return {'total':r['delta'],'rate':r['rate'],'occupancy':r['occupancy']}


def allowance_ratio(a: F,b: F,absolute: F | None=None,relative: F | None=None) -> F:
    if absolute is None: absolute=f64('1e-22')
    if relative is None: relative=f64('1e-6')
    if absolute<=0 or relative<0:
        raise ValueError('INVALID_REFERENCE_ALLOWANCE')
    return abs(a-b)/(absolute+relative*max(abs(a),abs(b)))


def condition(a:F,b:F) -> F|None:
    total=a+b
    return (abs(a)+abs(b))/abs(total) if total else None


def load_mode_csv(path:Path, rows_expected:int=385, step_column:str='step'):
    with Path(path).open(newline='') as file:
        data=list(csv.DictReader(file))
    if len(data)!=rows_expected:
        raise ValueError(f'ROW_COUNT_MISMATCH_{path.name}_{len(data)}')
    if step_column in data[0]:
        for i,row in enumerate(data):
            if int(row[step_column])!=i:
                raise ValueError(f'CLOCK_STEP_MISMATCH_{path.name}_{i}')
    return data
