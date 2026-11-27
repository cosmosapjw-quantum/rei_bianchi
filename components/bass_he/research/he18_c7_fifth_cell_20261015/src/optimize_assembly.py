#!/usr/bin/env python3
"""Replace the slow 16-panel Bernstein residual kernel by exact Fraction algebra.

Only the interval-coefficient Bernstein evaluation is changed; the analytic
Taylor remainder and parent photon/gas moment contracts stay unchanged.
"""
from pathlib import Path
import argparse

NEW_KERNEL = '''
def residual_bounds(mid,whole,parts=16):
    # Interval inputs contain endpoints of c0,c1,c2 and whole-domain c3.
    coeff=[tuple(map(Q,mid[k])) for k in range(3)]
    remainder=max(abs(Q(t)) for t in whole[3])
    if any(lo_>hi_ for lo_,hi_ in coeff):
        raise ValueError("REVERSED_TAYLOR_COEFFICIENT")
    gmax=Q(0); integ=Q(0); weighted=Q(0)
    def control(a,b):
        low=Q(0);high=Q(0)
        for (cl,cu),v in zip(coeff,(Q(1),a,b)):
            t0=v*cl;t1=v*cu
            low+=min(t0,t1);high+=max(t0,t1)
        return max(abs(low),abs(high))
    for i in range(parts):
        aa=Q(i,parts)-Q(1,2)
        bb=Q(i+1,parts)-Q(1,2)
        step=bb-aa
        # Degree-two Bernstein control ordinates of p on [aa,bb].
        mx=max(control(aa,aa*aa),
               control((aa+bb)/2,aa*bb),
               control(bb,bb*bb))
        gmax=max(gmax,mx)
        integ+=step*mx
        weighted+=step*(Q(1,2)-(aa+bb)/2)*mx
    return dict(sup=gmax+remainder/8,
        integral=integ+remainder/32,
        weighted_integral=weighted+remainder/64,
        third_coeff=remainder,polynomial_sup=gmax)

'''
def patch(runtime):
    path=runtime/"src/assemble_certificate.py"
    s=path.read_text()
    a=s.find("def residual_bounds(")
    b=s.find("def inverse(",a)
    if a<0 or b<=a:raise ValueError("ASSEMBLY_KERNEL_BASELINE_CHANGED")
    if "def control(a,b):" in s:raise ValueError("ALREADY_OPTIMIZED")
    path.write_text(s[:a]+NEW_KERNEL+s[b:])
    print("EXACT_FRACTION_BERNSTEIN_KERNEL_READY")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--runtime",type=Path,required=True)
    args=parser.parse_args()
    patch(args.runtime)
