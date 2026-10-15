"""Source-scoped MD14 Case-A evidence identity: no global EoR admission."""
import argparse,hashlib,json
from pathlib import Path

RLIB_SOURCE="fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67"
FROZEN_SOURCE="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
RLIB_SHA="44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f"
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for blob in iter(lambda:f.read(2**20),b""):h.update(blob)
    return h.hexdigest()
def build(root,binary,rlib,source_only_binary):
    d=json.loads((root/"results/CONTINUOUS_CASEA_RESULTS.json").read_text())
    si=json.loads((root/"SOURCE_METHOD_IDENTITY.json").read_text())
    if d["paired_cases"]!=24 or d["individual_lanes"]!=48:
        raise ValueError("Original actual source cases missing")
    if si["source_function_count"]!=2 or \
       not si["all_two_original_MD14_source_methods_byte_identical"] or \
       si["frozen_full_source_identity_sha256"]!=FROZEN_SOURCE or \
       si["rlib_full_source_identity_sha256"]!=RLIB_SOURCE:
        raise ValueError("Original source method identity mismatch")
    if sha(rlib)!=RLIB_SHA:raise ValueError("Native research rlib not original")
    if d["max_ledger_abs"]["total_energy_error"]>=3e-12:
        raise ValueError("Original source ledger failed")
    c8=json.loads((root/"results/BOUNDARY_2D_ANALYSIS.json").read_text())
    if c8["cases"]!=20 or not c8["all_finite_source_centroids_physically_above_13p6_at_endpoint"] or c8["scientific_admission"]!="SCOPED_SOURCE_ONLY_C8_NUMERICALLY_CHECKED_NOT_FULL_EOR":
        raise ValueError("Native source-only C8 physics contract did not match")
    files=[{"relative_path":str(f.relative_to(root)),"bytes":f.stat().st_size,"sha256":sha(f)}
           for f in sorted(root.rglob("*")) if f.is_file() and
           f.name!="DELIVERY_EVIDENCE_MANIFEST.json" and "__pycache__" not in f.parts
           and f.suffix!=".pyc"]
    return {"schema":"he18.axbi.original_md14_continuous_casea_evidence.v1",
            "status":"SOURCE_SCOPED_EXECUTED_NOT_GLOBAL_EOR_CERTIFIED",
            "actual_native_MD14_source_birth":True,
            "live_owner_original_frozen_epoch_sha256":FROZEN_SOURCE,
            "separate_rlib_source_epoch_sha256":RLIB_SOURCE,
            "original_rlib_binary_sha256":RLIB_SHA,
            "full_native_compilation_identities_equal":False,
            "two_native_MD14_source_methods_byte_equal":True,
            "native_casea_rec_photons":"energy_ESCAPE_ledger_only_no_OTS_spectrum",
            "stellar_emitter_stress_and_baryon_recoil":"NOT_INTEGRATED",
            "native_subagent":"NOT_RUN","local_codex":"NOT_USED",
            "final_research_binary_sha256":sha(binary),
            "source_only_energy_time_binary_sha256":sha(source_only_binary),
            "source_only_energy_time_executed_cases":c8["cases"],
            "source_only_energy_time_evidence_sha256":sha(root/"results/SOURCE_BOUNDARY_2D.csv"),
            "source_only_grid_time_scope":"Numerical lower-energy support artifact; no coupled gas-grid accuracy claim",
            "pairs":d["paired_cases"],"lanes":d["individual_lanes"],
            "max_ledger_abs":d["max_ledger_abs"],
            "files_count":len(files),"files_total_bytes":sum(x["bytes"] for x in files),
            "files":files,"scientific_admission":"HOLD_FULL_EOR_AND_CMB"}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--rlib",type=Path,required=True)
    p.add_argument("--source-only-binary",type=Path,required=True)
    a=p.parse_args()
    r=build(a.root,a.binary,a.rlib,a.source_only_binary)
    (a.root/"DELIVERY_EVIDENCE_MANIFEST.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:r[k] for k in (
      "files_count","files_total_bytes","pairs","lanes","final_research_binary_sha256")},indent=2))
