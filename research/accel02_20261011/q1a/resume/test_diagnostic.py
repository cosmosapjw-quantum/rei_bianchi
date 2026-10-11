"""Manufactured wrapper routing only: no native process or ODE."""
from pathlib import Path
import importlib.util,sys,unittest
from unittest.mock import patch
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import compare_continuation_diagnostic as d

def fixture():
    fields=d.FIELDS+d.MOMENTS
    history=[dict(time_s=float(k),z=20.-k/10,**{name:1. for name in fields}) for k in range(129)]
    r=dict(history=history,checks={'accepted_gas_domain':True})
    m=dict(history=[dict(row) for row in history],geometry_preflight={})
    return r,{},m,{},dict(whole_interval=True),dict(energy=0.,number=0.)

class DiagnosticRoutingTests(unittest.TestCase):
    def run_fixture(self,a,b):
        with patch.object(d.original,'load_bound_run',return_value=a),patch.object(d,'load_continuation_run',return_value=b),patch.object(d,'pair_identities',return_value={'verified_operator':True}),patch.object(d,'sha',return_value='manufactured'):
            return d.diagnostic_compare(Path('coarse'),Path('fine'),{'fixture':True})
    def test_even_equal_fields_never_admit(self):
        x=self.run_fixture(fixture(),fixture())
        self.assertTrue(x['all_recorded_field_and_conservation_checks_pass'])
        self.assertFalse(x['scientific_admission']);self.assertFalse(x['time_convergence_inherited'])
        self.assertEqual(x['status'],'CONTINUED_TRAJECTORY_DIAGNOSTIC_NOT_ADMITTED')
        self.assertEqual(len(x['comparisons']['65']['fields']),24)
        self.assertEqual(len(x['comparisons']['129']['fields']),24)
    def test_each_epoch_set_keeps_own_amplitude(self):
        a,b=fixture(),fixture();key=d.MOMENTS[0]
        a[2]['history'][127][key]=2.;b[2]['history'][127][key]=3.
        x=self.run_fixture(a,b)
        self.assertTrue(x['comparisons']['65']['fields'][key]['pass_budget'])
        self.assertAlmostEqual(x['comparisons']['129']['fields'][key]['scaled_error'],1/3)
        self.assertFalse(x['all_recorded_field_and_conservation_checks_pass'])

if __name__=='__main__':unittest.main()
