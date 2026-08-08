#!/usr/bin/env python3
"""Run optional JAX backend audits in a disposable Python process.

The JAX candidate is diagnostic-only.  Isolating these checks prevents the
runtime/device state from contaminating the long-lived repository pytest
process while preserving all parity and compile-count assertions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _batch():
    tensor = _load("r2b_r2a_tensorized_isolated", STAGE / "analysis/tensorized_inputs.py")
    data = tensor.load_tensorized_inputs(repo_root=REPO)
    n = 256
    y = data.state0.values[:, :n]
    pop = y[:5].T.copy()
    temperature = data.state0.temperature_K[:n]
    z = float(data.z_mid[0, 0])
    volume = data.comoving_volume_cm3[:n] / (1.0 + z) ** 3
    heat = np.zeros(n)
    hubble = np.full(n, 2.0e-18)
    parent_energy = y[5].copy()
    dt = np.full(n, 2.5e12)
    return np.log(temperature), pop, volume, heat, hubble, parent_energy, dt


def relmax(a, b):
    a = np.asarray(a); b = np.asarray(b)
    scale = np.maximum.reduce([np.abs(a), np.abs(b), np.ones_like(a)])
    return float(np.max(np.abs(a - b) / scale))


def run(case: str) -> dict[str, object]:
    m = _load(f"r2b_r2a_thermal_isolated_{case}", STAGE / "analysis/thermal_backends.py")
    args = _batch()
    if case == "balance_parity":
        npb = m.NumpyThermalBackend(); jxb = m.JaxThermalBackend.from_repo(REPO)
        jxb.warmup(*args)
        residual = relmax(jxb.evaluate(*args), npb.evaluate(*args))
        assert residual < 1.0e-12 and jxb.compile_count == 1
        return {"case": case, "relative_residual": residual, "compile_count": 1}
    if case == "balance_dt_compile":
        jxb = m.JaxThermalBackend.from_repo(REPO); jxb.warmup(*args)
        for factor in (1.0, 0.5, 0.25, 0.125, 0.0625):
            trial = list(args); trial[-1] = args[-1] * factor; jxb.evaluate(*trial)
        assert jxb.compile_count == 1
        return {"case": case, "compile_count": 1}
    logt, pop, volume, heat, hubble, parent_energy, dt = args
    temperature = np.exp(logt)
    if case == "root_parity":
        ref = m.NumpyThermalBackend().solve(populations=pop, parent_energy=parent_energy,
              parent_temperature=temperature, volume=volume, photoheat=heat,
              hubble=hubble, dt=dt)
        backend = m.JaxThermalBackend.from_repo(REPO)
        got = backend.solve(populations=pop, parent_energy=parent_energy,
              parent_temperature=temperature, volume=volume, photoheat=heat,
              hubble=hubble, dt=dt)
        assert np.array_equal(got.bracketed, ref.bracketed)
        residual = max(relmax(got.energy, ref.energy), relmax(got.temperature, ref.temperature),
                       relmax(got.rhs, ref.rhs))
        assert residual < 1.0e-11
        assert float(np.max(got.relative_residual)) <= 1.0e-10
        assert backend.root_compile_count == 1
        return {"case": case, "relative_residual": residual, "root_compile_count": 1}
    if case == "root_dt_compile":
        backend = m.JaxThermalBackend.from_repo(REPO)
        for factor in (1.0, 0.5, 0.25, 0.125, 0.0625):
            backend.solve(populations=pop, parent_energy=parent_energy,
                parent_temperature=temperature, volume=volume, photoheat=heat,
                hubble=hubble, dt=dt * factor)
        assert backend.root_compile_count == 1
        return {"case": case, "root_compile_count": 1}
    if case == "device_get_count":
        backend = m.JaxThermalBackend.from_repo(REPO)
        for factor in (1.0, 0.5, 0.25):
            backend.solve(populations=pop, parent_energy=parent_energy,
                parent_temperature=temperature, volume=volume, photoheat=heat,
                hubble=hubble, dt=dt * factor)
        assert backend.device_get_count == 3
        return {"case": case, "device_get_count": 3}
    if case == "metadata":
        backend = m.JaxThermalBackend.from_repo(REPO)
        assert backend.root_iterations == 41
        return {"case": case, "root_iterations": 41}
    raise ValueError(case)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=["balance_parity", "balance_dt_compile", "root_parity",
                        "root_dt_compile", "device_get_count", "metadata"])
    args = parser.parse_args()
    print(json.dumps(run(args.case), sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
