"""One-temperature consistency diagnostic for the pinned H--He Q11/Q12 fits.

For a temperature-independent momentum-transfer cross section sigma_1(g),
the frozen normalization is

    Q11 = integral exp(-gamma**2) gamma**5 sigma_1 dgamma,
    Q12 = (1/3) integral exp(-gamma**2) gamma**7 sigma_1 dgamma.

It implies d ln Q11 / d ln T = 3 (Q12 / Q11 - 1). Independently fitted
rows need not satisfy this identity exactly. The reported residual diagnoses
their compatibility; it is neither a calibrated source uncertainty nor an
admission of an underlying differential collision law.

Q11 is read from the saved HE34 result and bound to the original HE34
collision_integral evaluator. Only Q12 and the analytic Q11 derivative are
new extensions. Actual source evaluation is restricted to T = 20000 K.
No source evaluation occurs on import.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
import math
from numbers import Real
from pathlib import Path
import sys
from typing import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[4]
SELECTED_TEMPERATURE_K = 20000.0
DOMAIN_K = (50.0, 50000.0)
AREA_FACTOR_M2 = math.pi * 1e-20
Q11_BINDING_RELATIVE_TOLERANCE = 8.0 * sys.float_info.epsilon
SOURCE_COMMIT = "58678c0e038eb2f078fed3b45640741fdaf167dc"
_HE34 = Path("research/he34_sandbox_certified_relaxation_20261022")
_PR102 = Path("research/program_expansion_20261025/continuation_20261025")
RELATIVE_PATHS = {
    "selected_source": _PR102 / "pair_source/SELECTED_H_HE_SOURCE.json",
    "legacy_code": _HE34 / "src/neutral_transport.py",
    "legacy_data": _HE34 / "data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json",
    "saved_result": _HE34 / "results/NEUTRAL_TRANSPORT.json",
    "upstream_cpp": _PR102 / "pair_source/upstream/CapitelliIntegrals.cpp",
    "upstream_header": _PR102 / "pair_source/upstream/CapitelliIntegrals.h",
}
EXPECTED_SHA256 = {
    "selected_source": "6f6237db79e5542ee66d7a8e75b175d1f4b780706f8cae2131a3405226386892",
    "legacy_code": "40cf77034e077adb77ae145ec747de168d7674b55307dd7f722dada60e1e61d9",
    "legacy_data": "699114aa23d13d38bd1d67fd74358fb52d06c25e8d3c87aa8d282de82dc26542",
    "saved_result": "eb8503ee40eb9d2a417af0cb10bde58d3d0a5e97d18541c2f2cb95212938f67c",
    "upstream_cpp": "7992430925c6cb04c1e029e930f078ca4713d9f2cb93b52176d7af8c9389fc23",
    "upstream_header": "0001ecff76e12e13f82bae059040e99a28f8d46227c659adb0e992022f4e4c56",
}


def _finite_real(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real scalar, excluding bool")
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} is not representable in binary64") from error
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _temperature(value):
    value = _finite_real(value, "T_K")
    if not DOMAIN_K[0] <= value <= DOMAIN_K[1]:
        raise ValueError("The source domain is 50 <= T_K <= 50000 K")
    return value


def _coefficients(values):
    if not isinstance(values, (tuple, list)) or len(values) != 7:
        raise ValueError("Seven finite real coefficients are required")
    result = tuple(_finite_real(x, f"coefficient[{i}]") for i, x in enumerate(values))
    if result[3] == 0.0 or result[6] == 0.0:
        raise ValueError("Logistic widths must be nonzero")
    return result


def default_evidence_paths(repo_root=REPO_ROOT):
    return {name: Path(repo_root) / path for name, path in RELATIVE_PATHS.items()}


@dataclass(frozen=True)
class PinnedInputs:
    q11_coefficients: tuple[float, ...]
    q12_coefficients: tuple[float, ...]
    saved_q11_m2: float
    legacy_code_path: Path
    evidence: tuple[tuple[str, str, str], ...]


def load_pinned_inputs(paths: Mapping[str, Path] | None = None):
    """Validate input bytes and inherited values without evaluating a fit."""
    if paths is not None and not isinstance(paths, Mapping):
        raise ValueError("Evidence paths must be a mapping")
    paths = default_evidence_paths() if paths is None else dict(paths)
    if set(paths) != set(EXPECTED_SHA256):
        raise ValueError("The complete frozen evidence set is required")
    raw = {}
    evidence = []
    for name, expected in EXPECTED_SHA256.items():
        path = Path(paths[name])
        content = path.read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ValueError(f"Changed evidence identity: {name}")
        raw[name] = content
        evidence.append((name, str(path), actual))
    source = json.loads(raw["selected_source"])
    legacy = json.loads(raw["legacy_data"], parse_float=Decimal, parse_int=Decimal)
    saved = json.loads(raw["saved_result"])
    if (source["source"]["commit"] != SOURCE_COMMIT
            or source["source_pair_labels"] != ["H", "He"]
            or source["temperature_domain_K"] != list(DOMAIN_K)
            or source["source_calibrated_uncertainty"] is not None
            or source["differential_cross_section_supplied"] is not False
            or source["joint_event_law_supplied"] is not False):
        raise ValueError("Source meaning or admission fields changed")
    selected = {}
    for kind in ("Q11", "Q12"):
        row = source["fit_rows"][kind]
        if (row["formula"] != "Bruno-Eq(11)" or row["area_unit"] != "m^2"
                or row["fit_to_area_multiplier"] != "pi * 1e-20"):
            raise ValueError("Source formula or area normalization changed")
        try:
            decimal = tuple(Decimal(x) for x in row["coefficients_decimal"])
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError("Invalid source decimal coefficient") from error
        if len(decimal) != 7 or not all(x.is_finite() for x in decimal):
            raise ValueError("Invalid source coefficient count or finiteness")
        selected[kind] = _coefficients([float(x) for x in decimal])
        if kind == "Q11":
            inherited = [r for r in legacy["fits"]
                         if r["pair"] == ["H", "He"] and r["kind"] == kind]
            if len(inherited) != 1 or decimal != tuple(inherited[0]["coefficients"]):
                raise ValueError("Q11 differs from the HE34 source coefficients")
    if (saved["temperature_K"] != SELECTED_TEMPERATURE_K
            or saved["coefficients"]["T_K"] != SELECTED_TEMPERATURE_K
            or saved["source_sha256"]["src/neutral_transport.py"]
            != EXPECTED_SHA256["legacy_code"]):
        raise ValueError("Saved Q11 result does not bind the selected evaluator/point")
    q11 = _finite_real(saved["coefficients"]["QHHe11_m2"], "saved Q11")
    if q11 <= 0.0:
        raise ValueError("Saved Q11 must be positive")
    return PinnedInputs(selected["Q11"], selected["Q12"], q11,
                        Path(paths["legacy_code"]), tuple(evidence))


def _legacy_module(path=None):
    """Import the original SHA-bound HE34 evaluator, without a copied kernel."""
    path = default_evidence_paths()["legacy_code"] if path is None else Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_SHA256["legacy_code"]:
        raise ValueError("Changed evidence identity: legacy_code")
    data_path = path.parent.parent / "data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json"
    if hashlib.sha256(data_path.read_bytes()).hexdigest() != EXPECTED_SHA256["legacy_data"]:
        raise ValueError("Changed evidence identity: legacy_data")
    module_name = "_he34_source_diagnostic_dependency_40cf7703"
    module = sys.modules.get(module_name)
    if module is not None:
        if Path(module.__file__).resolve() != path.resolve():
            raise ValueError("The cached HE34 module belongs to a different path")
        return module
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError("The HE34 evaluator cannot be imported")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        # Execute the original pinned bytes; compile avoids writing pyc in HE34.
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def _fit_terms(T_K, coefficients: Sequence[float]):
    temperature = _temperature(T_K)
    a = _coefficients(coefficients)
    x = math.log(temperature)
    z1 = _finite_real(2.0 * ((x - a[2]) / a[3]), "first logistic argument")
    z2 = _finite_real(2.0 * ((x - a[5]) / a[6]), "second logistic argument")
    expit = _legacy_module()._expit
    s1, s2 = expit(z1), expit(z2)
    return a, x, z1, z2, s1, s2, expit


def bruno_fit_area(T_K, coefficients: Sequence[float]):
    """Minimal extra-row evaluation using HE34's stable expit and SI factor."""
    a, x, _, _, s1, s2, _ = _fit_terms(T_K, coefficients)
    value = _finite_real(AREA_FACTOR_M2 * ((a[0] + a[1] * x) * s1 + a[4] * s2),
                         "fit Qbar_m2")
    if value <= 0.0:
        raise ValueError("Fit Qbar must be positive")
    return value


