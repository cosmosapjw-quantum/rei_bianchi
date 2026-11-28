#!/usr/bin/env python3
"""Read saved HE-ANG hashes, receipts, DAG and 20 dual-provider ACKs.
No science import, test, IVP, network access, or source regeneration.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import tarfile
import uuid

EXPECTED = [f"R{i}" for i in range(1, 11)] + [f"C{i}" for i in range(1, 11)]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def default_unit():
    here = Path(__file__).resolve().parent
    return next((p for p in (here, *here.parents) if (p / "BUDGET.json").is_file()), here)


def atom(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, default=default_unit())
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="interim saved-evidence check; pending stages/manifests stay explicit")
    parser.add_argument("--archive-dir", type=Path, action="append", default=[],
                        help="restored stage-archive directory; may repeat; use ACK archive basename")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    unit = args.unit.resolve()
    errors, pending, notes = [], [], []
    protected = {(unit / n).resolve() for n in ("BUDGET.json", "CONTRACT.json",
                 "DAG.json", "RESOURCE_LEDGER.json", "SCIENCE_MANIFEST.json", "LOCAL_FILE_MANIFEST.json")}
    archive_cache, archive_reports = {}, []
    report = {"schema": "he_ang.saved_evidence_verification.v1",
              "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "unit": str(unit), "science_executions": 0,
              "remote_reads": 0, "remote_byte_verification": "NOT_PERFORMED",
              "errors": errors, "pending": pending, "notes": notes}
    def check(condition, message):
        if not condition:
            errors.append(message)
    def safe_path(relative):
        path = (unit / relative).resolve()
        if not path.is_relative_to(unit):
            raise ValueError("reference outside unit: " + str(relative))
        protected.add(path)
        return path
    def identity(row, context):
        path = safe_path(row["path"])
        if not path.is_file():
            errors.append(context + ": missing " + row["path"])
            return False
        expected_hash = row.get("sha256")
        check(isinstance(expected_hash, str) and len(expected_hash) == 64 and
              all(c in "0123456789abcdef" for c in expected_hash.lower()), context + ": valid SHA256 required " + row["path"])
        ok = True
        if "sha256" in row:
            ok = digest(path) == row["sha256"]
            check(ok, context + ": SHA256 mismatch " + row["path"])
        size = row.get("bytes", row.get("size"))
        if size is not None:
            check(path.stat().st_size == size, context + ": size mismatch " + row["path"])
        return ok

    def rows_of(value):
        rows = value["files"] if isinstance(value, dict) else value
        if isinstance(rows, dict):
            rows = [dict(v, path=k) if isinstance(v, dict)
                    else {"path": k, "sha256": v} for k, v in rows.items()]
        if not isinstance(rows, list):
            raise ValueError("manifest files must be a list or mapping")
        return rows

    def archive_payload(ack, stage):
        """Read bytes only; exact unit/relative members; never extract to disk."""
        original = Path(ack.get("local_path", ""))
        basename = Path(ack.get("archive") or original.name).name
        candidates = [original] if original.is_absolute() else [unit / original]
        candidates += [folder.resolve() / basename for folder in args.archive_dir]
        archive = next((path for path in candidates if path.is_file()), None)
        if archive is None:
            archive_reports.append({"stage": stage, "archive": basename, "status": "LOCAL_ARCHIVE_UNAVAILABLE"})
            return None
        archive = archive.resolve()
        protected.add(archive)
        key = (str(archive), ack.get("sha256"))
        if key in archive_cache:
            return archive_cache[key]
        result = {"available": True, "valid": True, "files": {}}
        entry = {"stage": stage, "archive": str(archive), "archive_sha256": digest(archive),
                 "payload_files_verified": 0, "manifest": "ABSENT"}
        archive_reports.append(entry)
        def archive_check(condition, text):
            if not condition:
                result["valid"] = False
                errors.append(stage + ": " + text)
        archive_check(archive.stat().st_size == ack["bytes"] and entry["archive_sha256"] == ack["sha256"],
                      "available local archive identity mismatch")
        if result["valid"]:
            with tarfile.open(archive, "r:*") as tf:
                members = [m for m in tf.getmembers() if m.isfile()]
                names = [m.name for m in members]
                archive_check(len(names) == len(set(names)), "duplicate archive member names")
                member_by_name = {m.name: m for m in members}
                root_manifest = member_by_name.get("MANIFEST.json")
                if root_manifest is not None:
                    manifest = json.load(tf.extractfile(root_manifest))
                    rows = rows_of(manifest)
                    entry["manifest"] = "MANIFEST.json"
                    if "stage" in manifest:
                        archive_check(manifest["stage"] == stage, "archive MANIFEST stage mismatch")
                    if "payload_files" in ack:
                        archive_check(len(rows) == ack["payload_files"], "archive MANIFEST payload count mismatch")
                    actual_unit_paths = {m.name[len("unit/"):] for m in members if m.name.startswith("unit/")}
                    if actual_unit_paths:
                        archive_check(actual_unit_paths == {r["path"] for r in rows}, "archive MANIFEST payload inventory mismatch")
                else:
                    rows = [{"path": m.name[len("unit/"):]} for m in members if m.name.startswith("unit/")]
                    notes.append(stage + ": archive identity verified; root MANIFEST absent")
                seen = set()
                for row in rows:
                    relative = row["path"]
                    pp = PurePosixPath(relative)
                    valid_relative = not pp.is_absolute() and ".." not in pp.parts and str(pp) == relative
                    archive_check(valid_relative, "noncanonical archive MANIFEST path: " + relative)
                    if not valid_relative:
                        continue
                    archive_check(relative not in seen, "duplicate archive MANIFEST path: " + relative)
                    seen.add(relative)
                    aliases = ("unit/" + relative, relative, unit.name + "/" + relative)
                    matches = [member_by_name[name] for name in aliases if name in member_by_name]
                    archive_check(len(matches) == 1, "missing/ambiguous archive payload: " + relative)
                    if len(matches) != 1:
                        continue
                    payload = tf.extractfile(matches[0]).read()
                    actual = {"sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}
                    if root_manifest is not None:
                        archive_check(actual["sha256"] == row.get("sha256"), "MANIFEST payload SHA256 mismatch: " + relative)
                        expected_size = row.get("size", row.get("bytes"))
                        archive_check(isinstance(expected_size, int) and actual["size"] == expected_size,
                                      "MANIFEST payload size mismatch: " + relative)
                    result["files"][relative] = actual
                    entry["payload_files_verified"] += 1
        entry["status"] = "VERIFIED" if result["valid"] else "FAILED"
        archive_cache[key] = result
        return result

    lock = None
    try:
        lock_path = unit / "evidence/execution/RESOURCE.lock"
        if lock_path.exists():
            lock = lock_path.open("r")
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        budget = read(unit / "BUDGET.json")
        contract = read(unit / "CONTRACT.json")
        fixed = {name: digest(unit / name) for name in ("BUDGET.json", "CONTRACT.json")}
        report["frozen_inputs"] = fixed
        check(contract["unit_id"] == budget["fresh_unit"], "contract/budget unit mismatch")

        manifests = {}
        for name in ("SCIENCE_MANIFEST.json", "LOCAL_FILE_MANIFEST.json"):
            path = unit / name
            if not path.is_file():
                pending.append("final manifest absent: " + name)
                continue
            value = read(path)
            rows = rows_of(value)
            paths = [r["path"] for r in rows]
            check(bool(rows), name + ": empty manifest")
            check(len(paths) == len(set(paths)), name + ": duplicate paths")
            check(name not in paths, name + ": self hash reference is not permitted")
            for row in rows:
                identity(row, name)
            manifests[name] = {"files": len(rows), "manifest_sha256": digest(path),
                               "manifest_dependencies": [n for n in ("SCIENCE_MANIFEST.json", "LOCAL_FILE_MANIFEST.json") if n in paths]}
        report["manifests"] = manifests
        if len(manifests) == 2:
            check(not ("LOCAL_FILE_MANIFEST.json" in manifests["SCIENCE_MANIFEST.json"]["manifest_dependencies"] and
                       "SCIENCE_MANIFEST.json" in manifests["LOCAL_FILE_MANIFEST.json"]["manifest_dependencies"]),
                  "science/local manifests form a circular hash reference")
        report["publication_scope"] = "Saved science/content identities only; Git expected-SHA push/readback and delivery-containing commit identity require their separate receipts. No publication approval is inferred."

        dag = read(unit / "DAG.json")
        nodes = dag["nodes"]
        ids = [n["id"] for n in nodes]
        check(ids == EXPECTED, "DAG must preserve R1-R10 then C1-C10 order")
        check(dag["total"] == 20, "DAG total differs from 20")
        complete = [n for n in nodes if n["status"] == "complete"]
        check(dag["completed"] == len(complete), "DAG completion count mismatch")
        check(dag.get("no_merge") is True and dag.get("no_activation") is True,
              "DAG no-merge/no-activation holds changed")
        check(dag.get("physical_goal_completion_percentage") is None,
              "undefined total physical goal percentage became numeric")
        complete_ids = {n["id"] for n in complete}
        ack_count, historical = 0, []
        for node in nodes:
            if node["status"] != "complete":
                pending.append("stage not complete: " + node["id"])
                continue
            check(set(node.get("depends_on", [])).issubset(complete_ids),
                  node["id"] + ": incomplete predecessor")
            ack_path = safe_path(node.get("backup_evidence", "delivery/" + node["id"] + "_ACK.json"))
            if not ack_path.is_file():
                errors.append(node["id"] + ": missing backup ACK")
                continue
            ack = read(ack_path)
            check(ack.get("stage") == node["id"], node["id"] + ": ACK stage mismatch")
            archive_size = ack.get("bytes")
            check(isinstance(archive_size, int) and archive_size > 0,
                  node["id"] + ": archive byte size missing")
            check(isinstance(ack.get("sha256"), str) and len(ack["sha256"]) == 64,
                  node["id"] + ": local archive SHA256 absent")
            for provider in ("dropbox", "drive"):
                p = ack.get(provider, {})
                check(p.get("status") in ("completed", "completed_metadata_verified"),
                      node["id"] + ": " + provider + " ACK not completed")
                check(bool(p.get("id")) and p.get("bytes") == archive_size,
                      node["id"] + ": " + provider + " identity/size mismatch")
            check(node.get("backup") == "dual_acknowledged", node["id"] + ": DAG backup status")
            ack_count += 1
            archived = archive_payload(ack, node["id"])
            for row in node.get("evidence", []):
                path = safe_path(row["path"])
                if path.is_file() and digest(path) == row["sha256"]:
                    continue
                # Stage references retain their epoch. Available wrong bytes are errors;
                # absent archived bytes are pending, never a final-complete claim.
                archived_ok = archived is not None and archived["valid"] and archived["files"].get(row["path"], {}).get("sha256") == row["sha256"]
                historical.append({"stage": node["id"], "path": row["path"],
                                   "sha256": row["sha256"], "verified_in_local_stage_archive": archived_ok})
                if archived is None:
                    pending.append(node["id"] + ": historical archive required for " + row["path"])
                else:
                    check(archived_ok, node["id"] + ": available archive missing/mismatched historical evidence " + row["path"])
            preflight = node.get("preflight")
            if preflight:
                check(safe_path(preflight).is_file(), node["id"] + ": missing preflight reference")
        report["dag"] = {"completed": len(complete), "total": 20,
                         "dual_ack_records_checked": ack_count,
                         "historical_references": historical,
                         "ack_scope": "saved provider ACK identity/size; not fresh remote readback"}

        report["stage_archives"] = archive_reports
        ledger_path = unit / "RESOURCE_LEDGER.json"
        if not ledger_path.is_file():
            pending.append("no resource execution ledger")
        else:
            ledger = read(ledger_path)
            check(ledger.get("schema") == "he_ang.resource_events.v1", "resource schema mismatch")
            check(ledger.get("frozen_inputs") == fixed, "resource frozen input identity changed")
            check(not ledger.get("unknown_cost_records"), "resource unknown costs block completion")
            starts, finishes, summaries = {}, {}, []
            total_cpu, total_wall = 0.0, 0.0
            for event in ledger["events"]:
                path = safe_path(event["record"])
                check(path.is_file() and digest(path) == event["sha256"],
                      "resource record identity: " + event["record"])
                rec = read(path)
                ident = event["attempt_id"]
                check(rec["attempt_id"] == ident, "resource attempt ID mismatch")
                if event["event"] == "START":
                    check(ident not in starts, "duplicate START: " + ident)
                    check(starts.keys() == finishes.keys(), "overlapping resource STARTs")
                    check(rec["prior_consumed_cpu_s"] == total_cpu and rec["prior_consumed_wall_s"] == total_wall,
                          "START prior debit mismatch: " + ident)
                    check(rec["frozen_inputs"] == fixed, "START frozen identity: " + ident)
                    starts[ident] = rec
                elif event["event"] == "FINISH":
                    check(ident in starts and ident not in finishes, "unmatched/duplicate FINISH: " + ident)
                    check(rec["cost_status"] == "KNOWN_CHILD_REAPED", "unknown child cost: " + ident)
                    for key in ("cpu_charge_s", "wall_charge_s"):
                        check(isinstance(rec.get(key), (int, float)) and math.isfinite(rec[key]) and rec[key] >= 0,
                              "invalid charge: " + ident + "/" + key)
                    check(rec["cpu_charge_s"] == rec["child_cpu_s"] + rec["wrapper_cpu_known_s"],
                          "child/wrapper CPU charge sum mismatch: " + ident)
                    check(rec["wall_charge_s"] == rec["wrapper_wall_observed_s"] and
                          0 <= rec["child_wall_s"] <= rec["wall_charge_s"],
                          "child/wrapper wall charge mismatch: " + ident)
                    total_cpu += rec["cpu_charge_s"]
                    total_wall += rec["wall_charge_s"]
                    limits = rec["limits"]
                    check(limits["cpu_s"] <= budget["per_invocation"]["cpu_s"] and
                          limits["wall_s"] <= budget["per_invocation"]["wall_s"] and
                          limits["address_space_bytes"] <= budget["cap"]["peak_address_space_bytes"],
                          "attempt limits exceed frozen budget: " + ident)
                    check(rec["frozen_inputs"] == fixed, "FINISH frozen identity: " + ident)
                    for relative, value in rec.get("outputs", {}).items():
                        output = (path.parent / relative).resolve()
                        protected.add(output)
                        check(output.is_relative_to(path.parent) and output.is_file() and
                              output.stat().st_size == value["bytes"] and digest(output) == value["sha256"],
                              "saved output identity: " + ident + "/" + relative)
                    finishes[ident] = rec
                    summaries.append({"attempt_id": ident, "state": rec["state"],
                                      "cpu_charge_s": rec["cpu_charge_s"], "wall_charge_s": rec["wall_charge_s"]})
                else:
                    errors.append("unknown resource event")
            check(starts.keys() == finishes.keys(), "unresolved START blocks completion")
            for start_path in (unit / "evidence/execution/attempts").glob("*/START.json"):
                check(read(start_path)["attempt_id"] in starts, "orphan saved START")
            check(total_cpu == ledger.get("known_consumed_cpu_s"), "CPU ledger sum mismatch")
            check(total_wall == ledger.get("known_consumed_wall_s"), "wall ledger sum mismatch")
            remaining_cpu = budget["cap"]["cpu_s"] - total_cpu
            remaining_wall = budget["cap"]["wall_s"] - total_wall
            check(remaining_cpu == ledger.get("remaining_cpu_s"), "CPU remaining mismatch")
            check(remaining_wall == ledger.get("remaining_wall_s"), "wall remaining mismatch")
            check(remaining_cpu >= 0 and remaining_wall >= 0, "cumulative budget exceeded")
            report["resources"] = {"attempts": summaries, "known_consumed_cpu_s": total_cpu,
                                   "known_consumed_wall_s": total_wall,
                                   "remaining_cpu_s": remaining_cpu, "remaining_wall_s": remaining_wall,
                                   "scope": "saved whole-child/known-wrapper receipts; no new timing experiment"}
    except Exception as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    finally:
        if lock is not None:
            lock.close()
    output_allowed = args.output is None or args.output.resolve() not in protected
    if not output_allowed:
        errors.append("--output would overwrite verified input/evidence; choose an unmanifested report path")
    if errors:
        report["status"] = "FAIL_SAVED_EVIDENCE"
    elif pending:
        report["status"] = "IN_PROGRESS_SAVED_EVIDENCE"
    else:
        report["status"] = "PASS_SAVED_EVIDENCE"
    report["final_complete"] = not errors and not pending
    report["historical_reference_qualification"] = "Current manifests are verified directly; historical stage evidence must match available archive/MANIFEST bytes. Missing required historical bytes remain pending; a mismatch is a saved-evidence error, not an automatic new scientific verdict."
    if args.output and output_allowed:
        atom(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 1 if errors or (pending and not args.allow_incomplete) else 0


if __name__ == "__main__":
    raise SystemExit(main())
