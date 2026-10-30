import os,sys,json,unittest,io,csv,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import bridge

class PhysicsBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bath,cls.arr,cls.rei,cls.arrays,cls.result=bridge.calc()
    def test_original_193x21(self):
        self.assertEqual((len(self.bath),len(self.arr),len(self.rei)),(193,192,7))
        self.assertEqual(self.arrays['F21_per_baryon_s'].shape,(193,21))
        self.assertEqual(self.arrays['J21_per_s'].shape,(193,21,21))
    def test_independent_directional_FJ_finite_difference(self):
        # Fresh finite-difference oracle against original native analytic J on
        # four original frozen epochs; does not run the cosmological IVP.
        import io
        with bridge.load_archive('REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip') as z:
            net,s,_=bridge.net_and_trajectory(z)
        di={str(n):s['diagnostics'][:,j] for j,n in enumerate(s['diagnostic_names'])}
        direction=np.sin(np.arange(21)+1.0);direction/=np.linalg.norm(direction)
        for k in (0,33,97,192):
            y=s['Y'][k];h=1e-7
            args=(di['T_K'][k],di['uv_scale'][k],di['nb_m3'][k])
            fd=(net.evaluate(y+h*direction,*args)['dY_dt']-net.evaluate(y-h*direction,*args)['dY_dt'])/(2*h)
            target=self.arrays['J21_per_s'][k]@direction
            self.assertLess(np.linalg.norm(fd-target)/np.linalg.norm(target),1e-9)
    def test_original_source_sha(self):
        self.assertEqual(self.result['trajectory_sha256'],bridge.TRAJ)
    def test_exact_original_normalization(self):
        X=self.arrays
        self.assertLess(np.max(abs(X['A21']@X['F21_per_baryon_s'].T)),1e-22)
    def test_original_native_J_is_analytic(self):
        self.assertLess(self.result['independent_regression']['max_HHe_J_and_projection_residual'],2e-24)
    def test_original_BASS_HHe_source_parity(self):
        self.assertLess(self.result['independent_regression']['max_HHe_F_and_projection_residual'],2e-24)
    def test_original_native_power_identity(self):
        self.assertEqual(self.result['independent_regression']['max_saved_power_density_residual_W_m3'],0.)
    def test_original_charge_matches_ne(self):
        self.assertLess(self.result['independent_regression']['max_ne_relative_saved_vs_native'],1e-12)
    def test_baryon_number_dilution(self):
        self.assertLess(self.result['independent_regression']['nb_a3_rel_range'],1e-12)
    def test_photo_count_equals_sum_channel(self):
        for row in self.arr:
            got=sum(row[f'conditional_first_abs_{j}_per_baryon'] for j in ('H_I','He_I','He_II','Li_I'))
            self.assertAlmostEqual(got,row['conditional_absorptions_per_baryon'],places=21)
    def test_conditional_electron_integral(self):
        got=sum(a['conditional_electron_count_source_per_baryon_s']*a['proper_interval_s'] for a in self.arr)
        self.assertAlmostEqual(got,5.183362629197418e-11,places=22)
    def test_conditional_primary_energy_integral(self):
        got=sum(a['conditional_primary_kinetic_source_eV_per_baryon_s']*a['proper_interval_s'] for a in self.arr)
        self.assertAlmostEqual(got,7.997916399993968e-10,places=20)
    def test_photon_causal_direction(self):
        self.assertTrue(all(a['proper_interval_s']>0 and a['z_high']>a['z_low'] for a in self.arr))
    def test_heat_source_not_temperature_solution(self):
        self.assertEqual(self.result['conditional_causal']['actual_heat'],'UNBOUND')
        self.assertEqual(self.result['counts']['new_IVP'],0)
    def test_temperature_capacity_units(self):
        for a in self.arr:
            expected=1.5*bridge.KB_EV_K*a['N_thermal_mid']
            self.assertLess(abs(a['Cv_eV_per_baryon_per_K']-expected),2e-19)
    def test_no_unqualified_K_background(self):
        self.assertEqual(self.result['gates']['N_HREF_CLOCK_COMMON'],'UNBOUND')
        self.assertTrue(all(a['background_K_native']=='UNBOUND' for a in self.bath))
    def test_no_overwritten_physical_sources(self):
        self.assertTrue(self.result['gates']['NO_MERGE'])
        self.assertFalse(self.result['gates']['L4_ready'])
    def test_nonzero_bianchi_asymmetry_flag(self):
        self.assertGreater(max(abs(a['b_bianchi']) for a in self.bath),0.)
    def test_rank_one_li6_J_cross_block(self):
        J=self.arrays['J17xLi6_cross_per_s']
        # Relative row tolerance in Frobenius norm, not absolute tiny error.
        for j in [0,40,100,192]:
            sv=np.linalg.svd(J[j],compute_uv=False)
            self.assertLess(sv[1]/sv[0],1e-12)
    def test_exact_saved_17_projection(self):
        self.assertLess(np.max(abs(self.arrays['F17_BASS_restriction_per_baryon_s']-self.arrays['F21_per_baryon_s'][:,bridge.S21])),1e-28)
    def test_separate_REI_clock_not_approved(self):
        self.assertTrue(all(r['same_initial_condition_or_background']=='NOT_ESTABLISHED' for r in self.rei))
        self.assertLess(max(abs(r['z_matched_relative_time_difference']) for r in self.rei),0.01)
    def test_original_data_is_not_actual_secondary_heat(self):
        self.assertEqual(self.result['provenance']['radiation'],'PR287 original prescribed-gas 2E1 all-singlet conditional first-flight')
        self.assertEqual(self.result['gates']['PRODUCTION'],'HOLD')

if __name__=='__main__':unittest.main(verbosity=2)
