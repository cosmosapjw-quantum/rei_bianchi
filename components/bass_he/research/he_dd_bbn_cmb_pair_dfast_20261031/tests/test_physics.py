import csv, math, pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from physics import *

class PhysicalValidation(unittest.TestCase):
    def test_original_source_masses(self):
        self.assertAlmostEqual(Q_MEV,23.8464782,places=6)

    def test_pdf_source_sha_locked(self):
        import hashlib
        p=pathlib.Path('/mnt/data/Rice_1998(2).pdf')
        if not p.exists(): self.skipTest('source user PDF only in authoring sandbox')
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'87fe939659151b09a1653467f1ac2098d971048fa4cf3611b447fce8cc976336')

    def test_planck_cmb_number_density(self):
        n=gg_number_density(1e4)/(1e4+1)**3
        self.assertGreater(n,410.0);self.assertLess(n,411.5)

    def test_baryon_abundance_charge_neutral(self):
        for z in [1e4,2e5,1e6]:
            s=state(z)
            self.assertAlmostEqual(s['n_e_cm3'],s['n_H_cm3']+2*s['n_alpha_cm3'],delta=s['n_e_cm3']*1e-13)
            self.assertAlmostEqual(s['n_H_cm3']+4*s['n_alpha_cm3'],s['n_b_cm3'],delta=s['n_b_cm3']*1e-13)

    def test_bw_sigma_threshold(self):
        self.assertEqual(bw_sigma_cm2(0.0),0.0)
        self.assertTrue(0.20 < bw_sigma_cm2(.7)/SIGMA_T_CM2 < 0.27)

    def test_bw_external_wolfram_reference(self):
        # Independently evaluated Wolfram Language ratio on this research loop.
        self.assertAlmostEqual(bw_sigma_cm2(0.7)/SIGMA_T_CM2,0.25563674642071383,places=12)

    def test_kinematics_external_wolfram_reference(self):
        a,b=born_d_pair_kinetics(220.,0.5)
        self.assertAlmostEqual(a,114.9484964712988,places=10)
        self.assertAlmostEqual(b,81.20502532870111,places=10)

    def test_bw_sigma_nonnegative(self):
        bs=np.linspace(0,.9999,200)
        self.assertTrue(np.all(bw_sigma_cm2(bs)>=0))

    def test_positive_pair_rates(self):
        for z in [1e5,2e5,5e5,1e6]:
            for E in [150.,170.,220.,250.]:
                r=bb_pair_rate_s(E,z)
                self.assertTrue(math.isfinite(r) and r>=0)

    def test_pair_energy_monotone(self):
        for z in [1e5,2e5,1e6]:
            rates=[bb_pair_rate_s(E,z) for E in [150.,170.,220.,250.]]
            self.assertTrue(all(a<=b for a,b in zip(rates,rates[1:])))

    def test_pair_redshift_monotone(self):
        for E in [150.,220.]:
            self.assertLess(bb_pair_rate_s(E,1e5),bb_pair_rate_s(E,2e5))
            self.assertLess(bb_pair_rate_s(E,2e5),bb_pair_rate_s(E,1e6))

    def test_nested_quad_independent(self):
        for z,E in [(1e5,220.),(2e5,220.),(5e5,170.),(1e6,220.)]:
            numerical=bb_pair_rate_s(E,z)
            independent=bw_pair_quad_independent(E,z)
            self.assertLess(abs(numerical-independent)/independent,2e-5)

    def test_pair_quadrature_convergence(self):
        for z,E in [(1e5,170.),(2e5,220.),(1e6,250.)]:
            x=bb_pair_rate_s(E,z,128,96)
            y=bb_pair_rate_s(E,z,220,140)
            self.assertLess(abs(x-y)/y,4e-5)

    def test_gamma_over_H_crossover(self):
        from scipy.optimize import brentq
        for E in [150.,190.,250.]:
            z=brentq(lambda z: math.log10(bb_pair_rate_s(E,z)/state(z)['H_s_inv']),8e4,5e5)
            self.assertAlmostEqual(bb_pair_rate_s(E,z)/state(z)['H_s_inv'],1.0,delta=1e-8)

    def test_he_dd_correct_units(self):
        s=state(1e6)
        r=he_dd_rate_per_photon(170.,1e6)
        self.assertAlmostEqual(r/(s['n_alpha_cm3']*c.c*100),8.29e-33,delta=1e-45)
        r2=he_dd_rate_per_photon(220.,1e6)
        self.assertAlmostEqual(r2/(s['n_alpha_cm3']*c.c*100),4.34e-33,delta=1e-45)

    def test_two_channel_fraction_finite(self):
        for z in [1e5,2e5,1e6]:
            g=bb_pair_rate_s(220.,z)
            d=he_dd_rate_per_photon(220.,z)
            p=d/(d+g)
            self.assertTrue(0<=p<=1)

    def test_kinematics_energy_conservation(self):
        for E in [150.,170.,190.,220.,250.]:
            for mu in [-1,-0.5,0,.5,1]:
                ka,kb=born_d_pair_kinetics(E,mu)
                self.assertGreater(ka,0);self.assertGreater(kb,0)
                self.assertAlmostEqual(ka+kb,E-Q_MEV,delta=1e-12)
                ka2,kb2=born_d_pair_kinetics(E,-mu)
                self.assertAlmostEqual(ka,kb2,delta=1e-12)
                self.assertAlmostEqual(kb,ka2,delta=1e-12)

    def test_electron_drag_positive(self):
        for z in [1e4,2e5,1e6,2e7]:
            for Ed in [50.,100.,150.]:
                row=d_electron_drag(Ed,z)
                self.assertGreater(row['dE_dt_e_dynamic_MeV_s'],0)
                self.assertTrue(0<=row['thermal_F']<=1)
                self.assertTrue(row['lnLambda_dynamic']>=row['lnLambda_static']>1)
                self.assertLess(row['plasma_coupling_gamma'],1e-3)

    def test_drag_nonzero_thermal_factor(self):
        a=d_electron_drag(50,2e7)
        self.assertLess(a['thermal_F'],1.)
        self.assertGreater(a['thermal_F'],0.0)

    def test_drag_weak_coupling_scaling(self):
        for z in [1e5,1e6,1e7]:
            a=d_electron_drag(100,z)
            self.assertLess(a['t_loss_e_dynamic_over_Hubble'],1e-3)

    def test_energy_cascade_not_claimed(self):
        import json
        j=json.loads((ROOT/'data'/'PHYSICS_SUMMARY.json').read_text())
        self.assertEqual(j['DAG_current']['central'],'28/88')
        self.assertEqual(j['DAG_current']['HE_physical'],'14/18')
        self.assertIn('NOT observed cosmic 150-250 MeV gamma injection',j['provenance'])

    def test_model_rows(self):
        expected=[('PHYSICAL_CMB_GAMMAGAMMA_PAIR_OPACITY_55.csv',55),
                  ('PHYSICAL_FASTD_PLASMA_ELECTRON_DRAG_55.csv',55),
                  ('RICE_BINMODEL_DD_VS_CMB_PAIR_HAZARDS_22.csv',22),
                  ('PHYSICAL_GAMMA_TRANSPARENCY_TRANSITION_15.csv',15),
                  ('SOURCE_FLRW_IONIZED_STATES_11.csv',11),
                  ('MODEL_CONDITIONAL_SOURCE_BIN_BIRTH_6.csv',6)]
        for f,n in expected:
            with open(ROOT/'data'/f) as fh:
                self.assertEqual(len(list(csv.DictReader(fh))),n)

    def test_source_probability_semantics(self):
        with open(ROOT/'data'/'RICE_BINMODEL_DD_VS_CMB_PAIR_HAZARDS_22.csv') as f:
            header=next(csv.reader(f))
            self.assertIn('two_channel_first_interaction_dd_fraction',header)
            self.assertNotIn('cosmic_event_rate',header)

if __name__=='__main__':unittest.main()
