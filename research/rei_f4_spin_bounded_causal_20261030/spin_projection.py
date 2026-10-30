"""Ferrett direct R31/R32 conditional n=2+n=3 neutral Li K-shell residual fractions.

No assertion that experimental (n2+n3) denominator equals total BASS K source.
For original BASS measured-window-only source events, the singlet source is bounded
between zero and K * n2_rest. The Langer-B/C decomposition is exploratory only.
"""
from __future__ import annotations
from math import isfinite

def fractions(r: float, t: float) -> dict[str, float]:
    if not all(isfinite(x) and x >= 0 for x in (r, t)):
        raise ValueError('nonfinite or negative direct lab ratios')
    denominator = (1.0+r)*(1.0+t)
    return {'triplet_3S':r/denominator,
            'other_n2':1.0/denominator,
            'n3':t/(1.0+t)}

def singlet_event_envelope(K: float, r: float, t: float) -> tuple[float, float]:
    if not isfinite(K) or K < 0:
        raise ValueError('invalid source event amplitude')
    return (0.0, K*fractions(r,t)['other_n2'])

def exploratory_langer_mixing(r: float,t: float,B: float,C: float) -> dict[str,float]:
    if not all(isfinite(x) and x>=0 for x in (B,C)):
        raise ValueError('nonfinite or negative cross-paper ratios')
    f=fractions(r,t)
    if r*C>1+1e-14:
        raise ValueError('incompatible cross-paper singlet positivity')
    p3=C*f['triplet_3S']
    s1=(f['other_n2']-p3)/(1+B)
    if s1 < -1e-14:
        raise ValueError('negative singlet from inconsistent experimental ratios')
    return {'triplet_3S':f['triplet_3S'], 'triplet_3P':p3,
            'singlet_1S':max(0.,s1), 'singlet_1P':B*max(0.,s1), 'n3':f['n3']}
