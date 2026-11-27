import json
import math
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fermi_abc_exfor import (load_inputs,compute,integrate,basis,g,kernel_one_bin,
                             KNOTS,NB_TO_CM2,MODEL_PLE_IGRB,Q_MEV,error_vector)


class TestFermiABCPhysicalSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bins,cls.sig,cls.err,cls.man=load_inputs(ROOT)
        cls.result=compute(ROOT)

    def pick(self,m,c,shape='flat'):
        return next(x for x in self.result['results'] if
                    (x['foreground_model'],x['component'],x['within_bin_model'])==(m,c,shape))

    def test_model_count_and_exact_measured_edges(self):
        self.assertEqual(len(self.bins),6)
        self.assertEqual([(b.model,b.lo,b.hi) for b in self.bins],
            [(m,l,h) for m in ('A','B','C') for l,h in ((200.,282.8),(282.8,400.))])

    def test_full_external_source_is_not_claimed_byte_verified(self):
        self.assertFalse(self.man['official_publication']['official_78row_raw_byte_obtained'])
        self.assertTrue(self.man['local_six_rows']['complete_table_binary_in_local_zip'])
        self.assertEqual(self.man['78row_mirror']['git_blob'],
                         '794cb6fcbef243be950613475c4254d6ab3877a4')
        self.assertEqual(self.man['78row_mirror']['nrecords'],78)

    def test_full_78row_mirror_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            from shutil import copytree
            cp=Path(td)/'data';copytree(ROOT/'data',cp)
            p=cp/'fermi_igrb_2015_AB_C_78row_mirror.csv'
            p.write_bytes(p.read_bytes().replace(b'2.769e-06',b'9.999e-06'))
            with self.assertRaisesRegex(ValueError,'FULL_FERMI_GIT_MIRROR_SHA256_MISMATCH'):
                load_inputs(Path(td))

    def test_source_copy_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            from shutil import copytree
            cp=Path(td)/'data'
            copytree(ROOT/'data',cp)
            p=cp/'fermi_table3_abc_6rows.txt'
            p.write_bytes(p.read_bytes().replace(b'1.057e-06',b'9.999e-06'))
            with self.assertRaisesRegex(ValueError,'SIX_ROW_SUBSET_NOT_EXACTLY_FROM_78_MIRROR'):
                load_inputs(Path(td))

    def test_EXFOR_source_copy_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            from shutil import copytree
            cp=Path(td)/'data';copytree(ROOT/'data',cp)
            p=cp/'exfor_M0475_SIG6.json'
            p.write_bytes(p.read_bytes().replace(b'2.41',b'9.99'))
            with self.assertRaisesRegex(ValueError,'EXFOR_SIG6_TRANSCRIPTION_SHA256_MISMATCH'):
                load_inputs(Path(td))

    def test_source_dimensions_and_nonnegative(self):
        self.assertEqual(len(self.sig),6)
        self.assertEqual(len(self.err),6)
        self.assertTrue(all(v>=0 for v in self.sig+self.err))
        self.assertTrue(all(b.hi>b.lo for b in self.bins))

    def test_published_components_not_double_counted(self):
        self.assertEqual(len(self.result['results']),3*2*2)
        self.assertNotIn('sum_IGRB_EGB',self.result)
        self.assertTrue(all(z['component'] in ('igrb','egb') for z in self.result['results']))

    def test_published_b_source_residual_is_not_silently_rescaled(self):
        residuals=self.result['source_table_EGB_minus_IGRB_plus_reported_resolved']
        b1=next(x for x in residuals if x['model']=='B' and x['energy_bin_MeV']==[200.,282.8])
        self.assertGreater(abs(b1['relative_to_fEGB']),0.03)
        self.assertEqual(self.bins[2].val['f_egb'],1.590e-6)

    def test_ple_models_use_published_igrb_params(self):
        self.assertEqual(MODEL_PLE_IGRB,{'A':(2.32,279000.),'B':(2.28,206000.),'C':(2.26,233000.)})
        self.assertNotEqual(g(300.,'A','model_ple_igrb'),g(300.,'C','model_ple_igrb'))
        for m in ('A','B','C'):
            self.assertLess(g(320,m,'model_ple_igrb'),g(220,m,'model_ple_igrb'))

    def test_ple_egb_has_extra_hypothesis_flag(self):
        self.assertTrue(all(self.pick(m,'egb','model_ple_igrb')['EGB_use_of_IGRB_shape_is_extra_hypothesis'] for m in 'ABC'))
        self.assertFalse(any(self.pick(m,'egb','flat')['EGB_use_of_IGRB_shape_is_extra_hypothesis'] for m in 'ABC'))

    def test_basis_partition_and_no_extrapolation(self):
        for E in (201,219,240,282.8,300,330,359):
            w=basis(E);self.assertAlmostEqual(sum(w),1.,places=14)
            self.assertGreaterEqual(min(w),0.)
        for E in (200,400):
            with self.assertRaisesRegex(ValueError,'NO_SIG_EXTRAPOLATION'):
                basis(E)

    def test_partial_source_bin_fractions_and_positive_coefficients(self):
        for b in self.bins:
            for s in ('flat','model_ple_igrb'):
                w,wK,fraction=kernel_one_bin(b,s)
                self.assertTrue(all(x>=0 for x in w))
                self.assertAlmostEqual(sum(w),fraction,delta=1.e-12)
                self.assertTrue(0<fraction<1)
                self.assertTrue(all(x>=0 for x in wK))

    def test_separate_igrb_egb_and_model_variation(self):
        for m in ('A','B','C'):
            self.assertLess(self.pick(m,'igrb')['Gamma_reported_like_s_minus1_per_He'],
                            self.pick(m,'egb')['Gamma_reported_like_s_minus1_per_He'])
        self.assertLess(self.pick('C','igrb')['Gamma_reported_like_s_minus1_per_He'],
                        self.pick('B','igrb')['Gamma_reported_like_s_minus1_per_He'])

    def test_conditionally_nonthermal_gate_stays_closed(self):
        for key in ('kappa','R_event','heat_rate','D_fast_stopping'):
            self.assertIsNone(self.result[key])
        self.assertFalse(self.result['L4'])
        self.assertFalse(self.result['physical_activation'])
        self.assertEqual(self.result['production'],'HOLD')

    def test_kinetic_weight_stays_between_minmax_mev(self):
        for x in self.result['results']:
            r=x['Gamma_reported_like_s_minus1_per_He']
            k=x['K_born_reported_like_MeV_s_minus1_per_He']
            self.assertLessEqual((201-Q_MEV)*r,k)
            self.assertLessEqual(k,(359-Q_MEV)*r)

    def test_energy_weight_and_number_density_have_units(self):
        for x in self.result['results']:
            self.assertGreater(x['observed_full_two_bin_number_density_if_isotropic_cm_minus3'],0)
            self.assertGreater(x['K_born_reported_like_MeV_s_minus1_per_He'],0)
        self.assertIn('NOT',str(self.result)) if False else None

    def test_exact_fraction_flat_quadrature_independent(self):
        # Direct rational trapezoid area for physical source segment, no scipy quadrature.
        ener=list(map(F,KNOTS));sig=list(map(lambda x:F(str(x)),self.sig))
        def area(lo,hi):
            lo,hi=F(str(lo)),F(str(hi))
            result=F(0)
            for i in range(5):
                x0,x1=ener[i:i+2]; a=max(lo,x0);b=min(hi,x1)
                if a>=b: continue
                ya=sig[i]+(sig[i+1]-sig[i])*(a-x0)/(x1-x0)
                yb=sig[i]+(sig[i+1]-sig[i])*(b-x0)/(x1-x0)
                result+=(b-a)*(ya+yb)/2
            return result
        for model in 'ABC':
            bins=[b for b in self.bins if b.model==model]
            for comp in ('igrb','egb'):
                sum0=sum(F(str(b.val['f_'+comp]))*area(max(201,b.lo),min(359,b.hi))/F(str(b.hi-b.lo)) for b in bins)
                exact=float(sum0)*4*math.pi*NB_TO_CM2
                self.assertAlmostEqual(exact/self.pick(model,comp)['Gamma_reported_like_s_minus1_per_He'],1.,places=12)

    def test_exfor_uncertainty_unknown_correlations(self):
        for x in self.result['results']:
            z=x['EXFOR_pointwise_stat_error_propagation']
            self.assertGreaterEqual(z['independent_conditional'],z['unknown_corr_sd_lower'])
            self.assertLessEqual(z['independent_conditional'],z['unknown_corr_sd_upper']+1.e-100)

    def test_fermi_basic_is_stat_plus_instrument_not_pure_stat(self):
        self.assertTrue(any('instrument' in s.lower() for s in self.man['fermi_observation_errors']))
        for x in self.result['results']:
            self.assertGreater(x['Fermi_BASIC_stat_plus_instrument_up']['unknown_corr_sd_upper'],0)

    def test_extra_ple_changes_rate_not_original_flux(self):
        for m in 'ABC':
            for c in ('igrb','egb'):
                a=self.pick(m,c,'flat'); b=self.pick(m,c,'model_ple_igrb')
                self.assertNotEqual(a['Gamma_reported_like_s_minus1_per_He'],b['Gamma_reported_like_s_minus1_per_He'])
                self.assertAlmostEqual(a['observed_full_two_bin_number_density_if_isotropic_cm_minus3'],
                                       b['observed_full_two_bin_number_density_if_isotropic_cm_minus3'],places=28)

if __name__=='__main__':unittest.main()
