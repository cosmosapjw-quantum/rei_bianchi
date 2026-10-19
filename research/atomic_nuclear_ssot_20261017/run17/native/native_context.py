"""RUN17 first-birth restriction of the unchanged RUN13 native coupled RHS.

The 265 coordinates are five affine invariant gas coordinates, the 252 active
optical depths, four fresh local photo-absorption integrals, and four local
photo-heating integrals.  Future depths remain exactly zero until their births.
No old full transport ledger is reconstructed.  Loading this module/context
does not start a native process or run an ODE.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"
import numpy as np

GAS_SHA256 = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"
PACKET_SHA256 = "67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a"
POINT_SHA256 = "385f61f57b5d314dbf69d2111f5576bf4be09fc0d94f67682eeb7a95daf25515"
PREFIX_C_SHA256 = "69cd9e459991fa7f0bf1ed6fed12bedbadffc1b5451ad0b8a380235e8f8813eb"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_identity(path):
    p = Path(path)
    return {"path": str(p.resolve()), "bytes": p.stat().st_size, "sha256": sha256(p)}


def save_json(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


class Context:
    def __init__(self, source_root, run16_root):
        self.source_root = Path(source_root).resolve()
        self.run16_root = Path(run16_root).resolve()
        point_path = self.run16_root / "feedback/execution01/RECORDED_STATE_FEEDBACK.json"
        prefix_path = self.run16_root / "feedback/prefix_stephalf_execution01/PREFIX_STEP_HALVING.json"
        if sha256(point_path) != POINT_SHA256 or sha256(prefix_path) != PREFIX_C_SHA256:
            raise ValueError("frozen RUN16 point/prefix-C identity mismatch")
        self.point = json.loads(point_path.read_text())
        self.prefix = json.loads(prefix_path.read_text())
        self.verify_original_sources()
        packet_path = self.source_root / "inputs/spectral11/m2.json"
        events_path = self.source_root / "inputs/spectral11/m2_events.json"
        if sha256(packet_path) != PACKET_SHA256:
            raise ValueError("different original M2 packet")
        packet = json.loads(packet_path.read_text())
        events = json.loads(events_path.read_text())
        if events["packet_sha256"] != PACKET_SHA256:
            raise ValueError("event identity belongs to another packet")
        sys.path.insert(0, str(self.source_root / "scripts"))
        self.native = importlib.import_module("retarded_integrator")
        sided = importlib.import_module("spectral_joint11")
        if (Path(self.native.ROOT).resolve() != self.source_root or
                Path(sided.R).resolve() != self.source_root):
            raise ValueError("original module imported from a different checkout")
        self.model = sided.SpectralModel(self.native.coalesce_reflections(packet))
        births = np.unique(self.model.birth)
        self.left, self.right = map(float, births[:2])
        if [self.left, self.right] != [0.004989333151072248, 0.02371416180174271]:
            raise ValueError("unexpected first two births")
        if any(self.left < float(p) < self.right for p in events["points"]):
            raise ValueError("selected panel contains another event")
        self.active = int(np.searchsorted(self.model.birth, self.left, side="right"))
        self.cells = sorted(set(self.model.coh[:self.active, 7].astype(int).tolist()))
        if self.active != 252 or self.cells != list(range(48)):
            raise ValueError("first birth must retain all 48 cells and 252 reflection pairs")
        physical = np.asarray(packet["cohorts"])
        self.physical_active = int(np.count_nonzero(physical[:, 0] == physical[0, 0]))
        if self.physical_active != 2 * self.active:
            raise ValueError("reflection source count mismatch")
        self.model.set_interval(self.left, self.right, self.active)
        self.pick = np.array([2, 4, 11, 12, 13])
        n = self.point["coordinate_normalizations"]
        self.scale = np.array([n["H_per_initial_H"], n["D_per_initial_H"],
            n["He_per_initial_H"], n["He_per_initial_H"], n["initial_thermal_eV_per_H"]])
        self.lift = np.asarray(self.point["lift_matrix_to_original_gas_14"], dtype=float)
        self.gas0 = self.model.y0[:14].copy()
        self.q0 = self.gas0[self.pick] / self.scale
        self.q_initial = np.asarray(self.prefix["sample_q"][-1], dtype=float)
        gas_prefix = np.asarray(self.prefix["sample_gas_14"][-1], dtype=float)
        if (self.prefix["sample_z"][-1] != self.left or
                not np.array_equal(self.gas_from_q(self.q_initial), gas_prefix)):
            raise ValueError("prefix-C physical input cannot be reconstructed exactly")
        self.depth_slice = slice(5, 5 + self.active)
        self.absorption_slice = slice(5 + self.active, 9 + self.active)
        self.heat_slice = slice(9 + self.active, 13 + self.active)
        self.dimension = 13 + self.active
        self.initial = np.zeros(self.dimension)
        self.initial[:5] = self.q_initial
        self.source_population = self.model.B[:self.active].copy()
        self.photonscale = self.model.nh * self.model.a0**3
        self.identity = {
            "packet": file_identity(packet_path), "events": file_identity(events_path),
            "run16_point": file_identity(point_path), "run16_prefix_C": file_identity(prefix_path),
            "source_manifest": file_identity(self.source_root / "SHA256SUMS.txt"),
            "verified_source_input_files": self.point["verified_source_input_files"],
            "context_code": file_identity(__file__),
        }

    def verify_original_sources(self):
        if sha256(self.source_root / "SHA256SUMS.txt") != self.point["original_manifest_sha256"]:
            raise ValueError("original source manifest identity mismatch")
        for relative, info in self.point["verified_source_input_files"].items():
            if sha256(self.source_root / relative) != info["sha256"]:
                raise ValueError(f"original source/input changed: {relative}")

    def gas_from_q(self, q):
        """Affine original-nuclei lift; scalar or leading sample axes allowed."""
        q = np.asarray(q, dtype=float)
        if q.shape[-1:] != (5,):
            raise ValueError("five gas coordinates required")
        return self.gas0 + np.einsum("ij,...j->...i", self.lift, q-self.q0)

    def temperature(self, gas):
        gas = np.asarray(gas)
        return 2*gas[..., 13]*self.native.EV_J / (
            3*self.native.KB*(gas[..., :13] @ (1+self.native.CHARGE)))

    def photo_parts(self, z, q, depths):
        """Unchanged section-mask ray opacity, all four absorbers and heating."""
        if not self.left <= z <= self.right:
            raise ValueError("outside first-birth panel")
        gas = self.gas_from_q(q)
        depths = np.asarray(depths, dtype=float)
        if gas.shape != (14,) or depths.shape != (self.active,):
            raise ValueError("scalar gas and complete active depths required")
        if (not np.isfinite(gas).all() or not np.isfinite(depths).all() or
                (gas[:13] < 0).any() or gas[13] <= 0):
            raise ValueError("nonphysical gas state; no clipping")
        energy, de, hubble, a = self.model.rays(float(z), self.active)
        volume = (a/self.model.a0)**3
        sigma = self.model.section_sigma(energy)
        density = gas[:13]*self.model.nh/volume
        hazard = self.native.C*self.model.dx/hubble*sigma*density[self.native.LO][None, :]
        population = self.source_population*np.exp(-depths)
        events = hazard*population[:, None]
        net = events.sum(axis=0)
        heat = (events*(energy[:, None]-self.model.chi)).sum(axis=0)
        photo = np.zeros(14)
        np.add.at(photo, self.native.LO, -net)
        np.add.at(photo, self.native.UP, net)
        photo[13] = heat.sum()
        return {"gas": gas, "energy": energy, "de_dX": de,
            "hubble": float(hubble), "a": float(a), "volume": float(volume),
            "sigma": sigma, "hazard": hazard, "population": population,
            "tau_rate": hazard.sum(axis=1), "net_absorption_rate": net,
            "net_heat_rate": heat, "photo_gas_rate_14": photo}

    def rhs_parts(self, z, state, native_callable):
        """One native call; callable(proper14, tcmb_K, mask=7) returns payload28.

        Returns `rhs` in the 265-coordinate order and separate physical blocks.
        The callable owns its count, trace, binary identity and resource budget.
        """
        state = np.asarray(state, dtype=float)
        if state.shape != (self.dimension,) or not np.isfinite(state).all():
            raise ValueError("finite complete reduced state required")
        part = self.photo_parts(z, state[:5], state[self.depth_slice])
        proper = part["gas"]*self.model.gscale[:14]/part["volume"]
        tcmb = 2.7255/part["a"]
        raw = np.asarray(native_callable(proper, tcmb, mask=7), dtype=float)
        if raw.shape != (28,) or not np.isfinite(raw).all():
            raise ValueError("native payload must contain 28 finite values")
        native_rate = self.model.dx*part["volume"]/part["hubble"]*raw[:14]/self.model.gscale[:14]
        native_rate[13] -= 2*self.model.dx*part["gas"][13]
        gas_rate = native_rate + part["photo_gas_rate_14"]
        rhs = np.zeros(self.dimension)
        rhs[:5] = gas_rate[self.pick]/self.scale
        rhs[self.depth_slice] = part["tau_rate"]
        rhs[self.absorption_slice] = part["net_absorption_rate"]
        rhs[self.heat_slice] = part["net_heat_rate"]
        part.update(rhs=rhs, gas_rate_14=gas_rate, native_gas_rate_14=native_rate,
            native_payload_28=raw, proper_state_14=proper, tcmb_K=float(tcmb))
        return part

    def input_record(self):
        return {"schema": "rei.run17.first-birth-input.v1", "identity": self.identity,
            "source_root": str(self.source_root), "run16_root": str(self.run16_root),
            "code_z": "(X-0.7)/(0.7004-0.7); integration coordinate, not cosmological redshift",
            "interval_z": [self.left, self.right],
            "endpoint_sides": ["outgoing after first activation", "incoming before second activation"],
            "physical_source_rows": self.physical_active, "active_reflection_pairs": self.active,
            "spectral_cells": self.cells, "total_original_physical_source_rows": 80640,
            "total_original_reflection_pairs": self.model.m,
            "original_full_dimension": self.model.dim, "dimension": self.dimension,
            "state_layout": {"q": [0, 5], "tau": [5, 5+self.active],
                "local_absorption_H_HeI_HeII_D": [5+self.active, 9+self.active],
                "local_heat_H_HeI_HeII_D": [9+self.active, 13+self.active]},
            "coordinates": self.point["coordinates"], "q_scale": self.scale.tolist(),
            "lift_14_by_5": self.lift.tolist(), "gas_original_initial_14": self.gas0.tolist(),
            "q_original_initial_5": self.q0.tolist(), "reduced_initial_state": self.initial.tolist(),
            "first_birth_gas_14": self.gas_from_q(self.q_initial).tolist(),
            "first_birth_T_K": float(self.temperature(self.gas_from_q(self.q_initial))),
            "first_birth_population_per_initial_H": self.source_population.tolist(),
            "photonscale_to_comoving_m3": float(self.photonscale),
            "local_ledger_origin": "zero absorption/heating immediately after first activation; no previous global ledgers inferred",
            "full_transport_restart": False, "prefix_initial_error": "RUN16 prefix C numerical input; no rigorous enclosure supplied"}


def load_context(source_root, run16_root):
    return Context(source_root, run16_root)


class TracedNative:
    """One explicit binary process, finite trace and shared call/time cap."""
    def __init__(self, context, binary, trace_path, call_cap=500, wall_cap=20.0):
        self.context = context
        self.binary = Path(binary).resolve()
        if sha256(self.binary) != GAS_SHA256:
            raise ValueError("original native executable identity mismatch")
        if not 0 < call_cap <= 1000 or not 0 < wall_cap <= 20:
            raise ValueError("bounded native caps required")
        self.trace_path = Path(trace_path)
        self.call_cap, self.wall_cap = call_cap, wall_cap
        self.calls, self.native_wall = 0, 0.0

    def __enter__(self):
        self.trace = self.trace_path.open("x")
        self.server = self.context.native.GasServer(path=self.binary)
        self.server.__enter__()
        self.started = time.perf_counter()
        return self

    def callable(self, z, purpose):
        def invoke(proper, tcmb, mask=7):
            if self.calls >= self.call_cap or time.perf_counter()-self.started > self.wall_cap:
                raise TimeoutError("RUN17 native call/wall cap reached")
            before = time.perf_counter()
            raw = self.server.rhs(proper, tcmb, mask=mask)
            self.native_wall += time.perf_counter()-before
            self.calls += 1
            self.trace.write(json.dumps({"call": self.calls, "purpose": purpose, "z": float(z),
                "mask": mask, "tcmb_K": float(tcmb), "proper_state_14": np.asarray(proper).tolist(),
                "native_payload_28": raw.tolist()}, allow_nan=False)+"\n")
            return raw
        return invoke

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.server.calls != self.calls:
                raise AssertionError("native protocol count mismatch")
        finally:
            self.server.__exit__(exc_type, exc, tb)
            self.trace.close()
