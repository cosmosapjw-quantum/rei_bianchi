"""Bounded independent checks for the frozen RR adapter contract."""

import hashlib
import json
import math
from pathlib import Path

from scipy.integrate import quad
from scipy.special import gamma

from rr_adapter import CHANNELS, CM3_TO_M3, K_B_J_K, STATUS, rr_rate


SOURCE = Path(__file__).resolve().parents[4] / (
    "research/rei_isotope_quotient_pilot_20261022/pilot/data/"
    "verner_ferland_rr_table1_original.dat"
)
ROWS = json.loads(Path(__file__).with_name("rr_rows.json").read_text())
EXPECTED = ("H I", "HeI a", "HeII", "LiI", "LiII", "LiIII")
CHARGES = ((1, 0), (1, 0), (2, 1), (1, 0), (2, 1), (3, 2))


def check_source():
    sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert sha == ROWS["source_sha256"] == "2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091"
    assert ROWS["source_url"] == "https://www.pa.uky.edu/~verner/rec.html"
    assert tuple(row[0] for row in ROWS["rows"]) == CHANNELS == EXPECTED
    source_lines = SOURCE.read_text().splitlines()
    for row, (qin, qout) in zip(ROWS["rows"], CHARGES):
        matches = [line for line in source_lines if line.startswith(row[0]) and
                   line[len(row[0]):].split()[:2] == [str(row[1]), str(row[2])]]
        assert len(matches) == 1, row[0]
        columns = matches[0][len(row[0]):].split()
        assert len(columns) == 6
        assert (int(columns[0]), int(columns[1])) == tuple(row[1:3])
        assert tuple(map(float, columns[2:])) == tuple(row[3:])
        rate = rr_rate(row[0], 1000)
        assert (rate["input_charge"], rate["output_charge"]) == (qin, qout)
    assert math.isclose(CM3_TO_M3, (0.01)**3, rel_tol=1e-15)
    return {"source_sha256": sha, "selected_rows": len(ROWS["rows"]),
            "charge_mapping": list(map(list, CHARGES)), "cm3_to_m3": CM3_TO_M3}


def reference_alpha(row, temperature):
    _, _, _, a, b, t0, t1 = row
    x, y = math.sqrt(temperature / t0), math.sqrt(temperature / t1)
    return a / (x * (1 + x)**(1 - b) * (1 + y)**(1 + b))


def check_slope():
    worst = 0.0
    h = 1e-5
    for row in ROWS["rows"]:
        for T in (100.0, 1000.0, 10000.0):
            r = rr_rate(row[0], T)
            fd = (math.log(reference_alpha(row, T*math.exp(h))) -
                  math.log(reference_alpha(row, T*math.exp(-h)))) / (2*h)
            mixed = abs(r["d_ln_alpha_d_ln_T"] - fd) / max(1.0, abs(fd))
            worst = max(worst, mixed)
            assert mixed <= 2e-9, (row[0], T, mixed)
            assert math.isclose(r["alpha_m3_s"], 1e-6*reference_alpha(row, T), rel_tol=2e-15)
            assert r["status"] == STATUS
    return {"cases": 18, "max_mixed_slope_error": worst, "limit": 2e-9}


def check_grid_and_invalid():
    factors = []
    for channel in CHANNELS:
        for j in range(257):
            T = 100 * 100**(j/256)
            r = rr_rate(channel, T)
            factors.append(r["kinetic_factor"])
            assert all(math.isfinite(r[key]) for key in (
                "alpha_m3_s", "d_ln_alpha_d_ln_T", "kinetic_factor", "lambda_J_m3_s"))
            assert r["alpha_m3_s"] > 0 and r["lambda_J_m3_s"] >= 0
    invalid = [("bogus", 1000, None), ("H I", 99.999, None),
               ("H I", 10000.001, None), ("H I", float("nan"), None),
               ("H I", float("inf"), None), ("H I", -float("inf"), None),
               ("H I", 1000, -1.0), ("H I", 1000, float("nan")),
               ("H I", 1000, float("inf"))]
    for channel, T, chi in invalid:
        try:
            rr_rate(channel, T, chi)
        except ValueError:
            pass
        else:
            raise AssertionError((channel, T, chi))
    return {"grid_cases": len(factors), "min_factor": min(factors),
            "max_factor": max(factors), "invalid_cases": len(invalid)}


def check_manufactured_moments():
    worst = 0.0
    for p in (-0.5, 0.0, 1.0):
        for T in (0.5, 2.0, 10.0):
            # Dimensionless k_B=1. Each direct integral is independent of the
            # derivative and of the gamma-function reference.
            I0 = quad(lambda E: E**(p+1)*math.exp(-E/T), 0, math.inf,
                      epsabs=1e-12, epsrel=1e-12)[0]
            I1 = quad(lambda E: E**(p+2)*math.exp(-E/T), 0, math.inf,
                      epsabs=1e-12, epsrel=1e-12)[0]
            alpha = T**(-1.5)*I0
            moment = T**(-1.5)*I1
            alpha_exact = gamma(p+2)*T**(p+0.5)
            moment_exact = gamma(p+3)*T**(p+1.5)
            derivative_identity = alpha * T * (1.5 + p+0.5)
            for got, target in ((alpha, alpha_exact), (moment, moment_exact),
                                (moment/alpha, (p+2)*T),
                                (derivative_identity, moment)):
                rel = abs(got-target)/abs(target)
                worst = max(worst, rel)
                assert rel <= 2e-10, (p, T, rel)
    return {"cases": 9, "max_relative_error": worst, "limit": 2e-10}


def check_ledger():
    worst = 0.0
    chi = 13.6 * 1.602176634e-19  # positive synthetic energy, not channel spectroscopy
    for channel in CHANNELS:
        for j in range(257):
            T = 100*100**(j/256)
            r = rr_rate(channel, T, chi)
            ledger = r["coefficient_ledger_J_m3_s"]
            assert ledger["thermal"] == -r["lambda_J_m3_s"]
            assert ledger["binding"] == -chi*r["alpha_m3_s"]
            assert ledger["completed_cascade"] == r["lambda_J_m3_s"] + chi*r["alpha_m3_s"]
            total = math.fsum(ledger.values())
            scale = sum(abs(v) for v in ledger.values())
            mixed = abs(total)/scale
            worst = max(worst, mixed)
            assert mixed <= 5e-15, (channel, T, mixed)
    return {"cases": 6*257, "chi_J_synthetic": chi,
            "max_scaled_residual": worst, "limit": 5e-15}


def run():
    return {"source": check_source(), "slope": check_slope(),
            "grid": check_grid_and_invalid(),
            "manufactured": check_manufactured_moments(), "ledger": check_ledger()}
