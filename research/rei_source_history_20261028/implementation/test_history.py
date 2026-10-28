"""Targeted new history/coupling checks. No IVP calls or old campaign tests."""
import json
import unittest
import numpy as np
from history import UNIT,old,baseline,diagnose,clock,affine_reservoir,envelope_step,five_fixed_point
from coupled import Coupled,dynamic_new


class HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=baseline();cls.c=old.config();cls.d=diagnose(cls.data,cls.c)
        cls.model=Coupled(cls.data)

    def test_clock_and_input_mapping(self):
        d=self.data
        self.assertEqual(d['t'].shape,(201,));self.assertEqual(d['t'][0],0)
        self.assertTrue(np.all(np.diff(d['t'])>0))
        eta=np.array([0.,.2,.7,1.]);H=np.full(4,2.)
        t,_=clock(eta,H);np.testing.assert_allclose(t,eta/2,rtol=3e-15,atol=0)
        self.assertEqual(tuple(old.LABELS[-4:]),('Li7_0','Li7_1','Li7_2','Li7_3'))
        self.assertEqual(self.model.photo.shape,(201,6))
        self.assertLessEqual(max(self.model.bath_metadata['max_relative_H_nref_mismatch']),1e-10)

    def test_affine_scalar_and_zero_input_limits(self):
        B0,S0,slope,L,t=2.,3.,.4,.7,1.3
        expected=np.exp(-L*t)*B0+S0*(1-np.exp(-L*t))/L+slope*(t/L-(1-np.exp(-L*t))/L**2)
        self.assertAlmostEqual(affine_reservoir(B0,S0,slope,L,t),expected,places=14)
        self.assertEqual(affine_reservoir(B0,S0,slope,0,t),B0+S0*t+slope*t*t/2)
        self.assertAlmostEqual(affine_reservoir(B0,0,0,L,t),B0*np.exp(-L*t),places=14)
        np.testing.assert_allclose(affine_reservoir(B0,S0,slope,1e-10,t),B0+S0*t+slope*t*t/2,rtol=2e-10)

    def test_initial_mismatch_and_envelope_logic(self):
        np.testing.assert_array_equal(self.d['relative'][0],[1.,1.])
        self.assertFalse(self.d['certified'][0].any())
        self.assertAlmostEqual(envelope_step(1.,0.,2.,.5),np.exp(-1),places=15)
        # For u'=s-lambda*u with zero IC and constant fixed point, this bound
        # equals exact tracking error and crosses1% at ln100/lambda.
        self.assertAlmostEqual(envelope_step(1.,0.,2.,np.log(100)/2),.01,places=15)
        self.assertTrue(np.all(self.d['M']>=0));self.assertTrue(np.all(self.d['contraction']>0))

    def test_frozen_five_stock_residual(self):
        c=self.c
        for k in (0,100,200):
            x=self.d['fixed'][k];s=self.d['S'][k]
            r=old.reservoirs(self.data['y'][k],1.,c)
            q=old.qss(self.data['y'][k],self.data['nref'][k],1.,c,r)
            np.testing.assert_allclose(x,np.r_[r['B'],q['stocks']],rtol=3e-15,atol=0)
            self.assertLess(np.max(abs((s-r['L']*x[:2])/s)),1e-14)
        off=five_fixed_point(np.zeros(2),0.,{**c,'thermal_injection_per_Href_s':[0.]*17})
        np.testing.assert_array_equal(off,np.zeros(5))

    def test_dynamic_fast_energy_and_event_invariants(self):
        c=self.c;y=self.data['y'][100].copy();y[[0,5,6]]=[1e-20,1e-20,2e-20]
        B=np.array([2e-22,3e-20]);U=B*np.array([7e5,2e6])
        op,dU=dynamic_new(y,B,U,self.data['nref'][100],1.,c,True)
        res=old.reservoirs(y,1.,c)
        np.testing.assert_allclose(dU,res['P']-res['L']*U,rtol=1e-15)
        slow_power=op['transport_power']['slowing'].sum()
        self.assertAlmostEqual(slow_power/(c['ks_n_s']*U[0]+c['ks_T_s']*U[1]),1.,places=14)
        for event in op['events']:
            self.assertEqual(old.A@event['nu']+event['external_A'],0)
            self.assertEqual(old.Q@event['nu']-event['electron'],0)
        scale=sum(abs(x) for x in op['power'].values())
        self.assertLess(abs(op['energy_residual'])/scale,1e-14)
        with self.assertRaises(ValueError):dynamic_new(y,np.zeros(2),np.ones(2),self.data['nref'][0],1.,c,True)

    def test_coupled_rhs_static_structure(self):
        model=self.model
        for k in (0,100,200):
            G,n,hidden,hdot=model.fields(model.t[k])
            off=G.copy();np.fill_diagonal(off,0)
            self.assertTrue(np.all(off>=0))
            self.assertTrue(np.all(G[[0,5,6]]==0))
            np.testing.assert_allclose(old.A[:17]@G,np.zeros(17),atol=1e-26)
            rhs=model.rhs_physical(model.t[k],model.y0,'ON')
            self.assertTrue(np.isfinite(rhs).all())
            baryon=old.A@rhs[:19]+rhs[21]+6*hdot.sum()
            charge=old.Q@rhs[:19]+np.arange(4)@hdot-rhs[22]
            self.assertLess(abs(baryon),1e-25);self.assertLess(abs(charge),1e-25)
        # Snapshot finite difference of genuinely nonlinear n/H capture, no
        # trajectory integration. Its cross derivative must equal -nref*C.
        y=model.y0[:17].copy();y[0]=1e-15
        r0=dynamic_new(y,np.zeros(2),np.zeros(2),self.data['nref'][0],0.,self.c,False)[0]['rates']['capture_H1_0']
        h=1e-5;y[1]+=h
        r1=dynamic_new(y,np.zeros(2),np.zeros(2),self.data['nref'][0],0.,self.c,False)[0]['rates']['capture_H1_0']
        expected=self.data['nref'][0]*self.c['capture_C_cm3_s']*y[0]
        self.assertAlmostEqual((r1-r0)/h/expected,1.,delta=2e-10)

    def test_signed_trial_extension_jacobian_and_off_escape(self):
        m=self.model
        # Radau's initial energy finite-difference probes have U>0 with B=0.
        probe=m.y0.copy();probe[19]=1e-25
        self.assertTrue(np.isfinite(m.rhs_physical(0.,probe)).all())
        probe[0]=-1e-20;probe[17]=-1e-25
        self.assertTrue(np.isfinite(m.rhs_physical(0.,probe)).all())
        # Exact affine B column derivative agrees with signed central probes.
        x=m.y0.copy();h=1e-24
        plus=x.copy();minus=x.copy();plus[17]+=h;minus[17]-=h
        derivative=(m.rhs_physical(0.,plus)-m.rhs_physical(0.,minus))/(2*h)
        expected=-(self.c['ks_n_s']+self.c['ke_n_s']+self.c['lambda_n_s'])
        self.assertAlmostEqual(derivative[17]/expected,1.,places=14)
        # OFF has no fast escape even when a nonzero fast stock is supplied.
        off=m.new['OFF'];on=m.new['ON']
        self.assertAlmostEqual(off[4][0],self.c['ks_n_s']+self.c['lambda_n_s'],places=16)
        self.assertAlmostEqual(on[4][0]-off[4][0],self.c['ke_n_s'],places=16)
        # Compiled derivative agrees with the event operator at a nonnegative
        # dynamic snapshot, including source, capture and external boundaries.
        state=m.y0.copy();state[[0,5,6]]=[2e-20,3e-20,4e-20]
        state[17:19]=[1e-22,2e-20];state[19:21]=[5e-17,8e-14]
        G,n,_,hdot=m.fields(m.t[100])
        for mode in ('ON','OFF'):
            op,dU=dynamic_new(state[:17],state[17:19],state[19:21],n,1. if mode=='ON' else 0.,self.c,mode=='ON')
            actual=m.rhs_physical(m.t[100],state,mode)
            expected=np.r_[G@state[:17]+op['dy'][:17],op['dy'][17:19],dU]
            np.testing.assert_allclose(actual[:21],expected,rtol=2e-13,atol=1e-45)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(HistoryTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'IVP_execution':'NOT_RUN',
            'old_bath_metadata':getattr(HistoryTests,'model',None).bath_metadata if hasattr(HistoryTests,'model') else None}
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    (out/'TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
