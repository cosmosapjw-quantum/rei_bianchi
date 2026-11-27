#!/usr/bin/env python3
"""Reproduce only light source-bound H convergence from archived returned arrays."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from wu088_hh.convergence import compare_h

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError('use a new output path; no old evidence overwritten')
    baseline=json.loads((ROOT/'evidence/BASELINE_SOURCE_MANIFEST.json').read_text())
    output=[]
    for z in [0,16,32,48,64]:
        dirs=[ROOT/'data/anchors'/f'z{z}'/f'B{n}' for n in [160,192]]
        for d in dirs:
            for name in ['ASSEMBLED.npz','IDENTITY.json','RESULTS.json']:
                p=d/name
                if digest(p)!=baseline[str(p.relative_to(ROOT))]:raise ValueError(f'input changed: {p}')
        ids=[json.loads((d/'IDENTITY.json').read_text()) for d in dirs]
        if ids[0]['n']!=160 or ids[1]['n']!=192:raise ValueError('basis orders')
        for k in set(ids[0])|set(ids[1]):
            if k not in ('n','grid_sha256') and ids[0].get(k)!=ids[1].get(k):raise ValueError(f'identity mismatch: {k}')
        with np.load(dirs[0]/'ASSEMBLED.npz',allow_pickle=False) as aa,np.load(dirs[1]/'ASSEMBLED.npz',allow_pickle=False) as bb:
            if float(aa['z'])!=z or float(bb['z'])!=z:raise ValueError('geometry mismatch')
            r=compare_h(aa['H'],bb['H']);r.update(z=z,sources=[dict(path=str(d.relative_to(ROOT)),assembled_sha256=digest(d/'ASSEMBLED.npz'),identity_sha256=digest(d/'IDENTITY.json')) for d in dirs])
            output.append(r)
    result=dict(schema='WU088_R31K_B_ANCHOR_H_REPLAY_V1',anchors=output,new_heavy_scientific_runs=0,
                next='RECOVER_OR_COMPUTE_SAME_Z_INDEPENDENT_DOTO_AND_IONIC_PROVIDER',
                full49_admitted=False,production_admitted=False)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
    return 0 if all(r['failure_count']==0 for r in output) else 2
if __name__=='__main__':raise SystemExit(main())
