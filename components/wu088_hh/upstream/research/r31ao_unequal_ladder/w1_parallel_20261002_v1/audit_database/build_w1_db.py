#!/usr/bin/env python3
"""Append a compact, source-bound W1 audit without changing prior tables.

This program records evidence. It never launches science, validates an integral,
or converts tests/JSON records into scientific admission.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3

BASE_COMMIT = "957714bff2d6c97cc5b3541baa3f2f83fdfa3182"
PRIOR_DB_SHA = "63347a8f9b4a04577af442280f9d8b630b82c719c4f4a9dee0039dc4351da118"
PROMPT_SHA = "70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e"
PRIOR_STAGE_SHA = "260a9171d64b79519f6a7b3570d692ff67a43a757d387a7be7635fb8fb589f09"
STAGE_SCHEMA = "WU088_W1_PARALLEL_STAGE_DELTA_V1"
LEDGER_SCHEMA = "WU088_W1_PARALLEL_EXECUTION_LEDGER_V1"
STAGES = {f"G{i}" for i in range(10)}
EXCLUDED = {"__pycache__", ".git", ".pytest_cache"}
SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
MAX_DATABASE_BYTES = 32 * 1024 * 1024


def canonical(value):
    def encode(obj):
        if isinstance(obj, bytes):
            return {"sqlite_blob_hex": obj.hex()}
        raise TypeError(type(obj).__name__)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False, default=encode)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def source_files(root):
    out = []
    for directory, folders, files in os.walk(root, followlinks=False):
        folders[:] = sorted(n for n in folders if n not in EXCLUDED)
        for name in folders + sorted(files):
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError("Source symlink is not supported: " + str(path))
            if path.is_file() and path.suffix != ".pyc":
                out.append(path)
    return sorted(out)


def relative_source(root, text):
    if not isinstance(text, str) or not text:
        raise ValueError("Evidence path must be nonempty relative POSIX text")
    relative = PurePosixPath(text)
    if relative.is_absolute() or ".." in relative.parts or str(relative) != text or "\\" in text:
        raise ValueError("Evidence path must be canonical and inside its namespace")
    path = root / text
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence is not an available regular file: " + text)
    return path


def quoted(name):
    return '"' + name.replace('"', '""') + '"'


def state(db, tables=None, objects=None):
    all_objects = list(db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"))
    if objects is not None:
        all_objects = [row for row in all_objects if row[1] in objects]
    if tables is None:
        tables = [row[1] for row in all_objects if row[0] == "table"]
    tables = sorted(tables)
    digest = hashlib.sha256(canonical(all_objects).encode())
    counts = {}
    for name in tables:
        rows = sorted(canonical(tuple(row)) for row in db.execute("SELECT * FROM " + quoted(name)))
        counts[name] = len(rows)
        digest.update(canonical([name, len(rows)]).encode())
        for row in rows:
            digest.update(row.encode()); digest.update(b"\n")
    return {"logical_sha256": digest.hexdigest(), "row_counts": counts,
            "schema": all_objects, "tables": tables, "objects": [row[1] for row in all_objects]}


def checks(db):
    if list(db.execute("PRAGMA integrity_check")) != [("ok",)] or list(db.execute("PRAGMA foreign_key_check")):
        raise ValueError("Database integrity/foreign-key check failed")


def identity(document, schema):
    if (document.get("schema") != schema or document.get("base_commit") != BASE_COMMIT
            or document.get("original_prompt_sha256") != PROMPT_SHA
            or document.get("prior_database_sha256") != PRIOR_DB_SHA):
        raise ValueError("Input contract identity mismatch: " + schema)


def verify_snapshot(root, prior, prompt, prior_db, source_map):
    bases = {"continuation": root, "prior": prior}
    special = {"contract:ORIGINAL_USER_RESEARCH_PROMPT.txt": prompt,
               "checkpoint:wide_domain_audit.sqlite": prior_db}
    expected_new = set()
    for row in source_map["artifacts"]:
        path = special.get(row["artifact_id"])
        if path is None:
            path = relative_source(bases[row["namespace"]], row["relative_path"])
        if path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError("Source bytes changed: " + row["artifact_id"])
        if row["namespace"] == "continuation":
            expected_new.add(row["relative_path"])
    actual = {p.relative_to(root).as_posix() for p in source_files(root)}
    if actual != expected_new:
        raise ValueError("Continuation file set changed; rebuild into a new output directory")
    return True


def receipt_fields(receipt):
    native = receipt
    if isinstance(receipt.get("native_stdout"), str):
        try:
            parsed = json.loads(receipt["native_stdout"])
            if isinstance(parsed, dict):
                native = parsed
        except (ValueError, TypeError):
            pass
    wrapper = receipt.get("wrapper", {})
    return {"accepted": receipt.get("accepted"), "primitive_index": receipt.get("index"),
            "native_execution_observed": wrapper.get("native_execution_observed"),
            "status": native.get("status", receipt.get("reason")),
            "evaluations": native.get("dispatched_evaluations"),
            "integration_calls": native.get("integration_calls"),
            "elapsed_wall_ns": wrapper.get("elapsed_wall_ns")}


def build(root, prior, prior_db, prompt, output):
    root, prior, prior_db, prompt, output = (Path(x).resolve() for x in (root, prior, prior_db, prompt, output))
    if output.exists():
        raise FileExistsError("Create-only output directory already exists: " + str(output))
    if output.is_relative_to(root) or output.is_relative_to(prior):
        raise ValueError("Generated DB must be outside current and prior source trees")
    for path, expected in ((prior_db, PRIOR_DB_SHA), (prompt, PROMPT_SHA), (prior / "STAGE_DELTA.json", PRIOR_STAGE_SHA)):
        if path.is_symlink() or sha(path) != expected:
            raise ValueError("Pinned prior source hash mismatch: " + str(path))
    if load(root / "RECOVERY_INVENTORY.json").get("base_commit") != BASE_COMMIT:
        raise ValueError("Unexpected recovery base commit")
    delta, ledger = load(root / "STAGE_DELTA.json"), load(root / "EXECUTION_LEDGER.json")
    identity(delta, STAGE_SCHEMA); identity(ledger, LEDGER_SCHEMA)
    prior_stages = {s["id"]: s["current_status"] for s in load(prior / "STAGE_DELTA.json")["stages"]}
    stages = delta.get("stages", [])
    if len(stages) != 10 or {s.get("id") for s in stages} != STAGES or set(prior_stages) != STAGES:
        raise ValueError("Stage delta must contain G0 through G9 exactly once")
    with sqlite3.connect(prior_db.as_uri() + "?mode=ro", uri=True) as old:
        checks(old); prior_state = state(old)
        if any(name.startswith("w1_") for name in prior_state["objects"]):
            raise ValueError("Prior database already has W1 namespace")
        meta = dict(old.execute("SELECT key,value_json FROM meta"))
        if json.loads(meta["original_prompt_sha256"]) != PROMPT_SHA:
            raise ValueError("Prior database prompt mismatch")
        if dict(old.execute("SELECT stage_id,current_status FROM stage_delta")) != prior_stages:
            raise ValueError("Prior SQLite stage state disagrees with prior JSON")
        if not old.execute("SELECT 1 FROM artifacts WHERE relative_path=? AND sha256=?", ("STAGE_DELTA.json", PRIOR_STAGE_SHA)).fetchone():
            raise ValueError("Prior stage JSON identity is absent from pinned database")
        prior_artifacts = set(old.execute("SELECT namespace,relative_path,sha256 FROM artifacts"))
        historical_hashes = {row[2] for row in prior_artifacts}
        if "prior_artifact_records" in prior_state["tables"]:
            historical_hashes.update(row[0] for row in old.execute("SELECT sha256 FROM prior_artifact_records"))

    artifacts = {}
    def add(namespace, relative, path):
        aid = namespace + ":" + relative
        row = {"artifact_id": aid, "namespace": namespace, "relative_path": relative,
               "bytes": path.stat().st_size, "sha256": sha(path)}
        if aid in artifacts and artifacts[aid] != row:
            raise ValueError("Source changed during intake: " + aid)
        artifacts[aid] = row
        return aid

    def evidence(item):
        if not isinstance(item, dict) or item.get("namespace") not in {"continuation", "prior"}:
            raise ValueError("Evidence namespace must be continuation or prior")
        path = relative_source(root if item["namespace"] == "continuation" else prior, item.get("path"))
        if not isinstance(item.get("sha256"), str) or not SHA_PATTERN.fullmatch(item["sha256"]) or sha(path) != item["sha256"]:
            raise ValueError("Explicit evidence SHA mismatch: " + str(path))
        return add(item["namespace"], item["path"], path), path

    for path in source_files(root):
        add("continuation", path.relative_to(root).as_posix(), path)
    add("checkpoint", "wide_domain_audit.sqlite", prior_db)
    add("contract", "ORIGINAL_USER_RESEARCH_PROMPT.txt", prompt)
    add("prior", "STAGE_DELTA.json", prior / "STAGE_DELTA.json")
    stage_evidence = []
    for stage in stages:
        sid = stage["id"]
        if stage.get("prior_status") != prior_stages[sid]:
            raise ValueError("Incorrect prior status: " + sid)
        if any(not isinstance(stage.get(k), str) or not stage[k] for k in ("current_status", "scope")):
            raise ValueError("Explicit current status and scope required")
        if not isinstance(stage.get("remaining_gates"), list) or not all(isinstance(x, str) for x in stage["remaining_gates"]):
            raise ValueError("Explicit remaining_gates list required")
        if not isinstance(stage.get("evidence"), list) or not stage["evidence"]:
            raise ValueError("Every stage requires explicit evidence")
        seen = set()
        for item in stage["evidence"]:
            aid, _ = evidence(item)
            if aid in seen:
                raise ValueError("Duplicate stage evidence: " + sid + ":" + aid)
            seen.add(aid); stage_evidence.append((sid, aid, item["sha256"]))

    records = ledger.get("records")
    host_events = ledger.get("host_events", [])
    if not isinstance(records, list) or not isinstance(host_events, list) or not all(isinstance(e, dict) for e in host_events):
        raise ValueError("Explicit records/host_events lists required")
    counts = {"actual_native_invocations": 0, "accepted_current_invocations": 0,
              "rejected_current_invocations": 0, "reused_accepted_receipts": 0,
              "host_events_not_invocations": len(host_events)}
    ids, receipts, rows = set(), set(), []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Execution record must be a mapping")
        rid, kind = record.get("record_id"), record.get("kind")
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("Missing or duplicate record_id")
        ids.add(rid)
        if kind not in {"ACTUAL_NATIVE_INVOCATION", "REUSED_ACCEPTED_RECEIPT"}:
            raise ValueError("Unsupported execution kind")
        if not isinstance(record.get("tile_id"), str) or not record["tile_id"]:
            raise ValueError("tile_id must be nonempty text")
        if type(record.get("primitive_index")) is not int or record["primitive_index"] != 0:
            raise ValueError("This continuation is bound to primitive index 0")
        if type(record.get("accepted")) is not bool or record.get("native_execution_observed") is not True:
            raise ValueError("Explicit boolean accepted and observed native execution required")
        ref = record.get("receipt")
        aid, path = evidence(ref)
        if ref["sha256"] in receipts:
            raise ValueError("Duplicate receipt SHA would double-count an invocation")
        receipts.add(ref["sha256"])
        expected_namespace = "continuation" if kind == "ACTUAL_NATIVE_INVOCATION" else "prior"
        if ref["namespace"] != expected_namespace:
            raise ValueError("Execution kind/receipt namespace mismatch")
        if kind == "ACTUAL_NATIVE_INVOCATION" and ref["sha256"] in historical_hashes:
            raise ValueError("A historical receipt cannot count as a new native invocation")
        if kind == "REUSED_ACCEPTED_RECEIPT" and ("continuation", ref["path"], ref["sha256"]) not in prior_artifacts:
            raise ValueError("Reused receipt is not recorded at that path/SHA in the prior database")
        fields = receipt_fields(load(path))
        for key in ("accepted", "primitive_index", "native_execution_observed", "status"):
            if record.get(key) != fields[key] or type(record.get(key)) is not type(fields[key]):
                raise ValueError("Ledger " + key + " disagrees with receipt")
        if not isinstance(record.get("status"), str) or not record["status"]:
            raise ValueError("Explicit observed status required")
        for key in ("evaluations", "integration_calls", "elapsed_wall_ns"):
            if key in record and (type(record[key]) is not int or record[key] < 0 or record[key] != fields[key]):
                raise ValueError("Ledger " + key + " disagrees with receipt")
        if kind == "REUSED_ACCEPTED_RECEIPT":
            if record["accepted"] is not True:
                raise ValueError("Reused receipt must be accepted")
            counts["reused_accepted_receipts"] += 1
        else:
            counts["actual_native_invocations"] += 1
            counts["accepted_current_invocations" if record["accepted"] else "rejected_current_invocations"] += 1
        rows.append((rid, kind, record["tile_id"], 0, int(record["accepted"]), record["status"], aid, ref["sha256"], canonical(record)))
    if "counts" in ledger and ledger["counts"] != counts:
        raise ValueError("Declared ledger counts disagree with source-bound records")

    source_map = {"schema": "WU088_W1_SOURCE_MAP_V1", "base_commit": BASE_COMMIT,
                  "artifacts": [artifacts[k] for k in sorted(artifacts)]}
    verify_snapshot(root, prior, prompt, prior_db, source_map)
    output.mkdir(parents=True, exist_ok=False)
    database = output / "w1_parallel_audit.sqlite"
    metadata = {"schema": "WU088_W1_PARALLEL_AUDIT_V1", "base_commit": BASE_COMMIT,
                "original_prompt_sha256": PROMPT_SHA, "prior_database_sha256": PRIOR_DB_SHA,
                "prior_database_logical_sha256": prior_state["logical_sha256"],
                "prior_database_row_counts": prior_state["row_counts"], "execution_counts": counts,
                "science_executed_by_builder": False, "scientific_admission_inferred": False,
                "execution_policy": "Only explicit receipt-bound ledger records count; imported accepted receipts and host events are separate from new native invocations",
                "validation_scope": "File identities and declared receipt fields; integral/source validity is delegated to explicit runner/reviewer evidence",
                "index_policy": "Current file inventory and explicit stage/receipt links only; prior tables copied unchanged, no recursive SHA search"}
    with sqlite3.connect(prior_db.as_uri() + "?mode=ro", uri=True) as old, sqlite3.connect(database) as db:
        old.backup(db)
        db.executescript((root / "audit_database/schema.sql").read_text(encoding="utf-8"))
        db.executemany("INSERT INTO w1_meta VALUES (?,?)", [(k, canonical(v)) for k, v in sorted(metadata.items())])
        db.executemany("INSERT INTO w1_artifacts VALUES (?,?,?,?,?)", [(r["artifact_id"], r["namespace"], r["relative_path"], r["bytes"], r["sha256"]) for r in source_map["artifacts"]])
        db.executemany("INSERT INTO w1_execution_records VALUES (?,?,?,?,?,?,?,?,?)", rows)
        db.executemany("INSERT INTO w1_host_events VALUES (?,?)", [(i, canonical(e)) for i, e in enumerate(host_events)])
        db.executemany("INSERT INTO w1_stage_delta VALUES (?,?,?,?,?,?,?)", [(s["id"], s["prior_status"], s["current_status"], s["scope"], canonical(s["remaining_gates"]), "continuation:STAGE_DELTA.json", "prior:STAGE_DELTA.json") for s in stages])
        db.executemany("INSERT INTO w1_stage_evidence VALUES (?,?,?)", stage_evidence)
        db.commit(); checks(db)
        inherited = state(db, prior_state["tables"], prior_state["objects"])
        if inherited != prior_state:
            raise ValueError("Prior table contents/schema changed during append")
        combined = state(db)
        sql_path = output / "w1_parallel_audit.sql"
        with sql_path.open("x", encoding="utf-8") as stream:
            for line in db.iterdump():
                stream.write(line + "\n")
    if database.stat().st_size > MAX_DATABASE_BYTES:
        raise ValueError("Database exceeds the 32 MiB delivery limit; failed output retained")
    restored_path = output / "restored_from_sql.sqlite"
    with sqlite3.connect(restored_path) as restored:
        restored.executescript(sql_path.read_text(encoding="utf-8"))
        checks(restored); restored_state = state(restored)
    if restored_state != combined:
        raise ValueError("SQL restore did not preserve logical contents and schema")
    verify_snapshot(root, prior, prompt, prior_db, source_map)
    if sha(prior_db) != PRIOR_DB_SHA:
        raise ValueError("Prior database bytes changed")
    write_json(output / "W1_SOURCE_MAP.json", source_map)
    report = {"schema": "WU088_W1_DB_VERIFICATION_V1", "status": "VERIFIED_LOCAL_APPEND_AND_SQL_RESTORE",
              "base_commit": BASE_COMMIT, "prior_database_sha256": PRIOR_DB_SHA,
              "prior_database_bytes_unchanged": True, "prior_tables_and_schema_preserved": True,
              "prior_row_counts": prior_state["row_counts"], "row_counts": combined["row_counts"],
              "database_logical_sha256": combined["logical_sha256"], "restored_logical_sha256": restored_state["logical_sha256"],
              "integrity_check": "ok", "foreign_key_violations": 0,
              "source_snapshot_unchanged": True, "execution_counts": counts,
              "database_delivery_limit_bytes": MAX_DATABASE_BYTES,
              "database_within_delivery_limit": True,
              "science_executed_by_builder": False, "cloud_restore_verified": False,
              "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in (database, sql_path, output / "W1_SOURCE_MAP.json")]}
    write_json(output / "W1_DB_VERIFICATION.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "prior", "prior-db", "prompt", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.prior, args.prior_db, args.prompt, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
