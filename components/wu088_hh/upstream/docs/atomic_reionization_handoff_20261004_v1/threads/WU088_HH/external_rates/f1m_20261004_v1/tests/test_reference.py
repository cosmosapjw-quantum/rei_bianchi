from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,unittest
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hh_moment_compatibility import analytic_moments,raw_monotonicity_witness,MomentError

def f(record):return F(int(record['numerator']),int(record['denominator']))

class Regression(unittest.TestCase):
    def test_exact_shapes_and_temperature_scaling(self):
        for provider,a in [('LCS91',F(27,10)),('GLOVER2015_KS91_EQ14',F(3))]:
            one=analytic_moments(provider,'10000');two=analytic_moments(provider,'20000')
            self.assertEqual(f(one['gamma_shape']),a)
            self.assertEqual(f(two['variance_energy_over_kB2_K2']),4*f(one['variance_energy_over_kB2_K2']))
    def test_mean_is_above_activation_but_not_a_heat_value(self):
        x=analytic_moments('LCS91','10000')
        self.assertGreater(f(x['mean_energy_over_kB_K']),f(x['activation_energy_over_kB_K']))
        self.assertIsNone(x['thermal_loss_per_event_J']);self.assertIsNone(x['outgoing_electron_spectrum'])
    def test_source_identifiers_are_preserved(self):
        self.assertEqual(analytic_moments('KS92_corrected_Glover15','10000'),analytic_moments('GLOVER2015_KS91_EQ14','10000'))
    def test_invalid_values_are_not_silently_zeroed(self):
        for val in [True,1.0,'NaN','Infinity','0','-1','1e1001']:
            with self.assertRaises(MomentError):analytic_moments('LCS91',val)
    def test_unknown_provider_is_refused(self):
        with self.assertRaises(MomentError):analytic_moments('arbitrary','10000')
    def test_corrected_scenario_does_not_inherit_raw_floor(self):
        x=analytic_moments('GLOVER2015_KS91_EQ14','1000')
        self.assertEqual(f(x['mean_energy_over_kB_K']),160800)
        self.assertFalse(x['admission'])
    def test_cutoff_strict_order_is_required(self):
        for pair in [('3001','3000'),('3000','3000'),('0','3001'),('3001','3002')]:
            with self.assertRaises(MomentError):raw_monotonicity_witness(*pair)
    def test_witness_inherits_raw_floor_without_modifying_it(self):
        x=raw_monotonicity_witness()
        self.assertEqual(x['values'][0]['raw_rate_cm3_s'],['1E-20','1E-20'])
        self.assertFalse(x['original_floor_modified']);self.assertFalse(x['admission'])
    def test_one_pair_without_violation_does_not_admit_a_kernel(self):
        x=raw_monotonicity_witness('3000','1000000')
        self.assertFalse(x['violates_nonnegative_fixed_kernel_necessary_condition'])
        self.assertFalse(x['nonviolation_is_kernel_admission'])
    def test_original_reference_bytes_preserved(self):
        original=ROOT/'sources/hh_external.original.py'
        self.assertEqual((ROOT/'src/hh_external.py').read_bytes(),original.read_bytes())
    def test_cli_exclusive_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result.json'
            cmd=[sys.executable,'-B',str(ROOT/'src/hh_moment_compatibility.py'),'--mode','moments','--T','10000','--out',str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
            before=out.read_bytes();r=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(before,out.read_bytes())
    def test_cli_unsupported_floor_leaves_no_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result.json'
            r=subprocess.run([sys.executable,'-B',str(ROOT/'src/hh_moment_compatibility.py'),'--mode','moments','--T','3000','--out',str(out)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertFalse(out.exists())

if __name__=='__main__':unittest.main()
