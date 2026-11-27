"""Read-only shared-reference HE29 temperature decomposition.

Only admitted, same-cohort returns supply Radau/DOP853 reference candidates.
The archived HE28 audit is copied as existing evidence. Its old time and mixed
differences are never recomputed here. No integration or native owner is called.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import sys

from linear_budget import LinearForm, exact, project, rational_record
import partial_returns as returns
from reference_contract import OWNER, JOBS, THREADS, same_model

LANE = Path(__file__).resolve().parents[1]
HE29 = LANE.parent
AUDIT_SHA256 = "2bcd94edde08854599597ea8b962683a86cb5ca4af1ad0e1c3bec09b9e3c20cc"
AUDIT_PATH = LANE / "evidence/reused/NATIVE_RETURN_AUDIT.json"
STUDY_ROOT = HE29 / "inputs/study"
METHODS = ("Radau", "DOP853")
CONTRASTS = (("strip", (2, 512), (4, 512)),
             ("strip", (4, 512), (8, 512)),
             ("table", (4, 512), (4, 1024)))
SKILL_CONTEXT = {
    "name": "physmath-research-loop", "version": "1.3.0", "selected_stages": ["C5", "C6"],
    "package_path": "/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop",
    "read": ["SKILL.md", "references/CODING_LOOP.md", "references/POLICY_INTEGRATION.md",
             "references/SUBAGENT_MODE.md"],
    "boundary": "delegated integration and its new manufactured checks only; no recursive review",
}


def case_key(r, nodes):
    return f"m8_r{r}_table{nodes}"


def transport_key(r, n):
    return f"m8_r{r}_n{n}"


def _issue(exc, context, *, missing=False):
    return {"kind": "MISSING" if missing else "INVALID", "context": context,
            "type": type(exc).__name__, "message": str(exc)}


def _input_manifest():
    return returns._pinned_json(HE29 / "provenance/INPUT_SHA256.json", returns.INPUT_MANIFEST_SHA)


def load_transport(study_root=STUDY_ROOT):
    """Read/hash the original 18 saved study JSON files; no old audit execution."""
    study_root = Path(study_root)
    rows, issues = [], []
    try:
        manifest = _input_manifest()
    except Exception as exc:
        return {"cases": [], "errors": [_issue(exc, "fixed INPUT_SHA256.json")],
                "manifest_sha256": returns.INPUT_MANIFEST_SHA, "expected_files": 18,
                "files_matched": 0, "old_audit_recomputations": 0}
    matched = 0
    for r in (2, 4, 8):
        for n in (32, 64):
            key = transport_key(r, n)
            data, files, errors = {}, {}, []
            for name in ("IDENTITY.json", "RESULT.json", "TABLE.json"):
                path = study_root / key / name
                relative = f"inputs/study/{key}/{name}"
                try:
                    if path.is_symlink() or not path.is_file():
                        if not path.exists():
                            raise FileNotFoundError(relative)
                        raise ValueError("HE29_TRANSPORT_REGULAR_FILE_REQUIRED")
                    observed = returns.digest(path)
                    files[name] = {"input_manifest_key": relative, "bytes": path.stat().st_size,
                                   "sha256": observed, "expected_sha256": manifest[relative]}
                    if observed != manifest[relative]:
                        raise ValueError("HE29_TRANSPORT_INPUT_HASH_MISMATCH: " + relative)
                    data[name] = returns.read_json(path)
                    matched += 1
                except Exception as exc:
                    errors.append(_issue(exc, relative, missing=isinstance(exc, FileNotFoundError)))
            row = {"key": key, "r": r, "n": n, "status": "MISSING", "validated": False,
                   "files": files, "errors": errors}
            if len(data) == 3:
                try:
                    identity, result, table = (data[k] for k in ("IDENTITY.json", "RESULT.json", "TABLE.json"))
                    if result.get("status") != "SCOPED_NATIVE_COMPLETED":
                        raise ValueError("HE29_TRANSPORT_COMPLETION_STATUS")
                    if identity.get("n") != n or identity.get("source_table_nodes") != 512:
                        raise ValueError("HE29_TRANSPORT_TIME_OR_TABLE_NODES")
                    table_sha = table.get("source_table_sha256")
                    same_model({**identity["spec"], "source_table_nodes": identity["source_table_nodes"],
                                "table": table_sha},
                               {"m": 8, "angles": 4, "q": 0., "strips": r,
                                "source_table_nodes": 512, "table": result.get("source_table_sha256")})
                    if identity.get("owner_source") != OWNER or identity.get("numerical_thread_environment") != THREADS:
                        raise ValueError("HE29_TRANSPORT_OWNER_OR_THREADS")
                    physical = result["results"]["transport"]
                    if physical.get("metadata", {}).get("n") != n:
                        raise ValueError("HE29_TRANSPORT_METHOD_TIME_INDEX")
                    exact(physical["temperature_K"])
                    row.update(status="VALID", validated=True, identity=identity, result=physical,
                               table=table, table_sha256=table_sha, temperature_K=physical["temperature_K"],
                               admission_evidence="reused pinned HE28 SCOPED_NATIVE_COMPLETED record")
                except Exception as exc:
                    errors.append(_issue(exc, key))
            if errors:
                row["status"] = "INVALID" if any(e["kind"] == "INVALID" for e in errors) else "MISSING"
                row["validated"] = False
            rows.append(row)
            issues.extend(errors)
    return {"cases": rows, "errors": issues, "manifest_sha256": returns.INPUT_MANIFEST_SHA,
            "expected_files": 18, "files_matched": matched,
            "old_audit_recomputations": 0, "old_native_or_solver_calls": 0}


def load_audit(path=AUDIT_PATH):
    """Preserve the exact already published audit bytes and parsed data."""
    path = Path(path)
    raw = path.read_bytes()
    observed = hashlib.sha256(raw).hexdigest()
    if observed != AUDIT_SHA256:
        raise ValueError("HE29_REUSED_AUDIT_HASH_MISMATCH")
    data = returns.read_json(path)
    return {"status": "REUSED_BYTES_VERIFIED", "sha256": observed, "bytes": len(raw),
            "raw_json_utf8": raw.decode("utf-8"), "data": data,
            "original_archive": "BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz",
            "activity": "old audit bytes copied; old time/mixed values not recalculated"}


def _reference_key(case):
    return case["cohort_id"] + ":" + case["key"]


def _projection(form, candidates):
    record = project(form, candidates)
    selected = {key: candidates[key]["Radau"] for key, _ in form.terms}
    record["primary_Radau_value"] = rational_record(form.evaluate(selected))
    return record


def _matched_transport(reference, stored):
    if stored is None or not stored.get("validated") or stored.get("status") != "VALID":
        raise ValueError("HE29_MATCHING_TRANSPORT_NOT_VALIDATED")
    old, new = stored["identity"], reference["identity"]
    if old.get("owner_source") != new.get("owner_source") or old.get("owner_source") != OWNER:
        raise ValueError("HE29_REFERENCE_TRANSPORT_OWNER_MISMATCH")
    if old.get("numerical_thread_environment") != new.get("numerical_thread_environment") or old.get("numerical_thread_environment") != THREADS:
        raise ValueError("HE29_REFERENCE_TRANSPORT_THREAD_MISMATCH")
    same_model({**old["spec"], "source_table_nodes": old["source_table_nodes"],
                "table": stored["table_sha256"]},
               {"m": new["m"], "angles": new["angles"], "q": new["q"], "strips": new["r"],
                "source_table_nodes": new["table_nodes"],
                "table": reference["table"]["source_table_sha256"]})
    old_sources = dict(old.get("parent_sources", {}))
    old_sources.update({"research/he28_strip_refinement_20261018/" + k: v
                        for k, v in old.get("he28_sources", {}).items()})
    new_sources = new.get("parent_sources", {})
    if not new_sources or any(old_sources.get(k) != v for k, v in new_sources.items()):
        raise ValueError("HE29_REFERENCE_TRANSPORT_PHYSICAL_SOURCE_MISMATCH")
    return exact(stored["temperature_K"]), {
        "model_table_owner_threads_match": True,
        "matched_parent_source_files": len(new_sources),
        "transport_binary_sha256": old.get("binary_sha256"),
        "reference_binary_sha256": new.get("binary_sha256"),
        "binary_byte_identity": old.get("binary_sha256") == new.get("binary_sha256"),
        "whole_native_runtime_equivalence": "HOLD",
        "transport_input_files": copy.deepcopy(stored["files"])}


def build_budget(classified, transport, audit):
    """Pure affine reduction; the CLI supplies strictly validated input records.

    Saved transport values are individually converted to exact rationals only
    in rows conditioned on an admitted reference. The old audit is opaque here.
    """
    errors = copy.deepcopy(transport.get("errors", []))
    if audit.get("status") != "REUSED_BYTES_VERIFIED":
        errors.extend(copy.deepcopy(audit.get("errors", [_issue(ValueError("HE29_REUSED_AUDIT_UNAVAILABLE"), "audit")])))
    cases = {row["key"]: row for row in classified.get("cases", [])}
    expected = [case_key(r, nodes) for r, nodes in JOBS]
    candidates, accepted = {}, {}
    for key in expected:
        case = cases.get(key)
        if case is None or not case.get("admitted"):
            continue
        try:
            if not isinstance(case.get("cohort_id"), str) or not case["cohort_id"]:
                raise ValueError("HE29_BUDGET_REFERENCE_COHORT_REQUIRED")
            values = {method: exact(case["results"][method]["temperature_K"]) for method in METHODS}
            candidates[_reference_key(case)] = values
            accepted[key] = case
        except Exception as exc:
            errors.append(_issue(exc, key))
    stored = {(row["r"], row["n"]): row for row in transport.get("cases", [])}
    residuals, held_residuals, matching, residual_forms = [], [], {}, {}
    for key, case in accepted.items():
        if case["table_nodes"] != 512:
            continue
        for n in (32, 64):
            row = stored.get((case["r"], n))
            try:
                temperature, provenance = _matched_transport(case, row)
                form = LinearForm(temperature) - LinearForm.reference(_reference_key(case))
                residual_forms[key, n] = form
                matching[key, n] = (temperature, provenance)
                residuals.append({"case": key, "cohort_id": case["cohort_id"], "r": case["r"], "n": n,
                    "reference_key": _reference_key(case), "units": "K", "formula": "T_transport(r,n)-theta(r,512)",
                    "interpretation": "signed reference-conditioned transport residual",
                    "transport_temperature": rational_record(temperature),
                    "projection": _projection(form, candidates), "provenance": provenance,
                    "true_solution_error_radius": False})
            except Exception as exc:
                missing = row is None or row.get("status") == "MISSING"
                issue = _issue(exc, f"{key}/n{n}", missing=missing)
                held_residuals.append({"case": key, "n": n, "status": "HOLD", "reason": issue})
                if not missing:
                    errors.append(issue)
    contrasts, held_contrasts = [], []
    for axis, left, right in CONTRASTS:
        a, b = case_key(*left), case_key(*right)
        label = {"axis": axis, "from_case": a, "to_case": b, "units": "K"}
        absent = [key for key in (a, b) if key not in accepted]
        if absent:
            held_contrasts.append({**label, "status": "HOLD_MISSING_ADMITTED_REFERENCE", "missing_cases": absent})
            continue
        ca, cb = accepted[a], accepted[b]
        if ca["cohort_id"] != cb["cohort_id"]:
            held_contrasts.append({**label, "status": "HOLD_COHORT_MISMATCH",
                                  "cohorts": {a: ca["cohort_id"], b: cb["cohort_id"]}})
            continue
        try:
            theta_a = LinearForm.reference(_reference_key(ca))
            theta_b = LinearForm.reference(_reference_key(cb))
            reference = theta_b - theta_a
            row = {**label, "status": "AVAILABLE", "cohort_id": ca["cohort_id"],
                   "projection": _projection(reference, candidates),
                   "true_solution_error_radius": False, "decompositions": [], "decomposition_holds": []}
            if axis == "strip":
                for n in (32, 64):
                    if (a, n) not in residual_forms or (b, n) not in residual_forms:
                        row["decomposition_holds"].append({"n": n, "status": "HOLD_MATCHING_TRANSPORT_REQUIRED"})
                        continue
                    ta, tb = matching[a, n][0], matching[b, n][0]
                    observed = LinearForm(tb) - LinearForm(ta)
                    temporal = residual_forms[b, n] - residual_forms[a, n]
                    assembled = reference + temporal
                    closure = assembled - observed
                    if closure.constant != 0 or closure.terms:
                        raise ArithmeticError("HE29_SHARED_REFERENCE_AFFINE_CLOSURE_NOT_ZERO")
                    row["decompositions"].append({"n": n,
                        "formula": "T_b,n-T_a,n=(theta_b-theta_a)+(T_b,n-theta_b)-(T_a,n-theta_a)",
                        "observed_transport_delta": _projection(observed, candidates),
                        "reference_difference": _projection(reference, candidates),
                        "signed_temporal_residual_difference": _projection(temporal, candidates),
                        "assembled_difference": _projection(assembled, candidates),
                        "closure": _projection(closure, candidates), "closure_exact_zero": True,
                        "same_theta_occurrences_merged_before_hull": True})
            contrasts.append(row)
        except Exception as exc:
            errors.append(_issue(exc, a + " -> " + b))
            held_contrasts.append({**label, "status": "INVALID", "reason": str(exc)})
    missing_cases = [key for key in expected if key not in accepted]
    invalid_return = bool(classified.get("global_errors")) or any(
        case.get("status") == "INVALID" for case in cases.values())
    invalid = invalid_return or any(error["kind"] == "INVALID" for error in errors)
    complete = (not invalid and len(accepted) == 4 and len(contrasts) == 3 and not held_contrasts
                and len(residuals) == 6 and not held_residuals and audit.get("status") == "REUSED_BYTES_VERIFIED")
    status = "INVALID_WITH_VALID_SUBSET_PRESERVED" if invalid else "COMPLETE_CONDITIONAL_FINITE_CANDIDATE_ANALYSIS" if complete else "HOLD_MISSING_REFERENCE_OR_INPUT_OR_COHORT"
    return {"schema": "he29.reference.conditioned_budget.v1", "status": status,
        "exit_code": 2 if invalid else 0 if complete else 1,
        "complete": complete, "admitted_reference_pairs": len(accepted), "expected_reference_pairs": 4,
        "missing_cases": missing_cases, "signed_residuals": residuals, "held_residuals": held_residuals,
        "contrasts": contrasts, "held_contrasts": held_contrasts,
        "reference_dependent_rows": len(residuals) + len(contrasts), "errors": errors,
        "reference_candidates": {key: {method: rational_record(value) for method, value in row.items()}
                                 for key, row in candidates.items()},
        "reference_choice_rule": {"primary_method": "Radau", "alternative_method": "DOP853",
            "shared_variable": "exact cohort_id plus declared case/table key",
            "product_hull": "independent finite method choices per distinct surviving reference key",
            "coherent_hull": "one common method label across all surviving reference keys",
            "interpretation": "ranges of stored finite candidates; no true-solution error radius"},
        "classification": copy.deepcopy(classified),
        "performance": [{"case": case["key"], "status": case.get("status"),
                          "admitted": case.get("admitted", False),
                          "recorded_metrics": copy.deepcopy(case.get("performance", {}))}
                         for case in classified.get("cases", [])],
        "performance_reduction": "existing timing scopes copied; no speedup computed",
        "transport_input": {"manifest_sha256": transport.get("manifest_sha256"),
            "expected_files": transport.get("expected_files", 18), "files_matched": transport.get("files_matched", 0),
            "cases": [{key: copy.deepcopy(row[key]) for key in ("key", "r", "n", "status", "validated", "files", "errors") if key in row}
                      for row in transport.get("cases", [])]},
        "reused_audit": copy.deepcopy(audit), "baseline_code_revision": returns.BASELINE_CODE,
        "solver_calls_this_analysis": 0, "native_owner_calls_this_analysis": 0,
        "new_solver_results_created": 0, "old_audit_recomputations": 0,
        "true_solution_error_radius": False,
        "hold": ["continuous spectrum", "global gas-temperature error bound", "full EoR",
                 "upstream Grackle whole-runtime equivalence", "observational Bianchi/CMB",
                 "strip-by-table interaction outside the four declared pairs"],
        "skill_context_used": copy.deepcopy(SKILL_CONTEXT)}


def analyze(root, *, binary=None, data_root=None, study_root=None):
    if study_root is None:
        study_root = (Path(data_root) / "inputs/study") if data_root is not None else STUDY_ROOT
    classified = returns.classify_campaign(root, binary=binary, data_root=data_root)
    transport = load_transport(study_root)
    try:
        audit = load_audit()
    except Exception as exc:
        audit = {"status": "UNAVAILABLE", "errors": [_issue(exc, "saved NATIVE_RETURN_AUDIT.json")],
                 "old_audit_recomputations": 0}
    return build_budget(classified, transport, audit)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="original four-case reference campaign")
    parser.add_argument("--out", required=True, help="fresh create-only budget JSON")
    parser.add_argument("--binary", help="optional returned owner binary bytes")
    parser.add_argument("--data-root", help="existing baseline HE29 DATA root; code/manifests remain in Git")
    parser.add_argument("--study-root", help="saved study DATA; default data-root/inputs/study or this HE29 inputs/study")
    args = parser.parse_args(argv)
    if Path(args.out).exists() or Path(args.out).is_symlink():
        parser.error("output must be a new immutable file")
    result = analyze(args.root, binary=args.binary, data_root=args.data_root, study_root=args.study_root)
    returns._write_json(args.out, result)
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
