#!/usr/bin/env python3
"""Accept the Case-A EVENTS bridge at two saved production stages.

This invokes the exact production preflight, NativeConsumer and
ProductionInterval.stage. The second point is an explicitly saved-state probe,
not a new evolved endpoint. No interval solver or Decimal oracle is rerun.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import shlex
import sys
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
PRODUCTION_PYTHON = REPOSITORY / "rust/rei_microphysics/python"
DEFAULT_PACKET = REPOSITORY / "research/physical_provider_20261010"
ORACLE_SHA256 = "57c0ad93cc2cfe8edebf4728bb4405e2457ca5f77e90137896c0132222d7522f"
COMPONENT_TOL = 3e-11
GROSS_TOL = 3e-11
INVARIANT_TOL = 1e-12
EV, KB = 1.602176634e-12, 1.380649e-16
CHI = np.asarray([13.598434599702, 24.587389011, 54.41776])
PRIMITIVE_SLICES = {
    "CI": (0, 3), "RR": (3, 6), "DR": (6, 8), "PI": (8, 11),
    "RR_kinetic": (11, 14), "DR_kinetic": (14, 16),
    "PI_heat": (16, 19), "PI_absorbed_energy": (19, 22),
}
EVENTS_SCHEMA = {
    "primitive_slices": PRIMITIVE_SLICES,
    "species_HI_HII_HeI_HeII_HeIII": [22, 27], "electron": 27,
    "photon_number": 28, "photon_power": 29, "thermal": 30,
    "binding": 31, "escape": 32, "external": 33, "temperature": 34,
    "number_residual": 35, "energy_residual": 36,
    "rates": "proper cm^-3 s^-1", "powers": "proper erg cm^-3 s^-1",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def load_production():
    # Load this checkout's exact production module and its build validator.
    # Their digests are checked by NativeConsumer's prelaunch build receipt.
    sys.path.insert(0, str(PRODUCTION_PYTHON))
    name = "rei_event_probe_source_bound_interval"
    path = PRODUCTION_PYTHON / "source_bound_interval.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fsum(values):
    return math.fsum(float(value) for value in np.asarray(values).ravel())


def check_scaled(checks, name, actual, expected, scale, limit):
    actual, expected, scale = np.broadcast_arrays(
        np.asarray(actual, dtype=float), np.asarray(expected, dtype=float),
        np.asarray(scale, dtype=float))
    finite = bool(np.isfinite(actual).all() and np.isfinite(expected).all()
                  and np.isfinite(scale).all() and (scale >= 0).all())
    delta = np.abs(actual - expected)
    # A genuinely absent channel must be exactly zero; no positive absolute
    # floor is introduced to conceal a spurious source in that channel.
    exact_zero = bool(np.all(delta[scale == 0] == 0)) if finite else False
    errors = delta[scale > 0] / scale[scale > 0] if finite else np.asarray([])
    maximum = float(np.max(errors)) if errors.size else 0.0
    checks.append({
        "id": name, "pass": finite and exact_zero and maximum <= limit,
        "limit": limit, "scaled_max": maximum if finite else None,
        "zero_scale_exact": exact_zero, "finite": finite,
        "actual": actual.tolist(), "expected": expected.tolist(),
        "normalization": scale.tolist(),
    })


def check_boolean(checks, name, condition, detail=None):
    checks.append({"id": name, "pass": bool(condition), "detail": detail})


def split_primitives(events):
    return {name: events[lo:hi] for name, (lo, hi) in PRIMITIVE_SLICES.items()}


def gross_scales(p):
    edge = p["PI"] + p["CI"] + p["RR"]
    edge = edge.copy()
    edge[1] += fsum(p["DR"])
    species = np.asarray([edge[0], edge[0], edge[1], edge[1] + edge[2], edge[2]])
    thermal = (fsum(p["PI_heat"]) + EV * fsum(CHI * p["CI"])
               + fsum(p["RR_kinetic"]) + fsum(p["DR_kinetic"]))
    binding = EV * fsum(CHI * edge)
    escape = (EV * (fsum(CHI * p["RR"]) + CHI[1] * fsum(p["DR"]))
              + fsum(p["RR_kinetic"]) + fsum(p["DR_kinetic"]))
    return dict(edge=edge, species=species, electron=fsum(edge),
                thermal=thermal, binding=binding, escape=escape)


def source_expectation(p, source_number, source_power):
    net = p["PI"] + p["CI"] - p["RR"]
    net = net.copy()
    net[1] -= fsum(p["DR"])
    species = np.asarray([-net[0], net[0], -net[1], net[1] - net[2], net[2]])
    thermal = (fsum(p["PI_heat"]) - EV * fsum(CHI * p["CI"])
               - fsum(p["RR_kinetic"]) - fsum(p["DR_kinetic"]))
    escape = (EV * (fsum(CHI * p["RR"]) + CHI[1] * fsum(p["DR"]))
              + fsum(p["RR_kinetic"]) + fsum(p["DR_kinetic"]))
    return dict(species=species, electron=fsum(net),
                photon_number=source_number - fsum(p["PI"]),
                photon_power=source_power - fsum(p["PI_absorbed_energy"]),
                thermal=thermal, binding=EV * fsum(CHI * net),
                escape=escape, external=source_power)


def compare_sources(checks, prefix, events, expected, scales, p,
                    source_number, source_power):
    check_scaled(checks, prefix + "/species", events[22:27], expected["species"],
                 scales["species"], GROSS_TOL)
    check_scaled(checks, prefix + "/electron", events[27], expected["electron"],
                 scales["electron"], GROSS_TOL)
    check_scaled(checks, prefix + "/photon_number", events[28], expected["photon_number"],
                 abs(source_number) + fsum(p["PI"]), GROSS_TOL)
    check_scaled(checks, prefix + "/photon_power", events[29], expected["photon_power"],
                 abs(source_power) + fsum(p["PI_absorbed_energy"]), GROSS_TOL)
    for name, index in (("thermal", 30), ("binding", 31), ("escape", 32)):
        check_scaled(checks, prefix + "/" + name, events[index], expected[name],
                     scales[name], GROSS_TOL)
    check_scaled(checks, prefix + "/external", events[33], expected["external"],
                 abs(source_power), GROSS_TOL)


def oracle_primitives(oracle):
    event = oracle["events"]
    energy = oracle["energy_components_erg_cm3_s"]
    array = lambda values: np.asarray([float(value) for value in values])
    return {
        "CI": array(event["CI_cm3_s"]), "RR": array(event["RR_cm3_s"]),
        "DR": array(event["DR_HeII_to_HeI_cm3_s"]), "PI": array(event["PI_cm3_s"]),
        "RR_kinetic": -array(energy["RR_thermal_by_edge"]),
        "DR_kinetic": -array(energy["DR_thermal_by_resonance"]),
        "PI_heat": array(energy["PI_heat_by_species"]),
        "PI_absorbed_energy": array(energy["PI_absorbed_energy_by_species"]),
    }


def validate_stage(label, state, values, source, rhs, events, oracle=None):
    checks = []
    n = int(values[11])
    nodes = values[12:].reshape(n, 4)
    energy, mu, number_ref = nodes[:, 0], nodes[:, 1], nodes[:, 2]
    volume, hubble, shear = values[1] ** 3, values[3], values[4]
    nh, nhe = values[5], values[6]
    h, he1, he2, w = state[:4]
    source_number = fsum(source) / volume
    source_power_ref = EV * fsum(source * energy)
    source_power = source_power_ref / volume
    lower = np.asarray([nh * (1 - h), nhe * (1 - (he1 + he2)), nhe * he1])
    ne = nh * h + nhe * (he1 + 2 * he2)
    u = w * nh * EV
    temperature = 2 * u / (3 * KB * (nh + nhe + ne))
    p = split_primitives(events)
    scales = gross_scales(p)
    expected = source_expectation(p, source_number, source_power)
    check_boolean(checks, "primitive/nonnegative", bool(np.all(events[:22] >= 0)))
    check_boolean(checks, "stage/actual_HM12_source", source_number > 0 and source_power > 0)
    check_boolean(checks, "stage/FT03_domain", 30000 <= temperature <= 110000)
    compare_sources(checks, "bundle_projection", events, expected, scales, p,
                    source_number, source_power)

    # H and He nuclear counts are independent of the generic AXI baryon guard.
    check_scaled(checks, "invariant/H_nuclei", events[22] + events[23], 0,
                 scales["edge"][0], INVARIANT_TOL)
    check_scaled(checks, "invariant/He_nuclei", fsum(events[24:27]), 0,
                 fsum(scales["edge"][1:]), INVARIANT_TOL)
    check_scaled(checks, "invariant/charge",
                 events[23] + events[25] + 2 * events[26] - events[27], 0,
                 scales["electron"] * 2, INVARIANT_TOL)
    check_scaled(checks, "invariant/photon_number",
                 events[28] - source_number + fsum(p["PI"]), 0,
                 abs(source_number) + fsum(p["PI"]), INVARIANT_TOL)
    check_scaled(checks, "invariant/energy", fsum(events[29:33]) - events[33], 0,
                 fsum(np.abs(events[29:34])), INVARIANT_TOL)
    check_scaled(checks, "invariant/PI_partition", p["PI_absorbed_energy"],
                 p["PI_heat"] + EV * CHI * p["PI"],
                 p["PI_absorbed_energy"], INVARIANT_TOL)
    check_scaled(checks, "invariant/native_EVENTS_residuals", events[35:37],
                 [0, 0], [1, 1], INVARIANT_TOL)
    check_scaled(checks, "invariant/native_RHS_residuals", rhs[12:14],
                 [0, 0], [1, 1], INVARIANT_TOL)

    # Compare sources, not tiny fractional derivatives, at an equilibrium IC.
    check_scaled(checks, "RHS_EVENTS/fraction_sources",
                 rhs[:3] * np.asarray([nh, nhe, nhe]), events[[23, 25, 26]],
                 scales["species"][[1, 3, 4]], GROSS_TOL)
    expected_wdot = -2 * hubble * w + events[30] / (nh * EV)
    check_scaled(checks, "RHS_EVENTS/gas_expansion_work", rhs[3], expected_wdot,
                 2 * abs(hubble * w) + scales["thermal"] / (nh * EV), GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/escape_reference_volume", rhs[4],
                 events[32] * volume, scales["escape"] * volume, GROSS_TOL)
    photon_u = EV * fsum(number_ref * energy) / volume
    delta_p = EV * fsum(number_ref * energy * (3 * mu ** 2 - 1) / 2) / volume
    work_terms = np.asarray([hubble * photon_u, 2 * shear * delta_p, 2 * hubble * u]) * volume
    check_scaled(checks, "RHS_EVENTS/geometry_work_reference_volume", rhs[5],
                 fsum(work_terms), fsum(np.abs(work_terms)), GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/source_energy_reference_volume", rhs[6],
                 source_power_ref, abs(source_power_ref), GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/absorbed_number_reference_volume", rhs[7],
                 fsum(p["PI"]) * volume, fsum(p["PI"]) * volume, GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/Gamma_density_prefactor", rhs[8:11] * lower,
                 p["PI"], p["PI"], GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/temperature", [rhs[11], events[34]],
                 [temperature, temperature], [temperature, temperature], GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/residual_identity", rhs[12:14], events[35:37],
                 [1, 1], INVARIANT_TOL)
    check_scaled(checks, "RHS_EVENTS/photon_node_number", fsum(rhs[14:]) / volume,
                 events[28], abs(source_number) + fsum(p["PI"]), GROSS_TOL)
    check_scaled(checks, "RHS_EVENTS/photon_node_energy", EV * fsum(rhs[14:] * energy) / volume,
                 events[29], abs(source_power) + fsum(p["PI_absorbed_energy"]), GROSS_TOL)

    if oracle is not None:
        op = oracle_primitives(oracle)
        for name in PRIMITIVE_SLICES:
            check_scaled(checks, "Decimal60/primitive/" + name, p[name], op[name],
                         np.abs(op[name]), COMPONENT_TOL)
        oe, oq = oracle["events"], oracle["energy_components_erg_cm3_s"]
        oe_expected = {
            "species": np.asarray(oe["species_source_cm3_s_HI_HII_HeI_HeII_HeIII_e"][:5], dtype=float),
            "electron": float(oe["direct_electron_source_cm3_s"]),
            "photon_number": source_number - fsum(op["PI"]),
            "photon_power": source_power + float(oq["interaction_photon_total"]),
            "thermal": float(oq["interaction_thermal_total"]),
            "binding": float(oq["interaction_binding_total"]),
            "escape": float(oq["escape_total"]), "external": source_power,
        }
        compare_sources(checks, "Decimal60/sources", events, oe_expected,
                        gross_scales(op), op, source_number, source_power)
        check_scaled(checks, "Decimal60/Gamma", rhs[8:11],
                     np.asarray(oe["photo_Gamma_s"], dtype=float),
                     np.asarray(oe["photo_Gamma_s"], dtype=float), COMPONENT_TOL)
        check_scaled(checks, "Decimal60/temperature", events[34],
                     float(oracle["input"]["T_K"]), float(oracle["input"]["T_K"]), COMPONENT_TOL)
    else:
        check_boolean(checks, "saved_final/nonunit_reference_volume", volume != 1.0,
                      "Saved final state used only for this affected callback; no new endpoint history.")
    return {"label": label, "status": "PASS_SCOPED" if all(c["pass"] for c in checks) else "FAIL",
            "time_s": float(values[0]), "a_rel": float(values[1]), "volume": float(volume),
            "nodes": n, "actual_source_number_proper": source_number,
            "actual_source_power_proper": source_power, "checks": checks}


def recorded_call(consumer, command, values, count, output, stem):
    request = command + " " + " ".join(format(float(v), ".17e") for v in values) + "\n"
    with (output / (stem + ".request.txt")).open("x") as handle:
        handle.write(request)
    result = consumer.call(command, values, count)
    write_json(output / (stem + ".response.json"), {
        "command": command, "representation": "unmodified parsed binary64 NativeConsumer response",
        "expected_values": count, "values": result.tolist()})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, default=HERE / "EVENT_REFERENCE_1STAGE.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, str(Path(__file__).resolve()), *(sys.argv[1:] if argv is None else argv)]
    start = time.perf_counter()
    receipt = {
        "schema": "rei-case-a-event-probe-v1", "task": "HERE_RUX03_EVENT_BRIDGE_02",
        "started_utc": datetime.now(timezone.utc).isoformat(), "command": command,
        "command_display": shlex.join(command), "cwd": str(Path.cwd()),
        "driver_sha256": sha256(__file__), "python": platform.python_version(),
        "numpy": np.__version__, "status": "STARTED", "events_schema": EVENTS_SCHEMA,
        "criteria": {"primitive_relative": COMPONENT_TOL, "gross_source_scaled": GROSS_TOL,
                     "invariant_scaled": INVARIANT_TOL},
        "scope": "IC Decimal60 comparison plus retained-final-state RHS/EVENTS affected callback",
        "saved_later_state_consumed_for_probe": True, "solver_intervals": 0,
        "old_campaign_replays": 0, "oracle_reexecutions": 0,
        "independent_decision": "NOT_PERFORMED_BY_THIS_DRIVER",
    }
    write_json(output / "START.json", receipt)
    consumer, validation, failure = None, None, None
    exit_code = 1
    try:
        production = load_production()
        packet, binary, build = args.packet.resolve(), args.binary.resolve(), args.build_receipt.resolve()
        oracle_path = args.oracle.resolve()
        if sha256(oracle_path) != ORACLE_SHA256:
            raise ValueError("EVENT_ORACLE_SHA_MISMATCH")
        oracle = json.loads(oracle_path.read_text())
        verified = production.preflight(packet)
        production.verify_bytes(packet / "evidence/extended.json", production.REFERENCE_JSON_SHA)
        receipt["input_sha256"] = {**verified["identities"],
            "evidence/extended.json": production.REFERENCE_JSON_SHA,
            "Decimal60_oracle": ORACLE_SHA256}
        receipt["paths"] = {"packet": str(packet), "binary": str(binary),
                            "build_receipt": str(build), "oracle": str(oracle_path)}
        with (output / "BIND.request.txt").open("x") as handle:
            handle.write("BIND " + " ".join(verified["identities"].values()) + "\n")
        consumer = production.NativeConsumer(binary, verified["identities"], build)
        consumer.calls["EVENTS"] = 0
        receipt["prelaunch_build_identity"] = consumer.build_identity
        write_json(output / "BUILD_RECEIPT.json", json.loads(build.read_text()))
        interval = production.ProductionInterval(packet, verified, consumer)
        # Deliberate diagnostic use of saved later states; integrate() is never called.
        with np.load(packet / "evidence/extended_dataset.npz", allow_pickle=False) as data:
            times = data["times_s"].copy()
            final_state = data["states"][:, -1].copy()
        if not np.array_equal(times, interval.times) or final_state.shape != interval.y0.shape:
            raise ValueError("SAVED_STAGE_COORDINATE_SHAPE_MISMATCH")
        stages = [("initial_IC", 0.0, interval.y0.copy(), oracle),
                  ("retained_final_saved_stage_probe", float(times[-1]), final_state, None)]
        stage_results = []
        for label, t, state, stage_oracle in stages:
            point = output / label
            point.mkdir()
            values, source = interval.stage(t, state)
            write_json(point / "STAGE_INPUT.json", {
                "label": label, "time_s": t, "state": state.tolist(),
                "production_stage_values": values.tolist(), "source_reference_per_node": source.tolist(),
                "origin": "retained initial IVP" if stage_oracle is not None else "stored final state; diagnostic only",
                "new_evolved_state": False})
            rhs = recorded_call(consumer, "RHS", values, 14 + interval.n, point, "RHS")
            events = recorded_call(consumer, "EVENTS", values, 37, point, "EVENTS")
            result = validate_stage(label, state, values, source, rhs, events, stage_oracle)
            write_json(point / "VALIDATION.json", result)
            stage_results.append(result)
        validation = {
            "status": "PASS_SCOPED" if all(s["status"] == "PASS_SCOPED" for s in stage_results) else "FAIL",
            "stages": stage_results,
            "same_state_RHS_EVENTS": True, "initial_primitive_count": 22,
            "saved_final_point_scope": "affected stage/volume probe, not a computed interval endpoint",
            "single_consumption_injected_RR_test": "separate Rust acceptance evidence; not claimed by this driver",
            "physical_admission": "UNCHANGED_CONDITIONAL_SCOPE",
        }
        write_json(output / "VALIDATION.json", validation)
        exit_code = 0 if validation["status"] == "PASS_SCOPED" else 1
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
        traceback.print_exc()
    finally:
        if consumer is not None:
            receipt["native_calls"] = dict(consumer.calls)
            try:
                consumer.close()
            except Exception as error:
                close_error = {"type": type(error).__name__, "message": str(error)}
                receipt["native_close_failure"] = close_error
                failure = failure or close_error
                exit_code = 1
            receipt["native_exit_code"] = consumer.proc.returncode
        receipt["elapsed_wall_s"] = time.perf_counter() - start
        receipt["exit_code"] = exit_code
        receipt["status"] = "PASS_SCOPED" if exit_code == 0 else "FAIL"
        receipt["failure"] = failure
        receipt["validation_file"] = "VALIDATION.json" if validation is not None else None
        write_json(output / "EXECUTION_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"], "output": str(output),
                      "native_calls": receipt.get("native_calls"), "failure": failure}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
