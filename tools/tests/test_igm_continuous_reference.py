"""New source oracle contracts; written before implementation."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import igm_reference as old
from igm_compare import compare_rows

MODULE=Path(__file__).resolve().parent.parent/'igm_continuous_reference.py'
CFG=old.read_config(Path(__file__).resolve().parents[2]/'configs/igm_manufactured_v1.cfg')

def implementation():
    if not MODULE.exists():
        return None
    import igm_continuous_reference
    return igm_continuous_reference

class ContinuousSourceTests(unittest.TestCase):
    def setUp(self):
        self.ref=implementation()
        self.assertIsNotNone(self.ref,'continuous-source independent oracle has not been implemented')

    def test_fixed_rate_moments_against_independent_high_precision(self):
        from decimal import Decimal, localcontext
        for z in (0.,1e-12,1e-6,.1,1.,100.,1e6):
            with localcontext() as ctx:
                ctx.prec=65
                d=Decimal(str(z))
                phi=float((1-(-d).exp())/d) if z else 1.
                psi=float((d-1+(-d).exp())/(d*d)) if z else .5
            self.assertAlmostEqual(self.ref.phi(z),phi,delta=3e-15*abs(phi))
            self.assertAlmostEqual(self.ref.psi(z),psi,delta=3e-15*abs(psi))
            v=self.ref.fixed_rate_moments(.7,40.,.3,np.array([z/6,z/3,z/2]),1.)
            self.assertAlmostEqual(v['N']+sum(v['A']),1.,delta=2e-15)
            self.assertAlmostEqual(v['U']+sum(v['B'])+v['R'],40.,delta=1e-13)

    def test_adjacent_float_event_interval_retains_source_and_incoming_cutoff(self):
        left=-2.5
        right=np.nextafter(left,np.inf)
        source,active,channels=self.ref.segment_masks(np.array([left]),np.array([right]),np.array([[right,right,right]]),left,right)
        self.assertTrue(source[0])
        self.assertTrue(active[0])
        self.assertTrue(np.all(channels))

    def test_threshold_band_grid_splits_swept_support_edges(self):
        eta,w=self.ref.spectral_grid(CFG,2,2,grid='threshold-bands')
        s0,s1=-math.log1p(CFG['z_start']),-math.log1p(CFG['z_end'])
        lo,hi=s0+math.log(13.7),s1+math.log(100.)
        cuts=sorted({lo,hi,*[s+math.log(e) for s in (s0,s1) for e in (13.7,100.,*old.CUTOFF) if lo<s+math.log(e)<hi]})
        self.assertEqual(len(eta),4*(len(cuts)-1))
        for a,b in zip(cuts[:-1],cuts[1:]):
            inside=(eta>a)&(eta<b)
            self.assertEqual(inside.sum(),4)
            self.assertAlmostEqual(w[inside].sum(),b-a,delta=1e-15)
        self.assertTrue(np.all(w>0))
        with self.assertRaises(ValueError): self.ref.spectral_grid(CFG,2,grid='unsupported')

    def test_grid_and_source_jacobian_one_proper_time_conversion(self):
        ref=self.ref
        eta,weights=ref.spectral_grid(CFG,80,4)
        self.assertTrue(np.all(weights>0))
        self.assertEqual(len(eta),320)
        s=-math.log1p(CFG['z_start'])+.005
        q=ref.source_derivative(CFG,s,eta,weights)
        E=np.exp(eta-s)
        mask=(E>=13.7)&(E<=100)
        expected=weights[mask]*1e-15/(1/13.7-1/100)/E[mask]/old.background(CFG,s)['H']
        np.testing.assert_allclose(q[mask],expected,rtol=3e-15,atol=0)
        self.assertTrue(np.all(q[~mask]==0))

    def test_short_history_positive_and_original_budgets(self):
        cfg=dict(CFG,z_end=11.995,output_panels=2)
        result=self.ref.solve_history(cfg,spectral_panels=16,order=2,rtol=1e-11,atol=1e-14)
        self.assertTrue(result['stats']['completed'])
        self.assertTrue(compare_rows(result['rows'],result['rows'])['passed'])
        self.assertGreater(result['rows'][-1]['x_heii'],0)
        self.assertEqual(result['rows'][0]['Nactive'],0)
        self.assertTrue(all(r['emitted_N']>0 for r in result['rows'][1:]))
        self.assertTrue(np.all(result['nodes'][:,-1]>=0))

    def test_support_switch_outflow_and_sourcefree_logs(self):
        cfg=dict(CFG,z_end=11.999,output_panels=2,energy_min_ev=13.60001,energy_max_ev=13.6001)
        result=self.ref.solve_history(cfg,spectral_panels=4,rtol=1e-11,atol=1e-14)
        row=result['rows'][-1]
        self.assertGreater(row['out_N'],0.)
        self.assertAlmostEqual(row['out_E']/row['out_N'],13.60*old.EV,delta=1e-25)
        self.assertTrue(compare_rows(result['rows'],result['rows'])['passed'])
        self.assertLessEqual(result['stats']['accepted_number_budget_ratio'],1.)
        self.assertLessEqual(result['stats']['accepted_energy_budget_ratio'],1.)

    def test_source_below_hi_is_immediate_outflow_without_redshift(self):
        cfg=dict(CFG,z_end=11.999,output_panels=2,energy_min_ev=10.,energy_max_ev=12.)
        result=self.ref.solve_history(cfg,spectral_panels=4)
        row=result['rows'][-1]
        self.assertEqual(row['Nactive'],0.)
        self.assertEqual(row['out_N'],row['emitted_N'])
        self.assertAlmostEqual(row['out_E'],row['emitted_E'],delta=1e-28)
        self.assertEqual(row['redshift_E'],0.)
        self.assertTrue(compare_rows(result['rows'],result['rows'])['passed'])

    def test_zero_source_adiabatic_exact_neutral_boundary(self):
        cfg=dict(CFG,z_end=11.995,output_panels=2,source_rate=0.,x_hii=0.)
        result=self.ref.solve_history(cfg,spectral_panels=4)
        row=result['rows'][-1]
        self.assertEqual(row['Nactive'],0)
        self.assertEqual(row['x_heii'],0)
        self.assertAlmostEqual(row['T'],30*((1+cfg['z_end'])/13)**2,delta=1e-9)
        self.assertTrue(compare_rows(result['rows'],result['rows'])['passed'])

if __name__=='__main__': unittest.main()
