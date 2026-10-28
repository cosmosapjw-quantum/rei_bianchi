"""C5 authored controls. NOT EXECUTED at publication; fixtures are not source data."""
import unittest
from fractions import Fraction as F
import finite_thermal as ft


class FiniteThermalTests(unittest.TestCase):
    def point(self, **changes):
        args = dict(Na="2", Ta="3", cv="5", dN="1", Q="7", W="-2")
        args.update(changes)
        return ft.finite_endpoint(**args)

    def test_zero_event_and_representation_volume(self):
        p = self.point(dN="0", Q="0", W="0")
        self.assertEqual(p.T, F(3))
        self.assertEqual(p.temperature_ratio, F(1))
        self.assertEqual((p.log_energy_argument, p.log_count_argument), (F(1), F(1)))
        proper = ft.proper_coordinates(U=p.U, N=p.N, R="8")
        self.assertEqual((proper.energy, proper.particles), (F(15, 4), F(1, 4)))
        self.assertEqual(proper.energy / (p.cv * proper.particles), p.T)

    def test_positive_heat_can_lower_temperature(self):
        p = ft.finite_endpoint(Na="1", Ta="4", cv="3/2", dN="1", Q="3", W="0")
        self.assertEqual(p.T, F(3))
        self.assertEqual(p.temperature_ratio, F(3, 4))

    def test_negative_heat_can_raise_temperature(self):
        p = ft.finite_endpoint(Na="2", Ta="4", cv="3/2", dN="-1", Q="-3/2", W="0")
        self.assertEqual(p.T, F(7))
        self.assertEqual(p.temperature_ratio, F(7, 4))

    def test_geometry_work_applied_once(self):
        p = ft.finite_endpoint(Na="2", Ta="8", cv="3/2", dN="0", Q="0", W="-18")
        self.assertEqual((p.U, p.T), (F(6), F(2)))
        proper = ft.proper_coordinates(U=p.U, N=p.N, R="8")
        self.assertEqual(proper.energy / (p.cv * proper.particles), F(2))

    def test_initial_and_balance_residuals_not_double_counted(self):
        p = self.point()
        s = ft.saved_endpoint_diagnostics(p, Ua="31", Ub="38", Nb="4")
        self.assertEqual((s.r0, s.r_balance, s.rE, s.rN), (F(1), F(2), F(3), F(1)))
        self.assertEqual(s.T, F(19, 10))
        self.assertEqual(s.temperature_difference, F(-13, 30))
        self.assertEqual(s.identity_difference, s.temperature_difference)
        self.assertEqual(s.r0 + s.r_balance, s.rE)
        # A saved initial mismatch is diagnosed, not replaced by the caloric value.
        alternate = ft.saved_endpoint_diagnostics(p, Ua="-1", Ub="38", Nb="4")
        self.assertEqual((alternate.r0, alternate.r_balance, alternate.rE), (F(-31), F(34), F(3)))

    def test_mixed_direction_caloric_and_log_identity(self):
        p = self.point()
        d = ft.endpoint_jvp(p, dNa="1/3", dTa="-2/5", dcv="1/7", ddN="4/9", dQ="-3", dW="2/11")
        self.assertEqual(d.dN, F(7, 9))
        self.assertEqual(d.dU, F(5) - F(4) + F(6, 7) - F(3) + F(2, 11))
        self.assertEqual(p.cv * p.N * d.dT + p.N * p.T / 7 + p.cv * p.T * F(7, 9), d.dU)
        self.assertEqual(d.dlogT, d.dT / p.T)

    def test_proper_and_baryon_normalization_tangents(self):
        p = self.point()
        c = ft.normalized_coordinates(U=p.U, N=p.N, R="2", b="7")
        d = ft.normalized_coordinates_jvp(U=p.U, N=p.N, R="2", b="7", dU="3", dN="-1", dR="1/5", db="2/3")
        self.assertEqual(d.energy / c.energy - d.particles / c.particles, F(3) / p.U + F(1) / p.N)
        self.assertNotEqual(d.energy, F(3, 14))
        a = ft.proper_coordinates(U=p.U, N=p.N, R="2")
        da = ft.proper_coordinates_jvp(U=p.U, N=p.N, R="2", dU="3", dN="-1", dR="1/5")
        self.assertEqual(da.energy / a.energy - da.particles / a.particles, F(3) / p.U + F(1) / p.N)

    def bath(self):
        return ft.source_bath_counts(initial_stocks=(F(2), F(1), F(1), F(3)), final_stocks=(F(1), F(1), F(1), F(4)), events=(F(-1), F(0), F(0), F(2)), electrons_initial="3", electrons_final="9/2", NH="7", fHe="1/10")

    def test_saved_stock_and_separate_electron_defects(self):
        c = self.bath()
        self.assertEqual(c.stock_residuals, (F(0), F(0), F(0), F(-1)))
        self.assertEqual(c.electron_residual, F(-1, 2))
        self.assertEqual((c.dN, c.rN), (F(3), F(-3, 2)))
        self.assertEqual(c.Nb - c.Na - c.dN, sum(c.stock_residuals) + c.electron_residual)
        self.assertEqual(ft.selected_h_thermal_count((F(2), F(1), F(1), F(3)), "3"), F(10))

    def test_inert_helium_changes_count_and_parameter_tangent(self):
        c = self.bath()
        self.assertEqual((c.inert_He, c.Na, c.Nb), (F(7, 10), F(107, 10), F(61, 5)))
        direction = ft.source_bath_counts_jvp(NH="7", fHe="1/10", dNH="2", dfHe="3/20", d_initial_stocks=(F(0),) * 4, d_final_stocks=(F(0),) * 4, d_events=(F(0),) * 4, d_electrons_initial="0", d_electrons_final="0")
        self.assertEqual((direction.dB, direction.dNa, direction.dNb, direction.ddN), (F(5, 4), F(5, 4), F(5, 4), F(0)))

    def test_unweighted_composition_and_associativity(self):
        a = ft.Segment(F(8), F(1), F(2), F(-3))
        b = ft.Segment(F(2), F(4), F(5), F(-6))
        c = ft.Segment(F(3), F(-1), F(2), F(7))
        ab = ft.compose_local_segments(a, b)
        self.assertEqual(ab, ft.Segment(F(16), F(33), F(42), F(-51)))
        self.assertEqual(ft.compose_local_segments(ab, c), ft.compose_local_segments(a, ft.compose_local_segments(b, c)))

    def test_composition_tangent_product_term(self):
        a = ft.Segment(F(8), F(1), F(2), F(-3))
        b = ft.Segment(F(2), F(4), F(5), F(-6))
        da = ft.SegmentDirection(F(1, 2), F(1), F(0), F(-1))
        db = ft.SegmentDirection(F(-1, 3), F(2), F(3), F(4))
        d = ft.compose_local_segments_jvp(a, b, da, db)
        self.assertEqual(d, ft.SegmentDirection(F(-5, 3), F(19), F(53, 2), F(28)))

    def test_positive_cartesian_interval_and_defect_bound(self):
        p = self.point()
        interval = ft.temperature_interval(Ulo="33", Uhi="37", Nlo="11/4", Nhi="13/4", cv="5")
        self.assertEqual((interval.lower, interval.upper), (F(132, 65), F(148, 55)))
        self.assertEqual(interval.scope, "CARTESIAN_ENCLOSURE_NOT_PHYSICAL_CERTIFICATE")
        bound = ft.temperature_error_bound(p, eE="2", eN="1/4")
        self.assertEqual(bound, F(59, 165))
        s = ft.saved_endpoint_diagnostics(p, Ua="30", Ub="37", Nb="11/4")
        self.assertEqual(abs(s.temperature_difference), bound)
        self.assertEqual(ft.endpoint_interval(p, eE="2", eN="1/4"), interval)

    def test_unknown_radii_are_not_zero(self):
        p = self.point()
        self.assertIsNone(ft.temperature_error_bound(p, eE=None, eN="0"))
        self.assertIsNone(ft.endpoint_interval(p, eE="0", eN=None))
        with self.assertRaises(ValueError):
            ft.temperature_error_bound(p, eE="-1", eN=None)

    def test_domain_and_exact_input_rejection(self):
        for changes in (dict(Na="0"), dict(Ta="0"), dict(cv="-1"), dict(dN="-2"), dict(Q="-100")):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.point(**changes)
        for bad in (1, True, 0.1, float("nan")):
            with self.subTest(value=repr(bad)), self.assertRaises(TypeError):
                ft.exact(bad)
        for bad in (" 1", "1_0", "NaN", "1/0"):
            with self.subTest(value=bad), self.assertRaises((ValueError, ZeroDivisionError)):
                ft.exact(bad)
        with self.assertRaises(ValueError):
            ft.proper_coordinates(U="1", N="1", R="0")
        with self.assertRaises(ValueError):
            ft.normalized_coordinates(U="1", N="1", R="1", b="0")
        with self.assertRaises(ValueError):
            ft.temperature_error_bound(self.point(), eE="0", eN="3")
        with self.assertRaises(ValueError):
            ft.temperature_interval(Ulo="0", Uhi="1", Nlo="1", Nhi="2", cv="1")

    def test_typed_source_decimal_binary64_hex_are_distinct(self):
        binary = ft.decode_source_literal("0.1", "JSON_NUMBER_VIA_BINARY64")
        decimal = ft.decode_source_literal("0.1", "SAVED_MP_DECIMAL_STRING")
        hexa = ft.decode_source_literal("0x1.999999999999ap-4", "BINARY64_HEX_STRING")
        self.assertEqual(binary, F(3602879701896397, 36028797018963968))
        self.assertEqual(decimal, F(1, 10))
        self.assertEqual(hexa, binary)
        self.assertNotEqual(binary, decimal)
        for text, kind in (("true", "JSON_NUMBER_VIA_BINARY64"), ("1e9999", "JSON_NUMBER_VIA_BINARY64"), ("NaN", "SAVED_MP_DECIMAL_STRING"), ("0.1", "UNKNOWN")):
            with self.subTest(text=text, kind=kind), self.assertRaises((TypeError, ValueError)):
                ft.decode_source_literal(text, kind)

    def test_frozen_source_checks_reject_wrong_bytes(self):
        with self.assertRaises(ValueError):
            ft.load_literal_binding(b"{}")
        with self.assertRaises(ValueError):
            ft.consume_saved_source(b"{}", b"{}")

    def test_gas_port_ownership_and_null_physical_outputs(self):
        event = (F(100), F(200), F(7), F(300), F(400))
        work = (F(1), F(2), F(-2), F(4), F(5))
        self.assertEqual(ft.gas_ports(event, work, sector_order=ft.ENERGY_ORDER), (F(7), F(-2)))
        bad_order = tuple(reversed(ft.ENERGY_ORDER))
        with self.assertRaises(ValueError):
            ft.gas_ports(event, work, sector_order=bad_order)
        physical = ft.physical_output_boundary()
        self.assertIsNone(physical["actual_temperature_update"])
        self.assertIsNone(physical["actual_native25"])
        self.assertIsNone(physical["physical_radii"])
        self.assertFalse(physical["full_state_update"])
        self.assertFalse(physical["L4_ready"])

    def test_source_energy_bridge_and_exact_serialization(self):
        bridge = ft.source_temperature_bridge(theta_eV="2", EV_J="3", kBoltz_source="1", native_T_K="4")
        self.assertEqual(bridge.energy_temperature_K * ft.K_B_SI, F(6))
        self.assertEqual(bridge.energy_temperature_K - bridge.native_temperature_K, bridge.energy_minus_native_K)
        self.assertEqual(bridge.theta_minus_kBoltz_native_eV, F(-2))
        self.assertEqual(ft.to_wire(F(-13, 30)), {"num": "-13", "den": "30"})
        self.assertIsNone(ft.to_wire(None))


