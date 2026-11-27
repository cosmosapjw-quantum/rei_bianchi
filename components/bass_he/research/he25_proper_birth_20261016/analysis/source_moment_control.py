"""Read-only HE25 source quadrature control; no native or evolution solver calls.

Reproduce only the reviewed fixed-grid construction, bypass Model.__init__,
and compare Model.source against direct quadrature in the current birth frame.
Existing run ledgers provide accumulated source energy; no runs are repeated.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve()
SRC = HERE.parents[1] / "src"
CHECKOUT = HERE.parents[3]
sys.path.insert(0, str(SRC))
import physics

EXPECTED_PHYSICS = "6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden_solver(*args, **kwargs):
    raise RuntimeError("SOURCE_CONTROL_FORBIDS_EVOLUTION_SOLVERS")


def reference_moments(order):
    z, w = np.polynomial.legendre.leggauss(order)
    energy = (100.0 + 13.6) / 2 + (100.0 - 13.6) * z / 2
    density = physics.shape(energy)
    norm = float(np.dot(w, density) * (100.0 - 13.6) / 2)
    mean = float(np.dot(w, density * energy) / np.dot(w, density))
    return {"order": order, "unnormalized_integral": norm, "mean_energy_eV": mean}


def grid_only(m, q, angles=4):
    # This is the reviewed grid construction from physics.py:37-49 only.
    # Model.__init__ would build an ODE clock and is deliberately never called.
    model = physics.Model.__new__(physics.Model)
    model.q = q
    model.source_per_x = 1.0
    model._source_mask = None
    model.x = lambda x: x
    model.H = lambda x: 1.0  # Cancels from all normalized source moments.
    mus, mw = np.polynomial.legendre.leggauss(angles)
    eg, ew = np.polynomial.legendre.leggauss(4)
    energy, directions, weights = [], [], []
    narrow_panels = 0
    for mu, aw in zip(mus, mw / 2):
        g = model.factor(physics.X_END, mu)
        bounds = sorted(set([13.6, 24.59, 54.42, 100.0,
                             13.6 / g, 24.59 / g, 54.42 / g, 100.0 / g]))
        for lo, hi in zip(bounds[:-1], bounds[1:]):
            parts = m if hi / lo > 1.01 else 1
            narrow_panels += int(hi / lo <= 1.01)
            edges = np.geomspace(lo, hi, parts + 1)
            for a, b in zip(edges[:-1], edges[1:]):
                energy.extend((a + b) / 2 + (b - a) * eg / 2)
                directions.extend([mu] * len(eg))
                weights.extend(ew * (b - a) / 2 * aw)
    model.Eref = np.array(energy)
    model.mu0 = np.array(directions)
    model.weights = np.array(weights)
    return model, narrow_panels


def control(runtime):
    physics_path = Path(physics.__file__).resolve()
    if sha(physics_path) != EXPECTED_PHYSICS:
        raise RuntimeError("REVIEWED_PHYSICS_IDENTITY_CHANGED")
    physics.solve_ivp = forbidden_solver
    references = [reference_moments(order) for order in (128, 256)]
    reference = references[-1]
    stability = abs(references[0]["mean_energy_eV"] - reference["mean_energy_eV"])
    if stability > 1e-11:
        raise RuntimeError("DIRECT_MOMENT_REFERENCE_UNSTABLE")
    samples = []
    for q in (-0.005, 0.0, 0.005):
        for m in (4, 8, 16):
            model, narrow_panels = grid_only(m, q)
            for fraction in (0.0, 0.1, 0.37, 0.5, 0.9, 1.0):
                x = fraction * physics.X_END
                source = model.source(x)
                g = model.factor(x, model.mu0)
                energy = model.Eref * g
                mu = model.mu0 * np.exp(-(1 - 2 * q) * x) / g
                mask = (energy >= 13.6) & (energy <= 100.0)
                raw = model.weights * physics.shape(energy) * np.exp(-3 * x) / g**2 * mask
                mean = float(np.dot(source, energy) / source.sum())
                samples.append({
                    "q": q, "m": m, "angles": 4, "x_fraction": fraction,
                    "photon_modes": len(model.Eref), "narrow_panels": narrow_panels,
                    "gauss_nodes_per_narrow_panel": 4,
                    "normalized_source_total": float(source.sum()),
                    "raw_integral_relative_error": float(raw.sum() / reference["unnormalized_integral"] - 1),
                    "mean_energy_eV": mean,
                    "mean_energy_error_eV": mean - reference["mean_energy_eV"],
                    "mean_mu": float(np.dot(source, mu) / source.sum()),
                    "mean_mu2_error": float(np.dot(source, mu * mu) / source.sum() - 1 / 3),
                })
    accumulated = []
    paths = [*sorted((runtime / "temporal").glob("*/RESULT.json")),
             *sorted((runtime / "resolution").glob("*/RESULT.json")),
             *sorted((runtime / "references_final").glob("*.json"))]
    for path in paths:
        record = json.loads(path.read_text())
        result = record.get("result", {})
        if "ledger" not in result:
            continue
        ledger = result["ledger"]
        count, energy = ledger["birth_n"], ledger["birth_e"]
        if count <= 0:
            raise RuntimeError("NONPOSITIVE_RECORDED_SOURCE_COUNT")
        accumulated.append({
            "path": str(path), "sha256": sha(path), "status": record.get("status"),
            "q": result["q"], "m": result["m"], "angles": result["angles"],
            "method": result["metadata"]["method"], "birth_n_per_H": count,
            "birth_e_eV_per_H": energy,
            "mean_birth_energy_error_eV": energy / count - reference["mean_energy_eV"],
            "accumulated_source_energy_bias_eV_per_H": energy - count * reference["mean_energy_eV"],
        })
    return {
        "scope": "algebra and source quadrature only; existing ledgers read without rerun",
        "independence": "direct birth-frame moment quadrature versus reviewed fixed Killing-grid source",
        "classification": "moving-edge spectral refinement remains untested by m alone; temporal evidence retained",
        "identities": {
            "analysis_sha256": sha(HERE), "physics_sha256": sha(physics_path),
            "he21_photo_sha256": sha(Path(sys.modules["he21_photo"].__file__).resolve()),
        },
        "reference_method": "Gauss-Legendre integration of shape(E) on [13.6,100] eV",
        "direct_birth_frame_references": references,
        "reference_mean_stability_eV": stability,
        "samples": samples,
        "accumulated_source_comparisons": accumulated,
        "interpretation": "Instantaneous source-shape error and accumulated source-energy bias are distinct; neither is a derived bound on the gas endpoint error.",
    }


def atomic_create(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("x") as f:
        json.dump(payload, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.link(temporary, path)
    temporary.unlink()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = control(args.runtime.resolve())
    atomic_create(args.out.resolve(), result)
    print(json.dumps({"out": str(args.out.resolve()), "samples": len(result["samples"]),
                      "existing_records": len(result["accumulated_source_comparisons"]),
                      "reference_mean_stability_eV": result["reference_mean_stability_eV"]}))
