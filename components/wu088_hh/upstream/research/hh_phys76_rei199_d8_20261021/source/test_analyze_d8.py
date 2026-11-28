import numpy as np
import pytest

from analyze_d8 import crossing_brackets


def test_one_strict_adjacent_bracket():
    assert crossing_brackets(np.array([0., 1., 2., 3.]), np.array([-2., -1., 1., 2.])) == [1]


def test_no_crossing_and_zero_touch_are_not_brackets():
    assert crossing_brackets(np.arange(4.), np.array([-2., -1., 0., 1.])) == []


def test_multiple_brackets_are_reported_individually():
    assert crossing_brackets(np.arange(5.), np.array([-1., 1., -1., 1., -1.])) == [0, 1, 2, 3]


def test_nonmonotone_grid_rejected():
    with pytest.raises(ValueError):
        crossing_brackets(np.array([0., 2., 1.]), np.array([-1., 1., -1.]))
