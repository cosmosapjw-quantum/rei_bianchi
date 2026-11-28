"""Independent, manufactured-model checks for the new scaled callback adapter.

No HE29 inputs, native models, historical tests, or table files are used.
"""
from pathlib import Path
import math
import sys

import numpy as np
import unittest
from itertools import product
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vigilode_callbacks import CallbackContractError, SegmentCallbacks, validate_model


def cases(names, values):
    names = tuple(name.strip() for name in names.split(","))
    def decorate(fn):
        fn._case_specs = getattr(fn, "_case_specs", []) + [(names, values)]
        return fn
    return decorate


def raises(exception):
    return unittest.TestCase().assertRaises(exception)


class ManufacturedModel:
    def __init__(self, sparse_jac=False):
        self.jac_times = []
        self.jac_states = []
        self.rhs_times = []
        self.rhs_states = []
        self.sparse_jac = sparse_jac
        self.scale = np.array([0.5, 2.0, 5.0, 20.0])
        self.t_end = 8.0
        self.breakpoints = np.array([2.0, 5.0])

    def initial_state(self):
        return np.array([0.2, 0.3, 0.4, 0.5])

    def rhs(self, t, y):
        self.rhs_times.append(float(t))
        self.rhs_states.append(y.copy())
        return np.array([2*y[0] + y[1]*y[2] + t*t,
                         -3*y[1] + math.sin(t) + y[0]*y[0],
                         t*y[0] - y[2] + 2*y[3],
                         0.25*y[0]*y[3] - y[3] + 2*t + 1])

    def jac(self, t, y):
        self.jac_times.append(float(t))
        self.jac_states.append(y.copy())
        matrix = np.array([[2, y[2], y[1], 0],
                           [2*y[0], -3, 0, 0],
                           [t, 0, -1, 2],
                           [0.25*y[3], 0, 0, 0.25*y[0]-1]], dtype=float)
        self.returned_matrix = sparse.csr_matrix(matrix) if self.sparse_jac else matrix
        return self.returned_matrix

    @staticmethod
    def directional(t, y, w):
        return np.array([2*w[0] + w[1]*y[2] + y[1]*w[2],
                         -3*w[1] + 2*y[0]*w[0],
                         t*w[0] - w[2] + 2*w[3],
                         0.25*(w[0]*y[3] + y[0]*w[3]) - w[3]])

    @staticmethod
    def partial_time(t, y):
        return np.array([2*t, math.cos(t), y[0], 2.0])


@cases("interval", [(0.0, 1.0), (2.0, 5.75), (1.0, 1.125)])
def test_rhs_time_and_state_scaling(interval):
    model = ManufacturedModel()
    left, right = interval
    scale = np.array([0.5, 2.0, 5.0, 20.0])
    z = np.array([0.2, -0.3, 0.4, 0.1])
    u = 0.37
    callback = SegmentCallbacks(model, left, right, scale)
    y = scale*z
    t = left + u*(right-left)
    physical = np.array([2*y[0]+y[1]*y[2]+t*t,
                         -3*y[1]+math.sin(t)+y[0]**2,
                         t*y[0]-y[2]+2*y[3],
                         0.25*y[0]*y[3]-y[3]+2*t+1])
    np.testing.assert_allclose(callback.rhs(u, z), (right-left)*physical/scale,
                               rtol=3e-15, atol=1e-14)
    np.testing.assert_array_equal(model.rhs_states[-1], y)
    assert model.rhs_times[-1] == t


@cases("sparse_jac", [False, True])
@cases("scale", [np.array([0.5, 2, 5, 20]),
                                  np.array([1e-6, 1e3, 2e-2, 1e5])])
def test_jvp_includes_both_state_scales_and_dt(sparse_jac, scale):
    model = ManufacturedModel(sparse_jac)
    callback = SegmentCallbacks(model, 2.0, 5.75, scale)
    z = np.array([0.2, -0.3, 0.4, 0.1])
    v = np.array([0.7, 0.2, -0.6, 0.3])
    t = callback.time(0.4)
    expected = 3.75*model.directional(t, scale*z, scale*v)/scale
    np.testing.assert_allclose(callback.jvp(0.4, z, v), expected,
                               rtol=3e-14, atol=3e-13)