class AuthorizationTests(unittest.TestCase):
    """Pure validation controls; no subprocess, import check or actual-source run."""
    def candidate(self):
        import run_once as r
        hashes = {name: "fixture-hash-not-source-identity" for name in r.FILES}
        command = ["fixture-command-not-executable"]
        auth = dict(schema="REI_FINITE_THERMAL_RUN_AUTH_V1", unit=r.UNIT,
                    approved=True, authority_ref="SYNTHETIC_TEST_NOT_AUTHORIZATION",
                    attempt_id="fixture", accounting_boundary="fixture-only",
                    unknown_costs="UNKNOWN_NOT_ZERO", mode="tests", attempts=1,
                    source_sha256=hashes, worker_command=command,
                    prior_known_planning_cpu_s="15.929490885",
                    approved_absolute_planning_cap_cpu_s="20",
                    limits=dict(attempt_cpu_s="3", worker_cpu_s="2",
                                final_record_reserve_cpu_s="0.25", wall_s="20", memory_bytes=268435456))
        return r, auth, hashes, command

    def test_unapproved_execution_is_rejected(self):
        r, auth, hashes, command = self.candidate()
        auth["approved"] = False
        with self.assertRaises(ValueError):
            r.validate_authorization(auth, mode="tests", source_hashes=hashes, worker_command=command)

    def test_mode_and_source_identity_are_not_interchangeable(self):
        r, auth, hashes, command = self.candidate()
        with self.assertRaises(ValueError):
            r.validate_authorization(auth, mode="source", source_hashes=hashes, worker_command=command)
        with self.assertRaises(ValueError):
            r.validate_authorization(auth, mode="tests", source_hashes={}, worker_command=command)

    def test_historical_debit_and_supervisor_allowance_are_preserved(self):
        r, auth, hashes, command = self.candidate()
        auth["prior_known_planning_cpu_s"] = "1"
        with self.assertRaises(ValueError):
            r.validate_authorization(auth, mode="tests", source_hashes=hashes, worker_command=command)
        auth["prior_known_planning_cpu_s"] = "15.929490885"
        auth["limits"]["final_record_reserve_cpu_s"] = "1"
        with self.assertRaises(ValueError):
            r.validate_authorization(auth, mode="tests", source_hashes=hashes, worker_command=command)


