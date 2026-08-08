from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).parents[1] / 'analysis/run_sdirk_fast_preflight.py'


def load():
    spec = importlib.util.spec_from_file_location('r2b_fast_preflight', MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_fast_runner_is_optimization_only_and_sealed():
    m = load()
    assert m.CANDIDATE_METHOD == 'NONAUTONOMOUS_MPRK22_ALPHA1_PLUS_LSTABLE_ALEXANDER_SDIRK2_ANALYTIC_ROOT'
    assert m.PARTITIONS == (512, 1024, 2048)
    assert m.PARITY_REFERENCE == 'ATTEMPT_1_MPRK22_ALPHA1_LSTABLE_SDIRK2_THERMAL'
