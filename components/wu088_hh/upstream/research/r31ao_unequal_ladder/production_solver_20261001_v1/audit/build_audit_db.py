#!/usr/bin/env python3
"""Build a new HH execution evidence index; never reconstruct the lost research DB.

Python standard library only. Inputs are read-only. --output-root must not exist.
Paths in the database use solver:, research:, and workspace_audit: namespaces;
provider paths retain their original namespace prefix. Rebuild after source changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE meta(key TEXT PRIMARY KEY, value_json TEXT NOT NULL CHECK(json_valid(value_json)));
CREATE TABLE artifacts(
 artifact_id TEXT PRIMARY KEY, namespace TEXT NOT NULL, relative_path TEXT NOT NULL,
 kind TEXT NOT NULL, present INTEGER NOT NULL CHECK(present IN (0,1)),
 bytes INTEGER CHECK(bytes>=0), sha256 TEXT CHECK(sha256 IS NULL OR length(sha256)=64),
 UNIQUE(namespace,relative_path), CHECK((present=0 AND bytes IS NULL AND sha256 IS NULL) OR
 (present=1 AND bytes IS NOT NULL AND sha256 IS NOT NULL)));
CREATE TABLE stage_audit(
 stage_id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,theory TEXT,
 implementation TEXT,execution TEXT,remaining TEXT,
 source_artifact_id TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE completion_checks(
 check_id INTEGER PRIMARY KEY,criterion TEXT NOT NULL,status TEXT NOT NULL,note TEXT,
 source_artifact_id TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE blocker_audit(
 blocker_id TEXT PRIMARY KEY,status TEXT NOT NULL,reason TEXT NOT NULL,
 source_artifact_id TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE provider_objects(
 provider TEXT NOT NULL,object_id TEXT NOT NULL,title TEXT NOT NULL,path TEXT,
 bytes INTEGER CHECK(bytes>=0),created_time TEXT,modified_time TEXT,
 source_artifact_id TEXT NOT NULL REFERENCES artifacts,
 PRIMARY KEY(provider,object_id));
CREATE TABLE database_snapshots(
 snapshot_id TEXT PRIMARY KEY,role TEXT NOT NULL,reported_identity_sha256 TEXT,
 verification_level TEXT NOT NULL,actual_content_read INTEGER NOT NULL CHECK(actual_content_read IN (0,1)),
 integrity_status TEXT,foreign_key_violations INTEGER,unchanged_after_read INTEGER,
 source_artifact_id TEXT NOT NULL REFERENCES artifacts,
 database_artifact_id TEXT REFERENCES artifacts,
 library_file_id TEXT,drive_file_id TEXT,archive_member TEXT,
 original_equivalence TEXT NOT NULL);
CREATE TABLE snapshot_table_counts(
 snapshot_id TEXT NOT NULL REFERENCES database_snapshots,table_name TEXT NOT NULL,
 row_count INTEGER NOT NULL CHECK(row_count>=0),PRIMARY KEY(snapshot_id,table_name));
CREATE TABLE component_runs(
 run_id TEXT PRIMARY KEY,component TEXT NOT NULL,run_kind TEXT NOT NULL,status TEXT NOT NULL,
 scope TEXT,tests_run INTEGER,failures INTEGER,errors INTEGER,native_backend_runs INTEGER,
 actual_hh_runs INTEGER,production_admitted INTEGER CHECK(production_admitted IN (0,1)),
 facts_json TEXT NOT NULL CHECK(json_valid(facts_json)),
 source_artifact_id TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE evidence_links(
 link_id TEXT PRIMARY KEY,artifact_id TEXT NOT NULL REFERENCES artifacts,
 stage_id TEXT REFERENCES stage_audit,check_id INTEGER REFERENCES completion_checks,
 blocker_id TEXT REFERENCES blocker_audit,run_id TEXT REFERENCES component_runs,
 relation TEXT NOT NULL,
 CHECK((stage_id IS NOT NULL)+(check_id IS NOT NULL)+(blocker_id IS NOT NULL)+(run_id IS NOT NULL)=1));
CREATE INDEX evidence_by_artifact ON evidence_links(artifact_id);
"""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def quote_identifier(value):
    return '"' + value.replace('"', '""') + '"'


def tables(connection):
    return [r[0] for r in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]


