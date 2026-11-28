#!/usr/bin/env python3
"""Create-only evidence snapshot. Does not execute science or infer admission."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3

BASE_COMMIT = "449dee7d05c9c055db04f0e7fa730bd4792a385c"
PRIOR_DB_SHA = "98d9acd99222a0080118157ce1ec2e71bff9630d310bb594ffac05ad414abb71"
PROMPT_SHA = "70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e"
PRIOR_STAGE_SHA = "575a7ad9e121d6c66d3c3614651c0a4baeb72d259f63ad389bf110893b03c609"
STAGE_RELATIVE = "audit_database/STAGE_RECONCILIATION.json"
STAGES = {"G" + str(i) for i in range(10)}
EXCLUDED = {"__pycache__", ".git", ".pytest_cache"}
STATUS_KEYS = {"status", "STATUS", "classification"}
EXIT_KEYS = {"exit_code", "returncode", "return_code"}
SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def source_files(root):
    """Never silently omit a symlink or a runtime failure file."""
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


def pointer_part(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def walk_json(value, pointer=""):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in sorted(value.items()):
            yield from walk_json(child, pointer + "/" + pointer_part(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_json(child, pointer + "/" + str(index))


def table_names(db):
    return [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]


def row_counts(db):
    return {name: db.execute('SELECT count(*) FROM "' + name + '"').fetchone()[0] for name in table_names(db)}


def logical_hash(db):
    content = {
        "schema": list(db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")),
        "tables": {name: sorted(canonical(row) for row in db.execute('SELECT * FROM "' + name + '"')) for name in table_names(db)},
    }
    return hashlib.sha256(canonical(content).encode()).hexdigest()


def checks(db):
    if list(db.execute("PRAGMA integrity_check")) != [("ok",)] or list(db.execute("PRAGMA foreign_key_check")):
        raise ValueError("Database integrity/foreign-key check failed")


def relative_source(root, text):
    if not isinstance(text, str) or not text:
        raise ValueError("Evidence path must be nonempty relative POSIX text")
    rel = PurePosixPath(text)
    if rel.is_absolute() or ".." in rel.parts or str(rel) != text or "\\" in text:
        raise ValueError("Evidence path must be canonical and inside its namespace")
    path = root / text
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence is not an available regular file: " + text)
    return path


def verify_snapshot(root, prior, prompt, prior_db, source_map):
    bases = {"continuation": root, "prior": prior}
    special = {"contract:ORIGINAL_USER_RESEARCH_PROMPT.txt": prompt,
               "checkpoint:continuation_audit.sqlite": prior_db}
    expected_new = set()
    for row in source_map["artifacts"]:
        aid = row["artifact_id"]
        path = special.get(aid)
        if path is None:
            path = relative_source(bases[row["namespace"]], row["relative_path"])
        if path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError("Source bytes changed: " + aid)
        if row["namespace"] == "continuation":
            expected_new.add(row["relative_path"])
    actual = {p.relative_to(root).as_posix() for p in source_files(root)}
    if actual != expected_new:
        raise ValueError("Continuation file set changed; rebuild into a new output directory")
    return True


def build(root, prior, prior_db, prompt, output):
    root, prior, prior_db, prompt, output = (Path(x).resolve() for x in (root, prior, prior_db, prompt, output))
    if output.exists():
        raise FileExistsError("Create-only output directory already exists: " + str(output))
    if output.is_relative_to(root) or output.is_relative_to(prior):
        raise ValueError("Generated DB must be outside current and prior source trees")
    for path, expected in ((prior_db, PRIOR_DB_SHA), (prompt, PROMPT_SHA), (prior / STAGE_RELATIVE, PRIOR_STAGE_SHA)):
        if sha(path) != expected:
            raise ValueError("Pinned prior source hash mismatch: " + str(path))
    recovery = load(root / "RECOVERY_INVENTORY.json")
    if recovery.get("base_commit") != BASE_COMMIT:
        raise ValueError("Unexpected recovery base commit")
    delta = load(root / "STAGE_DELTA.json")
    if (delta.get("schema") != "WU088_WIDE_DOMAIN_STAGE_DELTA_V1"
            or delta.get("base_commit") != BASE_COMMIT
            or delta.get("original_prompt_sha256") != PROMPT_SHA):
        raise ValueError("Stage delta contract identity mismatch")
    stages = delta.get("stages", [])
    if len(stages) != 10 or {s.get("id") for s in stages} != STAGES:
        raise ValueError("Stage delta must contain G0 through G9 exactly once")
    prior_stages = {s["id"]: s for s in load(prior / STAGE_RELATIVE)["stages"]}
    if set(prior_stages) != STAGES:
        raise ValueError("Prior stage identities differ")
    with sqlite3.connect(prior_db.as_uri() + "?mode=ro", uri=True) as old:
        checks(old)
        prior_counts, prior_logical = row_counts(old), logical_hash(old)
        prior_meta = dict(old.execute("SELECT key,value_json FROM meta"))
        if json.loads(prior_meta["original_prompt_sha256"]) != PROMPT_SHA:
            raise ValueError("Prior database prompt identity mismatch")
        prior_records = list(old.execute("SELECT artifact_id,namespace,relative_path,bytes,sha256 FROM artifacts ORDER BY artifact_id"))
        db_stages = dict(old.execute("SELECT stage_id,status FROM stage_delta WHERE delta_id LIKE 'ORIGINAL_PROMPT_RECONCILIATION_%'"))
        if db_stages != {key: val["current_status"] for key, val in prior_stages.items()}:
            raise ValueError("Prior SQLite stage state disagrees with prior reconciliation")
        if not any(r[2] == STAGE_RELATIVE and r[4] == PRIOR_STAGE_SHA for r in prior_records):
            raise ValueError("Prior stage JSON is not bound in prior database")
    artifacts, paths, documents = {}, {}, {}

    def add(namespace, relative, path):
        aid = namespace + ":" + relative
        if aid not in artifacts:
            artifacts[aid] = (aid, namespace, relative, path.stat().st_size, sha(path))
            paths[aid] = path
        return aid

    for path in source_files(root):
        aid = add("continuation", path.relative_to(root).as_posix(), path)
        if path.suffix.lower() == ".json":
            documents[aid] = load(path)
    prior_id = add("checkpoint", "continuation_audit.sqlite", prior_db)
    prompt_id = add("contract", "ORIGINAL_USER_RESEARCH_PROMPT.txt", prompt)
    prior_stage_id = add("prior", STAGE_RELATIVE, prior / STAGE_RELATIVE)
    for stage in stages:
        if stage.get("prior_status") != prior_stages[stage["id"]]["current_status"]:
            raise ValueError("Incorrect prior status: " + stage["id"])
        if any(not isinstance(stage.get(key), str) or not stage[key] for key in ("current_status", "scope")):
            raise ValueError("Explicit current status and scope required")
        if not isinstance(stage.get("remaining_gates"), list) or not all(isinstance(x, str) for x in stage["remaining_gates"]):
            raise ValueError("Explicit remaining_gates list required")
        if not isinstance(stage.get("evidence"), list) or not stage["evidence"]:
            raise ValueError("Every stage requires explicit evidence")
        for item in stage["evidence"]:
            if item.get("namespace") not in {"continuation", "prior"}:
                raise ValueError("Evidence namespace must be continuation or prior")
            base = root if item["namespace"] == "continuation" else prior
            path = relative_source(base, item.get("path"))
            if not isinstance(item.get("sha256"), str) or not SHA_PATTERN.fullmatch(item["sha256"]) or sha(path) != item["sha256"]:
                raise ValueError("Stage evidence SHA mismatch: " + str(path))
            add(item["namespace"], item["path"], path)
    # All validation above is read-only. Once created, a failed output remains for inspection.
    output.mkdir(parents=True, exist_ok=False)
    database = output / "wide_domain_audit.sqlite"
    metadata = {
        "schema": "WU088_WIDE_DOMAIN_AUDIT_V1", "base_commit": BASE_COMMIT,
        "original_prompt_sha256": PROMPT_SHA, "prior_database_sha256": PRIOR_DB_SHA,
        "prior_database_logical_sha256": prior_logical, "prior_database_row_counts": prior_counts,
        "status_policy": "Exact declared fields only; exit0, filenames, tests and source presence do not infer scientific completion or admission",
        "run_record_policy": "A record is a JSON mapping containing reported status or exit fields; nested/aggregate/historical records overlap and must not be summed as executions",
        "stage_policy": "Only root-authored STAGE_DELTA.json sets current G0-G9 labels; previous labels must match pinned prior SQLite and JSON",
        "prior_record_policy": "Prior artifact rows reproduce identities recorded in the pinned SQLite; their payloads are not all reread or newly verified",
        "snapshot_policy": "All current regular files except cache directories/pyc; byte hashes and file set checked again; late evidence requires a new create-only snapshot",
        "science_executed_by_builder": False, "original_research_database_recovery_claimed": False,
    }
    with sqlite3.connect(database) as db:
        db.executescript((root / "audit_database/schema.sql").read_text(encoding="utf-8"))
        db.executemany("INSERT INTO meta VALUES(?,?)", [(key, canonical(value)) for key, value in sorted(metadata.items())])
        db.executemany("INSERT INTO artifacts VALUES(?,?,?,?,?)", [artifacts[key] for key in sorted(artifacts)])
        db.executemany("INSERT INTO prior_artifact_records VALUES(?,?,?,?,?,?)", [tuple(row) + (prior_id,) for row in prior_records])

        def link(source, target, old_target, relation, pointer, declared, verification):
            fields = (source, target, old_target, relation, pointer, declared, verification)
            lid = hashlib.sha256(canonical(fields).encode()).hexdigest()
            db.execute("INSERT OR IGNORE INTO source_links VALUES(?,?,?,?,?,?,?,?)", (lid,) + fields)

        delta_id = "continuation:STAGE_DELTA.json"
        link(delta_id, prompt_id, None, "ORIGINAL_USER_CONTRACT", "/original_prompt_sha256", PROMPT_SHA, "MATCHES_AVAILABLE_BYTES")
        link(delta_id, prior_id, None, "CONTINUES_PINNED_DATABASE", None, PRIOR_DB_SHA, "MATCHES_AVAILABLE_BYTES")
        link(delta_id, prior_stage_id, None, "PRIOR_G0_G9_STATE", None, PRIOR_STAGE_SHA, "MATCHES_AVAILABLE_BYTES_AND_PRIOR_DATABASE")
        available_hashes, recorded_hashes = {}, {}
        for aid, row in artifacts.items():
            available_hashes.setdefault(row[4], []).append(aid)
        for row in prior_records:
            recorded_hashes.setdefault(row[4], []).append(row[0])
        for aid, document in sorted(documents.items()):
            references = {}
            for pointer, value in walk_json(document):
                if isinstance(value, str) and SHA_PATTERN.fullmatch(value):
                    references.setdefault(value, pointer)
                if not isinstance(value, dict) or not (STATUS_KEYS | EXIT_KEYS).intersection(value):
                    continue
                statuses = {key: value[key] for key in sorted(STATUS_KEYS.intersection(value))}
                exits = {key: value[key] for key in sorted(EXIT_KEYS.intersection(value))}
                scalars = {key: child for key, child in value.items() if not isinstance(child, (list, dict))}
                run_id = hashlib.sha256(canonical([aid, pointer]).encode()).hexdigest()
                db.execute("INSERT INTO run_records VALUES(?,?,?,?,?,?,?)", (run_id, aid, pointer, artifacts[aid][2].split("/")[0], canonical(statuses), canonical(exits), canonical(scalars)))
            for declared, pointer in sorted(references.items()):
                targets = available_hashes.get(declared, [])
                old_targets = recorded_hashes.get(declared, [])
                for target in targets:
                    link(aid, target, None, "DECLARED_SHA256", pointer, declared, "MATCHES_AVAILABLE_BYTES")
                for target in old_targets:
                    link(aid, None, target, "DECLARED_SHA256", pointer, declared, "MATCHES_PRIOR_DATABASE_RECORDED_IDENTITY")
                if not targets and not old_targets:
                    link(aid, None, None, "DECLARED_SHA256", pointer, declared, "REFERENCED_BYTES_NOT_INDEXED")
        for stage in sorted(stages, key=lambda s: s["id"]):
            db.execute("INSERT INTO stage_delta VALUES(?,?,?,?,?,?,?)", (stage["id"], stage["prior_status"], stage["current_status"], stage["scope"], canonical(stage["remaining_gates"]), delta_id, prior_stage_id))
            for item in stage["evidence"]:
                aid = item["namespace"] + ":" + item["path"]
                db.execute("INSERT OR IGNORE INTO stage_evidence VALUES(?,?,?)", (stage["id"], aid, item["sha256"]))
        db.commit()
        checks(db)
        counts, logical = row_counts(db), logical_hash(db)
        dump = "\n".join(db.iterdump()) + "\n"
        with (output / "wide_domain_audit.sql").open("x", encoding="utf-8") as stream:
            stream.write(dump)
        with sqlite3.connect(output / "restored_from_sql.sqlite") as restored:
            restored.executescript(dump)
            restored.execute("PRAGMA foreign_keys=ON")
            checks(restored)
            if row_counts(restored) != counts or logical_hash(restored) != logical:
                raise ValueError("SQL restoration mismatch")
    source_map = {"schema": "WU088_WIDE_DOMAIN_SOURCE_MAP_V1", "artifacts": [dict(zip(("artifact_id", "namespace", "relative_path", "bytes", "sha256"), artifacts[key])) for key in sorted(artifacts)]}
    verify_snapshot(root, prior, prompt, prior_db, source_map)
    write_json(output / "WIDE_DOMAIN_SOURCE_MAP.json", source_map)
    report = {
        "schema": "WU088_WIDE_DOMAIN_DB_VERIFICATION_V1", "status": "PASS_DATABASE_BUILD_AND_SQL_RESTORE",
        "base_commit": BASE_COMMIT, "prior_database_sha256": PRIOR_DB_SHA,
        "prior_database_preserved": sha(prior_db) == PRIOR_DB_SHA,
        "original_prompt_sha256": PROMPT_SHA, "row_counts": counts,
        "logical_sha256": logical, "restored_logical_sha256": logical,
        "integrity_check": "ok", "foreign_key_violations": 0,
        "source_snapshot_unchanged": True, "science_executed_by_builder": False,
        "run_counts_are_scientific_execution_counts": False,
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(output.iterdir()) if p.is_file()},
    }
    write_json(output / "WIDE_DOMAIN_DB_VERIFICATION.json", report)
    return report


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuation-root", type=Path, default=root)
    parser.add_argument("--prior-root", type=Path, default=root.parent / "native_execution_20261001_v1")
    parser.add_argument("--prior-db", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, default=root.parent / "production_solver_20261001_v1/audit/ORIGINAL_USER_RESEARCH_PROMPT.txt")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.continuation_root, args.prior_root, args.prior_db, args.prompt, args.output_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
