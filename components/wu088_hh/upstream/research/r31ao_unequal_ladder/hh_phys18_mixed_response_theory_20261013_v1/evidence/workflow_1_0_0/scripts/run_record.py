#!/usr/bin/env python3
"""Create and check optional research/coding run records.

  run_record.py init --task research|coding|both --unit-id UNIT --output PATH
  run_record.py check PATH

Initialization uses exclusive creation. Checks cover JSON structure, enumerated
states, references and reuse identities; they do not assess scientific validity,
inspect external evidence, execute commands, or convert existing project state.
Unknown informational fields are preserved and are not interpreted as evidence.
"""

import argparse
import json
from pathlib import Path
import sys


WORKFLOW = Path(__file__).resolve().parents[1] / "references" / "WORKFLOW.json"
COLLECTIONS = ("dependencies", "evidence", "stages", "claims", "checks", "executions")
NOTES = ("decisions", "overrides", "failures", "next_actions")
OPEN_BASES = {"conjectural", "unresolved", "blocked"}
EVALUATED = {"pass_scoped", "partial", "fail"}
CLOSED = {"complete", "reused", "not_applicable"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def load_workflow():
    workflow = read_json(WORKFLOW)
    if not isinstance(workflow, dict) or type(workflow.get("schema_version")) is not int \
            or workflow["schema_version"] != 1 or workflow.get("workflow_version") != "1.0.0":
        raise ValueError("WORKFLOW.json must define schema 1 and workflow 1.0.0")
    tracks = workflow.get("tracks")
    if not isinstance(tracks, dict):
        raise ValueError("WORKFLOW.json tracks must be an object")
    for task, prefix in (("research", "R"), ("coding", "C")):
        rows = tracks.get(task)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows) \
                or [row.get("id") for row in rows] != [f"{prefix}{i}" for i in range(1, 11)]:
            raise ValueError(f"WORKFLOW.json must define ordered {prefix}1–{prefix}10")
    for key in ("task_statuses", "stage_statuses", "evidence_kinds", "claim_bases",
                "check_domains", "check_results", "execution_statuses", "failure_classes",
                "no_go_criteria"):
        values = workflow.get(key)
        if not isinstance(values, list) or not values \
                or any(not isinstance(value, str) or not value.strip() for value in values) \
                or len(values) != len(set(values)):
            raise ValueError(f"WORKFLOW.json {key} must be unique nonempty strings")
    if workflow["no_go_criteria"] != [f"NG{i}" for i in range(1, 8)]:
        raise ValueError("WORKFLOW.json must define NG1–NG7")
    return workflow


def stage_definitions(workflow, task):
    tasks = ("research", "coding") if task == "both" else (task,)
    return [stage for selected in tasks for stage in workflow["tracks"][selected]]


def new_record(workflow, task, unit_id):
    if not unit_id.strip():
        raise ValueError("unit_id must be nonempty text")
    record = {"schema_version": 1, "workflow_version": "1.0.0", "task": task,
              "unit_id": unit_id, "objective": "", "scope": "", "status": "pending"}
    record.update({key: [] for key in COLLECTIONS + NOTES})
    record["stages"] = [{"id": stage["id"], "status": "pending", "evidence_refs": [],
                         "dependency_ids": [], "reason": "", "reuse": None}
                        for stage in stage_definitions(workflow, task)]
    return record


