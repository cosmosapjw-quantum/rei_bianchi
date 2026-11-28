"""Pinned H--He transport-moment intake and conditional Maxwellian exchange.

This module does not evaluate the Bruno fit. It exposes exact source coefficients
and maps a separately evidenced Qbar11(T_*) value into elastic pair moments.
Source Qbar(l,s) is already a velocity/angular integral, not a differential law.
The user of the moment function must supply and review the isotope/mass mapping.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import xml.etree.ElementTree as ET

KB_J_K = 1.380649e-23
ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT / "sources/raw/mutationpp_collisions.xml"
LEGACY_PATH = ROOT / "sources/raw/he34_neutral_transport_subset.json"
XML_SHA256 = "25e0ac6affa33361e9652d3fd3f43760f40f1a500c0a4993b1ace82c5ce501c2"
XML_BLOB = "d86bf74e05e6bcac9db67cfc03055621ebed2f8c"
LEGACY_SHA256 = "699114aa23d13d38bd1d67fd74358fb52d06c25e8d3c87aa8d282de82dc26542"
SOURCE_COMMIT = "58678c0e038eb2f078fed3b45640741fdaf167dc"
KINDS = ("Q11", "Q12", "Q13", "Q14", "Q15", "Q22", "Q23", "Q24", "Q33")
DOMAIN_K = (50.0, 50000.0)


def _pinned_bytes(path: Path, expected_sha256: str) -> bytes:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(f"Source content identity changed: {path.name}")
    return raw


def load_h_he_fit_input(xml_path=XML_PATH, legacy_path=LEGACY_PATH) -> dict:
    """Read exact source rows and cross-check only the inherited two coefficients.

    This is data intake. No interpolation, fit evaluation or scientific replay
    occurs. Additional Q12,...,Q33 rows remain source-intaken, unevaluated inputs.
    """
    raw = _pinned_bytes(Path(xml_path), XML_SHA256)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != XML_BLOB:
        raise ValueError("Unexpected Git identity for the collision source")
    root = ET.fromstring(raw)
    pairs = [p for p in root.findall("pair")
             if p.get("s1") == "H" and p.get("s2") == "He"]
    if len(pairs) != 1:
        raise ValueError("Expected one explicit H--He pair")
    rows = {}
    for kind in KINDS:
        selected = pairs[0].findall(kind)
        if len(selected) != 1:
            raise ValueError(f"Missing or duplicate explicit {kind}")
        element = selected[0]
        if (element.get("type") != "Bruno-Eq(11)"
                or element.get("ref") != "Bruno2010" or len(element)):
            raise ValueError("H--He formula/reference changed")
        tokens = (element.text or "").split()
        try:
            valid = len(tokens) == 7 and all(Decimal(v).is_finite() for v in tokens)
        except InvalidOperation as error:
            raise ValueError("Non-numeric source coefficient") from error
        if not valid:
            raise ValueError("Expected seven finite decimal coefficients")
        rows[kind] = {
            "coefficients_decimal": tokens,
            "formula": "Bruno-Eq(11)",
            "source_xpath": f"/collisions/pair[@s1='H'][@s2='He']/{kind}",
            "quantity": "Qbar_" + kind[1] + "_" + kind[2],
            "area_unit": "m^2",
            "fit_to_area_multiplier": "pi * 1e-20",
            "admission": "SOURCE_INPUT_ONLY",
        }
    previous = json.loads(_pinned_bytes(Path(legacy_path), LEGACY_SHA256),
                          parse_float=Decimal, parse_int=Decimal)
    old = {r["kind"]: r["coefficients"] for r in previous["fits"]
           if r["pair"] == ["H", "He"]}
    if set(old) != {"Q11", "Q22"}:
        raise ValueError("Inherited H--He subset is not the expected two rows")
    for kind, coeffs in old.items():
        if tuple(Decimal(x) for x in rows[kind]["coefficients_decimal"]) != tuple(coeffs):
            raise ValueError(f"Coefficient disagreement with inherited {kind}")
        rows[kind]["admission"] = "INHERITED_SCOPED_TRANSPORT_RESULT_REUSED"
    return {
        "schema": "he.h_he_selected_transport_input.v1",
        "source": {
            "repository": "mutationpp/Mutationpp",
            "commit": SOURCE_COMMIT,
            "path": "data/transport/collisions.xml",
            "blob": blob,
            "sha256": XML_SHA256,
            "bytes": len(raw),
            "primary_publication_doi": "10.1063/1.3495980",
            "primary_locations": ["Eq(1)", "Eq(2)", "Eq(11)", "Table I", "Section II.A.2"],
        },
        "source_pair_labels": ["H", "He"],
        "source_quantity": "velocity-averaged transport collision integrals",
        "temperature_argument": "relative Maxwellian temperature T_star",
        "temperature_domain_K": list(DOMAIN_K),
        "temperature_extrapolation": False,
        "source_isotope_resolution": "UNRESOLVED_SOURCE_LABELS_ARE_H_AND_He",
        "mass_mapping": "explicit caller evidence; isotope substitution is conditional",
        "differential_cross_section_supplied": False,
        "joint_event_law_supplied": False,
        "source_calibrated_uncertainty": None,
        "fit_rows": rows,
        "physical_provider_admitted": False,
        "HE_ANG": "SOURCE_INPUT_PENDING",
        "new_fit_evaluations": 0,
        "historical_suites_replayed": 0,
    }


def _real(value, name: str, *, positive=False, nonnegative=False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real scalar")
    value = float(value)
    if positive and value <= 0.0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and value < 0.0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def relative_temperature(T_a_K, T_b_K, mass_a_kg, mass_b_kg) -> float:
    """T_*=(m_b T_a + m_a T_b)/(m_a+m_b), with no fit extrapolation."""
    ta = _real(T_a_K, "T_a_K", positive=True)
    tb = _real(T_b_K, "T_b_K", positive=True)
    ma = _real(mass_a_kg, "mass_a_kg", positive=True)
    mb = _real(mass_b_kg, "mass_b_kg", positive=True)
    scale = max(ma, mb)
    aa, bb = ma / scale, mb / scale
    # Equal-temperature endpoints remain exact, without numerical clipping.
    tstar = ta if ta == tb else (bb / (aa + bb)) * ta + (aa / (aa + bb)) * tb
    if not DOMAIN_K[0] <= tstar <= DOMAIN_K[1]:
        raise ValueError("Source requires 50 <= T_star <= 50000 K")
    return tstar


@dataclass(frozen=True)
class ConditionalPairMoments:
    T_star_K: float
    reduced_mass_kg: float
    mean_relative_speed_m_s: float
    thermal_conductance_W_m3_K: float
    heat_a_W_m3: float
    heat_b_W_m3: float
    linear_drag_kg_m3_s: float
    q11_value_evidence: str
    mass_binding_evidence: str
    basis: str = "DERIVED_CONDITIONAL_MAXWELLIAN_ELASTIC_MOMENTS"
    source_uncertainty: None = None
    physical_provider_admitted: bool = False

    def to_dict(self):
        return asdict(self)


def conditional_h_he_moments(
        *, T_H_K, T_He_K, n_H_m3, n_He_m3, mass_H_kg, mass_He_kg,
        q11_m2, q11_temperature_K, q11_value_evidence, mass_binding_evidence):
    """Map an evidenced Qbar11 into no-drift heat and linear-drift force moments.

    Heat rates are for zero bulk-relative drift, distinct classical Maxwellians,
    an elastic rotation-invariant pair law and fixed particle identities/counts.
    The returned drag K defines R_H=-K*(u_H-u_He) to first order in small drift.
    q11_m2 is an *input* at T_star; no source fit is evaluated here. The input
    evidence strings preserve provenance without claiming its scientific approval.
    """
    ta = _real(T_H_K, "T_H_K", positive=True)
    tb = _real(T_He_K, "T_He_K", positive=True)
    na = _real(n_H_m3, "n_H_m3", nonnegative=True)
    nb = _real(n_He_m3, "n_He_m3", nonnegative=True)
    ma = _real(mass_H_kg, "mass_H_kg", positive=True)
    mb = _real(mass_He_kg, "mass_He_kg", positive=True)
    q11 = _real(q11_m2, "q11_m2", positive=True)
    qtemp = _real(q11_temperature_K, "q11_temperature_K", positive=True)
    for value, label in ((q11_value_evidence, "q11_value_evidence"),
                         (mass_binding_evidence, "mass_binding_evidence")):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must identify the supplied input evidence")
    tstar = relative_temperature(ta, tb, ma, mb)
    if qtemp != tstar:
        raise ValueError("Qbar11 input must carry exactly the requested T_star; no rounded cache")
    scale = max(ma, mb)
    aa, bb = ma / scale, mb / scale
    fa, fb = aa / (aa + bb), bb / (aa + bb)
    reduced_mass = min(ma, mb) / (1.0 + min(ma, mb) / max(ma, mb))
    try:
        speed = math.sqrt((8.0 / math.pi) * KB_J_K * tstar / reduced_mass)
        if na == 0.0 or nb == 0.0:
            conductance = drag = heat_a = 0.0
        else:
            conductance = 4.0 * KB_J_K * na * nb * fa * fb * speed * q11
            drag = (4.0 / 3.0) * na * nb * reduced_mass * speed * q11
            heat_a = conductance * (tb - ta)
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Pair inputs exceed binary64 representability") from error
    _real(speed, "mean relative speed", positive=True)
    _real(conductance, "thermal conductance", nonnegative=True)
    _real(drag, "linear drag", nonnegative=True)
    _real(heat_a, "heat source")
    if na > 0.0 and nb > 0.0 and (conductance == 0.0 or drag == 0.0):
        raise ValueError("Nonzero pair coefficient underflowed binary64")
    return ConditionalPairMoments(tstar, reduced_mass, speed, conductance,
                                  heat_a, -heat_a, drag, q11_value_evidence,
                                  mass_binding_evidence)

