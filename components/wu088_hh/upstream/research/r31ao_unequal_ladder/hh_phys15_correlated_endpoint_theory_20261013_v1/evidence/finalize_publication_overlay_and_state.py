#!/usr/bin/env python3
"""Finalize the reviewed PHYS15 entry overlay and create its open R9/R10 record.

This is a one-time local metadata operation. It does not run a physical model,
solve a root, replay a scientific history, or publish to a remote provider.
"""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time

BASE = Path("/workspace/scratch/b826cbaab54f")
CORE = BASE / "HH_PHYS15_THEORY_20261012_v1"
OLD = BASE / "HH_PHYS14_20261012_v1/publication_overlay"
OVERLAY = CORE / "publication_overlay"
SKILL = Path("/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d")
GITCORE = "research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1"
PARENT = "087a16f28d0ee4fc7ae74ae50bfcafe578716e85"
TREE = "61a4dc1ed1bf42530ed8fda9596a91962e9912e7"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def readj(path):
    return json.loads(path.read_text(encoding="utf-8"))


def payload(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


decision_path = CORE / "review/DECISION.json"
decision = readj(decision_path)
decision_sha = sha(decision_path.read_bytes())
assert decision["decision"] == "PROMOTE_SCOPED"
assert not decision["remaining_blocking_findings"]
assert len(decision["claim_decisions"]) == 9
assert decision_sha == "8addd12246ded9a540ecfb85b98651013f8c55e6a0c72840166546e686da3c44"
theory_sha = sha((CORE / "theory/CORRELATED_ENDPOINT_THEORY_KO.md").read_bytes())
photon_sha = sha((CORE / "theory/PHOTON_DEFECT_THEOREM_KO.md").read_bytes())
assert theory_sha == "60c9d5e52df1fa43e317c2043598e0d44ed89854c79dad4bed474aa4f200ef61"
assert photon_sha == "252908a82fef7c9975d442182d487163ee8cf84257eaacc6b7c8a306937c4de2"
assert (CORE / "contracts/ENDPOINT_ENCLOSURE_CONTRACT.json").is_file()
assert not (CORE / "ROOT_OVERLAY_FINAL.json").exists()
assert not (CORE / "state/RESEARCH_STATE.json").exists()

draft_receipt = readj(CORE / "evidence/ROOT_OVERLAY_DRAFT.json")
draft_by_path = {row["path"]: row for row in draft_receipt["files"]}
files = list(draft_by_path)
original_bytes = {rel: (OLD / rel).read_bytes() for rel in files}
draft_bytes = {rel: (OVERLAY / rel).read_bytes() for rel in files}
for rel in files:
    assert sha(original_bytes[rel]) == draft_by_path[rel]["source_sha256"]
    assert sha(draft_bytes[rel]) == draft_by_path[rel]["draft_sha256"]

status_text = (
    "Independent review accepted nine scoped theoretical claims as PROMOTE_SCOPED "
    "with no remaining blocking findings. PHYS15 is the current accepted theory; "
    "PHYS14 remains its carried physical baseline."
)
old_status = (
    "Independent review is in progress; root will update this draft from the "
    "actual decision before publication."
)
accepted = {
    "loop": "PHYS15",
    "core_path": GITCORE,
    "task": "theory",
    "status": "PROMOTE_SCOPED",
    "decision": "PROMOTE_SCOPED",
    "science_decision": "PROMOTE_SCOPED",
    "review_status_text": status_text,
    "theory": GITCORE + "/theory/CORRELATED_ENDPOINT_THEORY_KO.md",
    "theory_sha256": theory_sha,
    "photon_theory_sha256": photon_sha,
    "independent_decision": GITCORE + "/review/DECISION.json",
    "independent_decision_sha256": decision_sha,
    "independent_review_decided_at_utc": decision["decided_at_utc"],
    "accepted_theoretical_claim_count": 9,
    "remaining_blocking_findings": [],
    "source_parent_commit": PARENT,
    "source_root_tree": TREE,
    "source_pr": "https://github.com/cosmosapjw-quantum/WU088_HH/pull/49",
    "scope": decision["decision_scope"],
    "inherited_premises": decision["inherited_premises"],
    "new_atomic_source_callbacks": 0,
    "new_physical_root_solves": 0,
    "new_physical_history_runs": 0,
    "new_NCP_jobs": 0,
    "next_task": "HH_CORRELATED_ENDPOINT_ENCLOSURE",
    "numerical_endpoint_defect_execution": "not_run",
    "publication_preparation_status": "SCIENCE_ACCEPTED_DOCUMENTATION_AND_DELIVERY_IN_PROGRESS",
    "commit_identity": "The detached delivery receipt will bind the actual containing commit and provider acknowledgements.",
}

final_bytes = {}
for rel in ["AGENTS.md", "README.md", "README_KO.md", "docs/coding/IMPLEMENTATION_PLAN.md"]:
    assert draft_bytes[rel].endswith(original_bytes[rel])
    prefix = draft_bytes[rel][:-len(original_bytes[rel])].decode("utf-8")
    if rel == "AGENTS.md":
        prefix = prefix.replace(
            old_status + " The admitted scientific baseline remains PHYS14 PROMOTE_SCOPED while this review is running.",
            status_text + " The accepted decision is recorded in " + GITCORE + "/review/DECISION.json.",
        )
        prefix = prefix.replace(
            "Root updates review and actual publication identities before publishing.",
            "Root binds actual publication identities and delivery acknowledgements when publishing.",
        ).replace(
            "and advance this theory node according to its final review.",
            "and advance the PHYS15 theory node with its actual PROMOTE_SCOPED decision.",
        ).replace(
            "The next local inclusion task keeps heavy_queue=[] and launch=false; native and microscopic lanes retain their own scientific conditions.",
            "The current inherited-data successor plan records heavy_queue=[] and launch=false. Execution routing follows its actual needs and the authorized task; native and microscopic lanes retain their existing scientific conditions.",
        )
    elif rel == "README.md":
        prefix = prefix.replace(
            old_status + " PHYS14 remains the admitted scientific baseline.", status_text
        )
        prefix = prefix.replace(
            "The current workflow is",
            "The [independent decision](" + GITCORE + "/review/DECISION.json) and "
            "[endpoint inclusion contract](" + GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json) "
            "bind the accepted scope and the numerical successor. Formal documentation and final delivery are in progress.\n\nThe current workflow is",
        )
    elif rel == "README_KO.md":
        prefix = prefix.replace(
            "독립 검토가 진행 중이며, 게시 전에 root가 실제 판정에 따라 이 초안을 갱신한다. 채택된 과학 기준점은 PHYS14 PROMOTE_SCOPED다.",
            "독립 검토에서 이론 주장 9개를 PROMOTE_SCOPED로 채택했고 남은 차단 지적은 0개다. 현재 채택된 이론은 PHYS15이며, PHYS14는 재사용하는 물리 계산 기준점으로 유지한다.",
        )
        prefix = prefix.replace(
            "- [현재 개발계획](CURRENT_DEVELOPMENT_PLAN.json)\n",
            "- [현재 개발계획](CURRENT_DEVELOPMENT_PLAN.json)\n"
            "- [독립 판정](" + GITCORE + "/review/DECISION.json)\n"
            "- [endpoint 포함 계산 계약](" + GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json)\n",
        )
        prefix = prefix.replace(
            "현재 운영 규약은",
            "정식 보고서와 최종 전달 기록은 현재 마무리 중이다.\n\n현재 운영 규약은",
        )
    else:
        prefix = prefix.replace(
            old_status + " The existing independently admitted baseline is PHYS14.", status_text
        )
        prefix = prefix.replace(
            "The next bounded numerical task is HH_CORRELATED_ENDPOINT_ENCLOSURE.",
            "The next bounded numerical task is HH_CORRELATED_ENDPOINT_ENCLOSURE, governed by "
            + GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json.",
        )
        prefix = prefix.replace(
            "Heavy queue is empty and launch=false.",
            "The current successor plan records an empty heavy queue and launch=false; execution routing follows the actual inherited-data inclusion needs.",
        )
        prefix = prefix.replace(
            "The current draft awaits the actual independent decision before root finalizes publication metadata.",
            "The independent PROMOTE_SCOPED decision is final for this theory scope; root completes the report and binds actual publication metadata at delivery.",
        )
    assert old_status not in prefix
    assert "독립 검토가 진행 중" not in prefix
    final_bytes[rel] = prefix.encode("utf-8") + original_bytes[rel]

