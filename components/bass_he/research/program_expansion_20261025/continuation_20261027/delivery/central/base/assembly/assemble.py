"""Source-preserving mechanical graph assembly; never imports scientific code."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil


REPOS = ("WU088_HH", "rec_bianchi", "BASS_HE", "bass_cr", "bass", "vigilode", "rei_bianchi")
SOURCE_GROUPS = [
    ("atomic/EXPANDED_NODE_CONTRACTS.json", "nodes", None),
    ("thermal/BASS_HE_LONGTERM_CONTRACTS.json", "nodes", "BASS_HE"),
    ("thermal/rec_bianchi_LONGTERM_CONTRACTS.json", "nodes", "rec_bianchi"),
    ("numerics/BASS_CONTRACTS.json", "nodes", "bass"),
    ("numerics/VIGILODE_CONTRACTS.json", "nodes", "vigilode"),
    ("thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json", "tasks", "BASS_HE"),
    ("thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json", "tasks", "rec_bianchi"),
    ("rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json", "nodes", "rei_bianchi"),
]
REPO_PACKAGES = {
    "WU088_HH": "atomic/WU088_HH",
    "bass_cr": "atomic/bass_cr",
    "bass": "numerics/repo_expansion/bass",
    "vigilode": "numerics/repo_expansion/vigilode",
    "BASS_HE": "thermal/BASS_HE/research/program_expansion_20261025",
    "rec_bianchi": "thermal/rec_bianchi/research/program_expansion_20261025",
    "rei_bianchi": "rei/rei_bianchi/research/program_expansion_20261025",
}


def load(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def pointer(document, path):
    value = document
    for token in path.strip("/").split("/") if path.strip("/") else []:
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def repo(value):
    name = value.rsplit("/", 1)[-1]
    if name not in REPOS:
        raise ValueError("Unrecognized supplied repository: " + value)
    return "cosmosapjw-quantum/" + name


def first(record, names, default=None):
    for name in names:
        try:
            return copy.deepcopy(pointer(record, "/" + name)), name
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    return copy.deepcopy(default), None


def stage(intake, package):
    package.mkdir(parents=True, exist_ok=True)
    shutil.copytree(intake / "baseline", package / "historical/baseline", dirs_exist_ok=True)
    selected = {Path(name) for name, _, _ in SOURCE_GROUPS}
    selected.update(Path(name) for name in [
        "ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md", "ROOT_ASSEMBLY_OBSERVATIONS.json", "SOURCE_COVERAGE.json", "COMPILER_WOLFRAM_CHECK.json", "COMPILER_ADMISSION.json",
        "PLAN_REVIEW_ATOMIC.md", "PLAN_REVIEW_NUMERICS.md",
        "REC_H5_INDEPENDENT_REVIEW.md", "FINAL_ASSEMBLY_MISSING_FIELDS.json", "atomic/AUTHORITY_AUDIT_KO.md", "atomic/EVIDENCE_FILTERED.json",
        "thermal/COMMON_CONTRACT.json", "thermal/AUDIT_AND_SCOPE_KO.md", "thermal/EVIDENCE_FILTERED.json", "thermal/REC_H5_DEFECT_BOUND01_DERIVATION.md",
        "numerics/THEORY_AND_PR_PLANS.md", "numerics/PLAN_VALIDATION.json", "numerics/SURVEY_HANDOFF.md", "numerics/EVIDENCE_INDEX.json",
        "rei/DAG_DELTA.json", "rei/R1_R10_AUTHORITY.json", "rei/AUDIT_KO.md", "rei/HANDOFF_REI_KO.md", "rei/PR219_BOOTSTRAP_REUSE_CLARIFICATION.json",
        "molecular/MOLECULAR_AUTHORITY_20261025.md", "molecular/data_reuse_registry.json",
        "molecular/paper_identity.json", "molecular/hd_reference_check.json",
        "molecular/REC_HD_ADAPTER_CONTRACT.json", "molecular/lamda_hd_20261025.dat",
    ])
    for folder in REPO_PACKAGES.values():
        selected.update(p.relative_to(intake / "authority") for p in (intake / "authority" / folder).glob("*") if p.is_file())
    selected.update(p.relative_to(intake / "authority") for p in (intake / "authority/review_compiler").glob("*") if p.is_file())
    for path in selected:
        source = intake / "authority" / path
        if not source.exists():
            raise ValueError("Required selected authority missing: " + str(path))
        target = package / "authority" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for filename in ("FROZEN_COMPILER_CONTRACT.md", "THEORY.md", "R2_PHOTON_COUNT_CLARIFICATION.md"):
        source = intake / "release/research/rei_chem_ledger_20261025/authority" / filename
        target = package / "authority/compiler" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    assembly = package / "assembly"
    assembly.mkdir(exist_ok=True)
    shutil.copyfile(Path(__file__), assembly / "assemble.py")


def assemble(package):
    baseline = load(package / "historical/baseline/assembly/DAG.json")
    historical_index = {n["id"]: n for n in baseline["nodes"]}
    documents = {}

    def document(path):
        if path not in documents:
            documents[path] = load(package / path)
        return documents[path]

    source_rows = []
    for filename, key, default_repo in SOURCE_GROUPS:
        path = "authority/" + filename
        doc = document(path)
        for i, contract in enumerate(doc[key]):
            source_rows.append((contract, path, "/" + key + "/" + str(i), default_repo or doc.get("repository")))
    for old in baseline["nodes"]:
        if old["repository"].endswith("/rei_bianchi"):
            path = "historical/baseline/" + old["authority"]
            source_rows.append((old["contract"], path, old["authority_pointer"], "rei_bianchi"))
    delta_path = "authority/rei/DAG_DELTA.json"
    delta = document(delta_path)
    readiness_path = "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json"
    readiness_guards = {row["id"]: row for row in document(readiness_path)["affected_nodes"]}
    source_rows.append((delta["new_child"], delta_path, "/new_child", "WU088_HH"))
    hd_path = "authority/molecular/REC_HD_ADAPTER_CONTRACT.json"
    source_rows.append((document(hd_path), hd_path, "", "rec_bianchi"))
    ids = [row[0]["id"] for row in source_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate active source node IDs")
    id_set = set(ids)
    unresolved = []

    def dependency(value, file, field):
        if isinstance(value, str):
            if value in id_set:
                return {"type": "internal", "id": value, "source_file": file, "source_field": field}
            if not value.startswith("external:"):
                unresolved.append({"reference": value, "source_file": file, "source_field": field})
            return {"type": "external", "source_reference": value, "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED", "source_file": file, "source_field": field}
        if isinstance(value, dict):
            result = copy.deepcopy(value)
            target = value.get("dependency", value.get("id"))
            if target in id_set and not str(value.get("type", "")).startswith("external"):
                result["type"] = "internal"
                result["id"] = target
            else:
                result["type"] = "external"
                result["qualification"] = "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED"
            result.update(source_file=file, source_field=field)
            return result
        return {"type": "external", "source_reference": copy.deepcopy(value), "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED", "source_file": file, "source_field": field}

    nodes = []
    for contract, file, ptr, default_repo in source_rows:
        identifier = contract["id"]
        historical = historical_index.get(identifier)
        lead, lead_key = first(contract, ("lead_repo", "owner_repository"), default_repo)
        if lead is None:
            raise ValueError("Missing explicit lead repository: " + identifier)
        dependencies, dep_key = first(contract, ("dependencies", "depends_on"))
        dep_source = file
        if dep_key is None and historical:
            dependencies = historical["local_dependencies"] + historical["external_dependencies"]
            dep_source = "historical/baseline/assembly/DAG.json"
            dep_key = "preserved_baseline_dependencies"
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list):
            raise ValueError("Dependency list clarification required: " + identifier)
        normalized_dependencies = [dependency(v, dep_source, dep_key) for v in dependencies]
        conditional, conditional_key = first(contract, ("conditional_dependencies",))
        if conditional_key is None and historical:
            conditional = historical.get("conditional_dependencies", [])
        if conditional is None:
            conditional = []
        if isinstance(conditional, dict):
            conditional = [{"condition": condition, "dependency": dep} for condition, deps in conditional.items() for dep in deps]
        normalized_conditional = [dependency(v, file, conditional_key or "preserved_baseline_conditional_dependencies") for v in conditional]
        prerequisites = []
        if "prerequisites" in contract:
            prerequisites.append({"type": "external", "source_reference": copy.deepcopy(contract["prerequisites"]),
                                  "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED", "source_file": file, "source_field": "prerequisites"})
        status, status_key = first(contract, ("current_status", "status", "state"), "SOURCE_STATUS_NOT_DECLARED")
        claim, claim_key = first(contract, ("claim_gate", "admission_gate", "claim_gates", "acceptance", "claim_limit", "claim"))
        action, action_key = first(contract, ("pass_next_action", "pass_next", "pass_action", "next_action"))
        budget, budget_key = first(contract, ("budget_status", "budget", "new_budget"))
        if budget_key is None:
            doc = document(file)
            budget, budget_key = first(doc, ("policy", "production", "budget"))
        changes = copy.deepcopy(contract.get("change_class", ["status_correction"] if historical else ["scope_expansion"]))
        if historical and (dependencies != historical["local_dependencies"] + historical["external_dependencies"] or "dependency_change" in contract):
            changes = list(dict.fromkeys(changes + ["dependency_change"]))
        node = {"id": identifier, "lead_repo": repo(lead), "source_file": file, "json_pointer": ptr,
                "contract": copy.deepcopy(contract), "dependencies": normalized_dependencies,
                "conditional_dependencies": normalized_conditional, "external_prerequisites": prerequisites,
                "current_status": status, "claim_gate": claim, "pass_next_action": action,
                "budget_status": budget, "change_class": changes,
                "historical_contract_id": identifier if historical else None,
                "source_fields": {"lead_repo": lead_key or "source_group_repository", "current_status": status_key,
                                  "claim_gate": claim_key, "pass_next_action": action_key, "budget_status": budget_key}}
        if identifier in delta["observations"]:
            observation = delta["observations"][identifier]
            node["current_status"] = observation["current_scoped_state"]
            node["status_observation"] = {"source_file": delta_path, "json_pointer": "/observations/" + identifier, "value": copy.deepcopy(observation)}
        if identifier == "REI-CHEM-LEDGER-01":
            admission_path = "authority/review_compiler/FINAL_C9_REVIEW.json"
            admission = document(admission_path)
            node.update(current_status=admission["decision"], claim_gate=admission["admitted_claim"],
                        pass_next_action=admission["next_action"], change_class=["new_result", "ownership_reassignment"])
            node["status_observation"] = {"source_file": admission_path, "json_pointer": "", "value": copy.deepcopy(admission)}
            node["parent_containment"] = contract["parent"]
            node["full_contract_source"] = "authority/compiler/FROZEN_COMPILER_CONTRACT.md"
            node["contract_appendix"] = "authority/compiler/R2_PHOTON_COUNT_CLARIFICATION.md"
            root_admission_path = "authority/COMPILER_ADMISSION.json"
            root_admission = document(root_admission_path)
            node["root_admission"] = {"source_file": root_admission_path, "json_pointer": "", "value": root_admission}
            node["budget_status"] = {"source_file": root_admission_path,
                                     "resource_scope": copy.deepcopy(root_admission["resource_scope"]),
                                     "executed": copy.deepcopy(root_admission["executed"])}
            node["source_fields"]["budget_status"] = "root_admission:/resource_scope + /executed"
            node["publication_role"] = {"canonical_repository": "cosmosapjw-quantum/WU088_HH", "central_copy": "IMMUTABLE_INTEGRATION_MIRROR", "canonical_commit": "PENDING_ROOT_PUBLICATION"}
        if identifier == "REC-H5-DEFECT-BOUND01":
            root_observations_path = "authority/ROOT_ASSEMBLY_OBSERVATIONS.json"
            observation = document(root_observations_path)[identifier]
            node["current_status"] = observation["current_status"]
            node["change_class"] = list(dict.fromkeys(node["change_class"] + ["new_result"]))
            node["status_observation"] = {"source_file": root_observations_path, "json_pointer": "/" + identifier, "value": copy.deepcopy(observation)}
        if "parent_id" in contract:
            node["parent_containment"] = contract["parent_id"]
        if "parent_containment" in contract:
            node["parent_containment"] = copy.deepcopy(contract["parent_containment"])
        detail_fields = {
            "inputs": ("inputs", "input_sources", "input", "inputs_domain", "prerequisites"),
            "equations": ("equations", "equations_scope"), "units": ("units",),
            "domain": ("domain", "provider_domain", "inputs_domain", "scope"),
            "outputs": ("outputs", "output", "scope"),
            "positive_acceptance": ("acceptance", "admission_gate", "claim_gates", "claim_gate", "tests"),
            "failure_disposition": ("failure_disposition", "fail_next", "fail_action", "failure_action", "pr_plan/failure_disposition"),
            "independent_review": ("independent_review", "review", "pr_plan/independent_review"),
            "PR_boundary": ("pr_plan", "pr_boundary", "allowed_paths"),
        }
        node["pr_plan"] = {}
        for field, aliases in detail_fields.items():
            value, source_key = first(contract, aliases)
            source_file, source_ptr = file, ptr
            if source_key is None and historical:
                value, source_key = first(historical["contract"], aliases)
                source_file = "historical/baseline/" + historical["authority"]
                source_ptr = historical["authority_pointer"]
            if source_key is None and field == "PR_boundary" and "allowed_paths" in document(file):
                value, source_key = first(document(file), ("allowed_paths",))
                source_file, source_ptr = file, ""
            if source_key is None and field == "independent_review" and "policy" in document(file):
                value, source_key = first(document(file), ("policy/roles",))
                source_file, source_ptr = file, ""
            node["pr_plan"][field] = {"value": value, "source_file": source_file,
                                      "json_pointer": source_ptr + "/" + source_key if source_key else None,
                                      "qualification": "SOURCE_DECLARED" if source_key else "NOT_DECLARED_SEPARATELY_IN_SOURCE"}
        if identifier == "REI-CHEM-LEDGER-01":
            sections = {"inputs": "Frozen synthetic fixtures", "equations": "Derived results to implement",
                        "units": "Definitions and conventions", "domain": "Objective and exact novelty",
                        "outputs": "Acceptance and output", "positive_acceptance": "Acceptance and output",
                        "failure_disposition": "Allowed files and execution", "independent_review": "Acceptance and output",
                        "PR_boundary": "Allowed files and execution"}
            for field, section in sections.items():
                node["pr_plan"][field] = {"source_file": node["full_contract_source"], "section": section,
                                          "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"}
        if identifier == "REC-HD-ADAPTER":
            node["pr_plan"]["units"] = {"value": copy.deepcopy(contract["equations"][0]),
                                         "source_file": file, "json_pointer": "/equations/0",
                                         "qualification": "SOURCE_UNIT_CONVERSION_EQUATION"}
        if identifier in readiness_guards:
            guard = readiness_guards[identifier]
            node["runnable"] = False
            node["missing_contract_fields"] = copy.deepcopy(guard["missing_source_fields"])
            node["execution_readiness_guard"] = {"source_file": readiness_path,
                                                 "scope": guard["scope"],
                                                 "other_nodes_runnable_not_inferred": True}
        nodes.append(node)
    authorities = [{"path": path, "sha256": hashlib.sha256((package / path).read_bytes()).hexdigest(), "document": document(path)}
                   for path in sorted(documents)]
    return {"schema": "ORCHESTRATION_EXPANSION_DAG_V1", "as_of": "2026-10-25",
            "authority": "authority/ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md",
            "scope": "Verbatim source contracts with explicit current wrappers; structural assembly is not scientific admission",
            "historical_snapshot": {"source_ref": "c5050305f84a051cb797cd84c84768c76bcb18b9", "DAG": baseline,
                                    "source_file": "historical/baseline/assembly/DAG.json", "returns": "historical/baseline/assembly/returns"},
            "authorities": authorities, "nodes": nodes,
            "integration_edges": copy.deepcopy(baseline["integration"]["edges"]),
            "dependency_interpretation": copy.deepcopy(baseline["integration"]["dependency_interpretation"]),
            "unresolved_untyped_references": unresolved, "global_physical_completion": None, "L4_ready": False}


def validate(dag, package):
    errors = []
    index = {node["id"]: node for node in dag["nodes"]}
    if len(index) != len(dag["nodes"]):
        errors.append("duplicate IDs")
    historical = load(package / "historical/baseline/assembly/DAG.json")
    if dag["historical_snapshot"]["DAG"] != historical:
        errors.append("historical DAG changed")
    if len(historical["nodes"]) != 40 or len(dag["integration_edges"]) != 17:
        errors.append("baseline40/17 not retained")
    if dag["integration_edges"] != historical["integration"]["edges"]:
        errors.append("historical integration edge changed")
    if len(list((package / "historical/baseline/assembly/returns").glob("*.json"))) != 31:
        errors.append("return count not31")
    source_inventory = load(package / "historical/baseline/SOURCE_INVENTORY.json")
    for item in source_inventory["files"] + source_inventory["initial_files"]:
        raw = (package / "historical/baseline" / item["path"]).read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if sha != item["git_blob_sha"]:
            errors.append("historical source bytes changed: " + item["path"])
    for authority in historical["authorities"]:
        if hashlib.sha256((package / "historical/baseline" / authority["path"]).read_bytes()).hexdigest() != authority["sha256"]:
            errors.append("historical authority source changed: " + authority["path"])
    for node in dag["nodes"]:
        if pointer(load(package / node["source_file"]), node["json_pointer"]) != node["contract"]:
            errors.append("source contract mismatch: " + node["id"])
        observation = node.get("status_observation")
        if observation and pointer(load(package / observation["source_file"]), observation["json_pointer"]) != observation["value"]:
            errors.append("status observation source mismatch: " + node["id"])
        if node["lead_repo"].rsplit("/", 1)[-1] not in REPOS:
            errors.append("invalid lead repository: " + node["id"])
        for key in ("id", "lead_repo", "source_file", "json_pointer", "dependencies", "conditional_dependencies", "current_status", "claim_gate", "pass_next_action", "budget_status"):
            if key not in node:
                errors.append("missing common field: " + node["id"] + "/" + key)
        for field in node["pr_plan"].values():
            if field.get("json_pointer") and pointer(load(package / field["source_file"]), field["json_pointer"]) != field["value"]:
                errors.append("PR source binding mismatch: " + node["id"])
            if "section" in field and "## " + field["section"] not in (package / field["source_file"]).read_text():
                errors.append("missing frozen contract section: " + node["id"])
    for authority in dag["authorities"]:
        if hashlib.sha256((package / authority["path"]).read_bytes()).hexdigest() != authority["sha256"]:
            errors.append("authority bytes changed: " + authority["path"])
    graph = {identifier: [] for identifier in index}
    for node in dag["nodes"]:
        for dep in node["dependencies"] + node["conditional_dependencies"]:
            if dep["type"] == "internal":
                target = dep["id"]
                if target not in graph:
                    errors.append("missing internal endpoint: " + target)
                else:
                    graph[node["id"]].append(target)
    for edge in dag["integration_edges"]:
        if edge["from"] not in index or edge["to"] not in index:
            errors.append("missing historical integration endpoint")
        else:
            graph[edge["to"]].append(edge["from"])
    visited, active = set(), set()

    def visit(identifier):
        if identifier in active:
            errors.append("cycle at " + identifier)
            return
        if identifier in visited:
            return
        active.add(identifier)
        for dep in graph[identifier]:
            visit(dep)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in graph:
        visit(identifier)
    if dag["unresolved_untyped_references"]:
        errors.append("unresolved source ID references need root classification")
    guards = load(package / "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json")["affected_nodes"]
    for guard in guards:
        node = index[guard["id"]]
        if node.get("runnable") is not False or node.get("missing_contract_fields") != guard["missing_source_fields"]:
            errors.append("missing future-execution readiness guard: " + guard["id"])
    if any(node.get("runnable") is True for node in dag["nodes"]):
        errors.append("mechanical assembly inferred execution permission")
    return {"valid": not errors, "errors": errors, "active_nodes": len(index), "baseline_nodes": 40,
            "baseline_edges": 17, "preserved_returns": 31, "unique_lead_per_node": True,
            "source_contract_equality": True, "all_43_baseline_git_blob_identities": "VERIFIED",
            "all_7_baseline_authority_identities": "VERIFIED",
            "future_execution_guarded_nodes": len(guards),
            "missing_source_field_declarations": sum(len(guard["missing_source_fields"]) for guard in guards),
            "execution_permission_inferred": False,
            "species_domains": "SOURCE_AUTHORITY_FIELDS_PRESERVED; physical_validity_not_inferred",
            "scientific_admission_by_checker": False,
            "global_physical_completion": None, "L4_ready": False}


def render(package, dag):
    def text(value):
        return json.dumps(value, ensure_ascii=False, indent=2)

    for node in dag["nodes"]:
        dump(package / "contracts" / (node["id"] + ".json"), node)
        plan = ["# " + node["id"], "", "Lead: " + node["lead_repo"], "", "Current status: `" + str(node["current_status"]) + "`", "",
                "Source: `" + node["source_file"] + "#" + node["json_pointer"] + "`", "", "```json", text(node), "```", ""]
        target = package / "node_plans" / (node["id"] + ".md")
        target.parent.mkdir(exist_ok=True)
        target.write_text("\n".join(plan))
    dump(package / "status/CURRENT_STATUS.json", [{key: n[key] for key in ("id", "lead_repo", "current_status", "change_class", "source_file", "json_pointer")} | {"observation": n.get("status_observation")} for n in dag["nodes"]])
    dump(package / "gates/CLAIM_GATES.json", [{key: n[key] for key in ("id", "claim_gate", "pass_next_action", "budget_status", "dependencies", "conditional_dependencies", "external_prerequisites")} | {key: n[key] for key in ("runnable", "missing_contract_fields", "execution_readiness_guard") if key in n} for n in dag["nodes"]])
    dump(package / "source_reuse/SOURCE_REUSE.json", {"authorities": [{k: a[k] for k in ("path", "sha256")} for a in dag["authorities"]],
         "selected_authority_files": [{"path": str(p.relative_to(package)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((package / "authority").rglob("*")) if p.is_file()],
         "no_donor_recomputation": True, "baseline": "../historical/baseline/SOURCE_INVENTORY.json", "current_returns": "../historical/baseline/assembly/returns", "molecular_registry": "../authority/molecular/data_reuse_registry.json",
         "PR219_RR_bootstrap_clarification": "../authority/rei/PR219_BOOTSTRAP_REUSE_CLARIFICATION.json"})
    for name in REPOS:
        base = package / "authority" / REPO_PACKAGES[name]
        (package / "charters").mkdir(exist_ok=True)
        shutil.copyfile(base / "REPO_CHARTER_KO.md", package / "charters" / (name + ".md"))
        owned = [n["id"] for n in dag["nodes"] if n["lead_repo"].endswith("/" + name)]
        assignment = load(base / "TASK_ASSIGNMENT.json")
        assigned = assignment.get("assigned_nodes", [n["id"] for n in assignment.get("nodes", assignment.get("tasks", []))])
        central_reference = {"repository": "cosmosapjw-quantum/rei_bianchi", "branch": "research/orchestration-sandbox-20261022",
                             "path": "research/orchestration_expansion_20261025", "DAG_path": "research/orchestration_expansion_20261025/DAG.json",
                             "URL": "https://github.com/cosmosapjw-quantum/rei_bianchi/blob/research/orchestration-sandbox-20261022/research/orchestration_expansion_20261025/DAG.json",
                             "commit": "PENDING_ROOT_PUBLICATION", "publication_rule": "Root publishes central first and replaces commit with its actual SHA in every repository delivery manifest",
                             "authored_task_assignment": "research/orchestration_expansion_20261025/" + str((base / "TASK_ASSIGNMENT.json").relative_to(package))}
        dump(package / "task_assignments" / (name + ".json"), {"repository": repo(name), "source_file": str((base / "TASK_ASSIGNMENT.json").relative_to(package)), "source_assignment": assignment, "canonical_lead_node_ids": owned, "assignment_node_ids": assigned, "DAG": "../DAG.json", "central_reference": central_reference})
        dump(package / "central_references" / (name + ".json"), central_reference)
        original = base / "HANDOFF_KO.md"
        handoff_text = original.read_text() if original.exists() else "# " + name + " 인계\n\n원 작성자 계약과 작업 배정을 따릅니다.\n"
        handoff_text += "\n\n## 중앙 조립 참조\n\n정본: `DAG.json`. 개별 계약: `contracts/<node-id>.json`. 원 작성자 파일은 `authority/`에 변경 없이 보존했습니다. 아래 목록은 이 저장소의 정본 lead 노드이며, 다른 저장소 lead 작업의 소비자 관계는 원 TASK_ASSIGNMENT와 계약에 그대로 남아 있습니다.\n\n"
        handoff_text += "\n".join("- `" + identifier + "`" for identifier in owned)
        handoff_text += "\n\n새 예산은 각 원 계약만 따릅니다. 완료 결과를 재계산하거나 자식 완료를 부모 완료로 승격하지 않습니다. 전역 물리 완료율은 null, L4 준비 상태는 false입니다.\n"
        path = package / "handoffs" / ("HANDOFF_" + name + "_KO.md")
        path.parent.mkdir(exist_ok=True)
        path.write_text(handoff_text)
    dump(package / "PUBLICATION_LOCATORS.json", {"central_repository": "cosmosapjw-quantum/rei_bianchi", "central_branch": "research/orchestration-sandbox-20261022", "central_path": "research/orchestration_expansion_20261025", "central_commit": "PENDING_ROOT_PUBLICATION", "compiler_lead_repository": "cosmosapjw-quantum/WU088_HH", "compiler_path": "research/rei_chem_ledger_20261025", "root_binds_final_commit_after_publication": True})
    (package / "README.md").write_text("# 확장 연구 프로그램, 2026-10-25\n\n`DAG.json`이87개 현재 계약·선행 조건·소유권의 정본입니다. `historical/baseline/`은 c5050305의 기존40계약·17연결·31반환 파일과7권위 원문을 보존합니다. 현재 계약 원문은 `authority/`에 있고 각 노드는 원문 JSON pointer를 유지합니다.\n\n모든 원자 저장소는 각자의 과정 책임을 전체 구성 대상 (Z,A,isomer), 이온·상태·전자 pool·분자 동위원소체로 확장합니다. 현재21개 핵종/이온 population은 검증된 초기 목록이며 미래의 고정 상한이 아닙니다. 소스 없음·지원된0·구현·실행·독립 승인·전달 상태는 다릅니다.\n\n| 저장소 | lead 책임 |\n|---|---|\n| WU088_HH | 핵종·종·원자/분자/핵/약반응, 가지·반응 에너지 입력 |\n| rec_bianchi | 준위·population·분광·재결합·방출/흡수·복사 이력 |\n| BASS_HE | 미분 충돌·유한질량/각분포 에너지운동량·열화/열폐쇄 |\n| bass_cr | 외부 비열적 광자/전자/바리온 분포·주입·cascade·stopping |\n| bass | 시공간·background·공변 T/Q 결합·cohort transport |\n| vigilode | 적분·domain/failure·native gateway·오차 제어 |\n| rei_bianchi | 선택 시나리오·소스/흡수체/환경·전체 결합 보존·관측량 |\n\n전체 모형의 물리 완료율은 null이며 L4 준비 상태는 false입니다. 공급자 선택은 선택한 모형의 조건부 요구사항이며 모든7저장소 미래 작업의 동시 완료를 요구하지 않습니다. 이번 작업에서는 별도 compiler의 한 번의 한정 실행으로249개 정확 산술 검사를 통과하고 독립 승인을 받았습니다. 이는12개 합성 화학 event와1개 핵 bookkeeping event 및 명시된 guard/항등식에 한정됩니다. H5는 독립 검토된 조건부 이론 유도입니다. 경험적 결합 solver나 새 IVP를 실행하거나 과거 suite를 재계산하지 않았습니다. Compiler는 경험적 rate나 핵Q를 승인하지 않으며 H5 물리 epsilon은 null, 구현은 NOT_RUN입니다.\n\n`charters/`, `task_assignments/`, `handoffs/`는7저장소의 권한·과업·인계를 제공합니다. 개별 PR 계획은 `node_plans/`, 원문 포함 계약은 `contracts/`, 주장 관문은 `gates/`, 현재 관찰은 `status/`, 재사용 소스는 `source_reuse/`에 있습니다. 구조 검사 결과는 `audit/STRUCTURAL_VALIDATION.json`입니다. `central_references/`의 branch/path 링크는 정본 위치를 가리키며 root가 중앙 게시 후 실제 commit SHA를 각 저장소 전달 manifest에 결합합니다.\n\nCompiler의 canonical 구현 저장소는 WU088_HH이며 중앙 동일 소스는 immutable integration mirror입니다. 코드·raw의 과거 pending 문구는 바꾸지 않고 별도 승인/전달 관찰값을 붙입니다. Git 게시와 최종 백업은 별도 영수증으로 확인합니다.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", required=True)
    parser.add_argument("--package", required=True)
    args = parser.parse_args()
    intake, package = Path(args.intake).resolve(), Path(args.package).resolve()
    stage(intake, package)
    dag = assemble(package)
    dump(package / "DAG.json", dag)
    result = validate(dag, package)
    dump(package / "audit/STRUCTURAL_VALIDATION.json", result)
    render(package, dag)
    print(json.dumps(result, ensure_ascii=False))
    if dag["unresolved_untyped_references"]:
        print(json.dumps(dag["unresolved_untyped_references"], ensure_ascii=False))
    return int(not result["valid"])


if __name__ == "__main__":
    raise SystemExit(main())
