#!/usr/bin/env python3
"""Read-only independent, full-row physical audit of REI F05 tick161 previews.

No native source imports and no acceptance-worker calls. Recomputes electron
identity, positive thermal energy, fraction physical cones, source/provider
identity, step uncertainty overlap, per-lane byte hashes and NPZ packaging.
"""
from pathlib import Path
import argparse,csv,gzip,hashlib,json,math,zipfile

LANES=("primary","recomb","shield")
COLUMNS=("source_H_nuclei_N","source_He_nuclei_N","tick160_xHII",
    "tick161_preview_xHII","tick161_preview_xHeII","tick161_preview_xHeIII",
    "tick160_Tgas_K","tick161_preview_Tgas_K","tick160_electron_count_N",
    "tick161_preview_electron_count_N","tick161_preview_U_erg",
    "tick160_to_161_delta_logT","tick160_to_161_delta_electron_N")
N=46080
KB=1.380649e-16
SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def allowed_diff(a,b,rel=1e-11):
    return max(0.0, a-b) <= rel*max(abs(a),abs(b),1e-300)
def get(row,key):
    a=float(row[key+"_lower"])
    b=float(row[key+"_upper"])
    if not (math.isfinite(a) and math.isfinite(b) and a<=b):
        raise ValueError("NONFINITE_OR_INVERTED:"+key)
    return a,b
def check_row(row,node):
    if int(row["node"])!=node:raise ValueError("BAD_NODE_ORDER")
    nh=get(row,"source_H_nuclei_N");he=get(row,"source_He_nuclei_N")
    oldxh=get(row,"tick160_xHII");xh=get(row,"tick161_preview_xHII")
    xhe2=get(row,"tick161_preview_xHeII");xhe3=get(row,"tick161_preview_xHeIII")
    t0=get(row,"tick160_Tgas_K");t=get(row,"tick161_preview_Tgas_K")
    ne0=get(row,"tick160_electron_count_N");ne=get(row,"tick161_preview_electron_count_N")
    U=get(row,"tick161_preview_U_erg");dz=get(row,"tick160_to_161_delta_logT")
    dne=get(row,"tick160_to_161_delta_electron_N")
    if nh[0]<=0 or he[0]<=0 or t0[0]<=0 or t[0]<=0 or U[0]<=0 or ne[0]<=0:
        raise ValueError("NONPOSITIVE_PHYSICAL_QUANTITY")
    for key,iv in (("xh",xh),("heII",xhe2),("heIII",xhe3),("oldH",oldxh)):
        if iv[0]<-1e-11 or iv[1]>1+1e-11:
            raise ValueError("ION_FRACTION_CONE_"+key)
    if xhe2[0]+xhe3[0]>1+1e-11:
        raise ValueError("HE_NUCLEUS_CONE")
    ne_formula_lo=nh[0]*xh[0]+he[0]*(xhe2[0]+2*xhe3[0])
    ne_formula_hi=nh[1]*xh[1]+he[1]*(xhe2[1]+2*xhe3[1])
    if not (allowed_diff(ne_formula_lo,ne[1]) and allowed_diff(ne[0],ne_formula_hi)):
        raise ValueError("ELECTRON_COUNTS_NOT_COMPATIBLE_WITH_HHE_CHARGE")
    Ulo=1.5*KB*(nh[0]+he[0]+ne[0])*t[0]
    Uhi=1.5*KB*(nh[1]+he[1]+ne[1])*t[1]
    if not (allowed_diff(Ulo,U[1]) and allowed_diff(U[0],Uhi)):
        raise ValueError("GAS_THERMAL_ENERGY_MISMATCH")
    independent_dne=(ne[0]-ne0[1],ne[1]-ne0[0])
    if not (allowed_diff(dne[0],independent_dne[1]) and
            allowed_diff(independent_dne[0],dne[1])):
        raise ValueError("CORRELATED_ELECTRON_DELTA_DISJOINT_FROM_NATIVE_OUTPUT")
    if not (allowed_diff(dz[0],math.log(t[1]/t0[0])) and
            allowed_diff(math.log(t[0]/t0[1]),dz[1])):
        raise ValueError("CORRELATED_THERMAL_DELTA_DISJOINT_FROM_NATIVE_OUTPUT")
    return {"N_e_lower":ne[0],"N_e_upper":ne[1],"U_lower":U[0],"U_upper":U[1],
            "dNe_lower":dne[0],"dNe_upper":dne[1]}
