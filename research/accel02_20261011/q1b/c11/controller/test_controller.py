"""C11 new controller behavior only; no native runs or completed-check replay."""
import copy
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_controller import (controlled_trial,next_boundary,validate_controls,run_bounded)


def control():
    return dict(schema='rei.q1b.c11.adaptive_controls.v1',method_order=1,local_defect_target=2e-4,
        observable_scales={'population':1.0,'trace':1.0},distribution_scales={},
        safety=0.8,min_shrink=0.2,max_growth=2.0,min_step_s=1e-12,max_step_s=1.,
        initial_step_s=.5,max_attempts=64,max_accepted_macros=32,
        physical_state_floor=False,scientific_normalization_changed=False)


def step(state,t):
    h=t-state['t_s'];s=copy.deepcopy(state);s['t_s']=t;s['population']=state['population']/(1+h)
    s['trace']=state['trace']+1e-20*h
    return s


def observe(s):return {'population':s['population'],'trace':s['trace']}

def validate(s):
    if not (math.isfinite(s['population']) and s['population']>=0 and s['trace']>=0):
        raise ArithmeticError('TOY_STRICT_DOMAIN')


class ControllerTests(unittest.TestCase):
    def test_zero_trace_scale_and_rejection_do_not_modify_state(self):
        s={'t_s':0.,'population':1.,'trace':0.};before=copy.deepcopy(s)
        trial=controlled_trial(s,.5,step,observe,validate,control())
        self.assertFalse(trial['accepted']);self.assertEqual(s,before)
        self.assertGreater(trial['next_step_s'],0)
        self.assertLess(trial['next_step_s'],.5)
        self.assertEqual(trial['defect']['normalized_by_scale']['trace'],0.)
        self.assertEqual(trial['fine_states'][0]['trace'],2.5e-21)

    def test_hard_event_and_final_not_crossed_no_nextafter(self):
        self.assertEqual(next_boundary(0.,.7,1.,(.25,.5)),(.25,'HARD_EVENT'))
        self.assertEqual(next_boundary(.25,.7,1.,(.25,.5)),(.5,'HARD_EVENT'))
        self.assertEqual(next_boundary(.5,1.,1.,(.25,.5)),(1.,'FINAL'))
        with self.assertRaises(ValueError):next_boundary(0.,1.,1.,(float('nan'),))

    def test_native_failure_failclosed_and_never_checkpointed(self):
        called=[]
        def broken(s,t):raise ArithmeticError('SOURCE_PRECISION_GATE')
        with self.assertRaisesRegex(ArithmeticError,'SOURCE_PRECISION_GATE'):
            run_bounded({'t_s':0.,'population':1.,'trace':0.},.1,broken,observe,validate,
                        control(),on_accept=lambda *a:called.append(a))
        self.assertEqual(called,[])

    def test_rejected_trial_not_committed_and_pair_checkpointed(self):
        rows=[];c=control();c['local_defect_target']=1e-3
        result=run_bounded({'t_s':0.,'population':1.,'trace':0.},.2,step,observe,validate,c,
                           hard_events=(.1,),on_accept=lambda pair,row,cursor:rows.append((pair,row,cursor)))
        self.assertEqual(result['status'],'REACHED_REQUESTED_BOUNDARY')
        self.assertTrue(any(not x['accepted'] for x in result['attempts']))
        self.assertGreater(len(rows),0)
        self.assertEqual(result['state']['t_s'],.2)
        self.assertTrue(any(pair[-1]['t_s']==.1 for pair,_,_ in rows))
        self.assertEqual(len(rows),result['cursor']['accepted_macros'])
        for pair,row,cursor in rows:
            self.assertEqual(len(pair),2);self.assertTrue(row['accepted'])
            self.assertEqual(cursor['accepted_clock_s'],pair[-1]['t_s'])
        self.assertLess(abs(result['state']['population']-math.exp(-.2)),.004)

    def test_finite_budget_exits_with_last_accepted_state(self):
        c=control();c['max_attempts']=1;c['initial_step_s']=.5
        result=run_bounded({'t_s':0.,'population':1.,'trace':0.},1.,step,observe,validate,c)
        self.assertEqual(result['status'],'BUDGET_BOUNDARY')
        self.assertEqual(result['state']['t_s'],0.)
        self.assertEqual(result['cursor']['rejected_macros'],1)
        self.assertFalse(result['scientific_admission'])

    def test_nonfinite_fields_and_scale_override_refused(self):
        c=control();c['observable_scales']['trace']=0
        with self.assertRaises(ValueError):validate_controls(c)
        c=control()
        def bad(s):return {'population':float('nan'),'trace':0.}
        with self.assertRaisesRegex(ValueError,'OBSERVABLE_DOMAIN'):
            controlled_trial({'t_s':0.,'population':1.,'trace':0.},.1,step,bad,validate,c)

if __name__=='__main__':unittest.main()
