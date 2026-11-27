import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"successor_policy.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_z35_lower_bounds():
    b=m.midpoint_lower_bounds(0.028316443455109017,0.06617406868623811,2.2358772390338113,1.0)
    assert b["O_fourth_lower_per_t4"]==pytest.approx(0.4350890062991452)
    assert b["K_second_lower_per_t3"]==pytest.approx(0.10589657526007562)
    assert b["O_fourth_lower_per_z4"]==pytest.approx(10.873514286761862)
    assert b["K_second_lower_per_t_z2"]==pytest.approx(0.5293925494899049)

def test_successor_consumes_z35():
    p=m.successor_training_policy()
    assert p["training_nodes_z"]==[0,.5,1,2,3,3.5,4]
    assert p["independent_validation_points"]==[]

def test_z25_preserved_fresh():
    x=m.next_holdout_information()
    assert x["z"]==2.5
    assert x["S_design_only_per_ta"]==pytest.approx(0.280789512416017)
    assert x["K_half_gap_per_ta"]==pytest.approx(0.09561189201673985)
    assert x["Dmax_half_gap_per_ta"]==pytest.approx(0.10280590292237807)
    assert x["execution_authorized"] is False

def test_halving_factors():
    assert m.conditional_halving_coefficients()=={"O_cubic":1/16,"K_linear":1/4}

def test_invalid():
    with pytest.raises(ValueError):m.midpoint_lower_bounds(-1,.1,1)
    with pytest.raises(ValueError):m.midpoint_lower_bounds(.1,.1,0)
