from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

ANALYSIS=Path(__file__).resolve().parents[1]/'analysis'
REPO=Path(__file__).resolve().parents[3]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module

def test_four_site_lower_corner_primal_parity_primary_lane():
    m=load('evalsite_trial',ANALYSIS/'evaluation_site_trial.py')
    result=m.primal_parity_audit(REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY',partition=2048)
    assert result['parity_pass'], result
    assert result['site_trace'][:4]==[
        'population_t0','population_t1_predictor','thermal_tgamma','thermal_t1_final'
    ]
    assert result['max_state_relative_difference']<=1.0e-13
    assert result['max_temperature_relative_difference']<=1.0e-13
    assert result['ledger_equal']
