import itertools
from fractions import Fraction
from math import isclose
import unittest

from rei_bianchi.microphysics.he import (BINDING_EV, EV_ERG, FIT_THRESHOLD_EV, LINE_EV,
                                        correlated_partition_bounds, f05_local_lya_ledger,
                                        primary_case_a_ledger)

class TestIntegratedHelium(unittest.TestCase):
    def test_correlated_event_conserves_photons_and_energy(self):
        for v, f, z in itertools.product((0., .3, 1.), (.1, .51, 1.), (0., .82, 1.)):
            l = f05_local_lya_ledger(7.5, v, f, z)
            self.assertTrue(isclose(l.absorbed_hi + l.absorbed_hei + l.escaped_photons, l.incoming_photons))
            self.assertTrue(isclose(l.heat_erg + l.binding_erg + l.escaped_erg, l.incoming_energy_erg))
            self.assertEqual(l.absorbed_heii, 0.)
            self.assertTrue(l.already_in_native_rhs)
        with self.assertRaises(ValueError): f05_local_lya_ledger(1., .2, 0., .4)

    def test_primary_uses_fit_cutoff_and_separate_physical_binding(self):
        for species, threshold in FIT_THRESHOLD_EV.items():
            l = primary_case_a_ledger(species, threshold, 10.)
            self.assertGreater(l.heat_erg, 0.)
            self.assertTrue(isclose(l.heat_erg + l.binding_erg, l.incoming_energy_erg))
            with self.assertRaises(ValueError): primary_case_a_ledger(species, BINDING_EV[species], 1.)
            self.assertEqual(primary_case_a_ledger(species, 0., 0.).heat_erg, 0.)

    def test_two_correlated_faces_exhaustive(self):
        # Integer endpoints and one unit-sum constraint have integral vertices.
        # Enumerate every integer point, independently of the production optimizer.
        for e in ((4, 4), (7, 9), (1, 8), (12,12)):
            bounds = correlated_partition_bounds(e, (0,5), (1,4), (0,3))
            pts = [(a,b,c) for a,b,c in itertools.product(range(6),range(1,5),range(4)) if e[0]<=a+b+c<=e[1]]
            weights = list(map(Fraction, ('13.598434599702','24.587389011','40.813320','1.602176634e-12')))
            h, he, line, conv = weights
            expected = {'emitted_photons':[sum(p) for p in pts], 'local_absorptions':[a+b for a,b,c in pts],
                        'emitted_energy_erg':[sum(p)*line*conv for p in pts], 'escaped_erg':[c*line*conv for a,b,c in pts],
                        'binding_erg':[(a*h+b*he)*conv for a,b,c in pts], 'heat_erg':[(a*(line-h)+b*(line-he))*conv for a,b,c in pts],
                        'hydrogen_absorptions':[a for a,b,c in pts], 'helium_absorptions':[b for a,b,c in pts]}
            self.assertEqual(bounds,{k:(min(v),max(v)) for k,v in expected.items()})
            h_lo,h_hi=bounds['hydrogen_absorptions'];he_lo,he_hi=bounds['helium_absorptions']
            self.assertIn((h_lo,he_hi),[(a,b) for a,b,c in pts]);self.assertIn((h_hi,he_lo),[(a,b) for a,b,c in pts])

    def test_empty_and_zero(self):
        with self.assertRaises(ValueError): correlated_partition_bounds((7,8),(1,2),(0,1),(0,1))
        self.assertTrue(all(v==(0,0) for v in correlated_partition_bounds(*([(0,0)]*4)).values()))
        for bad in (float('nan'), -1., float('inf')):
            with self.assertRaises(ValueError): f05_local_lya_ledger(bad,.3,.5,.6)

if __name__=='__main__': unittest.main()
