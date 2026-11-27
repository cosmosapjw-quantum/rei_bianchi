import importlib.util
from pathlib import Path
import pytest
import math

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"unequal_order_ladder.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_threshold():
    assert m.THRESHOLD==pytest.approx(1.2239010857415446)

def test_ratio_known_orders():
    assert m.ratio_model(1)==pytest.approx(1.5)
    assert m.ratio_model(2)==pytest.approx(1.8409090909090908)

def test_solver_recovers_p():
    for p in [0.1,0.5,1,2,4,8]:
        assert m.solve_positive_order(m.ratio_model(p))==pytest.approx(p,rel=1e-10,abs=1e-11)

def test_no_positive_order_below_threshold():
    with pytest.raises(ValueError):m.solve_positive_order(m.THRESHOLD)
    with pytest.raises(ValueError):m.solve_positive_order(1.0)

def test_conditional_error_formula():
    p=2.0
    d23=0.01
    rho=m.ratio_model(p)
    x=m.conditional_errors(rho*d23,d23)
    assert x["p_conditional"]==pytest.approx(2.0)
    assert x["E192_conditional"]==pytest.approx(d23/((192/160)**2-1))
    assert x["E160_conditional"]==pytest.approx(d23/(1-(160/192)**2))
    assert x["rigorous"] is False
    assert x["stable_error_direction_required"] is True

def test_authority_ladder():
    a=m.authority_ladder()
    assert a["orders"]==[128,160,192]
    assert a["source_modification_required"] is False
    assert a["science_execution_authorized"] is False

def test_large_finite_ratio_has_positive_solution():
    p=m.solve_positive_order(1e200)
    assert math.log(m.ratio_model(p))==pytest.approx(math.log(1e200),abs=1e-10)

def test_small_positive_power_ratio_is_stable():
    p=1e-12
    expected=m.THRESHOLD*(1+(math.log(5/4)+math.log(6/5))*p/2)
    assert m.ratio_model(p)==pytest.approx(expected,abs=5e-16,rel=0)
