#!/usr/bin/env python3
"""Optimize the already admitted exact rational 16-panel Bernstein residual bounds.

Physics, source, Taylor orders, and interval coefficients are identical. Reuse
shared rational basis coefficients across all 2904 photon residuals.
"""
from functools import lru_cache
from fractions import Fraction as Q
from pathlib import Path
import argparse
NEW_KERNEL = '''
from functools import lru_cache
@lru_cache(maxsize=8)
def _panel_weights(parts):
    if not isinstance(parts,int) or parts<1:
        raise ValueError("NONPOSITIVE_PANEL_COUNT")
    half=Q(1,2)
    out=[]
    for j in range(parts):
        a=Q(j,parts)-half
        b=Q(j+1,parts)-half
        step=b-a
        wt=step*(half-(a+b)/2)
        basis=((Q(1),a,a*a),
               (Q(1),(a+b)/2,a*b),
               (Q(1),b,b*b))
        out.append((step,wt,basis))
    return tuple(out)
def residual_bounds(mid,whole,parts=16):
    coeff=[tuple(map(Q,mid[k])) for k in range(3)]
    if any(a>b for a,b in coeff):
        raise ValueError("REVERSED_TAYLOR_COEFFICIENT")
    rem=max(abs(Q(t)) for t in whole[3])
    poly_sup=Q(0);integ=Q(0);weighted=Q(0)
    for step,wt,basis in _panel_weights(parts):
        hull=Q(0)
        for coeffs in basis:
            lo_=Q(0);hi_=Q(0)
            for (a,b),w in zip(coeff,coeffs):
                if w>=0:
                    lo_+=a*w;hi_+=b*w
                else:
                    lo_+=b*w;hi_+=a*w
            hull=max(hull,abs(lo_),abs(hi_))
        poly_sup=max(poly_sup,hull)
        integ+=step*hull
        weighted+=wt*hull
    return dict(sup=poly_sup+rem/8,
        integral=integ+rem/32,
        weighted_integral=weighted+rem/64,
        third_coeff=rem,polynomial_sup=poly_sup)

'''
def patch(runtime:Path)->None:
    file=runtime/"src/assemble_certificate.py"
    s=file.read_text()
    a=s.find("def residual_bounds(")
    b=s.find("def inverse(",a)
    if not (0<=a<b):raise ValueError("RESIDUAL_KERNEL_ANCHOR_CHANGED")
    if "_panel_weights(" in s:raise ValueError("REFUSE_REOPTIMIZE")
    file.write_text(s[:a]+NEW_KERNEL+s[b:])
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--runtime",type=Path,required=True)
    args=p.parse_args()
    patch(args.runtime)
    print("C8_FRACTION_CACHED_BERNSTEIN_READY")
