#!/usr/bin/env python3
"""Complete bounded evidence after the strict native binary byte gate failed.

Reads the existing five-setting and three-control outputs without rerunning
them. Performs only the previously unexecuted original gas build. Records
observed ELF/package-metadata differences without claiming their cause proved.
"""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import traceback

EXPECTED_D = "6405bcba8ec654bf3ab98182be344cd8c3915b97"
EXPECTED_NATIVE = "ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66"
EXPECTED_GAS = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"
PREFIX = "research/atomic_nuclear_ssot_20261017"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--reproduction-root", required=True, type=Path)
    parser.add_argument("--toolchain-prefix", required=True, type=Path)
    parser.add_argument("--reference-native-binary", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    old = args.reproduction_root.resolve(strict=True)
    prefix = args.toolchain_prefix.resolve(strict=True)
    output = args.output_root.absolute()
    reference_binary = args.reference_native_binary.resolve(strict=True)
    if output.exists() or output.is_symlink() or repo == output or repo in output.parents:
        raise ValueError("new external output root required")
    output.mkdir(parents=True)
    (output / "logs").mkdir()
    helper = Path(__file__).resolve().with_name("verify_scoped_science_commit.py")
    spec = importlib.util.spec_from_file_location("scoped_numeric_reader", helper)
    shared = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared)
    file_id, save = shared.file_id, shared.save
    original_receipt = json.loads((old / "SCOPED_CLEAN_REPRODUCTION_RECEIPT.json").read_bytes())
    if (original_receipt["science_commit"] != EXPECTED_D
            or original_receipt["error"] != "new native binary SHA/size differs from published execution"
            or not original_receipt["fixed_gas_reproduction"]["all_numeric_fields_match_exactly"]):
        raise ValueError("this continuation applies only to the retained strict native byte mismatch")
    run15 = repo / PREFIX / "run15"
    native = run15 / "postloss_native"
    build = old / "postloss_native_build"
    new_binary = build / "target/release/positive_planck_panel_postloss"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0",
               GIT_TERMINAL_PROMPT="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    receipt = {"schema": "rei.run15.postloss.scoped_clean_continuation.v1", "status": "IN_PROGRESS",
               "science_commit": EXPECTED_D, "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "script": file_id(Path(__file__)), "numeric_reader": file_id(helper),
               "command_argv": [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]],
               "retained_strict_failure": {"path": str(old / "SCOPED_CLEAN_REPRODUCTION_RECEIPT.json"),
                                            **file_id(old / "SCOPED_CLEAN_REPRODUCTION_RECEIPT.json")},
               "old_and_new_native_IVP_runs": 0, "test_suite_executions": 0,
               "repeated_fixed_gas_settings": 0, "repeated_native_CLI_controls": 0, "commands": []}
    def run(name, argv, cwd=repo, custom_env=None, timeout=120):
        e = env if custom_env is None else custom_env
        argv = list(map(str, argv))
        stdout, stderr = output / "logs" / (name + ".stdout.txt"), output / "logs" / (name + ".stderr.txt")
        row = {"stage": name, "argv": argv, "cwd": str(cwd),
               "environment": {k: e[k] for k in shared.ENV_KEYS if k in e}}
        save(output / "logs" / (name + ".request.json"), row)
        print(json.dumps({"stage": name, "status": "STARTED"}), flush=True)
        start = time.monotonic()
        with stdout.open("xb") as out, stderr.open("xb") as err:
            result = subprocess.run(argv, cwd=cwd, env=e, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, timeout=timeout)
        row.update(exit_code=result.returncode, seconds=time.monotonic() - start,
                   stdout={"path": str(stdout.relative_to(output)), **file_id(stdout)},
                   stderr={"path": str(stderr.relative_to(output)), **file_id(stderr)})
        receipt["commands"].append(row)
        save(output / "logs" / (name + ".command.json"), row)
        print(json.dumps({"stage": name, "exit_code": result.returncode, "seconds": row["seconds"]}), flush=True)
        if result.returncode:
            raise ValueError("command failed: " + name)
        return stdout.read_bytes()

    def elf_sections(path):
        import hashlib
        raw = path.read_bytes()
        if raw[:6] != b"\x7fELF\x02\x01":
            raise ValueError("expected ordinary ELF64 little-endian file")
        shoff = struct.unpack_from("<Q", raw, 40)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", raw, 58)
        if shentsize != 64 or not 0 < shnum < 65536 or shstrndx >= shnum or shoff + shnum * shentsize > len(raw):
            raise ValueError("unsupported ELF section table")
        headers = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * shentsize) for i in range(shnum)]
        names_header = headers[shstrndx]
        names = raw[names_header[4]:names_header[4] + names_header[5]]
        rows = []
        for index, h in enumerate(headers):
            end = names.find(b"\0", h[0])
            if end < 0:
                raise ValueError("malformed ELF section name")
            name = names[h[0]:end].decode("ascii")
            if h[1] != 8 and h[4] + h[5] > len(raw):
                raise ValueError("ELF section outside file")
            data = None if h[1] == 8 else raw[h[4]:h[4] + h[5]]
            rows.append({"index": index, "name": name, "type": h[1], "file_offset": h[4],
                         "size": h[5], "sha256": None if data is None else hashlib.sha256(data).hexdigest()})
        return rows

    def fingerprint_rows(target):
        root = target / "release/.fingerprint"
        rows = []
        for p in sorted(root.glob("*/*.json")):
            if p.name not in ("lib-rei_iso_couple_reference.json", "lib-rei_run15_positive_planck.json",
                              "bin-positive_planck_panel_postloss.json"):
                continue
            d = json.loads(p.read_bytes())
            rows.append({"relative_path": p.relative_to(target).as_posix(), **file_id(p),
                         "observed_metadata": d})
        return rows

    failure = None
    try:
        old_controls = json.loads((native / "evidence/controls/THREE_CLI_CONTROLS.json").read_bytes())
        new_controls = json.loads((build / "controls/THREE_CLI_CONTROLS.json").read_bytes())
        comparison = shared.compare_numeric(old_controls["cases"], new_controls["cases"])
        stdout_equal = (native / "evidence/controls/STDOUT.jsonl").read_bytes() == (build / "controls/STDOUT.jsonl").read_bytes()
        if (len(new_controls["cases"]) != 3 or new_controls["status"] != "NUMERICALLY_CHECKED"
                or any(c["status"] != "PASS" for c in new_controls["cases"])
                or not comparison["all_numeric_fields_match_exactly"] or not stdout_equal):
            raise ValueError("existing three-control numerical comparison failed")
        comparison.update(schema="rei.run15.native_controls_exact_numeric_reproduction.v1",
                          published_controls=file_id(native / "evidence/controls/THREE_CLI_CONTROLS.json"),
                          reproduced_controls=file_id(build / "controls/THREE_CLI_CONTROLS.json"),
                          exact_stdout_bytes_equal=stdout_equal, total_emitted_nodes=16,
                          node_weight_numeric_fields=32, comparison_runs=1, new_CLI_executions=0)
        save(output / "NATIVE_CONTROL_NUMERIC_COMPARISON.json", comparison)
        receipt["native_control_reproduction"] = {"cases": 3, "published_acceptance_status": "PASS",
                                                "reproduced_acceptance_status": "PASS",
                                                "numeric_fields": comparison["fields"],
                                                "exact_matches": comparison["exact_matches"],
                                                "all_nodes_weights_exact": True,
                                                "emitted_nodes": 16, "node_weight_numbers": 32,
                                                "stdout_bytes_identical": stdout_equal,
                                                "numerical_reproduction": "IMPLEMENTATION_VERIFIED"}
        reference_id = file_id(reference_binary)
        new_id = file_id(new_binary)
        if reference_id["sha256"] != EXPECTED_NATIVE:
            raise ValueError("reference native file is not the published binary")
        old_elf, new_elf = elf_sections(reference_binary), elf_sections(new_binary)
        old_by_name = {r["name"]: r for r in old_elf}
        new_by_name = {r["name"]: r for r in new_elf}
        elf_comparison = [{"name": name, "published": old_by_name.get(name), "new": new_by_name.get(name),
                          "section_bytes_same": name in old_by_name and name in new_by_name
                            and old_by_name[name]["sha256"] == new_by_name[name]["sha256"]
                            and old_by_name[name]["size"] == new_by_name[name]["size"]}
                         for name in sorted(set(old_by_name) | set(new_by_name))]
        metadata = {"schema": "rei.run15.native_build_byte_mismatch_observations.v1",
                    "published_binary": {"path": str(reference_binary), **reference_id},
                    "new_binary": {"path": str(new_binary), **new_id},
                    "byte_identical": reference_id == new_id,
                    "source_lib_sha256": file_id(native / "src/lib.rs")["sha256"],
                    "source_main_sha256": file_id(native / "src/main.rs")["sha256"],
                    "new_materialization": json.loads((old / "postloss_native_crate/MATERIALIZATION.json").read_bytes()),
                    "published_materialization": json.loads((native / "evidence/MATERIALIZATION.json").read_bytes()),
                    "published_build": json.loads((native / "evidence/POSTLOSS_NATIVE_BUILD_RECEIPT.json").read_bytes())["binary"],
                    "ELF_sections": elf_comparison,
                    "new_package_fingerprint_metadata": fingerprint_rows(build / "target"),
                    "published_local_package_fingerprint_metadata": fingerprint_rows(reference_binary.parents[2]),
                    "observations": ["Materialized dependency path differs with the new checkout location.",
                                     "Source lib/main bytes, original owner113, compiler and Cargo identity match the published source scope.",
                                     "ELF section and package fingerprint differences are recorded; three CLI outputs match byte for byte."],
                    "cause_status": "UNRESOLVED: path/package metadata variation is observed; causality, exact instruction equivalence and a path-independent byte-reproduction recipe are not established.",
                    "scope": "Read-only comparison; neither native CLI nor any IVP is rerun."}
        save(output / "NATIVE_BINARY_BYTE_MISMATCH_OBSERVATIONS.json", metadata)
        receipt["native_binary_byte_identity"] = {"status": "MISMATCH", "published": reference_id,
                                                  "new_build": new_id, "cause_status": metadata["cause_status"]}

        gas = output / "original_gas_build"
        gas.mkdir()
        (gas / "cargo_home").mkdir()
        (gas / "target").mkdir()
        gas_env = dict(env)
        for key in list(gas_env):
            if key.startswith("CARGO_") or key.startswith("RUSTFLAGS") or key in {
                "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTDOC", "RUSTDOCFLAGS"}:
                gas_env.pop(key)
        gas_env.update(PATH=str(prefix / "bin") + os.pathsep + env.get("PATH", ""),
                       LD_LIBRARY_PATH=str(prefix / "lib"), RUSTC=str(prefix / "bin/rustc"),
                       CARGO_HOME=str(gas / "cargo_home"), CARGO_TARGET_DIR=str(gas / "target"),
                       CARGO_NET_OFFLINE="true")
        owner = repo / PREFIX / "run13/recovered/code/rei_bass_coupled"
        run("01_original_gas_fresh_build", [prefix / "bin/cargo", "build", "--release", "--offline",
                                           "--locked", "--example", "gas_rhs_server", "--jobs", "2"],
            cwd=owner, custom_env=gas_env, timeout=180)
        gas_id = file_id(gas / "target/release/examples/gas_rhs_server")
        receipt["original_gas_rebuild"] = {"binary": gas_id, "expected_sha256": EXPECTED_GAS,
                                           "expected_bytes": 571904,
                                           "exact_byte_identity": gas_id["sha256"] == EXPECTED_GAS and gas_id["bytes"] == 571904,
                                           "binary_process_executions": 0,
                                           "fresh_target": str(gas / "target")}
        if not receipt["original_gas_rebuild"]["exact_byte_identity"]:
            raise ValueError("original gas binary failed historical byte identity")
        before = json.loads((old / "03_git_source_before.json").read_bytes())["files"]
        after = []
        for row in before:
            path = shared.safe_path(repo, row["path"])
            identity = file_id(path)
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            if any(identity[key] != row[key] for key in ("bytes", "sha256", "git_blob")) or mode != row["mode"]:
                raise ValueError("source changed during scope completion: " + row["path"])
            after.append({"path": row["path"], "mode": mode, **identity})
        head = run("02_final_head", ["git", "rev-parse", "HEAD"]).decode().strip()
        tree = run("03_final_tree", ["git", "rev-parse", "HEAD^{tree}"]).decode().strip()
        index = file_id(repo / ".git/index")
        if head != EXPECTED_D or tree != original_receipt["science_tree"] or index != original_receipt["index_before"]:
            raise ValueError("Git HEAD/tree/index changed")
        save(output / "FINAL_SOURCE_UNCHANGED.json", {"science_commit": head, "science_tree": tree,
                                                     "tracked_files": len(after), "files": after,
                                                     "all_bytes_modes_unchanged": True, "index": index})
        receipt["unchanged_source"] = {"scoped_tracked_files": len(after),
                                       "all_scoped_bytes_modes_unchanged": True,
                                       "Git_head_tree_index_unchanged": True}
        receipt["status"] = "VERIFIED_SCOPED_WITH_BINARY_BYTE_MISMATCH"
        receipt["admissions"] = {
            "D_159_stage_files": "EXACT_BYTES_VERIFIED",
            "original_RUN13_payload333_manifest332_source113": "EXACT_BYTES_VERIFIED",
            "fixed_gas_five_settings_326_numeric_fields": "BIT_IDENTICAL",
            "postloss_native_three_controls": "BIT_IDENTICAL_NUMERIC_FIELDS_AND_EXACT_STDOUT",
            "postloss_native_binary_byte_identity": "FAILED_STRICT_GATE_RETAINED",
            "original_gas_binary_byte_identity": "EXACT_BYTES_VERIFIED",
            "preloss_RUN15_342_raw_case_files": "LOST_IN_CURRENT_SURFACE",
            "full_spectral_continuum_bound": "NOT_ESTABLISHED"}
    except Exception as exc:
        failure = exc
        receipt.update(status="FAILED_OR_BLOCKED", error_type=type(exc).__name__, error=str(exc),
                       traceback=traceback.format_exc())
    save(output / "SCOPED_CLEAN_COMPLETION_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"],
                      "receipt": str(output / "SCOPED_CLEAN_COMPLETION_RECEIPT.json"),
                      "native_controls": receipt.get("native_control_reproduction"),
                      "gas": receipt.get("original_gas_rebuild"), "error": receipt.get("error")}, indent=2), flush=True)
    return 0 if failure is None else 1

if __name__ == "__main__":
    raise SystemExit(main())
