"""Neutral atomic mass candidate conversion, without changing WU authority."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
SELECTED_IDENTITIES = {
    "sp_7b3d2e472131e6c645d7": ("NIST_AME2012_H1_NEUTRAL_GROUND", "NIST_H"),
    "sp_17efcd73203997543678": ("NIST_AME2012_HE4_NEUTRAL_GROUND", "NIST_HE"),
}


def _positive_decimal(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} must preserve the source decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Invalid {label}") from error
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{label} must be positive and finite")
    return number


def convert_candidates(packet=None, authority=None):
    """Convert Ar*m_u and retain separate uncertainty sensitivities.

    The primary fields are a dated NIST transcription, not raw HTTP bytes.
    Unknown covariance is retained; no quadrature or total error is invented.
    """
    packet = (json.loads((SOURCES / "NEUTRAL_H1_HE4_MASS_CANDIDATES.json").read_text())
              if packet is None else packet)
    authority = (json.loads((SOURCES / "raw/WU_R1_species.json").read_text())["rows"]
                 if authority is None else authority)
    if (packet["schema"] != "he.neutral_ground_isotope_mass_candidates.v1"
            or packet["source_support"]["only_two_neutral_ground_ids"] is not True
            or len(packet["mass_rows"]) != 2):
        raise ValueError("This conversion is bound to the selected neutral-ground pair")
    unit = packet["atomic_mass_constant"]
    m_u = _positive_decimal(unit["kg"], "m_u")
    u_m_u = _positive_decimal(unit["standard_uncertainty_kg"], "u(m_u)")
    rows = []
    seen = set()
    with localcontext() as context:
        context.prec = 50
        for row in packet["mass_rows"]:
            sid = row["wu_species_id"]
            if sid in seen or sid not in authority:
                raise ValueError("Unknown or duplicate WU species identity")
            if (sid not in SELECTED_IDENTITIES
                    or (row["id"], row["source_ref"]) != SELECTED_IDENTITIES[sid]):
                raise ValueError("Selected isotope and primary source row identity differ")
            seen.add(sid)
            target = authority[sid]["compiler_record"]
            if (row["charge"] != 0 or row["pool"] != "material"
                    or row["state"] not in {"1s_ground", "electronic_ground"}
                    or any(row[key] != target[key]
                           for key in ("composition", "charge", "state", "pool"))):
                raise ValueError("Neutral ground-state mass identity differs from WU authority")
            ar = _positive_decimal(row["relative_atomic_mass"], "Ar")
            u_ar = _positive_decimal(row["standard_uncertainty_relative_atomic_mass"], "u(Ar)")
            mass = ar * m_u
            mass_binary64 = float(mass)
            if not math.isfinite(mass_binary64) or mass_binary64 <= 0:
                raise ValueError("Mass is not positive finite in binary64")
            rows.append({
                "source_row_id": row["id"], "wu_species_id": sid,
                "mass_kg_decimal": str(mass), "mass_kg_binary64": mass_binary64,
                "uncertainty_sensitivity_Ar_kg_decimal": str(m_u * u_ar),
                "uncertainty_sensitivity_m_u_kg_decimal": str(ar * u_m_u),
                "combined_standard_uncertainty_kg": None,
                "covariance_retrieved": False, "independence_assumed": False,
                "nuclear_or_electronic_binding_added_again": False,
                "source_ref": row["source_ref"],
            })
    if seen != set(SELECTED_IDENTITIES):
        raise ValueError("Selected isotope set differs from the fixed H1/He4 pair")
    return {"schema": "he.neutral_mass_candidate_conversion.v1", "rows": rows,
            "arithmetic": "50-digit Decimal multiplication of quoted source fields",
            "source_fields": packet["source_fields"],
            "transport_source_binding": "CONDITIONAL_CLASSICAL_FIXED_POTENTIAL_MODEL_ONLY",
            "transport_isotope_accuracy_calibrated": False,
            "raw_http_bytes_verified": False,
            "physical_provider_admitted": False}
