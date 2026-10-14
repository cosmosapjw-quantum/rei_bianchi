#!/usr/bin/env python3
"""Metadata-only portable PHYS29 stage construction; never import or run science."""
from datetime import datetime, timezone
import ast
import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
TASK = "REI-PHYS29-20261011"
ENTRYPOINT = "contributions/numerics/second_order_width.py"
FREEZE = "contributions/numerics/PREEXECUTION_FROZEN.json"
PROTOCOL = "contributions/numerics/PROTOCOL.json"
FIRST = "contributions/numerics/SECOND_ORDER_FIRST.json"
EXPECTED = {
    ENTRYPOINT: "faf7c3911d54f9739b4d486f88fa388af7165c50684bfbb036dcf02e5a8c5bda",
    PROTOCOL: "6ab5d3c488a00ebfb868e4d4e83d98a2fe1db9479956b587f673d9d9b86e7573",
    FREEZE: "544efcc1dda9cd0a4f63d5806cb59c2a092484016de8b20755f785f47a0b9c7b",
    FIRST: "40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row(path):
    p = ROOT / path
    raw = p.read_bytes()
    return {"path": path, "bytes": len(raw), "sha256": sha(raw), "mode": "100644"}


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode()


def write_new(path, raw):
    with path.open("xb") as handle:
        handle.write(raw)


def main():
    frozen_utc = datetime.now(timezone.utc).isoformat()
    for name, expected in EXPECTED.items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("root-authorized scientific identity changed: " + name)
    freeze = json.loads((ROOT / FREEZE).read_bytes())
    protocol = json.loads((ROOT / PROTOCOL).read_bytes())
    first = json.loads((ROOT / FIRST).read_bytes())
    execution = json.loads((ROOT / "contributions/numerics/EXECUTION.json").read_bytes())
    if (first["summary"]["all_pass"] is not True or execution["exit_code"] != 0
            or execution["raw_result"]["sha256"] != EXPECTED[FIRST]):
        raise ValueError("first science result is not the actually observed accepted reference")
    freeze_rows = {item["path"]: item for item in freeze["files"]}
    protocol_rows = {item["path"]: item for item in protocol["inputs"]}
    extras = {
        ENTRYPOINT, PROTOCOL,
        "contributions/numerics/INPUT_PROVENANCE.json",
        "contributions/numerics/STATIC_CHECKS.json",
        "contributions/numerics/PREEXECUTION_CHANGES.json",
    }
    if (len(freeze_rows) != len(freeze["files"]) or len(freeze_rows) != 25
            or len(protocol_rows) != len(protocol["inputs"]) or len(protocol_rows) != 20
            or set(freeze_rows) != set(protocol_rows) | extras):
        raise ValueError("unexpected frozen/runtime member closure")
    closure_checks = []
    for name, item in freeze_rows.items():
        current = row(name)
        p = ROOT / name
        same = all(current[key] == item[key] for key in ("bytes", "sha256"))
        regular_644 = (p.is_file() and not p.is_symlink()
                       and stat.S_IMODE(p.stat().st_mode) == 0o644)
        closure_checks.append({"kind": "frozen_to_actual", "path": name,
                               "identity_equal": same, "regular_mode_100644": regular_644})
        if not same or not regular_644:
            raise ValueError("frozen payload identity/mode mismatch: " + name)
    for name, item in protocol_rows.items():
        if any(freeze_rows[name][key] != item[key] for key in ("bytes", "sha256")):
            raise ValueError("protocol input identity differs from freeze: " + name)
    runtime_names = sorted(set(freeze_rows) | {FREEZE})
    source = (ROOT / ENTRYPOINT).read_text()
    module = ast.parse(source, filename=ENTRYPOINT)
    imports = sorted({
        alias.name.split(".")[0] for node in ast.walk(module) if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".")[0] for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module
    })
    if not all(name in sys.stdlib_module_names for name in imports):
        raise ValueError("non-stdlib candidate dependency found")
    direct_reads = [
        PROTOCOL, FREEZE, "PHYSICS_CONTRACT.json", "SOURCE_MANIFEST.json",
        "inputs/PHYS22_INITIAL_COEFFICIENTS.json",
        "inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json",
        "inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json",
        "inputs/PHYS28/contributions/numerics/SMALL_WIDTH_FIRST.json",
    ]
    if not set(direct_reads).issubset(runtime_names):
        raise ValueError("direct program input not in frozen closure")
    runner = OUT / "repro.py"
    runner_ast = ast.parse(runner.read_text(), filename="portability/repro.py")
    compile(runner_ast, "portability/repro.py", "exec")
    manifest = {
        "schema": 1, "task": TASK, "frozen_utc": frozen_utc,
        "entrypoint": ENTRYPOINT, "files": [row(name) for name in runtime_names],
        "runtime_files": runtime_names,
        "closure": "25 frozen identity files plus PREEXECUTION_FROZEN.json itself; no first-result payload or unrelated historical archive",
        "comparison_reference": {key: value for key, value in row(FIRST).items() if key != "mode"},
        "comparison_reference_is_runtime_input": False,
        "archive_layout": "26 regular payload files plus PORTABLE_MANIFEST.json, all100644; sorted members; fixed ZIP timestamp1980-01-01; DEFLATElevel9",
        "independent_physics_credit": 0,
    }
    manifest_raw = encode(manifest)
    write_new(OUT / "PORTABLE_MANIFEST.json", manifest_raw)
    payloads = {name: (ROOT / name).read_bytes() for name in runtime_names}
    payloads["PORTABLE_MANIFEST.json"] = manifest_raw
    archive_path = OUT / "PHYS29_PORTABLE_STAGE.zip"
    with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for name in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            handle.writestr(info, payloads[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(archive_path) as handle:
        archive_checks = [{
            "path": item.filename, "byte_equal": handle.read(item.filename) == payloads[item.filename],
            "regular_mode_100644": (item.external_attr >> 16) == 0o100644,
            "fixed_timestamp": item.date_time == (1980, 1, 1, 0, 0, 0),
        } for item in handle.infolist()]
        exact_set = handle.namelist() == sorted(payloads)
        if (not exact_set or not all(all(item[key] for key in (
                "byte_equal", "regular_mode_100644", "fixed_timestamp")) for item in archive_checks)):
            raise ValueError("stage readback identity/mode/member check failed")
    archive_id = {"path": "portability/PHYS29_PORTABLE_STAGE.zip", "bytes": archive_path.stat().st_size,
                  "sha256": sha(archive_path.read_bytes()), "entries": len(payloads)}
    runner_id = {"path": "portability/repro.py", "bytes": runner.stat().st_size,
                 "sha256": sha(runner.read_bytes())}
    destination = ROOT.parent / "phys29_portability_fresh_20261011"
    if destination.exists():
        raise FileExistsError("fresh replay destination already exists")
    port_protocol = {
        "task": TASK, "status": "FROZEN_BEFORE_REPLAY", "frozen_utc": frozen_utc,
        "agent": "/root/phys29_portability", "role": "Same-program operational replay; not candidate or final reviewer",
        "root_replay_GO_observed": True,
        "authorization_basis": "Actual root message: EXPLICIT REPLAY GO, once your portable protocol/stage/runtime closure is frozen and prechecks pass. Exactly once; no corecode/protocol/freeze changes.",
        "model": "GPT-6 Astra from trusted developer designation GPT-6 Astra Pro; no switch or performance claim",
        "first_science_completed_observed": True, "first_execution_identity": row("contributions/numerics/EXECUTION.json"),
        "first_result_identity": manifest["comparison_reference"], "accepted_science_sha256": EXPECTED,
        "declared_protocol_inputs": 20, "frozen_identity_files": 25, "runtime_payload_files": 26,
        "archive_entries_including_manifest": 27,
        "archive": archive_id, "runner": runner_id,
        "destination": str(destination), "destination_absent_at_freeze": True,
        "record_prefix": str(OUT / "REPLAY"), "reference_result": str(ROOT / FIRST),
        "replay_invocations_at_freeze": 0, "kernel_evaluations_by_porter_at_freeze": 0,
        "limits": {"replay_main_max": 1, "joint_evaluations": 8, "k_outputs": 8,
                   "k_prime_outputs": 8, "k_second_outputs": 8, "three_components_total": 24,
                   "new_physical_roots": 0, "old_PHYS19_through_PHYS28_main_suite_imports": 0,
                   "automatic_retries": 0, "timeout_seconds": 30, "independent_physics_credit": 0},
        "acceptance": [
            "Exact archive and every payload identity/member/mode comparison before replay",
            "20 protocol inputs,25 frozen files,26 runtime files form exact declared closure",
            "Fresh absent destination and new evidence record paths; no overwrite",
            "One PHYS29 scientific subprocess exit0 with no timeout; exact original raw and parsed JSON equality",
            "Original all238 numerical predicates reproduced and frozen actual count limits observed",
            "All26 runtime payloads plus manifest unchanged in content,member set and mode after replay"
        ],
        "failure_policy": "Preserve first failure and invocation/time/raw outputs; no science code/tolerance edits or retry",
        "first_result_read_scope": "Full EXECUTION_STARTED,EXECUTION,FIRST_STDOUT; FIRST_STDERR byte0; raw task/python/precision/summary only. Not an independent reassessment of scientific predicates.",
        "preexecution_versions": "Only finalv3runtime staged. Preserved earlier drafts remain in main provenance; none run by porter.",
        "claim_ceiling": "Implementation reproducibility on a separate path within the same cloud host/Python; not independent physical data,implementation,OS,native arithmetic or uncertainty enclosure",
        "protected_state": json.loads((ROOT / "PHYSICS_CONTRACT.json").read_bytes())["protected_state"],
    }
    write_new(OUT / "PORTABILITY_PROTOCOL.json", encode(port_protocol))
    stage_receipt = {
        "task": TASK, "status": "STAGE_AND_DECLARED_CLOSURE_PASS_NO_SCIENCE_RUN",
        "created_utc": datetime.now(timezone.utc).isoformat(), "archive": archive_id,
        "manifest_identity": row("portability/PORTABLE_MANIFEST.json"), "runner": runner_id,
        "portable_protocol_identity": row("portability/PORTABILITY_PROTOCOL.json"),
        "builder_identity": row("portability/build_stage.py"),
        "closure_counts": {"protocol_inputs": 20, "frozen_identity_files": 25, "runtime_files": 26, "zip_entries": 27},
        "frozen_actual_identity_checks": closure_checks, "protocol_subset_equal": True,
        "candidate_static_io_inspection": {
            "source_read": "All786lines read; imports,ROOT/HERE assignments,science digest/read paths and main output control inspected",
            "imports": imports, "all_stdlib": True,
            "ROOT": "Path(__file__).resolve().parents[2]", "HERE": "Path(__file__).resolve().parent",
            "direct_runtime_reads": direct_reads, "additional_runtime_reads": "Every frozenfile is byte-hashed; no dependency is imported from those inputs",
            "historical_code_payload_semantics": "PHYS28 code is only byte-hashed as a provenance input; never imported/executed",
            "output": "Required --output path outside restored tree for immutable pre/post closure",
            "no_absolute_runtime_input_paths": True, "no_dynamic_import_or_eval_exec": True,
            "scope": "Static declared closure inspection, not traced OS-wide open audit or independent science review"
        },
        "runner_static_parse_compile_only": True, "exact_zip_member_set": exact_set,
        "archive_readback_checks": archive_checks,
        "candidate_imports": 0, "scientific_program_invocations": 0, "kernel_derivative_evaluations": 0,
        "new_physical_roots": 0, "independent_physics_credit": 0,
    }
    write_new(OUT / "STAGE_RECEIPT.json", encode(stage_receipt))
    print(json.dumps({"status": stage_receipt["status"], "archive": archive_id,
                      "runner": runner_id, "protocol": row("portability/PORTABILITY_PROTOCOL.json"),
                      "runtime_files": 26, "scientific_program_invocations": 0}))


if __name__ == "__main__":
    main()
