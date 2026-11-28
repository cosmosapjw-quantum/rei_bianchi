import io,json,sys,unittest,zipfile
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from second_cell_pilot import source_probe,identity_and_incoming,Source

class SecondSavedCell(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.o=source_probe()
    def test_selected_physical_source_and_cell(self):
        o=self.o
        self.assertEqual(o['cell_s'],['6250000000','12500000000'])
        self.assertEqual(o['source_commit'],'a5c958c414dea41216b445c05f58df837f05cacb')
        self.assertEqual(o['old_ivp_integrations'],0)
        self.assertEqual(o['scientific_admission'],'EXPLORATORY_ONLY')
    def test_exact_r4_right_slope_is_second_left(self):
        s=Source()
        with np.load(ROOT/'inputs/FIXED_REFERENCE_R4.npz') as data:
            first_right=data['slope_right']
        self.assertTrue(np.array_equal(first_right,s.rhs(s.times[1],s.y[:,1])[0].astype(float)))
    def test_bernstein_domain_and_positive_photon(self):
        self.assertTrue(all(self.o['Bernstein_exact_control_points'].values()))
        for row in self.o['data']:
            self.assertGreaterEqual(row['min_photon_population'],0)
            self.assertGreater(row['Tgas_K'],30000)
            self.assertLess(row['Tgas_K'],110000)
    def test_unit_conversion_and_column_order(self):
        o=self.o
        # With n_e = nH(cm^-3)*chi_e, c is 299792458(m/s), hence
        # column[m^-2] = c_SI * (1e6 cm^-3 -> m^-3) * integral n_e dt.
        sigma=Decimal('6.6524587051e-29')
        center=Decimal(o['column_center_recon']['Hermite_GL24_m2'])
        tau=Decimal(o['column_center_recon']['Hermite_GL24_tau'])
        self.assertLess(abs(tau-sigma*center),Decimal('1e-22'))
        self.assertGreater(tau,Decimal('7e-9'))
        self.assertLess(tau,Decimal('9e-9'))
        self.assertLess(abs(center-Decimal(o['column_center_recon']['old_stored_proper_ne_PL_m2']))/center,Decimal('1e-6'))
    def test_new_cell_incoming_error_must_remain(self):
        obj,phot,gas=identity_and_incoming()
        self.assertEqual(len(phot),2904)
        self.assertEqual(len(gas),4)
        self.assertTrue(any(x>0 for x in phot))
        self.assertIsNone(self.o['true_second_cell_tau_interval'])
        self.assertIsNone(self.o['error_majorants_second_cell'])
        self.assertFalse(self.o['incoming_first_cell']['zero_incoming_error_assumed'])

if __name__=='__main__':unittest.main()
