"""Focused science/identity tests: measured bins plus conditional energy convolution."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import trapezoid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_igrb_exfor import (load_data,compute,interpolate_sigma,spectral_shape,
                              NB_CM2,C_CMS,Q_MEV,integral_with_knots)

class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fermi,cls.exfor=load_data(ROOT)
        cls.fit=compute(ROOT)
        cls.flat=compute(ROOT,'flat_within_bin')
    def test_transcription_units_and_source(self):
        self.assertEqual(self.fermi['foreground_model'],'A')
        self.assertEqual(self.fermi['doi'],'10.1088/0004-637X/799/1/86')
        self.assertEqual(self.exfor['subentry'],'M0475003')
        self.assertEqual(len(self.fermi['bins']),2)
        self.assertEqual(len(self.exfor['rows']),6)
        self.assertEqual([x[0] for x in self.exfor['rows']],[201,225,253,285,320,359])
    def test_measured_fermi_two_bin_intensities(self):
        a,b=self.fermi['bins']
        self.assertEqual(float(a['IGRB_intensity']),1.1e-6)
        self.assertEqual(float(b['IGRB_intensity']),6.7e-7)
        self.assertEqual(float(a['IGRB_fg_minus']),4e-7)
        self.assertEqual(float(b['EGB_intensity']),9.7e-7)
    def test_curated_source_byte_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td);(path/'data').mkdir()
            for f in (ROOT/'data').glob('*.json'):
                (path/'data'/f.name).write_bytes(f.read_bytes())
            p=path/'data/fermi_2015_table3_two_bins.json'
            p.write_bytes(p.read_bytes().replace(b'1.1e-6',b'1.2e-6'))
            with self.assertRaisesRegex(ValueError,'CURATED_FERMI_DATA_IDENTITY_MISMATCH'):
                load_data(path)
    def test_cross_section_no_unmeasured_extrapolation(self):
        for E in (200,359.000001,400):
            with self.assertRaisesRegex(ValueError,'NO_UNMEASURED_ENERGY_EXTRAPOLATION'):
                interpolate_sigma(E,self.exfor['rows'])
    def test_reported_cross_section_recovers_exact_nodes(self):
        for E,sigma,_ in self.exfor['rows']:
            self.assertAlmostEqual(interpolate_sigma(E,self.exfor['rows']),float(sigma),places=13)
    def test_pair_birth_defect_only_not_heat(self):
        self.assertAlmostEqual(Q_MEV,23.8464782,places=7)
        for component in ('IGRB','EGB'):
            total=self.fit['totals'][component]
            self.assertGreater(total['rate_like_per_He_s_minus1'],0)
            self.assertGreater(total['kinetic_like_MeV_per_He_s'],0)
        for key in ('R_event','heat_rate','D_fast_transport','cosmological_redshift_history','event_normalization'):
            self.assertIsNone(self.fit[key])
        self.assertFalse(self.fit['physical_activation'])
        self.assertFalse(self.fit['L4'])
        self.assertEqual(self.fit['production'],'HOLD')
    def test_both_bins_are_partially_covered(self):
        covered={(tuple(x['Fermi_bin_MeV']),tuple(x['included_support_MeV']))
                 for x in self.fit['bins']}
        self.assertEqual(covered,{((200,280),(201,280)),((280,400),(280,359))})
        self.assertTrue(all(0<x['modeled_fraction_within_EXFOR_support']<1 for x in self.fit['bins']))
    def test_model_difference_is_not_data_error(self):
        a=self.fit['totals']['IGRB']['rate_like_per_He_s_minus1']
        b=self.flat['totals']['IGRB']['rate_like_per_He_s_minus1']
        self.assertGreater(abs(a-b)/a,0.05)
        self.assertLess(abs(a-b)/a,0.2)
    def test_both_categories_separate_not_summed(self):
        self.assertGreater(self.fit['totals']['EGB']['rate_like_per_He_s_minus1'],
                           self.fit['totals']['IGRB']['rate_like_per_He_s_minus1'])
        self.assertEqual(len([b for b in self.fit['bins'] if b['component']=='IGRB']),2)
    def test_bin_number_density_mapping(self):
        I=sum(float(b['IGRB_intensity']) for b in self.fermi['bins'])
        self.assertAlmostEqual(self.fit['totals']['IGRB']['photon_number_density_in_two_bins_cm_minus3'],
                               4*math.pi*I/C_CMS,delta=1e-28)
    def test_independent_brute_force_quadrature(self):
        # Different vectorized trapezoidal algorithm vs source adaptive quad
        for b in self.fit['bins']:
            category=b['component']; lo,hi=b['included_support_MeV']
            fermi_b=next(x for x in self.fermi['bins'] if x['energy_min_MeV']==b['Fermi_bin_MeV'][0])
            allE=np.linspace(*b['Fermi_bin_MeV'],300001)
            g=np.power(allE/100.,-2.32)*np.exp(-allE/279000.)
            norm=trapezoid(g,allE)
            E=np.linspace(lo,hi,300001)
            s=np.interp(E,[x[0] for x in self.exfor['rows']],[float(x[1]) for x in self.exfor['rows']])
            weighted=trapezoid((E/100.)**(-2.32)*np.exp(-E/279000.)*s,E)/norm
            rate=4*math.pi*NB_CM2*float(fermi_b[category+'_intensity'])*weighted
            self.assertAlmostEqual(rate/b['conditional_rate_like_per_He_s_minus1'],1.,delta=2e-8)
    def test_uncertainty_separates_foreground_and_stat(self):
        for key in ('EGB','IGRB'):
            a=self.fit['totals'][key]
            self.assertGreater(a['Fermi_foreground_minus_s_minus1'],0)
            self.assertGreater(a['Fermi_stat_sd_independent_only_s_minus1'],0)
            self.assertTrue(all(a[x]<a['rate_like_per_He_s_minus1'] for x in
                                ('Fermi_foreground_minus_s_minus1','Fermi_stat_sd_independent_only_s_minus1')))

if __name__=='__main__':unittest.main()
