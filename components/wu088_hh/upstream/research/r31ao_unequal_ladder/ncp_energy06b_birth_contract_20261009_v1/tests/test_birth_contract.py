"""Focused tests for the pinned source and a synthetic scalar BE submodel."""
import json
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from birth_contract import (
    ContractRefused, read_birth_contract,
    toy_full, toy_halves, toy_delta_closed,
    toy_full_tangent, toy_halves_tangent, toy_halves_tangent_closed,
    audit_ncp_science_gates,
)

ROOT = Path(__file__).resolve().parents[1]


class SourceBoundTest(unittest.TestCase):
    def test_full_and_half_schedule_are_distinct_but_same_total(self):
        c=read_birth_contract(ROOT/'inputs')
        self.assertEqual(c.start, Q(160000000000))
        self.assertEqual(c.middle, Q(160625000000))
        self.assertEqual(c.end, Q(161250000000))
        self.assertEqual(len(c.full), 1)
        self.assertEqual(len(c.halves), 2)
        self.assertNotEqual(c.full, c.halves)
        self.assertEqual(sum(w for _,w in c.full),sum(w for _,w in c.halves))
        self.assertEqual(c.full[0][1],c.amount)
        self.assertEqual(c.effective_source * (c.end-c.start), c.amount)
        self.assertEqual(c.original_rate_binary64,Q.from_float(5e-15))

    def test_source_bound_reported_birth_moment_is_exact(self):
        c=read_birth_contract(ROOT/'inputs')
        delta=sum(t*w for t,w in c.halves)-sum(t*w for t,w in c.full)
        self.assertEqual(delta, -c.amount*(c.end-c.start)/4)
        self.assertEqual(delta, Q(-72057594037927939453125,36893488147419103232))

    def test_mutated_original_rust_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)
            for name in ['NCP_ENERGY06_SOURCE_MEASURE.json', 'PINNED_paired_runtime.rs', 'PINNED_hh_paired_extension.rs']:
                shutil.copy2(ROOT/'inputs'/name, out/name)
            f=out/'PINNED_paired_runtime.rs';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ContractRefused, 'SOURCE_IDENTITY'):
                read_birth_contract(out)

    def test_forged_moment_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            for name in ['NCP_ENERGY06_SOURCE_MEASURE.json','PINNED_paired_runtime.rs','PINNED_hh_paired_extension.rs']:
                shutil.copy2(ROOT/'inputs'/name, out/name)
            f=out/'NCP_ENERGY06_SOURCE_MEASURE.json'
            data=json.loads(f.read_text()); data['first_time_moment_half_minus_full_exact']='0'
            f.write_text(json.dumps(data))
            with self.assertRaisesRegex(ContractRefused,'RECORDED_MOMENT_MISMATCH'):
                read_birth_contract(out)

    def test_claim_is_not_upgraded(self):
        a=audit_ncp_science_gates(ROOT/'inputs')
        self.assertFalse(a['executable_science_scope'])
        self.assertEqual(a['coverage_accepted'],24)
        self.assertEqual(a['missing_unbounded'],265)
        self.assertTrue(a['authorization_missing'])
        self.assertFalse(a['owner_full_paired_admitted'])


class ScalarBEComparison(unittest.TestCase):
    def test_exact_closed_form_paired_difference(self):
        for x in [Q(0),Q(1,1000),Q(1,4),Q(1),Q(4)]:
            for p in [Q(0),Q(2,5),Q(5)]:
                w=Q(1,20)
                self.assertEqual(toy_halves(p,w,x)-toy_full(p,w,x),toy_delta_closed(p,w,x))

    def test_no_absorption_has_exact_zero_paired_defect(self):
        self.assertEqual(toy_delta_closed(Q(3,5),Q(1,20),Q(0)),0)

    def test_source_dominated_case_has_positive_defect(self):
        self.assertGreater(toy_delta_closed(Q(0),Q(1,20),Q(1,4)),0)

    def test_zero_birth_has_nonzero_paired_defect_from_propagation(self):
        # Opposite counterexample: equal zero birth measures, different BE propagators.
        self.assertLess(toy_delta_closed(Q(1,5),Q(0),Q(1,4)),0)

    def test_equilibrium_has_zero_defect_with_unequal_birth_times(self):
        x=Q(1,4);w=Q(1,20);p=w/x
        self.assertEqual(toy_full(p,w,x),p)
        self.assertEqual(toy_halves(p,w,x),p)
        self.assertEqual(toy_delta_closed(p,w,x),0)

    def test_inherited_stock_can_reverse_defect_sign(self):
        x=Q(1,4);w=Q(1,20);p=3*w/x
        self.assertLess(toy_delta_closed(p,w,x),0)

    def test_full_tangent_matches_rational_difference_quotient(self):
        p,dp,w,dw,x,dx=[Q(1,7),Q(1,13),Q(2,17),Q(1,19),Q(1,4),Q(1,9)]
        val,dv=toy_full_tangent(p,dp,w,dw,x,dx)
        self.assertEqual(val,toy_full(p,w,x))
        # Independent analytic quotient rule
        d=((dp+dw)*(1+x)-(p+w)*dx)/(1+x)**2
        self.assertEqual(dv,d)

    def test_halves_tangent_matches_independent_closed_derivative(self):
        for x in [Q(0),Q(1,1000),Q(1,4),Q(4)]:
            p,dp,w,dw,dx=Q(1,7),Q(1,13),Q(2,17),Q(1,19),Q(1,9)
            self.assertEqual(toy_halves_tangent(p,dp,w,dw,x,dx),
                             toy_halves_tangent_closed(p,dp,w,dw,x,dx))

    def test_incoming_tangent_is_not_zeroed_at_second_half(self):
        p,dp,w,dw,x,dx=Q(1,7),Q(1,13),Q(2,17),Q(1,19),Q(1,4),Q(1,9)
        correct=toy_halves_tangent(p,dp,w,dw,x,dx)[1]
        incorrect=toy_halves_tangent(p,Q(0),w,dw,x,dx)[1]
        self.assertNotEqual(correct,incorrect)
        self.assertEqual(correct-incorrect,dp/(1+x/2)**2)

    def test_invalid_negative_inputs_refused(self):
        for inp in [(Q(-1),Q(1),Q(1,3)), (Q(1),Q(-1),Q(1,3)), (Q(1),Q(1),Q(-1,3))]:
            with self.assertRaisesRegex(ContractRefused,'TOY_DOMAIN'):
                toy_delta_closed(*inp)


if __name__=='__main__': unittest.main()
