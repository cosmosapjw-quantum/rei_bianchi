import unittest
from fractions import Fraction as F
from interior_pilot.engine import (Interval as I, Rectangle as R, RangeClaim,
    Caps, Budget, DomainFailure, ResourceLimit, integrate_range)
from interior_pilot.toys import point,polynomial_range,constant_range,nested_range


class InteriorTests(unittest.TestCase):
    def test_exact_interval_and_complex_product(self):
        self.assertEqual(I(-2, 3)*I(-5, -1), I(-15, 10))
        self.assertEqual(R(I(1, 1), I(2, 2))*R(I(3, 3), I(4, 4)), R(I(-5, -5), I(10, 10)))

    def test_reject_float_and_reversed_interval(self):
        for values in ((0.0, 1), (2, 1), (False, 1)):
            with self.subTest(values=values), self.assertRaises((TypeError, ValueError)):
                I(*values)

    def test_inner_real_exact_one_third(self):
        res = integrate_range(polynomial_range, I(0, 1), point(1), caps=Caps(target_width=F(1, 64)))
        self.assertEqual(res.status, 'TARGET_WIDTH_MET')
        self.assertTrue(res.enclosure.real.contains(F(1, 3)))
        self.assertEqual(res.enclosure.imag, I(0, 0))
        self.assertLessEqual(res.enclosure.max_width, F(1, 64))

    def test_uniform_complex_parameter_box(self):
        z = R(I(1, 2), I(-1, 1))
        res = integrate_range(polynomial_range, I(0, 1), z, caps=Caps(target_width=F(3, 4)))
        self.assertEqual(res.status, 'TARGET_WIDTH_MET')
        exact = R(I(F(1, 3), F(2, 3)), I(F(-1, 3), F(1, 3)))
        self.assertTrue(res.enclosure.contains(exact))

    def test_nested_uniform_outer_one_sixth(self):
        budget = Budget(Caps(target_width=F(1, 16), max_evaluations=15000, max_panels=1024))
        res = integrate_range(lambda t,z:nested_range(t,z,budget), I(0, 1), point(0), budget=budget)
        self.assertEqual(res.status, 'TARGET_WIDTH_MET')
        self.assertTrue(res.enclosure.real.contains(F(1, 6)))
        self.assertLessEqual(res.enclosure.max_width, F(1, 16))
        self.assertGreater(res.metrics['evaluations'], res.metrics['peak_live_panels'])
        self.assertEqual(budget.live_panels, 0)
        self.assertEqual(budget.live_state_bytes, 0)

    def test_midpoint_only_inner_claim_rejected(self):
        def midpoint(t,z):
            return RangeClaim(point((z.real.lo+z.real.hi)/6), t, z, False, 'midpoint_only')
        res = integrate_range(midpoint, I(0, 1), R(I(0, 1), I(0, 0)))
        self.assertEqual(res.status, 'INVALID_RANGE_CONTRACT')
        self.assertIsNone(res.enclosure)

    def test_wrong_parameter_or_panel_claim_rejected(self):
        for wrong_t,wrong_z in ((I(0, 1),point(2)), (I(0, F(1, 2)),point(1))):
            res = integrate_range(lambda t,z:RangeClaim(point(1),wrong_t,wrong_z,True,'wrong'), I(0, 1), point(1))
            self.assertEqual(res.status, 'INVALID_RANGE_CONTRACT')

    def test_missing_proof_reference_rejected(self):
        res = integrate_range(lambda t,z:RangeClaim(point(1),t,z,True,''), I(0, 1), point(1))
        self.assertEqual(res.status, 'INVALID_RANGE_CONTRACT')

    def test_domain_failure(self):
        def invalid(t,z): raise DomainFailure('toy domain guard')
        res = integrate_range(invalid,I(0,1),point(1))
        self.assertEqual(res.status, 'CALLBACK_DOMAIN_FAILURE')
        self.assertIsNone(res.enclosure)

    def test_evaluation_cap(self):
        res = integrate_range(polynomial_range,I(0,1),point(1),caps=Caps(max_evaluations=1,target_width=F(1,1000)))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_EVALUATIONS')
        self.assertEqual(res.metrics['evaluations'],1)
        self.assertTrue(res.enclosure.real.contains(F(1,3)))

    def test_panel_cap(self):
        res = integrate_range(polynomial_range,I(0,1),point(1),caps=Caps(max_panels=2,target_width=F(1,1000)))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_LIVE_PANELS')

    def test_cooperative_wall_guard_after_callback(self):
        time=[0.0]
        budget=Budget(Caps(max_wall_seconds=1),clock=lambda:time[0])
        def slow(t,z):
            time[0]=2.0
            return constant_range(t,z)
        res=integrate_range(slow,I(0,1),point(1),budget=budget)
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_WALL_SECONDS')
        self.assertIsNone(res.enclosure)
        self.assertEqual(res.metrics['wall_seconds'],2.0)

    def test_state_memory_estimate_cap(self):
        res=integrate_range(polynomial_range,I(0,1),point(1),caps=Caps(max_memory_bytes=10))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_TRACKED_STATE_BYTES')

    def test_hard_process_memory_not_claimed(self):
        with self.assertRaises(ValueError): Caps(require_hard_memory_limit=True)

    def test_rational_precision_cap(self):
        def giant(t,z): return RangeClaim(point(F(1,1<<100)),t,z,True,'exact_tiny_constant')
        res=integrate_range(giant,I(0,1),point(1),caps=Caps(max_rational_bits=64))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_RATIONAL_BITS')

    def test_valid_wide_parameter_image_is_not_failure(self):
        res=integrate_range(constant_range,I(0,1),R(I(0,1),I(0,0)),caps=Caps(target_width=F(1,10)))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_WIDTH')
        self.assertEqual(res.enclosure,R(I(0,1),I(0,0)))

    def test_zero_length_integral_and_negative_interval(self):
        zero=integrate_range(constant_range,I(2,2),point(3))
        negative=integrate_range(constant_range,I(-2,-1),point(3))
        self.assertEqual(zero.enclosure,point(0))
        self.assertEqual(zero.metrics['evaluations'],0)
        self.assertEqual(negative.enclosure,point(3))

    def test_callback_exception_classification_and_budget_release(self):
        budget=Budget(Caps())
        def bad(t,z): raise RuntimeError('synthetic bug')
        res=integrate_range(bad,I(0,1),point(1),budget=budget)
        self.assertEqual(res.status,'CALLBACK_IMPLEMENTATION_FAILURE')
        self.assertEqual(budget.live_panels,0)
        self.assertEqual(budget.live_state_bytes,0)

    def test_shared_nested_evaluation_cap_counts_all_callbacks(self):
        budget=Budget(Caps(max_evaluations=10,target_width=F(1,1000)))
        res=integrate_range(lambda t,z:nested_range(t,z,budget),I(0,1),point(0),budget=budget)
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_EVALUATIONS')
        self.assertEqual(res.metrics['evaluations'],10)
        self.assertEqual(budget.live_panels,0)
        self.assertEqual(budget.live_state_bytes,0)

    def test_depth_cap_preserves_last_complete_enclosure(self):
        res=integrate_range(polynomial_range,I(0,1),point(1),caps=Caps(max_depth=1,target_width=F(1,1000)))
        self.assertEqual(res.status,'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(res.reason,'MAX_SUBDIVISION_DEPTH')
        self.assertTrue(res.enclosure.real.contains(F(1,3)))

    def test_wrong_callback_return_type(self):
        res=integrate_range(lambda t,z:None,I(0,1),point(1))
        self.assertEqual(res.status,'INVALID_RANGE_CONTRACT')
        self.assertIsNone(res.enclosure)


if __name__=='__main__': unittest.main()
