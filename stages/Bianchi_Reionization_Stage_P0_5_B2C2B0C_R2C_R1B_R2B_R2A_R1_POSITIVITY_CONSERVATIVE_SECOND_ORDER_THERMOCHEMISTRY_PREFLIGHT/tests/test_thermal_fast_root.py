from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ANALYSIS = Path(__file__).parents[1] / 'analysis'
R2A_ANALYSIS = Path(__file__).resolve().parents[3] / 'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis'


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture(n: int = 64):
    rng = np.random.default_rng(78123)
    nh = 10.0 ** rng.uniform(55.0, 60.0, size=n)
    nhe = 0.08 * nh
    xh = rng.uniform(0.05, 0.95, size=n)
    he = rng.dirichlet(np.array([2.0, 1.5, 0.7]), size=n)
    pop = np.column_stack([
        nh * (1.0 - xh), nh * xh,
        nhe * he[:, 0], nhe * he[:, 1], nhe * he[:, 2],
    ])
    temperature = 10.0 ** rng.uniform(2.7, 5.1, size=n)
    volume = 10.0 ** rng.uniform(67.0, 72.0, size=n)
    heat = 10.0 ** rng.uniform(30.0, 39.0, size=n)
    hubble = 10.0 ** rng.uniform(-19.0, -16.0, size=n)
    return pop, temperature, volume, heat, hubble


def test_analytic_rhs_matches_locked_numpy_oracle():
    fast = load('r2b_fast_thermal', ANALYSIS / 'thermal_fast_root.py')
    oracle = load('r2b_fast_thermal_oracle', R2A_ANALYSIS / 'thermal_backends.py')
    pop, temperature, volume, heat, hubble = fixture()
    rhs, _ = fast.thermal_rhs_and_dlogT(
        np.log(temperature), pop, volume, heat, hubble
    )
    expected = oracle._thermal_rhs_numpy(
        np.log(temperature), pop, volume, heat, hubble
    )
    scale = np.maximum(np.abs(expected), 1.0e-300)
    assert np.max(np.abs(rhs - expected) / scale) < 1.0e-12


def test_analytic_log_temperature_derivative_matches_central_difference():
    fast = load('r2b_fast_thermal_derivative', ANALYSIS / 'thermal_fast_root.py')
    pop, temperature, volume, _heat, hubble = fixture()
    # Remove the large temperature-independent photoheating offset so the
    # central difference is not dominated by subtractive cancellation.
    heat = np.zeros_like(temperature)
    x = np.log(temperature)
    _, derivative = fast.thermal_rhs_and_dlogT(x, pop, volume, heat, hubble)
    h = 2.0e-6
    plus, _ = fast.thermal_rhs_and_dlogT(x + h, pop, volume, heat, hubble)
    minus, _ = fast.thermal_rhs_and_dlogT(x - h, pop, volume, heat, hubble)
    finite = (plus - minus) / (2.0 * h)
    scale = np.maximum.reduce([np.abs(finite), np.abs(derivative), np.full_like(finite, 1.0e-300)])
    assert np.max(np.abs(derivative - finite) / scale) < 2.0e-6


def test_fast_sdirk_root_matches_bisection_reference():
    fast = load('r2b_fast_thermal_solver', ANALYSIS / 'thermal_fast_root.py')
    reference = load('r2b_fast_thermal_reference', ANALYSIS / 'thermal_sdirk2.py')
    oracle = load('r2b_fast_thermal_rhs_oracle', R2A_ANALYSIS / 'thermal_backends.py')
    pop0, temperature, volume, heat, hubble = fixture(32)
    # Small conservative ionization shifts preserve positive nuclei totals.
    stage = pop0.copy(); final = pop0.copy()
    stage[:, 0] *= 0.999; stage[:, 1] = pop0[:, 0] + pop0[:, 1] - stage[:, 0]
    final[:, 0] *= 0.998; final[:, 1] = pop0[:, 0] + pop0[:, 1] - final[:, 0]
    parent_energy = reference.energy_from_temperature(pop0, temperature)
    dt = np.full(32, 2.5e11)
    old = reference.solve_sdirk2(
        parent_populations=pop0,
        stage_populations=stage,
        final_populations=final,
        parent_energy=parent_energy,
        parent_temperature=temperature,
        stage_volume=volume,
        final_volume=volume * 1.0001,
        stage_photoheat=heat,
        final_photoheat=heat * 1.0002,
        stage_hubble=hubble,
        final_hubble=hubble * 1.0001,
        dt=dt,
        rhs_function=oracle._thermal_rhs_numpy,
    )
    new = fast.solve_sdirk2_fast(
        parent_populations=pop0,
        stage_populations=stage,
        final_populations=final,
        parent_energy=parent_energy,
        parent_temperature=temperature,
        stage_volume=volume,
        final_volume=volume * 1.0001,
        stage_photoheat=heat,
        final_photoheat=heat * 1.0002,
        stage_hubble=hubble,
        final_hubble=hubble * 1.0001,
        dt=dt,
    )
    assert np.all(new.stage.bracketed)
    assert np.all(new.final.bracketed)
    assert np.max(new.stage.relative_residual) < 1.0e-10
    assert np.max(new.final.relative_residual) < 1.0e-10
    assert np.max(np.abs(new.stage.temperature / old.stage.temperature - 1.0)) < 1.0e-10
    assert np.max(np.abs(new.final.temperature / old.final.temperature - 1.0)) < 1.0e-10
    assert np.max(np.abs(new.final.energy / old.final.energy - 1.0)) < 1.0e-10



def test_fast_backward_euler_root_matches_bisection_reference():
    fast = load('r2b_fast_be_solver', ANALYSIS / 'thermal_fast_root.py')
    reference = load('r2b_fast_be_reference', ANALYSIS / 'thermal_trapezoid.py')
    oracle = load('r2b_fast_be_rhs_oracle', R2A_ANALYSIS / 'thermal_backends.py')
    pop, temperature, volume, heat, hubble = fixture(32)
    parent_energy = reference.energy_from_temperature(pop, temperature)
    dt = np.full(32, 2.5e11)
    old = reference.solve_backward_euler(
        populations=pop,
        parent_energy=parent_energy,
        parent_temperature=temperature,
        volume=volume,
        photoheat=heat,
        hubble=hubble,
        dt=dt,
        rhs_function=oracle._thermal_rhs_numpy,
    )
    new = fast.solve_backward_euler_fast(
        populations=pop,
        parent_energy=parent_energy,
        parent_temperature=temperature,
        volume=volume,
        photoheat=heat,
        hubble=hubble,
        dt=dt,
    )
    assert np.all(new.bracketed)
    assert np.max(new.relative_residual) < 1.0e-10
    assert np.max(np.abs(new.temperature / old.temperature - 1.0)) < 1.0e-10
    assert np.max(np.abs(new.energy / old.energy - 1.0)) < 1.0e-10
    assert new.iterations < 20

def test_fast_root_rejects_nonpositive_input():
    fast = load('r2b_fast_thermal_invalid', ANALYSIS / 'thermal_fast_root.py')
    pop, temperature, volume, heat, hubble = fixture(4)
    pop[0, 0] = 0.0
    with pytest.raises(ValueError):
        fast.solve_sdirk2_fast(
            parent_populations=pop,
            stage_populations=pop,
            final_populations=pop,
            parent_energy=np.ones(4),
            parent_temperature=temperature,
            stage_volume=volume,
            final_volume=volume,
            stage_photoheat=heat,
            final_photoheat=heat,
            stage_hubble=hubble,
            final_hubble=hubble,
            dt=np.ones(4),
        )