class Validator:
    def __init__(self, workflow):
        self.workflow = workflow
        self.errors = []

    def error(self, path, message):
        self.errors.append(f"{path}: {message}")

    def text(self, value, path, nonempty=True):
        if not isinstance(value, str) or (nonempty and not value.strip()):
            self.error(path, "must be nonempty text" if nonempty else "must be text")
            return False
        return True

    def array(self, value, path):
        if not isinstance(value, list):
            self.error(path, "must be an array")
            return []
        return value

    def enum(self, value, choices, path):
        if not isinstance(value, str) or value not in choices:
            self.error(path, "must be one of " + ", ".join(choices))
            return False
        return True

    def rows(self, record, key):
        rows, index = [], {}
        for i, row in enumerate(self.array(record.get(key), key)):
            path = f"{key}[{i}]"
            if not isinstance(row, dict):
                self.error(path, "must be an object")
                continue
            rows.append((path, row))
            identity = row.get("id")
            if self.text(identity, path + ".id"):
                if identity in index:
                    self.error(path + ".id", "duplicate ID")
                else:
                    index[identity] = row
        return rows, index

    def refs(self, value, index, path, required=False):
        refs = self.array(value, path)
        if required and not refs:
            self.error(path, "requires at least one evidence reference")
        seen = set()
        for i, ref in enumerate(refs):
            if not self.text(ref, f"{path}[{i}]"):
                continue
            if ref in seen:
                self.error(path, f"duplicate reference: {ref}")
            seen.add(ref)
            if ref not in index:
                self.error(path, f"unresolved reference: {ref}")
        return seen

    def execution_link(self, value, path, required=False, evaluated=False):
        if value is None and not required:
            return
        if self.text(value, path):
            if value not in self.executions:
                self.error(path, f"unresolved execution: {value}")
            elif evaluated and self.executions[value].get("status") not in ("completed", "failed"):
                self.error(path, "evaluated check requires a completed or failed execution")

    def stage(self, path, row):
        status = row.get("status")
        self.enum(status, self.workflow["stage_statuses"], path + ".status")
        evidence_refs = self.refs(row.get("evidence_refs"), self.evidence, path + ".evidence_refs",
                                  status in ("complete", "reused"))
        dependencies = self.refs(row.get("dependency_ids"), self.dependencies, path + ".dependency_ids")
        self.text(row.get("reason"), path + ".reason", status in ("blocked", "not_applicable"))
        reuse = row.get("reuse")
        if reuse is None and status != "reused":
            return
        if not isinstance(reuse, dict):
            self.error(path + ".reuse", "must be an object for reused stages")
            return
        snapshot = reuse.get("dependency_identities")
        if snapshot is None and status != "reused":
            return
        if not isinstance(snapshot, dict):
            self.error(path + ".reuse.dependency_identities", "must be an object")
            return
        for key, identity in snapshot.items():
            self.text(identity, path + f".reuse.dependency_identities[{key!r}]")
        if status == "reused":
            required = set()
            for ref in evidence_refs & self.evidence.keys():
                declared = self.evidence[ref].get("dependency_ids")
                if isinstance(declared, list):
                    required.update(item for item in declared if isinstance(item, str))
            if not required <= dependencies:
                self.error(path + ".dependency_ids", "must include dependencies of reused evidence")
            if set(snapshot) != dependencies:
                self.error(path + ".reuse.dependency_identities", "must cover dependency_ids exactly")
            for key in dependencies & snapshot.keys() & self.dependencies.keys():
                if snapshot[key] != self.dependencies[key].get("identity"):
                    self.error(path + ".reuse.dependency_identities", f"stale identity: {key}")

    def claim(self, path, row):
        self.text(row.get("statement"), path + ".statement")
        self.text(row.get("scope"), path + ".scope")
        bases = self.array(row.get("basis"), path + ".basis")
        if not bases:
            self.error(path + ".basis", "requires at least one basis")
        seen = set()
        for basis in bases:
            if self.enum(basis, self.workflow["claim_bases"], path + ".basis"):
                if basis in seen:
                    self.error(path + ".basis", f"duplicate basis: {basis}")
                seen.add(basis)
        self.refs(row.get("evidence_refs"), self.evidence, path + ".evidence_refs",
                  bool(seen - OPEN_BASES))
        self.array(row.get("obligations"), path + ".obligations")
        if "strong_no_go" not in row:
            return
        no_go = row["strong_no_go"]
        if not isinstance(no_go, dict):
            self.error(path + ".strong_no_go", "must be an object")
            return
        self.enum(no_go.get("status"), ("candidate", "admitted"), path + ".strong_no_go.status")
        criteria = no_go.get("criteria")
        if not isinstance(criteria, dict):
            self.error(path + ".strong_no_go.criteria", "must be an object")
            return
        admitted = no_go.get("status") == "admitted"
        if admitted and set(criteria) != set(self.workflow["no_go_criteria"]):
            self.error(path + ".strong_no_go.criteria", "admitted no-go requires exactly NG1–NG7")
        for name, criterion in criteria.items():
            label = path + ".strong_no_go.criteria." + name
            self.enum(name, self.workflow["no_go_criteria"], label)
            if not isinstance(criterion, dict):
                self.error(label, "must be an object")
                continue
            self.enum(criterion.get("status"), ("met", "open"), label + ".status")
            if admitted and criterion.get("status") != "met":
                self.error(label, "admitted no-go requires status met")
            self.refs(criterion.get("evidence_refs"), self.evidence, label + ".evidence_refs",
                      admitted or criterion.get("status") == "met")

    def execution(self, path, row):
        status = row.get("status")
        self.enum(status, self.workflow["execution_statuses"], path + ".status")
        actual = status in ("running", "completed", "failed")
        command = row.get("command")
        if isinstance(command, list):
            if actual and not command:
                self.error(path + ".command", "actual execution requires a command")
            for i, part in enumerate(command):
                self.text(part, f"{path}.command[{i}]")
        else:
            self.text(command, path + ".command", actual)
        environment = row.get("environment")
        if isinstance(environment, dict):
            if actual and not environment:
                self.error(path + ".environment", "actual execution requires environment details")
        else:
            self.text(environment, path + ".environment", actual)
        self.refs(row.get("evidence_refs"), self.evidence, path + ".evidence_refs",
                  status in ("completed", "failed"))
        code = row.get("exit_code")
        if code is not None and type(code) is not int:
            self.error(path + ".exit_code", "must be an integer or null")
        if status == "completed" and (type(code) is not int or code != 0):
            self.error(path + ".exit_code", "completed execution requires integer exit code 0")
        self.text(row.get("reason"), path + ".reason", status in ("failed", "blocked"))

    def validate(self, record):
        if not isinstance(record, dict):
            return ["record: must be an object"]
        if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
            self.error("schema_version", "must be integer 1")
        if record.get("workflow_version") != "1.0.0":
            self.error("workflow_version", "must be 1.0.0")
        task = record.get("task")
        valid_task = self.enum(task, ("research", "coding", "both"), "task")
        self.enum(record.get("status"), self.workflow["task_statuses"], "status")
        self.text(record.get("unit_id"), "unit_id")
        for key in ("objective", "scope"):
            self.text(record.get(key), key, record.get("status") == "complete")
        rows, indices = {}, {}
        for key in COLLECTIONS:
            rows[key], indices[key] = self.rows(record, key)
        self.dependencies, self.evidence, self.executions = (indices[key] for key in ("dependencies", "evidence", "executions"))
        if valid_task and [row.get("id") for _, row in rows["stages"]] != [stage["id"] for stage in stage_definitions(self.workflow, task)]:
            self.error("stages", "must contain the exact ordered stages for task " + task)
        for path, row in rows["dependencies"]:
            self.text(row.get("identity"), path + ".identity")
            self.text(row.get("description"), path + ".description", False)
        for path, row in rows["evidence"]:
            self.enum(row.get("kind"), self.workflow["evidence_kinds"], path + ".kind")
            for key in ("locator", "scope"):
                self.text(row.get(key), path + "." + key)
            self.refs(row.get("dependency_ids"), self.dependencies, path + ".dependency_ids")
        for key, handler in (("stages", self.stage), ("claims", self.claim), ("executions", self.execution)):
            for path, row in rows[key]:
                handler(path, row)
        for path, row in rows["checks"]:
            result = row.get("result")
            self.enum(row.get("domain"), self.workflow["check_domains"], path + ".domain")
            self.enum(result, self.workflow["check_results"], path + ".result")
            evaluated = isinstance(result, str) and result in EVALUATED
            self.refs(row.get("evidence_refs"), self.evidence, path + ".evidence_refs", evaluated)
            self.text(row.get("reason"), path + ".reason", result in ("blocked", "not_applicable"))
            self.execution_link(row.get("execution_ref"), path + ".execution_ref",
                                evaluated and row.get("domain") in ("numerics", "implementation"), evaluated)
        for key in NOTES:
            seen = set()
            for i, row in enumerate(self.array(record.get(key), key)):
                path = f"{key}[{i}]"
                if not isinstance(row, dict):
                    if key == "failures":
                        self.error(path, "must be an object")
                    continue
                if "id" in row and self.text(row["id"], path + ".id"):
                    if row["id"] in seen:
                        self.error(path + ".id", "duplicate ID")
                    seen.add(row["id"])
                if "evidence_refs" in row or key == "failures":
                    self.refs(row.get("evidence_refs"), self.evidence, path + ".evidence_refs", key == "failures")
                if "dependency_ids" in row:
                    self.refs(row["dependency_ids"], self.dependencies, path + ".dependency_ids")
                if "execution_ref" in row:
                    self.execution_link(row["execution_ref"], path + ".execution_ref")
                if key == "failures":
                    self.enum(row.get("class"), self.workflow["failure_classes"], path + ".class")
                    self.text(row.get("next_action"), path + ".next_action", False)
        if record.get("status") == "complete" and any(row.get("status") not in tuple(CLOSED) for _, row in rows["stages"]):
            self.error("status", "complete record requires every stage complete, reused, or not_applicable")
        return self.errors


def emit(status, path, errors=()):
    print(json.dumps({"status": status, "path": str(path),
                      "validation_scope": "structure_and_references",
                      "scientific_validity": "not_assessed", "errors": list(errors)}, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="action", required=True)
    create = commands.add_parser("init", help="create a pending record without overwriting")
    create.add_argument("--task", choices=("research", "coding", "both"), required=True)
    create.add_argument("--unit-id", required=True)
    create.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check", help="check structure and internal references")
    check.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    path = args.output if args.action == "init" else args.path
    try:
        workflow = load_workflow()
        if args.action == "init":
            payload = json.dumps(new_record(workflow, args.task, args.unit_id), ensure_ascii=False, indent=2) + "\n"
            with path.open("x", encoding="utf-8") as stream:
                stream.write(payload)
            emit("created", path)
            return 0
        errors = Validator(workflow).validate(read_json(path))
        emit("invalid" if errors else "valid", path, errors)
        return 1 if errors else 0
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        emit("error", path, [str(exc)])
        return 2


if __name__ == "__main__":
    sys.exit(main())