for rel in ["CURRENT_DEVELOPMENT_PLAN.json", "RESEARCH_STATE.json"]:
    current = json.loads(draft_bytes[rel])
    original = json.loads(original_bytes[rel])
    assert current["previous_PHYS14_root_snapshot"] == original
    baseline = copy.deepcopy(original.get("current_science", original.get("scientific_baseline")))
    assert baseline["loop"] == "PHYS14"
    current["carried_physical_baseline"] = baseline
    current["current_accepted_theory"] = copy.deepcopy(accepted)
    current["current_candidate"] = copy.deepcopy(accepted)
    current["publication_preparation_status"] = "SCIENCE_ACCEPTED_DOCUMENTATION_AND_DELIVERY_IN_PROGRESS"
    current["publication_review_status"] = status_text
    current["workflow_policy_override"]["status"] = "APPLIED_TO_CURRENT_THEORY"
    current["current_science_state"] = GITCORE + "/state/RESEARCH_STATE.json"
    current["observable_contracts"] = GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json"
    if rel == "CURRENT_DEVELOPMENT_PLAN.json":
        current["decision"] = "PHYS15_THEORY_PROMOTE_SCOPED"
        current["scope"] = decision["decision_scope"]
        current["scientific_baseline"] = copy.deepcopy(accepted)
        current["current_scientific_baseline"] = copy.deepcopy(accepted)
        current["next_action"] = (
            "Complete the reviewed theory report and delivery, then implement and evaluate "
            "HH_CORRELATED_ENDPOINT_ENCLOSURE from its frozen contract using the existing "
            "same-COMMON source/carry/preconditioner binding."
        )
        current["next_here_status"] = "CONTRACTED_NUMERICAL_SUCCESSOR; EXECUTION_NOT_RUN"
        current["independent_science_review_sha256"] = decision_sha
    else:
        current["current_science"] = copy.deepcopy(accepted)
        current["current_execution"]["status"] = "THEORY_ACCEPTED_DOCUMENTATION_AND_DELIVERY_IN_PROGRESS"
        current["current_execution"]["scientific_status"] = "THEORY_PROMOTE_SCOPED; PHYSICAL_ENDPOINT_ENCLOSURE_NOT_RUN"
        current["current_execution"]["execution_evidence"] = {
            "photon_algebra": GITCORE + "/checks/photon/RUN_RECORD.json",
            "sector_signs": GITCORE + "/checks/photon/SECTOR_RUN_RECORD.json",
            "independent_review": GITCORE + "/review/RUN_RECORD.json",
            "nonlinear_discriminator": GITCORE + "/checks/NONLINEAR_TRANSFER_CHECKS.json",
            "symbolic_algebra": GITCORE + "/checks/WOLFRAM_ALGEBRA.json",
        }
        current["current_plan_update"]["status"] = "THEORY_PROMOTE_SCOPED; NUMERICAL_SUCCESSOR_NOT_RUN"
        current["current_plan_update"]["contract"] = GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json"
        current["admitted_current_science_remains_PHYS14_until_final_decision"] = False
    assert current["previous_PHYS14_root_snapshot"] == original
    final_bytes[rel] = payload(current)

