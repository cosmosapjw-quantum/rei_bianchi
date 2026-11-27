"""Synthetic exact arithmetic only; never calls evaluate_pinned/HH/Frozen107."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).with_name('select_cutoff.py')
spec = importlib.util.spec_from_file_location('select_cutoff_under_test', PATH)
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)


def test_upward_rounding_exact_grid_and_error():
    for q in [Q(0), Q(1, 3), Q(7, 9), Q(1, 1 << 400), Q(1 << 600), Q(123456789, 134567891)]:
        value = s.up(q)
        assert value >= q
        assert value == q or value < q * (1 + Q(1, 1 << 127))
        assert s.up(value) == value


def test_positive_decomposition_matches_unrounded_direct_expression():
    row = dict(c_abs=Q(3), C_F=Q(2), L_t=Q(5), W_t=Q(7), L_u=Q(11), W_u=Q(13),
               U_t={2: Q(17), 3: Q(19)}, U_u={2: Q(23), 4: Q(29)})
    lower, coefficients, evidence = s.aggregate([row])
    assert lower == 6 * (5 * 13 + 7 * 11)
    assert coefficients == {2: 6 * (17 * 13 + 7 * 23), 3: 6 * 19 * 13, 4: 6 * 7 * 29}
    assert evidence[0]['lower_contribution'] == lower
    T = Q(1 << 32)
    direct = 6 * ((5 + 17 / T**2 + 19 / T**3) * 13 + 7 * (11 + 23 / T**2 + 29 / T**4))
    assert s.up(lower + s.evaluate_polynomial(coefficients, 32)) >= direct


def test_aggregate_outward_rational_rounding_no_cancellation():
    rows = [dict(c_abs=Q(1, 7), C_F=Q(1, 11), L_t=Q(1, 13), W_t=Q(1, 17),
                 L_u=Q(1, 19), W_u=Q(1, 23), U_t={2: Q(1, 29)}, U_u={3: Q(1, 31)})] * 5
    lower, coefficients, _ = s.aggregate(rows)
    T = Q(1 << 40)
    direct = 5 * Q(1, 77) * ((Q(1, 13) + Q(1, 29) / T**2) * Q(1, 23) + Q(1, 17) * (Q(1, 19) + Q(1, 31) / T**3))
    assert s.up(lower + s.evaluate_polynomial(coefficients, 40)) >= direct


def test_candidate_choice_and_monotonicity():
    # Bound T^-2*2^64 <=2^-21 first holds at candidate exponent 48.
    choice = s.choose(Q(0), {2: Q(1 << 64)})
    assert choice['status'] == 'FIRST_TESTED_CUTOFF_SELECTED'
    assert choice['selected_upper_exponent'] == 48
    assert len(choice['candidates']) == 5
    values = [Q(row['combined_radius']) for row in choice['candidates']]
    assert values == sorted(values, reverse=True)
    assert choice['selection_is_global_optimum'] is False


def test_lower_budget_failure_and_no_candidate_success():
    assert s.choose(2*s.TARGET, {2: Q(1)})['status'] == 'LOWER_BUDGET_EXCEEDED'
    assert s.choose(Q(0), {2: Q(1 << 200)})['status'] == 'NO_TESTED_CUTOFF_MEETS_BUDGET'


def test_nonexact_or_negative_inputs_refused():
    for value in [-1, Q(-1, 3), 0.5, True, '1/2']:
        with unittest.TestCase().assertRaises(s.CutoffError): s.up(value)


def test_unplanned_cutoff_refused():
    for exponent in [31, 33, 65, True, 32.0]:
        with unittest.TestCase().assertRaises(s.CutoffError): s.evaluate_polynomial({2: Q(1)}, exponent)


def test_invalid_degree_and_disabled_actual_execution():
    with unittest.TestCase().assertRaises(s.CutoffError): s.evaluate_polynomial({1: Q(1)}, 32)
    with unittest.TestCase().assertRaises(s.CutoffError): s.evaluate_polynomial({2: Q(-1)}, 32)
    with unittest.TestCase().assertRaises(s.CutoffError): s.choose(Q(0), {2: Q(1)}, Q(0))
    with unittest.TestCase().assertRaises(s.CutoffError): s.evaluate_pinned()
    with unittest.TestCase().assertRaises(s.CutoffError): s.evaluate_pinned(execute_pinned=True, lower_cutoff=Q(1, 256))


def test_relative_rounder_identical_to_existing_planner_without_executing_data():
    import ast
    source = s.PLANNER.read_text()
    tree = ast.parse(source)
    selected = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'upward_dyadic')
    module = ast.Module(body=[selected], type_ignores=[])
    def integer(value, lo, hi, name):
        assert type(value) is int and lo <= value <= hi
    namespace = dict(Q=Q, integer=integer, EndpointError=ValueError, LimitReached=RuntimeError,
                     MAX_QUANT_INPUT_BITS=65536, MAX_QUANT_WORK_BITS=131072)
    exec(compile(ast.fix_missing_locations(module), str(s.PLANNER), 'exec'), namespace)
    for numerator in [1, 3, 17, 2**300+1]:
        for denominator in [1, 3, 11, 2**500+1]:
            q=Q(numerator,denominator)
            assert s.up(q) == namespace['upward_dyadic'](q,128)


if __name__ == '__main__':
    suite = unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in sorted(globals().copy().items()) if name.startswith('test_'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
