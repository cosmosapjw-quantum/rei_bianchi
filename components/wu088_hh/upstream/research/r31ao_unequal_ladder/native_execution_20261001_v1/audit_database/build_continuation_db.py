#!/usr/bin/env python3
"""Create-only continuation index. No numerical evaluation or provider access.

Source namespaces are relative to --continuation-root, --prior-root and their
research parent. Preserve the old audit SQL; rebuild into a new output directory
after all final runtime receipts are written. Only reported statuses are indexed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3


PROMPT_SHA = "70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e"
BASE_COMMIT = "c3f0cf25efdd50deca51355a237b863e5fcd631d"
ARCHIVE_SHAS = {"7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df",
                "53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87"}
OWN_OUTPUTS = {"continuation_audit.sqlite", "continuation_audit.sql", "restored_from_sql.sqlite",
               "CONTINUATION_DB_VERIFICATION.json", "CONTINUATION_SOURCE_MAP.json"}
FACT_KEYS = {"tests", "tests_run", "failures", "errors", "skipped", "returncode", "exit_code",
             "native_backend_runs", "native_executable_runs", "actual_HH_runs", "native_calls",
             "integrations", "actual_raw_decode_runs", "decoded_member_count", "decoded_logical_elements",
             "bounded_historical_layout_admitted", "actual_endpoint_task_evaluations",
             "actual_native_callback_integral_evaluations", "actual_full_D_certificates",
             "production_admitted", "production_admission", "scientific_admission", "rigorous",
             "continuum_error_certified", "historical_wheel_fidelity_claimed", "native_compiled",
             "native_executed", "wall_seconds", "elapsed_ns", "status", "STATUS", "scope", "schema",
             "reason", "native_runtime_executed", "mpi_runtime_verified", "ncp_host_benchmark",
             "callback_calls", "accepted_tasks", "completed_tasks", "classification", "run_kind"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def table_names(db):
    return [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]


def row_counts(db):
    return {name: db.execute('SELECT count(*) FROM "' + name + '"').fetchone()[0] for name in table_names(db)}


def logical_hash(db):
    content = {"schema": list(db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")),
               "tables": {name: sorted(canonical(row) for row in db.execute('SELECT * FROM "' + name + '"')) for name in table_names(db)}}
    return hashlib.sha256(canonical(content).encode()).hexdigest()


def checks(db):
    if list(db.execute("PRAGMA integrity_check")) != [("ok",)] or list(db.execute("PRAGMA foreign_key_check")):
        raise ValueError("Database integrity/foreign-key check failed")


def valid_source(path, root):
    rel = path.relative_to(root)
    return (path.is_file() and not path.is_symlink()
            and not any(part in {"__pycache__", ".git", ".pytest_cache"} for part in rel.parts)
            and path.suffix != ".pyc"
            and not (rel.parts[0] == "audit_database" and path.name in OWN_OUTPUTS))


def hash_references(value, prefix=""):
    if isinstance(value, dict):
        for key, child in sorted(value.items()):
            # Plans remain full hashed artifacts. Task/term identity arrays are
            # computational plans, not thousands of additional source files.
            if key in {"tasks", "terms", "values"} and isinstance(child, list):
                continue
            yield from hash_references(child, prefix + "/" + str(key).replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from hash_references(child, prefix + "/" + str(index))
    elif isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value):
        yield prefix, value


def build(root, prior, output):
    if output.exists():
        raise FileExistsError("Create-only output directory already exists: " + str(output))
    if output.is_relative_to(root) or output.is_relative_to(prior):
        raise ValueError("Place generated DB outside both source trees")
    scope = load(root / "SCOPE.json")
    if scope["base_commit"] != BASE_COMMIT:
        raise ValueError("Unexpected continuation base commit")
    prompt = prior / "audit/ORIGINAL_USER_RESEARCH_PROMPT.txt"
    prior_sql = prior / "audit/CURRENT_AUDIT.sql"
    if sha(prompt) != PROMPT_SHA:
        raise ValueError("Original prompt hash mismatch")
    old_pin = next(x for x in scope["old_production_source_inventory"] if x["path"] == "audit/CURRENT_AUDIT.sql")
    if sha(prior_sql) != old_pin["sha256"]:
        raise ValueError("Prior audit SQL changed since the base source inventory")
    sources = sorted(p for p in root.rglob("*") if valid_source(p, root))
    sources += [prompt, prior_sql, prior / "audit/AUDIT_DB_VERIFICATION.json", prior / "audit/STAGE_AUDIT.json",
                root.parent / "gap_closure_20261001_g0_g6_v1/exact_raw_decoder/decoder.py"]
    namespaces = [("continuation", root), ("prior", prior), ("research", root.parent)]
    artifacts, documents, identity = {}, {}, {}
    for path in sources:
        namespace, base = next((n, b) for n, b in namespaces if path.is_relative_to(b))
        relative = path.relative_to(base).as_posix()
        aid = namespace + ":" + relative
        pin = sha(path)
        artifacts[aid] = (aid, namespace, relative, path.stat().st_size, pin)
        identity[aid] = path
        # Exact array values and archived historical metadata are hash references,
        # not new execution records. Never infer runtime acceptance from names.
        if (path.suffix == ".json" and namespace == "continuation"
                and not relative.startswith("intake/evidence/")
                and not path.name.endswith((".exact_dyadic.json", ".provenance.json"))):
            documents[aid] = load(path)
    output.mkdir(parents=True, exist_ok=False)
    database = output / "continuation_audit.sqlite"
    with sqlite3.connect(database) as db:
        db.executescript((root / "audit_database/schema.sql").read_text())
        db.executemany("INSERT INTO artifacts VALUES(?,?,?,?,?)", [artifacts[k] for k in sorted(artifacts)])
        metadata = {"schema": "WU088_NATIVE_CONTINUATION_AUDIT_V1", "role": "ADDITIVE_CURRENT_EXECUTION_EVIDENCE_INDEX",
                    "base_commit": BASE_COMMIT, "original_prompt_sha256": PROMPT_SHA,
                    "prior_audit_sql_sha256": old_pin["sha256"],
                    "source_namespaces": {"continuation": "--continuation-root", "prior": "--prior-root", "research": "continuation parent"},
                    "status_policy": "Preserve reported status/exit only; filename, exit0 and source presence do not confer numerical or production admission",
                    "snapshot_policy": "Sources must remain unchanged during build; later runtime receipts require a fresh create-only build",
                    "source_link_policy": "One representative JSON pointer per referenced SHA; task/term/value arrays remain hash-bound whole artifacts",
                    "G2_scope_limit": "Exactly two reviewed B192 archives, twelve decoded real/complex NPY members; integer n.npy is metadata only",
                    "original_research_database_recovery_claimed": False}
        db.executemany("INSERT INTO meta VALUES(?,?)", [(k, canonical(v)) for k, v in sorted(metadata.items())])
        def link(source, target, relation, pointer=None, declared=None, verification="REFERENCE"):
            lid = hashlib.sha256(canonical([source, target, relation, pointer, declared]).encode()).hexdigest()
            db.execute("INSERT OR IGNORE INTO source_links VALUES(?,?,?,?,?,?,?)", (lid, source, target, relation, pointer, declared, verification))
        link("continuation:SCOPE.json", "prior:audit/CURRENT_AUDIT.sql", "CONTINUES_PRIOR_AUDIT", declared=old_pin["sha256"], verification="MATCHES_FROZEN_BASE_INVENTORY")
        link("continuation:SCOPE.json", "prior:audit/ORIGINAL_USER_RESEARCH_PROMPT.txt", "ORIGINAL_USER_CONTRACT", declared=PROMPT_SHA, verification="MATCHES_ORIGINAL_PROMPT_PIN")
        by_hash = {}
        for aid, row in artifacts.items():
            by_hash.setdefault(row[4], []).append(aid)
        runs = set()
        component_stages = {"assembly_host": "G7", "native_driver": "G6", "refined_native_driver": "G6",
                            "interior_design": "G6", "mpi_host": "EXECUTION_INFRASTRUCTURE",
                            "mpi_native_tasks": "EXECUTION_INFRASTRUCTURE", "backend_build": "G4",
                            "runtime": "RUNTIME_OBSERVATION"}
        for aid, data in sorted(documents.items()):
            if not isinstance(data, dict):
                continue
            unique_references = {}
            for pointer, declared in hash_references(data):
                unique_references.setdefault(declared, pointer)
            for declared, pointer in sorted(unique_references.items()):
                targets = by_hash.get(declared, [])
                if targets:
                    for target in targets:
                        link(aid, target, "DECLARED_SHA256", pointer, declared, "MATCHES_AVAILABLE_BYTES")
                else:
                    link(aid, None, "DECLARED_SHA256", pointer, declared, "REFERENCED_BYTES_NOT_INDEXED")
            if not any(key in data for key in ["status", "STATUS", "returncode", "exit_code"]):
                continue
            component = artifacts[aid][2].split("/")[0]
            status = data.get("status", data.get("STATUS"))
            status = status if isinstance(status, str) else None
            exit_code = data.get("returncode", data.get("exit_code"))
            exit_code = exit_code if type(exit_code) is int else None
            facts = {k: v for k, v in data.items() if k in FACT_KEYS and not isinstance(v, (list, dict))}
            reported_scope = data.get("scope") if isinstance(data.get("scope"), str) else None
            db.execute("INSERT INTO run_records VALUES(?,?,?,?,?,?,?,?)", (aid, aid, component, data.get("schema"), status, exit_code, reported_scope, canonical(facts)))
            runs.add(aid)
            if component in component_stages:
                db.execute("INSERT INTO stage_delta VALUES(?,?,?,?,?,?,?)", (aid, component_stages[component], status or "NO_EXPLICIT_STATUS_REPORTED", reported_scope or "Scope not specified in source record", aid, aid,
                            "Source record observation only; acceptance is not inferred from filename or exit status"))
        reconciliation_id = "continuation:audit_database/STAGE_RECONCILIATION.json"
        if reconciliation_id in documents:
            reconciliation = documents[reconciliation_id]
            if (reconciliation.get("schema") != "WU088_NATIVE_CONTINUATION_ORIGINAL_STAGE_RECONCILIATION_V1"
                    or reconciliation.get("base_commit") != BASE_COMMIT
                    or reconciliation.get("evidence", {}).get("prompt", {}).get("sha256") != PROMPT_SHA):
                raise ValueError("Stage reconciliation contract identity mismatch")
            stages = reconciliation.get("stages", [])
            expected = {"G" + str(i) for i in range(10)}
            if len(stages) != 10 or {stage.get("id") for stage in stages} != expected:
                raise ValueError("Stage reconciliation must explicitly contain G0 through G9 once")
            for stage in stages:
                if any(not isinstance(stage.get(key), str) or not stage[key]
                       for key in ("current_status", "scope")):
                    raise ValueError("Stage reconciliation requires explicit status and scope")
                claim_limit = canonical({
                    "policy": "Original-prompt reconciliation observation; no completion or admission inferred",
                    "remaining_gate_ko": stage.get("remaining_gate_ko", []),
                    "evidence_ids": stage.get("evidence_ids", [])})
                db.execute("INSERT INTO stage_delta VALUES(?,?,?,?,?,?,?)", (
                    "ORIGINAL_PROMPT_RECONCILIATION_" + stage["id"], stage["id"],
                    stage["current_status"], stage["scope"], reconciliation_id, None, claim_limit))
        review_id = "continuation:review/B192_BYTE_AND_SOURCE_REVIEW.json"
        decode_id = "continuation:intake/decoded/DECODE_RESULT.json"
        review, decoded = documents[review_id], documents[decode_id]
        admitted = (review.get("bounded_historical_layout_admitted") is True
                    and review.get("status") == "PASS_BOUNDED_HISTORICAL_LAYOUT_INFERENCE"
                    and {r["archive_sha256"] for r in review["npz_member_binding_observations"]} == ARCHIVE_SHAS
                    and decoded.get("status") == "PASS_BOUNDED_EXACT_RAW_DECODE"
                    and decoded.get("review_sha256") == artifacts[review_id][4]
                    and decoded.get("decoded_member_count") == 12
                    and decoded.get("decoded_logical_elements") == 4586
                    and len(decoded.get("decoded_members", [])) == 12)
        if not admitted:
            raise ValueError("Bounded G2 review/decode evidence chain is not satisfied")
        link(decode_id, review_id, "BOUNDED_LAYOUT_REVIEW", declared=decoded["review_sha256"], verification="MATCHES_AVAILABLE_BYTES")
        db.execute("INSERT INTO stage_delta VALUES(?,?,?,?,?,?,?)", ("G2_B192_TWO_ARCHIVE_DELTA", "G2", "BOUNDED_HISTORICAL_LAYOUT_AND_EXACT_RAW_DECODE_COMPLETE",
                    "Two exact B192 OD/JVP archives; 12 real/complex NPY members, 4586 logical elements; n.npy metadata only", decode_id, decode_id,
                    "Not universal G2, wheel fidelity, continuum error, model-gap, historical machine predicate or production admission"))
        db.commit()
        checks(db)
        counts, logical = row_counts(db), logical_hash(db)
        dump = "\n".join(db.iterdump()) + "\n"
        (output / "continuation_audit.sql").write_text(dump, encoding="utf-8")
        with sqlite3.connect(output / "restored_from_sql.sqlite") as restored:
            restored.executescript(dump)
            restored.execute("PRAGMA foreign_keys=ON")
            checks(restored)
            if row_counts(restored) != counts or logical_hash(restored) != logical:
                raise ValueError("SQL restoration mismatch")
        for aid, path in identity.items():
            if sha(path) != artifacts[aid][4] or path.stat().st_size != artifacts[aid][3]:
                raise ValueError("Source changed during build: " + aid)
        if sorted(str(p.relative_to(root)) for p in root.rglob("*") if valid_source(p, root)) != sorted(row[2] for row in artifacts.values() if row[1] == "continuation"):
            raise ValueError("Source file set changed during build")
        run_statuses = [list(row) for row in db.execute("SELECT component,reported_status,count(*) FROM run_records GROUP BY component,reported_status ORDER BY component,reported_status")]
    source_map = {"namespaces": metadata["source_namespaces"], "artifacts": [dict(zip(["artifact_id", "namespace", "relative_path", "bytes", "sha256"], artifacts[k])) for k in sorted(artifacts)]}
    (output / "CONTINUATION_SOURCE_MAP.json").write_text(json.dumps(source_map, indent=2) + "\n")
    report = {"schema": "WU088_CONTINUATION_DB_VERIFICATION_V1", "status": "PASS_DATABASE_BUILD_AND_SQL_RESTORE",
              "base_commit": BASE_COMMIT, "row_counts": counts, "logical_sha256": logical,
              "restored_logical_sha256": logical, "restored_row_counts_equal": True,
              "integrity_check": "ok", "foreign_key_violations": 0, "source_snapshot_unchanged": True,
              "prior_audit_preserved": True, "reported_run_statuses": run_statuses,
              "science_executed_by_builder": False,
              "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(output.iterdir()) if p.is_file()}}
    (output / "CONTINUATION_DB_VERIFICATION.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuation-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--prior-root", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.continuation_root.resolve()
    prior = args.prior_root.resolve() if args.prior_root else root.parent / "production_solver_20261001_v1"
    print(json.dumps(build(root, prior, args.output_root.resolve()), indent=2))


if __name__ == "__main__":
    main()
