from pathlib import Path
import importlib.util, sys
import numpy as np

HERE = Path(__file__).resolve().parents[1] / "analysis"
REPO = Path(__file__).resolve().parents[3]


def load(name):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_degenerate_interval_rhs_contains_floating_source_at_canonical_state():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    v = model.source_v_point(coordinates[3])
    rhs_iv = model.rhs_interval(
        coordinates=model.point_box(coordinates),
        time_lower_s=0.0,
        time_upper_s=0.0,
        v_interval=model.point_box(v),
        f_interval=model.scalar_interval(0.1),
    )
    reference = model.floating_reference_rhs(
        coordinates=coordinates,
        time_s=0.0,
        v=v,
        f=0.1,
    )
    assert np.all(rhs_iv.lo <= reference)
    assert np.all(reference <= rhs_iv.hi)
    scale = np.maximum(np.abs(reference), 1.0e-30)
    assert float(np.max((rhs_iv.hi-rhs_iv.lo)/scale)) < 1.0e-6


def test_reconstruction_preserves_nuclei_and_structural_population_cone():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    box = model.point_box(model.initial_coordinates())
    populations = model.reconstruct_populations(box)
    assert np.all(populations[0].lo >= 0.0)
    assert np.all(populations[2].lo >= 0.0)
    hsum = populations[0] + populations[1]
    hesum = populations[2] + populations[3] + populations[4]
    assert np.all(hsum.lo <= model.n_h)
    assert np.all(hsum.hi >= model.n_h)
    assert np.all(hesum.lo <= model.n_he)
    assert np.all(hesum.hi >= model.n_he)


def test_internal_helium_coordinates_are_simplex_preserving_triangular_coordinates():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    physical = model.physical_fraction_box(model.point_box(coordinates))
    q = physical.lo[1] + physical.lo[2]
    r = physical.lo[2] / q
    y = model.inputs.state0.values
    expected_q = (y[3] + y[4]) / model.n_he
    expected_r = y[4] / (y[3] + y[4])
    assert np.allclose(q, expected_q, rtol=2.0e-13, atol=2.0e-15)
    assert np.allclose(r, expected_r, rtol=2.0e-13, atol=2.0e-15)
    assert np.all((0.0 < q) & (q < 1.0))
    assert np.all((0.0 < r) & (r < 1.0))

    # A wide but physical rectangular box in direct neutral/conditional
    # coordinates must reconstruct an interval-valued helium simplex without
    # negative He I.
    lo = coordinates.copy()
    hi = coordinates.copy()
    lo[1] *= 0.5
    hi[1] *= 1.5
    lo[2] *= 0.5
    hi[2] *= 1.5
    populations = model.reconstruct_populations(mod.iv.Interval(lo, hi))
    assert np.all(populations[2].lo >= 0.0)
    assert np.all(populations[3].lo >= 0.0)
    assert np.all(populations[4].lo >= 0.0)


def test_finite_internal_box_maps_strictly_inside_hydrogen_and_helium_cones():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    # A broad finite internal box must remain strictly physical without
    # intersecting or clipping against x=0 or x=1 boundaries.
    lo = coordinates.copy()
    hi = coordinates.copy()
    lo[:3] *= 0.75
    hi[:3] = np.minimum(0.999999, hi[:3] * 1.25)
    lo[3] -= 0.25
    hi[3] += 0.25
    box = mod.iv.Interval(lo, hi)
    physical = model.physical_fraction_box(box)
    assert np.all(physical.lo[:3] > 0.0)
    assert np.all(physical.hi[:3] < 1.0)
    populations = model.reconstruct_populations(box)
    assert all(np.all(item.lo > 0.0) for item in populations)



def test_internal_neutral_coordinates_reconstruct_the_initial_state():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    reconstructed = model.coordinates_to_state(coordinates)
    assert np.allclose(reconstructed.values, model.inputs.state0.values, rtol=2.0e-13, atol=0.0)
    assert np.allclose(reconstructed.temperature_K, model.inputs.state0.temperature_K, rtol=2.0e-13, atol=0.0)

def test_internal_coordinates_use_direct_neutral_fractions_and_conditional_heiii():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    y = model.inputs.state0.values
    x_hi = y[0] / model.n_h
    x_hei = y[2] / model.n_he
    r_heiii = y[4] / (y[3] + y[4])
    assert np.allclose(coordinates[0], x_hi, rtol=0.0, atol=0.0)
    assert np.allclose(coordinates[1], x_hei, rtol=0.0, atol=0.0)
    assert np.allclose(coordinates[2], r_heiii, rtol=0.0, atol=0.0)


def test_source_v_interval_is_table_tight_and_contains_point_policy():
    mod = load("reduced_interval_rhs")
    model = mod.ReducedIntervalModel.from_repo(REPO)
    coordinates = model.initial_coordinates()
    box = model.point_box(coordinates)
    vbox = model.source_v_interval(box)
    lower = model.policy.build_v_field_from_temperature("CELL_LOWER_STRICT", np.exp(coordinates[3]))
    upper = model.policy.build_v_field_from_temperature("CELL_UPPER_STRICT", np.exp(coordinates[3]))
    assert np.all(vbox.lo <= lower)
    assert np.all(upper <= vbox.hi)
    table = np.exp(coordinates[3]) >= 1.0e4
    assert np.all(vbox.lo[table] >= np.nextafter(0.285, -np.inf))
    assert np.all(vbox.hi[table] <= np.nextafter(0.375, np.inf))
    assert np.all(vbox.lo[~table] == 0.0)
    assert np.all(vbox.hi[~table] == 1.0)
