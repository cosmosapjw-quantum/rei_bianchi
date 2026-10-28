"""Calibrate the supplied inverse against the preserved C7 stdout only.

Authoring does not execute this program. The controller must supply a separate
quantified run authorization and whole-command resource accounting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from caloric_branch import CaloricBranch, exact, wire

SOURCE_BYTES = 19293
SOURCE_SHA256 = "2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948"
SOURCE_PATH = str(Path(__file__).resolve().parent.parent/"inputs"/"C7_STDOUT.json")
FIELDS = ("U", "N", "cv", "T")


def calibrate(raw: bytes, *, source_path: str = SOURCE_PATH) -> dict:
    if type(raw) is not bytes or len(raw) != SOURCE_BYTES or hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("INPUT_PENDING: saved C7 source byte identity mismatch")
    document = json.loads(raw)
    endpoint = document["reconstructed_endpoint"]
    if any(name not in endpoint for name in FIELDS):
        raise ValueError("INPUT_PENDING: saved C7 endpoint fields unavailable")
    E, D, cv, saved_T = (exact(endpoint[name]) for name in FIELDS)
    if D <= 0 or cv <= 0:
        raise ValueError("INPUT_PENDING: saved thermal count/cv invalid")
    branch = CaloricBranch(((1, cv*D), (10000, cv*D*10000)),
                           "C7_COMMON_V0", "GAS_THERMAL_ONLY",
                           "preserved C7 reconstructed_endpoint, represented ideal caloric law")
    if not (branch.temperatures[0] <= saved_T <= branch.temperatures[-1]):
        raise ValueError("INPUT_PENDING: saved temperature outside declared calibration bracket")
    ratio = E/(cv*D)
    inverse = branch.inverse(E)
    if inverse != ratio or inverse != saved_T or branch.evaluate(saved_T) != E:
        raise ValueError("SAVED_SOURCE_IDENTITY_FAILURE: no tolerance or fallback")
    return {
        "unit": "rei_supplied_caloric_branch_20261028",
        "status": "REPRESENTED_SOURCE_CALIBRATION_ONLY",
        "source": {"path": source_path, "bytes": SOURCE_BYTES, "sha256": SOURCE_SHA256,
                   "record": "reconstructed_endpoint", "fields": list(FIELDS)},
        "branch": {"knots": [[wire(t), wire(u)] for t, u in branch.knots],
                   "reference_volume_id": branch.reference_volume_id,
                   "energy_store_id": branch.energy_store_id,
                   "provenance": branch.provenance, "m0": wire(branch.m0)},
        "operands": {"E": wire(E), "D": wire(D), "cv": wire(cv), "saved_T": wire(saved_T)},
        "inverse_T": wire(inverse), "independent_ideal_quotient_T": wire(ratio),
        "represented_temperature_interval": [wire(x) for x in branch.enclose_energy(E, E, 0)],
        "conditional_temperature_radius": wire(branch.residual_radius(saved_T, E, 0, 0)),
        "uncertainty_basis": {"eta": "0 explicit for represented supplied ideal law only",
                              "eE": "0 explicit for represented saved E only",
                              "physical_eta": None, "physical_eE": None},
        "physical_temperature_interval": None, "actual_recipient_temperature": None,
        "actual_native25": None, "physical_radii": None, "full_state_update": False,
        "L4_ready": False, "global_physical_completion": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = calibrate(args.input.read_bytes(), source_path=str(args.input.resolve()))
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