def counts(connection):
    return {name: connection.execute("SELECT count(*) FROM " + quote_identifier(name)).fetchone()[0]
            for name in tables(connection)}


def logical_digest(connection):
    """Schema plus canonically sorted rows, independent of SQLite page layout."""
    h = hashlib.sha256()
    schema = list(connection.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name"))
    h.update(canonical(schema).encode())
    for name in tables(connection):
        rows = sorted(canonical(row) for row in connection.execute("SELECT * FROM " + quote_identifier(name)))
        h.update(canonical([name, rows]).encode())
    return h.hexdigest()


def check_database(connection):
    integrity = [r[0] for r in connection.execute("PRAGMA integrity_check")]
    foreign = list(connection.execute("PRAGMA foreign_key_check"))
    if integrity != ["ok"] or foreign:
        raise ValueError(f"SQLite check failed: {integrity}, foreign-key violations={len(foreign)}")


class Builder:
    def __init__(self, connection, solver, audit):
        self.db = connection
        self.solver = solver
        self.audit = audit
        self.roots = [("solver", solver), ("research", solver.parent), ("workspace_audit", audit)]
        self.observed = {}

    def artifact(self, path, kind="evidence"):
        path = path.resolve()
        for namespace, root in self.roots:
            if path.is_relative_to(root):
                relative = path.relative_to(root).as_posix()
                break
        else:
            raise ValueError("Evidence outside declared source roots: " + str(path))
        aid = namespace + ":" + relative
        present = path.is_file()
        size = path.stat().st_size if present else None
        digest = sha(path) if present else None
        identity = (present, size, digest)
        if aid in self.observed and self.observed[aid][1] != identity:
            raise ValueError("Input changed during build: " + aid)
        self.observed[aid] = (path, identity)
        self.db.execute("INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?,?,?)",
                        (aid, namespace, relative, kind, int(present), size, digest))
        return aid

    def link(self, aid, subject, identity, relation):
        keys = {"stage_id": None, "check_id": None, "blocker_id": None, "run_id": None}
        keys[subject] = identity
        lid = hashlib.sha256(canonical([aid, subject, identity, relation]).encode()).hexdigest()
        self.db.execute("INSERT OR IGNORE INTO evidence_links VALUES(?,?,?,?,?,?,?)",
                        (lid, aid, *keys.values(), relation))

    def evidence(self, reference, subject, identity):
        path = (self.solver / reference).resolve()
        if reference.startswith("provider/") and not path.exists():
            path = (self.solver / "audit" / reference).resolve()
        if path.is_dir():
            files = [p for p in sorted(path.rglob("*")) if include_source(p)]
            if not files:
                self.link(self.artifact(path, "empty_directory_reference"), subject, identity, reference)
            for file in files:
                self.link(self.artifact(file), subject, identity, reference)
        else:
            self.link(self.artifact(path), subject, identity, reference)

    def local_catalog_path(self, value):
        path = Path(value)
        if path.is_relative_to(self.audit):
            return path
        # Catalogs can have been written in another workspace; preserve the suffix.
        if "production_audit" in path.parts:
            return self.audit.joinpath(*path.parts[path.parts.index("production_audit") + 1:])
        if not path.is_absolute():
            return self.audit / path
        raise ValueError("Unmappable catalog path: " + value)

    def verify_unchanged(self):
        for aid, (path, before) in self.observed.items():
            present = path.is_file()
            after = (present, path.stat().st_size if present else None, sha(path) if present else None)
            if before != after:
                raise ValueError("Input changed during build: " + aid)


def include_source(path):
    return (path.is_file() and not any(part in {"__pycache__", ".git", ".pytest_cache", "current_db"}
                                      for part in path.parts)
            and path.name not in {"current_audit.sql", "current_audit.sqlite", "AUDIT_DB_VERIFICATION.json"}
            and path.suffix not in {".pyc", ".sqlite", ".db"})


def import_stages(builder):
    path = builder.solver / "audit/STAGE_AUDIT.json"
    aid = builder.artifact(path, "stage_contract")
    data = read_json(path)
    if {x["id"] for x in data["stages"]} != {f"G{i}" for i in range(10)}:
        raise ValueError("Expected exactly G0 through G9")
    if ({x["id"] for x in data["original_completion_checklist"]} != set(range(1, 16))
            or {x["id"] for x in data["blockers"]} != {f"B{i:02d}" for i in range(1, 7)}):
        raise ValueError("Expected 15 completion checks and 6 blockers")
    for row in data["stages"]:
        builder.db.execute("INSERT INTO stage_audit VALUES(?,?,?,?,?,?,?,?)",
                           (*(row.get(k) for k in ["id", "title", "status", "theory", "implementation", "execution", "remaining"]), aid))
        for ref in row.get("evidence", []):
            builder.evidence(ref, "stage_id", row["id"])
    for row in data["original_completion_checklist"]:
        builder.db.execute("INSERT INTO completion_checks VALUES(?,?,?,?,?)",
                           (row["id"], row["criterion"], row["status"], row.get("note"), aid))
        builder.link(aid, "check_id", row["id"], "source_checklist")
        for ref in row.get("evidence", []):
            builder.evidence(ref, "check_id", row["id"])
    for row in data["blockers"]:
        builder.db.execute("INSERT INTO blocker_audit VALUES(?,?,?,?)",
                           (row["id"], row["status"], row["reason"], aid))
        builder.link(aid, "blocker_id", row["id"], "source_blocker_record")
        for ref in row.get("evidence", []):
            builder.evidence(ref, "blocker_id", row["id"])
    return data


def import_providers(builder):
    inputs = [("dropbox", "dropbox/RELEVANT_OBJECT_CATALOG.json"), ("drive", "drive/INVENTORY.json")]
    for provider, rel in inputs:
        path = builder.audit / rel
        aid = builder.artifact(path, "provider_inventory_input")
        source = read_json(path)
        rows = source if isinstance(source, list) else source["objects"]
        selected = {}
        for row in rows:
            title = row.get("title") or row.get("name") or ""
            remote_path = row.get("path") if provider == "dropbox" else row.get("url")
            if "WU088" not in title.upper() and "WU088" not in (remote_path or "").upper():
                continue
            oid = row.get("id") or row.get("file_id")
            if not oid:
                raise ValueError("Provider object has no id")
            if provider == "drive":
                # Persist a durable object reference, never a connector transfer URL.
                remote_path = "https://drive.google.com/file/d/" + oid + "/view"
            size = row.get("size", row.get("file", {}).get("size"))
            value = (provider, oid, title, remote_path, int(size) if size is not None else None,
                     row.get("created_time"), row.get("modified_time"), aid)
            if oid in selected and selected[oid] != value:
                raise ValueError("Conflicting duplicate provider object: " + oid)
            selected[oid] = value
        builder.db.executemany("INSERT INTO provider_objects VALUES(?,?,?,?,?,?,?,?)",
                               [selected[k] for k in sorted(selected)])


def import_snapshots(builder):
    path = builder.solver / "audit/provider/DATABASE_VERSION_CATALOG.json"
    if not path.is_file():
        path = builder.audit / "drive/DATABASE_VERSION_CATALOG.json"
    source_id = builder.artifact(path, "database_content_catalog")
    for row in sorted(read_json(path)["artifacts"], key=lambda r: r["role"]):
        role = row["role"]
        if "database" not in role and "catalog" not in role:
            continue
        expected = row.get("sha256") or row.get("manifest_sha256") or row.get("expected_reported_sha256")
        local = builder.local_catalog_path(row["local_path"]) if row.get("local_path") else None
        actual_read, integrity, foreign, unchanged, snapshot_counts = 0, None, None, None, {}
        db_id = builder.artifact(local, "prior_database_snapshot") if local else None
        level = row["verification_level"]
        if local and local.is_file():
            before = sha(local)
            if expected and before != expected:
                raise ValueError("Prior database hash mismatch: " + role)
            with sqlite3.connect(local.as_uri() + "?mode=ro&immutable=1", uri=True) as connection:
                connection.execute("PRAGMA query_only=ON")
                check_database(connection)
                snapshot_counts = counts(connection)
            if sha(local) != before:
                raise ValueError("Prior database mutated: " + role)
            actual_read, integrity, foreign, unchanged = 1, "ok", 0, 1
            level = "ACTUAL_BYTES_HASH_VERIFIED_READONLY_INTEGRITY_AND_COUNTS"
        elif local:
            level = "LOCAL_BYTES_UNAVAILABLE_PRIOR_CATALOG_CLAIM_ONLY"
        builder.db.execute("INSERT INTO database_snapshots VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            role, role, expected, level, actual_read, integrity, foreign, unchanged, source_id, db_id,
            row.get("library_file_id"), row.get("drive_file_id"), row.get("archive_member"),
            "NOT_CLAIMED; current audit index and acquisition catalogs do not recover lost theorem/method/test/risk entities"))
        builder.db.executemany("INSERT INTO snapshot_table_counts VALUES(?,?,?)",
                               [(role, table, count) for table, count in sorted(snapshot_counts.items())])


