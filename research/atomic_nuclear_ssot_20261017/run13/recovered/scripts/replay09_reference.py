import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,numpy as np
from retarded_integrator import RetardedModel,coalesce_reflections,solve_packet
R=Path(__file__).resolve().parents[1]
packet=json.loads((R/'inputs/refined/r2.json').read_text());m=RetardedModel(coalesce_reflections(packet))
y,rec=solve_packet(m,rtol=3e-11,wall_cap=38.)
original=np.load(R/'evidence/r2_paired_DOP853_3e-11/endpoint.npz')['state']
assert np.array_equal(y,original),'same-runtime float64 endpoint equality failed'
(R/'replay').mkdir(exist_ok=True)
rec['endpoint_float64_exact_equal']=True
(R/'replay/REFERENCE.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS_REPRESENTATIVE_REFERENCE','dimension':m.dim,'physical_cohorts':len(packet['cohorts']),'birth_times':rec['birth_times'],'endpoint_float64_exact_equal':True,'wall_s':rec['wall_s'],'entire_7case_replayed':False},indent=2))
