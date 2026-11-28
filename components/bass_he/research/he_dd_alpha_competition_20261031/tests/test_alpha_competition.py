import unittest, math, sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from alpha_competition import *
from transport import sigma_kn_independent, sigma_kn

class AlphaCompetitionPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=solve_cascade(10000.,'rice',delta_E=2,nquad=96)
        cls.r220=next(r for r in cls.rows if r['E_inj_MeV']==220)
    def test_source_fit_thresholds(self):
        for k,v in SOURCES.items():
            q=v[1]
            self.assertEqual(sigma_cyburt_cm2(q,k),0)
            self.assertEqual(sigma_cyburt_cm2(q-.5,k),0)
            self.assertGreater(sigma_cyburt_cm2(q+1,k),0)
    def test_cross_section_unit_and_direct_formula(self):
        # Form A mb Q^a (E-Q)^b/E^(a+b), independent direct expression.
        E=220.;A,q,a,b=SOURCES['npD']
        exact=A*1e-27*q**a*(E-q)**b/E**(a+b)
        self.assertAlmostEqual(sigma_cyburt_cm2(E,'npD')/exact,1,places=13)
    def test_source_nuclear_multiplicity(self):
        r=self.r220
        self.assertAlmostEqual(r['N_D_birth_per_gamma'],2*r['P_dd']+r['P_npD'],places=17)
    def test_baryon_number_from_alpha(self):
        r=self.r220
        total=(r['N_p_from_alpha_per_gamma']+r['N_n_from_alpha_per_gamma']+2*r['N_D_birth_per_gamma']+3*r['N_T_birth_per_gamma']+3*r['N_He3_birth_per_gamma'])
        self.assertAlmostEqual(total,4*r['P_alpha_photo_total'],delta=1e-15)
    def test_charge_from_alpha(self):
        r=self.r220
        charge=r['N_p_from_alpha_per_gamma']+r['N_D_birth_per_gamma']+r['N_T_birth_per_gamma']+2*r['N_He3_birth_per_gamma']
        self.assertAlmostEqual(charge,2*r['P_alpha_photo_total'],delta=1e-15)
    def test_probability_normalization(self):
        for r in self.rows:
            self.assertLess(r['P_normalization_abs_error'],2e-9)
            self.assertTrue(0<=r['P_total']<1+1e-9)
    def test_projectile_energy_ledger(self):
        for r in self.rows:
            self.assertLess(r['E_ledger_rel_error'],2e-9)
    def test_photo_nuclear_positive_and_dominance(self):
        r=self.r220
        self.assertGreater(r['P_npD'],100*r['P_dd'])
        self.assertGreater(r['P_pT'],0)
        self.assertGreater(r['P_nHe3'],0)
    def test_KN_kernel_pdf(self):
        self.assertLess(self.r220['KN_pdf_max_normalization_abs_error'],1e-9)
    def test_KN_exact_total_independent_angular(self):
        self.assertLess(abs(sigma_kn_independent(220)/sigma_kn(220)-1),1e-9)
    def test_rice_only_exclusive_source_not_switch(self):
        self.assertAlmostEqual(sigma_rice_dd_cm2(220)/1e-33,4.34,places=12)
        ratio=sigma_rice_dd_cm2(220)/sigma_cyburt_cm2(220,'dd_cyburt_extrap')
        self.assertGreater(ratio,1000)
    def test_source_switch_sign(self):
        cy=solve_cascade(10000.,'cyburt_extrap',delta_E=2,nquad=96)
        cy220=next(x for x in cy if x['E_inj_MeV']==220)
        self.assertLess(cy220['P_dd'],self.r220['P_dd'])
        self.assertAlmostEqual(cy220['P_npD'],self.r220['P_npD'],delta=2e-9)
    def test_input_guard(self):
        with self.assertRaises(ValueError):rates(300,10000)
        with self.assertRaises(ValueError):rates(220,10000,'invented')
        with self.assertRaises(ValueError):solve_cascade(10000,'rice',3)
    def test_positivity_of_all_rows(self):
        for r in self.rows:
            for k,v in r.items():
                if k.startswith(('P_','N_','E_','K_')) and isinstance(v,(float,int)):
                    self.assertGreaterEqual(v,-1e-10)
    def test_grid_refinement(self):
        r1=next(x for x in solve_cascade(10000.,'rice',1.,96) if x['E_inj_MeV']==220)
        for key in ('P_dd','P_npD','P_pT','P_nHe3','N_D_birth_per_gamma'):
            self.assertLess(abs(r1[key]/self.r220[key]-1),.006,key)

if __name__=='__main__':unittest.main()
