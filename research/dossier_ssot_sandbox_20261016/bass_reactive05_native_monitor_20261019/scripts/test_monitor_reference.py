#!/usr/bin/env python3
"""Independent reference tests with analytic values and threshold countercases."""
import math
import unittest
from monitor_reference import age_reference, cross_section_m2, CHI


class ReferenceTests(unittest.TestCase):
    def test_uniform_gl2_mass_moments_and_quantile_distance(self):
        f = .5 - math.sqrt(3)/6
        a = age_reference(0, [(f, .5), (1-f, .5)])
        self.assertEqual(a['mass'], 1.)
        self.assertAlmostEqual(a['mean'], .5, places=15)
        self.assertAlmostEqual(a['second'], 1/3, places=15)
        self.assertAlmostEqual(a['cdf_sup'], .5-f, places=15)
        self.assertAlmostEqual(a['w1'], f*f+(.5-f)**2, places=15)

    def test_thin_and_thick_reference(self):
        thin = age_reference('1e-300', [(.5, 1)])
        self.assertEqual(thin['exact_mass'], 1.)
        self.assertEqual(thin['exact_mean'], .5)
        self.assertEqual(thin['exact_second'], 1/3)
        self.assertEqual(thin['w1'], .25)
        thick = age_reference(1000, [(math.log(1000)/1000, 1)])
        self.assertEqual(thick['exact_mass'], .001)
        self.assertEqual(thick['exact_mean'], .001)
        self.assertEqual(thick['exact_second'], .000002)
        self.assertLess(abs(thick['relative_mass_defect']), 2e-15)

    def test_invalid_reference_input_is_rejected(self):
        for tau in ('NaN', 'Infinity', '-1'):
            with self.subTest(tau=tau), self.assertRaises(ValueError):
                age_reference(tau, [(.5, 1)])
        for nodes in ([(-.1, 1)], [(1.1, 1)], [(.5, -1)], [('NaN', 1)], [(.5, 'Infinity')]):
            with self.subTest(nodes=nodes), self.assertRaises(ValueError):
                age_reference(1, nodes)

    def test_binding_and_fitting_thresholds_remain_distinct(self):
        # The inherited H fit is zero between H binding and the 13.60 eV edge.
        self.assertEqual(cross_section_m2((CHI[0]+13.60)/2, 0), 0.)
        self.assertGreater(cross_section_m2(13.60, 0), 0.)
        # H-equality D cross section is additionally gated by manufactured D edge.
        energy = (13.60+CHI[3])/2
        self.assertGreater(cross_section_m2(energy, 0), 0.)
        self.assertEqual(cross_section_m2(energy, 3), 0.)
        self.assertEqual(cross_section_m2(20, 0), cross_section_m2(20, 3))


if __name__ == '__main__':
    unittest.main(verbosity=2)
