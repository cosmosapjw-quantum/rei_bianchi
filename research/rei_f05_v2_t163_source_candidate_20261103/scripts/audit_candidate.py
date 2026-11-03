#!/usr/bin/env python3
"""Independent source-identity and physical-interval audit for the T163 candidate."""
from __future__ import annotations
import argparse, hashlib, json, math, tarfile
from pathlib import Path
import numpy as np

EXPECTED = {
    "source_tar": "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
    "kernel": "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644",
    "input_lock": "90137341a1a37344be762e82e6603cd5c6bf4db00164ab0ba98809f0e9d9f381",
    "initial_state": "7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d",
    "source162": "35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b",
    "runtime": "97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075",
    "runtime_git_head": "a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78",
    "candidate_npz": "ae57cadc4dc98f204085805480a57d7956987a916ae1f2ea4af38f8ab40d867e",
    "physical_body": "c8378bffd92535640dfb166316a33edad57f32bfb772c6f0020e8a610f006784",
    "accepted_record160": "59aed347bdf71fe788e3aee57742a78727971475d4b66ff935e4ca153ec90957",
}
LANES = {
    "LOCAL_NEUTRAL_HAZARD_PRIMARY": "primary",
    "RECOMBINATION_WEIGHTED_AUDITOR": "recomb",
    "SCRIPT_SELF_SHIELDING_AUDITOR": "shield",
}
EV_ERG = 1.602176634e-12
KB_ERG = 1.380649e-16
CHI = (13.598434599702, 24.587389011, 54.41776)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError("T163_AUDIT_" + label)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True,
                      separators=(",", ":"), sort_keys=True).encode("ascii")


def read_npz(path: Path):
    with np.load(path, allow_pickle=False) as z:
        required = ("population_lower", "population_upper",
                    "log_temperature_lower", "log_temperature_upper")
        require(set(required) == set(z.files), "NPZ_SCHEMA")
        lo = np.asarray(z["population_lower"], dtype="<f8")
        hi = np.asarray(z["population_upper"], dtype="<f8")
        tl = np.asarray(z["log_temperature_lower"], dtype="<f8")
        th = np.asarray(z["log_temperature_upper"], dtype="<f8")
    require(lo.shape == hi.shape == (46080, 5), "POPULATION_SHAPE")
    require(tl.shape == th.shape == (46080,), "TEMPERATURE_SHAPE")
    require(all(np.isfinite(a).all() for a in (lo, hi, tl, th)), "NONFINITE")
    require((lo > 0.0).all() and (hi >= lo).all() and (th >= tl).all(), "INTERVAL_ORDER")
    body = b"".join(np.ascontiguousarray(a).tobytes() for a in (lo, hi, tl, th))
    return lo, hi, tl, th, hashlib.sha256(body).hexdigest()


def totals(path: Path, nh: np.ndarray, nhe: np.ndarray):
    lo, hi, tl, th, body = read_npz(path)
    require(np.all(lo[:, 0] + lo[:, 1] <= nh * (1.0 + 5e-12)), "H_LOWER_CONE")
    require(np.all(hi[:, 0] + hi[:, 1] >= nh * (1.0 - 5e-12)), "H_UPPER_CONE")
    require(np.all(np.sum(lo[:, 2:5], axis=1) <= nhe * (1.0 + 5e-12)), "HE_LOWER_CONE")
    require(np.all(np.sum(hi[:, 2:5], axis=1) >= nhe * (1.0 - 5e-12)), "HE_UPPER_CONE")

    def sum_f64(values):
        return math.fsum(np.asarray(values, dtype=np.float64).tolist())

    def endpoint(pop, logt):
        ne = pop[:, 1] + pop[:, 3] + 2.0 * pop[:, 4]
        binding = EV_ERG * (CHI[0] * pop[:, 1]
                  + CHI[1] * (pop[:, 3] + pop[:, 4])
                  + CHI[2] * pop[:, 4])
        thermal = 1.5 * KB_ERG * (nh + nhe + ne) * np.exp(logt)
        return {"Ne": sum_f64(ne), "B_erg": sum_f64(binding),
                "U_gas_erg": sum_f64(thermal)}

    return {"lower": endpoint(lo, tl), "upper": endpoint(hi, th)}, body


