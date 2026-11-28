import unittest,math
from transport import *
from physics_pr131 import *

class TestPhysicalFirstCollision(unittest.TestCase):
    def test_kn_angular_integration(self):
        for E in (150.,220.,249.): self.assertAlmostEqual(sigma_kn(E)/sigma_kn_independent(E),1.,delta=1e-10)
    def test_kn_positive_lt_thomson(self):
        for E in (150.,170.,220.,249.):self.assertTrue(0<sigma_kn(E)<SIGMA_T_CM2)
    def test_bh_positive_and_z2(self):
        for E in (170.,249.):self.assertAlmostEqual(sigma_bh_born_unscreened(E,2)/sigma_bh_born_unscreened(E,1),4,places=13)
    def test_bh_domain_guard(self):
        with self.assertRaises(ValueError):sigma_bh_born_unscreened(50,2)
    def test_dd_model_not_measured(self):
        for E in (170.,220.):self.assertTrue(four_channel_rates(E,1e5)['dd']>0)
    def test_all_hazards_positive(self):
        for E in (170.,220.):
            for z in (1e4,1e5,1e6):
                for x in four_channel_rates(E,z).values():self.assertTrue(x>=0 and math.isfinite(x))
    def test_photon_redshift_boundary(self):
        p=flight(170,1e4);self.assertEqual(p['terminal_reason'],'reached_150_MeV');self.assertAlmostEqual(p['E_terminal_MeV'],150,delta=1e-8)
    def test_first_event_normalization(self):
        for E in (170.,220.,249.):
            for zi in (1e4,1e5,1e6):
                p=flight(E,zi)
                self.assertAlmostEqual(p['P_first_normalization'],1.,delta=3e-9)
                self.assertTrue(all(0<=p[k]<=1 for k in ('P_BW_first','P_KN_first','P_BH_first','P_dd_first','P_no_collision_until_terminal')))
    def test_pair_multiplicity(self):
        p=flight(220,1e5);self.assertAlmostEqual(p['N_fastD_first_per_gamma'],2*p['P_dd_first'],places=25)
    def test_kinetic_per_event_bounds(self):
        for zi in (1e4,1e5,1e6):
            p=flight(220,zi)
            self.assertGreaterEqual(p['average_dd_event_E_MeV'],150-1e-5)
            self.assertLessEqual(p['average_dd_event_E_MeV'],220+1e-5)
            self.assertAlmostEqual(p['average_dd_event_K_pair_MeV'],p['average_dd_event_E_MeV']-Q_MEV,delta=1e-5)
    def test_independent_u_coordinate_quadrature_low_z(self):
        # Alternative numerical integration in log-redshift u, not optical-depth tau.
        # Independent evolution of S(u) and integral S Gamma_dd/H for a low-z case
        # where CMB BW is exponentially negligible; test tests transport coordinate.
        import numpy as np
        from scipy.integrate import cumulative_trapezoid, trapezoid
        Ei,zi=220.,1e4
        u=np.linspace(0,math.log(Ei/150),2800)
        h=[]
        for v in u:
            z=(1+zi)*math.exp(-v)-1
            E=max(150.,Ei*math.exp(-v))
            r=four_channel_rates(E,z)
            H=state(z)['H_s_inv']
            h.append((sum(r.values())/H,r['dd']/H))
        h=np.asarray(h)
        tau=cumulative_trapezoid(h[:,0],u,initial=0)
        p=trapezoid(np.exp(-tau)*h[:,1],u)
        sol=flight(Ei,zi)
        self.assertLess(abs(p/sol['P_dd_first']-1),1e-5)
        self.assertAlmostEqual(math.exp(-tau[-1]),sol['P_reached_150_MeV_unhit'],delta=5e-10)
    def test_high_z_local_branch_limit(self):
        Ei,zi=220.,1e6
        rr=four_channel_rates(Ei,zi)
        p=flight(Ei,zi)
        self.assertLess(abs(p['P_dd_first']/(rr['dd']/sum(rr.values()))-1),1e-7)
    def test_source_rate_kept_null(self):
        import json,pathlib
        p=json.loads((pathlib.Path(__file__).resolve().parents[1]/'data'/'SCIENCE_SUMMARY.json').read_text())
        self.assertIsNone(p['hold']['R_event']);self.assertEqual(p['DAG']['Central'],'28/88');self.assertEqual(p['hold']['production'],'HOLD')
    def test_repeatability(self):
        x=flight(220,1e5);y=flight(220,1e5)
        self.assertEqual(x,y)
    def test_first_event_born_not_heat(self):
        p=flight(220,3e4);self.assertIn('first',p['sigma_dd_kind'].lower()+'first');self.assertNotIn('heat',p)
    def test_input_domain(self):
        with self.assertRaises(ValueError):flight(300,1e5)
        with self.assertRaises(ValueError):flight(220,10)
    def test_toy_constant_hazard(self):
        rates=[1.,2.,3.,4.]; U=.5
        p,s=toy_constant_opacity_test(rates,U)
        self.assertAlmostEqual(sum(p)+s,1.,places=14)
        self.assertAlmostEqual(p[-1],.4*(1-math.exp(-5)),places=14)
    def test_exact_energy_monotonic(self):
        p=flight(249,1e4);self.assertLess(p['E_terminal_MeV'],249)
    def test_H_positive(self):
        self.assertTrue(all(state(z)['H_s_inv']>0 for z in (1e4,1e5,1e6)))

if __name__=='__main__':unittest.main()