rows = []
for rel in files:
    saved_draft = CORE / "evidence/overlay_versions/independent_review_in_progress" / rel
    write_new(saved_draft, draft_bytes[rel])
    (OVERLAY / rel).write_bytes(final_bytes[rel])
    final_readback = (OVERLAY / rel).read_bytes()
    assert final_readback == final_bytes[rel]
    original_after = (OLD / rel).read_bytes()
    assert original_after == original_bytes[rel]
    if rel.endswith(".md"):
        preservation = {
            "method": "exact original PHYS14 UTF-8 bytes retained as suffix",
            "original_suffix_bytes": len(original_bytes[rel]),
            "exact_preservation": final_readback.endswith(original_bytes[rel]),
        }
    else:
        final_obj = json.loads(final_readback)
        preservation = {
            "method": "entire original PHYS14 JSON object retained at previous_PHYS14_root_snapshot",
            "exact_original_object_preserved": final_obj["previous_PHYS14_root_snapshot"] == json.loads(original_bytes[rel]),
            "carried_physical_baseline_preserved": final_obj["carried_physical_baseline"] == baseline,
        }
    assert all(v for k, v in preservation.items() if k.startswith("exact") or k.endswith("_preserved"))
    rows.append({
        "path": rel,
        "original_PHYS14_path": str(OLD / rel),
        "original_PHYS14_bytes": len(original_bytes[rel]),
        "original_PHYS14_sha256": sha(original_bytes[rel]),
        "source_git_blob_sha": draft_by_path[rel]["source_git_blob_sha"],
        "before_draft_bytes": len(draft_bytes[rel]),
        "before_draft_sha256": sha(draft_bytes[rel]),
        "before_draft_snapshot": str(saved_draft.relative_to(CORE)),
        "after_bytes": len(final_readback),
        "after_sha256": sha(final_readback),
        "preservation": preservation,
        "source_file_unchanged": True,
    })

overlay_receipt = {
    "schema": "WU088_HH_PHYS15_ROOT_OVERLAY_FINAL_V1",
    "created_at_utc": NOW,
    "status": "SCIENCE_ACCEPTED_DOCUMENTATION_AND_DELIVERY_IN_PROGRESS",
    "scientific_decision": "PROMOTE_SCOPED",
    "accepted_theory": "PHYS15",
    "carried_physical_baseline": "PHYS14",
    "review": {"path": "review/DECISION.json", "sha256": decision_sha,
               "claims": 9, "remaining_blocking_findings": []},
    "source_parent_commit": PARENT,
    "source_parent_tree": TREE,
    "planned_core": GITCORE,
    "files": rows,
    "all_six_original_files_unchanged": True,
    "all_six_original_contents_preserved": True,
    "observable_contracts": GITCORE + "/contracts/ENDPOINT_ENCLOSURE_CONTRACT.json",
    "current_science_state": GITCORE + "/state/RESEARCH_STATE.json",
    "policy_override": readj(OVERLAY / "CURRENT_DEVELOPMENT_PLAN.json")["workflow_policy_override"],
    "new_physical_source_evaluations": 0,
    "new_physical_root_solves": 0,
    "new_physical_history_runs": 0,
    "cloud_writes_by_this_operation": 0,
    "delivery_owner_next_action": "Root completes PDF/document closeout and records actual Git/provider identities; R9/R10 remain open in the workflow record.",
}
write_new(CORE / "ROOT_OVERLAY_FINAL.json", payload(overlay_receipt))

# Preserve only the current workflow references actually used to create/check
# this record. Their hashes bind procedural authority without changing science.
for rel in [
    "references/WORKFLOW.json", "references/EVIDENCE_AND_HANDOFF.md",
    "references/THEORY_LOOP.md", "references/RESEARCH_POLICY.md",
    "scripts/run_record.py",
]:
    write_new(CORE / "evidence/workflow_1_0_0" / rel, (SKILL / rel).read_bytes())

