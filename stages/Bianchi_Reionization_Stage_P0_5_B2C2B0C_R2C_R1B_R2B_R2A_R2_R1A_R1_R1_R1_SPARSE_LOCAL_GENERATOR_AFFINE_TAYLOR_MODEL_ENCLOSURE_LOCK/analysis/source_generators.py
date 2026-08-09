"""Exact node-local branch generators for the locked full-OTS source operator."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import sys
from pathlib import Path

import numpy as np

ELL = 57.0 / 40.0
M_CAS = 737.0 / 1000.0
F_CENTER = 0.55
F_HALF_WIDTH = 0.45
EV_ERG = 1.602176634e-12
HEII_LYA_EV = 40.81332
CHI_H_EV = 13.598434599702
CHI_HEI_EV = 24.587389011


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class SourceRHSTaylor:
    model: object
    population_linear: np.ndarray
    population_mixed: np.ndarray
    node_count: int
    robust_rank2_nodes: int
    rank1_nodes: int
    rank_lower_bound: int
    below_table_nodes: int
    table_event_distance_logT: np.ndarray
    minimum_table_event_distance_logT: float
    v_center: np.ndarray
    v_half_width: np.ndarray
    y: np.ndarray
    z: np.ndarray
    w: np.ndarray
    cascade_rate: np.ndarray
    n_h: np.ndarray
    n_he: np.ndarray
    q_he: np.ndarray
    r_heiii: np.ndarray
    particles: np.ndarray
    energy: np.ndarray

    def evaluate_local_rhs(self, *, nodes, theta_v: float, theta_f: float) -> np.ndarray:
        index = np.asarray(nodes, dtype=int)
        return np.ascontiguousarray(
            self.model.center[:, index]
            + self.model.local_linear[0][:, index] * float(theta_v)
            + self.model.local_linear[1][:, index] * float(theta_f)
            + self.model.local_mixed[:, index] * float(theta_v) * float(theta_f)
        )

    def evaluate_direct_local_rhs(self, *, nodes, theta_v: float, theta_f: float) -> np.ndarray:
        index = np.asarray(nodes, dtype=int)
        tv = float(theta_v)
        tf = float(theta_f)
        v = self.v_center[index] + self.v_half_width[index] * tv
        f = F_CENTER + F_HALF_WIDTH * tf
        y = self.y[index]
        z = self.z[index]
        w = self.w[index]
        rate = self.cascade_rate[index]
        ah = v * w + (1.0 - v) * f * z
        ae = v * M_CAS * (1.0 - y) + (1.0 - v) * f * (1.0 - z)
        vc = self.v_center[index]
        ahc = vc * w + (1.0 - vc) * F_CENTER * z
        aec = vc * M_CAS * (1.0 - y) + (1.0 - vc) * F_CENTER * (1.0 - z)
        dah = ah - ahc
        dae = ae - aec
        delta = np.zeros((4, len(index)), dtype=np.float64)
        delta[0] = -rate * dah / self.n_h[index]
        delta[1] = -rate * dae / self.n_he[index]
        delta[2] = -self.r_heiii[index] * rate * dae / (self.n_he[index] * self.q_he[index])
        excess = z * (HEII_LYA_EV - CHI_H_EV) + (1.0 - z) * (HEII_LYA_EV - CHI_HEI_EV)
        heat = rate * ((1.0 - v) * f - (1.0 - vc) * F_CENTER) * excess * EV_ERG
        delta[3] = heat / self.energy[index] - rate * (dah + dae) / self.particles[index]
        return np.ascontiguousarray(self.model.center[:, index] + delta)


def _table_event_distance(log_temperature: np.ndarray) -> np.ndarray:
    knots = np.log(10.0 ** np.arange(4.0, 5.0000001, 0.25))
    values = np.asarray(log_temperature, dtype=np.float64)
    return np.min(np.abs(values[:, None] - knots[None, :]), axis=1)


def build_source_rhs_taylor(repo_root: Path) -> SourceRHSTaylor:
    repo = Path(repo_root).resolve()
    stage = Path(__file__).resolve().parents[1]
    sparse = _load("sparse_local_model_runtime", stage / "analysis/sparse_local_model.py")
    interval_stage = next(repo.glob("stages/*R2_R1A_R1_VALIDATED_CONTINUOUS*"))
    rim = _load("sparse_local_reduced_interval_model", interval_stage / "analysis/reduced_interval_rhs.py")
    rank_stage = next(repo.glob("stages/*R2_R1A_R1_R1_AFFINE_SET*"))
    rank_mod = _load("sparse_local_rank_oracle", rank_stage / "analysis/branch_rank.py")

    reduced = rim.ReducedIntervalModel.from_repo(repo)
    coordinates = reduced.initial_coordinates()
    state = reduced.coordinates_to_state(coordinates)
    point = reduced.solver.forcing.point(interval=0, time_s=0.0)
    owner = reduced.solver._owner(state, point)
    photo = reduced.solver.backend.photo_fields(owner)
    volume = reduced.inputs.comoving_volume_cm3 / (1.0 + point.z) ** 3
    vlo = np.asarray(reduced.policy.build_v_field_from_temperature("CELL_LOWER_STRICT", state.temperature_K), dtype=np.float64)
    vhi = np.asarray(reduced.policy.build_v_field_from_temperature("CELL_UPPER_STRICT", state.temperature_K), dtype=np.float64)
    vc = 0.5 * (vlo + vhi)
    vh = 0.5 * (vhi - vlo)
    event = reduced.event.evaluate_event_flux(
        populations=state.values[:5].T,
        temperature_K=state.temperature_K,
        proper_volume_cm3=volume,
        photo_hi=photo.HI,
        photo_hei=photo.HeI,
        photo_heii=photo.HeII,
        v=vc,
        f=np.full(state.node_count, F_CENTER),
    )
    y = np.asarray(event.branches["y"], dtype=np.float64)
    z = np.asarray(event.branches["z"], dtype=np.float64)
    w = np.asarray(event.branches["w"], dtype=np.float64)
    rate = np.asarray(event.event_rates["HEIII_CASCADE"], dtype=np.float64)

    ah_v = vh * (w - F_CENTER * z)
    ah_f = F_HALF_WIDTH * (1.0 - vc) * z
    ah_vf = -vh * F_HALF_WIDTH * z
    ae_v = vh * (M_CAS * (1.0 - y) - F_CENTER * (1.0 - z))
    ae_f = F_HALF_WIDTH * (1.0 - vc) * (1.0 - z)
    ae_vf = -vh * F_HALF_WIDTH * (1.0 - z)

    ah = np.stack([ah_v, ah_f], axis=0)
    ae = np.stack([ae_v, ae_f], axis=0)
    population_linear = np.zeros((2, 5, state.node_count), dtype=np.float64)
    population_linear[:, 0] = -rate[None, :] * ah
    population_linear[:, 1] = rate[None, :] * ah
    population_linear[:, 2] = -rate[None, :] * ae
    population_linear[:, 3] = rate[None, :] * ae
    population_mixed = np.zeros((5, state.node_count), dtype=np.float64)
    population_mixed[0] = -rate * ah_vf
    population_mixed[1] = rate * ah_vf
    population_mixed[2] = -rate * ae_vf
    population_mixed[3] = rate * ae_vf

    n_h = reduced.n_h
    n_he = reduced.n_he
    x_hei = coordinates[1]
    q_he = 1.0 - x_hei
    r_heiii = coordinates[2]
    pop = state.values[:5].T
    particles = n_h + n_he + pop[:, 1] + pop[:, 3] + 2.0 * pop[:, 4]
    energy = state.values[5]

    local = np.zeros((2, 4, state.node_count), dtype=np.float64)
    mixed = np.zeros((4, state.node_count), dtype=np.float64)
    local[:, 0] = population_linear[:, 0] / n_h[None, :]
    local[:, 1] = population_linear[:, 2] / n_he[None, :]
    local[:, 2] = -r_heiii[None, :] * (rate[None, :] * ae) / (n_he[None, :] * q_he[None, :])
    mixed[0] = population_mixed[0] / n_h
    mixed[1] = population_mixed[2] / n_he
    mixed[2] = -r_heiii * (rate * ae_vf) / (n_he * q_he)

    excess = z * (HEII_LYA_EV - CHI_H_EV) + (1.0 - z) * (HEII_LYA_EV - CHI_HEI_EV)
    heat_v = rate * (-vh * F_CENTER) * excess * EV_ERG
    heat_f = rate * ((1.0 - vc) * F_HALF_WIDTH) * excess * EV_ERG
    heat_vf = rate * (-vh * F_HALF_WIDTH) * excess * EV_ERG
    particle_v = rate * (ah_v + ae_v)
    particle_f = rate * (ah_f + ae_f)
    particle_vf = rate * (ah_vf + ae_vf)
    local[0, 3] = heat_v / energy - particle_v / particles
    local[1, 3] = heat_f / energy - particle_f / particles
    mixed[3] = heat_vf / energy - particle_vf / particles

    center = reduced.floating_reference_rhs(coordinates=coordinates, time_s=0.0, v=vc, f=F_CENTER)
    audit = rank_mod.audit_source_safe_rank(repo)
    model = sparse.SparseLocalTaylorModel(
        center=center,
        local_linear=local,
        local_mixed=mixed,
        global_generators=np.empty((0, 4, state.node_count)),
        remainder_lo=np.zeros_like(center),
        remainder_hi=np.zeros_like(center),
        coordinate_names=("x_HI", "x_HeI", "r_HeIII", "log_T"),
        local_rank_hint=audit.source_safe_rank_lower_bound,
    )
    event_distance = _table_event_distance(coordinates[3])
    return SourceRHSTaylor(
        model=model,
        population_linear=np.ascontiguousarray(population_linear),
        population_mixed=np.ascontiguousarray(population_mixed),
        node_count=state.node_count,
        robust_rank2_nodes=audit.robust_rank2_nodes,
        rank1_nodes=audit.rank1_remainder_nodes,
        rank_lower_bound=audit.source_safe_rank_lower_bound,
        below_table_nodes=audit.below_table_nodes,
        table_event_distance_logT=np.ascontiguousarray(event_distance),
        minimum_table_event_distance_logT=float(np.min(event_distance)),
        v_center=np.ascontiguousarray(vc),
        v_half_width=np.ascontiguousarray(vh),
        y=np.ascontiguousarray(y),
        z=np.ascontiguousarray(z),
        w=np.ascontiguousarray(w),
        cascade_rate=np.ascontiguousarray(rate),
        n_h=np.ascontiguousarray(n_h),
        n_he=np.ascontiguousarray(n_he),
        q_he=np.ascontiguousarray(q_he),
        r_heiii=np.ascontiguousarray(r_heiii),
        particles=np.ascontiguousarray(particles),
        energy=np.ascontiguousarray(energy),
    )


__all__ = ["SourceRHSTaylor", "build_source_rhs_taylor"]
