#!/usr/bin/env python3
"""Memoize identical exact rational photon residual Taylor inputs.

Only residual bound computations are deduplicated; all 2904 photon source,
chemical coupling, outgoing component errors and physical output remain distinct.
Keys are the complete coefficient intervals actually consumed by residual_bounds.
Safe because the Bernstein residual is a pure deterministic Fraction function.
"""
from pathlib import Path
import argparse
HOOK= '''
def _memoized_photon_residuals(mid_photons,whole_photons):
    if len(mid_photons)!=2904 or len(whole_photons)!=2904:
        raise ValueError("PHOTON_RESIDUAL_DIMENSION_NOT_2904")
    cache={}
    results=[]
    for mid,whole in zip(mid_photons,whole_photons):
        # residual_bounds consumes mid[0:3] and whole[3], nothing else.
        key=(tuple(tuple(c) for c in mid[:3]),tuple(whole[3]))
        result=cache.get(key)
        if result is None:
            result=residual_bounds(mid,whole)
            cache[key]=result
        results.append(result)
    if len(results)!=2904:raise ValueError("MISSING_SOURCE_PHOTON")
    return results

'''
def patch(runtime:Path):
    file=runtime/"src/assemble_certificate.py"
    s=file.read_text()
    anchor="def inverse("
    old="rp=[residual_bounds(a,b) for a,b in zip(mid['photon'],whole['photon'])]"
    new="rp=_memoized_photon_residuals(mid['photon'],whole['photon'])"
    if s.count(old)!=1 or s.count(anchor)!=1:
        raise ValueError("MEMOIZATION_BASELINE_NOT_ADMITTED")
    if "_memoized_photon_residuals" in s:
        raise ValueError("REFUSE_SECOND_PATCH")
    s=s.replace(anchor,HOOK+anchor,1)
    s=s.replace(old,new,1)
    file.write_text(s)
    print("SOURCE_SAFE_PHOTON_EXACT_RESIDUAL_MEMOIZATION_ADMITTED")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--runtime",type=Path,required=True)
    args=p.parse_args()
    patch(args.runtime)
