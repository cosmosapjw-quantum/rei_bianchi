#!/usr/bin/env python3
"""Source-pinned KF96 number-rate readout of saved warm P01 OFF states."""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np


TOL = 5e-13
RATIO = 3.0 / 38.0
NU = (-1, 1, 0, 1, -1, 0)
SPECIES = ("HI", "HII", "HeI", "HeII", "HeIII", "e")


def checked_hash(path: Path, expected: str) -> str:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"INPUT_HASH_MISMATCH: {path}: {actual} != {expected}")
    return actual


def near(candidate: float, reference: Decimal, label: str) -> float:
    if not math.isfinite(candidate):
        raise ValueError(f"NONFINITE_RESULT: {label}")
    if reference == 0:
        if candidate != 0:
            raise ValueError(f"STRUCTURAL_ZERO_MISMATCH: {label}: {candidate}")
        return 0.0
    diff = abs(Decimal.from_float(candidate) - reference) / abs(reference)
    error = float(diff)
    if error > TOL:
        raise ValueError(f"DECIMAL_MISMATCH: {label}: {error}")
    return error


def validate_ionic(xh: float, x2: float, x3: float) -> None:
    if not all(math.isfinite(x) and 0 <= x <= 1 for x in (xh, x2, x3)):
        raise ValueError("IONIC_DOMAIN")
    if x2 + x3 > 1:
        raise ValueError("HE_NORMALIZATION")


def validate_times(times: list[float]) -> None:
    if len(times) != 17 or any(not math.isfinite(x) for x in times):
        raise ValueError("TIME_DOMAIN")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("TIME_NOT_STRICT")
    if any(x != i * 6_250_000_000.0 for i, x in enumerate(times)):
        raise ValueError("FROZEN_TIME_GRID_MISMATCH")


def candidate(k: float, n_h_cm3: float, xh: float, x2: float, x3: float) -> dict:
    validate_ionic(xh, x2, x3)
    if not math.isfinite(n_h_cm3) or n_h_cm3 <= 0 or not math.isfinite(k) or k <= 0:
        raise ValueError("DENSITY_OR_COEFFICIENT_DOMAIN")
    nh = 1e6 * n_h_cm3
    nhe = RATIO * nh
    nhi = nh * (1 - xh)
    nheiii = nhe * x3
    rate = k * nhi * nheiii
    if nhi > 0 and nheiii > 0 and rate <= 0:
        raise ValueError("POSITIVE_PRODUCT_UNDERFLOW")
    return {"nH_m3": nh, "nHe_m3": nhe, "nHI_m3": nhi, "nHeIII_m3": nheiii,
            "rate_m3_s": rate, "species_rates_m3_s": [v * rate for v in NU],
            "fraction_rates_s": [rate / nh, rate / nhe, -rate / nhe],
            "primary_photon_count_rate_m3_s": rate}


def decimal_reference(n_h_cm3: float, xh: float, x2: float, x3: float) -> dict:
    with localcontext() as ctx:
        ctx.prec = 70
        nh = Decimal(1_000_000) * Decimal.from_float(n_h_cm3)
        nhe = nh * Decimal(3) / Decimal(38)
        nhi = nh * (Decimal(1) - Decimal.from_float(xh))
        nheiii = nhe * Decimal.from_float(x3)
        rate = Decimal("1e-20") * nhi * nheiii
        return {"nH_m3": nh, "nHe_m3": nhe, "nHI_m3": nhi, "nHeIII_m3": nheiii,
                "rate_m3_s": rate, "species_rates_m3_s": [rate * Decimal(v) for v in NU],
                "fraction_rates_s": [rate / nh, rate / nhe, -rate / nhe],
                "primary_photon_count_rate_m3_s": rate}


