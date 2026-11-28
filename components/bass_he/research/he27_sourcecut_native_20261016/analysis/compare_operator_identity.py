"""Compare saved trajectories only: performance equivalence, no physical certification."""
from pathlib import Path
import json,gzip,hashlib,numpy as np
w=Path('/root/HE27_NCP_SOURCECUT_20261016');a=w/'v3_pilot_n16';b=w/'fast_pilot_n16'
ar=json.loads((a/'RESULT.json').read_text())['result'];br=json.loads((b/'RESULT.json').read_text())['result']
keys=['gas_final','temperature_K','photon_number','photon_energy_ev','binding_delta_ev','number_defect','energy_defect_ev','species_defect','ledger']
for k in keys:assert ar[k]==br[k],k
with np.load(a/'birth_cohorts.npz') as aa,np.load(b/'birth_cohorts.npz') as bb:
 assert aa.files==bb.files
 for key in aa.files:assert np.array_equal(aa[key],bb[key]),key
 count=int(aa['counts'].size)
def points(p):
 with gzip.open(p/'native.jsonl.gz','rt') as f:
  for l in f:
   r=json.loads(l)
   if r['kind']=='point':yield r['request'],r['response']
ap=list(points(a));bp=list(points(b));assert ap==bp
out={'status':'NUMERICAL_IDENTITY_PERFORMANCE_ONLY','scope':'saved q0m4GL4n16 source cohorts, native requests/responses and physical endpoints; NOT independent physics verification','physical_endpoint_fields_exact_equal':keys,'cohort_mode_values_bitwise_equal':count,'native_points_request_response_exact_equal':len(ap),'runtime_seconds_v3':json.loads((a/'RESULT.json').read_text())['elapsed_s'],'runtime_seconds_fast':json.loads((b/'RESULT.json').read_text())['elapsed_s']}
with (w/'OPERATOR_IDENTITY.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
