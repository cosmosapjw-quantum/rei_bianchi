"""New tests for the exact-input defect found by independent PHYS69 review."""
from fractions import Fraction as F

import pytest

from wu088_hh import phys69_angular_tail as tail


@pytest.mark.parametrize("field", ["numerator", "denominator"])
@pytest.mark.parametrize("bad", [True, False, 1.75])
def test_rational_rejects_coercion(field, bad):
    record = {"numerator": "1", "denominator": "2"}
    record[field] = bad
    with pytest.raises(ValueError):
        tail.read_rational(record)


@pytest.mark.parametrize("bad", [True, False, 1.75])
def test_dyadic_mantissa_rejects_coercion(bad):
    with pytest.raises(ValueError):
        tail._dyadic({"mantissa": bad, "exponent2": 0})


@pytest.mark.parametrize("bad", [True, False, 1.75, "0"])
def test_dyadic_exponent_requires_json_integer(bad):
    with pytest.raises(ValueError):
        tail._dyadic({"mantissa": "1", "exponent2": bad})


@pytest.mark.parametrize("n,d,expected", [(1, 2, F(1, 2)), ("-3", "8", F(-3, 8)),
                                         ("0", 7, F(0)), (7, "-2", F(-7, 2))])
def test_exact_integer_records_preserved(n, d, expected):
    assert tail.read_rational({"numerator": n, "denominator": d}) == expected
    assert tail._dyadic({"mantissa": n, "exponent2": -100}) == int(n)*F(2)**-100


@pytest.mark.parametrize("value", [None, ["numerator", "denominator"],
                                  {"numerator": "1", "denominator": "0"}])
def test_invalid_rational_record_refused(value):
    with pytest.raises(ValueError):
        tail.read_rational(value)


@pytest.mark.parametrize("ell", [True, "21", 21.5])
def test_goal_external_domain_checked_before_range(ell):
    with pytest.raises(ValueError):
        tail.minimum_cutoff_for_angular_goal("1e-62", ell=ell)
