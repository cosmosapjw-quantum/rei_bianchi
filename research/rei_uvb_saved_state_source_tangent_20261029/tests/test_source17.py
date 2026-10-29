import sys, unittest, json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import source17 as s

class TestSource17(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port,cls.bb,cls.p19,cls.rates,cls.geo=s.load_parent()
        cls.saved=s.saved_rows()
        cls.rec=cls.saved[3]
        cls.z=cls.rec['z'];cls.y=np.array(cls.rec['y'],float)
        cls.a=cls.geo['a0']
        cls.out=s.source17(cls.z,cls.y,cls.a,cls.rates,cls.port)

    def test_01_pinned_source_and_selected_rows(self):
        self.assertTrue(s.structural_check())
        self.assertEqual(len(self.saved),7)
        self.assertEqual(len(s.EVENTS),7)
        self.assertEqual(s.SOURCE_REI_MODEL_GIT_BLOB,'1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc')
        self.assertEqual(s.SOURCE_SAVED_CSV_GIT_BLOB,'189c2d903e25c18bee49e0ab6add3ba1d1805e93')
        self.assertEqual(self.saved[3]['target_z'],3.6)
        self.assertAlmostEqual(self.z,3.603019593287379,14)

    def test_02_event_conservation_and_electron(self):
        np.testing.assert_array_equal(s.A@s.STOICH,np.zeros(7))
        np.testing.assert_array_equal(s.Q@s.STOICH,np.ones(7))
        np.testing.assert_allclose(s.A@self.out['F'],0,atol=1e-25)
        np.testing.assert_allclose(s.Q@self.out['F'],self.out['events'].sum(),rtol=1e-15)
        np.testing.assert_allclose(s.Q@self.out['B'],self.out['electron_jac'],rtol=1e-13,atol=1e-29)

    def test_03_photo_jacobian_source_structure(self):
        Jy=self.out['J_y'];diag=np.diag(Jy)
        self.assertTrue(np.all(Jy-np.diag(diag)>=0))
        self.assertTrue(np.all(diag<=0))
        np.testing.assert_allclose(Jy.sum(axis=0),0,atol=1e-27)
        self.assertEqual(np.max(np.abs(Jy[13:,:])),0.)
        self.assertEqual(np.max(np.abs(Jy[:,13:])),0.)
        self.assertEqual(np.max(np.abs(Jy[0,:])),0.)
        self.assertEqual(np.max(np.abs(Jy[:,0])),0.)

    def test_04_jacobian_state_finite_difference(self):
        h=1e-6
        for j in [1,3,5,7,8,10,11]:
            yy=self.y.copy();yy[j]+=h
            v=s.source17(self.z,yy,self.a,self.rates,self.port)['F']
            np.testing.assert_allclose((v-self.out['F'])/h,self.out['J_y'][:,j],rtol=2e-10,atol=1e-24)

    def test_05_jacobian_rate_independent_event_matrix(self):
        # Directly assemble seven events from the rate input; do not reuse J_R.
        moments=self.out['rate_moments']
        def direct(mm):
            vec=np.zeros(17)
            for j,(src,dst,k,_) in enumerate(s.EVENTS):
                event=self.y[s.SRC[j]]*mm[2*k]
                vec[s.SRC[j]]-=event;vec[s.DST[j]]+=event
            return vec
        np.testing.assert_allclose(direct(moments),self.out['F'],rtol=0,atol=1e-30)
        for j in [0,2,4]:
            step=1e-13
            mm=moments.copy();mm[j]+=step
            np.testing.assert_allclose((direct(mm)-direct(moments))/step,self.out['J_R'][:,j],rtol=1e-14,atol=1e-11)
        self.assertEqual(np.max(np.abs(self.out['J_R'][:,[1,3,5]])),0.)

    def test_06_common_scale_parameter_jacobian(self):
        t=self.port.tvec(self.z)
        np.testing.assert_allclose(self.out['B'],np.outer(self.out['F'],self.port.L10*t),rtol=3e-15,atol=1e-30)
        np.testing.assert_allclose(self.out['electron_jac'],self.port.L10*self.out['electron_rate_per_Href_s']*t,rtol=3e-15,atol=1e-29)

    def test_07_finite_difference_beta_kappa(self):
        h=1e-4
        for j in range(2):
            da=np.zeros(2);da[j]=h
            plus=s.source17(self.z,self.y,self.a+da,self.rates,self.port)['F']
            minus=s.source17(self.z,self.y,self.a-da,self.rates,self.port)['F']
            np.testing.assert_allclose((plus-minus)/(2*h),self.out['B'][:,j],rtol=2e-8,atol=1e-28)

    def test_08_energy_bookkeeping_and_derivative(self):
        o=self.out
        self.assertAlmostEqual(o['absorbed_photon_eV_per_Href_s'],o['photoheat_eV_per_Href_s']+o['ionization_storage_eV_per_Href_s'],25)
        np.testing.assert_allclose(o['photoheat_jac'],self.port.L10*o['photoheat_eV_per_Href_s']*self.port.tvec(self.z),rtol=2e-15)
        np.testing.assert_allclose(o['ionization_storage_jac'],self.port.L10*o['ionization_storage_eV_per_Href_s']*self.port.tvec(self.z),rtol=2e-15)

    def test_09_source_only_mu1_zero(self):
        Jy=self.out['J_y']
        mu=np.max(np.diag(Jy)+np.sum(np.abs(Jy),axis=0)-np.abs(np.diag(Jy)))
        self.assertEqual(mu,0.)
        for r in s.saved_rows():
            o=s.source17(r['z'],r['y'],self.a,self.rates,self.port)
            np.testing.assert_allclose(o['J_y'].sum(axis=0),0,atol=1e-27)

    def test_10_fixed_epoch_rank_one_and_stacked_rank_two(self):
        B=self.out['B'];sv=np.linalg.svd(B,compute_uv=False)
        self.assertLess(sv[1]/sv[0],1e-15)
        Bstack=np.vstack([s.source17(r['z'],r['y'],self.a,self.rates,self.port)['B'] for r in self.saved])
        svs=np.linalg.svd(Bstack,compute_uv=False)
        self.assertGreater(svs[1]/svs[0],1e-3)

    def test_11_exact_box_corner_support(self):
        import itertools
        d=self.bb;z=self.z;y=self.y
        env=s.source_envelopes(z,y,self.rates,self.port,self.geo)['deterministic']
        base=s.source17(z,y,[0.,0.],self.rates,self.port)['electron_rate_per_Href_s']
        lo=np.array(d['jeans_smoothing_lower_dex']);hi=np.array(d['jeans_smoothing_upper_dex'])
        v=np.array(d['eos_response_dex']);A=self.geo['A'];r=self.geo['r'];t=self.port.tvec(z)
        factors=[10.**(t@A@(r+theta*v+np.where(bits,hi,lo))) for theta in [-1.,1.] for bits in itertools.product([False,True],repeat=7)]
        np.testing.assert_allclose(env['electron_per_Href_s'],[base*min(factors),base*max(factors)],rtol=1e-13)

    def test_12_joint95_support_witness(self):
        q=self.port.Q_JOINT2_95;t=self.port.tvec(self.z);geo=self.geo
        center=geo['center'];G=geo['G'];V=geo['V']
        u=np.sign(G.T@t)
        delta=math.sqrt(q)*V@t/math.sqrt(t@V@t)
        a=center+G@u+delta
        upper=s.source_envelopes(self.z,self.y,self.rates,self.port,geo)['joint2_95']['logfactor_dex'][1]
        self.assertAlmostEqual(t@a,upper,13)
        self.assertAlmostEqual(delta@np.linalg.solve(V,delta),q,12)

    def test_13_out_of_domain_and_bad_state(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE_OBSERVATION'):
            s.source17(4.757,self.y,self.a,self.rates,self.port)
        with self.assertRaisesRegex(ValueError,'INVALID_Y17'):
            s.source17(self.z,np.full(17,-1.),self.a,self.rates,self.port)
        with self.assertRaisesRegex(ValueError,'INVALID_Y17'):
            s.source17(self.z,np.ones(16),self.a,self.rates,self.port)

    def test_14_no_li_or_nuclear_injection(self):
        self.assertEqual(np.max(np.abs(self.out['F'][13:])),0.)
        self.assertEqual(np.max(np.abs(self.out['B'][13:])),0.)
        self.assertEqual(self.out['photo_source_only'],True)
        self.assertEqual(self.out['physical_trajectory_derivative'],False)

    def test_15_saved_run_results(self):
        o=s.run_saved()
        self.assertEqual(len(o['entries']),7)
        self.assertGreater(o['stacked_119x2_singular_values'][1],0.)
        self.assertTrue(all(x['mu1_photo_only_per_s']==0 for x in o['entries']))
        self.assertEqual(o['new_ivp_count'],0)

if __name__=='__main__': unittest.main()
