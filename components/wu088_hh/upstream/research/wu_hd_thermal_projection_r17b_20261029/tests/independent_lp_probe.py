"""Independent floating LP check against exact Fraction projection formula."""
from __future__ import annotations
import json, random
from fractions import Fraction as F
from pathlib import Path
from scipy.optimize import linprog
from src.thermal_projection import sharp_row_interval

def run(ncases=120, seed=20261029):
    rng=random.Random(seed); max_abs=0.0
    for case in range(ncases):
        n=4
        w=tuple(F(rng.randint(1,9),rng.randint(1,6)) for _ in range(n))
        l=(F(0),)*n
        u=tuple(F(rng.randint(1,7),rng.randint(1,5)) for _ in range(n))
        rates=tuple(ui * F(rng.randint(1,9),10) for ui in u)
        K=sum((wi*ri for wi,ri in zip(w,rates)),F(0))
        target=rng.randrange(n)
        lo,hi=sharp_row_interval(w,l,u,K,K,target)
        Af=[[float(q) for q in w],[-float(q) for q in w]]
        bf=[float(K),-float(K)]
        obj=[0.0]*n;obj[target]=1.0
        x=linprog(obj,A_ub=Af,b_ub=bf,bounds=[(float(a),float(b)) for a,b in zip(l,u)],method='highs')
        y=linprog([-v for v in obj],A_ub=Af,b_ub=bf,bounds=[(float(a),float(b)) for a,b in zip(l,u)],method='highs')
        assert x.success and y.success, (case,x.message,y.message)
        e=max(abs(x.x[target]-float(lo)),abs(y.x[target]-float(hi)))
        max_abs=max(max_abs,e)
        assert e <= 1e-9,(case,e,lo,hi)
    return {'reference':'scipy.optimize.linprog HiGHS independent LP','seed':seed,'tested':ncases,'max_abs_error':max_abs,'tolerance':1e-9,'verdict':'PASS','physical_admission':False}

if __name__=='__main__':
    out=run(); path=Path(__file__).resolve().parents[1]/'delivery'/'INDEPENDENT_LP_CHECK.json'
    path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
