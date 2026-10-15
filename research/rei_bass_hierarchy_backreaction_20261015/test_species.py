#!/usr/bin/env python3
"""Real photon+massless-neutrino coupled Einstein hierarchy physics regressions."""
from pathlib import Path
import math
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015"))
from species_hierarchy import SpeciesHierarchy
from run_hierarchy import source_lock,actual_electrons,public_sigma_from_q
from einstein_vlasov import Initial,KineticStressBackground

class SourcePartition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=source_lock()
        cls.donor,_=actual_electrons(Path.home()/"Dropbox/bianchi/rei_bianchi")
    def test_no_double_radiation_background_energy(self):
        m=SpeciesHierarchy(self.c,2.7255,8)
        self.assertAlmostEqual(m.f_gamma+m.f_nu,1,delta=1e-15)
        self.assertAlmostEqual(m.omega_gamma+m.omega_nu,self.c.omega_r,delta=1e-21)
        self.assertTrue(.5<m.f_gamma<.7)
        w=m.fields(0,m.initial_state())
        self.assertEqual(w["Pi_gamma_J_m3"],0)
        self.assertEqual(w["Pi_nu_J_m3"],0)
    def test_initial_quadrupole_species_pi_correct_normalization(self):
        m=SpeciesHierarchy(self.c,2.7255,8,kappa_gamma=.2,kappa_nu=-.2)
        y=m.initial_state();p=m.fields(0,y)
        energyγ=(m.omega_gamma/self.c.aref**4)*self.c.rhocrit_j_m3
        energyν=(m.omega_nu/self.c.aref**4)*self.c.rhocrit_j_m3
        self.assertAlmostEqual(p["Pi_gamma_J_m3"]/energyγ,.2/15,delta=1e-13)
        self.assertAlmostEqual(p["Pi_nu_J_m3"]/energyν,-.2/15,delta=1e-13)
    def test_BASS_PR159_identity_when_both_species_no_collisions(self):
        for q,k in ((0,.2),(.005,.2),(-.005,-.2)):
            sigma,ori=public_sigma_from_q(q)
            m=SpeciesHierarchy(self.c,2.7255,8,Sigma_ref=sigma,
                               orientation=ori,kappa_gamma=k,kappa_nu=k)
            sol,diag,_=m.integrate(n=131)
            bass=KineticStressBackground(Initial(q,k))
            target=bass.at_a(.2)
            self.assertAlmostEqual(sol.y[1,-1],target["b"],delta=1e-10)
            self.assertAlmostEqual(diag[-1]["Sigma"],
                 math.sqrt(3)*abs(target["s_per_s"])/target["h_per_s"],delta=1e-10)
            self.assertAlmostEqual(diag[-1]["Pi_radiation_J_m3"],
                  target["pi_energy_over_crit_today"]*self.c.rhocrit_j_m3,
                  delta=1e-20)
    def test_cmb_only_scattering_neutrino_has_no_direct_collision(self):
        control=SpeciesHierarchy(self.c,2.7255,8,kappa_gamma=.2,kappa_nu=.2)
        collided=SpeciesHierarchy(self.c,2.7255,8,kappa_gamma=.2,kappa_nu=.2,
                                  ne_source=self.donor)
        init=control.initial_state()
        x=control.source.xmax*.5
        w=collided.fields(x,init)
        dy0=control.rhs(x,init);dy1=collided.rhs(x,init)
        n=collided.n
        self.assertTrue(np.array_equal(dy0[4+2*n:4+4*n],dy1[4+2*n:4+4*n]))
        self.assertLess(dy1[4+2],dy0[4+2])
        self.assertEqual(dy1[4],dy0[4])
        self.assertEqual(dy1[4+n],dy0[4+n])
        self.assertGreater(w["GammaT"],0)
    def test_full_N0_gamma_and_nu_conserved_positive_and_pi_source(self):
        for k in (-.2,0,.2):
            m=SpeciesHierarchy(self.c,2.7255,8,kappa_gamma=k,kappa_nu=-k,ne_source=self.donor)
            sol,info,_=m.integrate(n=151)
            self.assertTrue(all(abs(w["N_gamma"][0]-1)<2e-12 and abs(w["N_nu"][0]-1)<2e-12 for w in info))
            self.assertTrue(all(abs(w["Pi_radiation_J_m3"]-
                (w["Pi_gamma_J_m3"]+w["Pi_nu_J_m3"]))<1e-22 for w in info))
    def test_original_ax08_scoped_electron_donor_error_separately(self):
        self.assertLess(self.donor.max_relative_source_error,3e-4)
        self.assertGreater(self.donor.max_relative_source_error,1e-6)
        self.assertTrue(np.all(self.donor.density(np.exp(self.donor.x))>0))
    def test_invalid_species_quadrupole_and_viscosity_rejected(self):
        with self.assertRaises(ValueError):SpeciesHierarchy(self.c,2.7255,8,kappa_gamma=.9)
        with self.assertRaises(ValueError):SpeciesHierarchy(self.c,2.7255,8,kappa_nu=-.9)
        with self.assertRaises(ValueError):SpeciesHierarchy(self.c,2.7255,8,Sigma_ref=.02,orientation=0)
        with self.assertRaises(ValueError):SpeciesHierarchy(self.c,2.7255,8,matter_nu_viscosity=-.1)
        with self.assertRaises(ValueError):SpeciesHierarchy(self.c,3.0,8)
if __name__=="__main__":
    unittest.main(verbosity=2)
