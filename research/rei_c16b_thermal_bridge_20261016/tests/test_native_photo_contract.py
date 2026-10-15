import sys
from pathlib import Path
import unittest,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import source_aware as s
import native_photo_contract as n
class NativePointTests(unittest.TestCase):
    def test_mapping_electron_and_two_way_photo_ownership(self):
        gas=s.Gas(.9,.1,.02,.05,.01)
        x=n.photo_point(s.State((s.Node(18.,-.5,.12),s.Node(50.,.3,.23),s.Node(80.,.7,.18)),gas),1e-3)
        self.assertAlmostEqual(x.mapped_fractions[0],.1)
        self.assertAlmostEqual(x.mapped_fractions[1],.05/.08)
        self.assertAlmostEqual(x.mapped_fractions[2],.01/.08)
        self.assertAlmostEqual(x.n_he_over_n_h,.08)
        self.assertTrue(all(v>=0 for v in x.gamma_s))
        self.assertTrue(all(v>=0 for v in x.heat_erg_per_absorber_s))
        self.assertAlmostEqual(x.photon_energy_loss_ev_per_h_s,
                               x.photo_heat_ev_per_h_s+x.photo_binding_ev_per_h_s,
                               delta=1e-20)
        self.assertLess(abs(x.binding_heat_energy_residual_ev_per_h_s),1e-20)
        self.assertLess(abs(x.photon_event_residual),1e-25)
    def test_gamma_per_absorber_independent_of_gas_state(self):
        nodes=(s.Node(60.,.2,.35),)
        x=n.photo_point(s.State(nodes,s.Gas(1.,0.,.08,0.,0.)),.002)
        y=n.photo_point(s.State(nodes,s.Gas(.2,.8,.01,.02,.05)),.002)
        self.assertEqual(x.gamma_s,y.gamma_s)
        self.assertEqual(x.heat_erg_per_absorber_s,y.heat_erg_per_absorber_s)
        self.assertNotEqual(x.photo_events_per_h_s,y.photo_events_per_h_s)
    def test_n_h_density_linear_gamma(self):
        x=n.photo_point(s.State((s.Node(60.,0.,.1),),s.Gas(.8,.2,.04,.02,.02)),.001)
        y=n.photo_point(s.State((s.Node(60.,0.,.1),),s.Gas(.8,.2,.04,.02,.02)),.003)
        for a,b in zip(x.gamma_s,y.gamma_s):self.assertAlmostEqual(b,3*a,delta=1e-20)
    def test_below_all_fit_threshold_zero(self):
        x=n.photo_point(s.State((s.Node(12.,0.,.8),),s.Gas(1.,0.,.08,0.,0.)),.001)
        self.assertEqual(x.gamma_s,(0.,0.,0.))
        self.assertEqual(x.heat_erg_per_absorber_s,(0.,0.,0.))
    def test_physical_fit_vs_nist_binding(self):
        x=n.photo_point(s.State((s.Node(13.6,0.,.1),),s.Gas(.8,.2,.08,0.,0.)),.001)
        self.assertGreater(x.gamma_s[0],0.)
        self.assertGreater(x.heat_erg_per_absorber_s[0],0.)
        self.assertEqual(x.gamma_s[1],0.)
    def test_invalid_proper_units(self):
        st=s.State((s.Node(30.,0.,.05),),s.Gas(.8,.2,.08,0.,0.))
        with self.assertRaises(ValueError): n.photo_point(st,0.)
        with self.assertRaises(ValueError): n.photo_point(st,float('nan'))
    def test_he_absent_interface(self):
        st=s.State((s.Node(80.,.4,.1),),s.Gas(.8,.2,0.,0.,0.))
        x=n.photo_point(st,1e-3)
        self.assertEqual(x.n_he_over_n_h,0.)
        self.assertEqual(x.mapped_fractions[1:],(0.,0.))
        self.assertEqual(x.photo_events_per_h_s[1:],(0.,0.))
    def test_photo_rates_are_point_derivative(self):
        st=s.State((s.Node(27.,.5,.3),s.Node(110.,-.3,.07)),s.Gas(.8,.2,.04,.03,.01))
        p=n.photo_point(st,.001)
        after,led=s.evolve(st,1e6,.001)
        for observed,pred in zip(led.photo_events,p.photo_events_per_h_s):
            self.assertAlmostEqual(observed/1e6,pred,delta=2e-16)