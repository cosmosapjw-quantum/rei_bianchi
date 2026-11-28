#!/usr/bin/env python3
"""Append a compact, source-bound W3 strip pilot audit without changing prior tables.

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

BASE_COMMIT = "48443cd754329cd6b76c99f6e9e887081df1e29e"
PRIOR_DB_SHA = "73558531543754826eaf7cfe27f6960a055ac17a865509de469f148d3ab84e7c"
PROMPT_SHA = "70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e"
PRIOR_STAGE_SHA = "c6fb021704d0b872cfab409291096a2b454cf33a065ad546d88dc411cea7d33b"
STAGE_SCHEMA = "WU088_W3_STRIP_STAGE_DELTA_V1"
LEDGER_SCHEMA = "WU088_W3_STRIP_EXECUTION_LEDGER_V1"
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
               "checkpoint:w3_design_audit.sqlite": prior_db}
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


NATIVE_KIND = "ACTUAL_NATIVE_PILOT"
REUSED_KIND = "REUSED_ACCEPTED_W1_TILE"
PILOT_TILE_IDS = {"20", "52", "105", "57"}
W1_TILE_IDS = {f"{i:02d}" for i in range(16)}
NO_NATIVE_SCHEMA = "WU088_W3_STRIP_NO_NATIVE_OUTPUT_V1"
NO_NATIVE_MARKERS = {"wrapper", "native_stdout", "native_stderr", "index", "native_receipt",
                     "native_execution_observed", "dispatched_evaluations", "integration_calls"}


def receipt_fields(receipt):
    """Read explicit run accounting; wrapper declarations are not execution proof."""
    if not isinstance(receipt, dict):
        raise ValueError("Pilot/reuse receipt must be a mapping")
    return {key: receipt.get(key) for key in (
        "kind", "tile_id", "accepted", "primitive_index", "status", "native_integration_invocations",
        "candidate_polynomial_evaluations", "actual_worker_observed")}


def native_fields(receipt):
    if not isinstance(receipt, dict):
        raise ValueError("Native output receipt must be a mapping")
    native = receipt
    if isinstance(receipt.get("native_stdout"), str):
        try:
            parsed = json.loads(receipt["native_stdout"])
            if isinstance(parsed, dict):
                native = parsed
        except (ValueError, TypeError):
            pass
    wrapper = receipt.get("wrapper", {})
    if not isinstance(wrapper, dict):
        raise ValueError("Native receipt wrapper must be a mapping")
    return {"accepted": receipt.get("accepted"), "primitive_index": receipt.get("index"),
            "native_execution_observed": wrapper.get("native_execution_observed"),
            "status": native.get("status", receipt.get("reason"))}


def execution_counts(records, host_events, evidence, historical_hashes, w1_reuse_bindings):
    counts = {"native_dispatch_attempts": 0, "observed_native_integrations": 0,
              "accepted_current_pilots": 0, "rejected_current_pilots": 0,
              "reused_W1_tiles": 0, "candidate_polynomial_evaluations": 0,
              "host_events_not_invocations": len(host_events)}
    ids, receipts, outputs, tiles, rows = set(), set(), set(), set(), []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Execution record must be a mapping")
        rid, kind, tile = record.get("record_id"), record.get("kind"), record.get("tile_id")
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("Missing or duplicate record_id")
        ids.add(rid)
        if kind not in {NATIVE_KIND, REUSED_KIND}:
            raise ValueError("Unsupported execution kind; endpoint execution is outside scope")
        actual = kind == NATIVE_KIND
        if not isinstance(tile, str) or tile not in (PILOT_TILE_IDS if actual else W1_TILE_IDS):
            raise ValueError("Tile identity is outside the bounded pilot or original W1 reuse set")
        if (kind, tile) in tiles:
            raise ValueError("Duplicate tile in the same execution class")
        tiles.add((kind, tile))
        if type(record.get("primitive_index")) is not int or record["primitive_index"] != 0:
            raise ValueError("This continuation is bound to primitive index 0")
        if type(record.get("accepted")) is not bool:
            raise ValueError("Explicit boolean accepted required")
        if record.get("actual_worker_observed") is not actual:
            raise ValueError("Current worker observation must distinguish actual and reused records")
        observed_count = record.get("native_integration_invocations")
        if type(observed_count) is not int or observed_count not in {0, 1} or (not actual and observed_count != 0):
            raise ValueError("Observed native invocation count must be zero/one for actual, zero for reuse")
        if actual and observed_count == 0 and record["accepted"]:
            raise ValueError("An accepted pilot requires an observed native output")
        if type(record.get("candidate_polynomial_evaluations")) is not int or record["candidate_polynomial_evaluations"] != 0:
            raise ValueError("Endpoint polynomial evaluations are outside this continuation")
        ref = record.get("receipt")
        aid, path = evidence(ref)
        if ref["namespace"] != "continuation":
            raise ValueError("Pilot/reuse root wrapper must belong to continuation namespace")
        if ref["sha256"] in historical_hashes:
            raise ValueError("A historical receipt cannot stand in for a current ledger wrapper")
        if ref["sha256"] in receipts:
            raise ValueError("Duplicate receipt SHA would double-count a record")
        receipts.add(ref["sha256"])
        receipt = load(path)
        fields = receipt_fields(receipt)
        for key, value in fields.items():
            if record.get(key) != value or type(record.get(key)) is not type(value):
                raise ValueError("Ledger " + key + " disagrees with receipt")
        raw_ref = receipt.get("output")
        raw_aid, raw_path = evidence(raw_ref)
        if raw_ref["namespace"] != ("continuation" if actual else "inherited"):
            raise ValueError("Raw output namespace must distinguish actual and reused records")
        if actual and raw_ref["sha256"] in historical_hashes:
            raise ValueError("A historical output cannot count as a new native invocation")
        if not actual and raw_ref["sha256"] not in historical_hashes:
            raise ValueError("Reused output must be hash-known in the inherited database")
        if not actual and w1_reuse_bindings.get(tile) != raw_ref["sha256"]:
            raise ValueError("Reused tile ID does not match its pinned W1 receipt identity")
        if raw_aid == aid or raw_ref["sha256"] == ref["sha256"]:
            raise ValueError("Root receipt cannot be its own native output")
        if raw_ref["sha256"] in outputs:
            raise ValueError("Duplicate native output SHA would double-count a record")
        outputs.add(raw_ref["sha256"])
        raw = load(raw_path)
        if actual and observed_count == 0:
            if (not isinstance(raw, dict) or raw.get("schema") != NO_NATIVE_SCHEMA
                    or raw.get("native_output_observed") is not False or raw.get("accepted") is not False):
                raise ValueError("Unobserved pilot requires explicit source-bound missing-output evidence")
            if NO_NATIVE_MARKERS.intersection(raw):
                raise ValueError("Missing-output evidence cannot also carry native receipt markers")
            observed = {"accepted": raw.get("accepted"), "primitive_index": raw.get("primitive_index"), "status": raw.get("status")}
        else:
            observed = native_fields(raw)
            if observed["native_execution_observed"] is not True:
                raise ValueError("Native receipt must record actual execution at its original time")
        for key in ("accepted", "primitive_index", "status"):
            if record.get(key) != observed[key] or type(record.get(key)) is not type(observed[key]):
                raise ValueError("Ledger " + key + " disagrees with native output")
        if not isinstance(record.get("status"), str) or not record["status"]:
            raise ValueError("Explicit observed status required")
        if actual:
            counts["native_dispatch_attempts"] += 1
            counts["observed_native_integrations"] += observed_count
            counts["accepted_current_pilots" if record["accepted"] else "rejected_current_pilots"] += 1
        else:
            if record["accepted"] is not True:
                raise ValueError("A reused W1 receipt must be accepted")
            counts["reused_W1_tiles"] += 1
        rows.append((rid, kind, tile, 0, int(record["accepted"]), record["status"], observed_count, 0,
                     aid, ref["sha256"], raw_aid, raw_ref["sha256"], canonical(record)))
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
        if any(name.startswith("w3strip_") for name in prior_state["objects"]):
            raise ValueError("Prior database already has W3 strip namespace")
        meta = dict(old.execute("SELECT key,value_json FROM meta"))
        if json.loads(meta["original_prompt_sha256"]) != PROMPT_SHA:
            raise ValueError("Prior database prompt mismatch")
        if dict(old.execute("SELECT stage_id,current_status FROM w3_stage_delta")) != prior_stages:
            raise ValueError("Prior SQLite stage state disagrees with prior JSON")
        if not old.execute("SELECT 1 FROM w3_artifacts WHERE relative_path=? AND sha256=?", ("STAGE_DELTA.json", PRIOR_STAGE_SHA)).fetchone():
            raise ValueError("Prior stage JSON identity is absent from pinned database")
        prior_artifacts = set(old.execute("SELECT namespace,relative_path,sha256 FROM w3_artifacts"))
        historical_hashes = {row[2] for row in prior_artifacts}
        w1_reuse_bindings = {}
        for tile, primitive, accepted, receipt_sha in old.execute(
                "SELECT tile_id,primitive_index,accepted,receipt_sha256 FROM w1_execution_records"):
            if primitive == 0 and accepted == 1:
                if tile in w1_reuse_bindings:
                    raise ValueError("Pinned W1 database has duplicate accepted tile identity")
                w1_reuse_bindings[tile] = receipt_sha
        for artifact_table in ("artifacts", "w1_artifacts"):
            if artifact_table in prior_state["tables"]:
                historical_hashes.update(row[0] for row in old.execute("SELECT sha256 FROM " + artifact_table))
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
    add("checkpoint", "w3_design_audit.sqlite", prior_db)
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
    counts, rows = execution_counts(records, host_events, evidence, historical_hashes, w1_reuse_bindings)
    if "counts" in ledger and ledger["counts"] != counts:
        raise ValueError("Declared ledger counts disagree with source-bound records")

    source_map = {"schema": "WU088_W3_STRIP_SOURCE_MAP_V1", "base_commit": BASE_COMMIT,
                  "artifacts": [artifacts[k] for k in sorted(artifacts)]}
    verify_snapshot(root, prior, prompt, prior_db, source_map)
    output.mkdir(parents=True, exist_ok=False)
    database = output / "w3_strip_audit.sqlite"
    metadata = {"schema": "WU088_W3_STRIP_AUDIT_V1", "base_commit": BASE_COMMIT,
                "original_prompt_sha256": PROMPT_SHA, "prior_database_sha256": PRIOR_DB_SHA,
                "prior_database_logical_sha256": prior_state["logical_sha256"],
                "prior_database_row_counts": prior_state["row_counts"], "execution_counts": counts,
                "science_executed_by_builder": False, "scientific_admission_inferred": False,
                "execution_policy": "Current pilot dispatches and observed native outputs are counted separately; inherited accepted W1 records count only as reuse; endpoint evaluations remain zero",
                "validation_scope": "File identities, declared dispatch/reuse accounting and raw native receipt fields; mathematical/source validity and proof of execution are delegated to explicit independent reviewer evidence",
                "index_policy": "Current file inventory and explicit stage/receipt links only; prior tables copied unchanged, no recursive SHA search"}
    with sqlite3.connect(prior_db.as_uri() + "?mode=ro", uri=True) as old, sqlite3.connect(database) as db:
        old.backup(db)
        db.executescript((root / "audit_database/schema.sql").read_text(encoding="utf-8"))
        db.executemany("INSERT INTO w3strip_meta VALUES (?,?)", [(k, canonical(v)) for k, v in sorted(metadata.items())])
        db.executemany("INSERT INTO w3strip_artifacts VALUES (?,?,?,?,?)", [(r["artifact_id"], r["namespace"], r["relative_path"], r["bytes"], r["sha256"]) for r in source_map["artifacts"]])
        db.executemany("INSERT INTO w3strip_execution_records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        db.executemany("INSERT INTO w3strip_host_events VALUES (?,?)", [(i, canonical(e)) for i, e in enumerate(host_events)])
        db.executemany("INSERT INTO w3strip_stage_delta VALUES (?,?,?,?,?,?,?)", [(s["id"], s["prior_status"], s["current_status"], s["scope"], canonical(s["remaining_gates"]), "continuation:STAGE_DELTA.json", "prior:STAGE_DELTA.json") for s in stages])
        db.executemany("INSERT INTO w3strip_stage_evidence VALUES (?,?,?)", stage_evidence)
        db.commit(); checks(db)
        inherited = state(db, prior_state["tables"], prior_state["objects"])
        if inherited != prior_state:
            raise ValueError("Prior table contents/schema changed during append")
        combined = state(db)
        sql_path = output / "w3_strip_audit.sql"
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
    write_json(output / "W3_STRIP_SOURCE_MAP.json", source_map)
    report = {"schema": "WU088_W3_STRIP_DB_VERIFICATION_V1", "status": "VERIFIED_LOCAL_APPEND_AND_SQL_RESTORE",
              "base_commit": BASE_COMMIT, "prior_database_sha256": PRIOR_DB_SHA,
              "prior_database_bytes_unchanged": True, "prior_tables_and_schema_preserved": True,
              "prior_row_counts": prior_state["row_counts"], "row_counts": combined["row_counts"],
              "database_logical_sha256": combined["logical_sha256"], "restored_logical_sha256": restored_state["logical_sha256"],
              "integrity_check": "ok", "foreign_key_violations": 0,
              "source_snapshot_unchanged": True, "execution_counts": counts,
              "database_delivery_limit_bytes": MAX_DATABASE_BYTES,
              "database_within_delivery_limit": True,
              "science_executed_by_builder": False, "cloud_restore_verified": False,
              "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in (database, sql_path, output / "W3_STRIP_SOURCE_MAP.json")]}
    write_json(output / "W3_STRIP_DB_VERIFICATION.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "prior", "prior-db", "prompt", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.prior, args.prior_db, args.prompt, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
