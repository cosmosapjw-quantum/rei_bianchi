#!/usr/bin/env python3
"""Append a compact, source-bound W3 design audit without changing prior tables.

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

BASE_COMMIT = "b7e90411a155ce230d025871fc18e87e99fd9974"
PRIOR_DB_SHA = "a27bc17b9406f5fe558376e552381a08fdfe836fdd3ed362d83ad26ae7572ce6"
PROMPT_SHA = "70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e"
PRIOR_STAGE_SHA = "f6f55aaa745396edce2d431f3a8c39b9aecc1324b9f786ae6776f52a45482e1f"
STAGE_SCHEMA = "WU088_W3_DESIGN_STAGE_DELTA_V1"
LEDGER_SCHEMA = "WU088_W3_DESIGN_EXECUTION_LEDGER_V1"
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
    current = root
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("Evidence symlink component is not supported: " + text)
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
    bases = {"continuation": root, "prior": prior, "inherited": prior.parent}
    special = {"contract:ORIGINAL_USER_RESEARCH_PROMPT.txt": prompt,
               "checkpoint:w1_parallel_audit.sqlite": prior_db}
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


ENDPOINT_KINDS = {"ACTUAL_ENDPOINT_SELECTION", "ACTUAL_ENDPOINT_CROSSCHECK"}


def receipt_fields(receipt):
    """Read only explicit endpoint accounting; never infer integrations."""
    if not isinstance(receipt, dict):
        raise ValueError("Endpoint receipt must be a mapping")
    return {key: receipt.get(key) for key in (
        "kind", "accepted", "primitive_index", "status", "native_integration_invocations",
        "candidate_polynomial_evaluations", "actual_worker_observed")}


def endpoint_counts(records, host_events, evidence, historical_hashes):
    counts = {"actual_endpoint_selections": 0, "actual_endpoint_crosschecks": 0,
              "accepted_current_endpoint_records": 0, "rejected_current_endpoint_records": 0,
              "native_integration_invocations": 0, "candidate_polynomial_evaluations": 0,
              "host_events_not_invocations": len(host_events)}
    ids, receipts, outputs, rows = set(), set(), set(), []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Execution record must be a mapping")
        rid, kind = record.get("record_id"), record.get("kind")
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("Missing or duplicate record_id")
        ids.add(rid)
        if kind not in ENDPOINT_KINDS:
            raise ValueError("Unsupported endpoint execution kind; native integration is outside scope")
        if type(record.get("primitive_index")) is not int or record["primitive_index"] != 0:
            raise ValueError("This continuation is bound to primitive index 0")
        if record.get("actual_worker_observed") is not True:
            raise ValueError("Explicit observed endpoint worker required")
        if type(record.get("accepted")) is not bool:
            raise ValueError("Explicit boolean accepted required")
        if type(record.get("native_integration_invocations")) is not int or record["native_integration_invocations"] != 0:
            raise ValueError("Endpoint records cannot claim native integration invocations")
        if type(record.get("candidate_polynomial_evaluations")) is not int or record["candidate_polynomial_evaluations"] < 0:
            raise ValueError("Explicit nonnegative candidate polynomial count required")
        ref = record.get("receipt")
        aid, path = evidence(ref)
        if ref["namespace"] != "continuation":
            raise ValueError("Actual endpoint record must belong to continuation namespace")
        if ref["sha256"] in historical_hashes:
            raise ValueError("A historical receipt cannot count as a new endpoint operation")
        if ref["sha256"] in receipts:
            raise ValueError("Duplicate receipt SHA would double-count an endpoint operation")
        receipts.add(ref["sha256"])
        receipt = load(path)
        fields = receipt_fields(receipt)
        for key, value in fields.items():
            if record.get(key) != value or type(record.get(key)) is not type(value):
                raise ValueError("Ledger " + key + " disagrees with receipt")
        raw_ref = receipt.get("output")
        raw_aid, raw_path = evidence(raw_ref)
        if raw_ref["namespace"] != "continuation":
            raise ValueError("Actual endpoint output must belong to continuation namespace")
        if raw_ref["sha256"] in historical_hashes:
            raise ValueError("A historical output cannot count as a new endpoint operation")
        if raw_aid == aid or raw_ref["sha256"] == ref["sha256"]:
            raise ValueError("Endpoint receipt cannot be its own output")
        if raw_ref["sha256"] in outputs:
            raise ValueError("Duplicate output SHA would double-count an endpoint operation")
        outputs.add(raw_ref["sha256"])
        if not isinstance(record.get("status"), str) or not record["status"]:
            raise ValueError("Explicit observed status required")
        counts["actual_endpoint_selections" if kind == "ACTUAL_ENDPOINT_SELECTION" else "actual_endpoint_crosschecks"] += 1
        counts["accepted_current_endpoint_records" if record["accepted"] else "rejected_current_endpoint_records"] += 1
        counts["candidate_polynomial_evaluations"] += record["candidate_polynomial_evaluations"]
        rows.append((rid, kind, 0, int(record["accepted"]), record["status"], 0,
                     record["candidate_polynomial_evaluations"], aid, ref["sha256"], raw_aid, raw_ref["sha256"], canonical(record)))
    return counts, rows


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
        if any(name.startswith("w3_") for name in prior_state["objects"]):
            raise ValueError("Prior database already has W3 namespace")
        meta = dict(old.execute("SELECT key,value_json FROM meta"))
        if json.loads(meta["original_prompt_sha256"]) != PROMPT_SHA:
            raise ValueError("Prior database prompt mismatch")
        if dict(old.execute("SELECT stage_id,current_status FROM w1_stage_delta")) != prior_stages:
            raise ValueError("Prior SQLite stage state disagrees with prior JSON")
        if not old.execute("SELECT 1 FROM w1_artifacts WHERE relative_path=? AND sha256=?", ("STAGE_DELTA.json", PRIOR_STAGE_SHA)).fetchone():
            raise ValueError("Prior stage JSON identity is absent from pinned database")
        prior_artifacts = set(old.execute("SELECT namespace,relative_path,sha256 FROM w1_artifacts"))
        historical_hashes = {row[2] for row in prior_artifacts}
        if "artifacts" in prior_state["tables"]:
            historical_hashes.update(row[0] for row in old.execute("SELECT sha256 FROM artifacts"))
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
        if not isinstance(item, dict) or item.get("namespace") not in {"continuation", "prior", "inherited"}:
            raise ValueError("Evidence namespace must be continuation, prior, or inherited")
        bases = {"continuation": root, "prior": prior, "inherited": prior.parent}
        path = relative_source(bases[item["namespace"]], item.get("path"))
        if item["namespace"] == "inherited" and (path.resolve().is_relative_to(root) or path.resolve().is_relative_to(prior)):
            raise ValueError("Inherited evidence cannot alias continuation or prior")
        if not isinstance(item.get("sha256"), str) or not SHA_PATTERN.fullmatch(item["sha256"]) or sha(path) != item["sha256"]:
            raise ValueError("Explicit evidence SHA mismatch: " + str(path))
        return add(item["namespace"], item["path"], path), path

    for path in source_files(root):
        add("continuation", path.relative_to(root).as_posix(), path)
    add("checkpoint", "w1_parallel_audit.sqlite", prior_db)
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
    counts, rows = endpoint_counts(records, host_events, evidence, historical_hashes)
    if "counts" in ledger and ledger["counts"] != counts:
        raise ValueError("Declared ledger counts disagree with source-bound records")

    source_map = {"schema": "WU088_W3_SOURCE_MAP_V1", "base_commit": BASE_COMMIT,
                  "artifacts": [artifacts[k] for k in sorted(artifacts)]}
    verify_snapshot(root, prior, prompt, prior_db, source_map)
    output.mkdir(parents=True, exist_ok=False)
    database = output / "w3_design_audit.sqlite"
    metadata = {"schema": "WU088_W3_DESIGN_AUDIT_V1", "base_commit": BASE_COMMIT,
                "original_prompt_sha256": PROMPT_SHA, "prior_database_sha256": PRIOR_DB_SHA,
                "prior_database_logical_sha256": prior_state["logical_sha256"],
                "prior_database_row_counts": prior_state["row_counts"], "execution_counts": counts,
                "science_executed_by_builder": False, "scientific_admission_inferred": False,
                "execution_policy": "Only explicit current source-bound endpoint records count; polynomial evaluations are separate from native integrations, which remain zero; prior receipts are source references only",
                "validation_scope": "File identities and declared endpoint accounting fields; mathematical/source validity is delegated to explicit independent reviewer evidence",
                "index_policy": "Current file inventory and explicit stage/receipt links only; prior tables copied unchanged, no recursive SHA search"}
    with sqlite3.connect(prior_db.as_uri() + "?mode=ro", uri=True) as old, sqlite3.connect(database) as db:
        old.backup(db)
        db.executescript((root / "audit_database/schema.sql").read_text(encoding="utf-8"))
        db.executemany("INSERT INTO w3_meta VALUES (?,?)", [(k, canonical(v)) for k, v in sorted(metadata.items())])
        db.executemany("INSERT INTO w3_artifacts VALUES (?,?,?,?,?)", [(r["artifact_id"], r["namespace"], r["relative_path"], r["bytes"], r["sha256"]) for r in source_map["artifacts"]])
        db.executemany("INSERT INTO w3_execution_records VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        db.executemany("INSERT INTO w3_host_events VALUES (?,?)", [(i, canonical(e)) for i, e in enumerate(host_events)])
        db.executemany("INSERT INTO w3_stage_delta VALUES (?,?,?,?,?,?,?)", [(s["id"], s["prior_status"], s["current_status"], s["scope"], canonical(s["remaining_gates"]), "continuation:STAGE_DELTA.json", "prior:STAGE_DELTA.json") for s in stages])
        db.executemany("INSERT INTO w3_stage_evidence VALUES (?,?,?)", stage_evidence)
        db.commit(); checks(db)
        inherited = state(db, prior_state["tables"], prior_state["objects"])
        if inherited != prior_state:
            raise ValueError("Prior table contents/schema changed during append")
        combined = state(db)
        sql_path = output / "w3_design_audit.sql"
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
    write_json(output / "W3_SOURCE_MAP.json", source_map)
    report = {"schema": "WU088_W3_DB_VERIFICATION_V1", "status": "VERIFIED_LOCAL_APPEND_AND_SQL_RESTORE",
              "base_commit": BASE_COMMIT, "prior_database_sha256": PRIOR_DB_SHA,
              "prior_database_bytes_unchanged": True, "prior_tables_and_schema_preserved": True,
              "prior_row_counts": prior_state["row_counts"], "row_counts": combined["row_counts"],
              "database_logical_sha256": combined["logical_sha256"], "restored_logical_sha256": restored_state["logical_sha256"],
              "integrity_check": "ok", "foreign_key_violations": 0,
              "source_snapshot_unchanged": True, "execution_counts": counts,
              "database_delivery_limit_bytes": MAX_DATABASE_BYTES,
              "database_within_delivery_limit": True,
              "science_executed_by_builder": False, "cloud_restore_verified": False,
              "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in (database, sql_path, output / "W3_SOURCE_MAP.json")]}
    write_json(output / "W3_DB_VERIFICATION.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "prior", "prior-db", "prompt", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.prior, args.prior_db, args.prompt, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
