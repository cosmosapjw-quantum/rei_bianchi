import os
for v in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[v]='1'
import pathlib,json,sys,time,traceback,numpy as np
from retarded_integrator import RetardedModel,solve_packet,ROOT,coalesce_reflections
method=sys.argv[1] if len(sys.argv)>1 else 'DOP853';rtol=float(sys.argv[2]) if len(sys.argv)>2 else 3e-10
split=sys.argv[3] if len(sys.argv)>3 and sys.argv[3]!='joint' else None
n=int(sys.argv[4]) if len(sys.argv)>4 else 1
representation=sys.argv[5] if len(sys.argv)>5 else 'full'
label=f'{representation}_{method}_{rtol:.0e}_{split or "joint"}_n{n}';out=ROOT/'evidence'/label;out.mkdir(exist_ok=True)
try:
 packet=json.loads((ROOT/'inputs/FINITE_BIRTH_PACKET.json').read_text())
 if representation=='paired':packet=coalesce_reflections(packet)
 m=RetardedModel(packet);y,r=solve_packet(m,method,rtol,split=split,n=n)
 r['representation']=representation
 np.save(out/'endpoint.npy',y);(out/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='segments'},indent=2))
except Exception as e:
 (out/'FAILURE.txt').write_text(traceback.format_exc());raise