FACT_KEYS = {"tests_run", "failures", "errors", "skipped", "native_backend_runs", "actual_HH_runs",
             "actual_HH_computations", "archived_HH_array_reads", "native_compiled", "native_executed",
             "compile_exit_code", "test_exit_code", "cli_exit_code", "rigorous", "production_admitted",
             "scientific_admission", "independent_decision_review_admitted", "elapsed_seconds",
             "completed_tasks", "accepted_tasks", "schema", "scope", "status", "run_kind",
             "actual_endpoint_task_evaluations", "actual_native_callback_integral_evaluations",
             "actual_full_D_certificates", "source_terms", "engine_calls", "component_elapsed_ns",
             "process_exit_code", "radius_adequacy", "source_assembly_normalization_applied", "environment"}


def import_components(builder):
    for path in sorted(builder.solver.rglob("*")):
        if not include_source(path):
            continue
        aid = builder.artifact(path, "current_module_or_evidence")
        if path.suffix != ".json" or "provider" in path.relative_to(builder.solver).parts:
            continue
        data = read_json(path)
        if not isinstance(data, dict) or not ("status" in data or path.name == "WORKSPACE_INTAKE.json"):
            continue
        rel = path.relative_to(builder.solver)
        if rel.parts[0] not in {"composition", "endpoint_tasks", "native_driver", "primitive_join", "audit", "runtime"}:
            continue
        scope = str(data.get("scope", "UNSPECIFIED_IN_SOURCE"))
        kind = data.get("run_kind") or ("ACTUAL_ENDPOINT_COMPONENT" if "actual_endpoint_task_evaluations" in data
               else "WORKSPACE_INTAKE" if path.name == "WORKSPACE_INTAKE.json"
               else "SYNTHETIC_COMPONENT" if "synthetic" in (scope + path.name).lower()
               else "RECORDED_COMPONENT_EVIDENCE_NOT_SCIENTIFIC_ADMISSION")
        facts = {k: v for k, v in data.items() if k in FACT_KEYS and not isinstance(v, (dict, list))}
        execution = data.get("execution", {})
        admission = data.get("admission", {})
        native = data.get("native_backend_runs", execution.get("native_backend_runs"))
        actual = data.get("actual_HH_runs", data.get("actual_HH_computations"))
        admitted = data.get("production_admitted", admission.get("production_admitted"))
        builder.db.execute("INSERT INTO component_runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            aid, rel.parts[0], kind, str(data.get("status", "INTAKE_ONLY_NO_NATIVE_EXECUTION_CLAIM")), scope,
            data.get("tests_run"), data.get("failures"), data.get("errors"), native, actual,
            int(admitted) if isinstance(admitted, bool) else None, canonical(facts), aid))
        builder.link(aid, "run_id", aid, "recorded_component_manifest")