@cases("sparse_jac", [False, True])
def test_cache_uses_exact_state_bytes_and_physical_time(sparse_jac):
    model = ManufacturedModel(sparse_jac)
    callback = SegmentCallbacks(model, 2.0, 5.0, model.scale)
    z, v = np.array([0.2, -0.3, 0.4, 0.1]), np.ones(4)
    first = callback.jvp(0.3, z, v)
    callback.jvp(0.3, z.copy(), -v)
    assert callback.counts["jacobian_builds"] == 1
    assert callback.counts["jacobian_cache_hits"] == 1
    # A mutation in the returned parent-owned matrix must not alter the cache.
    if sparse_jac:
        model.returned_matrix.data[:] = 1e99
    else:
        model.returned_matrix[:] = 1e99
    np.testing.assert_array_equal(callback.jvp(0.3, z, v), first)
    z[0] = np.nextafter(z[0], np.inf)
    callback.jvp(0.3, z, v)
    assert callback.counts["jacobian_builds"] == 2
    callback.jvp(0.4, z, v)
    assert callback.counts["jacobian_builds"] == 3
    assert len(model.jac_times) == 3
    assert model.jac_times[-1] != model.jac_times[-2]


@cases("u", [0.0, 1e-9, 0.2, 0.8, 1-1e-9, 1.0])
def test_time_partial_has_dt_squared_at_fixed_scaled_state(u):
    model = ManufacturedModel()
    callback = SegmentCallbacks(model, 2.0, 5.75, model.scale)
    z = np.array([0.2, -0.3, 0.4, 0.1])
    expected = callback.dt**2 * model.partial_time(callback.time(u), z*model.scale) / model.scale
    np.testing.assert_allclose(callback.partial_u(u, z), expected,
                               rtol=2e-8, atol=2e-9)
    assert all(callback.left <= t <= callback.right for t in model.rhs_times)
    assert all(np.array_equal(y, z*model.scale) for y in model.rhs_states)
    assert callback.counts["partial_u"] == 1


class OffsetTimeModel(ManufacturedModel):
    def __init__(self, left, right):
        super().__init__()
        self.left, self.right = left, right
        self.slope = np.array([0.125, -0.375, 0.5, 1.0])

    def rhs(self, t, y):
        assert self.left <= t <= self.right
        self.rhs_times.append(float(t))
        tau = (t-self.left)/(self.right-self.left)
        return np.array([0.5, -0.25, 0.125, 2.0]) + tau*self.slope + 0.125*y

    def jac(self, t, y):
        return 0.125*np.eye(4)