class OutcomeClassificationTests(unittest.TestCase):
    """Authored pure controls only: no child execution or signal delivery."""
    def classify(self, **changes):
        import run_once as r
        args = dict(exit_code=0, terminal_usage_observed=True,
                    supervisor_error_kind=None, limit_overrun=False)
        args.update(changes)
        return r.classify_outcome(**args)

    def test_supervisor_error_is_not_an_invented_budget_overrun(self):
        # Static witness: fork raises OSError; no child usage can be observed.
        self.assertEqual(self.classify(exit_code=None, terminal_usage_observed=False,
                                       supervisor_error_kind="execution"),
                         ("EXECUTION_FAILED", "runtime_environment/execution_error"))

    def test_explicit_resource_stop_and_observed_overrun_remain_resource(self):
        self.assertEqual(self.classify(exit_code=None, terminal_usage_observed=False,
                                       supervisor_error_kind="resource"),
                         ("RESOURCE_STOP_OR_OVERRUN", "runtime_environment/resource_budget"))
        self.assertEqual(self.classify(limit_overrun=True),
                         ("RESOURCE_STOP_OR_OVERRUN", "runtime_environment/resource_budget"))

    def test_operator_interrupt_remains_separate(self):
        self.assertEqual(self.classify(exit_code=None, terminal_usage_observed=False,
                                       supervisor_error_kind="interrupted"),
                         ("INTERRUPTED", "execution/operator_interruption"))

    def test_worker_timer_signals_do_not_become_ordinary_nonzero_exit(self):
        import signal
        for sig in (signal.SIGALRM, signal.SIGPROF, signal.SIGXCPU):
            with self.subTest(signal=sig):
                self.assertEqual(self.classify(exit_code=-sig),
                                 ("WORKER_RESOURCE_SIGNAL", "runtime_environment/resource_signal_cause_unconfirmed"))

    def test_sigkill_and_missing_measurement_do_not_prove_budget_exhaustion(self):
        import signal
        self.assertEqual(self.classify(exit_code=-signal.SIGKILL),
                         ("EXECUTION_FAILED", "runtime_environment/signal_cause_unconfirmed"))
        for code in (None, 0):
            with self.subTest(exit_code=code):
                self.assertEqual(self.classify(exit_code=code, terminal_usage_observed=False),
                                 ("INCOMPLETE_OBSERVATION", "runtime_environment/incomplete_observation"))

    def test_zero_and_nonzero_exit_do_not_adjudicate_physics(self):
        self.assertEqual(self.classify(), ("EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION", None))
        for code in (1, 125):
            with self.subTest(exit_code=code):
                self.assertEqual(self.classify(exit_code=code),
                                 ("EXECUTION_FAILED", "execution/nonzero_exit_unadjudicated"))


if __name__ == "__main__":
    unittest.main()
