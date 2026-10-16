"""Six prescribed synthetic fixtures; all PL data here are tiny synthetic arrays."""
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from thomson_pair import (background_tuple, envelope, kernel_moments,
                          require_shared_background, write_json)

CONTRACT = json.loads((ROOT / "spec/THOMSON_PAIR_CONTRACT.json").read_text())
RTOL = CONTRACT["acceptance"]["numeric_fixture_rtol"]
ATOL = CONTRACT["acceptance"]["numeric_fixture_atol"]


def close(a, b):
    return math.isclose(a, b, rel_tol=RTOL, abs_tol=ATOL)


def synthetic_pl_norms(knots, values):
    """Analytic segment integrals, splitting sign changes for L1 only."""
    l1, l2 = [], []
    for x, y, u, v in zip(knots[:-1], knots[1:], values[:-1], values[1:]):
        width = y-x
        l2.append(width*(u*u+u*v+v*v)/3)
        if u*v < 0:
            l1.append(width*(u*u+v*v)/(2*(abs(u)+abs(v))))
        else:
            l1.append(width*(abs(u)+abs(v))/2)
    return {"Ninf": max(abs(v) for v in values), "N1": math.fsum(l1),
            "N2": math.sqrt(math.fsum(l2))}


def suffix_integral(knots, values, start):
    pieces = []
    for x, y, u, v in zip(knots[:-1], knots[1:], values[:-1], values[1:]):
        lo = max(start, x)
        if lo < y:
            vlo = u+(v-u)*(lo-x)/(y-x)
            pieces.append((y-lo)*(vlo+v)/2)
    return math.fsum(pieces)