@cases("ulps", [1, 2, 3, 8])
@cases("u", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_large_proper_time_tiny_interval_remains_bounded(ulps, u):
    left = float(2**60)
    right = left + ulps*math.ulp(left)
    model = OffsetTimeModel(left, right)
    callback = SegmentCallbacks(model, left, right, model.scale)
    z = np.array([0.2, -0.3, 0.4, 0.1])
    # This model varies linearly in normalized represented physical time.
    expected = callback.dt*model.slope/model.scale
    np.testing.assert_allclose(callback.partial_u(u, z), expected,
                               rtol=5e-15, atol=2e-12)
    assert model.rhs_times
    assert all(left <= t <= right for t in model.rhs_times)
    if ulps == 1:
        assert callback.counts["two_point_time_derivatives"] == 1


def test_constant_rhs_time_partial_is_zero():
    model = ManufacturedModel()
    model.rhs = lambda t, y: np.array([1e80, -2e80, 3e80, 4e80])
    callback = SegmentCallbacks(model, 2.0, 5.0, model.scale)
    for u in (0.0, 0.3, 1.0):
        np.testing.assert_array_equal(callback.partial_u(u, np.ones(4)), np.zeros(4))


def test_scale_is_owned_by_callback():
    model = ManufacturedModel()
    scale = model.scale.copy()
    callback = SegmentCallbacks(model, 2.0, 5.0, scale)
    scale[:] = 123.0
    np.testing.assert_array_equal(callback.scale, model.scale)


@cases("u", [-1e-9, 1+1e-9, np.nan, np.inf])
def test_time_domain_rejected(u):
    callback = SegmentCallbacks(ManufacturedModel(), 0.0, 1.0, np.ones(4))
    with raises(CallbackContractError):
        callback.time(u)


def test_roundoff_endpoint_admission_is_counted():
    callback = SegmentCallbacks(ManufacturedModel(), 2.0, 5.0, np.ones(4))
    assert callback.time(-np.finfo(float).eps) == 2.0
    assert callback.time(1+np.finfo(float).eps) == 5.0
    assert callback.counts["time_roundoff_clamps"] == 2


@cases("left,right", [(1, 1), (2, 1), (np.nan, 1), (0, np.inf),
                                       (-1e308, 1e308)])
def test_invalid_interval_rejected(left, right):
    with raises(CallbackContractError):
        SegmentCallbacks(ManufacturedModel(), left, right, np.ones(4))


@cases("scale", [[], [1, 0], [1, -1], [1, np.nan], [[1, 2]]])
def test_invalid_scale_rejected(scale):
    with raises(CallbackContractError):
        SegmentCallbacks(ManufacturedModel(), 0, 1, scale)


@cases("bad", [np.ones(3), np.ones((4, 1)), [1, 2, 3, np.nan],
                               [1, 2, 3, np.inf]])
def test_vector_input_rejection(bad):
    callback = SegmentCallbacks(ManufacturedModel(), 0, 1, np.ones(4))
    with raises(CallbackContractError):
        callback.rhs(0.4, bad)
    with raises(CallbackContractError):
        callback.jvp(0.4, np.ones(4), bad)


@cases("kind", ["rhs", "dense_jac", "sparse_jac", "jac_shape"])
def test_invalid_model_output_rejection(kind):
    model = ManufacturedModel()
    callback = SegmentCallbacks(model, 0, 1, np.ones(4))
    if kind == "rhs":
        model.rhs = lambda t, y: np.full(4, np.inf)
        call = lambda: callback.rhs(0.4, np.ones(4))
    else:
        if kind == "dense_jac":
            model.jac = lambda t, y: np.full((4, 4), np.nan)
        elif kind == "sparse_jac":
            model.jac = lambda t, y: sparse.csr_matrix(np.full((4, 4), np.inf))
        else:
            model.jac = lambda t, y: np.eye(3)
        call = lambda: callback.jvp(0.4, np.ones(4), np.ones(4))
    with raises(CallbackContractError):
        call()


@cases("method", ["rhs", "jvp"])
def test_overflowed_physical_state_rejected_before_model_call(method):
    model = ManufacturedModel()
    seen = []
    model.rhs = lambda t, y: (seen.append(y.copy()), np.zeros(4))[1]
    model.jac = lambda t, y: (seen.append(y.copy()), np.zeros((4, 4)))[1]
    callback = SegmentCallbacks(model, 0, 1, np.full(4, 1e308))
    with np.errstate(over="ignore", invalid="ignore"):
        with raises(CallbackContractError):
            if method == "rhs":
                callback.rhs(0.4, np.full(4, 1e308))
            else:
                callback.jvp(0.4, np.full(4, 1e308), np.zeros(4))
    assert seen == []


def test_overflowed_physical_jvp_direction_rejected():
    model = ManufacturedModel()
    callback = SegmentCallbacks(model, 0, 1, np.full(4, 1e308))
    with np.errstate(over="ignore", invalid="ignore"):
        with raises(CallbackContractError):
            callback.jvp(0.4, np.zeros(4), np.full(4, 1e308))


@cases("change", ["scale", "initial", "end", "cut_order",
                                  "cut_zero", "cut_end", "cut_nan"])
def test_validate_model_rejects_contract_defects(change):
    model = ManufacturedModel()
    if change == "scale":
        model.scale = [1, 0, 1, 1]
    elif change == "initial":
        model.initial_state = lambda: np.ones(3)
    elif change == "end":
        model.t_end = np.inf
    elif change == "cut_order":
        model.breakpoints = [3, 2]
    elif change == "cut_zero":
        model.breakpoints = [0, 2]
    elif change == "cut_end":
        model.breakpoints = [2, 8]
    else:
        model.breakpoints = [np.nan]
    with raises(CallbackContractError):
        validate_model(model)


def test_validate_model_returns_owned_ordered_segmentation():
    model = ManufacturedModel()
    scale, initial, cuts = validate_model(model)
    np.testing.assert_array_equal(cuts, [0, 2, 5, 8])
    model.scale[:] = 99
    model.breakpoints[:] = 77
    np.testing.assert_array_equal(scale, [0.5, 2, 5, 20])
    np.testing.assert_array_equal(initial, [0.2, 0.3, 0.4, 0.5])
    np.testing.assert_array_equal(cuts, [0, 2, 5, 8])


class CallbackAdapterTests(unittest.TestCase):
    """Each manufactured parameter combination is an independent unittest."""


for _name, _fn in list(globals().items()):
    if not _name.startswith("test_") or not callable(_fn):
        continue
    _specs = getattr(_fn, "_case_specs", [])
    _combos = product(*(values for _, values in _specs)) if _specs else [()]
    for _index, _combo in enumerate(_combos):
        _kwargs = {}
        for (_names, _values), _value in zip(_specs, _combo):
            _items = (_value,) if len(_names) == 1 else _value
            _kwargs.update(zip(_names, _items))
        def _run(self, fn=_fn, kwargs=_kwargs):
            fn(**kwargs)
        _run.__doc__ = _name + " " + str(_index)
        setattr(CallbackAdapterTests, _name + "_" + str(_index), _run)

# Do not leave the final loop value (the test class) visible under a second
# module name: unittest discovers class aliases as an additional suite.
del _fn


if __name__ == "__main__":
    unittest.main(verbosity=2)
