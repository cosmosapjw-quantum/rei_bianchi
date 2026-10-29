"""Source-locked local optical-depth sensitivity-jet invariant.

NO IVP is solved. No physical tau, electron-density tangent, or Bianchi
observable is produced. Uses only the saved counterfactual PR262 source rates.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
PARENT_SOURCE = UNIT.parent / "rei_uvb_saved_state_source_tangent_20261029/results/RESULT.json"
BUNDLED_SOURCE = UNIT / "source/PR262_RESULT_LOCKED.json"
SOURCE = PARENT_SOURCE if PARENT_SOURCE.exists() else BUNDLED_SOURCE
SOURCE_SHA256 = "72db6976ff554663ff11227a016d5421008b26d329a5adad25166a9a9c7f320f"
SOURCE_GIT_BLOB = "526773ad659171389466a629e1f127c61ada53cd"
PARENT_PR262_HEAD = "6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf"
PIVOT_Z = 3.6


def load_saved():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("SOURCE_PR262_RESULT_SHA256_MISMATCH")
    obj = json.loads(raw)
    if obj.get("schema") != "REI_17_FROZEN_SOURCE_TANGENT_RESULT_V1":
        raise ValueError("SOURCE_SCHEMA_MISMATCH")
    entries = obj["entries"]
    if len(entries) != 7:
        raise ValueError("EXPECTED_SEVEN_SAVED_EPOCHS")
    if not all(2.4 <= r["saved_z"] <= 4.75 and
               r["electron_creation_per_Href_s"] > 0 and
               r["d_electron_creation_d_beta"] > 0
               for r in entries):
        raise ValueError("INVALID_SAVED_SOURCE_OR_DOMAIN")
    if not all(entries[i]["saved_z"] < entries[i+1]["saved_z"] for i in range(6)):
        raise ValueError("NONMONOTONE_SAVED_Z")
    return obj


def mean_log_clock_jet(z, g):
    """Return coefficients normalized by C=K*nHref/H**2, not physical tau.

    At a *parameter-independent* restart state y0 and geometry, the local
    optical-depth second derivative is C*[g, (z-z*)*g], with
    g=Q^T dF_photo,proper/d beta.  The determinant of second/third jet
    rows divided by C**2 equals g**2 dz/dx = -(1+z)*g**2.
    Full third derivative itself is not known without the whole J_y.
    """
    z, g = float(z), float(g)
    if not (math.isfinite(z) and 2.4 <= z <= 4.75 and math.isfinite(g) and g >= 0):
        raise ValueError("INVALID_SOURCE_JET_DOMAIN")
    d = z - PIVOT_Z
    dz_dx = -(1.0 + z)
    return {
        "z_mean": z,
        "d_z_dx": dz_dx,
        "normalized_tau_xx_beta": g,
        "normalized_tau_xx_kappa": d*g,
        "normalized_det_x": dz_dx*g*g,
        "normalized_det_x_div_g2": dz_dx if g > 0 else None,
        "tau_xxx_individual_coefficients": None,
        "tau_xx_normalizer": "C=K*nHref/H**2, not bound",
        "tau_xxx_normalizer": "C and full chemical Jacobian unknown",
        "actual_physical_tau_tangent": False,
    }


def determinant_from_jet(A, d, u, zprime):
    """Abstract 2x2 jet determinant; u is unknown beta third derivative.

    [[A, d*A], [u, d*u + A*zprime]] has determinant A**2*zprime.
    """
    if not all(math.isfinite(float(v)) for v in (A,d,u,zprime)):
        raise ValueError("NONFINITE_JET")
    return A*(d*u + A*zprime) - d*A*u


def produce():
    saved = load_saved()
    records = []
    for r in saved["entries"]:
        z = float(r["saved_z"])
        g = float(r["d_electron_creation_d_beta"])
        h = float(r["d_electron_creation_d_kappa"])
        if not math.isclose(h, (z-PIVOT_Z)*g, rel_tol=5e-14, abs_tol=1e-30):
            raise ValueError("PR262_BETA_KAPPA_RANK1_VIOLATION")
        row = mean_log_clock_jet(z,g)
        row["source_kappa_direct"] = h
        row["source_electron_creation_per_Href_s"] = r["electron_creation_per_Href_s"]
        for scope in ("deterministic", "joint2_95"):
            lo, hi = map(float, r["envelopes"][scope]["electron_per_Href_s"])
            if not (math.isfinite(lo) and math.isfinite(hi) and 0 < lo <= hi):
                raise ValueError("NONPOSITIVE_SOURCE_ENVELOPE")
            # Exact monotone image of the conditional *pointwise* nuisance set:
            # det/C**2 = -(1+z) * (ln(10)*source_electron_rate)**2.
            mlo = (1.0+z) * (math.log(10.)*lo)**2
            mhi = (1.0+z) * (math.log(10.)*hi)**2
            row[scope+"_normalized_absdet_interval"] = [mlo,mhi]
            row[scope+"_normalized_signed_det_interval"] = [-mhi,-mlo]
        row["conditional_rank_two"] = True
        records.append(row)
    return {
        "schema":"REI_UVB_TAU_JET_LOCAL_INVARIANT_V1",
        "source_pr":262,"source_pr_head":PARENT_PR262_HEAD,
        "source_git_blob":SOURCE_GIT_BLOB,"source_sha256":SOURCE_SHA256,
        "input_count":len(records),"entries":records,
        "robust_rank_scope":"pointwise deterministic EOS/Jeans box and conditional joint2-95 Gaussian ellipsoid union, positive source only",
        "theorem":"det D_(beta,kappa)(tau_xx,tau_xxx) = (K*nHref/H**2 * Q^T B_beta,proper)**2 * dz_mean/dx",
        "assumptions":["fixed parameter-independent initial state and optical-depth initial datum",
                       "parameter-independent smooth H,nHref,K and mean z(x)",
                       "full chemical F differentiable near selected epoch; photo source B_kappa=(z-3.6)*B_beta",
                       "x=ln(a/a_ref), dz_mean/dx=-(1+z_mean)",
                       "tau_x=(K*nHref/H)*Q^T y; q is only ionic electron proxy"],
        "not_claimed":["actual BASS K/nHref/H binding","actual chemical J_y or D_a y",
                       "observed directional redshift","physical tau response or likelihood",
                       "practical identifiability with noisy optical-depth measurements",
                       "full time integration, new IVP, numerical physical radii"],
        "new_ivp_count":0,
        "dag":{"working":"33/88","central_last":"28/88","physical_delta":0},
        "F4":"PARTIAL","L4_ready":False
    }

if __name__ == '__main__':
    print(json.dumps(produce(),indent=2,ensure_ascii=False))
