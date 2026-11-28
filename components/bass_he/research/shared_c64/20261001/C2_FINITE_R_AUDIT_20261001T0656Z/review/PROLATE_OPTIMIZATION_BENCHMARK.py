"""One reference timing and three warm backend timings on one archived R2 pair."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'reference'))
sys.path.insert(0, str(ROOT/'code'))
from state_io import load_pair
import prolate_fast as fast
from coupling import direct as reference_direct, torque as reference_torque

parser=argparse.ArgumentParser()
parser.add_argument('pair',type=Path)
args=parser.parse_args()
started=time.perf_counter()
g,b=load_pair(args.pair)
if g.R != 2.0 or b.R != 2.0:
    raise ValueError('preregistered parity benchmark requires R=2')
results={}
for name,reference,order in [('direct',reference_direct,16),('torque',reference_torque,20)]:
    t=time.perf_counter(); ref=reference(g,b,order); ref_seconds=time.perf_counter()-t
    lane={'reference':ref,'reference_seconds_single':ref_seconds,'order':order,'backends':{}}
    for backend in ('python','native'):
        fn=getattr(fast,name)
        t=time.perf_counter();cold=fn(g,b,order,backend=backend); cold_seconds=time.perf_counter()-t
        times=[];outs=[]
        for _ in range(3):
            t=time.perf_counter();got=fn(g,b,order,backend=backend);times.append(time.perf_counter()-t);outs.append(got)
        diffs={k:max(abs(o[k]-v) for o in [cold]+outs) for k,v in ref.items() if isinstance(v,float)}
        median=float(np.median(times))
        lane['backends'][backend]={'cold_seconds':cold_seconds,'warm_seconds':times,
          'warm_median_seconds':median,'reference_single_over_warm_median':ref_seconds/median,
          'max_abs_difference':max(diffs.values()),'differences':diffs,
          'outputs_equal_across_repetitions':all(o==cold for o in outs),'output':outs[-1]}
    results[name]=lane
passed=all(b['max_abs_difference']<=1e-11 for l in results.values() for b in l['backends'].values())
result={'scope':'C2 R2 base archived coefficients; no new eigensolve; one reference timing not a statistical reference distribution',
 'pair_path':str(args.pair.resolve()),'pair_sha256':hashlib.sha256(args.pair.read_bytes()).hexdigest(),
 'config':g.metadata()['config'],'native_identity':fast.native_identity(),
 'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),
 'lanes':results,'passed':passed,'tolerance_abs':1e-11,
 'wall_seconds':time.perf_counter()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
 'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                 [ROOT/'code/prolate_fast.py',ROOT/'native/prolate_observables.f90',Path(__file__)]}}
output=ROOT/'review/PROLATE_OPTIMIZATION_PHYSICAL_PARITY.json'
with output.open('x') as f:
    json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:{'reference_seconds':v['reference_seconds_single'],
                      'backends':{bk:{kk:bb[kk] for kk in ['warm_median_seconds','reference_single_over_warm_median','max_abs_difference']}
                                  for bk,bb in v['backends'].items()}} for k,v in results.items()},indent=2))
print('PASS' if passed else 'FAIL')
assert passed
