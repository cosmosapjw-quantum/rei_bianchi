"""New source-specific behavior tests. No upstream scientific suite is run."""
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
from cutoff_certificate import cutoff_box, cutoff_displacement


def point(u):
    return [(0,0),(0,0),(0,0),(u,u),(0,0),(0,0),(0,0)]


class CutoffCertificateTests(unittest.TestCase):
    def test_exact_extrema_of_actual_composition_affine_form(self):
        box=[(0,F(1,2)),(0,F(1,4)),(0,F(1,4)),(12000,24000),(0,1),(0,2),(0,3)]
        self.assertEqual(cutoff_box(2,1,1,box), (F(-18750),F(21000),'CUTOFF_INTERSECTING'))

    def test_analytic_interior(self):
        self.assertEqual(cutoff_box(1,0,1,point(4501)),(F(2),F(2),'SMOOTH_ANALYTIC'))

    def test_floor_interior(self):
        self.assertEqual(cutoff_box(1,0,1,point(4499)),(F(-2),F(-2),'SMOOTH_FLOOR'))

    def test_exact_boundary_is_not_smooth_floor(self):
        self.assertEqual(cutoff_box(1,0,1,point(4500)),(F(0),F(0),'EXACT_CUTOFF'))

    def test_touch_from_above_is_not_global_smooth(self):
        box=point(4500);box[3]=(4500,4501)
        self.assertEqual(cutoff_box(1,0,1,box),(F(0),F(2),'CUTOFF_INTERSECTING'))

    def test_touch_from_below_is_not_global_smooth(self):
        box=point(4500);box[3]=(4499,4500)
        self.assertEqual(cutoff_box(1,0,1,box),(F(-2),F(0),'CUTOFF_INTERSECTING'))

    def test_exact_rational_separator_does_not_round_to_cutoff(self):
        e=F(1,10**100)
        self.assertEqual(cutoff_box(1,0,1,point(F(4500)+e)),(2*e,2*e,'SMOOTH_ANALYTIC'))

    def test_photon_coordinates_do_not_change_the_cutoff(self):
        box=point(4501);box[4:]=[(0,1000000),(0,2000000),(0,3000000)]
        self.assertEqual(cutoff_box(1,0,1,box),(F(2),F(2),'SMOOTH_ANALYTIC'))

    def test_absent_hydrogen_source_is_identically_zero(self):
        box=point(4500);box[3]=(4000,5000)
        self.assertEqual(cutoff_box(0,1,1,box),(F(-1000),F(1000),'ZERO_HH_SOURCE'))

    def test_unphysical_population_box_rejected(self):
        box=point(4500);box[1]=(0,F(3,4));box[2]=(0,F(1,2))
        with self.assertRaises(ValueError):cutoff_box(1,1,1,box)

    def test_float_inputs_rejected(self):
        with self.assertRaises(ValueError):cutoff_box(1.0,0,1,point(4500))

    def test_reversed_intervals_rejected(self):
        box=point(4500);box[3]=(4501,4500)
        with self.assertRaises(ValueError):cutoff_box(1,0,1,box)

    def test_seven_coordinate_shape_required(self):
        with self.assertRaises(ValueError):cutoff_box(1,0,1,point(4500)[:4])

    def test_nonpositive_thermal_energy_rejected(self):
        with self.assertRaises(ValueError):cutoff_box(1,0,1,point(0))

    def test_zero_boltzmann_constant_rejected(self):
        with self.assertRaises(ValueError):cutoff_box(1,0,0,point(4500))

    def test_positive_density_sum_required(self):
        with self.assertRaises(ValueError):cutoff_box(0,0,1,point(4500))

    def test_exact_cutoff_displacement(self):
        self.assertEqual(cutoff_displacement(1,1,150000,1,F(9003,2)),F(1,103000))

    def test_zero_displacement_at_cutoff(self):
        self.assertEqual(cutoff_displacement(1,1,150000,1,4500),F(0))

    def test_cold_displacement_sign(self):
        self.assertEqual(cutoff_displacement(1,1,150000,1,F(8997,2)),F(-1,103000))

    def test_no_density_division_for_vacuum(self):
        with self.assertRaises(ValueError):cutoff_displacement(0,1,150000,1,4500)

if __name__=='__main__':unittest.main()
