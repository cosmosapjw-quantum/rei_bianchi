import csv, math, os, sys, unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from threshold_transport import *
DATA=BASE/'data'

class SourcePhysicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_barnett_csv(DATA/'EXFOR_BARNETT_L0138002_216.csv')
        cls.samples=select_source_points(cls.rows)

    def test_source_216_and_units(self):
        self.assertEqual(len(self.rows),216)
        self.assertEqual({x['EXFOR_subentry'] for x in self.rows},{'L0138002'})
        self.assertTrue(all(x['stat_micro_b']>0 and x['shared_sys_percent']==2 for x in self.rows))
    def test_no_repeat_as_new_independent_experiments(self):
        self.assertLess(len(set(x['energy_MeV'] for x in self.rows)),len(self.rows))
    def test_exact_source_points(self):
        self.assertEqual([x['energy_MeV'] for x in self.samples],[139.8,144.02,148.04,152.03,156.13])
        self.assertEqual([x['sigma_micro_b'] for x in self.samples],[0.9266,3.2427,7.5233,11.9979,18.7546])
    def test_source_subthreshold_noise_not_physical_negative(self):
        self.assertTrue(any(x['energy_MeV']<THRESHOLD_COH for x in self.rows))
        self.assertTrue(all(x['energy_MeV']>THRESHOLD_COH for x in self.samples))
    def test_exact_coherent_threshold(self):
        self.assertAlmostEqual(THRESHOLD_COH,137.42070690153014,places=9)
    def test_first_fragmentary_pion_threshold(self):
        self.assertTrue(all(THRESHOLDS['pT']<THRESHOLDS[x] for x in ('nHe3','dd','npD','2p2n')))
        self.assertTrue(all(s['energy_MeV']<THRESHOLDS['pT'] for s in self.samples))
    def test_second_pion_reopen_exact(self):
        self.assertAlmostEqual(daughter_reproduction_threshold(),171.16490690153043,places=8)
        self.assertLess(max_daughter(self.samples[-1]['energy_MeV']),THRESHOLD_COH)
        self.assertGreater(max_daughter(180),THRESHOLD_COH)
    def test_negative_below_coherent_threshold(self):
        with self.assertRaises(ValueError):pion_lab(120,0)
    def test_recoil_lab_conservation(self):
        for s in self.samples:
            for mu in (-1,-.2,0,.6,1):
                k=pion_lab(s['energy_MeV'],mu)
                self.assertAlmostEqual(k['E_pi_MeV']+k['recoil_alpha_K_MeV'],s['energy_MeV'],places=10)
                self.assertGreaterEqual(k['E_gamma_min_MeV'],0)
                self.assertGreater(k['E_gamma_max_MeV'],k['E_gamma_min_MeV'])
    def test_pwave_isotropic_exact_total_count(self):
        for law in ['pwave','isotropic']:
            kin=angular_ensemble(self.samples[1]['energy_MeV'],law)
            self.assertAlmostEqual(float(kin['weights'].sum()),1,places=13)
            self.assertAlmostEqual(kin['N_exact'],1.97646,places=12)
            self.assertLess(kin['max_daughter_MeV'],THRESHOLD_COH)
    def test_angular_model_not_mislabelled_measured(self):
        kin=angular_ensemble(self.samples[1]['energy_MeV'],'pwave')
        self.assertAlmostEqual(float(np.dot(kin['mu'],kin['weights'])),0.,places=12)
    def test_source_projection_photon_count(self):
        kin=angular_ensemble(150,'pwave')
        g=np.geomspace(.5,120,200)
        f,w=project_pi_daughter_source(g,kin)
        self.assertAlmostEqual(float(np.dot(f,w)),2*B_2G,places=12)
    def test_source_rejected_bad_angular_law(self):
        with self.assertRaises(ValueError):angular_ensemble(145,'pretend-measured')
    def test_source_published_bbnn_and_nonnegative(self):
        self.assertTrue(THRESHOLDS['npD']>THRESHOLDS['pT'])
        self.assertGreater(Q_NPD,Q_DD)
    def test_code_smoke_measured_physics(self):
        case=solve_epoch(self.samples[1],1e5,NE=64)['case']
        self.assertGreater(case['D_net_per_primary_first_hit'],0)
        self.assertTrue(0<case['pion_first_hit_P']<1)
        self.assertLess(abs(case['known_stoichiometry_baryon_residual']),1e-12)
        self.assertLess(abs(case['known_stoichiometry_charge_residual']),1e-12)
        self.assertLess(case['D_net_first_hit_sys_shared_1sigma'],case['D_net_per_primary_first_hit'])
        self.assertGreater(case['fastD_from_dd_plus_npD_gross_upper_MeV_per_pi0'],case['fastD_from_dd_gross_lower_MeV_per_pi0'])
    def test_published_outputs_row_contract(self):
        path=DATA/'MEASURED_NEAR_THRESHOLD_PHYSICS_GREEN_15.csv'
        with path.open() as f:rs=list(csv.DictReader(f))
        self.assertEqual(len(rs),15)
        self.assertEqual({float(x['z']) for x in rs},{1e4,1e5,1e6})
        self.assertTrue(all(float(r['D_net_per_primary_first_hit'])>0 for r in rs))
    def test_published_17_channel_and_9nuclide_rows(self):
        for name,expected in [('NUCLEAR_17_CHANNEL_EVENTS_255.csv',255),('NUCLIDE_SIGNED_RESPONSE_135.csv',135)]:
            with (DATA/name).open() as f:self.assertEqual(sum(1 for _ in csv.DictReader(f)),expected)

if __name__=='__main__':unittest.main()
