"""Conditional He4(gamma,d)d bridge. Not a physical rate or heat model.

Consumes only the byte-frozen Git atlas from BASS_HE PR113. The 330 MeV
sigma is an explicitly unmeasured model interpolation of *reported* SIG.
Momentum injection is a per-event (two correlated daughter) kinematic kernel.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import mpmath as mp

ATLAS_GIT_BLOB = "293cb5d6937cf6c84584cb8d6f0a37336f50535f"
SOURCE_SHA256 = "b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f"
SOURCE_COMMIT = "939a14d7bba1ddce51975cb5e8711ce96b3b0871"
M_ALPHA = F("3727.3794118")  # M_alpha*c^2 [MeV], parent PR104
M_D = F("1875.61294500")    # m_d*c^2 [MeV], parent PR104
Q = 2 * M_D - M_ALPHA
E_THRESHOLD = Q + Q * Q / (2 * M_ALPHA)
EXPECTED_SIG_ENERGIES = [201, 225, 253, 285, 320, 359]
EXPECTED_DA_COORDINATES = {(E, a) for E in (213, 258, 330)
                           for a in (46, 61, 73, 87)}


def git_blob(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def load_frozen_atlas(path: Path) -> dict:
    raw = path.read_bytes()
    if git_blob(raw) != ATLAS_GIT_BLOB:
        raise ValueError("ATLAS_BYTE_IDENTITY_MISMATCH")
    atlas = json.loads(raw)
    source = atlas["source"]
    if (source["sha256"] != SOURCE_SHA256
            or source["commit"] != SOURCE_COMMIT
            or atlas["qualifications"]["full_330_MeV_SIG"] is not False):
        raise ValueError("SOURCE_PROVENANCE_MISMATCH")
    rows = atlas["measured_rows"]
    sig = rows["SIG_M0475003"]
    da = rows["DA_M0475002"]
    if [r["E_gamma_MeV"] for r in sig] != EXPECTED_SIG_ENERGIES:
        raise ValueError("SIG_ENERGY_GRAIN_MISMATCH")
    if {(r["E_gamma_MeV"], r["theta_CM_deg"]) for r in da} != EXPECTED_DA_COORDINATES:
        raise ValueError("DA_ANGULAR_GRAIN_MISMATCH")
    if len(sig) != 6 or len(da) != 12:
        raise ValueError("EXFOR_18_ROW_MISMATCH")
    return atlas


def linear_330_reported(sig320: F, err320: F, sig359: F, err359: F) -> dict:
    """A source-reported SIG estimate, NOT measured, event-normalized or physical.

    Statistical errors are pointwise ERR-S. Independence is a conditional scenario;
    min/max SD bounds range over all two-point correlations rho in [-1,1].
    The interpolation-model error has NO certified bound from these rows.
    """
    if min(sig320, err320, sig359, err359) < 0:
        raise ValueError("NEGATIVE_CROSS_SECTION_OR_ERROR")
    w320, w359 = F(29, 39), F(10, 39)
    est = w320 * sig320 + w359 * sig359
    a, b = w320 * err320, w359 * err359
    ksum = F(330) - Q
    return {
        "status": "MODEL_DEPENDENT_NOT_MEASURED",
        "observable": "SIG_reported_not_sigma_event",
        "model": "piecewise_linear_from_measured_320_and_359",
        "sigma330_nb": str(est), "weight320": str(w320), "weight359": str(w359),
        "stat_sd_independent_nb_approx": str(mp.sqrt(mp.mpf((a*a+b*b).numerator) / (a*a+b*b).denominator)),
        "stat_sd_min_rho_nb": str(abs(a-b)),
        "stat_sd_max_rho_nb": str(a+b),
        "model_systematic_uncertainty": None,
        "interpolation_remainder": "sigma_true(330)-sigma_linear(330)=-145 MeV^2 * sigma_second_derivative(xi), xi in (320,359)",
        "curvature_coefficient_MeV2": "145",
        "curvature_bound_nb_per_MeV2": None,
        "kinetic_pair_MeV": str(ksum),
        "sigma_times_pairK_nb_MeV": str(est*ksum),
        "kappa": None, "R_event": None, "heat_rate": None,
        "physical_activation": False, "L4": False, "production": "HOLD"
    }


def estimate_from_frozen_atlas(path: Path) -> dict:
    atlas = load_frozen_atlas(path)
    r = {v["E_gamma_MeV"]: v for v in atlas["measured_rows"]["SIG_M0475003"]}
    if sorted(r) != EXPECTED_SIG_ENERGIES or 330 in r:
        raise ValueError("SOURCE_ENERGIES_CHANGED_OR_330_IS_MEASURED")
    return linear_330_reported(F(r[320]["SIG_reported_nb"]), F(r[320]["ERR_S_nb"]),
                               F(r[359]["SIG_reported_nb"]), F(r[359]["ERR_S_nb"]))


def pair_momentum_kernel(E_gamma_MeV: F, theta_CM_deg: F, phi_CM_deg: F = F(0)):
    """Two physical D daughters per event in He-rest orthonormal coordinates.

    Four-vector components are (E [MeV], p*c [MeV]); no detector arm is assigned.
    The incident photon travels along +z, with arbitrary azimuth phi.
    For E_gamma>=threshold the unordered event is (pplus,pminus).
    """
    if E_gamma_MeV < E_THRESHOLD:
        raise ValueError("PHOTON_BELOW_RECOIL_THRESHOLD")
    if not (0 <= theta_CM_deg <= 180):
        raise ValueError("INVALID_CM_ANGLE")
    mp.mp.dps = 80
    def v(x):
        return mp.mpf(x.numerator) / x.denominator
    M, m, e = map(v, (M_ALPHA, M_D, E_gamma_MeV))
    theta = v(theta_CM_deg) * mp.pi / 180
    phi = v(phi_CM_deg) * mp.pi / 180
    s = M*M + 2*M*e
    q = mp.sqrt(s/4 - m*m)
    cm_gamma = (M+e)/mp.sqrt(s)
    pl = cm_gamma*q*mp.cos(theta)
    pt = q*mp.sin(theta)
    x, y = pt*mp.cos(phi), pt*mp.sin(phi)
    delta = e*q*mp.cos(theta)/mp.sqrt(s)
    plus = ((M+e)/2 + delta, (x, y, e/2 + pl))
    minus = ((M+e)/2 - delta, (-x, -y, e/2 - pl))
    return plus, minus


def pair_invariants(E_gamma_MeV: F, theta_CM_deg: F, phi_CM_deg: F = F(0)):
    plus, minus = pair_momentum_kernel(E_gamma_MeV, theta_CM_deg, phi_CM_deg)
    m, M, e = (mp.mpf(x.numerator)/x.denominator
               for x in (M_D, M_ALPHA, E_gamma_MeV))
    return {
        "daughter_count": 2,
        "energy_minus_initial_MeV": plus[0] + minus[0] - (M+e),
        "kinetic_minus_E_minus_Q_MeV": plus[0]+minus[0]-2*m-(e-(2*m-M)),
        "momentum_minus_photon_pc_MeV": tuple(plus[1][i]+minus[1][i]-(e if i==2 else 0)
                                             for i in range(3)),
        "shell_residuals_MeV2": tuple(p[0]**2-sum(x*x for x in p[1])-m*m
                                       for p in (plus,minus)),
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--atlas", required=True, type=Path,
                   help="PR113 immutable results/MEASURED_KINETIC_COORDINATES.json")
    a = p.parse_args()
    print(json.dumps(estimate_from_frozen_atlas(a.atlas), indent=2))


if __name__ == "__main__":
    main()