def audit(args):
    candidate = Path(args.candidate_dir)
    runtime_doc = json.loads(Path(args.runtime_contract).read_text())
    contract = runtime_doc["full_runtime_contract"]
    contract_copy = dict(contract)
    contract_sha = contract_copy.pop("sha256")
    require(hashlib.sha256(canonical(contract_copy)).hexdigest() == contract_sha == EXPECTED["runtime"], "RUNTIME_CONTRACT_HASH")
    require(runtime_doc["runtime_bound_git_commit"] == EXPECTED["runtime_git_head"], "RUNTIME_GIT_HEAD")
    require(runtime_doc["worker_runtime_sha256"] == "ce6cc44af3055b73553cfafd429d979190b80143cf512929e1ec3d78c038e4d7", "WORKER_RUNTIME_ID")

    require(sha(Path(args.source_tar)) == EXPECTED["source_tar"], "SOURCE_TAR_ID")
    require(sha(Path(args.kernel)) == EXPECTED["kernel"], "KERNEL_ID")
    require(sha(Path(args.input_lock)) == EXPECTED["input_lock"], "INPUT_LOCK_ID")
    require(sha(Path(args.initial_state)) == EXPECTED["initial_state"], "INITIAL_STATE_ID")
    require(sha(Path(args.source162)) == EXPECTED["source162"], "PARENT162_ID")

    with tarfile.open(args.source_tar, "r:gz") as archive:
        control = json.load(archive.extractfile("CONTROL.json"))
        accepted_bytes = archive.extractfile("history/accepted_00000003.json").read()
        accepted = json.loads(accepted_bytes)
    require(control["cursor"]["accepted_tick"] == 160 and control["cursor"]["accepted_index"] == 3, "ORIGINAL_V1_CURSOR")
    require(control["latest_record_sha256"] == EXPECTED["accepted_record160"], "ORIGINAL_V1_RECORD_HASH")
    require(hashlib.sha256(accepted_bytes).hexdigest() == EXPECTED["accepted_record160"], "ORIGINAL_V1_RECORD_BYTES")
    require(accepted["accepted_index"] == 3 and accepted["cursor_after"]["accepted_tick"] == 160, "ORIGINAL_V1_ACCEPTED_RECORD")

    tx_control = json.loads(Path(args.tx_control).read_text())
    require(tx_control["versioned_branch_accepted_tick"] == 162, "V2_PARENT_TICK")
    require(tx_control["official_original_production_advance"] is False, "NO_PRODUCTION_PROMOTION")

    manifest = json.loads((candidate / "PUBLIC_NEXT163.json").read_text())
    require(manifest["candidate_V2_next_tick"] == 163 and manifest["old_V1_accepted_tick"] == 160, "TIME_SCOPE")
    require(manifest["official_V1_tick163"] is False and manifest["production_control"] == "NOT_YET_INSTALLED", "NOT_ACCEPTED")
    require(manifest["continuum_ode_error_certified"] is False, "NO_CONTINUUM_CERTIFICATE")
    require(manifest["native_maps"] == 9 and manifest["physical_realizations"] == 1, "MAP_COUNT")
    require(manifest["source_original_tar_sha256"] == EXPECTED["source_tar"], "MANIFEST_SOURCE_TAR")
    require(manifest["source_original_26event_kernel_sha256"] == EXPECTED["kernel"], "MANIFEST_KERNEL")
    require(manifest["source_research_tick162_npz_sha256"] == EXPECTED["source162"], "MANIFEST_PARENT")
    require(manifest["full_runtime_sha256"] == EXPECTED["runtime"], "MANIFEST_RUNTIME")

    with np.load(args.initial_state, allow_pickle=False) as z:
        nh = np.asarray(z["N_HI"] + z["N_HII"], dtype=np.float64)
        nhe = np.asarray(z["N_HeI"] + z["N_HeII"] + z["N_HeIII"], dtype=np.float64)
    require(nh.shape == nhe.shape == (46080,) and (nh > 0).all() and (nhe > 0).all(), "NUCLEI_INVENTORY")
    parent_totals, _ = totals(Path(args.source162), nh, nhe)

    lane_results = {}
    candidate_hashes = set()
    body_hashes = set()
    for lane, slug in LANES.items():
        lane_dir = candidate / slug
        state_path = lane_dir / "NEW_SOURCE_TICK163.npz"
        receipt_path = lane_dir / "NATIVE_RECEIPT.json"
        receipt = json.loads(receipt_path.read_text())
        require(receipt["lane"] == lane, "LANE_ID_" + slug)
        require(receipt["source_tar_sha256"] == EXPECTED["source_tar"], "RECEIPT_TAR_" + slug)
        require(receipt["source_kernel_sha256"] == EXPECTED["kernel"], "RECEIPT_KERNEL_" + slug)
        require(receipt["parent162_original_npz_sha256"] == EXPECTED["source162"], "RECEIPT_PARENT_" + slug)
        require(receipt["full_sevenpin_runtime_sha256"] == EXPECTED["runtime"], "RECEIPT_RUNTIME_" + slug)
        require(receipt["acceptance"] == "V2_POLICY_CANDIDATE_NOT_YET_CONTROL", "RECEIPT_ACCEPTANCE_" + slug)
        require(receipt["official_original_V1_tick"] == 160 and receipt["continuous_ode_error_certified"] is False, "RECEIPT_SCOPE_" + slug)
        maps = receipt["native_map_receipts"]
        require(set(maps) == {"full", "half1", "half2"}, "MAPS_" + slug)
        require(all(m["status"] == "PASS" and m["native_certified"] is True for m in maps.values()), "MAP_PASS_" + slug)
        require(all(m["original_table_event_count"] == 0 for m in maps.values()), "TABLE_EVENT_" + slug)
        ledgers = receipt["original_14_ledgers"]
        require(len(ledgers) == 14, "LEDGER_COUNT_" + slug)
        require(all(len(v) == 2 and math.isfinite(float(v[0])) and math.isfinite(float(v[1])) and float(v[0]) <= 0.0 <= float(v[1]) for v in ledgers.values()), "LEDGER_ZERO_" + slug)
        defects = receipt["source_correlated_discrete_defect"]
        widths = receipt["original_public_widths"]
        max_defect = max(float(v) for v in defects.values())
        max_width = max(float(v) for v in widths.values())
        require(max_defect < 2e-4 and max_width < 2e-3, "FIXED_GATES_" + slug)
        require(sha(state_path) == EXPECTED["candidate_npz"] == manifest["new_source_tick163_npz_sha256"], "CANDIDATE_NPZ_ID_" + slug)
        require(receipt["new162to163_source_state_sha256"] == EXPECTED["candidate_npz"], "RECEIPT_NPZ_ID_" + slug)
        values, body = totals(state_path, nh, nhe)
        require(body == EXPECTED["physical_body"] == manifest["new_physical_body_sha256"], "PHYSICAL_BODY_ID_" + slug)
        candidate_hashes.add(sha(state_path)); body_hashes.add(body)
        lane_results[slug] = {"npz_sha256": sha(state_path), "physical_body_sha256": body,
                              "native_maps": 3, "native_ledgers": len(ledgers),
                              "maximum_local_estimator": max_defect, "maximum_public_width": max_width}

    require(len(candidate_hashes) == len(body_hashes) == 1, "LANE_PHYSICAL_IDENTITY")
    new_totals, _ = totals(candidate / "primary/NEW_SOURCE_TICK163.npz", nh, nhe)
    deltas = {}
    for key in ("Ne", "B_erg", "U_gas_erg"):
        deltas[key] = [new_totals["lower"][key] - parent_totals["upper"][key],
                       new_totals["upper"][key] - parent_totals["lower"][key]]
    expected = {
        "Ne": [-1.9145263975830813e60, -1.2038693356921076e60],
        "B_erg": [-4.747062280253878e49, -2.7388375467290745e49],
        "U_gas_erg": [-1.2212854130721702e50, 6.095376770622375e49],
    }
    for key, pair in expected.items():
        require(all(math.isclose(a, b, rel_tol=2e-12, abs_tol=0.0) for a, b in zip(deltas[key], pair)), "EXTENSIVE_DELTA_" + key)

    return {
        "schema": "REI_F05_V2_T163_SOURCE_CANDIDATE_INDEPENDENT_AUDIT_V1",
        "audit_status": "PASS",
        "scope": "source-discrete candidate only; no accepted tick or production control",
        "source_identity": {"source_tar_sha256": EXPECTED["source_tar"], "kernel_sha256": EXPECTED["kernel"],
                            "input_lock_sha256": EXPECTED["input_lock"], "initial_state_sha256": EXPECTED["initial_state"],
                            "parent162_npz_sha256": EXPECTED["source162"], "full_runtime_sha256": EXPECTED["runtime"],
                            "runtime_bound_git_commit": EXPECTED["runtime_git_head"]},
        "candidate_identity": {"tick": 163, "npz_sha256": next(iter(candidate_hashes)),
                               "physical_body_sha256": next(iter(body_hashes))},
        "native_original_maps": 9,
        "lanes": lane_results,
        "maximum_source_discrete_local_estimator": max(v["maximum_local_estimator"] for v in lane_results.values()),
        "maximum_public_width": max(v["maximum_public_width"] for v in lane_results.values()),
        "source_discrete_extensive_delta_outer": deltas,
        "state_semantics": "per-cell integrated particle counts; sum over cells gives extensive Ne/B/U, while physical volume is used separately in the rate evaluation",
        "official_V1_accepted_tick": 160,
        "candidate_tick_accepted": False,
        "production_control_installed": False,
        "continuum_ode_error_certified": False,
        "automatic_tick164": False,
        "canonical_DAG": "28/88",
        "canonical_DAG_delta": 0,
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("candidate-dir", "runtime-contract", "source-tar", "kernel", "input-lock", "initial-state", "source162", "tx-control"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--output")
    a = p.parse_args()
    result = audit(a)
    text = json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n"
    if a.output:
        out = Path(a.output)
        require(not out.exists(), "NO_OVERWRITE_AUDIT_OUTPUT")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    print(text, end="")

if __name__ == "__main__":
    main()
