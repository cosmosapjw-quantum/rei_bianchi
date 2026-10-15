"""Durable source byte identities for completed dynamic H/He A/B experiment."""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_ORIGINAL="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
SOURCE_RLIB="fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(2**20),b""):h.update(part)
    return h.hexdigest()

def build(root,bin_path,rlib):
    analysis=json.loads((root/"results/DYNAMIC_HHE_ANALYSIS.json").read_text())
    attest=json.loads((root/"results/ATOMIC_SOURCE_SURFACE_IDENTITY.json").read_text())
    if analysis["cases"]!=81 or analysis["lane_records"]!=162 or \
       analysis["scientific_admission"]!="HOLD_FULL_EOR_NATIVE":
        raise ValueError("Dynamic source evidence scope mismatch")
    if not attest["all_twelve_tested_function_bodies_equal"] or \
       attest["source_function_count"]!=12 or \
       attest["frozen_full_source_identity_sha256"]!=SOURCE_ORIGINAL or \
       attest["rlib_full_source_identity_sha256"]!=SOURCE_RLIB:
        raise ValueError("Atomic/transport historical source identity mismatch")
    expected="44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f"
    if sha(rlib)!=expected:raise ValueError("Native rlib changed")
    files=[]
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name!="DELIVERY_EVIDENCE_MANIFEST.json" and \
           "__pycache__" not in p.parts and p.suffix!=".pyc":
            files.append({"relative_path":str(p.relative_to(root)),
                          "bytes":p.stat().st_size,
                          "sha256":sha(p)})
    return {
        "schema":"he18.axbi.dynamic_photo_only_c5_evidence.v1",
        "source_model":"original cold rei_bianchi separately linked Rust rlib",
        "original_frozen_native_source_sha256":SOURCE_ORIGINAL,
        "separate_rlib_source_sha256":SOURCE_RLIB,
        "separate_rlib_binary_sha256":expected,
        "full_compiled_source_epochs_identical":False,
        "test_passed_atomic_transport_source_function_count":12,
        "final_rust_binary_sha256":sha(bin_path),
        "gas_ode_photoionization_only":True,
        "original_full_eor_native_replayed":False,
        "n_physical_cases":81,"n_photon_transport_records":162,
        "serial_parallel_bitwise_equal_physics":True,
        "n_files":len(files),"source_file_bytes":sum(x["bytes"] for x in files),
        "files":files,
        "scientific_admission":"C5_IMPLEMENTATION_VERIFIED_SOURCE_SCOPED; GLOBAL_EOR_HOLD",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--rlib",type=Path,required=True)
    a=p.parse_args()
    info=build(a.project,a.binary,a.rlib)
    dest=a.project/"DELIVERY_EVIDENCE_MANIFEST.json"
    dest.write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps({k:info[k] for k in ("n_physical_cases","n_photon_transport_records","n_files","source_file_bytes","final_rust_binary_sha256")},indent=2))
