"""One bounded joint reference per independently specified birth support."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,sys,time,traceback,numpy as np,hashlib
from retarded_integrator import RetardedModel,coalesce_reflections,solve_packet
R=Path(__file__).resolve().parents[1]
r=int(sys.argv[1]);rep=sys.argv[2] if len(sys.argv)>2 else 'paired';rtol=float(sys.argv[3]) if len(sys.argv)>3 else 3e-11
method=sys.argv[4] if len(sys.argv)>4 else 'DOP853'
label=f'r{r}_{rep}_{method}_{rtol:.0e}';out=R/'evidence'/label;out.mkdir(exist_ok=True)
f=R/f'inputs/refined/r{r}.json';packet=json.loads(f.read_text());original_count=len(packet['cohorts'])
if rep=='paired':packet=coalesce_reflections(packet)
elif rep!='full':raise ValueError('representation')
try:
 m=RetardedModel(packet);y,rec=solve_packet(m,method=method,rtol=rtol,wall_cap=38.)
 rec.update(subdivisions=r,representation=rep,physical_cohorts=original_count,packet_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),parent_ode_implementation='unchanged RUN08 retarded_integrator.py',status='COMPLETE')
 np.savez_compressed(out/'endpoint.npz',state=y)
 (out/'result.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({k:v for k,v in rec.items() if k!='segments'},indent=2))
except Exception:
 (out/'FAILURE.txt').write_text(traceback.format_exc());raise
