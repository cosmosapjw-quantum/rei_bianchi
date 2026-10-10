#!/usr/bin/env python3
"""Production P01 conditional interval using frozen providers and initial data.

The interval state machine, stage assembly and acceptance comparison live here;
the production Rust crate owns the atomic/source/opacity/AXI RHS. Only the two
hash-checked table/background providers are imported from the research packet.
No research interval executable, RHS, solver or stored later state is consumed
by this integration. Historical states are opened separately after integration.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp

CRATE = Path(__file__).resolve().parents[1]
REPOSITORY = CRATE.parents[1]
DEFAULT_PACKET = REPOSITORY / "research/physical_provider_20261010"
EV, KB, C = 1.602176634e-12, 1.380649e-16, 29979245800.0
CHI = np.array([13.598434599702, 24.587389011, 54.41776])
CLOSURE = "HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE"
# Order is shared with the production Rust binding protocol. These are source
# identities, not claims about continuum error or scientific admission.
FROZEN_INPUTS = {
    "CONTRACT.json": "2f5f118b856a47fa339a510a58e7221e7d7ab3ea3a38625d2c61e9b93380ed6d",
    "background.py": "b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d",
    "hm12_data.py": "ede512206bd6f5acc85b1c6b90fda4edc256b4dd8a70c42f9726932b6bff5121",
    "sources/UVB.out": "a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc",
    "sources/emissivity.out": "88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b",
    "evidence/extended_dataset.npz": "3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be",
}
REFERENCE_JSON_SHA = "f1ef5e09495df872e705656ff8d1252376c230e860ccbb882e3527b17e41a24b"


def verify_bytes(path: Path, expected: str) -> str:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"IMMUTABLE_INPUT_SHA_MISMATCH: {path}: {actual}")
    return actual


def preflight(packet: Path) -> dict:
    identities = {name: verify_bytes(packet / name, digest)
                  for name, digest in FROZEN_INPUTS.items()}
    contract = json.loads((packet / "CONTRACT.json").read_text())
    if contract["closure"]["id"] != CLOSURE:
        raise ValueError("CONDITIONAL_CLOSURE_IDENTITY")
    return {"identities": identities, "contract": contract}


def load_provider(packet: Path, filename: str):
    # Exact provider byte checks precede import. Distinct module names avoid
    # accidentally using a provider already imported from another directory.
    name = "rei_p01_" + Path(filename).stem
    spec = importlib.util.spec_from_file_location(name, packet / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class NativeConsumer:
    def __init__(self, binary: Path, identities: dict):
        self.proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, bufsize=1)
        self.calls = {"BIND": 0, "SIGMA": 0, "RHS": 0}
        self.exchange("BIND", " ".join(identities.values()), 1)

    def exchange(self, command: str, payload: str, count: int):
        self.calls[command] += 1
        if self.calls.get("RHS", 0) > 10000:
            raise RuntimeError("CONDITIONAL_RHS_CALL_LIMIT")
        self.proc.stdin.write(command + " " + payload + "\n")
        self.proc.stdin.flush()
        response = self.proc.stdout.readline().strip()
        if not response.startswith("OK "):
            raise RuntimeError(f"PRODUCTION_{command}: {response!r}")
        tokens = response[3:].split()
        values = np.asarray([float(token) for token in tokens])
        if len(values) != count or not np.isfinite(values).all():
            raise RuntimeError("PRODUCTION_RESPONSE_SHAPE_OR_FINITE")
        return values

    def call(self, command, values, count):
        return self.exchange(command, " ".join(format(float(v), ".17e") for v in values), count)

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=10)
        error = self.proc.stderr.read()
        if self.proc.returncode != 0:
            raise RuntimeError(f"PRODUCTION_EXIT_{self.proc.returncode}: {error}")


def characteristics(q, mu0, geometry):
    b, a = geometry["b"], geometry["a_rel"]
    ratio = np.sqrt((1 - mu0**2) * np.exp(2*b) + mu0**2 * np.exp(-4*b)) / a
    return q * ratio, mu0 * np.exp(-2*b) / (a * ratio), ratio


class ProductionInterval:
    def __init__(self, packet, verified, consumer):
        self.consumer = consumer
        contract = verified["contract"]
        p = contract["background"]
        self.background = load_provider(packet, "background.py").BianchiBackground(
            r=p["initial_s_over_H"], z_i=p["initial_redshift_label"],
            Hfid_km_s_Mpc=p["Hfid_km_s_Mpc"], omega_m=p["Omega_m_fid"],
            omega_lambda=p["Omega_Lambda_fid"], omega_b=p["Omega_b_fid"],
            helium_mass_fraction=p["helium_mass_fraction"], b_i=p["initial_b"],
            t_max=p["proper_elapsed_time_s"][1])
        tables = load_provider(packet, "hm12_data.py").load_hm12()
        self.emissivity = tables["emissivity"]
        # Frozen discrete IVP input only. Later reference states are not read.
        with np.load(packet / "evidence/extended_dataset.npz", allow_pickle=False) as data:
            self.q, self.mu0, self.weights, self.y0 = [data[key].copy() for key in
                ("q_eV", "mu0", "weights", "initial_state")]
        self.n = len(self.q)
        if (self.n != 2904 or self.y0.shape != (self.n + 9,) or
                self.mu0.shape != self.q.shape or self.weights.shape != self.q.shape):
            raise ValueError("FROZEN_DISCRETE_IVP_SHAPE")
        self.times = np.linspace(*p["proper_elapsed_time_s"], 17)
        self.nh0, self.nhe0 = self.background.nH_i, self.background.nHe_i
        self.initial_photons = self.y0[4:4+self.n]
        initial_from_uvb = tables["uvb"].photon_number_log(self.q, p["initial_redshift_label"]) * self.weights
        # The archived IC bytes remain exact inputs. Re-evaluating a floating
        # expression in a different NumPy build can differ by a few ulps; this
        # consistency test is numerical, not a second byte-identity gate.
        if not np.allclose(initial_from_uvb, self.initial_photons,
                           rtol=8*np.finfo(float).eps, atol=0.):
            raise ValueError("FROZEN_PHOTON_IC_PROVIDER_DISAGREEMENT")
        self.scales = np.r_[np.ones(3), self.y0[3],
            np.maximum(self.initial_photons, 1e-12*self.initial_photons.sum()),
            np.full(3, self.energy(0., self.y0)), np.full(2, self.initial_photons.sum())]
        self.max_local_number = self.max_local_energy = 0.

    def energy(self, t, state):
        geometry = self.background.at(t)
        energy, _, _ = characteristics(self.q, self.mu0, geometry)
        x = state[:3]
        binding = self.nh0*x[0]*CHI[0] + self.nhe0*(x[1]*CHI[1]+x[2]*(CHI[1]+CHI[2]))
        return EV*(self.nh0*state[3] + binding + np.dot(state[4:4+self.n], energy))

    def stage(self, t, state):
        """One time and one state own geometry, opacity, source and gas stage."""
        geometry = self.background.at(t)
        energy, mu, ratio = characteristics(self.q, self.mu0, geometry)
        # Direction Jacobian and reference-volume convention are frozen:
        # E=qR, dOmega/dOmega0=(a_rel^3 R^3)^-1, N=a_rel^3 n.
        source = self.emissivity.photon_emission_log(energy, geometry["z"]) * self.weights / ratio**3
        nodes = np.column_stack([energy, mu, state[4:4+self.n], source]).ravel()
        values = np.r_[t, geometry["a_rel"], geometry["b"], geometry["H"], geometry["s"],
                       geometry["nH"], geometry["nHe"], state[:4], self.n, nodes]
        return values, source

    def rhs(self, t, state):
        values, source = self.stage(t, state)
        out = self.consumer.call("RHS", values, 14+self.n)
        self.max_local_number = max(self.max_local_number, abs(out[12]))
        self.max_local_energy = max(self.max_local_energy, abs(out[13]))
        return np.r_[out[:4], out[14:], out[4:8], source.sum()]

    def observables(self, t, state):
        g = self.background.at(t)
        energy, mu, _ = characteristics(self.q, self.mu0, g)
        photons = state[4:4+self.n]/g["a_rel"]**3
        sigma = self.consumer.call("SIGMA", energy, 3*self.n).reshape(-1, 3)
        gamma = C*np.sum(sigma*photons[:, None], axis=0)
        ne = g["nH"]*state[0]+g["nHe"]*(state[1]+2*state[2])
        temperature = 2*state[3]*g["nH"]*EV/(3*KB*(g["nH"]+g["nHe"]+ne))
        counters = state[4+self.n:]
        energy_residual = (self.energy(t, state)+counters[0]+counters[1]-counters[2]-self.energy(0., self.y0))/self.energy(0., self.y0)
        number_residual = (sum(state[4:4+self.n])+counters[3]-counters[4]-sum(self.initial_photons))/sum(self.initial_photons)
        return dict(time_s=float(t), z=g["z"], xHII=state[0], xHeII=state[1], xHeIII=state[2],
            T_K=temperature, nH_cm3=g["nH"], ne_cm3=ne, photon_cm3=float(photons.sum()),
            photon_erg_cm3=float(EV*np.dot(photons, energy)),
            delta_pressure_erg_cm3=float(EV*np.dot(photons*energy, (3*mu**2-1)/2)),
            GammaHI_s=gamma[0], GammaHeI_s=gamma[1], GammaHeII_s=gamma[2],
            energy_ledger_scaled=float(energy_residual), number_ledger_scaled=float(number_residual),
            min_photon_cm3_reference=float(state[4:4+self.n].min()),
            escape_erg_cm3_reference=counters[0], work_erg_cm3_reference=counters[1],
            source_erg_cm3_reference=counters[2], absorbed_cm3_reference=counters[3],
            source_cm3_reference=counters[4])

    def integrate(self):
        end = self.times[-1]
        def normalized_rhs(tau, scaled):
            return end*self.rhs(end*tau, scaled*self.scales)/self.scales
        solution = solve_ivp(normalized_rhs, (0., 1.), self.y0/self.scales,
                            method="DOP853", t_eval=self.times/end,
                            rtol=2e-10, atol=2e-13, max_step=1/16)
        if not solution.success:
            raise RuntimeError("PRODUCTION_INTEGRATION_FAILED: " + solution.message)
        states = solution.y*self.scales[:, None]
        rows = [self.observables(t, states[:, i]) for i, t in enumerate(self.times)]
        return states, rows, solution.nfev


def compare_reference(packet, interval, states, rows, contract):
    verify_bytes(packet / "evidence/extended.json", REFERENCE_JSON_SHA)
    reference_rows = json.loads((packet / "evidence/extended.json").read_text())["history"]
    with np.load(packet / "evidence/extended_dataset.npz", allow_pickle=False) as reference:
        reference_states = reference["states"]
        if not np.array_equal(reference["times_s"], interval.times):
            raise ValueError("REFERENCE_TIME_COORDINATE_MISMATCH")
    if len(rows) != len(reference_rows) or states.shape != reference_states.shape:
        raise ValueError("REFERENCE_HISTORY_SHAPE_MISMATCH")
    state_error = float(np.max(np.abs(states-reference_states)/interval.scales[:, None]))
    errors = {}
    for key in reference_rows[0]:
        a = np.array([row[key] for row in rows])
        b = np.array([row[key] for row in reference_rows])
        if key in ("energy_ledger_scaled", "number_ledger_scaled"):
            errors[key] = float(np.max(np.abs(a-b)))
        elif key == "delta_pressure_erg_cm3":
            scale = np.array([row["photon_erg_cm3"] for row in reference_rows])
            errors[key] = float(np.max(np.abs(a-b)/scale))
        else:
            scale = float(np.max(np.abs(b)))
            errors[key] = float(np.max(np.abs(a-b))/scale) if scale else float(np.max(np.abs(a-b)))
    numerical = contract["numerical_contract"]
    ledger_limit = numerical["energy_ledger_scaled_target"]
    checks = {
        "finite_states": bool(np.isfinite(states).all()),
        "state_agreement": state_error <= numerical["time_field_relative_target"],
        "observable_agreement": max(errors.values()) <= numerical["time_field_relative_target"],
        "temperature_domain": all(30000 <= row["T_K"] <= 110000 for row in rows),
        "positive_photons": bool(np.all(states[4:4+interval.n] >= 0)),
        "ionic_normalization": bool(np.all((states[:3] >= 0) & (states[:3] <= 1)) and
                                    np.all(states[1]+states[2] <= 1)),
        "global_energy_ledger": max(abs(row["energy_ledger_scaled"]) for row in rows) <= ledger_limit,
        "global_photon_ledger": max(abs(row["number_ledger_scaled"]) for row in rows) <= ledger_limit,
        "local_energy_ledger": interval.max_local_energy <= ledger_limit,
        "local_photon_ledger": interval.max_local_number <= ledger_limit,
    }
    return dict(status="PASS_SCOPED" if all(checks.values()) else "FAIL",
                checks={key: bool(value) for key, value in checks.items()},
                state_scaled_max=state_error, observable_errors=errors,
                max_local_number_ledger=interval.max_local_number,
                max_local_energy_ledger=interval.max_local_energy,
                scope="Production consumer agreement with the frozen discretization; historical empirical refinement reused; no continuum/global admission")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--binary", type=Path, default=CRATE/"target/release/axisym_conditional")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = args.packet.resolve()
    verified = preflight(packet)
    if args.output.exists():
        raise FileExistsError("P01_OUTPUT_ALREADY_EXISTS: use a new output directory")
    args.output.mkdir(parents=True)
    start = time.perf_counter()
    consumer = NativeConsumer(args.binary.resolve(), verified["identities"])
    try:
        interval = ProductionInterval(packet, verified, consumer)
        states, rows, nfev = interval.integrate()
        validation = compare_reference(packet, interval, states, rows, verified["contract"])
        files = [Path(__file__), CRATE/"Cargo.toml", CRATE/"Cargo.lock", *sorted((CRATE/"src").rglob("*.rs"))]
        metadata = dict(execution_path="production SourceBoundConditional", closure=CLOSURE,
            source_sha256=verified["identities"],
            production_source_sha256={str(p.relative_to(CRATE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            binary_sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest(),
            method="DOP853", nfev=nfev, rtol=2e-10, atol=2e-13, max_step_normalized=1/16,
            native_calls=consumer.calls, elapsed_wall_s=time.perf_counter()-start, nodes=interval.n,
            emitted_recombination_photon_count="UNDEFINED", optional_CR_RCT_HH="OFF",
            scientific_admission="HOLD", claim="SOURCE_BACKED_CONDITIONAL_FIRST_INTERVAL")
        result = dict(metadata=metadata, validation=validation, history=rows)
        (args.output/"production_interval.json").write_text(json.dumps(result, indent=2)+"\n")
        np.savez_compressed(args.output/"production_dataset.npz", q_eV=interval.q,
            mu0=interval.mu0, weights=interval.weights, initial_state=interval.y0,
            times_s=interval.times, states=states)
        print(json.dumps(dict(metadata=metadata, validation=validation), indent=2))
        if validation["status"] != "PASS_SCOPED":
            raise SystemExit(1)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
