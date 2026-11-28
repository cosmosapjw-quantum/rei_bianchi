from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hh_moment_compatibility import analytic_moments,raw_monotonicity_witness,MomentError

class RequiredBehavior(unittest.TestCase):
    def test_incoming_mean_is_not_activation_energy_alone(self):
        got=analytic_moments('LCS91','10000')
        self.assertEqual(got.get('mean_energy_over_kB_K'),{'numerator':'184800','denominator':'1'})
    def test_raw_floor_cannot_be_promoted_to_analytic_kernel(self):
        with self.assertRaisesRegex(MomentError,'RAW_FLOOR_NOT_ANALYTIC_KERNEL'):
            analytic_moments('LCS91','3000')
    def test_strict_raw_transform_monotonicity_violation(self):
        self.assertIs(raw_monotonicity_witness().get('violates_nonnegative_fixed_kernel_necessary_condition'),True)
    def test_incoming_energy_is_not_ionization_heat(self):
        with self.assertRaisesRegex(MomentError,'OUTGOING_PARTITION_OR_HEAT_NOT_DETERMINED'):
            analytic_moments('LCS91','10000',quantity='thermal_loss')

if __name__=='__main__':unittest.main()
