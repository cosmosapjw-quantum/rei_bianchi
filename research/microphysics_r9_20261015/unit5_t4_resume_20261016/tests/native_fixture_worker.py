"""Synthetic-only control-flow integration of native_worker; no PySCF/physical H.
Input loading and reconstruction are injected toy equivalents. The actual
checkpoint SHA acquisition check is replaced for this deliberately synthetic
checkpoint only; ordinary load_checkpoint numerical and metadata gates run.
"""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

spec=importlib.util.spec_from_file_location('test_resume',Path(__file__).with_name('test_resume.py'))
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
r,b=t.r,t.b
config=json.loads(Path(sys.argv[1]).read_text());cp=Path(config['checkpoint'])
K,g,u=t.fixture();W=.7;E0=-2.;i=np.sqrt(.3)*g+np.sqrt(W)*u;H=K+E0*np.eye(len(g))
r.b.load_saved=lambda receipt,data: ({'daughter':{'E_BO_Eh':E0}}, {},i,g,u,{'W':W})
OriginalBudget=b.ActionBudget
class ToyBudget(OriginalBudget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.headroom_gib=0
b.ActionBudget=ToyBudget
original_sha=b.sha
actual_sha=json.loads((r.ROOT/'intake/SOURCE_PIN.json').read_text())['actual_checkpoint_sha256']
b.sha=lambda path: actual_sha if Path(path)==cp else original_sha(path)

def toy_reconstruct(receipt,arrays,ii,gg,uu,info,source,budget):
    action=lambda v:budget.apply(lambda x:H@x,v)
    checks=b.reconstruction_checks(action,i,g,u,E0,float(np.vdot(i,H@i).real),float(np.vdot(H@i,H@i).real),0.)
    checks['fixture']='synthetic dense toy H; no physical reconstruction'
    def projected(v):
        q=b.project(v,g)
        return b.project(action(q)-E0*q,g)
    return checks,projected

b.reconstruct=toy_reconstruct
code=r.native_worker(sys.argv[1])
receipt_path=Path(config['out'])/'receipt.json'
receipt=json.loads(receipt_path.read_text())
receipt.update(fixture_kind='synthetic native-worker integration with injected inputs and toy reconstruction',
               actual_checkpoint_compatibility='NOT_RUN',actual_physical_H_actions=0,NCP_actions=0,
               input_acquisition_check='synthetic injection; actual archive not available',
               headroom_check='disabled only in injected small dense toy budget; production default unchanged',
               campaign_action_interval_classification='SIMULATED bookkeeping only; actual historical campaign remains UNKNOWN [86,160]')
b.dump(receipt_path,receipt)
raise SystemExit(code)
