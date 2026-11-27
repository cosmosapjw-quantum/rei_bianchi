"""One-shot offline verification of the pinned HE-F2C imported evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import jsonschema
from rct_intake import expect, validate, verify_saved, PROFILES

BASE = Path(__file__).resolve().parent
ROOT = next(p for p in BASE.parents if (p / ".git").exists())


def read(name):
    return json.loads((BASE / name).read_text())


def publish(name, value):
    """Create an immutable result atomically; never overwrite an earlier result."""
    fd, temporary = tempfile.mkstemp(prefix=".intake-", dir=BASE)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, BASE / name)
        directory = os.open(BASE, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temporary)


def main():
    inputs, audit, delta = (read(k) for k in ("INPUT_IDENTITY.json", "SOURCE_AUDIT.json", "FETCH_DELTA.json"))
    observed = inputs["observations"] + audit["observations"] + delta["observations"]
    verify_saved(BASE, observed)
    bundle = {}
    for key, name in {
        "return": "publication/he_consumer_return/HE_F2_RCT_CONSUMER_RETURN.json",
        "providers": "publication/PROVIDER_SELECTION_RECORDS.json",
        "final": "evidence/FINAL_INTEGRATION.json", "e2": "evidence/INDEPENDENT_RESULT.json",
        "e2x": "evidence/FT03_INDEPENDENT_RESULT.json", "review": "review/POST_FT03_REVIEW.json",
        "theory": "theory/CONTRACT.json", "cases": "evidence/FT03_INDEPENDENT_CASES.json",
        "kf": "survey/thermal_rate_views/KF96_THERMAL_RATE_PACKET.json",
        "gm": "survey/thermal_rate_views/GM25_THERMAL_RATE_PACKET.json",
    }.items():
        bundle[key] = read("consumer/" + name)
    result = validate(bundle)
    publication = bundle["return"]["publication"]
    for key, value in [("native_commit", publication["immutable_commit"]),
                       ("tree", publication["tree"]), ("parent", publication["parent"]),
                       ("changed_native_paths_since_code", [])]:
        expect(audit[key], value, key)
    expect(audit["publication_head"], inputs["consumer_commit"], "doc head")
    expect(audit["descendant_status"], "ahead", "code ancestry")
    final_sources = {x["sha256"] for x in bundle["final"]["file_identities"] if "/target/" not in x["path"]}
    source_observations = [x for x in audit["observations"] if x.get("expected_sha256")]
    expect(len(source_observations), 8, "source count")
    expect({x["sha256"] for x in source_observations}, final_sources, "published source identities")
    for item in source_observations:
        expect(item["matches_expected"], True, item["path"])
    local_hashes = {x["local_path"].removeprefix("consumer/"): x["sha256"]
                    for x in observed if x.get("local_path")}
    for item in bundle["review"]["reviewed_files"]:
        if item["path"] in local_hashes:
            expect(local_hashes[item["path"]], item["sha256"], "reviewed " + item["path"])
    schema_path = "docs/atomic_reionization_handoff_20261004_v1/common/PROVIDER_CONTRACT.schema.json"
    schema_bytes = (ROOT / schema_path).read_bytes()
    expect(hashlib.sha256(schema_bytes).hexdigest(), bundle["providers"]["validation"]["schema_sha256"], "schema SHA")
    schema = json.loads(schema_bytes)
    jsonschema.Draft202012Validator.check_schema(schema)
    for record in bundle["providers"]["records"]:
        jsonschema.Draft202012Validator(schema).validate(record)
    supplier_pin = bundle["return"]["producer_input"]["code_pin"]
    supplier_base = "research/shared_c64/20261003/EOR_B3_ATOMIC_EXPORT_v1/src/bass_he_atomic_export/"
    for profile, filename in zip(PROFILES, ["_kf96.py", "_rate.py"]):
        path = supplier_base + filename
        pinned = subprocess.check_output(["git", "show", supplier_pin + ":" + path], cwd=ROOT)
        expect(hashlib.sha256(pinned).hexdigest(), profile[-1], "supplier pinned core")
        expect((ROOT / path).read_bytes(), pinned, "supplier current core")
    verification = {"status": "PASS", "scope": "INPUT_AND_RECEIPT_BOUNDARY_ONLY",
        "native_commit": audit["native_commit"], "native_tree": audit["tree"],
        "consumer_document_commit": inputs["consumer_commit"], "supplier_code_pin": supplier_pin,
        "saved_artifacts_verified": len(local_hashes), "published_sources_verified": 8,
        "schema_records_verified": 2, "supplier_core_files_verified": 2,
        "reused_evidence": {"native_tests": 116, "E2_assertions": 12789, "E2X_assertions": 212},
        "scientific_runs_this_intake": 0,
        "historical_fetch_failure": "SOURCE_AUDIT.json contains a guessed CSV path HTTP404; FETCH_DELTA.json records actual published CSV",
        "acceptance": result}
    publish("INTAKE_VERIFICATION.json", verification)
    publish("REACTION_BINDING.json", {"schema": "bass-he.rct-local-binding.v1", **result,
        "reaction_id": "R_CX:He2+_H1s:He+1s_H+", "species_order": ["HI", "HII", "HeI", "HeII", "HeIII", "e"],
        "stoichiometry": [-1, 1, 0, 1, -1, 0], "provider_records": "consumer/publication/PROVIDER_SELECTION_RECORDS.json",
        "provider_selection_owner": "rei_bianchi explicit caller; exactly one profile",
        "density_application_owner": "consumer; proper nHI*nHeIII exactly once",
        "source_scalar_contains_density": False, "native_commit": audit["native_commit"],
        "source_moments_resolved": False, "paired_window_K": [1000, 10000],
        "actual_FT03_guard_K": [30000, 110000], "GM25_actual_FT03": "REJECT_OUTSIDE_DOMAIN"})
    publish("CONSUMER_LEDGER_ACCEPTANCE.json", {"schema": "bass-he.rct-ledger-acceptance.v1", **result,
        "local_RHS_binding_accepted": True, "basis": "pinned final execution, Decimal70 oracles and POST_FT03_REVIEW; identity and contract intake",
        "closure": bundle["return"]["closure"], "free_electron_increment": 0,
        "CountOnly_thermal_solver_admissible": False,
        "tracked_primary_zero_reason": "explicit escape route outside tracked field, not missing source moment",
        "Ebar_provenance": "finite positive caller input; exact value/origin/scenario in external manifest or CSV",
        "synthetic_Ebar_is_atomic_prediction": False,
        "native_116_E2_E2X": "inherited evidence, not re-executed here",
        "HE_F2_global_completed": False, "HE_F3": "WAIT_REI_F09_RESULT",
        "F04_full": False, "physical_source": "HOLD", "HE_FLRW02B_mixed_native": "SEPARATE_PENDING"})
    print(json.dumps(verification, ensure_ascii=False))


if __name__ == "__main__":
    main()
