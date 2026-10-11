"""Changed controller native-observation and restart bindings only."""
from pathlib import Path
import copy
import json
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_controller import validate_controls,native_observables,run_bounded


class BindingTests(unittest.TestCase):
    def test_frozen_controls_bind_full_distributions_without_trace_floor(self):
        controls=json.loads((Path(__file__).parent/'CONTROL_V1.json').read_text())
        validate_controls(controls)
        class Provider:
            def geometry(self,t):return {'nH':.001,'nHe':.00008,'a_rel':1.}
        state={'t_s':0.,'gas':np.array([.0002,0.,0.,.1]),'N':np.array([[0.,1e-8]]),
               'U_eV':np.array([[0.,2e-7]]),'diagnostics':{'gamma':[1e-17,1e-18,0.]}}
        before=copy.deepcopy(state)
        fields=native_observables(state,Provider())
        self.assertEqual(set(fields),set(controls['observable_scales'])|set(controls['distribution_scales']))
        self.assertEqual(fields['xHeIII'],0.);self.assertEqual(fields['GammaHeII_s'],0.)
        self.assertEqual(fields['N_ref_distribution'][0,0],0.)
        np.testing.assert_array_equal(state['gas'],before['gas'])
        self.assertEqual(controls['observable_scales']['xHeIII'],1.)

    def test_restart_cursor_refuses_inconsistent_accepted_prefix(self):
        c=json.loads((Path(__file__).parent/'CONTROL_V1.json').read_text())
        s={'t_s':1.}
        cursor={'schema':'rei.q1b.c11.adaptive_cursor.v1','next_step_s':c['initial_step_s'],
            'attempts':3,'accepted_macros':1,'rejected_macros':2,'accepted_boundaries':1,
            'accepted_clock_s':1.}
        with self.assertRaisesRegex(ValueError,'COUNT_IDENTITY'):
            run_bounded(s,1.,None,None,lambda s:None,c,cursor=cursor)

if __name__=='__main__':unittest.main()
