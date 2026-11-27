"""Isolated spherical-state archive adapter; no implicit eigensolve on read.

The scheduler owns task authorization, source/native pins, limits and DATA/RESULT
publication.  This module owns one create-only STATE.npz and its reconstruction.
Operators remain the independent hp-FEM angular generator and radial derivative.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from mpi_batch import atomic_create
from optimized_solver import PartialWaveState


def _configuration(configuration):
    if not isinstance(configuration, dict):
        raise ValueError("spherical configuration must be an object")
    required = {"R", "m", "lmax", "elements", "degree", "rmax", "quadrature",
                "nroots", "center", "tol"}
    allowed = required | {"ZA", "ZB", "maxiter", "boundaries"}
    if not required <= set(configuration) or not set(configuration) <= allowed:
        raise ValueError("missing or unsupported spherical configuration fields")
    p = dict(configuration)
    p.setdefault("ZA", 1.)
    p.setdefault("ZB", 2.)
    p.setdefault("maxiter", 2000)
    for name in ("R", "ZA", "ZB", "rmax", "tol"):
        value = p[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if p["R"] <= 0 or min(p["ZA"], p["ZB"]) < 0 or p["ZA"]+p["ZB"] <= 0:
        raise ValueError("invalid spherical physical parameters")
    if p["center"] != "B" or p["rmax"] <= p["R"] or not 0 < p["tol"] < 1:
        raise ValueError("requires B origin, enclosing positive box and legal tolerance")
    for name, lower in (("m", 0), ("lmax", 0), ("elements", 4), ("degree", 2),
                        ("quadrature", 1), ("nroots", 1), ("maxiter", 1)):
        if type(p[name]) is not int or p[name] < lower:
            raise ValueError(f"{name} must be integer >= {lower}")
    if (p["m"] not in (0, 1) or p["lmax"] < p["m"] or p["nroots"] != 2
            or p["quadrature"] < p["degree"]+2):
        raise ValueError("illegal sector, root count or quadrature")
    return p


def _phase(state):
    """Read-only reproduction of the parent positive meridional phase probe."""
    radius = max(0.1, min(1., float(state.boundaries[-1])/4))
    value = float(np.sum(state.evaluate(np.full(9, radius), np.linspace(-.8, .8, 9))[0]))
    if not math.isfinite(value) or value <= 0:
        raise ArithmeticError("archived state fails positive meridional phase convention")
    return value


def _validate_state(state, configuration):
    p = _configuration(configuration)
    if (state.R, state.ZA, state.ZB, state.m, state.degree) != (
            p["R"], p["ZA"], p["ZB"], p["m"], p["degree"]):
        raise ValueError("state and requested physical configuration differ")
    numbers = [state.energy, state.residual, state.mass_norm]
    if (not np.isfinite(numbers).all() or state.residual < 0 or state.residual > 1e-9
            or abs(state.mass_norm-1.) > 1e-10):
        raise ArithmeticError("fixed spherical residual/norm gate failed")
    ls, boundaries, coefficients = state.ls, state.boundaries, state.coefficients
    if (ls.dtype.kind not in "iu" or ls.ndim != 1
            or not np.array_equal(ls, np.arange(p["m"], p["lmax"]+1))):
        raise ValueError("archive angular indices disagree with configuration")
    if (boundaries.dtype != np.float64 or boundaries.ndim != 1 or len(boundaries) < 3
            or not np.isfinite(boundaries).all() or boundaries[0] != 0
            or boundaries[-1] != p["rmax"] or np.any(np.diff(boundaries) <= 0)
            or not np.any(boundaries == p["R"])):
        raise ValueError("archive has an invalid spherical radial partition")
    if (p.get("boundaries") is not None
            and not np.array_equal(boundaries, np.asarray(p["boundaries"]))):
        raise ValueError("archive radial partition differs from requested explicit boundaries")
    expected_shape = (len(ls), (len(boundaries)-1)*p["degree"]+1)
    if (coefficients.dtype != np.float64 or coefficients.shape != expected_shape
            or not np.isfinite(coefficients).all()
            or np.any(coefficients[:, (0, -1)] != 0.)):
        raise ValueError("archive coefficients violate finite-element shape or boundary conditions")
    meta = state.metadata
    shift = p["ZA"]*p["R"]/(p["ZA"]+p["ZB"])
    if (not isinstance(meta, dict) or meta.get("origin_center") != "B"
            or meta.get("origin_shift_center_to_O") != shift
            or meta.get("nuclear_positions") != [-p["R"], 0.]
            or meta.get("degree") != p["degree"]
            or meta.get("angular_lmax") != p["lmax"]
            or meta.get("rmax") != p["rmax"]
            or meta.get("explicit_boundaries") != boundaries.tolist()):
        raise ValueError("archive metadata and physical origin/basis disagree")
    return _phase(state)


def solve_one(configuration, output_dir, backend="native"):
    """Solve exactly one authorized state and atomically save STATE.npz."""
    p = _configuration(configuration)
    if backend not in ("native", "numpy"):
        raise ValueError("explicit spherical backend must be native or numpy")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    destination = output/"STATE.npz"
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    import optimized_solver
    state = optimized_solver.solve(**p, backend=backend)
    phase = _validate_state(state, p)
    stream = BytesIO()
    np.savez_compressed(stream, coefficients=state.coefficients,
                        ls=state.ls, boundaries=state.boundaries)
    raw = stream.getvalue()
    atomic_create(destination, raw)
    return {
        "energy": float(state.energy), "residual": float(state.residual),
        "mass_norm": float(state.mass_norm), "metadata": state.metadata,
        "phase_probe": phase, "backend": backend, "state_file": destination.name,
        "state_bytes": len(raw), "state_sha256": hashlib.sha256(raw).hexdigest(),
        "phase_convention": "parent positive nine-point meridional probe; coefficients unchanged",
    }


def _json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate archived JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def load_one(folder):
    """Read DATA.json and hash-bound state; never solve or evaluate operators."""
    folder = Path(folder)
    document = _json(folder/"DATA.json")
    parameters = document["parameters"]
    if not isinstance(parameters, dict) or parameters.get("kind") != "sphere":
        raise ValueError("requires a spherical DATA record")
    p = _configuration(parameters["configuration"])
    value = document["value"]
    if not isinstance(value, dict) or value.get("state_file") != "STATE.npz":
        raise ValueError("unsupported spherical state archive name")
    archive = folder/value["state_file"]
    if archive.is_symlink():
        raise ValueError("spherical state archive cannot be a symbolic link")
    raw = archive.read_bytes()
    if (type(value.get("state_bytes")) is not int or len(raw) != value["state_bytes"]
            or hashlib.sha256(raw).hexdigest() != value.get("state_sha256")):
        raise ValueError("spherical state archive size/SHA-256 mismatch")
    with np.load(BytesIO(raw), allow_pickle=False) as arrays:
        if set(arrays.files) != {"coefficients", "ls", "boundaries"}:
            raise ValueError("unexpected spherical archive members")
        state = PartialWaveState(p["R"], p["ZA"], p["ZB"], p["m"], arrays["ls"],
                                 arrays["boundaries"], p["degree"], arrays["coefficients"],
                                 value["energy"], value["residual"], value["mass_norm"],
                                 value["phase_probe"], value["metadata"])
    phase = _validate_state(state, p)
    if (not isinstance(value["phase_probe"], (int, float))
            or not math.isfinite(value["phase_probe"])
            or not math.isclose(phase, value["phase_probe"], rel_tol=1e-12, abs_tol=1e-14)):
        raise ValueError("archived spherical phase probe differs from coefficients")
    state.phase_probe = phase
    return state


def observe_pair(leftdir, rightdir, orders=(14, 22, 30)):
    """Reconstruct g,b and independently evaluate direct operators per order."""
    if (not isinstance(orders, (list, tuple)) or not orders
            or any(type(order) is not int or order < 1 for order in orders)
            or any(a >= b for a, b in zip(orders[:-1], orders[1:]))):
        raise ValueError("orders must be a strictly increasing sequence of positive integers")
    g, b = load_one(leftdir), load_one(rightdir)
    from fast_observables import direct_observables
    records = {}
    for order in orders:
        direct = direct_observables(g, b, quadrature=order)
        local = direct["L_center_over_minus_i_hbar"]
        lever = direct["origin_shift_center_to_O"]*direct["p_x_over_minus_i_hbar"]
        total = direct["L_O_over_minus_i_hbar"]
        absolute_sum = abs(local)+abs(lever)
        if not np.isfinite([local, lever, total, direct["dipole_x"]]).all():
            raise ArithmeticError("nonfinite spherical direct observable")
        records[str(order)] = {
            **direct, "L_B_bar": local, "origin_lever_bar": lever,
            "L_O_bar": total, "L_O_scaled": total/g.R**3,
            "Q_O": total/g.R, "Q_B": -g.R**2*local,
            "cancellation_absolute_sum": absolute_sum,
            "cancellation_condition": absolute_sum/abs(total) if total != 0. else None,
            "zero_total": total == 0.,
        }
    identities = []
    for folder in (Path(leftdir), Path(rightdir)):
        value = _json(folder/"DATA.json")["value"]
        identities.append({"folder": str(folder.resolve()),
                           "data_sha256": hashlib.sha256((folder/"DATA.json").read_bytes()).hexdigest(),
                           "state_sha256": value["state_sha256"], "state_bytes": value["state_bytes"]})
    return {"R": g.R, "sectors": [g.m, b.m], "energies": [g.energy, b.energy],
            "phase_probes": [g.phase_probe, b.phase_probe], "direct": records,
            "states": identities, "new_eigensolves": 0,
            "operator_lane": "independent spherical angular generator plus radial-derivative momentum",
            "claim_scope": "frozen finite-basis direct integrals; no continuum or asymptotic certificate"}
