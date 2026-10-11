"""New cumulative-resume-budget bug reproduction; no old controller replay."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_controller_v2 import run_bounded


def controls():
    return dict(schema='rei.q1b.c11.adaptive_controls.v1',method_order=1,local_defect_target=1e-9,
        observable_scales={'population':1.},distribution_scales={},safety=.8,min_shrink=.2,
        max_growth=2.,min_step_s=1e-14,max_step_s=1.,initial_step_s=.5,max_attempts=2,
        max_accepted_macros=2,physical_state_floor=False,scientific_normalization_changed=False)


def cursor(attempts=1,accepted=0,rejected=1,t=0.):
    return dict(schema='rei.q1b.c11.adaptive_cursor.v1',next_step_s=.5,attempts=attempts,
                accepted_macros=accepted,rejected_macros=rejected,accepted_boundaries=2*accepted,
                accepted_clock_s=t)


def step(s,t):return {'t_s':t,'population':s['population']/(1+t-s['t_s'])}

def observe(s):return {'population':s['population']}

def validate(s):
    if s['population']<0:raise ArithmeticError('DOMAIN')


class CumulativeBudgetTests(unittest.TestCase):
    def test_resumed_rejection_spends_only_remaining_total_attempt(self):
        c=controls();before=copy.deepcopy(c)
        result=run_bounded({'t_s':0.,'population':1.},1.,step,observe,validate,c,cursor=cursor())
        self.assertEqual(result['status'],'BUDGET_BOUNDARY')
        self.assertEqual(len(result['attempts']),1)
        self.assertEqual(result['cursor']['attempts'],2)
        self.assertEqual(result['cursor']['rejected_macros'],2)
        self.assertEqual(c,before)

    def test_exhausted_cursor_executes_no_map_and_preserves_state(self):
        calls=[];s={'t_s':0.,'population':1.}
        def forbidden(*args):calls.append(args);raise AssertionError('MAP_MUST_NOT_EXECUTE')
        result=run_bounded(s,1.,forbidden,observe,validate,controls(),cursor=cursor(2,0,2))
        self.assertEqual(result['status'],'BUDGET_BOUNDARY');self.assertEqual(calls,[])
        self.assertEqual(result['state'],s);self.assertEqual(result['attempts'],[])

    def test_resumed_accepted_macro_limit_is_cumulative(self):
        c=controls();c['max_attempts']=10;c['max_accepted_macros']=2
        calls=[]
        def exact(s,t):calls.append(t);return {'t_s':t,'population':1.}
        result=run_bounded({'t_s':.1,'population':1.},2.,exact,observe,validate,c,
                           cursor=cursor(1,1,0,.1))
        self.assertEqual(result['status'],'BUDGET_BOUNDARY')
        self.assertEqual(result['cursor']['accepted_macros'],2)
        self.assertEqual(result['cursor']['accepted_boundaries'],4)
        self.assertEqual(len(calls),3)

    def test_overbudget_cursor_rejected_without_erasing_evidence(self):
        with self.assertRaisesRegex(ValueError,'CUMULATIVE_BUDGET'):
            run_bounded({'t_s':0.,'population':1.},1.,step,observe,validate,controls(),cursor=cursor(3,0,3))

if __name__=='__main__':unittest.main()
