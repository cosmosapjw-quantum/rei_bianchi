"""Typed SHA256 source/evidence identity and claim policy for native Case-A study."""
import argparse,hashlib,json
from pathlib import Path

ORIGINAL_SOURCE="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
SEPARATE_RLIB_SOURCE="fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67"
SEPARATE_RLIB_SHA="44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""):h.update(b)
    return h.hexdigest()

def build(root,binary,rlib):
    study=json.loads((root/"results/CASE_A_ANALYSIS.json").read_text())
    surfaces=json.loads((root/"SOURCE_RATE_SURFACE_IDENTITY.json").read_text())
    if study["physical_cases"]!=54 or study["individual_lanes"]!=108 or not study["serial_parallel_physics_byte_equal"]:
        raise ValueError("Real executed cold source A/B receipts missing")
    if study["max_residuals"]["optional_full_energy_residual_eV_per_H"]>3e-12:
        raise ValueError("Combined photon-gas global source-energy ledger failed")
    if surfaces["source_function_count"]!=7 or not surfaces["all_seven_tested_function_bodies_equal"]:
        raise ValueError("Original frozen rate and micro RHS method source mismatch")
    if surfaces["frozen_full_source_identity_sha256"]!=ORIGINAL_SOURCE or \
       surfaces["rlib_full_source_identity_sha256"]!=SEPARATE_RLIB_SOURCE:
        raise ValueError("Source epoch mismatch")
    if sha(rlib)!=SEPARATE_RLIB_SHA:raise ValueError("Different original source library")
    files=[]
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name!="DELIVERY_EVIDENCE_MANIFEST.json" and \
          "__pycache__" not in p.parts and p.suffix!=".pyc":
            files.append({"relative_path":str(p.relative_to(root)),
                          "bytes":p.stat().st_size,"sha256":sha(p)})
    return {
        "schema":"he18.axbi.cold_original_grackle_case_a_source_evidence.v1",
        "status":"SOURCE_SCOPED_CASE_A_HHE_CHEMISTRY_THERMAL_NUMERICALLY_CHECKED",
        "original_cold_native_source_epoch_sha256":ORIGINAL_SOURCE,
        "separate_rlib_compiled_source_epoch_sha256":SEPARATE_RLIB_SOURCE,
        "separate_original_rlib_binary_sha256":SEPARATE_RLIB_SHA,
        "original_native_source_and_rlib_whole_epoch_identical":False,
        "source_rate_method_body_count_byte_equal":7,
        "final_experimental_binary_sha256":sha(binary),
        "physical_A_B_pairs":study["physical_cases"],
        "transport_lanes":study["individual_lanes"],
        "full_photo_chem_cmb_escape_energy_ledger_max_abs_eV_per_H":
            study["max_residuals"]["optional_full_energy_residual_eV_per_H"],
        "photo_emissivity_enabled":False,
        "recombination_photon_fate":"Case-A escaping radiation ledger, not coupled OTS or photon stock",
        "gas_source":"Original AxbiProvider::point, native Grackle3.4.1 Case-A CI/RR/DR, thermal CE/freefree/CMB with photo input zero",
        "thermal_expansion":"exact adiabatic half maps; original point h=0 to prevent double count",
        "native_subagents":"NOT_RUN",
        "scientific_admission":"NUMERICALLY_CHECKED_SOURCE_SCOPED_ONLY; GLOBAL_EOR_AND_CMB_HOLD",
        "file_count":len(files),"source_files_total_bytes":sum(x["bytes"] for x in files),
        "files":files
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--rlib",type=Path,required=True)
    a=p.parse_args()
    result=build(a.project,a.binary,a.rlib)
    (a.project/"DELIVERY_EVIDENCE_MANIFEST.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in
      ("file_count","source_files_total_bytes","physical_A_B_pairs","transport_lanes",
       "final_experimental_binary_sha256","full_photo_chem_cmb_escape_energy_ledger_max_abs_eV_per_H")},indent=2))
