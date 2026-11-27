import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"adaptive_policy.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_z05_derivative_lower_bounds():
    b=m.midpoint_lower_bounds(0.0875296210906087,0.15030919260543524,2.2358772390338113,1.0)
    assert b["O_fourth_lower_per_t4"]==pytest.approx(1.3449138103246667)
    assert b["K_second_lower_per_t3"]==pytest.approx(0.24053574221790144)
    assert b["O_fourth_lower_per_z4"]==pytest.approx(33.611374498793744)
    assert b["K_second_lower_per_t_z2"]==pytest.approx(1.202473540843482)

def test_training_relabel():
    x=m.consume_validation_as_training()
    assert x["training_nodes_z"]==[0,.5,1,2,3,4]
    assert x["independent_validation_points"]==[]

def test_next_validation_is_z35():
    d=m.next_validation_design()
    assert d["selected_z"]==3.5
    assert d["selected_K_half_gap"]==pytest.approx(0.09561189201673982)
    assert d["selected_Dmax_half_gap"]==pytest.approx(0.10476936735470115)
    assert d["execution_authorized"] is False

def test_bad_inputs():
    with pytest.raises(ValueError):m.midpoint_lower_bounds(0,.1,1)
    with pytest.raises(ValueError):m.midpoint_lower_bounds(.1,.1,0)
