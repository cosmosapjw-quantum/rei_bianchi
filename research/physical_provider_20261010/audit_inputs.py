"""Bounded independent input/band audit; does not evolve or admit a history.

Run from any directory: python audit_inputs.py.  Writes evidence/input_audit.json.
Uses the unchanged native SIGMA consumer for atomic weights and a separate
Gauss-quadrature implementation. This is not independent atomic validation.
UVB values at final z are counterfactual tabulated diagnostics, never imposed
on the evolved photons. Source-weighted Gamma-like moments have units s^-2,
not photoionization rates; their tail fractions diagnose omitted injection.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from background import BianchiBackground
from hm12_data import C_CM_S, EV_ERG, H_ERG_S, MPC_CM, load_hm12

HERE = Path(__file__).resolve().parent
CHI = np.array([13.598434599702, 24.587389011, 54.41776])
THRESHOLDS = np.r_[CHI, 13.6, 24.59, 54.42]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class NativeSigma:
    """Independent minimal transport, deliberately not run_interval.Native."""
    def __enter__(self):
        self.binary = HERE / "native/target/release/rei_physical_native"
        self.proc = subprocess.Popen([str(self.binary)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.calls = 0
        return self

    def __call__(self, energies):
        self.calls += 1
        self.proc.stdin.write("SIGMA " + " ".join(f"{x:.17g}" for x in energies) + "\n")
        self.proc.stdin.flush()
        response = self.proc.stdout.readline()
        if not response.startswith("OK "):
            raise RuntimeError(f"Native SIGMA rejected audit: {response[:200]}")
        values = np.array([float(x) for x in response.split()[1:]])
        if values.size != 3 * len(energies) or np.any(values < 0) or not np.all(np.isfinite(values)):
            raise RuntimeError("Native SIGMA returned invalid shape/sign/finite state")
        return values.reshape(-1, 3)

    def __exit__(self, *exc):
        self.proc.stdin.close()
        self.proc.wait(timeout=10)
        stderr = self.proc.stderr.read()
        if self.proc.returncode:
            raise RuntimeError(f"Native SIGMA exit {self.proc.returncode}: {stderr}")


def raw_moments(table, z):
    low, high = table.energies_eV[[0, -1]]
    intervals = {"full_native": (low, high), "selected_10_200": (10, 200),
                 "below_10": (low, 10), "above_200": (200, high),
                 "ionizing_native_ge_13p6": (13.6, high),
                 "ionizing_selected_13p6_200": (13.6, 200),
                 "above_sigma_domain_50000": (50000, high)}
    values = {}
    for label, (a, b) in intervals.items():
        values[label] = {
            "bounds_eV": [float(a), float(b)],
            "proper_photon_number_moment": table.moment(a, b, z, proper_photons=True),
            "proper_photon_energy_moment_erg": EV_ERG * table.moment(a, b, z, power=1, proper_photons=True),
        }
    for quantity in ("proper_photon_number_moment", "proper_photon_energy_moment_erg"):
        values.setdefault("fractions", {})[quantity] = {
            "selected_of_full_native": values["selected_10_200"][quantity] / values["full_native"][quantity],
            "above200_of_ionizing_native": values["above_200"][quantity] / values["ionizing_native_ge_13p6"][quantity],
            "above50000_of_ionizing_native": values["above_sigma_domain_50000"][quantity] / values["ionizing_native_ge_13p6"][quantity],
        }
    values["units"] = ("number cm^-3; energy erg cm^-3" if table.kind == "uvb" else
                        "number cm^-3 s^-1; energy erg cm^-3 s^-1")
    return values


def sigma_moments(table, z, native_sigma, order):
    """Independent Gaussian integration on all native/log-energy segments."""
    knots = table.energies_eV
    edges = np.unique(np.r_[13.6, 200, 50000, THRESHOLDS,
                            knots[(knots > 13.6) & (knots < 50000)]])
    edges = edges[(edges >= 13.6) & (edges <= 50000)]
    gx, gw = np.polynomial.legendre.leggauss(order)
    energies, weights = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        dx = math.log(b/a)
        energies.extend(np.exp(math.log(a) + (1 + gx) * dx / 2))
        weights.extend(gw * dx / 2)
    energies, weights = np.array(energies), np.array(weights)
    sigma = native_sigma(energies)
    photon_log = table.values(energies, z) * table.proper_photon_factor(z)
    measure = C_CM_S * (weights * photon_log)[:, None] * sigma
    heat = measure * np.maximum(0, energies[:, None] - CHI[None, :]) * EV_ERG
    full, tail = energies >= 13.6, energies >= 200
    result = {}
    for mask, name in ((full, "13p6_to_50000"), (tail, "200_to_50000")):
        result[name] = {"number_weighted": np.sum(measure[mask], axis=0).tolist(),
                        "primary_heat_weighted_erg": np.sum(heat[mask], axis=0).tolist()}
    result["tail_fractions"] = {
        name: (np.array(result["200_to_50000"][name]) / np.array(result["13p6_to_50000"][name])).tolist()
        for name in ("number_weighted", "primary_heat_weighted_erg")}
    result["absorber_order"] = ["HI", "HeI", "HeII"]
    result["units"] = ("number s^-1 per absorber; primary heat erg s^-1 per absorber" if table.kind == "uvb" else
                        "injection-weighted number s^-2; primary heat erg s^-2, NOT actual rates")
    result["above_50000_rate_tail"] = "UNRESOLVED: outside native atomic fit domain; no zero-tail assertion"
    return result


def source_and_geometry_audit(tables):
    bg = BianchiBackground()
    saved = np.load(HERE / "evidence/base_dataset.npz")
    q, mu0, weights = (saved[k] for k in ("q_eV", "mu0", "weights"))
    initial = saved["initial_state"]
    initial_photons = initial[4:4+len(q)]
    uvb, source = tables["uvb"], tables["emissivity"]
    mu, wm = np.polynomial.legendre.leggauss(64)
    wm = wm / 2
    geometry = []
    sources = []
    for t in (0, 1e11):
        g = bg.at(t)
        aperp, _, aparallel = g["scale_rel"]
        # This form uses independently supplied spatial axes, not characteristic().
        radius = np.sqrt((1-mu**2) / aperp**2 + mu**2 / aparallel**2)
        det_inverse = 1 / (aperp**2 * aparallel)
        angular_jacobian = det_inverse / radius**3
        geometry.append({
            "time_s": t, "z": g["z"], "a_rel": g["a_rel"], "b": g["b"],
            "mean_R_minus3": float(np.dot(wm, radius**-3)),
            "a_rel_cubed": g["a_rel"]**3,
            "R_minus3_identity_relative_error": float(np.dot(wm, radius**-3) / g["a_rel"]**3 - 1),
            "angular_jacobian_integral_minus1": float(np.dot(wm, angular_jacobian) - 1),
            "formula": "dOmega/dOmega0=det(A^-1)/|A^-1 n0|^3=1/(a_rel^3 R^3)",
        })
        nodal_radius = np.sqrt((1-mu0**2)/aperp**2+mu0**2/aparallel**2)
        nodal_energy = q * nodal_radius
        nodal_source = source.photon_emission_log(nodal_energy, g["z"]) * weights / nodal_radius**3
        # Independently integrate the angle-dependent transported band exactly in E.
        exact_number = math.fsum(float(w / r**3) * source.moment(10*r, 200*r, g["z"], proper_photons=True)
                                for r, w in zip(radius, wm))
        exact_energy = EV_ERG * math.fsum(float(w / r**3) * source.moment(10*r, 200*r, g["z"], power=1, proper_photons=True)
                                        for r, w in zip(radius, wm))
        sources.append({
            "time_s": t, "z": g["z"],
            "number_reference_cm3_s_nodal": float(nodal_source.sum()),
            "number_reference_cm3_s_independent": exact_number,
            "number_relative_error": float(nodal_source.sum()/exact_number-1),
            "energy_reference_erg_cm3_s_nodal": float(EV_ERG*np.dot(nodal_source, nodal_energy)),
            "energy_reference_erg_cm3_s_independent": exact_energy,
            "energy_relative_error": float(EV_ERG*np.dot(nodal_source, nodal_energy)/exact_energy-1),
            "band_note": "Initial q in [10,200]; actual E endpoints are [10R,200R] at each mu0",
        })
    n_exact = uvb.moment(10, 200, 5.807, proper_photons=True)
    u_exact = EV_ERG * uvb.moment(10, 200, 5.807, power=1, proper_photons=True)
    unit_checks = {
        "IC_number_relative_error": float(initial_photons.sum()/n_exact-1),
        "IC_energy_relative_error": float(EV_ERG*np.dot(initial_photons,q)/u_exact-1),
        "IC_number_exact_cm3": n_exact, "IC_energy_exact_erg_cm3": u_exact,
        "UVB_4pi_over_c_h": 4*math.pi/(C_CM_S*H_ERG_S),
        "source_comoving_to_proper_initial": (1+5.807)**3/(MPC_CM**3*H_ERG_S),
        "source_units": "source table already angle-integrated emissivity: no extra 4pi",
    }
    # Bound static inspection to actual call sites, without claiming full code verification.
    tree = ast.parse((HERE / "run_interval.py").read_text())
    sites = {"photon_number_log": [], "photon_emission_log": []}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for item in ast.walk(node):
                if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute) and item.func.attr in sites:
                    sites[item.func.attr].append({"function": node.name, "line": item.lineno})
    expected = ([s["function"] for s in sites["photon_number_log"]] == ["__init__"] and
                [s["function"] for s in sites["photon_emission_log"]] == ["rhs"])
    if not expected:
        raise AssertionError("Unexpected J/source imposition call sites")
    return {"geometry": geometry, "source_normalization": sources,
            "initial_normalization": unit_checks, "J_source_static_call_sites": sites,
            "J_source_imposition_check": "PASS_SCOPED_STATIC: UVB only IC; emissivity only RHS; no later HM12 J imposed"}


def main():
    tables = load_hm12()
    redshifts = [5.807, 5.80698492362111]
    result = {
        "scope": "input moments, selected-band omission, source/J distinction, angular Jacobian only",
        "claim_ceiling": "no physical EoR admission; no independent atomic validation; finite native spectral domain only",
        "table_provenance": {k: t.provenance() for k, t in tables.items()},
        "endpoint_UVB_semantics": "counterfactual table diagnostic; not evolved endpoint photons",
        "native_sigma_binary_sha256": sha256(HERE / "native/target/release/rei_physical_native"),
        "run_interval_sha256": sha256(HERE / "run_interval.py"),
        "base_dataset_sha256": sha256(HERE / "evidence/base_dataset.npz"),
        "redshift_samples": [],
    }
    with NativeSigma() as native:
        for z in redshifts:
            sample = {"z": z, "tables": {}}
            for kind, table in tables.items():
                fine = sigma_moments(table, z, native, 16)
                coarse = sigma_moments(table, z, native, 8)
                residuals = []
                for interval in ("13p6_to_50000", "200_to_50000"):
                    for name in ("number_weighted", "primary_heat_weighted_erg"):
                        residuals.extend((np.array(coarse[interval][name])/np.array(fine[interval][name])-1).tolist())
                fine["quadrature_order_8_vs_16_max_relative_difference"] = max(map(abs, residuals))
                sample["tables"][kind] = {"raw_moments": raw_moments(table, z), "native_sigma_weighted": fine}
            result["redshift_samples"].append(sample)
        result["native_sigma_calls"] = native.calls
    result["normalization_checks"] = source_and_geometry_audit(tables)
    result["known_limitations"] = [
        "Above 50000 eV rate/heat tails unresolved; raw photon/energy tails integrated within table domain only.",
        "Above 200 eV omission must be judged per absorber; small photon-number tail does not ensure small heating tail.",
        "Source-weighted fractions quantify missing injection, not its later reprocessed photon spectrum.",
        "Endpoint table UVB diagnostics are distinct from the actual evolved photon field.",
        "Closure omissions, secondaries, fit uncertainty, HM12-to-Bianchi transfer remain outside this audit.",
    ]
    path = HERE / "evidence/input_audit.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"file": str(path), "sigma_calls": result["native_sigma_calls"],
                      "initial_tail_fractions": {k: v["native_sigma_weighted"]["tail_fractions"] for k,v in
                                                 result["redshift_samples"][0]["tables"].items()},
                      "normalization": result["normalization_checks"]}, indent=2))


if __name__ == "__main__":
    main()
