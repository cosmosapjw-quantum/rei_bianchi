"""Fixed source, no new IVP, source-defined budget consistency tests."""
import hashlib
import json
import unittest
from pathlib import Path
import numpy as np
from code import budget_cone as bc

class BoundedSpectrum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.net,cls.E,cls.M,cls.sig,cls.rows=bc.inputs()

    def test_01_original_sha_lock(self):
        bc.inputs()
        self.assertEqual(hashlib.sha256((bc.ROOT/'source/PR270_IMMUTABLE_FULL.zip').read_bytes()).hexdigest(),bc.PIN)

    def test_02_original_rates_and_grid(self):
        self.assertEqual(self.M.shape,(6,71))
        self.assertTrue(np.all(self.E>=5) and np.all(self.E<=200))
        self.assertEqual(len(self.rows),7)

    def test_03_bass_number_and_energy(self):
        N,W,phi=bc.budgets(self.net,self.E,3.603019593287379)
        self.assertGreater(N,1e10)
        self.assertGreater(W,2e11)
        self.assertAlmostEqual(float(self.E@phi),W,delta=W*1e-14)
        self.assertGreater(min(phi),0)

    def test_04_nonnegative_witness_8_constraints(self):
        z=self.rows[3]['z'];target=bc.sw.target_six(z)
        N,W,_=bc.budgets(self.net,self.E,z)
        A,b=bc.constraints(self.E,self.M,target,N,W)
        self.assertEqual(A.shape,(8,71))
        self.assertEqual(np.linalg.matrix_rank(A),8)
        p=bc.solve(A,b,self.sig[13]*bc.sw.FLUX_UNIT/bc.RATE_SCALE,'min')
        active=np.array(p['active']);flux=np.zeros(71);flux[active]=p['flux_active_m2_s']
        self.assertAlmostEqual(float(np.sum(flux)),N,delta=N*2e-9)
        self.assertAlmostEqual(float(self.E@flux),W,delta=W*2e-9)
        np.testing.assert_allclose(self.M@flux,target,rtol=2e-9)

    def test_05_endpoints_seven_z(self):
        for row in self.rows:
            r=bc.solve_at_z(row['z'],self.net,self.E,self.M,self.sig)
            self.assertGreater(r['LiI_min']['gamma_s'],0)
            self.assertLess(r['LiI_min']['gamma_s'],r['LiI_max']['gamma_s'])
            self.assertEqual(len(r['LiI_min']['active']),8)
            self.assertEqual(len(r['LiI_max']['active']),8)
            self.assertLess(r['LiI_min']['scaled_primal_residual'],2e-9)
            self.assertLess(r['LiI_max']['scaled_primal_residual'],2e-9)

    def test_06_unbounded_blind_ray_removed_by_number_budget(self):
        z=self.rows[3]['z'];target=bc.sw.target_six(z)
        p=bc.sw.nonnegative_witness(self.M,target)
        blind=bc.sw.li_blind_witness(self.E,self.M,self.sig,p['flux'])
        j=blind['index'];self.assertTrue(np.all(self.M[:,j]==0))
        self.assertGreater(self.sig[13,j],0)
        self.assertGreater(blind['delta_photon_flux_m2_s'],0)
        self.assertGreater((self.E[j]*blind['delta_photon_flux_m2_s']),0)

    def test_07_simple_global_photon_budget_bound(self):
        for row in self.rows:
            z=row['z'];r=bc.solve_at_z(z,self.net,self.E,self.M,self.sig)
            bound=np.max(self.sig[13])*r['original_BASS_N_m2_s']
            self.assertLessEqual(r['LiI_max']['gamma_s'],bound*(1+1e-10))

    def test_08_original_rate_not_relabelled_p19(self):
        z=self.rows[3]['z'];target=bc.sw.target_six(z)
        _,_,orig=bc.budgets(self.net,self.E,z)
        actual=self.M@orig
        self.assertGreater(np.max(abs(actual[:3]/target[:3]-1)),0.1)

    def test_09_invalid_input_and_no_z20(self):
        with self.assertRaises(ValueError):bc.sw.target_six(20)
        with self.assertRaises(ValueError):bc.constraints(self.E,self.M,np.ones(6),-1,2)
        with self.assertRaises(ValueError):bc.constraints(self.E,self.M,np.ones(6),1,0)
        with self.assertRaises(KeyError):bc.solve(np.eye(8),np.ones(8),np.ones(8),'other')

    def test_10_effect_on_lithium_source_only(self):
        row=self.rows[3];r=bc.solve_at_z(row['z'],self.net,self.E,self.M,self.sig)
        yLi0=float(row['y'][13])
        self.assertGreater(yLi0,0)
        self.assertGreater(yLi0*r['LiI_max']['gamma_s'],yLi0*r['LiI_min']['gamma_s'])

    def test_11_observed_original_li_is_not_compatibility_proof(self):
        r=bc.solve_at_z(self.rows[3]['z'],self.net,self.E,self.M,self.sig)
        self.assertGreater(r['original_BASS_LiI_rate_s'],r['LiI_min']['gamma_s'])
        self.assertLess(r['original_BASS_LiI_rate_s'],r['LiI_max']['gamma_s'])
        self.assertGreater(np.max(np.abs((self.M@bc.budgets(self.net,self.E,self.rows[3]['z'])[2])/np.array(r['P19_six_targets'])-1)),0.1)

    def test_12_results_machine_readable_no_ivp(self):
        r=bc.run()
        self.assertEqual(r['new_IVPs'],0)
        self.assertEqual(r['physical_fast'],'4/7')
        self.assertEqual(len(r['cases']),7)

if __name__=='__main__':unittest.main()
