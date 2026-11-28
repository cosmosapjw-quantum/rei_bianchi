"""Bind the completed PHYS71 displayed D3 enclosure to the PHYS72 exact tail.

This is read-only reuse of three fixed input byte identities.  No Coulomb
function, old panel, profile, or physical source integral is evaluated.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from bounds import (
    D3_CERTIFICATE_SHA256, FROZEN_NPZ_SHA256,
    born_remainder_bound, rational_record, verify_file_identity,
)


DISPLAY_SHA256 = "b22a110aa08e44fd9560da215ff5955ab138586a37016c1578bd48ea96be1a47"
INPUT_IDENTITIES = (
    ("FROZEN_U_SUBSET.npz", FROZEN_NPZ_SHA256),
    ("ALL_ANGULAR_CERTIFICATE.json", D3_CERTIFICATE_SHA256),
    ("DISPLAY_RESULT.json", DISPLAY_SHA256),
)


def assemble(input_root: Path) -> dict:
    checks = [verify_file_identity(input_root / name, sha) for name, sha in INPUT_IDENTITIES]
    if any(item["status"] != "MATCH" for item in checks):
        raise ValueError("BLOCKED_INPUT_IDENTITY_MISMATCH: completed evidence cannot be adopted")
    display = json.loads((input_root / "DISPLAY_RESULT.json").read_text(encoding="utf-8"))
    if (
        display["schema"] != "PHYS71_DISPLAY_RESULT_V1"
        or display["certificate_sha256"] != D3_CERTIFICATE_SHA256
        or display["units"] != "a0^-1"
        or display["HH_R10"] != "OFF"
    ):
        raise ValueError("Inherited display contract is inconsistent")
    # Parsing validates exact finite decimal centers. Their original strings
    # are retained; no additional display rounding is introduced here.
    Fraction(display["real"])
    Fraction(display["imag"])
    eps3 = Fraction(display["absolute_error_upper"])
    if eps3 <= 0:
        raise ValueError("Expected a positive inherited error radius")
    tail = born_remainder_bound(terms=3, lambda_abs=1)
    if tail.remainder_upper is None:
        raise ArithmeticError("Fixed lambda=1 must satisfy the proved bound")
    combined = eps3 + tail.remainder_upper
    target = Fraction("1e-78")
    return {
        "schema": "PHYS72_THIRD_AND_HIGHER_ENCLOSURE_V1",
        "status": "CERTIFIED_BY_DERIVATION_AND_REUSED_D3_ENCLOSURE",
        "quantity": "[(Z_1-Z_0)-D_1-D_2]_(21,20),m=0",
        "subtracted_D1_D2": "exact coefficients, not approximate numerical centers",
        "lambda": "1",
        "center": {"real": display["real"], "imag": display["imag"]},
        "units": "a0^-1",
        "inherited_D3_radius": rational_record(eps3),
        "order_ge4_radius": rational_record(tail.remainder_upper),
        "combined_radius": rational_record(combined),
        "convenient_outward_radius": "7.271949342749E-79",
        "convenient_outward_radius_verified": combined <= Fraction("7.271949342749E-79"),
        "target_budget": rational_record(target),
        "target_met": combined < target,
        "center_rounding": "original PHYS71 decimal strings retained exactly",
        "printing_error": "already included in inherited absolute_error_upper; not added twice",
        "full_numeric_DeltaZ_error_rule": "eps1+eps2+eps3+R_ge4 plus any new sum-display rounding",
        "full_numeric_DeltaZ_assembled": False,
        "evidence": {
            "input_identity_checks": checks,
            "PHYS71_adoption": "completed external DELIVERY closes frozen M PENDING",
            "PHYS72_proof": "theory/MULTIPLIER_REMAINDER_DRAFT.md sections 2-6",
            "bounds_source_sha256": hashlib.sha256(Path(__file__).with_name("bounds.py").read_bytes()).hexdigest(),
            "enclosure_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "old_panel_integrations": 0,
        "inherited_profile_integrations": 0,
        "new_physical_integrations": 0,
        "old_campaign_verifier_runs": 0,
        "source_eta": "F*y",
        "source_xi": "F*y-phi; separate unresolved obligation",
        "eta_C": "-10/7",
        "HH_R10": "OFF",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path(__file__).resolve().parents[1] / "inputs")
    parser.add_argument("--output", type=Path, help="Create-only JSON output; otherwise stdout")
    args = parser.parse_args(argv)
    try:
        result = assemble(args.input_root)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        else:
            print(encoded, end="")
        return 0
    except (OSError, ValueError, KeyError, ArithmeticError) as exc:
        parser.exit(2, f"PHYS72 enclosure input/output error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
