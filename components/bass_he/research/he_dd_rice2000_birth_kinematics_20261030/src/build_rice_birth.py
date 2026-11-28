#!/usr/bin/env python3
"""Rice (2000) source-conditional 4He(gamma,dd) birth kinematics, no radiation closure.

Rest energies in MeV, metric (-,+,+,+); c is retained in definitions by
E=M*c**2 and p*c. Angles in the source are effective CM angles of broad bins.
No interpolation of the experimental photon spectrum or response is made.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

E_ALPHA = 3727.3794118  # M_alpha*c^2 [MeV], frozen parent PR104
E_D = 1875.61294500     # m_d*c^2 [MeV], frozen parent PR104
Q = 2 * E_D - E_ALPHA
PARENT_BLOB_SHA = "9cdec4449b22bdba2797bbdfb815e98901b85636"


def source_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def invariants(egamma: float):
    if egamma < Q:
        raise ValueError("below two-deuteron threshold")
    s = E_ALPHA ** 2 + 2 * E_ALPHA * egamma
    q_star_c = 0.5 * math.sqrt(max(0.0, s - 4 * E_D ** 2))
    beta = egamma / (E_ALPHA + egamma)
    gam = (E_ALPHA + egamma) / math.sqrt(s)
    delta = egamma * q_star_c / math.sqrt(s)
    return s, q_star_c, beta, gam, delta


def one_pair(egamma: float, theta_cm_deg: float):
    s, q, beta, gam, delta = invariants(egamma)
    mu = math.cos(math.radians(theta_cm_deg))
    half = (egamma - Q) / 2
    kplus, kminus = half + delta * mu, half - delta * mu
    perp = q * math.sqrt(max(0.0, 1 - mu ** 2))
    long_plus = gam * (q * mu + beta * math.sqrt(s) / 2)
    long_minus = gam * (-q * mu + beta * math.sqrt(s) / 2)
    return {
        "K_plus_MeV": kplus, "K_minus_MeV": kminus,
        "K_high_MeV": max(kplus, kminus),
        "K_low_MeV": min(kplus, kminus),
        "K_sum_MeV": kplus + kminus,
        "pair_population_variance_MeV2": (delta * mu) ** 2,
        "p_perp_c_MeV": perp, "p_plus_z_c_MeV": long_plus,
        "p_minus_z_c_MeV": long_minus,
        "mass_shell_plus_MeV2": (kplus + E_D) ** 2 - long_plus ** 2 - perp ** 2 - E_D ** 2,
        "mass_shell_minus_MeV2": (kminus + E_D) ** 2 - long_minus ** 2 - perp ** 2 - E_D ** 2,
        "momentum_z_residual_c_MeV": long_plus + long_minus - egamma,
    }


def monotonic_certificate(lo: float, hi: float):
    """Interval proof 2*d(delta)/dE < 1 in the source bins.

    Set A=4*m_d^2, S=M^2+2*M*E, r=sqrt(1-A/S).
    2*delta'=r+E*A*M/(S^2*r). Bound each positive factor
    over [lo,hi] by its monotone endpoint envelope.
    """
    s_lo = E_ALPHA ** 2 + 2 * E_ALPHA * lo
    s_hi = E_ALPHA ** 2 + 2 * E_ALPHA * hi
    r_lo = math.sqrt(1 - 4 * E_D ** 2 / s_lo)
    r_hi = math.sqrt(1 - 4 * E_D ** 2 / s_hi)
    upper_two_delta_prime = r_hi + hi * (4 * E_D ** 2) * E_ALPHA / (s_lo ** 2 * r_lo)
    if not (upper_two_delta_prime < 1):
        raise ValueError("endpoint extrema not certified in this energy range")
    return upper_two_delta_prime


def atlas(source: dict):
    if len(source["observations"]) != 12 or source["independent_experiments"] != 1:
        raise ValueError("unexpected Rice source cardinality")
    records = []
    for i, obs in enumerate(source["observations"], 1):
        lo, hi = obs["Emin"], obs["Emax"]
        monotonic_ub = monotonic_certificate(lo, hi)
        plo = one_pair(lo, obs["theta_cm"])
        phi = one_pair(hi, obs["theta_cm"])
        sigma, stat = obs["sigma"], obs["stat_sd"]
        if not (sigma >= 0 and stat >= 0):
            raise ValueError("negative source cross section or error")
        output = {
            "row": i, "bin": obs["bin"],
            "Egamma_interval_MeV": [lo, hi],
            "effective_theta_cm_deg": obs["theta_cm"],
            "effective_theta_lab_author_deg": obs["theta_lab"],
            "measured_DA_nb_per_sr": sigma,
            "stat_sd_nb_per_sr": stat,
            "systematic_fraction_reported_not_joint_covariance": source["systematics"][obs["bin"]]["fraction"],
            "pair_Ksum_support_MeV": [plo["K_sum_MeV"], phi["K_sum_MeV"]],
            "daughter_Khigh_support_MeV": [plo["K_high_MeV"], phi["K_high_MeV"]],
            "daughter_Klow_support_MeV": [plo["K_low_MeV"], phi["K_low_MeV"]],
            "pair_population_variance_support_MeV2": [plo["pair_population_variance_MeV2"], phi["pair_population_variance_MeV2"]],
            "same_weight_birth_energy_DA_support_nb_MeV_per_sr": [sigma * (lo - Q), sigma * (hi - Q)],
            "same_weight_1sigma_stat_envelope_nb_MeV_per_sr": [max(0.0, sigma - stat) * (lo - Q), (sigma + stat) * (hi - Q)],
            "endpoint_Kplus_MeV": [plo["K_plus_MeV"], phi["K_plus_MeV"]],
            "endpoint_Kminus_MeV": [plo["K_minus_MeV"], phi["K_minus_MeV"]],
            "two_delta_prime_upper_proved": monotonic_ub,
            "status": "DERIVED_FROM_MEASURED_BIN_WITH_FIXED_EFFECTIVE_CM_ANGLE",
        }
        records.append(output)
    return {
        "schema": "BASS_HE_RICE2000_BIRTH_KINEMATIC_SOURCE_CONDITIONAL_V1",
        "source": {"doi": source["doi"], "parent_blob_sha": PARENT_BLOB_SHA,
                   "observations": 12, "independent_experiments": 1},
        "frozen_rest_energies_MeV": {"alpha": E_ALPHA, "deuteron": E_D, "Q": Q},
        "definition": "K+-=(Egamma-Q)/2 +/- Egamma*q_star*c/sqrt(s)*cos(theta_cm); pair variance=(Egamma*q_star*c/sqrt(s)*cos(theta_cm))^2",
        "contract": "End-point daughter energies and variance at fixed author effective theta_CM; true within-bin energy-angle distribution and photon response UNKNOWN. Measured DA×Ksum bounds require same nonnegative detector-corrected energy weighting as Rice DA. No photon phase-space, no astrophysical rate, no heat, no independent joint covariance.",
        "canonical_DAG": "28/88", "HE_physical_DAG": "14/18", "L4": False,
        "R_event": None, "heat_rate": None, "kappa": None, "production": "HOLD",
        "rows": records,
    }


def write(root: Path):
    source_path = root / "inputs/RICE2000_TABLE_I_AUTHORITATIVE.json"
    raw = source_path.read_bytes()
    if source_blob_sha(raw) != PARENT_BLOB_SHA:
        raise ValueError("Rice Table I byte identity changed")
    source = json.loads(raw)
    result = atlas(source)
    out = root / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "RICE2000_BIRTH_KINEMATICS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    fields = ["row", "bin", "effective_theta_cm_deg", "measured_DA_nb_per_sr", "stat_sd_nb_per_sr",
              "pair_Ksum_support_MeV", "daughter_Khigh_support_MeV", "daughter_Klow_support_MeV",
              "pair_population_variance_support_MeV2", "same_weight_birth_energy_DA_support_nb_MeV_per_sr"]
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["row", "bin", "theta_cm_deg", "DA_nb_sr", "stat_nb_sr", "Ksum_lo_MeV", "Ksum_hi_MeV",
                     "Khigh_lo_MeV", "Khigh_hi_MeV", "Klow_lo_MeV", "Klow_hi_MeV", "pair_var_lo_MeV2", "pair_var_hi_MeV2",
                     "birth_DA_lo_nb_MeV_sr", "birth_DA_hi_nb_MeV_sr"])
    for r in result["rows"]:
        vals = [r["row"], r["bin"], r["effective_theta_cm_deg"], r["measured_DA_nb_per_sr"], r["stat_sd_nb_per_sr"]]
        for field in fields[5:]:
            vals += [f"{v:.9f}" for v in r[field]]
        writer.writerow(vals)
    (out / "RICE2000_BIRTH_KINEMATICS.csv").write_text(buf.getvalue(), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print("source-qualified kinematic records:", len(write(args.root)["rows"]))
