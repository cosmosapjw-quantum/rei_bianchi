"""Finite independent checks, never an evolution or continuum certificate.

Uses mpmath adaptive angular integration and a direct proper-time trapezoidal
sum, independently of the reviewed production quadrature functions.
"""
from pathlib import Path
import hashlib
import json
import sys

import mpmath as mp
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "axbi_science"))
from background_stress import angular_moments


def main():
    mp.mp.dps = 50
    angular = []
    for bs in ["-0.01", "-0.005892934597757158", "0", "0.002946499991410193", "0.01"]:
        b = mp.mpf(bs)
        def radius(v):
            return mp.sqrt(mp.exp(2*b)*(1-v*v)+mp.exp(-4*b)*v*v)
        def stress(v):
            r = radius(v)
            mu = mp.exp(-2*b)*v/r
            return r*(3*mu*mu-1)/2
        m = mp.quad(radius, [0, 1])
        f = mp.quad(stress, [0, 1])
        pm, pf = angular_moments([float(b)])
        pm16, pf16 = angular_moments([float(b)], 16)
        angular.append({"b": bs, "M_adaptive50": str(m), "F_adaptive50": str(f),
                        "M_abs_difference": abs(float(m)-pm[0]),
                        "F_abs_difference": abs(float(f)-pf[0]),
                        "GL16_M_abs_difference": abs(float(m)-pm16[0]),
                        "GL16_F_abs_difference": abs(float(f)-pf16[0])})
    source = ROOT / "integration/private/source_full/private_inputs/SHEAR_MINUS/history.csv"
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    columns = ["time_s", "a", "b", "H_per_s", "s_per_s", "nH_proper_cm3",
               "ne_proper_cm3", "temperature_K", "photon_u_eV_per_H",
               "J0_photon_u_eV_per_H", "J2_photon_u_eV_per_H"]
    data = pd.read_csv(source, usecols=columns, float_precision="round_trip")
    a, b, t, h = (data[k].to_numpy() for k in ["a", "b", "time_s", "H_per_s"])
    assert np.all(np.diff(a)>0) and np.all(np.diff(t)>0)
    # Independent initial-direction integration; the production method uses local angle.
    v, w = np.polynomial.legendre.leggauss(32)
    w = w/2
    m = np.empty_like(a)
    f = np.empty_like(a)
    for begin in range(0, len(a), 8192):
        stop = min(begin+8192, len(a))
        bc = b[begin:stop, None]
        radius = np.sqrt(np.exp(2*bc)*(1-v*v)+np.exp(-4*bc)*v*v)
        mu = np.exp(-2*bc)*v/radius
        m[begin:stop] = np.sum(radius*w, axis=1)
        f[begin:stop] = np.sum(radius*(3*mu*mu-1)/2*w, axis=1)
    c, g, kb, ev = 299792458.0, 6.67430e-11, 1.380649e-23, 1.602176634e-19
    h0 = 67.4e3/3.0856775814913673e22
    coupling = 8*np.pi*g/(3*c*c)
    uref = h0*h0*.000092/(coupling*a**4)
    nh = data.nH_proper_cm3.to_numpy()*1e6
    dne = data.ne_proper_cm3.to_numpy()*1e6
    dpion = nh*ev*data.J2_photon_u_eV_per_H.to_numpy()
    dpbg = uref*f
    def integrate(dp):
        y = np.asarray(coupling*a**3*dp, dtype=np.longdouble)
        increments = (y[1:]+y[:-1])/2*np.diff(t).astype(np.longdouble)
        integral = np.concatenate([np.array([0], dtype=np.longdouble), np.cumsum(increments)])
        return np.array(integral/(a**3*h), dtype=float)
    ds_bg, ds_ion, ds_total = (integrate(dp) for dp in [dpbg, dpion, dpbg+dpion])
    hf2 = h0*h0*(.000092/a**4+.315/a**3+(1-.315-.000092))
    uth = 1.5*kb*data.temperature_K.to_numpy()*(nh*(1+.2454/(4*(1-.2454)))+dne)
    uion = nh*ev*data.photon_u_eV_per_H.to_numpy()
    extra = (uion+uth+abs((m-1)*uref))/(hf2/coupling)
    j0_identity = np.max(abs(data.photon_u_eV_per_H-data.J0_photon_u_eV_per_H))
    peak = int(np.argmax(abs(ds_total)))
    result = {
        "runtime_status": "PYTHON_PASS", "python_version":sys.version,
        "independence": "Separate reviewer without parent history; derivation independent; same saved sources and NumPy implementation of Legendre nodes; mpmath adaptive angular reference and long-double direct proper-time sum differ from production method.",
        "angular_adaptive_checks": angular,
        "case": "SHEAR_MINUS", "source_sha256":digest.hexdigest(), "rows": len(a),
        "native_direct_proper_time_trapezoid": {
            "max_abs_background_delta_s_over_H":float(max(abs(ds_bg))),
            "max_abs_ionizing_delta_s_over_H":float(max(abs(ds_ion))),
            "max_abs_total_delta_s_over_H":float(max(abs(ds_total))),
            "total_signed_peak":float(ds_total[peak]), "peak_zbar":float(1/a[peak]-1),
            "max_source_matching_extra_energy_over_Hflrw_background":float(max(extra)),
            "max_ionizing_plus_thermal_over_Hflrw_background":float(max((uion+uth)/(hf2/coupling))),
            "max_abs_J0_minus_inventory_eV_per_H": float(j0_identity),
            "max_relative_H_identity_residual":float(max(abs(h*h-(hf2+data.s_per_s.to_numpy()**2))/(h*h))),
            "max_superposition_residual":float(max(abs(ds_total-ds_bg-ds_ion)))},
        "limitations": ["One native history numerically spot-checked; other histories source hashes/production tests are the author's validation, not independently rerun here.", "Proper-time trapezoid differences are comparison evidence, not a rigorous integration bound.", "No coupled dynamics, abundance error, or original ODE convergence established."]}
    summary = json.loads((ROOT / "axbi_science/results/FULL_SUMMARY.json").read_text())["cases"]["SHEAR_MINUS"]
    numeric = result["native_direct_proper_time_trapezoid"]
    result["comparison_to_full_summary"] = {
        "total_max_abs_difference":abs(numeric["max_abs_total_delta_s_over_H"]-summary["max_abs_total_delta_s_over_H"]),
        "background_max_abs_difference":abs(numeric["max_abs_background_delta_s_over_H"]-summary["max_abs_background_delta_s_over_H"]),
        "ion_max_abs_difference":abs(numeric["max_abs_ionizing_delta_s_over_H"]-summary["max_abs_ionizing_delta_s_over_H"]),
        "extra_energy_max_abs_difference":abs(numeric["max_source_matching_extra_energy_over_Hflrw_background"]-summary["max_extra_energy_over_FLRW_background_source_comparator"])}
    (ROOT / "reviews/AXBI_INDEPENDENT_NUMERICS.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
