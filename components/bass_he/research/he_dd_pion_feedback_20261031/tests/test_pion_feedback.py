import unittest,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pion_feedback import pion_sigma_mb,pion_angular_spectrum,GEOM,RATES,_physical_model,CONVERSION

class UnitPhysics(unittest.TestCase):
    def test_measured_positive(self):
        for E in GEOM:self.assertAlmostEqual(pion_sigma_mb(E)*1000,RATES[E],places=10)
    def test_outside_measured_support_has_zero(self):
        for E in (135,150,205,242):self.assertEqual(pion_sigma_mb(E),0.)
    def test_interpolation_positive(self):
        for E in (208.,211.,215.,235.):self.assertGreater(pion_sigma_mb(E),0.)
    def test_photon_regeneration_not_underdetermined_interp(self):
        self.assertGreater(pion_angular_spectrum(155.,210.),0.)
        self.assertEqual(pion_angular_spectrum(155.,201.),0.)
    def test_published_nuclide_table(self):
        import acropolis.nucl as nu
        self.assertEqual(len(nu._reactions),17)
        self.assertEqual(nu._eth[9],26.071100)
        self.assertEqual(nu._eth[8],23.846527)
    def test_original_Jedamzik_correction(self):
        from acropolis.nucl import NuclearReactor
        from acropolis.input import InputInterface,locate_sm_file
        ii=InputInterface(locate_sm_file());r=NuclearReactor([lambda t:0.]*3,[lambda e,t:0.]*3,(1e-5,1e-5),250,ii)
        energy=220.;q=20.577615
        expected=20.7*(q/energy)**3.5*(1-q/energy)
        self.assertAlmostEqual(r.get_cross_section(7,energy)/CONVERSION,expected,places=12)
    def test_no_duplicate_absorption(self):
        from pi0_physics import interpolated_absorption
        for E in GEOM:self.assertLess(pion_sigma_mb(E)*1000,interpolated_absorption(E)['sigma_micro_b'])

class IntegrationPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.em,*_= _physical_model(241,1e5,48,do_gain=False,do_sink=False)
        cls.loss,*_= _physical_model(241,1e5,48,do_gain=False,do_sink=True)
        cls.gain,cls.spectrum,_,_,_= _physical_model(241,1e5,48,do_gain=True,do_sink=True)
        cls.control,*_=_physical_model(216,1e5,48,do_gain=True,do_sink=True)
    def test_nuclear_opacity_reduces_deuterium(self):
        self.assertLess(self.loss['D_net_per_initial_pi0'],self.em['D_net_per_initial_pi0'])
    def test_pion_gain_nonnegative(self):
        self.assertGreater(self.gain['D_net_per_initial_pi0'],self.loss['D_net_per_initial_pi0'])
    def test_no_supported_pion_regen_for_216(self):
        self.assertEqual(self.control['pion_regen_photon_count_measured_support'],0.)
    def test_gamma_grid_support(self):
        self.assertTrue(np.isfinite(self.spectrum).all())
        self.assertGreaterEqual(float(np.min(self.spectrum[1:])),0.)
    def test_energy_pion_kernel(self):
        self.assertLess(self.gain['max_pi_kernel_energy_model_relative_error'],.03)
        self.assertLess(self.gain['max_pi_kernel_count_norm_abs_err'],1e-12)
        self.assertLessEqual(self.gain['max_pi_kernel_energy_excess_MeV'],0.)
    def test_nuclei_conservation(self):
        self.assertLess(abs(self.gain['known_channels_baryon_residual']),1e-10)
        self.assertLess(abs(self.gain['known_channels_charge_residual']),1e-10)
    def test_signed_deuterium_net(self):
        r=self.gain
        self.assertAlmostEqual(r['D_net_per_initial_pi0'],r['D_born_per_initial_pi0']-r['D_destroy_per_initial_pi0'],places=14)
    def test_nonnegative_channels(self):
        self.assertTrue(all(float(v)>=0 for v in self.gain['channel_events'].values()))
    def test_no_production_heat_claim(self):
        self.assertTrue(self.gain['no_BASS_gamma_emissivity'])
        self.assertTrue(self.gain['no_final_heat_rate'])

if __name__=='__main__':unittest.main()
