"""Independent exact box/slab vertex review of frozen R17B projection code.

Does not implement the production row-projection formula as its oracle.
Enumerates geometric vertices of the clipped finite box using Fraction arithmetic.
All generated coefficients are synthetic; no physical HD rate is supplied.
"""
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'frozen_source/src/thermal_projection.py'
spec = importlib.util.spec_from_file_location('frozen_r17b_projection', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def vertices(w, lo, up, a, b):
    # K <= b and k >= 0 make each otherwise unbounded coordinate finite.
    hi = tuple(min(u, b/wi) if u is not None else b/wi
               for wi, u in zip(w, up))
    if any(l > u for l, u in zip(lo, hi)):
        return []
    out = set()
    n = len(w)
    def add(x):
        x = tuple(x)
        k = sum((wi*xi for wi,xi in zip(w,x)),F(0))
        if all(l <= xi <= u for l,xi,u in zip(lo,x,hi)) and a <= k <= b:
            out.add(x)
    for x in itertools.product(*zip(lo,hi)):
        add(x)
    for free in range(n):
        others = [i for i in range(n) if i != free]
        for values in itertools.product(*(tuple((lo[i],hi[i])) for i in others)):
            for total in set((a,b)):
                x = [F(0)]*n
                for i, value in zip(others,values):
                    x[i] = value
                x[free] = (total-sum((w[i]*x[i] for i in others),F(0)))/w[free]
                add(x)
    return sorted(out)


def main():
    t0,c0 = time.monotonic(),time.process_time()
    rng = random.Random(922907513)
    counts = {'synthetic_cases':0,'exact_target_projections':0,
              'infeasible_rejections':0,'unbounded_upper_cases':0,
              'nonzero_lower_cases':0,'singleton_cases':0,
              'factor_corners':0,'factor_targets':0,'contract_rejections':0}
    for case in range(160):
        n = 1+case%4
        w = tuple(F(rng.randint(1,7),rng.randint(1,7)) for _ in range(n))
        lo = tuple(F(rng.randint(0,5),rng.randint(1,5)) for _ in range(n))
        up = tuple(None if rng.randrange(4)==0 else l+F(rng.randint(0,8),rng.randint(1,6)) for l in lo)
        low_total = sum((wi*l for wi,l in zip(w,lo)),F(0))
        if case%7==0:
            a,b = F(0),max(F(0),low_total-F(1,7))
        else:
            a = max(F(0),low_total+F(rng.randint(-4,6),5))
            b = a+F(rng.randint(0,9),5)
        vs = vertices(w,lo,up,a,b)
        counts['synthetic_cases'] += 1
        counts['unbounded_upper_cases'] += any(u is None for u in up)
        counts['nonzero_lower_cases'] += any(l>0 for l in lo)
        counts['singleton_cases'] += n==1
        for target in range(n):
            if not vs:
                try:
                    mod.sharp_row_interval(w,lo,up,a,b,target)
                except mod.ContractError:
                    counts['infeasible_rejections'] += 1
                else:
                    raise AssertionError(('accepted empty',case,target))
            else:
                got = mod.sharp_row_interval(w,lo,up,a,b,target)
                ref = (min(x[target] for x in vs),max(x[target] for x in vs))
                assert got == ref, (case,target,got,ref)
                for endpoint in got:
                    assert any(x[target]==endpoint for x in vs)
                counts['exact_target_projections'] += 1

    # Degenerate all-zero aggregate and no-rate freedom.
    assert mod.sharp_row_interval((F(1),),(F(0),),(None,),F(0),F(0),0)==(F(0),F(0))
    assert mod.sharp_row_interval((F(2),),(F(1),),(F(1),),F(2),F(2),0)==(F(1),F(1))
    counts['exact_target_projections'] += 2

    # Exact all-corner check: all weights share a partition denominator.
    L = tuple(F(i+1,i+2) for i in range(9))
    U = tuple(l+F(i+1,11) for i,l in enumerate(L))
    weight_extrema = {(j,r): [None,None] for j in range(9) for r in (0,1)}
    for vals in itertools.product(*zip(L,U)):
        weights = mod.source_weights(vals)
        assert sum(weights,F(0))==5
        counts['factor_corners'] += 1
        for (j,r), ext in weight_extrema.items():
            q=weights[j*10+r]
            ext[0]=q if ext[0] is None else min(ext[0],q)
            ext[1]=q if ext[1] is None else max(ext[1],q)
    for (j,r), ext in weight_extrema.items():
        assert mod.target_weight_interval(L,U,j,r)==tuple(ext)
        counts['factor_targets'] += 1

    bad = [
        lambda: mod.sharp_row_interval((F(0),),(F(0),),(F(1),),F(0),F(1),0),
        lambda: mod.sharp_row_interval((F(1),),(F(-1),),(F(1),),F(0),F(1),0),
        lambda: mod.sharp_row_interval((F(1),),(F(0),),(F(-1),),F(0),F(1),0),
        lambda: mod.sharp_row_interval((F(1),),(F(0),),(None,),F(0),F(1),True),
        lambda: mod.target_weight_interval(L,U,True,0),
        lambda: mod.target_weight_interval(L,U,0,False),
        lambda: mod.source_weights((F(1),)*8+(1,)),
        lambda: mod.conservative_target_cap(F(1),F(0)),
        lambda: mod.printed_total_in_si(F(-1)),
    ]
    for f in bad:
        try:
            f()
        except mod.ContractError:
            counts['contract_rejections'] += 1
        else:
            raise AssertionError('missing rejection')
    assert mod.printed_total_in_si(F(1))==F(1,10**16)
    data=SOURCE.read_bytes()
    result={'verdict':'PASS_SCOPED','reviewer':'/root/r17b_independent_review',
            'source_commit':'31d3270ef210ef6659915105358f8fdbf8dae5a0',
            'source_git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),
            'source_sha256':hashlib.sha256(data).hexdigest(),
            'method':'independent exact clipped-box vertex enumeration and all-corner weight extremization',
            'counts':counts,'python':sys.version,'cpu_seconds':time.process_time()-c0,
            'wall_seconds':time.monotonic()-t0,'physical_source_admission':False,
            'prior_full_suite_replay':False}
    (ROOT/'INDEPENDENT_REVIEW_EXECUTION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