def bruno_fit_darea_dlogT(T_K, coefficients: Sequence[float]):
    """Analytic dQbar/dlnT [m^2]; stable logistic tails retain their slope."""
    a, x, z1, z2, s1, s2, expit = _fit_terms(T_K, coefficients)
    # expit(z)*expit(-z) preserves a small slope when expit(z) rounds to one.
    derivative = (a[1] * s1 + (a[0] + a[1] * x) * (2.0 / a[3])
                  * s1 * expit(-z1) + a[4] * (2.0 / a[6]) * s2 * expit(-z2))
    return _finite_real(AREA_FACTOR_M2 * derivative, "dQbar_dlnT_m2")


def same_law_residual(q11_m2, q12_m2, dq11_dlogT_m2):
    q11 = _finite_real(q11_m2, "Q11_m2")
    q12 = _finite_real(q12_m2, "Q12_m2")
    derivative = _finite_real(dq11_dlogT_m2, "dQ11_dlnT_m2")
    if q11 <= 0.0 or q12 <= 0.0:
        raise ValueError("Collision integrals must be positive")
    slope = _finite_real(derivative / q11, "dlnQ11_dlnT")
    ratio = _finite_real(q12 / q11, "Q12_over_Q11")
    try:
        residual = _finite_real(math.fsum((slope, -3.0 * (ratio - 1.0))), "identity residual")
    except OverflowError as error:
        raise ValueError("The identity residual exceeds binary64 representability") from error
    return slope, ratio, residual


