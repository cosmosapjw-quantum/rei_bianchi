import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location('m3_full_pair_screen', ROOT/'m3_full_pair_screen.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_pair_uses_historical_normalization_and_all_components():
    m = load()
    class H0:
        def h0(self, a, b, t, W, z, q, active):
            return np.full((7, 3), active+1, np.clongdouble), np.full((7, 3), active+2, np.longdouble)
    class Foreign:
        observed_threads = 1
        def __call__(self, t, gs, gw, W, pars):
            return np.ones((2, 2, 3), np.clongdouble), np.ones((2, 2, 3), np.longdouble)
    d = {'exponents': np.array([1.0, 4.0]), 'v': np.array(2.0), 'pref': np.array(3.0)}
    t = np.array([1.0]); W = np.zeros((3, 9, 1, 1)); gs = np.array([1.0]); gw = np.array([1.0])
    result = m.full_pair(H0(), Foreign(), d, t, W, gs, gw, (0, 1), 2.0)
    base = np.sqrt(2)*3*(2/np.pi)**.75*(8/np.pi)**.75
    expected = base*np.array([[1, 2, 2], [1, 4, 4]])
    assert result['H0'].shape == (2, 7, 3)
    assert result['H0_sumabs'].shape == (2, 7, 3)
    assert np.array_equal(result['foreign'], np.broadcast_to(expected, (2, 2, 3)))
    assert np.array_equal(result['foreign_sumabs'], np.broadcast_to(abs(expected), (2, 2, 3)))


def test_exact_gate_checks_each_component_numerically():
    m = load()
    ref = {'H0': np.array([1], dtype=np.clongdouble), 'H0_sumabs': np.array([2], dtype=np.longdouble),
           'foreign': np.array([3], dtype=np.clongdouble), 'foreign_sumabs': np.array([4], dtype=np.longdouble)}
    candidate = {k: v.copy() for k, v in ref.items()}
    assert m.compare_full_pair(ref, candidate)['all_exact'] is True
    candidate['foreign_sumabs'][0] += 1
    assert m.compare_full_pair(ref, candidate)['all_exact'] is False