state = {
    "schema_version": 1,
    "workflow_version": "1.0.0",
    "task": "research",
    "unit_id": "WU088_HH_PHYS15_CORRELATED_ENDPOINT_THEORY",
    "objective": "동일 COMMON의 Full과 실제 two-half 경로 사이의 상관된 기체·광자 잔차를 유도하고, 기존 Full 포함과 유한 관측량 식으로 endpoint 차이를 전달한다.",
    "scope": decision["decision_scope"],
    "status": "in_progress",
    "created_at_utc": NOW,
    "record_state": "R1-R8 closed; R9 formal PDF completion in progress; R10 final delivery pending",
    "locator_base": "Paths without a leading slash are relative to this PHYS15 core directory.",
    "dependencies": [],
    "evidence": [],
    "stages": [],
    "claims": [],
    "checks": [],
    "executions": [],
    "decisions": [],
    "overrides": [],
    "failures": [],
    "next_actions": [],
    "scientific_decision": "PROMOTE_SCOPED",
    "carried_physical_baseline": {"loop": "PHYS14", "source_commit": PARENT, "source_tree": TREE},
    "execution_counts": {"new_atomic_source_callbacks": 0, "new_physical_root_solves": 0,
                         "new_physical_history_runs": 0, "new_native_runs": 0, "new_NCP_jobs": 0},
    "same_file_preconditioner": {
        "file": "inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json",
        "q_upper": "0.00011736830563768177", "q_binary64_hex": "3f1ec474231fbe16",
        "binding": "fixed_C, abs_IminusCHp majorant, qArithmetic and exact binary radius from one original file",
    },
    "strong_no_go_claims": [],
}
ev_index = {}
dep_index = {}


def add_evidence(eid, rel, kind, scope, additional_dependencies=()):
    p = CORE / rel
    data = p.read_bytes()
    did = "dep_" + eid
    dep = {"id": did, "identity": "sha256:" + sha(data), "description": rel}
    state["dependencies"].append(dep)
    dep_index[did] = dep
    ev = {"id": eid, "kind": kind, "locator": rel, "scope": scope,
          "dependency_ids": [did, *additional_dependencies], "sha256": sha(data), "bytes": len(data)}
    state["evidence"].append(ev)
    ev_index[eid] = ev
    return eid


base_specs = [
    ("PHYS14_DECISION", "inputs/phys14/review/DECISION.json", "decision", "Inherited scoped actual two-half physical result and source/C2/root premises."),
    ("PHYS14_THEORY", "inputs/phys14/theory/THEORY_CANDIDATE_KO.md", "derivation", "Same-geometric-isotropic family, 39-state closure and actual second-half composition."),
    ("PHYS14_GEOMETRY", "inputs/phys14/review/GEOMETRY_REVIEW.json", "review", "Original geometric subfamily and verified remap branch."),
    ("PHYS14_RESULT", "inputs/phys14/results/advance01/ADVANCE_RESULTS.json", "calculation", "Actual carried second-half endpoint and derivative enclosures, reused without replay."),
    ("FIRST_CARRY", "inputs/phys14/inputs/phys11/CARRY_RESULTS.json", "calculation", "Actual first-half joint gas/photon/guard carry."),
    ("ROOT_READOUT", "inputs/phys14/inputs/phys13/THERMO_RESULTS.json", "calculation", "Inherited Full and first-half root/readout images."),
    ("FULL_SOURCE", "inputs/phys14/inputs/ncp07/results/full/SOURCE_BOX.json", "source", "Original whole-X Full source and derivative inclusions."),
    ("HALF_SOURCE", "inputs/phys14/inputs/ncp07/results/first_half/SOURCE_BOX.json", "source", "Original first-half source and captured normalization."),
    ("FULL_CENTRE", "inputs/phys14/inputs/ncp07/results/full/SOURCE_CENTRE.json", "source", "Original source at common gas centre."),
    ("HALF_CENTRE", "inputs/ncp07_additions/results/first_half/SOURCE_CENTRE.json", "source", "Original NCP07 first-half centre source, matched to archive member."),
    ("FULL_PRECONDITIONER", "inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json", "source", "Original same-file fixed_C, majorant B, radius S and qArithmetic."),
    ("FT03_SOURCE", "inputs/phys14/inputs/ncp07/candidate/src/ft03_interval.rs", "source", "Original photo-off reaction and thermal normalization graph."),
    ("HH_SOURCE", "inputs/ncp07_additions/candidate/src/hh_primary_extension.rs", "source", "Original HH source graph and threshold constants."),
]
for spec in base_specs:
    add_evidence(*spec)
