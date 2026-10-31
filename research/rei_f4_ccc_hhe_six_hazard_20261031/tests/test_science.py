"""Bounded adversarial tests for original-source, six-channel CCC partial hazards."""
import sys, pathlib, unittest, math, json, hashlib, tempfile, random
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import compute as m

class TestSourceAndPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.meta=m.load_ccc()
        cls.arr=pd.read_csv(ROOT/'inputs/PR302_ARRIVAL_192.csv')
        cls.chem=pd.read_csv(ROOT/'inputs/PR303_SPECIES_192.csv')
        cls.th=pd.read_csv(ROOT/'inputs/PR302_THERMAL_192.csv')
        cls.pl=pd.read_csv(ROOT/'inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv')
        cls.ev=pd.read_csv(ROOT/'results/CCC_FIRST_COLLISION_CHANNELS_23040.csv')
        cls.results=pd.read_csv(ROOT/'results/CCC_FIRST_COLLISION_ARRIVAL_192.csv')
    def test_01_original_shas(self):
        for name,d in m.SHA.items():self.assertEqual(m.sha(ROOT/'inputs'/name),d)
    def test_02_source_grid_shape(self):
        self.assertEqual((len(self.arr),len(self.chem),len(self.th),len(self.pl)),(192,192,192,193))
    def test_03_event_dimensions(self):
        self.assertEqual(len(self.ev),192*4*5*6);self.assertEqual(len(self.results),192)
    def test_04_all_six_blobs(self):
        self.assertEqual(set(self.meta['data']),set(m.TARGETS))
        self.assertEqual(self.meta['data']['HI_ion']['blob'],'d6bdc1c80292298227f1008427967d745f99412b')
        self.assertEqual(self.meta['data']['HeI_ion']['blob'],'ba9e10df7388816ae27ac5121de0b833ad415f8d')
    def test_05_source_energy_closure(self):
        self.assertAlmostEqual(self.results.primary_E_eV_per_b.sum(),6.749242464433259e-11,delta=1e-23)
    def test_06_source_electron_count(self):
        self.assertAlmostEqual(self.results.primary_electrons_per_b.sum(),4.374110632809568e-12,delta=1e-23)
    def test_07_source_reaggregate_each_arrival(self):
        a=self.ev.groupby(['arrival_interval','first_absorber','electron_band'],sort=False).first().reset_index()
        n=a.groupby('arrival_interval').electron_N_per_b.sum().to_numpy(); E=a.groupby('arrival_interval').electron_M_eV_per_b.sum().to_numpy()
        self.assertLess(np.max(abs(n-self.arr.total_absorbed_ionizations_per_b.to_numpy())),1e-23)
        self.assertLess(np.max(abs(E-self.arr.total_primary_e_eV_per_b.to_numpy())),1e-23)
    def test_08_species_density_positive(self):
        for c in ('nH_cm3','nH_I_cm3','nHe_I_cm3','ne_HHe_cm3','proper_interval_s'):
            self.assertTrue(np.all(self.results[c].to_numpy()>=0),c)
    def test_09_density_native_scaling(self):
        z=self.pl.z.to_numpy(); nb=self.pl.nb_m3.to_numpy()
        self.assertLess(max(abs(nb/(1+z)**3/(nb[0]/(1+z[0])**3)-1)),1e-11)
        self.assertLess(np.max(abs(self.results.nb_m3-self.pl.nb_m3.to_numpy()[1:])),1e-8)
    def test_10_threshold_helium_ion_corrected(self):
        a=self.data['HeI_ion']
        self.assertEqual(m.sigma_interp(a,24.585,'HeI_ion'),0)
        self.assertEqual(m.sigma_interp(a,24.587389011,'HeI_ion'),0)
        self.assertGreater(m.sigma_interp(a,24.595,'HeI_ion'),0)
    def test_11_hydrogen_excitation_threshold(self):
        for s in ('HI_2p','HI_2s'):
            self.assertEqual(m.sigma_interp(self.data[s],10.2,s),0)
            self.assertGreater(m.sigma_interp(self.data[s],11,s),0)
    def test_12_he_subthreshold_excitation(self):
        self.assertEqual(m.sigma_interp(self.data['HeI_t2s'],19,'HeI_t2s'),0)
        self.assertGreater(m.sigma_interp(self.data['HeI_t2s'],20,'HeI_t2s'),0)
    def test_13_helium_raw_unit_never_a0_squared(self):
        self.assertLess(self.data['HeI_ion'][:,1].max(),4e-17)
        self.assertGreater(self.data['HI_ion'][:,1].max(),5e-17)
    def test_14_no_spurious_nonzero(self):
        cols=['source_weighted_nu_mean_per_b_s','source_weighted_nu_lower_per_b_s','source_weighted_nu_upper_per_b_s','collision_nu_mean_s']
        self.assertFalse(self.ev[cols].isna().any().any())
        for c in cols:self.assertGreaterEqual(self.ev[c].min(),-1e-60)
    def test_15_hull_bounds_model_consistency(self):
        tol=1e-32
        self.assertLessEqual(np.max(self.ev.source_weighted_nu_lower_per_b_s-self.ev.source_weighted_nu_mean_per_b_s),tol)
        self.assertLessEqual(np.max(self.ev.source_weighted_nu_mean_per_b_s-self.ev.source_weighted_nu_upper_per_b_s),tol)
    def test_16_moment_hull_nontrivial(self):
        dif=self.ev.source_weighted_nu_upper_per_b_s-self.ev.source_weighted_nu_lower_per_b_s
        self.assertGreater(np.count_nonzero(dif>1e-55),1000)
    def test_17_zero_E_zero_rate(self):
        self.assertTrue((self.ev.loc[self.ev.electron_N_per_b==0,'source_weighted_nu_mean_per_b_s']==0).all())
    def test_18_no_mislabeled_Lya(self):
        self.assertIn('HI_2s',self.ev.channel.unique());self.assertIn('HI_2p',self.ev.channel.unique());self.assertNotIn('Lya',self.ev.channel.unique())
    def test_19_no_heiii_target(self):
        self.assertNotIn('HeIII_ion',self.ev.channel.unique());self.assertNotIn('HeII_ion',self.ev.channel.unique())
    def test_20_native_temporal_coordinates(self):
        self.assertLess(np.max(abs(self.results.z_low-self.pl.z.to_numpy()[1:])),1e-10)
        self.assertEqual(len(self.results[self.results.primary_electrons_per_b>0]),191)
    def test_21_no_event_yield_claim(self):
        k=json.loads((ROOT/'results/RESULTS.json').read_text())
        self.assertEqual(k['statuses']['native_nonthermal_cascade'],'NOT_RUN')
        self.assertEqual(k['statuses']['production'],'HOLD')
        self.assertEqual(k['statuses']['canonical_delta'],0)
    def test_22_negative_source_corruption(self):
        data=(ROOT/'inputs/PR302_ARRIVAL_192.csv').read_bytes()
        self.assertNotEqual(hashlib.sha256(data+b'0').hexdigest(),m.SHA['PR302_ARRIVAL_192.csv'])
    def test_23_randomized_two_point_measures(self):
        rng=random.Random(20261031)
        for _ in range(2400):
            c=rng.choice(m.TARGETS);s=rng.choice(m.SPECIES);b=rng.choice(m.BANDS)
            k=m.BANDS.index(b);lo=m.EDGES[k];hi=max(lo,min(m.EDGES[k+1],m.EDGES[-1]-m.ABS_THRESHOLDS[s]));
            L,U,knots,g=m.moment_geometry(self.data[c],lo,hi,c)
            v1=lo+(hi-lo)*rng.random();v2=lo+(hi-lo)*rng.random();p=rng.random();mu=p*v1+(1-p)*v2
            model=lambda e:np.interp(e,knots,g)
            val=p*model(v1)+(1-p)*model(v2)
            self.assertLessEqual(m.segment_interpolate(*L,mu)-val,1e-10*max(max(g),1e-50))
            self.assertLessEqual(val-m.segment_interpolate(*U,mu),1e-10*max(max(g),1e-50))
    def test_24_report_rates_are_rates_not_counts(self):
        d=json.loads((ROOT/'results/RESULTS.json').read_text())
        self.assertEqual(d['real_arrival_intervals'],192);self.assertEqual(d['source_first_photoelectron_channels'],23040)
        self.assertEqual(d['intervals_where_first_inelastic_collocation_faster_than_proper_interval'],85)

if __name__=='__main__':unittest.main()
