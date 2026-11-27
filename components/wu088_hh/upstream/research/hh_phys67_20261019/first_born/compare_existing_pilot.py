"""Compare exact stored PHYS66 binary64 bits to an existing PHYS67 enclosure.

This program reads results only. It never launches a solver or special-function
integration. Run from the repository root with PYTHONPATH=src.
"""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import numpy as np
from flint import arb, ctx, fmpq
from wu088_hh.phys67_first_born import dyadic_fraction


def q(value):
    value = F(value)
    return arb(fmpq(value.numerator, value.denominator))


def dyadic(value):
    m, e = value.man_exp()
    return {"mantissa": str(m), "exponent2": int(e)}


def fraction_record(value):
    return {"numerator_hex": format(value.numerator, "x"),
            "denominator_hex": format(value.denominator, "x")}


def main():
    root = Path(__file__).resolve().parents[3]
    pilot_npz = root / "research/hh_phys66_20261018/c5c8/results/PILOT_L28_T65.npz"
    pilot_json = pilot_npz.with_suffix(".json")
    certificate_path = Path(__file__).with_name("FIRST_BORN_CERTIFICATE.json")
    certificate = json.loads(certificate_path.read_text())
    pilot = json.loads(pilot_json.read_text())
    with np.load(pilot_npz, allow_pickle=False) as data:
        value = complex(data["contributions"][0, 21, 20])
    assert value == complex(*pilot["terms"][0]["physical_entry"])
    assert (certificate["ell"], certificate["ellprime"], certificate["m"], certificate["outer"]) == (21, 20, 0, "65")
    assert certificate["source_sha256"] == pilot["source_sha256"]
    records = {}
    with ctx.workprec(384):
        for kind in ("cutoff_enclosure", "full_radial_enclosure"):
            rectangle = certificate[kind]
            distance_min_squared = F(0); distance_max_squared = F(0)
            component = {}
            for name, stored in (("real", value.real), ("imag", value.imag)):
                exact_stored = F.from_float(stored)
                mid = dyadic_fraction(rectangle[name]["mid"])
                radius = dyadic_fraction(rectangle[name]["rad"])
                difference = exact_stored-mid
                distance_min_squared += max(abs(difference)-radius, F(0))**2
                distance_max_squared += (abs(difference)+radius)**2
                component[name] = {"stored_binary64_exact": fraction_record(exact_stored),
                    "error_interval_lower": fraction_record(difference-radius),
                    "error_interval_upper": fraction_record(difference+radius)}
            lower = q(distance_min_squared).sqrt().lower()
            upper = q(distance_max_squared).sqrt().upper()
            records[kind] = {"component_error_intervals": component,
                "absolute_error_lower_dyadic": dyadic(lower),
                "absolute_error_upper_dyadic": dyadic(upper),
                "absolute_error_lower_display": str(lower), "absolute_error_upper_display": str(upper),
                "strict_positive_error_proved": bool(lower > 0)}
        radius = certificate["numerical_complex_error_upper"]
        numerical = F(int(radius["numerator"]), int(radius["denominator_hex"], 16))
        tail = certificate["analytic_radial_tail_upper"]
        radial = F(int(tail["numerator_hex"], 16), int(tail["denominator_hex"], 16))
        lower = dyadic_fraction(records["full_radial_enclosure"]["absolute_error_lower_dyadic"])
        upper = dyadic_fraction(records["full_radial_enclosure"]["absolute_error_upper_dyadic"])
        strict_bounds = {
            "numerical_complex_radius_lt_2p328e_minus41": numerical < F("2.328e-41"),
            "radial_tail_lt_4p973e_minus53": radial < F("4.973e-53"),
            "old_pilot_error_gt_1p514e_minus36": lower > F("1.514e-36"),
            "old_pilot_error_lt_1p516e_minus36": upper < F("1.516e-36"),
        }
        result = {"schema": "PHYS67_EXISTING_PILOT_COMPARISON_V1",
            "recorded_utc": datetime.now(timezone.utc).isoformat(),
            "solver_executions": 0, "source_sha256": certificate["source_sha256"],
            "existing_pilot": {"physical_entry": [value.real, value.imag],
                "execution_origin": "RECOVERED_PRIOR_SANDBOX_PILOT_NOT_CURRENT_NCP"},
            "inputs_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (pilot_npz, pilot_json, certificate_path)},
            "comparisons": records,
            "numerical_complex_radius_display": str(q(numerical)),
            "analytic_radial_tail_display": str(q(radial)),
            "full_complex_error_upper_display": str(q(numerical+radial)),
            "strict_decimal_bounds": strict_bounds,
            "scope": "STORED_D1_21_20_ONLY;NO_ERROR_DECOMPOSITION_FOR_OLD_F64_PIPELINE",
            "HH_R10": "OFF"}
    output = Path(__file__).with_name("EXISTING_PILOT_COMPARISON.json")
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"numerical_radius": result["numerical_complex_radius_display"],
        "radial_tail": result["analytic_radial_tail_display"],
        "pilot_error_lower": records["full_radial_enclosure"]["absolute_error_lower_display"],
        "pilot_error_upper": records["full_radial_enclosure"]["absolute_error_upper_display"],
        "strict_decimal_bounds": strict_bounds}, indent=2))


if __name__ == "__main__":
    main()