reuse_refs = [row[0] for row in base_specs]
for spec in [
    ("WORKFLOW", "evidence/workflow_1_0_0/references/WORKFLOW.json", "source", "Current user-selected built-in 1.0.0 THEORY R1-R10 enums and stage definitions."),
    ("EVIDENCE_POLICY", "evidence/workflow_1_0_0/references/EVIDENCE_AND_HANDOFF.md", "source", "Current evidence, execution, reuse identity and handoff contract."),
    ("CONTRACT", "contracts/ENDPOINT_ENCLOSURE_CONTRACT.json", "artifact", "Reviewed expressions, domains, input/output units and exact numerical successor acceptance."),
    ("ROOT_THEORY", "theory/CORRELATED_ENDPOINT_THEORY_KO.md", "derivation", "Sections 1-9: contract, same-COMMON residual, source bridge, averaged Jacobian, finite readouts, ledgers and actual photon secant."),
    ("PHOTON_THEORY", "theory/PHOTON_DEFECT_THEOREM_KO.md", "derivation", "Six outgoing and seven integrated-absorption sectors, original-grid signs and guard chronology."),
    ("SOURCE_BINDING", "evidence/bindings/BINDINGS.json", "calculation", "Exact COMMON/birth/source leaves, original model graph and pullback/domain bindings."),
    ("SOURCE_NORMALIZATION", "theory/ASSUMPTIONS_AND_BINDINGS_KO.md", "derivation", "Same-alpha compatibility, density/fhat bridge and within-X temperature pullback."),
    ("C_BINDING", "evidence/bindings/FIXED_PRECONDITIONER_BINDING.json", "calculation", "Original fixed_C IEEE identity and same-file q/S/majorant binding; targeted exact rational checks."),
    ("THRESHOLD_IDENTITY", "evidence/bindings/FT03_THRESHOLD_IDENTITY.json", "calculation", "FT03 model threshold and original captured H/He chi binary identities."),
    ("PHOTON_CHECKS", "checks/photon/PHOTON_EXACT_CHECKS.json", "calculation", "3,148 exact scalar equalities in manufactured algebra examples and original leaf identities."),
    ("PHOTON_PRE_RUN", "checks/photon/PRE_RUN.json", "resource", "Original pre-run command, purpose and bounded algebra-check budget."),
    ("PHOTON_RUN", "checks/photon/RUN_RECORD.json", "resource", "Actual photon algebra command, zero exit and measured time/RSS."),
    ("SIGN_CHECKS", "checks/photon/SECTOR_SIGN_CHECKS.json", "calculation", "Exact captured-leaf inequality conditions for the scoped sector sign statements."),
    ("SIGN_PRE_RUN", "checks/photon/SECTOR_PRE_RUN.json", "resource", "Original sign-check command and budget."),
    ("SIGN_RUN", "checks/photon/SECTOR_RUN_RECORD.json", "resource", "Actual sign-check command, zero exit and measured time/RSS."),
    ("NONLINEAR_CHECKS", "checks/NONLINEAR_TRANSFER_CHECKS.json", "calculation", "Four-dimensional manufactured nonlinear residual and finite-temperature discriminators; 14 relations, no physical endpoint evaluation."),
    ("NONLINEAR_PRE_RUN", "checks/NONLINEAR_PRE_RUN.json", "resource", "Original exact-Fraction discriminating example plan and command."),
    ("WOLFRAM_CHECKS", "checks/WOLFRAM_ALGEBRA.json", "calculation", "Actual independent symbolic tool response {0,0,0,0} for four rational identities."),
    ("REVIEW", "review/REVIEW_KO.md", "review", "Independent proof, source graph and original-leaf examination with resolved componentwise secant notation finding."),
    ("REVIEW_DECISION", "review/DECISION.json", "decision", "Actual PROMOTE_SCOPED for nine theory claims; zero remaining blocking findings."),
    ("REVIEW_CHECKS", "review/INDEPENDENT_THEORY_CHECKS.json", "calculation", "Separately authored posthoc exact arithmetic, 26 checks; no candidate imports or physical replay."),
    ("REVIEW_RUN", "review/RUN_RECORD.json", "resource", "Actual independent check command, exit 0 and measured wall/CPU/RSS."),
    ("SECANT_CORRECTION", "checks/photon/SECANT_TYPE_CORRECTION.json", "artifact", "Scalar d_x is applied componentwise; corrected vector/matrix display type without coefficient changes."),
    ("OVERLAY_FINAL", "ROOT_OVERLAY_FINAL.json", "artifact", "Six before/after hashes; exact PHYS14 suffix/snapshot preservation and current policy mapping."),
    ("DAG_CHECK", "evidence/DAG_CHANGE_CHECK.json", "artifact", "Prior 10 nodes preserved, 12-node successor DAG acyclic and original global DAG hash retained."),
    ("REPORT_MARKDOWN", "REPORT_KO.md", "artifact", "Current formal report text; PDF completion remains R9 obligation."),
    ("HANDOFF", "HANDOFF_KO.md", "artifact", "Local concrete successor inputs, formulas, acceptance and restart instructions; final delivery remains R10 obligation."),
    ("PINNING_INCIDENT", "evidence/bindings/pinning_evidence/FIRST_FAILURE.json", "artifact", "Preserved metadata assembly TypeError; fixed variable shadowing after already successful source assertions."),
    ("OVERLAY_INCIDENT", "evidence/bindings/overlay_evidence/FIRST_ATTEMPT.json", "artifact", "Preserved first create-only attempt stopped on an already-created empty output directory; no file was changed by that attempt."),
]:
    add_evidence(*spec)


def stage(sid, status, refs, reason):
    dependencies = sorted({d for e in refs for d in ev_index[e]["dependency_ids"]})
    state["stages"].append({
        "id": sid, "status": status, "evidence_refs": refs,
        "dependency_ids": dependencies, "reason": reason,
        "reuse": {"dependency_identities": {d: dep_index[d]["identity"] for d in dependencies}}
                 if status == "reused" else None,
    })


