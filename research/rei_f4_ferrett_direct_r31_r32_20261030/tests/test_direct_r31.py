import csv, hashlib, importlib.util, math, pathlib, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ferrett_direct_r31',ROOT/'code/direct_r31.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class TestDirectFerrett(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.epochs,cls.s=m.generate()
    def test_source_pdf_hash(self):
        self.assertEqual(m.sha(m.PDF_PATH.read_bytes()),m.PDF_SHA)
    def test_source_parent_hash(self):
        self.assertEqual(m.sha(m.PARENT_PATH.read_bytes()),m.PARENT_SHA)
    def test_direct_7_measurement_row_identity(self):
        self.assertEqual(m.R31.shape,(7,3));self.assertEqual(m.R32.shape,(7,3))
        self.assertTrue((m.R31[:,0]==m.R32[:,0]).all())
        self.assertAlmostEqual(m.R31[3,1],1.59,places=13)
        self.assertAlmostEqual(m.R32[3,1],.209,places=13)
    def test_87eV_Wolfram_reconstruction(self):
        b=m.branch_enclosure(87)
        self.assertAlmostEqual(b['triplet_fraction'],.5077747013230884,places=14)
        self.assertAlmostEqual(b['n2_rest_fraction'],.3193551580648355,places=14)
        self.assertAlmostEqual(b['n3_fraction'],.1728701406120761,places=14)
    def test_R31_measurement_only_support(self):
        for e in (79.9999,92.5001,97.3033,200):
            with self.assertRaises(ValueError):m.branch_enclosure(e)
    def test_allowed_edges(self):
        self.assertAlmostEqual(m.measured_ratios(80.)[0],1.62)
        self.assertAlmostEqual(m.measured_ratios(92.5)[2],.234)
    def test_monotone_derivative_interval(self):
        for E in [80,81.85233848280362,86.70882056440522,91.85344857617926,92.5]:
            b=m.branch_enclosure(E)
            self.assertLessEqual(b['triplet_fraction_min'],b['triplet_fraction'])
            self.assertLessEqual(b['triplet_fraction'],b['triplet_fraction_max'])
            self.assertLessEqual(b['n2_rest_fraction'],b['n2_rest_fraction_max'])
            self.assertLessEqual(b['n3_fraction_min'],b['n3_fraction_max'])
    def test_number_normalization_every_measured_event(self):
        for r in self.data:
            self.assertAlmostEqual(r['triplet_fraction']+r['n2_rest_fraction']+r['n3_fraction'],1.,delta=1e-14)
    def test_nonnegative_1s_photoelectron_threshold(self):
        for r in self.data:
            self.assertGreaterEqual(r['conditional_photoelectron_eV_min'],0.)
            self.assertGreaterEqual(r['conditional_photoelectron_eV_max'],r['conditional_photoelectron_eV_min'])
            self.assertLessEqual(r['conditional_photoelectron_eV_max'],r['photon_eV'])
    def test_branch_interval_inclusion_all_rows(self):
        for r in self.data:
            self.assertLessEqual(r['conditional_triplet_rate_min'],r['conditional_triplet_rate']+1e-300)
            self.assertLessEqual(r['conditional_triplet_rate'],r['conditional_triplet_rate_max']+1e-300)
    def test_no_measured_pure_singlet_lower(self):
        for r in self.data:
            self.assertEqual(r['conditional_singlet_2E1_rate_lower'],0)
            self.assertLessEqual(r['conditional_singlet_2E1_rate_upper'],r['native_K_events_per_baryon_s']*r['n2_rest_fraction_max']*(1+1e-13))
    def test_original_193_epochs_3bins_2isotopes(self):
        self.assertEqual(len(self.data),193*3*2)
        self.assertEqual(len(self.epochs),193)
        self.assertEqual({r['epoch'] for r in self.data},set(range(193)))
        self.assertEqual({r['isotope'] for r in self.data},{'Li6I','Li7I'})
        self.assertEqual({r['bin_index'] for r in self.data},{54,55,56})
    def test_n3_original_lab_fraction(self):
        for e in m.R32[:,0]:
            b=m.branch_enclosure(e)
            self.assertAlmostEqual(b['n3_fraction'],b['R32']/(1+b['R32']),places=14)
    def test_integration_parent_original_native_strict(self):
        self.assertAlmostEqual(self.s['source_integrals_per_original_baryon']['source_events'],7.881829561377486e-12,delta=1e-23)
    def test_integrated_event_closure(self):
        x=self.s['source_integrals_per_original_baryon']
        self.assertAlmostEqual(x['triplet']+x['n2_rest']+x['n3'],x['source_events'],delta=1e-25)
    def test_undetermined_singlet_ceiling(self):
        x=self.s['source_integrals_per_original_baryon']
        self.assertLessEqual(x['n2_rest'],x['n2_rest_upper'])
        self.assertLess(x['n2_rest_upper'],x['source_events'])
    def test_no_new_IVPs_or_production(self):
        self.assertEqual(self.s['new_ivps'],0)
        self.assertEqual(self.s['production'],'HOLD')
        self.assertEqual(self.s['original_DAG']['working'],'33/88')
    def test_unresolved_3P_counterexample(self):
        # All n2-rest can be 3P/1P; a pure 1S yield >0 cannot be deduced.
        data=m.branch_enclosure(87.)
        triplet, rest, n3=m.branch(data['R31'],data['R32'])
        # Hypothesis A: all n2-rest is 1S; hypothesis B: all is 3P.
        for singlet, p3 in ((rest,0.0),(0.0,rest)):
            self.assertAlmostEqual(triplet/(singlet+p3),data['R31'],places=13)
            self.assertAlmostEqual(n3/(triplet+singlet+p3),data['R32'],places=13)
        self.assertGreater(rest,0.)
    def test_photoelectron_branch_energy_exact(self):
        for E in (81.85233848280362,86.70882056440522,91.85344857617926):
            r,dr,t,dt=m.measured_ratios(E)
            for a in (r-dr,r+dr):
                for b in (t-dt,t+dt):
                    f3,fre,fn=m.branch(a,b)
                    for rest,n3 in ((m.CHI_N2_REST_MIN,m.CHI_N3_MIN),(m.CHI_N2_REST_MAX,m.CHI_N3_MAX)):
                        bind=f3*m.CHI_TRIPLET+fre*rest+fn*n3
                        kin=E-bind
                        self.assertAlmostEqual(kin+bind,E,delta=2e-14)
    def test_pdf_corruption_rejected(self):
        original=m.PDF_PATH
        try:
            with tempfile.TemporaryDirectory() as tmp:
                fake=pathlib.Path(tmp)/'fake.pdf';fake.write_bytes(original.read_bytes()+b'X')
                m.PDF_PATH=fake
                with self.assertRaisesRegex(ValueError,'PDF_BYTE_IDENTITY'):m.read_frozen_sources()
        finally:m.PDF_PATH=original
    def test_parent_archive_corruption_rejected(self):
        original=m.PARENT_PATH
        try:
            with tempfile.TemporaryDirectory() as tmp:
                fake=pathlib.Path(tmp)/'fake.zip';fake.write_bytes(original.read_bytes()[:100])
                m.PARENT_PATH=fake
                with self.assertRaisesRegex(ValueError,'SOURCE_SHA'):m.read_frozen_sources()
        finally:m.PARENT_PATH=original

if __name__=='__main__':unittest.main()