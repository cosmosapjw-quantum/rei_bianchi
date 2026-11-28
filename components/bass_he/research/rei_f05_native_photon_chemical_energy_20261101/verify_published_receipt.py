#!/usr/bin/env python3
"""Public frozen derived-receipt verifier; does NOT read original private source.
Fails under python -O too (explicit checks instead of assertions).
"""
import csv,hashlib,json,math
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"
KNOWN={
 "NATIVE_REI_T160_FOUR_GROUP_THREE_SPECIES_PHOTOENERGY_12ROWS.csv":"73f1c739ab1ea3d940abca44edacca4a54e94e3a937a25a98b63fd065bd8bfc3",
 "SCIENCE_RESULT.json":"d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8",
 "INDEPENDENT_AUDIT.json":"e2f5f91a3637842facdb587739f2c5a84c2858ac27edf0a7c55f38607a0e28aa",
}
def ck(x,msg):
    if not x:raise ValueError("PUBLISHED_RECEIPT_"+msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def vclose(a,b):
    return math.isclose(float(a),float(b),rel_tol=1e-15,abs_tol=0.0)
def verify(folder=OUT):
    for f,h in KNOWN.items(): ck(sha(folder/f)==h,"HASH_DRIFT_"+f)
    raw=json.loads((folder/"SCIENCE_RESULT.json").read_text())
    audit=json.loads((folder/"INDEPENDENT_AUDIT.json").read_text())
    with (folder/"NATIVE_REI_T160_FOUR_GROUP_THREE_SPECIES_PHOTOENERGY_12ROWS.csv").open() as f:
        rows=list(csv.DictReader(f))
    ck(len(rows)==12,"ROW_COUNT")
    ck(len(raw["native_four_groups"])==4 and len(raw["source_photochannels"])==12,"SOURCE_SHAPE")
    ck(raw["nodes_read"]==46080 and raw["original_accepted_tick"]=="160/131072","ORIGINAL_SHAPE")
    ck(raw["central_DAG"]=="28/88_REPORTED" and raw["BASS_HE_physical_DAG"]=="14/18_REPORTED","DAG_TAMPER")
    ck(raw["canonical_delta"]==0 and raw["production"]=="HOLD" and
       not raw["official_tick161"] and not raw["photon_transport_admitted"],"FALSE_ADMISSION")
    ck(raw["native_G3_photon_current_upper_subnormal"]<1e-320,"HARD_CHANNEL_PROMOTION")
    ck(audit["source_material_energy_rate_pairs_checked"]==12,"INDEPENDENT_AUDIT_ABSENT")
    ck(audit["derived_sha256"]==KNOWN["SCIENCE_RESULT.json"],"AUDIT_INPUT_MISMATCH")
    ck(all(raw["direct_native_overlap"]["species"].values()) and raw["direct_native_overlap"]["heat"],
       "NATIVE_REI_FIELD_OVERLAP_FAILURE")
    ck(raw["three_moment_finite_difference_max_scaled_error"]<1e-7,"MOMENT_JACOBIAN_DIFFERENCE")
    for i,(csvrow,source) in enumerate(zip(rows,raw["source_photochannels"])):
        ck(int(csvrow["group"])==source["group"] and csvrow["species"]==source["species"],
           "CSV_CHANNEL_MISMATCH_"+str(i))
        for p,key in (
          ("rate","photo_events_per_s"),("binding","chemical_binding_power_erg_s"),("heat","primary_heat_power_erg_s")):
            for j,b in enumerate(("lo","hi")):
                ck(vclose(csvrow[f"{p}_{b}_"+("s" if p=="rate" else "erg_s")],source[key][j])
                   or (abs(float(csvrow[f"{p}_{b}_"+("s" if p=="rate" else "erg_s")]))<1e-320
                       and abs(source[key][j])<1e-320),
                   "CSV_CHANNEL_VALUE_"+str(i)+"_"+p)
    ck(raw["total_chemical_binding_power_erg_s"][0]>0,"NO_BINDING")
    ck(raw["total_primary_heat_power_erg_s"][0]>0,"NO_HEAT")
    print("PASS_PUBLISHED_DERIVED_RECEIPT_ONLY_NOT_ORIGINAL_SOURCE_REPLAY")
if __name__=="__main__":verify()
