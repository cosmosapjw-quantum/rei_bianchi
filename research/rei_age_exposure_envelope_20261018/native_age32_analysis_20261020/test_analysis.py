import copy
import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext
import analysis as a

class StoredTests(unittest.TestCase):
    def fixture(self,root):
        def put(name,obj): (root/(name+'.json')).write_text(json.dumps(obj))
        def state(n,p=0): return dict(N=n,ledgers=[0.]*4+[p,0.,0.]+[0.]*7)
        setup=dict(birth_count=2,births=[1.,2.],source_inventory=[[1.,20.],[2.,40.]],extra=14,x1=3.)
        put('setup',setup);put('endpoint',state(2.5,1.));put('ledgers',dict(photon_normalized=.1));put('solver_return',dict(status='COMPLETE',intervals=[]))
        rows=[dict(event=0,x=1.,active_before=0,active_after=1,source_inventory=setup['source_inventory'][0],status='AVAILABLE',pre=state(0),post=state(1.25)),dict(event=1,x=2.,active_before=1,active_after=2,source_inventory=setup['source_inventory'][1],status='AVAILABLE',pre=state(.5,.5),post=state(2.25,.5))]
        put('source_jumps',dict(records=rows));return rows
    def test_exact_cancel_and_nonzero_jumps(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);self.fixture(p)
            r=a.photon_history(p,dict(status='VERIFIED',N_initial=0,photo_initial=[0,0,0]))
            self.assertEqual(r['status'],'AVAILABLE');self.assertTrue(r['exact_zero_telescope_residual'])
            self.assertEqual(r['jumps']['signed_sum']['decimal80'],'0');self.assertEqual(r['jumps']['L1']['decimal80'],'0.5')
            self.assertEqual(r['continuous']['signed_sum']['decimal80'],'0.5')
    def test_missing_wrong_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);rows=self.fixture(p);initial=dict(status='VERIFIED',N_initial=0,photo_initial=[0,0,0])
            for bad,expected in [(rows[:1],'INCOMPLETE'),([rows[0],rows[0]],'INVALID')]:
                (p/'source_jumps.json').write_text(json.dumps(dict(records=bad)))
                self.assertEqual(a.photon_history(p,initial)['status'],expected)
            for key,value in [('x',1.5),('active_before',3),('source_inventory',[9.,20.])]:
                bad=copy.deepcopy(rows);bad[0][key]=value;(p/'source_jumps.json').write_text(json.dumps(dict(records=bad)))
                self.assertEqual(a.photon_history(p,initial)['status'],'INVALID')
    def test_initial_provenance_required(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);self.fixture(p)
            self.assertEqual(a.photon_history(p)['status'],'INCOMPLETE')
    def test_variance_scale_and_zero(self):
        e=dict(N=2.,U=4.,proper_time_s=1e15,cohorts=[[1.,2.],[1.,2.]])
        r=a.survivor_moments(e,[1e15-4,1e15-2]);self.assertEqual(r['N']['mean_age_s'],3);self.assertEqual(r['N']['variance_age_s2'],1)
        e.update(N=0.,U=0.,cohorts=[[0.,0.],[0.,0.]])
        self.assertEqual(a.survivor_moments(e,[0.,1.])['N']['status'],'UNDEFINED')
    def test_tail_endpoint_mismatch_and_missing_crosscheck(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);self.fixture(p)
            initial=dict(status='VERIFIED',N_initial=0,photo_initial=[0,0,0])
            (p/'solver_return.json').write_text(json.dumps(dict(status='COMPLETE',intervals=[dict(event=2,x=3.,active=2,N=2.5)])))
            np.save(p/'accepted_coordinates_event2.npy',[0.]*4+[0.]*4+[1.,0.,0.]+[0.]*7)
            r=a.photon_history(p,initial);self.assertEqual(r['status'],'AVAILABLE')
            self.assertEqual(len(r['crosschecks']),3);self.assertEqual(r['crosschecks'][-1]['status'],'VERIFIED')
            end=json.loads((p/'endpoint.json').read_text());end['N']*=2
            (p/'endpoint.json').write_text(json.dumps(end))
            self.assertEqual(a.photon_history(p,initial)['status'],'INVALID')
            end['N']=2.5;end['ledgers'][4]=2.
            (p/'endpoint.json').write_text(json.dumps(end))
            self.assertEqual(a.photon_history(p,initial)['status'],'INVALID')
            (p/'accepted_coordinates_event2.npy').unlink()
            r=a.photon_history(p,initial)
            self.assertEqual(r['crosschecks'][-1]['status'],'MISSING_CROSSCHECK')
    def test_scaled_exponential_products(self):
        with localcontext() as ctx:
            ctx.prec=100
            expected=float(Decimal.from_float(1e300)*Decimal(-1000).exp())
            self.assertTrue(math.isclose(a.source_step(1e300,0,1,1000)['n1'],expected,rel_tol=2e-13))
            x=Decimal(1491)
            expected=float(x/((x/2).exp()-(-x/2).exp()))
            self.assertGreater(expected,0.)
            self.assertLessEqual(abs(a.midpoint_ratio(1491)-expected),math.ulp(expected))
    def test_source_step_limits_positive_ledger(self):
        self.assertEqual(a.source_step(3,2,4,0),dict(n1=11.,absorbed=0.))
        for x in [1e-16,1e-8,.1,1,100,1000]:
            s=a.source_step(3,2,1,x)
            self.assertGreaterEqual(s['absorbed'],0);self.assertGreaterEqual(s['n1'],0)
            self.assertTrue(math.isclose(s['n1']+s['absorbed'],5,rel_tol=2e-16))
        self.assertAlmostEqual(a.source_step(3,2,1,1000)['n1'],.002)
    def test_decimal100_and_finite_sum(self):
        with localcontext() as ctx:
            ctx.prec=100
            for v in [0,1e-8,.1,1,10,100,1000]:
                x=Decimal.from_float(float(v))
                ref=Decimal(1) if x==0 else x/((x/2).exp()-(-x/2).exp())
                got=a.midpoint_ratio(v)
                self.assertTrue(math.isclose(got,float(ref),rel_tol=4e-15,abs_tol=5e-324),(v,got,ref))
                ratio=2/((x/4).exp()+(-x/4).exp())
                self.assertTrue(math.isclose(a.paired_ratio(v),float(ratio),rel_tol=4e-15,abs_tol=5e-324))
                self.assertTrue(math.isclose(a.paired_defect(v),float(1-ratio),rel_tol=4e-15,abs_tol=5e-324))
                if v:
                    m=7
                    mid=sum((-x*(Decimal(m)-Decimal(j)-Decimal('.5'))).exp() for j in range(m))
                    cont=(1-(-m*x).exp())/x
                    self.assertTrue(math.isclose(got,float(mid/cont),rel_tol=4e-15,abs_tol=5e-324))
                else: self.assertEqual(got,1.)
    def test_root_bracket(self):
        for eps in [1e-16,.005,.1,.9]:
            r=a.exposure_limits(eps,2)
            lo,hi=r['continuum_bracket']
            with localcontext() as ctx:
                ctx.prec=100
                def independent_defect(v):
                    x=Decimal.from_float(v)
                    return Decimal(1)-x/((x/2).exp()-(-x/2).exp())
                target=Decimal.from_float(eps)
                self.assertLessEqual(independent_defect(lo),target)
                self.assertGreaterEqual(independent_defect(hi),target)
            self.assertTrue(math.isclose(a.paired_defect(r['paired_limit']),eps,rel_tol=1e-14))
    def test_actual32_all_crosschecks_and_legacy64(self):
        if not os.environ.get('REI_V9_DATA32'):
            self.skipTest('Explicit actual data paths not supplied')
        data32=Path(os.environ['REI_V9_DATA32']);data64=Path(os.environ['REI_V9_DATA64'])
        r=a.photon_history(data32)
        self.assertEqual(r['status'],'AVAILABLE');self.assertEqual(r['birth_count'],32)
        self.assertEqual(len(r['crosschecks']),33)
        self.assertTrue(all(c['status']=='VERIFIED' for c in r['crosschecks']))
        self.assertTrue(r['exact_zero_telescope_residual'])
        diagnosis=a.diagnose(data32)
        self.assertEqual(diagnosis['source_jumps']['provenance'],'EXPLICIT_SOURCE_JUMPS_JSON')
        self.assertEqual(len(diagnosis['source_jumps']['records']),32)
        old=a.photon_history(data64)
        self.assertEqual(old['status'],'INCOMPLETE');self.assertIsNone(old['telescope'])
        self.assertNotIn('provenance',old['legacy_observation_diagnosis']['source_jumps'])
    def test_output_nonempty_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'preserve.txt').write_text('preserve')
            with self.assertRaisesRegex(ValueError,'NONEMPTY_OUTPUT'):
                a.run(p,p,p)
            self.assertEqual((p/'preserve.txt').read_text(),'preserve')
    def test_paired_budget_exact(self):
        e=lambda n,p:dict(N=n,ledgers=[0.]*4+[p,0.,0.])
        r=a.paired_budget(e(.5,.75),e(.25,.5),[1.],[.8])
        self.assertEqual(r['exact_identity_residual']['decimal80'],'0')

if __name__=='__main__':unittest.main()
