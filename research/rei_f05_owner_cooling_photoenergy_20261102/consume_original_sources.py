#!/usr/bin/env python3
"""Original REI F05 tick160 owner consumption of HE149 and CR162.

A fresh, source-locked derived scalar power comparison. Does NOT evolve the IVP,
replace the owner solver, add H(1s->2p) cooling, or admit canonical tick161.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
import math
from pathlib import Path

HE_CSV_SHA = "73f1c739ab1ea3d940abca44edacca4a54e94e3a937a25a98b63fd065bd8bfc3"
HE_JSON_SHA = "d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8"
CR_CSV_SHA = "0ba8549b289d5d3656afb7957fbc0e585fc6182f070e3ebe839bfc0d24c86e9c"
CR_JSON_SHA = "0ea4e8cb985f018ce35f69fa874638170e7a693d379f61da72935ed381a7a693"
F05_TAR_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
F05_STATE_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ORIGINAL_RHS_SHA = "b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
SPECIES = ("HI", "HeI", "HeII")

def demand(test:bool,message:str)->None:
    if not test: raise ValueError("REI_F05_OWNER_"+message)

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda:f.read(1<<20),b""):h.update(data)
    return h.hexdigest()

def verified_json(p:Path,expected:str)->dict:
    demand(sha(p)==expected,"SOURCE_JSON_SHA_"+p.name)
    return json.loads(p.read_text())

def close(a:float,b:float,r:float=2e-12)->bool:
    return math.isclose(a,b,rel_tol=r,abs_tol=1e-315)

def channel_verify(rows:list[dict],science:dict,owner:dict)->dict:
    demand(len(rows)==12 and len(science["source_photochannels"])==12,"HE_CHANNEL_ROWS")
    demand(science["nodes_read"]==46080 and owner["original_cells"]==46080,"NATIVE_CELL_NUMBER")
    demand(science["original_accepted_tick"]==owner["original_frozen_tick"]=="160/131072","OWNER_TICK")
    demand(science["original_REI_archive_sha256"]==owner["original_REI_tar_sha256"]==F05_TAR_SHA,"SOURCE_TAR")
    demand(science["original_REI_array_sha256"]==owner["original_REI_accepted_state_sha256"]==F05_STATE_SHA,"SOURCE_STATE")
    demand(science["original_REI_RHS_sha256"]==ORIGINAL_RHS_SHA,"SOURCE_RHS")
    demand(owner["source_science_json_sha256"]==HE_JSON_SHA,"REI_PARENT_BUDGET_AUTHORITY")
    demand(owner["original_channels_checked"]==12 and owner["canonical_delta"]==0,"PARENT_OWNER_ADMISSION")
    demand(owner["original_source_times_not_mixed_with_rei_0_to_64"],"CROSS_EPOCH_SCOPE")
    demand(science["native_G3_photon_current_upper_subnormal"]<1e-320,"SOURCE_GROUP3_HARD_PHOTON_LEAK")
    for i,(row,src) in enumerate(zip(rows,science["source_photochannels"])):
        demand(int(row["group"])==src["group"] and row["species"]==src["species"],"CHANNEL_KEY_"+str(i))
        demand(int(row["supported"])==int(src["supported"]),"CHANNEL_SUPPORT_"+str(i))
        for pre,key in (("rate","photo_events_per_s"),("binding","chemical_binding_power_erg_s"),("heat","primary_heat_power_erg_s")):
            unit="s" if pre=="rate" else "erg_s"
            for j,end in enumerate(("lo","hi")):
                value=float(row[f"{pre}_{end}_{unit}"])
                reference=float(src[key][j])
                demand(close(value,reference,4e-15),"CHANNEL_VALUE_"+str(i)+"_"+pre+"_"+end)
    for col,reference in (
        ("consumed_chemical_binding_power_erg_s","total_chemical_binding_power_erg_s"),
        ("consumed_primary_photoelectron_heat_power_erg_s","total_primary_heat_power_erg_s"),
        ("consumed_original_photoevents_per_s","total_original_photoionization_per_s"),
    ):
        demand(all(close(owner[col][k],science[reference][k],2e-15) for k in (0,1)), "PARENT_OWNER_CHANNEL_SUM_"+col)
    return {
        "photo_binding_erg_s":science["total_chemical_binding_power_erg_s"],
        "primary_photoheat_erg_s":science["total_primary_heat_power_erg_s"],
        "original_photoevents_per_s":science["total_original_photoionization_per_s"],
    }

def cooling_verify(rows:list[dict],cr:dict,he:dict)->dict:
    count=int(cr["supported_source_cells"])
    demand(count==12528 and cr["original_source_cells"]==he["nodes_read"]==46080,"CR_DOMAIN_COUNT")
    demand(int(cr["excluded_source_cells"])==46080-count,"CR_EXCLUDED_COUNT")
    demand(cr["temperature_support_K"]==[5000,20000],"CR_SUPPORTED_T")
    demand(cr["original_legacy_rhs_SHA256"]==he["original_REI_RHS_sha256"]==ORIGINAL_RHS_SHA,"CR_RHS_DIFFERENT")
    demand(cr["original_tick160_accepted"] and cr["tick161_preview_unaccepted"],"CR_TICK_ADMISSION")
    demand(cr["legacy_H_exc_in_original_RHS"] and cr["no_new_cooling_term_to_add"] and cr["no_replacement_of_whole_legacy_by_2p"],"CR_DOUBLE_COUNT_OWNER")
    demand(cr["source_assumptions"]==["Te_equals_gas_T","neutral_f1s_equals_1_saturation","fixed_original_source_state"],"CR_SOURCE_ASSUMPTIONS")
    # Same REI source clock, though the CR source-preview bytes and the HE source-TAR
    # are separately locked archives. This is not byte identity between ZIP formats.
    dt=float(cr["native_tick160_to_161_dt_seconds"])
    t=float(he["native_proper_time_s"])
    demand(math.isclose(160*dt,t,rel_tol=1e-14,abs_tol=1e-3),"ORIGINAL_SOURCE_CLOCK")
    demand(len(rows)==count,"CR_CELL_DATA_COUNT")
    seen=set(); values=[[],[],[]]; decimal_sums=[Decimal(0),Decimal(0),Decimal(0)]
    robust01=0;robust1=0;mx=0.0
    for row in rows:
        i=int(row["node"])
        demand(0<=i<46080 and i not in seen,"CR_DUPLICATE_OR_NODE_DOMAIN")
        seen.add(i)
        fields=[row["legacy_exc_erg_s_mid"],row["two_p_exc_erg_s_mid"],row["other_exc_residual_erg_s_mid"]]
        nums=[float(v) for v in fields]
        demand(all(math.isfinite(x) and x>0 for x in nums),"CR_NONPOSITIVE_PARTITION")
        demand(close(nums[0],nums[1]+nums[2],2e-13),"CR_PARTITION_NOT_CONSERVATIVE")
        frac=float(row["two_p_over_legacy_mid"])
        demand(0<frac<1 and close(frac,nums[1]/nums[0],3e-13),"CR_FRACTION_NOT_SOURCED")
        robust01+=int(row["two_p_over_native_robust_gt_0p1"])
        robust1+=int(row["two_p_over_native_robust_gt_1"])
        for j,(value,fv) in enumerate(zip(fields,nums)):
            values[j].append(fv)
            decimal_sums[j]+=Decimal(value)
        mx=max(mx,abs(nums[0]-(nums[1]+nums[2]))/nums[0])
    totals=[math.fsum(v) for v in values]
    with localcontext() as ctx:
        ctx.prec=65
        exact=[float(x) for x in decimal_sums]
    demand(all(close(totals[k],exact[k],5e-15) for k in range(3)),"CR_INDEPENDENT_DECIMAL_TOTAL")
    for j,key in enumerate(("legacy_H_exc_erg_per_s","two_p_exc_erg_per_s","other_H_exc_residual_erg_per_s")):
        demand(close(totals[j],cr["aggregates"][key],3e-12),"CR_AGGREGATE_"+key)
    demand(robust01==cr["epsilon_two_p_ROBUST_vs_original_native_preview_abs_gt_0p1_count"],"CR_PREVIEW_01_COUNTER")
    demand(robust1==cr["epsilon_two_p_ROBUST_vs_original_native_preview_abs_gt_one_count"],"CR_PREVIEW_1_COUNTER")
    demand(close(totals[1]/totals[0],cr["two_p_fraction_of_legacy_integrated"]),"CR_SOURCE_FRACTION")
    return {
        "original_legacy_excitation_mid_erg_s":totals[0],
        "two_p_component_mid_erg_s":totals[1],
        "positive_phenomenological_remnant_mid_erg_s":totals[2],
        "two_p_fraction_of_legacy":totals[1]/totals[0],
        "max_cell_relative_partition_residual":mx,
        "native_preview_nonadmission_flags":{"eps2p_above_0p1_times_preview_max":robust01,"eps2p_above_preview_max":robust1},
        "native_source_clock_t160_s":t,
        "used_original_source_cells":count,
    }

def consume(hecsv:Path,hejson:Path,crcsv:Path,crjson:Path,ownerjson:Path)->dict:
    demand(sha(hecsv)==HE_CSV_SHA,"HE_CSV_SOURCE_SHA")
    demand(sha(crcsv)==CR_CSV_SHA,"CR_CSV_SOURCE_SHA")
    he=verified_json(hejson,HE_JSON_SHA)
    cr=verified_json(crjson,CR_JSON_SHA)
    owner=json.loads(ownerjson.read_text())
    with hecsv.open(newline="") as f: he_rows=list(csv.DictReader(f))
    with gzip.open(crcsv,"rt",newline="") as f: cr_rows=list(csv.DictReader(f))
    h=channel_verify(he_rows,he,owner)
    c=cooling_verify(cr_rows,cr,he)
    heating=h["primary_photoheat_erg_s"]
    legacy=c["original_legacy_excitation_mid_erg_s"]
    p2=c["two_p_component_mid_erg_s"]
    binding=h["photo_binding_erg_s"]
    demand(0<heating[0]<=heating[1] and binding[0]>0,"HE_POWER_CONE")
    demand(legacy>heating[1],"PHYSICAL_SELECTED_CHANNEL_SIGN")
    result={
        "schema":"REI_F05_OWNER_FROZEN_T160_PRIMARY_HEAT_VS_H_EXCITATION_PARTITION_V1",
        "scientific_scope":"ACTUAL_ORIGINAL_REI_F05_FROZEN_ACCEPTED_T160_SOURCE_CONDITIONAL_ENERGY_RATE_COMPARISON",
        "owner_parent_pr":363,
        "owner_parent_sha":"abf83d4d883d5f311426b7f02cb001e70138ceb4",
        "original_source_archive_sha256":F05_TAR_SHA,
        "original_source_array_sha256":F05_STATE_SHA,
        "original_RHS_sha256":ORIGINAL_RHS_SHA,
        "donor_source_sha256":{"BASS_HE_149_CSV":HE_CSV_SHA,"BASS_HE_149_JSON":HE_JSON_SHA,"BASS_CR_162_CSV":CR_CSV_SHA,"BASS_CR_162_JSON":CR_JSON_SHA},
        "native_original_source_clock_s":c["native_source_clock_t160_s"],
        "original_photon_sources":h,
        "original_cooling_source":c,
        "selected_channel_source_midpoint_inequality":{
            "legacy_excitation_cooling_12528_over_global_primary_photoheat":[legacy/heating[1],legacy/heating[0]],
            "global_primary_photoheat_minus_legacy_supported_excitation_erg_s":[heating[0]-legacy,heating[1]-legacy],
            "two_p_cooling_over_global_primary_photoheat":[p2/heating[1],p2/heating[0]],
            "binding_fraction_of_gross_photo_material_power":[binding[0]/(binding[0]+heating[1]),binding[1]/(binding[1]+heating[0])],
            "numerator_cooling_is_source_midpoint_not_rigorous_interval":True,
            "denominator_photoheat_is_interval_from_frozen_source":True
        },
        "owner_decision":{
            "BASS_HE_149":"ALREADY_ACCEPTED_REI_363_ORIGINAL_F05_T160_GROSS_PHOTOCHANNEL_REUSE_ONLY",
            "BASS_CR_162":"ADMIT_EXISTING_H_EXCITATION_OVERLAP_AND_2P_PARTITION_FOR_SPECIFIED_DIAGNOSTIC_ONLY",
            "native_H_excitation_new_additive_term":"PROHIBITED_DOUBLE_COUNT",
            "native_H_excitation_replace_whole_with_2p":"PROHIBITED_UNASSIGNED_REMAINDER",
            "original_RHS_or_photon_ownership_mutation":"NOT_PERFORMED",
            "native_full_IVP_or_thermal_balance":"NOT_CLAIMED",
            "original_F05_tick161":"NOT_ACCEPTED"
        },
        "validation":{"source_crc_or_SHA":"SHA_CHECKED","he_original_channels":12,"cr_original_supported_nodes":len(cr_rows),"decimal_independent_12528_cell_sum":"CHECKED","same_source_clock":"CHECKED"},
        "dag":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","canonical_delta":0},
        "production":"HOLD",
        "next_critical_physics":"ORIGINAL_REI_F05_V2_WORKER_0_TO_64_RUNTIME_SOURCE_IDENTITY_AND_TICK160_TO_161_ACCEPT_REJECT"
    }
    return result

def main():
    a=argparse.ArgumentParser()
    for opt in ("he-csv","he-json","cr-csv","cr-json","owner-json","output"):
        a.add_argument("--"+opt,required=True,type=Path)
    args=a.parse_args()
    result=consume(args.he_csv,args.he_json,args.cr_csv,args.cr_json,args.owner_json)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PASS_REI_F05_SOURCE_CONDITIONAL_OWNER_ENERGY_COOLING_INTAKE")
    print(json.dumps({"physical_selected_erg_s":result["selected_channel_source_midpoint_inequality"]["global_primary_photoheat_minus_legacy_supported_excitation_erg_s"],"clock":result["native_original_source_clock_s"],"rows":result["validation"],"dag":result["dag"]},sort_keys=True))

if __name__=="__main__":main()