def build(solver, audit, output):
    if output.exists():
        raise FileExistsError("Create-only output root already exists: " + str(output))
    if output.is_relative_to(solver):
        raise ValueError("Output root must be outside the solver source tree")
    for required in [solver / "CURRENT_SCOPE.json", solver / "audit/STAGE_AUDIT.json",
                     audit / "dropbox/RELEVANT_OBJECT_CATALOG.json", audit / "drive/INVENTORY.json",
                     audit / "drive/DATABASE_VERSION_CATALOG.json"]:
        if not required.is_file():
            raise FileNotFoundError(required)
    output.mkdir(parents=True, exist_ok=False)
    database = output / "current_audit.sqlite"
    with sqlite3.connect(database) as connection:
        connection.executescript(SCHEMA)
        builder = Builder(connection, solver, audit)
        scope = read_json(solver / "CURRENT_SCOPE.json")
        stage = import_stages(builder)
        metadata = {"schema": "WU088_CURRENT_EXECUTION_AUDIT_V1", "role": "NEW_CURRENT_EVIDENCE_INDEX_NOT_ORIGINAL_RESEARCH_DB",
                    "current_scope": scope, "all_original_stages_complete": stage["all_original_stages_complete"],
                    "source_namespaces": {"solver": "production_solver_20261001_v1 root", "research": "solver parent research directory",
                                          "workspace_audit": "--workspace-audit-root"},
                    "provider_fields": ["provider", "object_id", "title", "path", "bytes", "created_time", "modified_time"],
                    "claims": "Recorded evidence only; synthetic/component results do not admit native, actual HH, or production execution",
                    "theorem_entities_imported": False}
        connection.executemany("INSERT INTO meta VALUES(?,?)", [(k, canonical(v)) for k, v in sorted(metadata.items())])
        builder.artifact(solver / "CURRENT_SCOPE.json", "current_scope")
        import_providers(builder)
        import_snapshots(builder)
        import_components(builder)
        for rel in ["dropbox/DROPBOX_DATABASE_CATALOG.json", "dropbox/DROPBOX_FINDINGS_KO.md",
                    "drive/DRIVE_AUDIT_KO.md", "drive/DATABASE_CONTENT_AUDIT_RAW.json",
                    "drive/DISTINCT_DATABASE_BYTE_AUDIT.json", "drive/V1_V3_CONTENT_COMPARISON.json",
                    "inputs/FROZEN_INPUTS_RECOVERY.json",
                    "inputs/FROZEN_INPUTS.npz", "ORIGINAL_USER_RESEARCH_PROMPT.txt"]:
            builder.artifact(audit / rel, "audit_source_reference_hash_only")
        builder.verify_unchanged()
        connection.commit()
        check_database(connection)
        row_counts = counts(connection)
        digest = logical_digest(connection)
        dump = "\n".join(connection.iterdump()) + "\n"
        (output / "current_audit.sql").write_text(dump, encoding="utf-8")
        restored = output / "restored_from_sql.sqlite"
        with sqlite3.connect(restored) as replica:
            replica.executescript(dump)
            replica.execute("PRAGMA foreign_keys=ON")
            check_database(replica)
            restored_counts, restored_digest = counts(replica), logical_digest(replica)
        if row_counts != restored_counts or digest != restored_digest:
            raise ValueError("SQL restoration logical identity mismatch")
        missing = [row[0] for row in connection.execute("SELECT artifact_id FROM artifacts WHERE present=0 ORDER BY artifact_id")]
        provider_counts = dict(connection.execute("SELECT provider,count(*) FROM provider_objects GROUP BY provider"))
        source_map = {"schema": "WU088_AUDIT_SOURCE_MAP_V1", "namespaces": metadata["source_namespaces"],
                      "artifacts": [dict(zip(["artifact_id", "namespace", "relative_path", "kind", "present", "bytes", "sha256"], row))
                                    for row in connection.execute("SELECT * FROM artifacts ORDER BY artifact_id")]}
        (output / "source_map.json").write_text(json.dumps(source_map, ensure_ascii=False, indent=2) + "\n")
        builder.verify_unchanged()
    report = {"schema": "WU088_CURRENT_AUDIT_DB_VERIFICATION_V1", "status": "PASS",
              "scope": "SQLite creation/read-only source audit/SQL restoration only; no scientific execution",
              "original_research_database_recovered": False, "row_counts": row_counts,
              "provider_counts": provider_counts, "integrity_check": "ok", "foreign_key_violations": 0,
              "logical_sha256": digest, "restored_logical_sha256": restored_digest,
              "restored_row_counts_equal": True, "missing_evidence_references": missing,
              "source_bytes_unchanged_during_build": True, "python": sys.version.split()[0],
              "sqlite_version": sqlite3.sqlite_version,
              "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
                        for p in [database, output / "current_audit.sql", restored, output / "source_map.json"]}}
    (output / "AUDIT_DB_VERIFICATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-audit-root", type=Path, required=True)
    parser.add_argument("--solver-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-root", type=Path, required=True, help="New directory; existing directories are refused")
    args = parser.parse_args()
    report = build(args.solver_root.resolve(), args.workspace_audit_root.resolve(), args.output_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