stage("R1", "complete", ["ROOT_THEORY", "CONTRACT", "WORKFLOW", "OVERLAY_FINAL"],
      "같은 COMMON·alpha·global lambda,b의 Full 대 실제 two-half를 이론 단위로 고정하고, 완료 조건과 수치 후속 계약 및 현재 절차 override를 명시했다.")
stage("R2", "reused", reuse_refs,
      "PHYS14의 승인된 실제 carry·source/C2/root·geometry 결과와 원 NCP07 source/preconditioner를 정확한 파일 identity로 재사용한다. 기존 과학 계산의 재실행은 없다.")
stage("R3", "complete", ["ROOT_THEORY", "SOURCE_BINDING", "SOURCE_NORMALIZATION", "C_BINDING", "THRESHOLD_IDENTITY"],
      "P1-P7과 원 capture의 density/fhat, source 시각, birth, 같은 계열과 X/pullback 영역을 직접 유도한 항등식 및 남은 수치 평가와 구분했다.")
stage("R4", "complete", ["ROOT_THEORY", "PHOTON_THEORY", "NONLINEAR_PRE_RUN", "PHOTON_PRE_RUN", "SIGN_PRE_RUN"],
      "공통 초기 입력을 제거한 잔차, 일곱 흡수 항, 온도 정렬 source 표현과 평균 Jacobian을 선택하고 endpoint Jacobian·미분 온도식과 구별하는 사례를 구성했다.")
stage("R5", "complete", ["ROOT_THEORY", "PHOTON_THEORY", "SOURCE_NORMALIZATION", "C_BINDING"],
      "상관 기체 잔차, chronology 분해, source 정규화 연결, 평균 Jacobian 포함, 유한 관측량·공통 adjoint·ledger·실제 photon endpoint 전달을 구성적으로 유도했다.")
stage("R6", "complete", ["REVIEW", "REVIEW_DECISION", "REVIEW_CHECKS", "REVIEW_RUN", "SECANT_CORRECTION"],
      "독립 검토자가 원 source 및 핵심 증명을 검토하고 별도 exact 검산을 수행했다. photon secant의 표시형 지적을 교정했고 남은 차단 지적은 없다.")
stage("R7", "complete", ["PHOTON_CHECKS", "PHOTON_RUN", "SIGN_CHECKS", "SIGN_RUN", "NONLINEAR_CHECKS", "WOLFRAM_CHECKS", "REVIEW_CHECKS", "REVIEW_RUN"],
      "실제 제조 대수·부호·유한 온도·평균 Jacobian 판별 검산과 독립 기호·exact 검산을 완료했다. 실제 물리 endpoint 구간은 이 증명 판정의 의무가 아니며 별도 후속 실행으로 남긴다.")
stage("R8", "complete", ["REVIEW_DECISION", "REVIEW", "CONTRACT"],
      "원 geometric isotropic same-COMMON 계열과 상속 전제 아래 이론 주장 9개를 PROMOTE_SCOPED로 채택했다. 새 strong no-go 주장은 없다.")
stage("R9", "in_progress", ["ROOT_THEORY", "PHOTON_THEORY", "REPORT_MARKDOWN", "CONTRACT"],
      "정식 보고서 본문과 수치 구현 계약이 작성됐다. root가 최종 LaTeX/PDF 제작·확인을 마친 뒤 이 단계를 종료한다.")
stage("R10", "pending", ["HANDOFF", "DAG_CHECK", "OVERLAY_FINAL"],
      "현재 local handoff와 DAG/root entry는 작성됐다. root가 최종 산출물 identity와 실제 Git/provider 전달 근거를 결박한 뒤 종료한다.")

claim_support = {
    "PHYS15_COMMON_INPUT_BINDING": ["SOURCE_BINDING", "PHYS14_THEORY"],
    "PHYS15_CORRELATED_GAS_RESIDUAL": ["ROOT_THEORY", "REVIEW_CHECKS"],
    "PHYS15_PHOTON_CHRONOLOGY": ["PHOTON_THEORY", "PHOTON_CHECKS"],
    "PHYS15_SOURCE_TIME_BRIDGE": ["SOURCE_NORMALIZATION", "SOURCE_BINDING", "THRESHOLD_IDENTITY"],
    "PHYS15_MEAN_JACOBIAN_TRANSFER": ["ROOT_THEORY", "C_BINDING", "FULL_PRECONDITIONER", "NONLINEAR_CHECKS"],
    "PHYS15_FINITE_OBSERVABLE_TRANSFER": ["ROOT_THEORY", "NONLINEAR_CHECKS", "WOLFRAM_CHECKS"],
    "PHYS15_LEDGER_AND_CHEMICAL_PROJECTION": ["ROOT_THEORY", "PHOTON_THEORY", "SIGN_CHECKS"],
    "PHYS15_ACTUAL_PHOTON_ENDPOINT_SECANT": ["ROOT_THEORY", "PHOTON_THEORY", "SECANT_CORRECTION", "REVIEW_CHECKS"],
    "PHYS15_SECTOR_SIGNS": ["PHOTON_THEORY", "SIGN_CHECKS"],
}
for claim in decision["claim_decisions"]:
    state["claims"].append({
        "id": claim["id"], "statement": claim["statement"],
        "scope": decision["decision_scope"], "basis": ["derived"],
        "evidence_refs": [*claim_support[claim["id"]], "REVIEW_DECISION"],
        "obligations": [], "decision": "PROMOTE_SCOPED",
        "proof_locations": claim["locations"],
        "conditional_premises": decision["inherited_premises"],
    })
