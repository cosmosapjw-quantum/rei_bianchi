from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

import pytest

spec=importlib.util.spec_from_file_location("phys68_saved_comparison",Path(__file__).with_name("compare_saved_results.py"))
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)


@pytest.mark.parametrize("number",[Fraction(2),Fraction(1,7),Fraction(1,1<<2000)])
def test_sqrt_outward_endpoints_satisfy_exact_rational_inequalities(number):
    low,high=module.sqrt_bounds(number)
    assert low>=0 and low*low<=number<=high*high


def test_exact_rectangle_distance_matches_independent_three_four_five_geometry():
    rectangle=module.Rectangle(Fraction(0),Fraction(0),Fraction(1),Fraction(2))
    low,high=rectangle.distance_bounds((Fraction(4),Fraction(6)))
    assert low==5
    assert high*high>=89
    assert rectangle.distance_bounds((Fraction(1),Fraction(1)))[0]==0


def test_radial_tail_uses_triangle_inequality_without_conjugation_or_double_count():
    rectangle=module.Rectangle(Fraction(10),Fraction(0),Fraction(1),Fraction(0))
    result=module.true_error_record(rectangle,Fraction(1,10),(Fraction(12),Fraction(0)))
    assert module.rational(result["absolute_error_lower"])==Fraction(9,10)
    assert module.rational(result["absolute_error_upper"])==Fraction(31,10)
    assert module.rational(result["relative_error_upper"])==Fraction(31,89)
    assert result["relative_goal_certified"] is False
    assert result["algorithm_uniform_error_bound"] is False


def test_binary64_point_is_exact_and_preserves_subnormal_magnitude():
    assert module.exact_f64(0.1)!=Fraction(1,10)
    assert module.exact_f64(float.fromhex("0x0.0000000000001p-1022"))==Fraction(1,1<<1074)
    for invalid in [1,True,float("nan"),float("inf")]:
        with pytest.raises(ValueError):module.exact_f64(invalid)


def test_rectangle_nesting_and_legacy_serialization_are_exact():
    def old_component(mid,rad):
        return {"mid":{"mantissa":str(mid),"exponent2":-3},
                "rad":{"mantissa":str(rad),"exponent2":-5}}
    legacy={"real":old_component(10,3),"imag":old_component(-7,2)}
    rectangle=module.Rectangle.from_record(legacy)
    inflated=rectangle.inflate(Fraction(1,32))
    assert inflated.contains(rectangle) and not rectangle.contains(inflated)
    assert rectangle.overlaps(inflated)
    with pytest.raises(ValueError):rectangle.inflate(Fraction(-1))


def test_relative_error_is_refused_when_true_modulus_may_vanish():
    rectangle=module.Rectangle(Fraction(0),Fraction(0),Fraction(1),Fraction(1))
    with pytest.raises(ValueError,match="modulus"):
        module.true_error_record(rectangle,Fraction(0),(Fraction(2),Fraction(2)))
