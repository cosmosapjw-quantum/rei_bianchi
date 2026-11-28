from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest

from wu088_hh import phys69_all_angular as assembly
from wu088_hh import phys69_angular_tail as tail

ROOT = Path(__file__).resolve().parents[1]
BAND = ROOT/"research/hh_phys69_20261019/band/run_j29_36_t65"


def test_exact_addition_one_radial_tail_and_charged_display():
    old, new = (F(1, 3), F(-2, 5)), (F(1, 7), F(1, 9))
    e0, e1 = F("8e-67"), F("3e-71")
    r = assembly.assemble_exact(old, new, e0, e1)
    mid = {k: tail.read_rational(v) for k, v in r["midpoint_exact"].items()}
    assert mid == {"real": F(10, 21), "imag": F(-13, 45)}
    error = e0+e1+tail.RADIAL_BETA2_L64_T65_UPPER+tail.excluded_second_born_bound(36)
    assert tail.read_rational(r["absolute_error_about_exact_midpoint"]) == error
    shown = r["display_midpoint"]
    display_error = sum(abs(mid[k]-F(shown[k])) for k in mid)
    assert tail.read_rational(r["display_rounding_error_l1"]) == display_error > 0
    assert tail.read_rational(r["absolute_error_about_display_midpoint"]) == error+display_error
    assert r["fixed_goal_met"] is True
    assert r["display_fixed_goal_met"] is False  # Printing O(1) to 24 digits costs >1e-62.
    assert tail.read_rational(r["error_components"]["exact_midpoint_addition"]) == 0


def test_synthetic_tiny_physical_scale_meets_original_goal():
    r = assembly.assemble_exact((F("7e-48"), F("3e-48")),
                               (F("8e-61"), F("2e-61")), F("8e-67"), F("3e-71"))
    assert r["display_fixed_goal_met"] is True
    assert r["real_part_strictly_positive"] and r["imag_part_strictly_positive"]
    assert F(r["display_absolute_error_upper_decimal"]) >= tail.read_rational(
        r["absolute_error_about_display_midpoint"])


@pytest.mark.parametrize("args", [
    ((1.0, F(0)), (F(0), F(0)), F(0), F(0)),
    ((True, F(0)), (F(0), F(0)), F(0), F(0)),
    ((F(0),), (F(0), F(0)), F(0), F(0)),
    ((F(0), F(0)), (F(0), F(0)), F(-1), F(0)),
])
def test_inexact_or_negative_budget_refused(args):
    with pytest.raises(ValueError):
        assembly.assemble_exact(*args)


def test_completed_band_is_verified_without_numeric_engine(monkeypatch):
    # This reads stored JSON only; no Flint module or PHYS68 integration entry is imported.
    cert, report = assembly.validate_saved_band(ROOT, BAND)
    assert report["payload_hashes_verified"] == 76
    assert report["boundary_carries_verified"] == 1216
    assert report["old_radial_integrations"] == report["new_radial_integrations"] == 0
    assert cert["full_intermediate_sum"] == list(range(29, 37))
    assert F(int(cert["D2_numerical_absolute_error_l1"]["numerator"]),
             int(cert["D2_numerical_absolute_error_l1"]["denominator"])) > 0


@pytest.mark.parametrize("field,changed", [
    ("scientific_execution", "PARTIAL_CHECKPOINT"), ("m", True),
    ("full_intermediate_sum", list(range(28, 37))),
    ("radial_cutoff_error_included", True), ("numerical_absolute_goal_met", 1),
])
def test_physical_or_execution_identity_tamper_refused(monkeypatch, field, changed):
    path = BAND/"CERTIFICATE.json"
    original_read = Path.read_bytes
    value = json.loads(original_read(path)); value[field] = changed
    replacement = json.dumps(value).encode()
    monkeypatch.setattr(Path, "read_bytes", lambda p: replacement if p == path else original_read(p))
    with pytest.raises(ValueError):
        assembly.validate_saved_band(ROOT, BAND, hashlib.sha256(replacement).hexdigest())


def test_payload_mutation_rejected_even_with_unchanged_top_manifest(monkeypatch):
    path = BAND/"panel_0000.json"
    original_read = Path.read_bytes
    value = json.loads(original_read(path)); value["payload"]["second_Born_terms"][0]["j"] = 28
    replacement = json.dumps(value).encode()
    monkeypatch.setattr(Path, "read_bytes", lambda p: replacement if p == path else original_read(p))
    with pytest.raises(ValueError, match="payload SHA256"):
        assembly.validate_saved_band(ROOT, BAND)


def test_exact_box_carry_detects_a_missing_sliver():
    inner = ((F(1), F(1, 3)), (F(-1), F(1, 5)))
    assert assembly._contains(inner, inner)
    outer = ((F(1), F(1, 3)-F(1, 10**100)), inner[1])
    assert not assembly._contains(outer, inner)
