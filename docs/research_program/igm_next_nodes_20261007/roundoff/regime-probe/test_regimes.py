#!/usr/bin/env python3
"""Independent exact-rational checks of saved reference neighborhoods and claims."""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json, math, struct, unittest
import probe_regimes as p
W=Path(__file__).resolve().parent
J=json.loads((W/'results.json').read_text())

def even(x):
    return struct.unpack('>Q',struct.pack('>d',x))[0]%2==0

class ProbeChecks(unittest.TestCase):
    def test_source_inputs_unchanged(self):
        for name,digest in J['inputs_sha256'].items():
            self.assertEqual(hashlib.sha256((W.parent/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256((W/'probe_regimes.py').read_bytes()).hexdigest(),J['script_sha256'])
    def test_all_saved_nearest_values_against_exact_neighbors(self):
        for label,e in J['examples'].items():
            x,P,R=e['x0'],e['P'],e['R']
            ref=(F(x)+F(P))/(1+F(P)+F(R))
            self.assertEqual(str(ref),e['exact_reference_fraction'])
            n=e['nearest'];error=abs(F(n)-ref)
            for v in [math.nextafter(n,-math.inf),math.nextafter(n,math.inf)]:
                verror=abs(F(v)-ref)
                self.assertLessEqual(error,verror,label)
                if error==verror:self.assertTrue(even(n),label)
    def test_saved_results_replay_exactly(self):
        for e in J['examples'].values():
            for name,fn in p.FUNCS.items():
                self.assertEqual(fn(e['x0'],e['P'],e['R']).hex(),e['methods'][name]['hex'])
    def test_stiff_delta_erases_normal_positive_root(self):
        self.assertEqual(p.delta(1.,0.,1e20),0.)
        self.assertEqual(p.pos(1.,0.,1e20),1e-20)
        self.assertEqual(p.guarded_decrement(1.,0.,1e20),1e-20)
    def test_stiff_delta_can_leave_domain(self):
        self.assertGreater(p.delta(.0002,1e308,0.),1.)
        self.assertLess(p.delta(.4545849162474018,4.854560956376076e29,5.357202049290628e246),0.)
    def test_overflow_scales_to_half(self):
        self.assertEqual(p.pos(1.,1e308,1e308),0.)
        self.assertTrue(math.isnan(p.delta(1.,1e308,1e308)))
        self.assertEqual(p.scaled_pos(1.,1e308,1e308),.5)
        self.assertEqual(p.compensated(1.,1e308,1e308),.5)
    def test_underflow_distinguishes_legitimate_and_false_zero(self):
        self.assertEqual(float(F(p.MIN)/2),0.)
        x,P,R=0.,p.MIN,math.nextafter(1.,0.)
        self.assertEqual(float((F(x)+F(P))/(1+F(P)+F(R))),p.MIN)
        self.assertEqual(p.compensated(x,P,R),0.)
    def test_compensated_counterexample_normal_inputs(self):
        x,P,R=math.nextafter(.5,0.),9007199254740994.,math.nextafter(1.,2.)
        ref=(F(x)+F(P))/(1+F(P)+F(R))
        self.assertNotEqual(p.compensated(x,P,R),float(ref))
    def test_captured_failures_keep_nearest(self):
        for label in ['captured_16','captured_34']:
            e=J['examples'][label]
            for name in ['delta_sum','guard_delta_half','guard_delta_half_decrement','compensated_positive']:
                self.assertEqual(e['methods'][name]['ulp_distance_to_nearest'],0,label)
    def test_compensated_all_34_captured(self):
        self.assertEqual(J['stats']['captured']['compensated_positive']['nearest'],34)
    def test_guard_and_scaled_domain_in_this_corpus(self):
        for group,ss in J['stats'].items():
            for name in ['guard_delta_half','guard_delta_half_decrement','positive_overflow_scaled','compensated_positive']:
                self.assertEqual(ss[name]['nonfinite'],0,(group,name))
                self.assertEqual(ss[name]['outside_unit_interval'],0,(group,name))
    def test_all_expected_cases(self):
        self.assertEqual(J['cases'],117363)
        self.assertEqual(sum(ss['positive_quotient']['count'] for ss in J['stats'].values()),J['cases'])
    def test_no_compensated_universal_dominance(self):
        self.assertGreater(J['compared_exact_absolute_error']['compensated_positive']['worse_than_positive'],0)
        self.assertGreater(J['compared_exact_absolute_error']['guard_delta_half']['worse_than_positive'],0)

if __name__=='__main__':unittest.main(verbosity=2)
