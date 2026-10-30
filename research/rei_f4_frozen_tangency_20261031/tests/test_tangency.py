import csv, sys, unittest
from pathlib import Path
import numpy as np
from scipy.integrate import simpson
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import build_physical_source as b

class SourceTangencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.stats,cls.arr,cls.info=b.compute()
        cls.parent,cls.original= b.locked_inputs()
        cls.DF=cls.arr[3]
    def test_01_owner_sha(self):
        self.assertEqual(b.sha256(b.MASTER) if hasattr(b,'sha256') else __import__('hashlib').sha256(b.MASTER.read_bytes()).hexdigest(),b.SHA)
    def test_02_epoch_and_shapes(self):
        self.assertEqual(len(self.rows),193)
        self.assertEqual(self.DF.shape,(193,21))
    def test_03_replacement_support_only(self):
        keep=set([1,2,10,11,12])
        self.assertEqual(np.max(np.abs(self.DF[:,[i for i in range(21) if i not in keep]])),0)
    def test_04_baryon_conservation(self):
        A=self.parent['A21'];self.assertLess(np.max(abs(self.DF@A)),1e-29)
        self.assertLess(self.stats['max_A_J_hybrid'],5e-21)
    def test_05_ionic_count_conservation(self):
        self.assertLess(np.max(abs(np.sum(self.DF,axis=1))),1e-29)
    def test_06_electron_charge_source(self):
        q=self.parent['q21'];by_charge=self.DF@q
        via_species=self.DF[:,2]+self.DF[:,11]+2*self.DF[:,12]
        self.assertLess(np.max(abs(by_charge-via_species)),1e-30)
        value=np.array([r['delta_electron_source_per_baryon_s'] for r in self.rows])
        self.assertLess(np.max(abs(value-by_charge)),1e-30)
    def test_07_binding_potential_identity(self):
        expr=(b.CHI_REI[0]*self.DF[:,2]+b.CHI_REI[1]*(self.DF[:,11]+self.DF[:,12])+b.CHI_REI[2]*self.DF[:,12]); nb=self.info['cv']
        actual=np.array([r['delta_binding_energy_per_baryon_s_ev'] for r in self.rows]);
        self.assertLess(np.max(abs(actual-expr)),1e-24)
    def test_08_tangency_algebra_exact(self):
        rb,rh=self.arr[4],self.arr[5]
        self.assertLess(np.max(abs(rh-rb+self.DF)),8e-31)
    def test_09_nonzero_actual_source_defect(self):
        self.assertEqual(self.stats['source_defect_nonzero_epochs'],193)
        self.assertGreater(self.stats['max_delta_F_per_Hubble'],1.0)
    def test_10_energy_compensation_is_opposite(self):
        self.assertLess(max(abs(r['delta_chemical_binding_erg_cm3_s']+r['required_opposite_energy_port_erg_cm3_s']) for r in self.rows),1e-47)
    def test_11_heat_capacity_number_loading(self):
        for r in self.rows:
            self.assertGreater(r['nb_cm3'],0.)
            self.assertAlmostEqual(r['formal_Q_over_Cv_K_s']+r['formal_number_loading_K_s'],r['formal_total_Tdot_bridge_K_s'],delta=1e-23)
    def test_12_time_clock_positive(self):
        x=self.info['t'];self.assertTrue(np.all(np.diff(x)>0))
        self.assertLess(self.stats['midpoint_H_dt_dx_rel_error_max'],1e-4)
    def test_13_signed_source_exposure(self):
        self.assertAlmostEqual(simpson(self.info['xeDot'],x=self.info['t']),self.stats['simpson_delta_electron_source_per_baryon'],delta=5e-13)
    def test_14_no_new_IVP(self):
        self.assertTrue(self.stats['no_new_ivp']);self.assertFalse(self.stats['actual_thermal_evolution'])
    def test_15_hybrid_weak_J_safety(self):
        self.assertAlmostEqual(self.stats['max_A_J_hybrid'],1.6543612497579586e-24,delta=1e-28)
    def test_16_graph_generated_files(self):
        self.assertEqual(len(list((ROOT/'results').glob('PLOT*.png'))),6)
    def test_17_negative_test_delete_weak(self):
        A=self.parent['A21'];bad=self.parent['J_naive'];self.assertGreater(np.max(abs(np.einsum('j,ijk->ik',A,bad))),1e-3)
    def test_18_causal_claim_not_evolved(self):
        self.assertEqual(self.stats['production'],'HOLD');self.assertEqual(self.stats['canonical']['delta'],0)

if __name__=='__main__':unittest.main(verbosity=2)
