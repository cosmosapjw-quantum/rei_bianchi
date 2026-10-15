"""Construct a source-scoped byte manifest for a completed original Rust A/B experiment."""
import argparse,hashlib,json
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(2**20),b""):
            h.update(block)
    return h.hexdigest()

def manifest(project,exe,rlib):
    root=project.resolve()
    files=[{"path":str(p.relative_to(root)),"bytes":p.stat().st_size,
            "sha256":sha(p)} for p in sorted(root.rglob("*"))
            if p.is_file() and p.name!="DELIVERY_EVIDENCE_MANIFEST.json"
            and "__pycache__" not in p.parts and p.suffix!=".pyc"]
    ab=json.loads((root/"results/FROZEN_AB_ANALYSIS.json").read_text())
    atomic=json.loads((root/"results/ATOMIC_SOURCE_SURFACE_IDENTITY.json").read_text())
    perf=json.loads((root/"results/PERFORMANCE.json").read_text())
    if ab["individual_lanes"]!=216 or ab["separate_ab_cases"]!=108:
        raise ValueError("Expected 108 paired and 216 individual native cases")
    if not atomic["all_twelve_tested_function_bodies_equal"]:
        raise ValueError("Atomic and geometry source function mismatch")
    if any(float(x)>3e-15 for x in ab["max_absolute_normalized_ledger_residuals"].values()):
        raise ValueError("Unaccepted original ledger discrepancy")
    return {"schema":"he18.axbi.frozen_hhe_final_evidence_manifest.v1",
        "scientific_status":"FROZEN_GAS_ONLY_IMPLEMENTATION_VERIFIED_GLOBAL_EOR_HOLD",
        "cold_source_epoch_original":atomic["frozen_full_source_identity_sha256"],
        "separately_linked_rlib_source_epoch":atomic["rlib_full_source_identity_sha256"],
        "full_compiled_source_epochs_identical":atomic["full_source_epochs_identical"],
        "source_function_byte_equal_count":atomic["source_function_count"],
        "rlib_sha256":sha(rlib),
        "final_optimized_binary_sha256":sha(exe),
        "original_model_nuclear_species":["HI","HII","HeI","HeII","HeIII"],
        "run_case_count":ab["separate_ab_cases"],
        "individual_transport_arms":ab["individual_lanes"],
        "pairwise_physics_string_identity_uncached_cached_serial_parallel":True,
        "max_normalized_ledger_residuals":ab["max_absolute_normalized_ledger_residuals"],
        "measured_benchmark_wall_seconds":perf["measurements_wall_s"],
        "file_count":len(files),
        "total_file_bytes":sum(r["bytes"] for r in files),
        "files":files,
        "native_ode_global_error_certified":False,
        "parent_rei_bianchi_publication_commit":"2b39b39e0273c20b539c75d92f0d03d64bdb8e2d",
        "next_state":"HHE_AB5: dynamic source-resolved H/He kinetics & thermal ledger",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--rlib",type=Path,required=True)
    args=p.parse_args()
    result=manifest(args.project,args.binary,args.rlib)
    path=args.project/"DELIVERY_EVIDENCE_MANIFEST.json"
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:result[k] for k in
         ("file_count","total_file_bytes","run_case_count",
          "individual_transport_arms","source_function_byte_equal_count",
          "final_optimized_binary_sha256")},indent=2))
