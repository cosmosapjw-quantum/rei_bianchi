from __future__ import annotations
import importlib.util,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def load_module():
    path=STAGE/'analysis/run_four_corner_preflight.py'
    spec=importlib.util.spec_from_file_location('run_four_corner_preflight',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module


def test_wide_corner_enclosure_is_a_robust_fail_closed_result():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':3e-3,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=False,
    )
    assert decision['classification']=='SOURCE_EXTENSION_CALIBRATION_REQUIRED_WIDE_ENCLOSURE'
    assert not decision['production_authorized']


def test_narrow_corners_do_not_certify_the_continuous_nonlinear_family():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':1e-5,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=False,
    )
    assert decision['classification']=='CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED'
    assert not decision['production_authorized']


def test_only_narrow_certified_enclosure_can_authorize():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':1e-5,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=True,
    )
    assert decision['classification']=='UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED'
    assert decision['production_authorized']


def test_numerical_failure_precedes_uncertainty_classification():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':0.0,'x_HeII':0.0,'x_HeIII':0.0,'log_T':0.0},
        all_numerical_gates_pass=False,
        continuous_parameter_certified=True,
    )
    assert decision['classification']=='HARD_GATE_FAILURE'
    assert not decision['production_authorized']


def test_numerical_and_source_uncertainty_gates_are_distinct():
    m=load_module()
    assert m.LOCAL_ERROR_GATE==2e-4
    assert m.UNCERTAINTY_GATE==2e-3
    assert m.LOCAL_ERROR_GATE < m.UNCERTAINTY_GATE
