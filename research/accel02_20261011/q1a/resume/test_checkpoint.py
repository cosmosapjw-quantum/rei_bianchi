"""Pure checkpoint fixtures: no production provider/native/RHS/ODE imports."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent

def load():
    p=HERE/'checkpoint.py'
    if not p.exists():raise AssertionError('resume validator absent: RED')
    spec=importlib.util.spec_from_file_location('q1a_resume_checkpoint',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class PureCheckpointTests(unittest.TestCase):
    def fixture(self):
        n=4;scales=np.ones(n+10);scales[3]=2.
        state=np.r_[.5,.1,.01,2.,np.ones(n),np.zeros(6)]
        u=np.arange(4)/128
        history=np.tile(state,(len(u),1))
        result=dict(status='FAILED_PRESERVED',checks={k:True for k in ('sampled_positive','accepted_positive','accepted_finite','accepted_gas_domain','energy_ledger','number_ledger')},
          completed_segments=1,n_nodes=n,history=[dict(time_s=float(t*10)) for t in u],
          failure=dict(type='TimeoutError',message='DECLARED_WALL_BUDGET_EXCEEDED',completed_segments=1,last_accepted_u=.03),
          accepted_gas_min={k:0. for k in ('xHII','xHeII','xHeIII','xHeI','T_K')},accepted_gas_max={k:1e6 for k in ('xHII','xHeII','xHeIII','xHeI','T_K')})
        result['checks']['whole_interval']=False
        return result,dict(u=u,scaled_states=history,scales=scales,q=np.arange(n)+10.,mu=np.zeros(n),weights=np.ones(n)),dict(u=np.array(.03),scaled_y=state,scales=scales),np.array([0,.02,.1,1.])
    def test_valid_interior_prefix(self):
        m=load();r,h,l,b=self.fixture();self.assertEqual(m.validate_payload(r,r['failure'],h,l,b)['resume_segment'],1)
    def test_reject_wrong_failure_and_domain_flag(self):
        m=load()
        for kind in ('minimum_step','domain'):
            r,h,l,b=self.fixture()
            if kind=='minimum_step':r['failure']['message']='Required step size is less than spacing between numbers.'
            else:r['checks']['accepted_gas_domain']=False
            with self.assertRaises(ValueError):m.validate_payload(r,r['failure'],h,l,b)
    def test_reject_epoch_gap_or_duplicate(self):
        m=load()
        for change in ('gap','duplicate'):
            r,h,l,b=self.fixture();h['u'][2]=4/128 if change=='gap' else h['u'][1]
            with self.assertRaises(ValueError):m.validate_payload(r,r['failure'],h,l,b)
    def test_reject_invalid_last_state(self):
        m=load()
        for j,value in [(0,1.01),(1,-1e-20),(4,-1e-30),(3,np.nan)]:
            r,h,l,b=self.fixture();l['scaled_y'][j]=value
            with self.assertRaises(ValueError):m.validate_payload(r,r['failure'],h,l,b)
    def test_reject_stale_hash(self):
        m=load()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'IDENTITY.json';p.write_text('{}\n')
            digest=hashlib.sha256(p.read_bytes()).hexdigest();m.verify_hashes(Path(d),{'IDENTITY.json':digest})
            p.write_text('{"stale":true}\n')
            with self.assertRaises(ValueError):m.verify_hashes(Path(d),{'IDENTITY.json':digest})

if __name__=='__main__':unittest.main()
