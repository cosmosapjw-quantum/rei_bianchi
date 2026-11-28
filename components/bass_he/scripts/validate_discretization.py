#!/usr/bin/env python3
"""New-kernel numerical refinement: CF depth and regularized action panels."""
from __future__ import annotations
import argparse, concurrent.futures, json, os, sys, time
from pathlib import Path
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from bass_he.geometry import unjsonable,atomic_json,contour_geometry
from bass_he.spectral import find_exceptional_point


def one(row):
    ep=row['ep'];t=time.perf_counter()
    higher=find_exceptional_point(ep['state_a'],ep['state_b'],ep['R'],depth=144)
    vals=[]
    for n in (32,64,128):
        a=contour_geometry(ep,0.,panels=n)
        vals.append(dict(panels=n,delta=a['delta'],max_spectral_residual=a['max_spectral_residual'],
            bisections=a['bisected_continuation_steps']))
    d1=abs(vals[0]['delta']-vals[1]['delta']);d2=abs(vals[1]['delta']-vals[2]['delta'])
    return dict(branch=row['branch'],CF_depth_96_to_144_abs_delta_R=abs(higher['R']-ep['R']),
        panels=vals,observed_order=float(np.log2(d1/d2)),relative_64_to_128=d2/vals[-1]['delta'],
        elapsed_s=time.perf_counter()-t)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ep-file',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--workers',type=int,default=2);args=ap.parse_args()
    rows=unjsonable(json.loads(Path(args.ep_file).read_text()));outputs=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(one,rows):
            outputs.append(result);atomic_json(args.out,outputs);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