def audit(root):
    root=Path(root).resolve()
    receipts=[]
    for folder in LANES:
        rdir=root/folder
        report=json.loads((rdir/"PREVIEW_RESULT.json").read_text())
        source=json.loads((rdir/"RESULT.json").read_text())
        if report["source_shape_lane"] != {
            "primary":"LOCAL_NEUTRAL_HAZARD_PRIMARY",
            "recomb":"RECOMBINATION_WEIGHTED_AUDITOR",
            "shield":"SCRIPT_SELF_SHIELDING_AUDITOR"}[folder]:
            raise ValueError("ORIGINAL_LANE_MISMATCH")
        assert report["original_source_tar_sha256"]==SOURCE_SHA
        assert report["original_accepted_state_array_sha256"]==STATE_SHA
        assert report["original_kernel_sha256"]==KERNEL_SHA
        assert report["official_state_161"]=="NOT_ACCEPTED_OR_WRITTEN"
        assert report["original_worker_acceptance"]=="UNCHANGED_HISTORICAL_FAILURE"
        assert report["central_DAG"]=="28/88_REPORTED" and report["canonical_delta"]==0
        assert report["production"]=="HOLD" and report["original_owner_modified"] is False
        assert report["actual_original_spatial_cells"]==N
        assert report["candidate_local_defect_upper"]["log_T"]<2e-4
        assert source["original_set_ledgers"]["passed"] and source["original_set_ledgers"]["evaluated_ledgers"]==14
        assert source["original_native_table_event_pass"] and source["original_public_width_pass"]
        assert all(source["steps"][label]["status"]=="PASS"
                   for label in ("full","half1","half2"))
        csv_file=rdir/report["physical_csv_file"]
        if digest(csv_file)!=report["physical_csv_sha256"]:
            raise ValueError("PHYSICAL_CSV_BYTE_IDENTITY_MISMATCH")
        npz=rdir/report["preview_state_file"]
        if digest(npz)!=report["preview_state_sha256"]:
            raise ValueError("PREVIEW_STATE_BYTE_IDENTITY_MISMATCH")
        if npz.read_bytes()[:8]==b"REIADP1\x00":raise ValueError("OFFICIAL_ACCEPTED_STATE_SPOOF")
        with zipfile.ZipFile(npz) as z:
            if z.testzip() is not None:raise ValueError("NPZ_CRC_FAILED")
            keys=sorted(z.namelist())
            if keys!=sorted([k+".npy" for k in ("population_lower","population_upper",
              "log_temperature_lower","log_temperature_upper",
              "parent_log_temperature_lower","parent_log_temperature_upper")]):
                raise ValueError("NONCANONICAL_NPZ_CONTENT")
        totals={key:[] for key in ("N_e_lower","N_e_upper","U_lower","U_upper",
                                   "dNe_lower","dNe_upper")}
        with gzip.open(csv_file,"rt",newline="") as f:
            rows=csv.DictReader(f)
            if rows.fieldnames != ["node"]+[y+suf for y in COLUMNS for suf in ("_lower","_upper")]:
                raise ValueError("PREVIEW_CSV_SCHEMA")
            count=0
            for row in rows:
                x=check_row(row,count)
                for key in totals:totals[key].append(x[key])
                count+=1
        if count!=N:raise ValueError("PREVIEW_CSV_ROW_COUNT")
        vals={key:math.fsum(value) for key,value in totals.items()}
        o=report["observables"]
        for key,field in (("N_e_lower","electron_count_N_lower"),("N_e_upper","electron_count_N_upper"),
              ("U_lower","gas_energy_erg_lower"),("U_upper","gas_energy_erg_upper"),
              ("dNe_lower","delta_electron_N_total_lower"),("dNe_upper","delta_electron_N_total_upper")):
            if not math.isclose(vals[key],o[field],rel_tol=2e-12,abs_tol=0):
                raise ValueError("GLOBAL_PHYSICAL_OBSERVABLES_SUM_MISMATCH:"+field)
        receipts.append({"lane":folder,"rows":count,"fields":len(rows.fieldnames),
           "physical_csv_sha256":digest(csv_file),"preview_npz_sha256":digest(npz),
           "original_14_ledger":"PASS","physical_electron_identity":"PASS",
           "gas_energy_identity":"PASS","positivity":"PASS","no_owner_admission":"PASS"})
    # All three lanes use the same frozen physical parent, so physical outputs
    # should match at least byte-for-byte under the same local environment.
    if len(set(x["physical_csv_sha256"] for x in receipts))!=1:
        raise ValueError("LOCAL_PHYSICAL_LANE_CSV_DIVERGENCE")
    if len(set(x["preview_npz_sha256"] for x in receipts))!=1:
        raise ValueError("LOCAL_PHYSICAL_LANE_PREVIEW_STATE_DIVERGENCE")
    return {"status":"PASS_LOCAL_FULL_ROW_INDEPENDENT_AUDIT","physics_source_datasets":1,
        "source_shape_lanes":3,"nodes":N,"physical_columns":receipts[0]["fields"],
        "lanes":receipts,"central_DAG":"28/88_REPORTED","canonical_delta":0,
        "original_tick161":"NOT_ACCEPTED","production":"HOLD"}
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.root)
    p=args.root/"INDEPENDENT_FULL_ROW_AUDIT.json"
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))