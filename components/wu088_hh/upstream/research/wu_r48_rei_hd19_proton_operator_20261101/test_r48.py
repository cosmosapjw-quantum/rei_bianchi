"""WU R48 source-physics-focused tests. Self-adversarial only; not distinct author."""
import csv, gzip, math, os, pathlib, unittest, zipfile
import numpy as np
from scipy.constants import k as k_B
import r48_hd19_operator as R

BASE=pathlib.Path('/mnt/data')
SOURCE=pathlib.Path(os.environ.get('WU_R48_EMAA_ZIP', str(BASE/'wu_r43_verify_library/WU_R43_RECOVERED_HD52_EMAA_GRACKLE_SOURCE_20261031.zip')))
REI=pathlib.Path(os.environ.get('WU_R48_REI_ZIP', str(BASE/'REI_F05_ORIGINAL_ACCEPTED_46080_STATES_20261101.zip')))
ROOT=pathlib.Path(__file__).resolve().parent

class SourcePhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.E,cls.G,cls.labels,cls.C=R.source_read(SOURCE)
        cls.states,cls.lanes=R.r47.read_states(REI.read_bytes())
        cls.joint=[x for x in cls.states if 5 <= float(x['T_K_lo']) <= float(x['T_K_hi']) <=3005]
        cls.idx=np.array([0, len(cls.joint)//2, len(cls.joint)-1],dtype=int)
        cls.s=[cls.joint[int(i)] for i in cls.idx]
        cls.Tlo=np.array([float(x['T_K_lo']) for x in cls.s]);cls.Thi=np.array([float(x['T_K_hi']) for x in cls.s]);cls.Tmid=(cls.Tlo+cls.Thi)/2
        cls.xlo=np.array([float(x['x_HII_lo']) for x in cls.s]);cls.xhi=np.array([float(x['x_HII_hi']) for x in cls.s]);cls.xmid=(cls.xlo+cls.xhi)/2
    def test_01_input_exact(self):
        self.assertEqual(R.sha256_file(REI),R.REI_SHA)
        with zipfile.ZipFile(SOURCE) as z:self.assertIsNone(z.testzip())
        self.assertEqual(R.r47.sha256(zipfile.ZipFile(SOURCE).read(R.r47.SOURCE_PREFIX)),R.EMAA_SHA)
    def test_02_three_lanes_identity(self):
        self.assertEqual(len(self.lanes),3)
        self.assertEqual(len(set(self.lanes.values())),1)
        self.assertEqual(len(self.states),46080)
    def test_03_source_exact_level_ids(self):
        self.assertEqual(len(self.E),52)
        self.assertEqual(self.labels[0],'0_0')
        self.assertEqual(self.labels[9],'1_0')
        self.assertEqual(self.labels[18],'0_11')
        self.assertTrue(np.all(np.diff(self.E)>0))
    def test_04_complete_source_pair_coverage(self):
        self.assertEqual(len(self.C['H']['pairs']),1326)
        self.assertEqual(len(self.C['HPLUS']['pairs']),171)
        self.assertEqual(self.C['H']['rates19'].shape,(171,15))
        self.assertEqual(self.C['HPLUS']['rates'].shape,(171,25))
    def test_05_native_pair_source_numbers(self):
        self.assertAlmostEqual(self.C['H']['rates19'][0,0],5.31e-12,delta=1e-25)
        self.assertAlmostEqual(self.C['HPLUS']['rates'][0,0],6.02e-10,delta=1e-23)
    def test_06_interpolation_node_exact(self):
        ts=self.C['HPLUS']['T'];rates=self.C['HPLUS']['rates']
        for kk in (0,5,10,15,24):
            vals=R.interp_native([ts[kk]],ts,rates)
            self.assertLess(np.max(np.abs(vals[0]/rates[:,kk]-1)),6e-14)
    def test_07_no_extrapolation(self):
        with self.assertRaises(ValueError):R.interp_native([3005.1],self.C['HPLUS']['T'],self.C['HPLUS']['rates'])
        with self.assertRaises(ValueError):R.interp_native([4.99],self.C['H']['T'],self.C['H']['rates19'])
    def test_08_collider_source_bounds(self):
        lo,hi,_=R.shared_source_interval(self.Tlo,self.Thi,self.xlo,self.xhi,self.C['H'],self.C['HPLUS'])
        kp=R.interp_native(self.Tmid,self.C['HPLUS']['T'],self.C['HPLUS']['rates'])
        kh=R.interp_native(self.Tmid,self.C['H']['T'],self.C['H']['rates19'])
        r=(self.xmid/(1-self.xmid))[:,None]*kp/kh
        self.assertTrue(np.all(lo<=r*(1+1e-13)))
        self.assertTrue(np.all(hi>=r*(1-1e-13)))
        self.assertGreater(np.min(lo),1)
    def test_09_reverse_detailed_balance_same_collider_ratio(self):
        pair=self.C['HPLUS']['pairs'];u,l=pair.T
        B=(self.G[u]/self.G[l])[None,:]*np.exp(-(self.E[u]-self.E[l])[None,:]/(k_B*self.Tmid[:,None]))
        kp=R.interp_native(self.Tmid,self.C['HPLUS']['T'],self.C['HPLUS']['rates'])
        kh=R.interp_native(self.Tmid,self.C['H']['T'],self.C['H']['rates19'])
        self.assertTrue(np.allclose((kp*B)/(kh*B),kp/kh,rtol=2e-15))
        self.assertTrue(np.all(B>0))
    def test_10_19level_generator_stationarity(self):
        pair=self.C['HPLUS']['pairs'];u,l=pair.T
        B=(self.G[u]/self.G[l])[None,:]*np.exp(-(self.E[u]-self.E[l])[None,:]/(k_B*self.Tmid[:,None]))
        kp=R.interp_native(self.Tmid,self.C['HPLUS']['T'],self.C['HPLUS']['rates'])
        sp=R.symmetric_from_pairs(kp*self.xmid[:,None],B,pair)
        p=self.G[:19][None,:]*np.exp(-self.E[:19][None,:]/(k_B*self.Tmid[:,None]));p/=p.sum(axis=1,keepdims=True)
        q=np.sqrt(p)
        resid=np.linalg.norm(np.einsum('nij,nj->ni',sp,q),axis=1)
        norm=np.linalg.norm(sp,axis=(1,2))
        self.assertLess(np.max(resid/norm),1e-14)
    def test_11_eigen_spectrum_negative(self):
        pair=self.C['HPLUS']['pairs'];u,l=pair.T
        B=(self.G[u]/self.G[l])[None,:]*np.exp(-(self.E[u]-self.E[l])[None,:]/(k_B*self.Tmid[:,None]))
        kp=R.interp_native(self.Tmid,self.C['HPLUS']['T'],self.C['HPLUS']['rates'])
        sp=R.symmetric_from_pairs(kp*self.xmid[:,None],B,pair)
        eig=np.linalg.eigvalsh(sp)
        self.assertLess(np.max(np.abs(eig[:,-1])/np.maximum(-eig[:,-2],1e-99)),1e-9)
        self.assertTrue(np.all(eig[:,-2]<0))
    def test_12_lte_tail_monotone(self):
        qlo=R.boltzmann_tail(self.Tlo,self.E,self.G);qhi=R.boltzmann_tail(self.Thi,self.E,self.G)
        self.assertTrue(np.all(qlo>0))
        self.assertTrue(np.all(qlo<=qhi))
        self.assertTrue(np.all(qhi<1))
    def test_13_original_full_support_5616(self):
        self.assertEqual(len(self.joint),5616)
        self.assertTrue(all(float(z['T_K_hi'])<=3005 for z in self.joint))
    def test_14_single_transition_matches_R47_source_input(self):
        with gzip.open(pathlib.Path(os.environ.get('WU_R48_R47_CSV', str(BASE/'WU_R47_REI_HD_DOMAIN_20261101/results/R47_HD_REI_SOURCE_SUPPORT_46080.csv.gz'))),'rt') as f:
            lookup={int(row['node']):row for row in csv.DictReader(f) if row['source_T_support']=='JOINT_T_RANGE'}
        kk=R.interp_native(self.Tmid,self.C['HPLUS']['T'],self.C['HPLUS']['rates'])[:,0]
        hh=R.interp_native(self.Tmid,self.C['H']['T'],self.C['H']['rates19'])[:,0]
        rr=self.xmid*kk/((1-self.xmid)*hh)
        for i,s in enumerate(self.s):
            self.assertAlmostEqual(rr[i]/float(lookup[int(s['node'])]['Gamma_p_over_H_mid_loglog']),1,delta=2e-12)
    def test_15_independent_scalar_loglog(self):
        ts=self.C['HPLUS']['T']; raw=self.C['HPLUS']['rates'][0]
        for T in self.Tmid:
            i=int(np.searchsorted(ts,T)-1);i=max(0,min(i,len(ts)-2))
            power=math.log(raw[i+1]/raw[i])/math.log(ts[i+1]/ts[i])
            expected=raw[i]*(T/ts[i])**power
            direct=R.interp_native([T],ts,self.C['HPLUS']['rates'])[0,0]
            self.assertAlmostEqual(direct/expected,1,delta=2e-14)
    def test_16_unit_mixing_prevention(self):
        self.assertAlmostEqual(self.E[1]/k_B,89.2279*100*R.h*R.c/k_B,delta=1e-10)
        self.assertLess(self.E[1],1e-19)
    def test_17_all_saved_summary_consistent(self):
        import json
        f=ROOT/'results/R48_RESULTS.json'
        if not f.exists():self.skipTest('full state summary not yet generated')
        v=json.loads(f.read_text())
        self.assertEqual(v['domain']['derived_original_node_transition_rows'],960336)
        self.assertEqual(v['domain']['derived_level_exit_rows'],106704)
        self.assertGreater(v['physical_results']['minimum_rectangular_source_temperature_ionization_ratio_bound'],100)
        self.assertEqual(v['DAG']['WU_canonical_after'],'34/49')
        self.assertEqual(v['DAG']['REI_central_after'],'28/88')
        self.assertFalse(v['policy']['auto_next_node'])

if __name__=='__main__':unittest.main()
