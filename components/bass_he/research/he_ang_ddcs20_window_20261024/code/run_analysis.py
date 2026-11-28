"""One bounded actual 32-cell computation plus required representation controls."""
import numpy as np

from ddcs_window import (UNIT, Source, atomic_json, load_source, moment_weights,
                         moment_key, quadrature_moments, theta_interpolation_control,
                         window_moments)


def main():
    s = load_source()
    result = window_moments(s)
    weights, _, _ = moment_weights(s)
    analytic = {key: float(np.sum(w * s.values)) for key, w in weights.items()}
    g16, g32 = quadrature_moments(s, 16), quadrature_moments(s, 32)
    quad = {}
    for key, value in analytic.items():
        scale = max(abs(value), analytic[(0, 0)])
        quad[moment_key(*key)] = {"analytic_native": value, "GL16_native": g16[key], "GL32_native": g32[key],
                                "GL16_scaled_error": abs(g16[key] - value) / scale,
                                "GL32_scaled_error": abs(g32[key] - value) / scale,
                                "GL16_GL32_scaled_difference": abs(g16[key] - g32[key]) / scale}
    alt16, alt32 = theta_interpolation_control(s, 16), theta_interpolation_control(s, 32)
    alt32["relative_raw_difference_from_mu_model"] = {k: (v - result["raw_moments"][k]) / result["raw_moments"][k] for k, v in alt32["raw_moments"].items()}
    alt32["conditional_difference_from_mu_model"] = {k: v - result["conditional"][k] for k, v in alt32["conditional"].items()}
    alt_quad = {k: abs(v - alt16["raw_moments"][k]) / max(abs(v), alt32["raw_moments"]["R_0_0"]) for k, v in alt32["raw_moments"].items()}
    result["linear_theta_alternative"] = alt32
    scaled = window_moments(Source(s.energy, s.mu, s.values * 3.7, s.uncertainty_percent))
    scale_residual = max(abs(scaled["conditional_deterministic_box_not_CI"][k][side] - bounds[side]) for k, bounds in result["conditional_deterministic_box_not_CI"].items() for side in ("minimum", "maximum"))
    r = result["conditional"]
    checks = {
        "N_W_positive": result["raw_moments"]["R_0_0"] > 0,
        "mean_mu_inside_window": s.mu[0] <= r["mean_mu"] <= s.mu[-1],
        "mean_E_inside_window": 3 <= r["mean_E_eV"] <= 6,
        "mean_P2_inside_physical_range": -0.5 <= r["mean_P2"] <= 1,
        "trace_relation": result["invariants"]["trace_tensor_scaled_residual"] <= 5e-13,
        "conditional_covariance_PSD": min(result["conditional_covariance_diag_div_2me_epsilon"]) >= -1e-12 * r["mean_E_eV"],
        "quadrature16_32": max(max(v[k] for k in ("GL16_scaled_error", "GL32_scaled_error", "GL16_GL32_scaled_difference")) for v in quad.values()) <= 5e-13,
        "theta_quadrature16_32": max(alt_quad.values()) <= 5e-13,
        "ratio_witness_stationarity_and_equality": all(bounds[side + suffix] <= 5e-13 for bounds in result["conditional_deterministic_box_not_CI"].values() for side in ("min", "max") for suffix in ("_equality_scaled_residual", "_stationarity_scaled_gap")),
        "common_scale_ratio_extrema_invariance": scale_residual <= 5e-13,
        "all_ratios_inside_their_box": all(b["minimum"] - 5e-14 <= r[k] <= b["maximum"] + 5e-14 for k, b in result["conditional_deterministic_box_not_CI"].items()),
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": {k: bool(v) for k, v in checks.items()}, "quadrature": quad,
                  "theta_GL16_GL32_scaled_difference": alt_quad, "common_scale_ratio_extrema_max_absolute_difference": scale_residual,
                  "claim_limit": "Numerical operator validation and actual finite-window results; physical HE-ANG provider remains SOURCE_INPUT_PENDING"}
    atomic_json(UNIT / "results/moments.json", result)
    atomic_json(UNIT / "results/validation.json", validation)
    if not all(checks.values()):
        raise RuntimeError("actual-output validation failed; preserve output and return to root")
    print("Actual 32-cell window analysis PASS; no full-domain or event-law admission.")


if __name__ == "__main__":
    main()