class FrozenFixtures(unittest.TestCase):
    records = []

    @classmethod
    def tearDownClass(cls):
        write_json(ROOT / "results/TEST_RESULTS.json", {
            "schema_version": 1, "tolerances": {"rtol": RTOL, "atol": ATOL},
            "fixtures": cls.records, "executed_fixture_count": len(cls.records),
            "status": "PASS" if len(cls.records) == 6 and all(r["pass"] for r in cls.records) else "FAIL",
            "scope": "Synthetic equation checks only; no raw histories, solver convergence or physical accuracy admission"})

    def record(self, ident, inputs, expected, observed, checks):
        passed = all(checks.values())
        self.records.append({"id": ident, "inputs": inputs, "expected": expected,
                             "observed": observed, "checks": checks, "pass": passed})
        self.assertTrue(passed, f"{ident}: {checks}")

    def test_constant_hazard_sharpness(self):
        norms = synthetic_pl_norms([0, 1], [.2, .2])
        moments = kernel_moments(0, 1, 32, (1, 0, 0, 1))
        result = envelope(norms, moments, 1, 1)
        tau = suffix_integral([0, 1], [.2, .2], 0)
        no_scatter_delta = abs(math.exp(-tau)-1)
        # Zero reference is a point mass on empty, so TV equals candidate's continuous mass.
        tv = 1-math.exp(-tau)
        expected_q = 1-math.exp(-.2)
        self.record("constant_hazard_sharpness", {"ref": 0, "candidate": .2, "interval": [0, 1]},
                    {"D": .2, "q": expected_q, "TV": expected_q},
                    {"norms": norms, "tau": tau, "B": result["B"], "q": result["q"],
                     "transmission_difference": no_scatter_delta, "TV": tv},
                    {"D": close(norms["N1"], .2), "L1_attains": close(result["components"]["B_L1"], tau),
                     "q": close(result["q"], expected_q), "transmission": close(no_scatter_delta, expected_q),
                     "TV": close(tv, result["q"])})

    def test_signed_cancellation(self):
        knots = [0, 1]
        norms = synthetic_pl_norms(knots, [-1, 1])
        tau_ref = suffix_integral(knots, [1, 1], 0)
        tau_cand = suffix_integral(knots, [0, 2], 0)
        cdf_ref = math.exp(-suffix_integral(knots, [1, 1], .5))
        cdf_cand = math.exp(-suffix_integral(knots, [0, 2], .5))
        delta = cdf_cand-cdf_ref
        expected = math.exp(-.75)-math.exp(-.5)
        q = -math.expm1(-norms["N1"])
        self.record("signed_cancellation", {"ref": "1", "candidate": "2*x", "interval": [0, 1], "CDF_at": .5},
                    {"tau_ref": 1, "tau_candidate": 1, "D": .5, "CDF_difference": expected},
                    {"tau_ref": tau_ref, "tau_candidate": tau_cand, "D": norms["N1"],
                     "CDF_reference": cdf_ref, "CDF_candidate": cdf_cand, "CDF_difference": delta, "q": q},
                    {"equal_tau": close(tau_ref, 1) and close(tau_cand, 1), "D": close(norms["N1"], .5),
                     "CDF_formula": close(delta, expected), "CDF_nonzero": delta != 0,
                     "CDF_bounded": abs(delta) <= q})

    def test_localized_visibility(self):
        observations = []
        for epsilon in (.1, .01):
            knots = [0, epsilon/2, epsilon]
            values = [0, 2*.2/epsilon, 0]
            norms = synthetic_pl_norms(knots, values)
            tau = suffix_integral(knots, values, 0)
            # This exact TV uses the point-mass reference; no visibility density inference.
            observations.append({"epsilon": epsilon, "D": norms["N1"],
                                 "tau": tau, "hazard_max": norms["Ninf"], "TV": 1-math.exp(-tau)})
        q = -math.expm1(-.2)
        self.record("localized_visibility", {"ref": 0, "candidate": "triangle with area .2", "epsilon": [.1, .01]},
                    {"D_each": .2, "hazard_maxima": [4, 40], "TV_each": q, "claim": "L1-only probability versus density distinction"},
                    observations,
                    {"D": all(close(r["D"], .2) for r in observations),
                     "TV_fixed": all(close(r["TV"], q) for r in observations),
                     "maxima": close(observations[0]["hazard_max"], 4) and close(observations[1]["hazard_max"], 40)})

    def test_zero_and_unit_conversion(self):
        moments = kernel_moments(-3.044522437723423, -1.6094379124341003,
                                 CONTRACT["algorithm"]["panels"], background_tuple())
        frozen = CONTRACT["immutable_metric_selection"]
        norms = {key: frozen[key] for key in ("N1", "N2", "Ninf")}
        const = CONTRACT["constants"]
        c, sigma = const["c_cm_per_s"], const["sigma_T_cm2"]
        zero = envelope({key: 0 for key in norms}, moments, c, sigma)
        cgs = envelope(norms, moments, c, sigma)
        si = envelope({key: value*1e6 for key, value in norms.items()}, moments, c/100, sigma/1e4, "SI")
        rejected = False
        try:
            envelope(norms, moments, c, sigma, ("m/s", "cm^2", "cm^-3"))
        except ValueError:
            rejected = True
        self.record("zero_and_unit_conversion", {"norms_cgs": norms, "SI_conversion": {"density": 1e6, "c": .01, "sigma": .0001}},
                    {"B_zero": 0, "q_zero": 0, "cgs_SI_agreement": True, "mixed_units_rejected": True},
                    {"zero": zero, "cgs": cgs, "SI": si, "mixed_units_rejected": rejected},
                    {"zero_exact": zero["B"] == 0 and zero["q"] == 0,
                     "all_components_agree": all(close(cgs["components"][k], si["components"][k]) for k in cgs["components"]),
                     "B_agrees": close(cgs["B"], si["B"]), "q_agrees": close(cgs["q"], si["q"]),
                     "unit_validation": rejected})

    def test_background_mismatch(self):
        ref, cand = (1, 0, 0, 1), (2, 0, 0, 1)
        rejected = False
        try:
            require_shared_background(ref, cand)
        except ValueError:
            rejected = True
        delta_tau = abs(1/ref[0]-1/cand[0])
        self.record("background_mismatch", {"n_ref": 1, "n_candidate": 1, "K": 1, "H_ref": 1, "H_candidate": 2, "interval": [0, 1]},
                    {"density_difference": 0, "abs_tau_difference": .5, "shared_background_rejected": True},
                    {"density_difference": 0, "abs_tau_difference": delta_tau, "shared_background_rejected": rejected},
                    {"tau_nonzero": close(delta_tau, .5), "shared_H_rejected": rejected})

    def test_analytic_matter_quadrature(self):
        moments = kernel_moments(-1, 0, CONTRACT["algorithm"]["panels"], (1, 1, 0, 0))
        exact = {"1": (1-math.exp(-1.5))/1.5, "2": (1-math.exp(-3))/3}
        checks = {}
        for p, row in moments["raw_moments"].items():
            checks[f"p{p}_bracket"] = row["left"] <= exact[p] <= row["right"]
            checks[f"p{p}_endpoint_identity"] = close(row["upper_minus_lower"], row["endpoint_width_formula"])
        self.record("analytic_matter_quadrature", {"H0": 1, "Omega_m": 1, "Omega_r": 0, "Omega_Lambda": 0, "interval": [-1, 0], "panels": moments["panels"]},
                    {"integral_w": exact["1"], "integral_w_squared": exact["2"], "left_le_exact_le_right": True},
                    moments, checks)


if __name__ == "__main__":
    unittest.main()
