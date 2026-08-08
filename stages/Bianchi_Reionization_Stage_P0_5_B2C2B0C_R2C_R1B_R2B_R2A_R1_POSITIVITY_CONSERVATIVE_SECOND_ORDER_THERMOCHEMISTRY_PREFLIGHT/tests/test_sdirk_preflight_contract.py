from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).parents[1] / 'analysis/run_sdirk_preflight.py'


def load():
    spec = importlib.util.spec_from_file_location('r2b_r2a_r1_sdirk_preflight', MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sdirk_runner_has_sealed_method_and_partitions():
    m = load()
    assert m.CANDIDATE_METHOD == 'NONAUTONOMOUS_MPRK22_ALPHA1_PLUS_LSTABLE_ALEXANDER_SDIRK2_THERMAL'
    assert m.PARTITIONS == (512, 1024, 2048)
    assert m.LANES == (
        'LOCAL_NEUTRAL_HAZARD_PRIMARY',
        'RECOMBINATION_WEIGHTED_AUDITOR',
        'SCRIPT_SELF_SHIELDING_AUDITOR',
    )


def test_sdirk_classification_requires_every_lane():
    m = load()
    rows = []
    for lane in m.LANES:
        rows.append({
            'lane': lane,
            'partition': 1024,
            'candidate_converged': True,
            'all_gates_pass': True,
            'local_error': 1.0e-4,
        })
    result = m.classify(rows)
    assert result['science_pass'] is True
    rows[-1]['local_error'] = 3.0e-4
    result = m.classify(rows)
    assert result['science_pass'] is False
    assert result['lane_pass'][m.LANES[-1]] is False
