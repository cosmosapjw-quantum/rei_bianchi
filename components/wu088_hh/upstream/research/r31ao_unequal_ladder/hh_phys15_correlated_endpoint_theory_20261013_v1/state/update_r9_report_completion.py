#!/usr/bin/env python3
"""Record final-report evidence and current JSON entries; keep delivery in progress."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time

CORE = Path(__file__).resolve().parents[1]
STATE = CORE / "state"
SKILL = Path("/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def readj(path):
    return json.loads(path.read_text(encoding="utf-8"))


def asbytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def create(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(value)


before_bytes = (STATE / "RESEARCH_STATE.json").read_bytes()
before_check = (STATE / "SCHEMA_CHECK.json").read_bytes()
before = json.loads(before_bytes)
current = copy.deepcopy(before)
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
assert before["stages"][8]["id"] == "R9" and before["stages"][8]["status"] == "in_progress"
assert before["stages"][9]["id"] == "R10" and before["stages"][9]["status"] == "pending"

qa = readj(CORE / "report/REPORT_QA.json")
manifest = readj(CORE / "report/REPORT_MANIFEST.json")
pdf_path = CORE / "report/WU088_HH_PHYS15_THEORY_20261013.pdf"
pdf_bytes = pdf_path.read_bytes()
assert len(pdf_bytes) == qa["pdf_bytes"] == 236812
assert sha(pdf_bytes) == qa["pdf_sha256"] == "bb56b101ce91b1323cf558214d58744293e40c085d4a81067720a86613fb7515"
assert qa["status"] == qa["visual_qa"]["result"] == "PASS"
assert qa["compile_exit_code"] == 0 and qa["page_count"] == 17
for key in ("overfull_hbox_count", "overfull_vbox_count", "missing_character_count",
            "undefined_reference_or_citation_count", "latex_warning_count",
            "replacement_character_count", "text_outside_page_count",
            "font_glyph_loss_count"):
    assert qa[key] == 0
manifest_by_path = {row["path"]: row for row in manifest["files"]}
verified_report_files = []
for rel in [*qa["report_source_sha256"], "WU088_HH_PHYS15_THEORY_20261013.pdf", "REPORT_QA.json"]:
    data = (CORE / "report" / rel).read_bytes()
    member = manifest_by_path[rel]
    assert len(data) == member["bytes"] and sha(data) == member["sha256"]
    if rel.endswith(".tex"):
        assert sha(data) == qa["report_source_sha256"][rel]
    verified_report_files.append({"path": "report/" + rel, "bytes": len(data), "sha256": sha(data)})

# The parent explicitly added these two current root JSON entries to this step.
# Keep four Markdown entries, prior snapshots, physical baseline and science intact.
gitcore = "research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1"
overlay = CORE / "publication_overlay"
overlay_receipt_path = CORE / "ROOT_OVERLAY_FINAL.json"
overlay_receipt_before = overlay_receipt_path.read_bytes()
overlay_receipt = json.loads(overlay_receipt_before)
overlay_json_before = {
    rel: (overlay / rel).read_bytes()
    for rel in ("CURRENT_DEVELOPMENT_PLAN.json", "RESEARCH_STATE.json")
}
report_binding = {
    "path": gitcore + "/report/WU088_HH_PHYS15_THEORY_20261013.pdf",
    "sha256": sha(pdf_bytes), "bytes": len(pdf_bytes), "page_count": 17,
    "tex": gitcore + "/report/WU088_HH_PHYS15_THEORY_20261013.tex",
    "qa": gitcore + "/report/REPORT_QA.json",
    "qa_sha256": sha((CORE / "report/REPORT_QA.json").read_bytes()),
    "manifest": gitcore + "/report/REPORT_MANIFEST.json",
    "manifest_sha256": sha((CORE / "report/REPORT_MANIFEST.json").read_bytes()),
}
publication_status = "SCIENCE_AND_REPORT_COMPLETE_DELIVERY_RECEIPT_SEPARATE"
next_action = (
    "Implement and evaluate HH_CORRELATED_ENDPOINT_ENCLOSURE using its reviewed "
    "common-input residual and endpoint contract with the existing source/carry/preconditioner binding."
)
json_after = {}
for rel, data in overlay_json_before.items():
    previous_entry = json.loads(data)
    entry = copy.deepcopy(previous_entry)
    entry["publication_preparation_status"] = publication_status
    entry["next_action"] = next_action
    entry["actual_publication_receipt"] = (
        "Actual Git commit/tree identities and provider acknowledgements are recorded in a separate "
        "delivery receipt after those operations; this report-complete state does not assert their success."
    )
    for key, item in entry.items():
        if key in {"scientific_baseline", "current_scientific_baseline", "current_accepted_theory",
                   "current_candidate", "current_science"}:
            assert isinstance(item, dict) and item["loop"] == "PHYS15"
            item["publication_preparation_status"] = publication_status
            item["report"] = copy.deepcopy(report_binding)
            item["next_action"] = next_action
    if rel == "RESEARCH_STATE.json":
        entry["current_execution"]["status"] = publication_status
    for key in previous_entry:
        if key.startswith("previous_") or key.startswith("historical_") or key == "carried_physical_baseline":
            assert entry[key] == previous_entry[key]
    json_after[rel] = asbytes(entry)

overlay_versions = CORE / "evidence/overlay_versions/report_pending"
create(overlay_versions / "ROOT_OVERLAY_FINAL.json", overlay_receipt_before)
for rel, data in overlay_json_before.items():
    create(overlay_versions / rel, data)
    (overlay / rel).write_bytes(json_after[rel])
for row in overlay_receipt["files"]:
    if row["path"] in json_after:
        rel = row["path"]
        assert row["after_sha256"] == sha(overlay_json_before[rel])
        row["before_report_completion_bytes"] = len(overlay_json_before[rel])
        row["before_report_completion_sha256"] = sha(overlay_json_before[rel])
        row["before_report_completion_snapshot"] = "evidence/overlay_versions/report_pending/" + rel
        row["after_bytes"] = len(json_after[rel])
        row["after_sha256"] = sha(json_after[rel])
        row["historical_objects_unchanged_at_report_closeout"] = True
        row["carried_physical_baseline_unchanged_at_report_closeout"] = True
overlay_receipt["updated_at_utc"] = now
overlay_receipt["status"] = publication_status
overlay_receipt["report"] = copy.deepcopy(report_binding)
overlay_receipt["previous_receipt"] = {
    "path": "evidence/overlay_versions/report_pending/ROOT_OVERLAY_FINAL.json",
    "sha256": sha(overlay_receipt_before),
}
overlay_receipt["delivery_owner_next_action"] = (
    "Root records actual containing Git commit/tree and provider acknowledgements in the separate delivery receipt; "
    "R10 remains in progress until the actual acknowledgement is bound."
)
overlay_receipt["next_scientific_action"] = next_action
overlay_receipt["report_closeout_mutations"] = {
    "current_root_json_entries": 2, "Markdown_entries": 0,
    "historical_objects": 0, "carried_physical_baseline": 0, "science_proof_contract_DAG": 0,
}
overlay_receipt_path.write_bytes(asbytes(overlay_receipt))

evidence_index = {row["id"]: row for row in current["evidence"]}
overlay_evidence = evidence_index["OVERLAY_FINAL"]
overlay_evidence["sha256"] = sha(overlay_receipt_path.read_bytes())
overlay_evidence["bytes"] = overlay_receipt_path.stat().st_size
for dep in current["dependencies"]:
    if dep["id"] == "dep_OVERLAY_FINAL":
        dep["identity"] = "sha256:" + overlay_evidence["sha256"]
assert sha((CORE / "HANDOFF_KO.md").read_bytes()) == evidence_index["HANDOFF"]["sha256"]
assert sha((CORE / "REPORT_KO.md").read_bytes()) == evidence_index["REPORT_MARKDOWN"]["sha256"]
new_evidence_ids = []
for eid, rel, kind, scope in [
    ("REPORT_PDF_FINAL", "report/WU088_HH_PHYS15_THEORY_20261013.pdf", "artifact",
     "Final frozen 17-page PDF, 236812 bytes; report QA and manifest bind these exact bytes."),
    ("REPORT_TEX_FINAL", "report/WU088_HH_PHYS15_THEORY_20261013.tex", "artifact",
     "Final XeLaTeX entry source; all six TeX source identities are also recorded and matched in the final QA and report manifest."),
    ("REPORT_QA_FINAL", "report/REPORT_QA.json", "review",
     "Actual report build/visual QA: compile exit 0, all 17 pages inspected, no missing glyphs or undefined references; math decision is separately linked."),
    ("REPORT_MANIFEST_FINAL", "report/REPORT_MANIFEST.json", "artifact",
     "Frozen PDF, six TeX sources, fonts and build/QA support-file identities; targeted PDF/TeX/QA members matched to actual bytes."),
]:
    assert eid not in evidence_index
    data = (CORE / rel).read_bytes()
    did = "dep_" + eid
    current["dependencies"].append({"id": did, "identity": "sha256:" + sha(data), "description": rel})
    evidence = {"id": eid, "kind": kind, "locator": rel, "scope": scope,
                "dependency_ids": [did], "sha256": sha(data), "bytes": len(data)}
    current["evidence"].append(evidence)
    evidence_index[eid] = evidence
    new_evidence_ids.append(eid)

# This is a report-status description, not a change to a scientific claim.
evidence_index["REPORT_MARKDOWN"]["scope"] = (
    "Formal report text captured before PDF closeout; the final PDF/TeX/QA/manifest evidence now closes the R9 report obligation."
)
r9 = current["stages"][8]
r9["status"] = "complete"
r9["evidence_refs"] = list(dict.fromkeys([*r9["evidence_refs"], *new_evidence_ids, "HANDOFF"]))
r9["dependency_ids"] = sorted({did for eid in r9["evidence_refs"]
                               for did in evidence_index[eid]["dependency_ids"]})
r9["reason"] = (
    "정식 17쪽 LaTeX/PDF와 실제 compile/visual QA PASS 및 report manifest를 결박했다. "
    "확정 PDF·TeX·QA의 파일 identity를 확인했고 수치 포함 계약과 인계 문서까지 연결하여 R9를 완료한다."
)
r10 = current["stages"][9]
r10["status"] = "in_progress"
r10["reason"] = (
    "정식 보고서, local handoff와 DAG/root entry가 준비됐다. root가 Git scientific commit과 실제 provider ACK를 "
    "확인하여 전달 identity를 연결하는 중이며, 해당 근거가 도착한 후 R10을 종료한다."
)
current["updated_at_utc"] = now
current["status"] = "in_progress"
current["record_state"] = "R1-R9 closed; R10 actual Git/provider delivery in progress"
current["decisions"].append({
    "id": "R9_REPORT_COMPLETED", "decision": "R9 complete",
    "decided_at_utc": now, "evidence_refs": [*new_evidence_ids, "CONTRACT", "HANDOFF"],
    "reason": "The frozen final PDF/TeX/QA records and the existing implementation/handoff contract satisfy the formal report obligation.",
    "pdf_sha256": sha(pdf_bytes), "pdf_bytes": len(pdf_bytes), "page_count": qa["page_count"],
})
current["checks"].append({
    "id": "FINAL_REPORT_BUILD_AND_QA", "domain": "packaging", "result": "pass_scoped",
    "evidence_refs": new_evidence_ids, "execution_ref": None,
    "reason": "Reused the actual final report build and visual QA; matched PDF/TeX/QA manifest identities. No report rebuild or scientific rerun was performed by this state update.",
})
current["next_actions"] = [row for row in current["next_actions"] if row["id"] != "FINISH_R9"]
for action in current["next_actions"]:
    if action["id"] == "FINISH_R10":
        action["status"] = "in_progress"
        action["action"] = "Bind the actual Git scientific commit and provider acknowledgements supplied by root, record final delivery identities, and then close R10."

# Keep the inherited R2 identity snapshot and all scientific assertions intact.
assert current["stages"][:8] == before["stages"][:8]
for old, updated in zip(before["dependencies"], current["dependencies"]):
    if old["id"] != "dep_OVERLAY_FINAL":
        assert old == updated
assert current["claims"] == before["claims"]
for old in before["evidence"]:
    if old["id"] not in {"REPORT_MARKDOWN", "OVERLAY_FINAL"}:
        assert evidence_index[old["id"]] == old
assert current["executions"] == before["executions"]

versions = STATE / "versions/pre_R9_pdf_closeout"
create(versions / "RESEARCH_STATE.json", before_bytes)
create(versions / "SCHEMA_CHECK.json", before_check)
after_bytes = asbytes(current)
(STATE / "RESEARCH_STATE.json").write_bytes(after_bytes)

checker = SKILL / "scripts/run_record.py"
command = [sys.executable, str(checker), "check", str(STATE / "RESEARCH_STATE.json")]
start = time.monotonic()
run = subprocess.run(command, capture_output=True, text=True, check=False)
elapsed = time.monotonic() - start
schema_check = {
    "schema": "WU088_HH_PHYS15_WORKFLOW_STATE_SCHEMA_CHECK_V1",
    "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": command, "execution_status": "completed" if run.returncode == 0 else "failed",
    "exit_code": run.returncode, "wall_seconds": elapsed,
    "environment": {"python": platform.python_version(), "platform": platform.platform()},
    "state_path": "state/RESEARCH_STATE.json", "state_sha256": sha(after_bytes),
    "state_snapshot": "R1-R9 complete/reused; R10 in_progress; actual delivery ACK pending",
    "checker_sha256": sha(checker.read_bytes()),
    "workflow_path": "evidence/workflow_1_0_0/references/WORKFLOW.json",
    "workflow_sha256": sha((SKILL / "references/WORKFLOW.json").read_bytes()),
    "stdout": run.stdout, "stderr": run.stderr,
    "validation_scope": "structure_and_internal_references",
    "scientific_validity": "not_assessed_by_schema_checker",
    "new_physical_source_evaluations": 0, "new_physical_root_solves": 0, "new_physical_history_runs": 0,
    "supersedes": "state/versions/pre_R9_pdf_closeout/SCHEMA_CHECK.json",
    "supersession_rule": "A later R10 state edit requires a new actual schema check; this receipt binds only the listed state hash.",
}
(STATE / "SCHEMA_CHECK.json").write_bytes(asbytes(schema_check))
create(STATE / "R9_REPORT_CLOSEOUT.json", asbytes({
    "schema": "WU088_HH_PHYS15_R9_REPORT_CLOSEOUT_V1",
    "created_at_utc": now, "before_state_sha256": sha(before_bytes),
    "after_state_sha256": sha(after_bytes), "R9": "complete", "R10": "in_progress",
    "verified_report_files": verified_report_files,
    "existing_R1_R8_stages_unchanged": True, "R2_reuse_identity_snapshot_unchanged": True,
    "existing_scientific_dependency_identities_unchanged": True, "scientific_claims_unchanged": True,
    "existing_scientific_evidence_unchanged": True,
    "proof_report_contract_DAG_mutations": 0, "root_overlay_Markdown_mutations": 0,
    "root_overlay_current_JSON_updates": 2, "historical_objects_unchanged": True,
    "overlay_receipt_before_sha256": sha(overlay_receipt_before),
    "overlay_receipt_after_sha256": sha(overlay_receipt_path.read_bytes()),
    "updated_non_scientific_dependency": "dep_OVERLAY_FINAL",
    "writes_scoped_to": ["state/", "publication_overlay/CURRENT_DEVELOPMENT_PLAN.json",
                        "publication_overlay/RESEARCH_STATE.json", "ROOT_OVERLAY_FINAL.json",
                        "evidence/overlay_versions/report_pending/"],
    "schema_check_exit_code": run.returncode,
    "schema_check_sha256": sha((STATE / "SCHEMA_CHECK.json").read_bytes()),
    "pending": "Actual Git scientific commit and provider acknowledgements from root before R10 closeout.",
}))
assert run.returncode == 0, run.stdout + run.stderr
print(json.dumps({
    "state_sha256": sha(after_bytes),
    "schema_check_sha256": sha((STATE / "SCHEMA_CHECK.json").read_bytes()),
    "R9_closeout_sha256": sha((STATE / "R9_REPORT_CLOSEOUT.json").read_bytes()),
    "R9": "complete", "R10": "in_progress", "schema_status": json.loads(run.stdout)["status"],
    "schema_exit_code": run.returncode, "R2_snapshot_preserved": True,
    "pdf_sha256": sha(pdf_bytes),
    "overlay_receipt_sha256": sha(overlay_receipt_path.read_bytes()),
    "root_JSON_sha256": {rel: sha(data) for rel, data in json_after.items()},
}, ensure_ascii=False, indent=2))