def controls(provider, provider_args: dict, source_path: Path, expected_hash: str) -> dict:
    passed = {}
    for name, args in (("fully_ionized_h_zero", (1, 0, 0.5)),
                       ("heiii_zero", (0.5, 0.5, 0))):
        result = candidate(1e-20, 1e-4, *args)
        assert result["rate_m3_s"] == 0
        passed[name] = True
    for args in ((-0.1, 0, 0), (0.5, 0.8, 0.3)):
        try:
            validate_ionic(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid ionic accepted")
    passed["negative_and_overnormalized_ionic_reject"] = True
    for times in ([0.0] * 17, [float("nan")] + [i * 6_250_000_000.0 for i in range(1, 17)]):
        try:
            validate_times(times)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid time accepted")
    passed["duplicate_and_nonfinite_time_reject"] = True
    for name, temperature, kwargs in (("kf96_999K_reject", 999, provider_args),
                                      ("missing_conflict_ack_reject", 50_000,
                                       {**provider_args, "acknowledge_source_conflict": False})):
        try:
            provider(temperature, **kwargs)
        except ValueError:
            passed[name] = True
        else:
            raise AssertionError(f"{name} accepted")
    try:
        candidate(1e-20, float("nan"), 0.5, 0.1, 0.1)
    except ValueError:
        passed["nonfinite_density_reject"] = True
    else:
        raise AssertionError("nonfinite density accepted")
    try:
        checked_hash(source_path, "0" * 64)
    except ValueError:
        passed["intentional_hash_mismatch_reject"] = True
    else:
        raise AssertionError("hash mismatch accepted")
    assert len(passed) == 8
    return passed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true", required=True)
    args = parser.parse_args()
    t0 = time.monotonic()
    contract = json.loads(args.contract.read_text())
    root = Path(contract["input_root"])
    provider_root = Path(contract["provider_root"])
    checked = {}
    for item in contract["immutable_inputs"]:
        path = root / item["path"]
        checked[str(path)] = checked_hash(path, item["sha256"])
    for item in contract["provider_files"]:
        path = provider_root / item["path"]
        checked[str(path)] = checked_hash(path, item["sha256"])
    sys.path.insert(0, str(provider_root))
    from provider._kf96 import rate as kf96_rate

    input_json = json.loads((root / contract["immutable_inputs"][1]["path"]).read_text())
    metadata = input_json["metadata"]
    if metadata["execution_path"] != "production SourceBoundConditional" or metadata["optional_CR_RCT_HH"] != "OFF":
        raise ValueError("P01_PRODUCTION_OFF_IDENTITY_MISMATCH")
    history = input_json["history"]
    if len(history) != 17:
        raise ValueError("HISTORY_LENGTH_MISMATCH")
    with np.load(root / contract["immutable_inputs"][0]["path"], allow_pickle=False) as npz:
        for key, expected in contract["saved_data_mapping"]["shapes"].items():
            if list(npz[key].shape) != expected:
                raise ValueError(f"NPZ_SHAPE_MISMATCH: {key}")
        states = npz["states"]
        npz_times = npz["times_s"]
        times = [float(row["time_s"]) for row in history]
        validate_times(times)
        if any(float(npz_times[i]) != t for i, t in enumerate(times)):
            raise ValueError("NPZ_JSON_TIME_MISMATCH")
        for j, field in enumerate(("xHII", "xHeII", "xHeIII")):
            if any(float(states[j, i]) != float(row[field]) for i, row in enumerate(history)):
                raise ValueError(f"NPZ_JSON_IONIC_MISMATCH: {field}")
    selected = contract["selected_provider"]
    provider_args = {"source_id": selected["source_id"], "distribution": selected["distribution"],
                     "acknowledge_source_conflict": True, "temperature_unit": selected["temperature_unit"],
                     "initial_state": selected["initial_state"], "isotope_basis": selected["isotope_basis"],
                     "relative_drift_m_s": selected["relative_drift_m_s"],
                     "radiation_model": selected["radiation_model"]}
    rows = []
    refs = []
    max_error = 0.0
    max_ne_error = 0.0
    max_cgs_error = 0.0
    for i, row in enumerate(history):
        xh, x2, x3 = (float(row[f]) for f in ("xHII", "xHeII", "xHeIII"))
        validate_ionic(xh, x2, x3)
        temperature = float(row["T_K"])
        n_h_cm3 = float(row["nH_cm3"])
        if not math.isfinite(temperature) or not 30_000 <= temperature <= 110_000 or not 1_000 <= temperature <= 10_000_000:
            raise ValueError(f"TEMPERATURE_DOMAIN: epoch {i}")
        packet = kf96_rate(temperature, unit="m3 s-1", **provider_args)
        cgs = kf96_rate(temperature, unit="cm3 s-1", **provider_args)
        for field, expected in (("source_id", selected["source_id"]), ("reaction_id", selected["reaction_id"]),
                                ("unit", selected["unit"]), ("rate_token", selected["rate_token"])):
            if packet[field] != expected:
                raise ValueError(f"KF96_PROVIDER_PACKET_MISMATCH: epoch {i} {field}")
        if cgs["unit"] != "cm3 s-1" or cgs["rate_token"] != selected["native_rate_token_cm3_s"]:
            raise ValueError(f"KF96_CGS_PACKET_MISMATCH: epoch {i}")
        result = candidate(float(packet["rate_token"]), n_h_cm3, xh, x2, x3)
        ref = decimal_reference(n_h_cm3, xh, x2, x3)
        for name in ("nH_m3", "nHe_m3", "nHI_m3", "nHeIII_m3", "rate_m3_s", "primary_photon_count_rate_m3_s"):
            max_error = max(max_error, near(result[name], ref[name], f"epoch {i} {name}"))
        for name in ("species_rates_m3_s", "fraction_rates_s"):
            for j, (v, d) in enumerate(zip(result[name], ref[name])):
                max_error = max(max_error, near(v, d, f"epoch {i} {name}[{j}]"))
        rate = result["rate_m3_s"]
        assert result["species_rates_m3_s"][0] + result["species_rates_m3_s"][1] == 0
        assert result["species_rates_m3_s"][2] + result["species_rates_m3_s"][3] + result["species_rates_m3_s"][4] == 0
        assert result["species_rates_m3_s"][5] == 0
        max_error = max(max_error, near(result["fraction_rates_s"][0] * result["nH_m3"], ref["rate_m3_s"], f"epoch {i} H fraction"))
        max_error = max(max_error, near(result["fraction_rates_s"][1] * result["nHe_m3"], ref["rate_m3_s"], f"epoch {i} HeII fraction"))
        max_error = max(max_error, near(result["fraction_rates_s"][2] * result["nHe_m3"], -ref["rate_m3_s"], f"epoch {i} HeIII fraction"))
        ne_recon = n_h_cm3 * xh + RATIO * n_h_cm3 * (x2 + 2 * x3)
        ne_saved = float(row["ne_cm3"])
        if not math.isfinite(ne_saved) or ne_saved <= 0:
            raise ValueError(f"SAVED_NE_DOMAIN: epoch {i}")
        ne_error = abs(ne_recon - ne_saved) / ne_saved
        max_ne_error = max(max_ne_error, ne_error)
        if ne_error > TOL:
            raise ValueError(f"NE_CROSSCHECK: epoch {i}: {ne_error}")
        cgs_rate = float(cgs["rate_token"]) * (result["nHI_m3"] / 1e6) * (result["nHeIII_m3"] / 1e6) * 1e6
        cgs_error = abs(cgs_rate - rate) / rate if rate > 0 else abs(cgs_rate)
        max_cgs_error = max(max_cgs_error, cgs_error)
        if cgs_error > TOL:
            raise ValueError(f"CGS_CROSSCHECK: epoch {i}: {cgs_error}")
        rows.append({"epoch": i, "time_s": times[i], "T_K": temperature, "nH_cm3": n_h_cm3,
                     "xHII": xh, "xHeII": x2, "xHeIII": x3, **result,
                     "species_order": SPECIES,
                     "fraction_rate_order": ("xHII", "xHeII", "xHeIII"),
                     "source_id": selected["source_id"], "reaction_id": selected["reaction_id"]})
        refs.append(ref)
    with localcontext() as ctx:
        ctx.prec = 70
        dts = [Decimal.from_float(times[i+1]) - Decimal.from_float(times[i]) for i in range(16)]
        n0 = rows[0]["nH_m3"]
        n0d = refs[0]["nH_m3"]
        samples = [rows[i]["rate_m3_s"] * (n0 / rows[i]["nH_m3"]) for i in range(17)]
        dsamples = [refs[i]["rate_m3_s"] * (n0d / refs[i]["nH_m3"]) for i in range(17)]
        exposure = sum((times[i+1]-times[i]) * (samples[i]+samples[i+1])/2 for i in range(16))
        dexposure = sum(dts[i] * (dsamples[i]+dsamples[i+1])/2 for i in range(16))
        max_error = max(max_error, near(exposure, dexposure, "saved-grid comoving exposure"))
        fraction_exposures = []
        for j in range(3):
            val = sum((times[i+1]-times[i]) * (rows[i]["fraction_rates_s"][j]+rows[i+1]["fraction_rates_s"][j])/2 for i in range(16))
            ref_val = sum(dts[i] * (refs[i]["fraction_rates_s"][j]+refs[i+1]["fraction_rates_s"][j])/2 for i in range(16))
            max_error = max(max_error, near(val, ref_val, f"saved-grid fraction exposure {j}"))
            fraction_exposures.append(val)
    control_status = controls(kf96_rate, provider_args, provider_root / contract["provider_files"][0]["path"],
                              contract["provider_files"][0]["sha256"])
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "per_epoch.json").write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n")
    validation = {"status": "PASS_SCOPED_SAVED_BASELINE_NUMBER_RATE_READOUT",
                  "contract_sha256": hashlib.sha256(args.contract.read_bytes()).hexdigest(),
                  "input_hashes": checked, "provider_calls": 36, "saved_epochs": 17,
                  "controls": control_status, "arithmetic_max_relative_error": max_error,
                  "ne_max_relative_error": max_ne_error, "cgs_max_relative_error": max_cgs_error,
                  "saved_grid_piecewise_linear_rate_exposure": {
                      "label": "SAVED_GRID_PIECEWISE_LINEAR_RATE_EXPOSURE_DIAGNOSTIC",
                      "comoving_events_per_initial_m3": exposure,
                      "fraction_exposures_xHII_xHeII_xHeIII": fraction_exposures,
                      "integration_error": "NOT_ESTIMATED"},
                  "missing_moments": {"mean_photon_energy": None, "heat": None, "spectrum": None,
                                      "reabsorption": None},
                  "scope": "Postprocessing of immutable P01 warm RCT-OFF saved baseline; no RCT-ON solver, continuum error, N5 materiality, or global admission.",
                  "python_version": platform.python_version(), "numpy_version": np.__version__,
                  "elapsed_wall_s": time.monotonic() - t0}
    (args.output / "VALIDATION.json").write_text(json.dumps(validation, indent=2, allow_nan=False) + "\n")
    (args.output / "REPORT_KO.md").write_text(
        "# RCT 저장 기준선 반응률 계산\n\n"
        "17개 warm P01 RCT-OFF epoch에서 선택된 KF96 명목 계수의 proper SI 수 반응률을 계산했습니다. "
        "이온종 및 분율 변화율, cgs 대조와 Decimal 70자리 기준값이 계약 오차 안에 있습니다.\n\n"
        f"최대 반응률: {max(r['rate_m3_s'] for r in rows):.17g} m^-3 s^-1. "
        f"저장 격자 선형 노출 진단: {exposure:.17g} events/initial m^3. "
        "이는 RCT-ON 변화나 물질성 판단이 아닙니다. 다음 gate는 독립 Astra 검토와 누락된 광자 에너지 모멘트입니다.\n")
    print(json.dumps({"status": validation["status"], "output": str(args.output),
                      "max_relative_error": max_error, "max_rate_m3_s": max(r["rate_m3_s"] for r in rows),
                      "exposure": exposure, "elapsed_wall_s": validation["elapsed_wall_s"]}))


if __name__ == "__main__":
    main()
