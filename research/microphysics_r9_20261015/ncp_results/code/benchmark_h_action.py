#!/usr/bin/env python3
"""Same accepted atomic FCI H-action at4/8/12threads, sequentially."""
import argparse,json,time,os,resource
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
import numpy as np
from pyscf import ao2mo,lib
import microphysics_driver_v3 as m
p=argparse.ArgumentParser();p.add_argument('--state-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--repeats',type=int,default=5);a=p.parse_args()
r=json.loads((a.state_dir/'receipt.json').read_text());case=r['case']
if case['kind']!='atomic' or not r['finite_model_numerics_passed']:raise SystemExit('require accepted atomic target')
try:lib.current_memory()
except FileNotFoundError:
    def mem():
        v,r=map(int,Path('/proc/self/statm').read_text().split()[:2]);p=os.sysconf('SC_PAGE_SIZE');return r*p/1e6,v*p/1e6
    lib.current_memory=mem
atom,charge,spin=m.SPECIES[case['species']]
mol=m.mol_build([(atom,(0,0,0))],case['basis'],charge,spin,case['memory_gib'])
data=np.load(a.state_dir/'data.npz');C=data['orbital_matrix'];ci=data['CI'];eri=ao2mo.kernel(mol,C);act=m.raw_action(data['h1'],eri,C.shape[1],mol.nelec);results=[];reference=None
for threads in [4,8,12]:
    lib.num_threads(threads);act(ci);elapsed=[]
    for _ in range(a.repeats):
        t=time.perf_counter();hc=act(ci);elapsed.append(time.perf_counter()-t)
    if reference is None:reference=hc.copy()
    results.append(dict(threads=threads,seconds=elapsed,median_s=float(np.median(elapsed)),H_action_difference_norm=float(np.linalg.norm(hc-reference))))
record=dict(state_data_sha256=m.sha(a.state_dir/'data.npz'),state_worker_source_sha256=r.get('runtime',{}).get('source_sha256'),benchmark_worker_source_sha256=m.sha(m.__file__),benchmark_source_sha256=m.sha(__file__),case=case,measurements=results,recommended_threads=min(results,key=lambda x:x['median_s'])['threads'],runtime=m.system_info(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
m.dump(a.out,record);print(json.dumps(record,indent=2))
