import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / 'm2_bridge.py'


def module():
    spec = importlib.util.spec_from_file_location('m2_bridge', SCRIPT)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_selects_real_cost_extremes_and_median():
    costs = {(0, 0): 9.0, (0, 1): 1.0, (1, 0): 5.0}
    assert module().classify_pairs(costs) == [
        ('cheap', (0, 1), 1.0), ('median', (1, 0), 5.0),
        ('expensive', (0, 0), 9.0)]


def test_exact_check_includes_sumabs():
    m = module()
    value = np.array([1 + 2j], dtype=np.clongdouble)
    sumabs = np.array([3], dtype=np.longdouble)
    assert m.exact_pair((value, sumabs), (value.copy(), sumabs.copy()))
    assert not m.exact_pair((value, sumabs), (value.copy(), sumabs + 1))


def test_bridge_drops_loader_injection_before_native_load():
    env = dict(os.environ, LD_LIBRARY_PATH='/tmp/untrusted')
    p = subprocess.run([sys.executable, '-c',
                        'import os; import research.r31s_ncp.m2_bridge; '
                        'print(os.environ.get("LD_LIBRARY_PATH"))'],
                       env=env, capture_output=True, text=True, check=True)
    assert p.stdout.strip() == 'None'
