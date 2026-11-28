"""Create-only, identity-aware PHYS82 sensitivity study.

Run this new command through source/leased_call.py.  It never launches the
historical PHYS81 runner: nine saved Li7 rows are copied, while the unchanged
finite operator is evaluated only at 63 new temperatures.  A complete saved
identity is structurally validated and returned without scientific callbacks.
Incomplete attempts fail closed for inspection rather than silently replaying.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, fields
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from numbers import Real
from pathlib import Path
import platform

import numpy as np
import scipy

if __package__:
    from .threshold_gap import (
        E0_EV, ICHEMICAL_EV, MATCHED_MODEL_NAMES, MODEL_NAMES, P_W, SIGMA0_CM2,
        ZA_SLOPE_CM2_PER_EV, ThresholdRate, combine_rates, fixed_exposure,
        from_finite_rate, named_models,
    )
    from .vendor.phys81.finite_ci import FiniteWindowCI
else:
    from threshold_gap import (
        E0_EV, ICHEMICAL_EV, MATCHED_MODEL_NAMES, MODEL_NAMES, P_W, SIGMA0_CM2,
        ZA_SLOPE_CM2_PER_EV, ThresholdRate, combine_rates, fixed_exposure,
        from_finite_rate, named_models,
    )
    from vendor.phys81.finite_ci import FiniteWindowCI


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "PHYS82_THRESHOLD_STUDY_V1"
SAVED_TEMPERATURES = (
    255.0, 300.0, 1000.0, 3000.0, 10000.0, 20000.0,
    25370.66308424773, 35000.0, 50000.0,
)
EXPOSURES = (1.0e9, 1.0e11, 1.0e13)
PINNED_INPUTS = {
    "CONTRACT.json": "450b36883f78b12976dec22e0c4d1435dfb337ad1d74af70b84e8c8ef6df5f13",
    "source_data/LI_THRESHOLD_SOURCE_CONTRACT.json":
        "04e5c0c1921720679a8bd96649ade1bc0a938c4dc01cb489a4fa7127ce60bbb5",
    "source_data/PHYS81_PARENT_REGISTRY.json":
        "2415d357c318f1ff1307239f4f39c8009e6a7005b140c3ec67b492f631097641",
    "source_data/PHYS81_LITERAL.csv":
        "522fd63bd4aead4314d7b4ea87f61e5454b23df0f046b1c8e48b2f2023272dad",
    "source_data/PHYS81_SAVED_RATE_PROFILES.json":
        "131de5ea39834a3a3a3dbf4a15ebfe196d1980ebabd69bebcf3e69100e7b2d33",
    "source/vendor/phys81/finite_ci.py":
        "e582e83650f39fbaf38e66be848d736845b2bbf38f52613c464ae4e2c1d77674",
    "source/vendor/phys81/vendor/ci_finite_c22d.py":
        "859cdf616ffa165c9fb3c3372d2202f5449e4b9a74a289a725fe456e26eb55b2",
    "source/vendor/phys81/vendor/CCC_TICS_1S.txt":
        "7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae",
    "source/vendor/phys78_run_pilot.py":
        "76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124",
}
INPUT_FILES = (
    "CONTRACT.json", "theory/THRESHOLD_CONSTRUCTION_KO.md",
    "source_data/LI_THRESHOLD_SOURCE_CONTRACT.json",
    "source_data/PHYS81_PARENT_REGISTRY.json",
    "source_data/PHYS81_LITERAL.csv",
    "source_data/PHYS81_SAVED_RATE_PROFILES.json",
    "source/vendor/REUSE.json",
    "source/vendor/phys81/vendor/CCC_TICS_1S.txt",
)
EXPECTED_COUNTS = {
    "temperatures": 72,
    "saved_baseline_rows_reused": 9,
    "new_baseline_evaluations": 63,
    "gap_evaluations": 360,
    "combined_rate_rows": 360,
    "exposure_rows": 1080,
    "matched_family_envelope_rows": 72,
    "historical_completed_identity_reexecutions": 0,
    "ODE": 0,
    "benchmark": 0,
}
RAW_LI_SOURCE_SHA256 = "ac76cfef7ca94accf4004267323251cfc6c7b6a68bcd0893ef4e634ad2a91ed9"
RATE_FIELDS = tuple(field.name for field in fields(ThresholdRate))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _bytes_sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        result[key] = value
    return result


def _reject_json_constant(value):
    raise ValueError("NONFINITE_JSON_CONSTANT:" + value)


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_json_object,
                      parse_constant=_reject_json_constant)


def _write_create(path: Path, payload) -> None:
    blob = (json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2)
            + "\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(blob)
        handle.flush()


def _number(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(name + "_REAL_NOT_BOOL_REQUIRED")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(name + "_FINITE_REQUIRED")
    return result


def load_saved_li_rows(root: Path) -> tuple[dict, dict[float, dict]]:
    """Read and validate saved rows; no historical numerical callback is used."""
    profile = _read_json(root / "source_data/PHYS81_SAVED_RATE_PROFILES.json")
    if (profile.get("schema") != "PHYS81_RATE_PROFILE_V2"
            or profile.get("status") != "COMPLETE_SCOPED"):
        raise ValueError("PHYS81_SAVED_PROFILE_NOT_COMPLETE")
    if tuple(profile["identity"]["temperatures_K"]) != SAVED_TEMPERATURES:
        raise ValueError("PHYS81_SAVED_TEMPERATURE_IDENTITY_MISMATCH")
    selected = [row for row in profile["rows"] if row.get("species") == "Li7"]
    if len(selected) != 9:
        raise ValueError("EXACTLY_NINE_SAVED_LI_ROWS_REQUIRED")
    rows = {}
    numeric_names = (
        "T_K", "finite_log10_K", "finite_K_cm3_s",
        "finite_mean_incoming_eV", "finite_mean_excess_over_chemical_eV",
        "finite_dlogK_dT_per_K",
    )
    for row in selected:
        for name in numeric_names:
            _number(row[name], "SAVED_" + name)
        temperature = float(row["T_K"])
        if temperature in rows or temperature not in SAVED_TEMPERATURES:
            raise ValueError("DUPLICATED_OR_UNEXPECTED_SAVED_LI_TEMPERATURE")
        if not isinstance(row["finite_underflow"], bool):
            raise ValueError("SAVED_UNDERFLOW_MUST_BE_BOOL")
        if (row["finite_K_cm3_s"] < 0.0
                or row["finite_underflow"] != (row["finite_K_cm3_s"] == 0.0)
                or not 6.0 < row["finite_mean_incoming_eV"] < 15.0):
            raise ValueError("MALFORMED_SAVED_LI_RATE")
        rows[temperature] = row
    if tuple(sorted(rows)) != SAVED_TEMPERATURES:
        raise ValueError("SAVED_LI_TEMPERATURE_SET_MISMATCH")
    return profile, rows


def study_temperatures() -> tuple[float, ...]:
    """Build only the frozen schedule, not rates or cross sections."""
    grid = tuple(float(t) for t in np.geomspace(255.0, 50000.0, 65))
    temperatures = tuple(sorted(set(grid).union(SAVED_TEMPERATURES)))
    new = set(temperatures).difference(SAVED_TEMPERATURES)
    if len(temperatures) != 72 or len(new) != 63:
        raise ValueError("PHYS82_EXPECTED_72_TEMPERATURES_AND_63_NEW_BASELINES")
    return temperatures


def _model_manifest() -> list[dict]:
    return [{
        "name": name,
        "p": P_W if name.startswith("W") else 1.0,
        "q": 1 if name in ("L1", "W1") else 0,
        "amplitude_cm2": (SIGMA0_CM2 if name in MATCHED_MODEL_NAMES else
                          ZA_SLOPE_CM2_PER_EV * (E0_EV - ICHEMICAL_EV)),
        "matched_CCC_endpoint": name in MATCHED_MODEL_NAMES,
        "classification": ("CONDITIONAL_CCC_MATCHED_FAMILY" if
                           name in MATCHED_MODEL_NAMES else
                           "RECENTERED_HISTORICAL_SLOPE_COMPARATOR"),
    } for name in MODEL_NAMES]


def build_identity(root: Path = ROOT) -> dict:
    """Hash every source .py and all frozen inputs before any new evaluation."""
    root = Path(root).resolve(strict=True)
    relative_files = set(INPUT_FILES)
    relative_files.update(path.relative_to(root).as_posix()
                          for path in (root / "source").rglob("*.py"))
    hashes = {}
    for relative in sorted(relative_files):
        path = root / relative
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError("IDENTITY_FILE_MISSING_OR_OUTSIDE_ROOT:" + relative)
        hashes[relative] = _bytes_sha(path.read_bytes())
    for relative, expected in PINNED_INPUTS.items():
        if hashes.get(relative) != expected:
            raise ValueError("IMMUTABLE_INPUT_PIN_MISMATCH:" + relative)
    for required in ("source/threshold_gap.py", "source/run_study.py",
                     "source/leased_call.py"):
        if required not in hashes:
            raise ValueError("SCIENTIFIC_SOURCE_MISSING:" + required)
    contract = _read_json(root / "CONTRACT.json")
    if (contract["I_eV"] != ICHEMICAL_EV or contract["E0_eV"] != E0_EV
            or contract["sigma0_cm2"] != SIGMA0_CM2
            or contract["T_domain_K"] != [255, 50000]
            or tuple(model["name"] for model in contract["models"]) != MODEL_NAMES
            or tuple(contract["scientific_design"]["exposures_cm3_inverse_s"]) != EXPOSURES):
        raise ValueError("FROZEN_CONTRACT_CONSTANT_MISMATCH")
    physical = contract["physical_contract"]
    if (physical["HH_R10"] != "OFF"
            or physical["production_admission"] != "NOT_ISSUED"
            or physical["coupled_feedback_error_bound"] is not False
            or physical["thermal_sink_per_event_eV"] != ICHEMICAL_EV):
        raise ValueError("FROZEN_PHYSICAL_SCOPE_MISMATCH")
    profile, _ = load_saved_li_rows(root)
    return {
        "schema": "PHYS82_SCIENTIFIC_IDENTITY_V1",
        "files_sha256": hashes,
        "runtime": {"python": platform.python_version(),
                    "numpy": np.__version__, "scipy": scipy.__version__},
        "temperatures_K": list(study_temperatures()),
        "saved_temperatures_K": list(SAVED_TEMPERATURES),
        "exposures_cm3_inverse_s": list(EXPOSURES),
        "models": _model_manifest(),
        "parent_saved_science_id": profile["science_id"],
        "baseline_policy": "REUSE_9_SAVED;UNCHANGED_OPERATOR_AT_63_NEW_T_ONLY",
        "physical_contract": physical,
        "execution": {"ODE": 0, "benchmark": 0,
                      "historical_completed_identity_reexecution": 0},
    }


def load_baseline_model(root: Path = ROOT) -> FiniteWindowCI:
    """Construct the byte-pinned 13-knot PL source; do not evaluate any rate."""
    root = Path(root)
    blob = (root / "source_data/PHYS81_LITERAL.csv").read_bytes()
    if _bytes_sha(blob) != PINNED_INPUTS["source_data/PHYS81_LITERAL.csv"]:
        raise ValueError("PHYS81_LITERAL_PIN_MISMATCH")
    rows = [row for row in csv.DictReader(io.StringIO(blob.decode("utf-8")))
            if row["project_nuclide_label"] == "Li7"]
    if len(rows) != 13:
        raise ValueError("PHYS81_LI_LITERAL_EXPECTS_13_ROWS")
    for row in rows:
        if (row["cross_section_unit"] != "cm^2"
                or row["raw_source_sha256"] != RAW_LI_SOURCE_SHA256
                or row["branch_contract"] != "Li I ground -> Li II ground"):
            raise ValueError("PHYS81_LI_LITERAL_SOURCE_CONTRACT_MISMATCH")
    energies = np.asarray([float(row["incident_energy_eV_literal"])
                           for row in rows])
    sigmas = np.asarray([float(row["cross_section_literal"]) for row in rows])
    if energies[0] != 6.0 or energies[-1] != 15.0 or sigmas[0] != SIGMA0_CM2:
        raise ValueError("PHYS81_CCC_ENDPOINT_MISMATCH")
    return FiniteWindowCI(
        species="Li7", energy_eV=energies, sigma_cm2=sigmas,
        source_identity="sha256:" + RAW_LI_SOURCE_SHA256,
        Ichemical_eV=ICHEMICAL_EV, lower_eV=6.0, upper_eV=15.0,
    )


def saved_baseline_rate(row: dict, parent_science_id: str) -> ThresholdRate:
    """Copy saved quantities, converting log units and derivative algebra only."""
    log_rate = row["finite_log10_K"] * math.log(10.0)
    dlog = row["finite_dlogK_dT_per_K"]
    derivative = (0.0 if dlog == 0.0 else
                  math.copysign(math.exp(log_rate + math.log(abs(dlog))), dlog))
    return ThresholdRate(
        row["T_K"], row["finite_K_cm3_s"], log_rate,
        row["finite_mean_incoming_eV"],
        row["finite_mean_excess_over_chemical_eV"],
        derivative, dlog, row["finite_underflow"],
        dlog != 0.0 and derivative == 0.0, "CCC_6_15", "baseline",
        "PHYS81_SAVED:" + parent_science_id, ICHEMICAL_EV, 6.0, 15.0, 0.0,
    )


def _rate_blob(rate: ThresholdRate) -> dict:
    result = asdict(rate)
    result["log10K_cm3_s"] = rate.log10K_cm3_s
    result["thermal_loss_per_event_eV"] = rate.thermal_loss_per_event_eV
    return result


def _validated_rate_blob(blob, *, component, model, temperature):
    if not isinstance(blob, dict) or set(blob) != set(RATE_FIELDS).union({
        "log10K_cm3_s", "thermal_loss_per_event_eV",
    }):
        raise ValueError("SAVED_RATE_FIELDS_MISMATCH")
    rate = ThresholdRate(**{name: blob[name] for name in RATE_FIELDS})
    if (rate.component != component or rate.model != model
            or rate.temperature_K != temperature
            or rate.Ichemical_eV != ICHEMICAL_EV
            or blob["thermal_loss_per_event_eV"] != ICHEMICAL_EV):
        raise ValueError("SAVED_RATE_BINDING_MISMATCH")
    if blob["log10K_cm3_s"] != rate.log10K_cm3_s:
        raise ValueError("SAVED_RATE_LOG_UNIT_MISMATCH")
    expected_window = {"baseline": (6.0, 15.0),
                       "gap": (ICHEMICAL_EV, 6.0),
                       "total": (ICHEMICAL_EV, 15.0)}[component]
    if (rate.lower_eV, rate.upper_eV) != expected_window:
        raise ValueError("SAVED_RATE_SUPPORT_MISMATCH")
    return rate


def validate_saved_output(result: dict, identity: dict, saved_rows: dict) -> None:
    """Validate stored evidence only; never evaluate a scientific callback."""
    if (result.get("schema") != SCHEMA
            or result.get("status") != "COMPLETE_SCOPED"
            or result.get("identity") != identity
            or result.get("science_id") != _digest(identity)):
        raise ValueError("SAVED_STUDY_IDENTITY_OR_STATUS_MISMATCH")
    checksum_payload = {k: v for k, v in result.items() if k != "payload_sha256"}
    if result.get("payload_sha256") != _digest(checksum_payload):
        raise ValueError("SAVED_STUDY_PAYLOAD_HASH_MISMATCH")
    if result.get("counts") != EXPECTED_COUNTS or result.get("models") != _model_manifest():
        raise ValueError("SAVED_STUDY_COUNTS_OR_MODELS_MISMATCH")
    if result.get("physical_contract") != identity["physical_contract"]:
        raise ValueError("SAVED_STUDY_PHYSICAL_CONTRACT_MISMATCH")
    temperatures = tuple(identity["temperatures_K"])
    if len(result["baseline_rows"]) != 72 or len(result["rate_rows"]) != 360:
        raise ValueError("SAVED_STUDY_RATE_ROW_COUNT_MISMATCH")
    baselines = {}
    for row in result["baseline_rows"]:
        temperature = _number(row["T_K"], "SAVED_BASELINE_T")
        if temperature not in temperatures or temperature in baselines:
            raise ValueError("SAVED_BASELINE_TEMPERATURE_SET_MISMATCH")
        rate = _validated_rate_blob(row["rate"], component="baseline",
                                    model="CCC_6_15", temperature=temperature)
        baselines[temperature] = rate
        expected_origin = ("PHYS81_SAVED" if temperature in saved_rows
                           else "NEW_UNCHANGED_FINITE_OPERATOR")
        if row["origin"] != expected_origin:
            raise ValueError("SAVED_BASELINE_ORIGIN_MISMATCH")
        if temperature in saved_rows:
            original = saved_rows[temperature]
            if row["parent_saved_row"] != original:
                raise ValueError("SAVED_PARENT_ROW_NOT_PRESERVED")
            for saved_key, rate_key in (
                ("finite_K_cm3_s", "K_cm3_s"),
                ("finite_mean_incoming_eV", "mean_incoming_eV"),
                ("finite_mean_excess_over_chemical_eV", "mean_excess_over_chemical_eV"),
                ("finite_dlogK_dT_per_K", "dlogK_dT_per_K"),
                ("finite_underflow", "float64_underflow"),
            ):
                if row["rate"][rate_key] != original[saved_key]:
                    raise ValueError("SAVED_PARENT_RATE_VALUE_CHANGED:" + rate_key)
        elif row["parent_saved_row"] is not None:
            raise ValueError("NEW_BASELINE_CANNOT_CLAIM_PARENT_ROW")
    expected_rate_keys = {(t, model) for t in temperatures for model in MODEL_NAMES}
    rates = {}
    for row in result["rate_rows"]:
        key = (_number(row["T_K"], "SAVED_RATE_T"), row["model"])
        if key not in expected_rate_keys or key in rates:
            raise ValueError("SAVED_RATE_CARTESIAN_GRID_MISMATCH")
        gap = _validated_rate_blob(row["gap"], component="gap",
                                  model=key[1], temperature=key[0])
        total = _validated_rate_blob(row["total"], component="total",
                                    model=key[1], temperature=key[0])
        if row["matched_CCC_family_member"] is not (key[1] in MATCHED_MODEL_NAMES):
            raise ValueError("SAVED_RATE_FAMILY_MEMBERSHIP_MISMATCH")
        if not total.logK_cm3_s >= max(gap.logK_cm3_s, baselines[key[0]].logK_cm3_s):
            raise ValueError("SAVED_TOTAL_RATE_ORDER_MISMATCH")
        if row["gap_fraction"] != total.gap_fraction:
            raise ValueError("SAVED_GAP_FRACTION_MISMATCH")
        _number(row["total_over_baseline"], "SAVED_ENHANCEMENT")
        _number(row["log_total_over_baseline"], "SAVED_LOG_ENHANCEMENT")
        rates[key] = (gap, total)
    if set(rates) != expected_rate_keys:
        raise ValueError("SAVED_RATE_CARTESIAN_GRID_INCOMPLETE")
    expected_exposure_keys = {(t, model, exposure) for t in temperatures
                              for model in MODEL_NAMES for exposure in EXPOSURES}
    seen = set()
    if len(result["exposure_rows"]) != 1080:
        raise ValueError("SAVED_EXPOSURE_ROW_COUNT_MISMATCH")
    for row in result["exposure_rows"]:
        key = (_number(row["T_K"], "SAVED_EXPOSURE_T"), row["model"],
               _number(row["exposure_cm3_inverse_s"], "SAVED_EXPOSURE"))
        if key not in expected_exposure_keys or key in seen:
            raise ValueError("SAVED_EXPOSURE_CARTESIAN_GRID_MISMATCH")
        seen.add(key)
        if row["prescribed_T_ne_only"] is not True or row["coupled_feedback_error_bound"] is not False:
            raise ValueError("SAVED_EXPOSURE_SCOPE_MISMATCH")
        for field in ("baseline_probability", "gap_alone_probability",
                      "total_probability", "delta_probability",
                      "delta_probability_upper_bound",
                      "delta_probability_unattenuated_upper_bound"):
            probability = _number(row[field], "SAVED_" + field)
            if not 0.0 <= probability <= 1.0:
                raise ValueError("SAVED_EXPOSURE_PROBABILITY_OUT_OF_RANGE")
        if not (row["delta_probability"] <= row["delta_probability_upper_bound"] + 2e-15
                <= row["delta_probability_unattenuated_upper_bound"] + 4e-15):
            raise ValueError("SAVED_EXPOSURE_BOUND_ORDER_MISMATCH")
    if seen != expected_exposure_keys:
        raise ValueError("SAVED_EXPOSURE_CARTESIAN_GRID_INCOMPLETE")
    if len(result["family_envelope_rows"]) != 72:
        raise ValueError("SAVED_ENVELOPE_ROW_COUNT_MISMATCH")
    envelope_temperatures = set()
    for row in result["family_envelope_rows"]:
        temperature = _number(row["T_K"], "SAVED_ENVELOPE_T")
        if temperature not in temperatures or temperature in envelope_temperatures:
            raise ValueError("SAVED_ENVELOPE_TEMPERATURE_SET_MISMATCH")
        envelope_temperatures.add(temperature)
        if (row["lower_rate_model"] != "W0" or row["upper_rate_model"] != "L1"
                or row["is_physical_confidence_interval"] is not False
                or row["ZA1969_included"] is not False):
            raise ValueError("SAVED_ENVELOPE_SCOPE_MISMATCH")
        if (row["lower_total_logK_cm3_s"] != rates[(temperature, "W0")][1].logK_cm3_s
                or row["upper_total_logK_cm3_s"] != rates[(temperature, "L1")][1].logK_cm3_s):
            raise ValueError("SAVED_ENVELOPE_RATE_BINDING_MISMATCH")


def _artifact_paths(output: Path):
    return tuple(Path(str(output) + suffix)
                 for suffix in (".identity.json", ".attempt.json", ".complete.json"))


def _claim_path(root: Path, science_id: str) -> Path:
    return root / "results/IDENTITY_CLAIMS" / (science_id + ".json")


def _claimed_output(root: Path, identity: dict) -> Path:
    science_id = _digest(identity)
    claim = _read_json(_claim_path(root, science_id))
    if (claim.get("schema") != "PHYS82_EXCLUSIVE_SCIENCE_ID_CLAIM_V1"
            or claim.get("science_id") != science_id):
        raise ValueError("SCIENCE_ID_CLAIM_MISMATCH")
    relative = claim.get("output_relative_to_study")
    if not isinstance(relative, str):
        raise ValueError("SCIENCE_ID_CLAIM_OUTPUT_MISSING")
    output = (root / relative).resolve()
    if not output.is_relative_to(root / "results"):
        raise ValueError("SCIENCE_ID_CLAIM_OUTPUT_OUTSIDE_RESULTS")
    return output


def _resume(root: Path, output: Path, identity: dict, saved_rows: dict) -> dict:
    if _claimed_output(root, identity) != output:
        raise ValueError("SCIENCE_ID_CLAIM_POINTS_TO_A_DIFFERENT_OUTPUT")
    identity_path, attempt_path, complete_path = _artifact_paths(output)
    if not all(path.is_file() for path in (identity_path, attempt_path, complete_path)):
        raise ValueError("INCOMPLETE_SAVED_STUDY_REQUIRES_INSPECTION_NO_REPLAY")
    frozen = _read_json(identity_path)
    attempt = _read_json(attempt_path)
    complete = _read_json(complete_path)
    science_id = _digest(identity)
    if (frozen.get("identity") != identity or frozen.get("science_id") != science_id
            or attempt.get("science_id") != science_id
            or complete.get("science_id") != science_id
            or complete.get("status") != "COMPLETE_SCOPED"):
        raise ValueError("SAVED_COMPLETION_RECORD_IDENTITY_MISMATCH")
    if complete.get("output_file_sha256") != _bytes_sha(output.read_bytes()):
        raise ValueError("SAVED_OUTPUT_FILE_HASH_MISMATCH")
    result = _read_json(output)
    validate_saved_output(result, identity, saved_rows)
    return {"status": "SKIPPED_IDENTICAL_COMPLETE", "science_id": science_id,
            "output": str(output), "scientific_callbacks": 0,
            "counts": result["counts"]}


def run_study(root: Path = ROOT, output: Path | None = None) -> dict:
    root = Path(root).resolve(strict=True)
    output = (root / "results/THRESHOLD_STUDY.json" if output is None
              else Path(output).resolve())
    if not output.is_relative_to(root / "results"):
        raise ValueError("PHYS82_OUTPUT_MUST_BE_WITHIN_THIS_STUDY_RESULTS_DIRECTORY")
    identity = build_identity(root)
    science_id = _digest(identity)
    profile, saved_rows = load_saved_li_rows(root)
    if output.exists():
        return _resume(root, output, identity, saved_rows)
    claim_path = _claim_path(root, science_id)
    if claim_path.exists():
        claimed_output = _claimed_output(root, identity)
        if claimed_output.is_file():
            # Changing the requested filename cannot authorize science replay.
            skipped = _resume(root, claimed_output, identity, saved_rows)
            skipped["requested_output"] = str(output)
            return skipped
        raise FileExistsError("SCIENCE_ID_ALREADY_ATTEMPTED_INSPECT_BEFORE_ANY_REPLAY")
    identity_path, attempt_path, complete_path = _artifact_paths(output)
    if any(path.exists() for path in (identity_path, attempt_path, complete_path)):
        raise FileExistsError("PRIOR_ATTEMPT_REQUIRES_INSPECTION_NO_SILENT_REPLAY")
    # The identity claim arbitrates callers even with different output names.
    _write_create(claim_path, {
        "schema": "PHYS82_EXCLUSIVE_SCIENCE_ID_CLAIM_V1",
        "science_id": science_id, "claimed_utc": _utc(),
        "output_relative_to_study": output.relative_to(root).as_posix(),
    })
    _write_create(identity_path, {
        "schema": "PHYS82_FROZEN_IDENTITY_V1", "frozen_utc": _utc(),
        "science_id": science_id, "identity": identity,
    })
    _write_create(attempt_path, {
        "schema": "PHYS82_CREATE_ONLY_ATTEMPT_V1", "started_utc": _utc(),
        "science_id": science_id, "status": "STARTED",
        "historical_runner_called": False,
    })
    models = named_models(source_identity="sha256:" +
                          identity["files_sha256"]["source_data/LI_THRESHOLD_SOURCE_CONTRACT.json"])
    baseline_model = load_baseline_model(root)
    baseline_rows, rate_rows, exposure_rows, family_rows = [], [], [], []
    actual_new_baselines, actual_gap_evaluations = 0, 0
    for temperature in identity["temperatures_K"]:
        if temperature in saved_rows:
            baseline = saved_baseline_rate(saved_rows[temperature], profile["science_id"])
            origin, parent_row = "PHYS81_SAVED", saved_rows[temperature]
        else:
            # A separate explicit guard protects the historical identity policy.
            if temperature in SAVED_TEMPERATURES:
                raise AssertionError("HISTORICAL_TEMPERATURE_MUST_NEVER_BE_REEVALUATED")
            baseline = from_finite_rate(baseline_model.evaluate(temperature))
            actual_new_baselines += 1
            origin, parent_row = "NEW_UNCHANGED_FINITE_OPERATOR", None
        baseline_rows.append({
            "T_K": temperature, "origin": origin, "rate": _rate_blob(baseline),
            "parent_saved_row": parent_row,
        })
        totals = {}
        for name, model in models.items():
            gap = model.evaluate(temperature)
            actual_gap_evaluations += 1
            total = combine_rates(baseline, gap)
            totals[name] = total
            log_enhancement = total.logK_cm3_s - baseline.logK_cm3_s
            rate_rows.append({
                "T_K": temperature, "model": name,
                "matched_CCC_family_member": name in MATCHED_MODEL_NAMES,
                "gap": _rate_blob(gap), "total": _rate_blob(total),
                "gap_fraction": total.gap_fraction,
                "log_total_over_baseline": log_enhancement,
                "total_over_baseline": math.exp(log_enhancement),
            })
            for exposure in EXPOSURES:
                exposure_rows.append({
                    "T_K": temperature, "model": name,
                    **asdict(fixed_exposure(baseline, gap, exposure)),
                })
        low, high = totals["W0"], totals["L1"]
        if any(not low.logK_cm3_s <= totals[name].logK_cm3_s <= high.logK_cm3_s
               for name in MATCHED_MODEL_NAMES):
            raise ArithmeticError("CONDITIONAL_FAMILY_RATE_ORDER_FAILED")
        family_rows.append({
            "T_K": temperature, "lower_rate_model": "W0",
            "upper_rate_model": "L1",
            "lower_total_logK_cm3_s": low.logK_cm3_s,
            "upper_total_logK_cm3_s": high.logK_cm3_s,
            "upper_over_lower_rate": math.exp(high.logK_cm3_s - low.logK_cm3_s),
            "minimum_mean_incoming_eV": high.mean_incoming_eV,
            "maximum_mean_incoming_eV": low.mean_incoming_eV,
            "is_physical_confidence_interval": False,
            "ZA1969_included": False,
        })
    if actual_new_baselines != 63 or actual_gap_evaluations != 360:
        raise AssertionError("NEW_SCIENTIFIC_CALLBACK_COUNT_MISMATCH")
    # Detect any code/input change during the execution before publication.
    if build_identity(root) != identity:
        raise ValueError("SCIENTIFIC_IDENTITY_CHANGED_DURING_EXECUTION")
    result = {
        "schema": SCHEMA, "status": "COMPLETE_SCOPED",
        "completed_utc": _utc(), "science_id": science_id,
        "identity": identity, "models": _model_manifest(),
        "counts": dict(EXPECTED_COUNTS),
        "physical_contract": identity["physical_contract"],
        "coverage": [model.coverage() for model in models.values()],
        "baseline_rows": baseline_rows, "rate_rows": rate_rows,
        "exposure_rows": exposure_rows, "family_envelope_rows": family_rows,
        "source_consistency": {
            "CCC_endpoint_cm2": SIGMA0_CM2,
            "ZA1969_independent_endpoint_cm2": models["ZA1969"].amplitude_cm2,
            "ZA1969_endpoint_over_CCC": models["ZA1969"].amplitude_cm2 / SIGMA0_CM2,
            "ZA1969_forced_to_CCC": False,
        },
        "interpretation": {
            "new_gap_models_are_conditional": True,
            "relative_enhancement_is_absolute_observable": False,
            "fixed_exposure_difference_formula": "exp(-Lambda*Kbase)*[-expm1(-Lambda*Kgap)]",
            "thermal_loss_per_event_eV": ICHEMICAL_EV,
            "physical_threshold_gap_coverage": "OPEN",
            "physical_tail_above_15_eV": "OPEN",
            "numerical_checks_are_continuum_error_certificates": False,
            "coupled_feedback_error_bound": False,
            "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
        },
    }
    result["payload_sha256"] = _digest(result)
    validate_saved_output(result, identity, saved_rows)
    _write_create(output, result)
    _write_create(complete_path, {
        "schema": "PHYS82_CREATE_ONLY_COMPLETION_V1",
        "status": "COMPLETE_SCOPED", "completed_utc": _utc(),
        "science_id": science_id,
        "output_file_sha256": _bytes_sha(output.read_bytes()),
        "payload_sha256": result["payload_sha256"],
        "counts": dict(EXPECTED_COUNTS),
    })
    return {"status": "COMPLETE_SCOPED", "science_id": science_id,
            "output": str(output), "counts": dict(EXPECTED_COUNTS),
            "scientific_callbacks": {"new_baseline": actual_new_baselines,
                                     "gap": actual_gap_evaluations,
                                     "combination": 360, "fixed_exposure": 1080}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(run_study(arguments.root, arguments.output),
                     ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
