from __future__ import annotations
import json, math, sys, unittest
from pathlib import Path
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from code import spectral_witness as sw
from code import upstream_native_rate as source

class PhysicalFastSixMomentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.net=source.new_native_network()
        cls.energies,cls.M,cls.sigma=sw.six_moment_matrix(cls.net)
        cls.rows=source.json.loads((source.SRC/'REI_SAVED7.json').read_text())['rows']

    def test_01_exact_original_source_pins(self):
        pins=source.source_manifest_check()
        self.assertEqual(len(pins),3)
        self.assertEqual(source.EXPECTED['BASS_ATOMIC_NETWORK.py'],pins['BASS_ATOMIC_NETWORK.py'])
        self.assertEqual(self.M.shape,(6,len(self.energies)))
        self.assertEqual(len(self.energies),71)

    def test_02_positive_moments_seven_saved(self):
        for r in self.rows:
            z=float(r['z']);t=sw.target_six(z);v=sw.nonnegative_witness(self.M,t)
            self.assertTrue(np.all(v['flux']>=0));self.assertLessEqual(len(v['active_indices']),6)
            pred=self.M@v['flux'];rel=np.max(abs(pred/t-1))
            self.assertLess(rel,1e-10)
            self.assertGreater(v['flux_total'],0)

    def test_03_independent_mp_75_decimal_binary_input(self):
        mp.mp.dps=75
        def exact_mp(x):
            n,d=float(x).as_integer_ratio()
            return mp.mpf(n)/d
        for r in self.rows:
            t=sw.target_six(float(r['z']));out=sw.nonnegative_witness(self.M,t)
            ind=out['active_indices'];self.assertEqual(len(ind),6)
            B=mp.matrix(6,6)
            for i in range(6):
                for j,k in enumerate(ind): B[i,j]=exact_mp(out['scaled_matrix'][i,k])
            x=mp.lu_solve(B,mp.matrix([1]*6))
            self.assertGreater(min(x),mp.mpf('1e-10'))
            self.assertLess(max(abs(q-1) for q in B*x),mp.mpf('1e-58'))

    def test_04_li_blind_bin_exact_H_He_null(self):
        z=float(self.rows[3]['z']);v=sw.nonnegative_witness(self.M,sw.target_six(z))
        w=sw.li_blind_witness(self.energies,self.M,self.sigma,v['flux'])
        i=w['index'];self.assertTrue(5.392<w['energy_eV']<13.6)
        self.assertTrue(np.array_equal(self.M[:,i],np.zeros(6)))
        self.assertGreater(w['delta_Gamma_LiI_s'],0)
        self.assertLess(w['max_absolute_HHe_moment_change'],1e-27)

    def test_05_arbitrary_nonnegative_blind_flux_family(self):
        z=float(self.rows[-1]['z']);v=sw.nonnegative_witness(self.M,sw.target_six(z))
        w=sw.li_blind_witness(self.energies,self.M,self.sigma,v['flux']);i=w['index']
        for t in (0,0.1,1,10,1000):
            plus=v['flux'].copy();plus[i]+=t*1e9
            self.assertLess(np.max(abs(self.M@plus-self.M@v['flux'])),1e-26)
            delta=float(self.sigma[13]@(plus-v['flux']))
            self.assertAlmostEqual(delta,t*1e9*w['sigma_LiI_m2'],delta=max(1e-30,1e-13*t*1e-10))

    def test_06_rei_li7_species_response(self):
        for r in self.rows:
            v=sw.nonnegative_witness(self.M,sw.target_six(float(r['z'])))
            w=sw.li_blind_witness(self.energies,self.M,self.sigma,v['flux'])
            self.assertGreater(r['y'][13]*w['delta_Gamma_LiI_s'],0)

    def test_07_P19_domain_and_heat_units(self):
        for z in (0,2.32,4.89,20,-1):
            with self.assertRaises(ValueError):sw.target_six(z)
        t=sw.target_six(float(self.rows[3]['z']))
        self.assertTrue(np.all(t>0));self.assertGreater(t[3]/t[0],0.5)
        self.assertGreater(t[5]/t[2],1.0)

    def test_08_hydrogen_helium_thresholds(self):
        thresholds=self.net.transition_energy_eV[list(sw.SPECIES)]
        self.assertEqual(tuple(sw.SPECIES),(1,7,8))
        self.assertTrue(np.allclose(thresholds,[13.6,24.59,54.42],rtol=0,atol=1e-12))
        sub=self.energies[(self.energies>5.392)&(self.energies<13.6)]
        self.assertGreater(len(sub),3)
        sig,_=self.net.photo_cross_sections(sub)
        self.assertTrue(np.all(sig[list(sw.SPECIES)]==0))
        self.assertTrue(np.all(sig[13]>0))

    def test_09_rebuild_complete_result_no_IVP(self):
        result=sw.seven_saved_witnesses()
        self.assertEqual(len(result['cases']),7)
        self.assertEqual(result['new_ivps'],0)
        self.assertEqual(result['number_of_BASS_original_bin_centres'],71)
        self.assertTrue(all(a['support_size']==6 and a['max_rel_error']<1e-10 for a in result['cases']))

    def test_10_numerical_controls_and_bad_shapes(self):
        t=sw.target_six(float(self.rows[0]['z']))
        with self.assertRaises(ValueError):sw.nonnegative_witness(self.M[:5],t)
        with self.assertRaises(ValueError):sw.nonnegative_witness(self.M,np.r_[t[:5],-1.])
        with self.assertRaises(ValueError):sw.nonnegative_witness(self.M[:, :4],t)
        v=sw.nonnegative_witness(self.M,t)
        e=self.energies;sig=self.sigma
        with self.assertRaises(ValueError):sw.li_blind_witness(e,self.M[:,:].copy()+1e-50,sig,v['flux'])

    def test_11_LiI_positive_dual_min_and_unbounded_max(self):
        for row in self.rows:
            t=sw.target_six(float(row['z']))
            b=sw.conditional_li_photo_bounds(self.energies,self.M,self.sigma,t)
            self.assertEqual(b['LiI_gamma_upper'],'UNBOUNDED')
            self.assertGreater(b['LiI_gamma_lower_s'],0)
            self.assertLess(b['LiI_dual_max_violation_scaled'],2e-7)
            self.assertLess(b['LiI_dual_gap_scaled'],2e-7)

    def test_12_LiII_LiIII_upper_from_fixed_HeII_moment(self):
        t=sw.target_six(float(self.rows[3]['z']))
        b=sw.conditional_li_photo_bounds(self.energies,self.M,self.sigma,t)
        lp=sw.nonnegative_witness(self.M,t)
        for i,key in [(14,'LiII'),(15,'LiIII')]:
            rate=float(self.sigma[i]@lp['flux'])
            self.assertLessEqual(rate,b['Li_higher_upper'][key]['gamma_upper_s']*(1+1e-13))
            self.assertGreater(b['Li_higher_upper'][key]['max_sigma_ratio_to_HeII'],0)

if __name__=='__main__':unittest.main()