def diagnose_h_he_source(T_K=SELECTED_TEMPERATURE_K, *, paths=None):
    """Evaluate this source at the single frozen temperature, with provenance."""
    temperature = _temperature(T_K)
    if temperature != SELECTED_TEMPERATURE_K:
        raise ValueError("This diagnostic authorizes only the selected 20000 K point")
    inputs = load_pinned_inputs(paths)
    q11_recomputed = _legacy_module(inputs.legacy_code_path).collision_integral(
        temperature, ("H", "He"), "Q11")
    q11 = inputs.saved_q11_m2
    relative_difference = abs(q11_recomputed - q11) / q11
    if (not math.isfinite(relative_difference)
            or relative_difference > Q11_BINDING_RELATIVE_TOLERANCE):
        raise ValueError("The HE34 evaluator disagrees with its saved Q11 result")
    q12 = bruno_fit_area(temperature, inputs.q12_coefficients)
    derivative = bruno_fit_darea_dlogT(temperature, inputs.q11_coefficients)
    slope, ratio, residual = same_law_residual(q11, q12, derivative)
    return {
        "schema": "he.h_he_q11_q12_same_law_diagnostic.v1",
        "temperature_K": temperature,
        "source_pair_labels": ["H", "He"],
        "source_commit": SOURCE_COMMIT,
        "Q11_saved_m2": q11,
        "Q11_legacy_recomputed_m2": q11_recomputed,
        "Q11_binding_relative_difference": relative_difference,
        "Q11_binding_relative_tolerance": Q11_BINDING_RELATIVE_TOLERANCE,
        "Q12_m2": q12,
        "dQ11_dlnT_m2": derivative,
        "dlnQ11_dlnT": slope,
        "Q12_over_Q11": ratio,
        "same_law_residual": residual,
        "residual_definition": "D = dlnQ11/dlnT - 3*(Q12/Q11 - 1)",
        "row_minus_derivative_H_heat_coefficient": "K*beta*D; multiply by |U|^2",
        "identity": "dlnQ11/dlnT = 3*(Q12/Q11 - 1)",
        "normalization": {
            "Q11": "integral exp(-gamma^2)*gamma^5*sigma_1 dgamma",
            "Q12": "(1/3)*integral exp(-gamma^2)*gamma^7*sigma_1 dgamma",
            "fit_to_m2": "pi*1e-20",
        },
        "source_temperature_count": 1,
        "temperature_scan_performed": False,
        "source_calibrated_uncertainty": None,
        "residual_is_uncertainty": False,
        "physical_provider_admitted": False,
        "differential_law_admitted": False,
        "source_isotope_binding": "UNRESOLVED_SOURCE_LABELS_ARE_H_AND_He",
        "evidence": [{"name": n, "path": p, "sha256": h}
                     for n, p, h in inputs.evidence],
    }


if __name__ == "__main__":
    print(json.dumps(diagnose_h_he_source(), indent=2, allow_nan=False))
