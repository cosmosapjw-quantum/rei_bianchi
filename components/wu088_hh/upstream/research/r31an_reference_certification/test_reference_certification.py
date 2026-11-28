import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"reference_certification.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_equal_ratio_ladder():
    assert m.ORDERS==(144,192,256)
    assert m.RATIO==pytest.approx(4/3)

def test_observed_order_power_law():
    p=4.0
    r=4/3
    d1=1-r**(-p)
    d2=r**(-p)*(1-r**(-p))
    assert m.observed_order_equal_ratio(d1,d2)==pytest.approx(p)

def test_conditional_power_errors():
    x=m.conditional_power_errors(.01,4)
    rho=(3/4)**4
    assert x["rho"]==pytest.approx(rho)
    assert x["E192_conditional"]==pytest.approx(.01/(1-rho))
    assert x["E256_conditional"]==pytest.approx(.01*rho/(1-rho))
    assert x["rigorous"] is False

def test_geometric_tail():
    x=m.conditional_geometric_tail(.01,.2)
    assert x["latest_tail_bound"]==pytest.approx(.0025)
    assert x["previous_tail_bound"]==pytest.approx(.0125)
    assert x["requires_certified_future_contraction"] is True

def test_current_primary_and_secondary_sensitivity():
    p=m.common_reference_radius(
      [.05250496632934204,.05457284174805037],
      [.3723284019854093,.3880297823244174]
    )
    s=m.common_reference_radius(
      [.05250496632934204,.05457284174805037],
      [.10963738645582422,.1423934281278521]
    )
    assert p["strict_common_radius_open"]==pytest.approx(.15991171777803362)
    assert s["strict_common_radius_open"]==pytest.approx(.028566210013241087)
    assert not p["radius_is_actual_source_error_bound"]

def test_contract_has_no_execution():
    c=m.study_contract()
    assert c["new_orders_required"]==[144,256]
    assert c["science_execution_authorized"] is False
    assert c["three_order_result_is_rigorous_continuum_bound"] is False

@pytest.mark.parametrize("args",[(0,.1),(.1,0),(-1,.1)])
def test_bad_order_inputs(args):
    with pytest.raises(ValueError):m.observed_order_equal_ratio(*args)