state["claims"].append({
    "id": "HH_CORRELATED_ENDPOINT_ENCLOSURE",
    "statement": "실제 원 입력에서 r,d,DeltaT,Deltae,Deltaw,Deltane 및 photon/guard endpoint 차이의 수치 구간을 계산한다.",
    "scope": "계약에 지정된 같은 입력 계열의 다음 수치 단위",
    "basis": ["unresolved"], "evidence_refs": ["CONTRACT"],
    "obligations": ["검토된 식을 공통 입력 표현으로 구현하고 실제 포함 계산을 수행한 후 결과·실행 근거와 독립 수치 판정을 기록한다."],
    "execution_status": "not_run",
})

for eid, runrel, refs, scope in [
    ("EXEC_PHOTON_ALGEBRA", "checks/photon/RUN_RECORD.json", ["PHOTON_RUN", "PHOTON_CHECKS"], "Python Fraction and exact dual algebra; manufactured examples and captured leaves."),
    ("EXEC_SECTOR_SIGNS", "checks/photon/SECTOR_RUN_RECORD.json", ["SIGN_RUN", "SIGN_CHECKS"], "Python Fraction exact original-leaf inequalities."),
    ("EXEC_INDEPENDENT_REVIEW", "review/RUN_RECORD.json", ["REVIEW_RUN", "REVIEW_CHECKS"], "Independently authored Python Fraction checks; no candidate module import."),
]:
    run = readj(CORE / runrel)
    assert run["exit_code"] == 0
    state["executions"].append({
        "id": eid, "status": "completed", "command": run["command"],
        "environment": {"runtime": "python3 as recorded by the original run",
                        "location": str(BASE), "arithmetic_and_scope": scope,
                        "original_run_record": runrel},
        "evidence_refs": refs, "exit_code": 0,
        "reason": "Existing actual execution record is linked; no re-execution in state assembly.",
    })
state["executions"].append({
    "id": "EXEC_ENDPOINT_ENCLOSURE", "status": "not_run", "command": [],
    "environment": {"input_contract": "contracts/ENDPOINT_ENCLOSURE_CONTRACT.json"},
    "evidence_refs": ["CONTRACT"], "exit_code": None,
    "reason": "Successor evaluator is specified by its contract; its concrete executable command belongs to the next implementation unit.",
})
for cid, domain, result, refs, execution, reason in [
    ("PHOTON_EXACT_ALGEBRA", "math", "pass_scoped", ["PHOTON_CHECKS", "PHOTON_RUN"], "EXEC_PHOTON_ALGEBRA", "3,148 scalar equalities check the stated exact algebra examples and captured identities; this is not a physical case count."),
    ("ORIGINAL_SECTOR_SIGNS", "physics", "pass_scoped", ["SIGN_CHECKS", "SIGN_RUN"], "EXEC_SECTOR_SIGNS", "Source leaf inequalities support the sign theorem on its explicit positive domain."),
    ("NONLINEAR_TRANSFER_DISCRIMINATORS", "math", "pass_scoped", ["NONLINEAR_CHECKS", "NONLINEAR_PRE_RUN"], None, "Actual stored exact-Fraction result distinguishes the averaged Jacobian and finite-temperature quotient from their local approximations."),
    ("WOLFRAM_IDENTITIES", "math", "pass_scoped", ["WOLFRAM_CHECKS"], None, "Actual symbolic tool output is {0,0,0,0}; no shell exit code is inferred for the symbolic service."),
    ("INDEPENDENT_THEORY_REVIEW", "math", "pass_scoped", ["REVIEW", "REVIEW_CHECKS", "REVIEW_RUN", "REVIEW_DECISION"], "EXEC_INDEPENDENT_REVIEW", "26 separately authored checks and direct proof review; all reported blocking findings resolved."),
    ("SOURCE_AND_PRECONDITIONER_BINDINGS", "physics", "pass_scoped", ["SOURCE_BINDING", "C_BINDING", "THRESHOLD_IDENTITY"], None, "Targeted original-file and exact binary/rational identity checks are reused."),
    ("ROOT_ENTRY_PRESERVATION", "packaging", "pass_scoped", ["OVERLAY_FINAL"], None, "Six original entries remain exact Markdown suffixes or complete unchanged JSON snapshots."),
    ("ACTUAL_PHYSICAL_ENDPOINT_ENCLOSURE", "numerics", "not_run", ["CONTRACT"], "EXEC_ENDPOINT_ENCLOSURE", "The named successor performs actual physical interval evaluation; current theory decision does not claim its values."),
]:
    state["checks"].append({"id": cid, "domain": domain, "result": result,
                            "evidence_refs": refs, "reason": reason, "execution_ref": execution})

