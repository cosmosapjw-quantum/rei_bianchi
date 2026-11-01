#!/usr/bin/env python3
"""Independent Decimal replay of source-original F05 HE149 × CR162 owner intake.

No import from consume_original_sources.py; checks public source physics from
a second arithmetic path, not independent author/experimental source.
"""
import argparse,csv,gzip,hashlib,json,decimal,math
from pathlib import Path

decimal.getcontext().prec=72
D=decimal.Decimal
BASE="REI_F05_INDEPENDENT_"

def need(ok,code):
    if not ok:raise ValueError(BASE+code)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    for name in ("he-csv","he-json","cr-csv","cr-json","owner-json","result","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    expected={
      a.he_csv:"73f1c739ab1ea3d940abca44edacca4a54e94e3a937a25a98b63fd065bd8bfc3",
      a.he_json:"d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8",
      a.cr_csv:"0ba8549b289d5d3656afb7957fbc0e585fc6182f070e3ebe839bfc0d24c86e9c",
      a.cr_json:"0ea4e8cb985f018ce35f69fa874638170e7a693d379f61da72935ed381a7a693",
    }
    for path,ref in expected.items():need(digest(path)==ref,"DONOR_BYTE_HASH")
    with open(a.he_csv,newline="") as f: hi=list(csv.DictReader(f))
    with gzip.open(a.cr_csv,"rt",newline="") as f:ci=list(csv.DictReader(f))
    with open(a.he_json) as f:h=json.load(f)
    with open(a.cr_json) as f:c=json.load(f)
    with open(a.owner_json) as f:o=json.load(f)
    with open(a.result) as f:r=json.load(f)
    need(len(hi)==12 and len(ci)==12528,"ROW_COUNTS")
    need(r["schema"]=="REI_F05_OWNER_FROZEN_T160_PRIMARY_HEAT_VS_H_EXCITATION_PARTITION_V1","OUTPUT_SCHEMA")
    need(c["original_legacy_rhs_SHA256"]==h["original_REI_RHS_sha256"]==r["original_RHS_sha256"],"SAME_RHS")
    need(h["original_REI_archive_sha256"]==o["original_REI_tar_sha256"]==r["original_source_archive_sha256"],"SAME_ARCHIVE")
    need(h["original_REI_array_sha256"]==o["original_REI_accepted_state_sha256"]==r["original_source_array_sha256"],"SAME_STATE")
    need(abs(float(h["native_proper_time_s"])-160*float(c["native_tick160_to_161_dt_seconds"]))<1e-3,"SAME_CLOCK")
    indexed={(int(t["group"]),t["species"]):t for t in hi}
    need(len(indexed)==12,"HE_UNIQUE_CHANNELS")
    sums=[]
    for pre in ("rate","binding","heat"):
        su=("s" if pre=="rate" else "erg_s")
        sums.append([sum(D(row[pre+"_"+edge+"_"+su]) for row in hi) for edge in ("lo","hi")])
    rates,bind,heat=sums
    need(bind[0]>0 and heat[0]>0 and rates[0]>0,"SOURCE_POSITIVITY")
    for vals,key in ((rates,"total_original_photoionization_per_s"),
                     (bind,"total_chemical_binding_power_erg_s"),
                     (heat,"total_primary_heat_power_erg_s")):
        for j in (0,1):
            target=D(str(h[key][j]))
            need(abs(vals[j]-target)/target< D("4e-14"),"INDEPENDENT_HE_SUM")
    totals=[D(0),D(0),D(0)]
    ids=set()
    k=("legacy_exc_erg_s_mid","two_p_exc_erg_s_mid","other_exc_residual_erg_s_mid")
    for row in ci:
        node=int(row["node"])
        need(node not in ids and 0<=node<46080,"CR_NODE_ID")
        ids.add(node)
        x=[D(row[z]) for z in k]
        need(x[0]>0 and x[1]>0 and x[2]>0,"CR_COOLING_CHANNEL_POSITIVE")
        need(abs(x[0]-x[1]-x[2])/x[0]<D("4e-15"),"CR_NONDOUBLECOUNT_PARTITION")
        for j in range(3):totals[j]+=x[j]
    for j,key in enumerate(("legacy_H_exc_erg_per_s","two_p_exc_erg_per_s","other_H_exc_residual_erg_per_s")):
        val=D(str(c["aggregates"][key]))
        need(abs(totals[j]-val)/val<D("4e-14"),"INDEPENDENT_CR_SUM")
    need(totals[0]>heat[1],"SELECTED_PHYSICAL_NEGATIVE_SIGN")
    ratio_low=totals[0]/heat[1]
    ratio_high=totals[0]/heat[0]
    diff_low=heat[0]-totals[0]
    diff_high=heat[1]-totals[0]
    got=r["selected_channel_source_midpoint_inequality"]
    for val,reported in zip((ratio_low,ratio_high),got["legacy_excitation_cooling_12528_over_global_primary_photoheat"]):
        need(abs(val-D(str(reported)))/val<D("7e-15"),"OWNER_RATIO")
    for val,reported in zip((diff_low,diff_high),got["global_primary_photoheat_minus_legacy_supported_excitation_erg_s"]):
        need(abs(val-D(str(reported)))/abs(val)<D("7e-15"),"OWNER_ENERGY_DIFF")
    need(r["dag"]["canonical_delta"]==0 and r["production"]=="HOLD","FALSE_PRODUCTION_PROMOTION")
    need(r["owner_decision"]["native_H_excitation_new_additive_term"]=="PROHIBITED_DOUBLE_COUNT","SOURCE_DOUBLE_COUNT_TRAP")
    result={
      "schema":"REI_F05_OWNER_CROSSREPO_INDEPENDENT_ARITHMETIC_V1",
      "result":"PASS_SCOPED_ORIGINAL_SOURCE_DERIVED_DATA",
      "independent_12528_row_decimal_sums":list(map(str,totals)),
      "independent_12_channel_decimal_sums":{"rate":list(map(str,rates)),"binding":list(map(str,bind)),"heat":list(map(str,heat))},
      "independent_supported_legacy_to_global_primary_heat":list(map(str,(ratio_low,ratio_high))),
      "independent_primary_heat_minus_supported_legacy_erg_s":list(map(str,(diff_low,diff_high))),
      "verified_source_digest_count":4,
      "science_limit":"CR_LEGACY_POINT_MIDPOINT; NOT GLOBAL_COOLING_INTERVAL; ORIGINAL_F05_PRODUCTION_HOLD",
      "independent_author":"NOT_RUN_SELF_HOSTILE_SEPARATE_CODE_PATH",
      "dag":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","delta":0}
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS_REI_F05_INDEPENDENT_ORIGINAL_SOURCE_DECIMAL_AUDIT")

if __name__=="__main__": main()
