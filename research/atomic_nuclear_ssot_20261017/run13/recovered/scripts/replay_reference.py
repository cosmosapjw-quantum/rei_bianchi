"""Replay a full-packet joint solve and one same-packet native split case.

This does not repeat the whole fifteen-configuration campaign.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,subprocess,csv,io,hashlib
import numpy as np
from retarded_integrator import ROOT,RetardedModel,solve_packet
out=Path(os.environ.get('REPLAY_OUT',str(ROOT/'replay')));out.mkdir(parents=True,exist_ok=True)
m=RetardedModel();y,r=solve_packet(m,'DOP853',3e-10)
old=np.load(ROOT/'evidence/DOP853_3e-10_joint_n1/endpoint.npy')
# Pre-declared roundoff reproduction criterion, separate from scientific accuracy.
rel=float(np.max(abs(y-old)/np.maximum(abs(old),1.0)))
assert rel<5e-13,rel
np.save(out/'JOINT_ENDPOINT.npy',y)
exe=ROOT/'code/rei_bass_coupled/target/release/examples/fixed_packet_campaign'
env=dict(os.environ,RUN08_PACKET_BITS=str(out/'NATIVE_PACKET.bits'))
p=subprocess.run([str(exe),'SIGNED_MINUS','2','121','mean','on','2','4','2','1'],capture_output=True,text=True,check=True,timeout=15,env=env)
(out/'NATIVE_FIXED_N2.csv').write_text(p.stdout)
new=list(csv.DictReader(io.StringIO(p.stdout)))[0]
oldrow=next(x for x in csv.DictReader((ROOT/'evidence/NATIVE_FIXED_PACKET.csv').open()) if x['steps']=='2')
assert new==oldrow,[(k,new[k],oldrow[k])for k in new if new[k]!=oldrow[k]]
assert (out/'NATIVE_PACKET.bits').read_bytes()==(ROOT/'evidence/JOINT_PACKET.bits').read_bytes()
record={'joint_endpoint_binary64_exact_equal':bool(np.array_equal(y,old)),'joint_roundoff_scaled_error':rel,'joint_dimension':len(y),'native_N2_csv_fields_exact_equal':new==oldrow,'native_source_tuples_byte_equal':True,'physical_source_tuples':15360,'full_15_case_campaign_repeated':False,'representative_joint_solver':r}
(out/'RESTORE_REFERENCE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k!='representative_joint_solver'},indent=2))