state["decisions"] = [
    {"id": "PHYS15_THEORY_ACCEPTED", "decision": "PROMOTE_SCOPED",
     "scope": decision["decision_scope"], "evidence_refs": ["REVIEW_DECISION"],
     "reason": decision["stop_reason"]},
    {"id": "NUMERICAL_SUCCESSOR_DEFINED", "decision": "HH_CORRELATED_ENDPOINT_ENCLOSURE",
     "evidence_refs": ["CONTRACT", "HANDOFF"],
     "reason": "Actual endpoint interval evaluation is the next research unit under the fixed reviewed input and expression contract."},
]
override = copy.deepcopy(overlay_receipt["policy_override"])
override["evidence_refs"] = ["WORKFLOW", "EVIDENCE_POLICY", "OVERLAY_FINAL"]
state["overrides"] = [override, {
    "id": "SECANT_COMPONENTWISE_NOTATION_CORRECTION",
    "previous_rule": "A displayed diagonal matrix was multiplied directly by scalar d_x while the left side denoted a vector.",
    "replacement": "Write the photon identity for each retained component j=0..32 and zero guard corrections.",
    "affected_dependencies": "Root equation (9.2) and photon equation (50); coefficients and truth conditions unchanged.",
    "status": "resolved",
    "evidence_refs": ["SECANT_CORRECTION", "REVIEW_DECISION"],
}]
state["failures"] = [
    {"id": "PRECONDITIONER_RECEIPT_ASSEMBLY_VARIABLE_SHADOWING",
     "class": "implementation", "status": "resolved",
     "evidence_refs": ["PINNING_INCIDENT", "C_BINDING"],
     "next_action": "Resolved by a metadata variable rename; source assertions retained and no physical computation replayed."},
    {"id": "EMPTY_OVERLAY_DIRECTORY_CREATE_GUARD",
     "class": "implementation", "status": "resolved",
     "evidence_refs": ["OVERLAY_INCIDENT", "OVERLAY_FINAL"],
     "next_action": "Resolved by target-file absence checks and exclusive creation; the first attempt wrote no target file."},
]
state["next_actions"] = [
    {"id": "FINISH_R9", "owner": "/root", "stage": "R9",
     "action": "Complete and verify the final LaTeX/PDF, bind report identities and mark R9 complete.",
     "evidence_refs": ["REPORT_MARKDOWN", "CONTRACT"]},
    {"id": "FINISH_R10", "owner": "/root", "stage": "R10",
     "action": "Complete actual publication/delivery acknowledgements, preserve artifact identities and handoff, then close R10.",
     "evidence_refs": ["HANDOFF", "DAG_CHECK", "OVERLAY_FINAL"]},
    {"id": "NEXT_THEORY_APPLICATION", "unit_id": "HH_CORRELATED_ENDPOINT_ENCLOSURE",
     "status": "not_run", "action": "Implement and evaluate the reviewed common-input residual/endpoint contract.",
     "evidence_refs": ["CONTRACT", "HANDOFF"]},
]
state_path = CORE / "state/RESEARCH_STATE.json"
write_new(state_path, payload(state))

# This sole new execution validates metadata structure and references only.
checker = SKILL / "scripts/run_record.py"
command = [sys.executable, str(checker), "check", str(state_path)]
start = time.monotonic()
run = subprocess.run(command, text=True, capture_output=True, check=False)
elapsed = time.monotonic() - start
check = {
    "schema": "WU088_HH_PHYS15_WORKFLOW_STATE_SCHEMA_CHECK_V1",
    "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": command,
    "execution_status": "completed" if run.returncode == 0 else "failed",
    "exit_code": run.returncode,
    "wall_seconds": elapsed,
    "environment": {"python": platform.python_version(), "platform": platform.platform()},
    "state_path": "state/RESEARCH_STATE.json",
    "state_sha256": sha(state_path.read_bytes()),
    "state_snapshot": "R1-R8 complete/reused; R9 in_progress; R10 pending",
    "checker_sha256": sha(checker.read_bytes()),
    "workflow_path": "evidence/workflow_1_0_0/references/WORKFLOW.json",
    "workflow_sha256": sha((SKILL / "references/WORKFLOW.json").read_bytes()),
    "stdout": run.stdout,
    "stderr": run.stderr,
    "validation_scope": "structure_and_internal_references",
    "scientific_validity": "not_assessed_by_schema_checker",
    "new_physical_source_evaluations": 0,
    "new_physical_root_solves": 0,
    "new_physical_history_runs": 0,
    "supersession_rule": "A later state edit requires a new actual schema-check receipt; this receipt binds only the listed snapshot hash.",
}
write_new(CORE / "state/SCHEMA_CHECK.json", payload(check))
write_new(CORE / "evidence/finalize_publication_overlay_and_state.py", Path(__file__).read_bytes())
assert run.returncode == 0, run.stdout + run.stderr
print(json.dumps({
    "overlay_files": [{"path": row["path"], "sha256": row["after_sha256"],
                       "preserved": row["preservation"]} for row in rows],
    "overlay_receipt_sha256": sha((CORE / "ROOT_OVERLAY_FINAL.json").read_bytes()),
    "state_sha256": sha(state_path.read_bytes()),
    "schema_check_sha256": sha((CORE / "state/SCHEMA_CHECK.json").read_bytes()),
    "schema_check_exit_code": run.returncode,
    "stage_statuses": {row["id"]: row["status"] for row in state["stages"]},
}, ensure_ascii=False, indent=2))
