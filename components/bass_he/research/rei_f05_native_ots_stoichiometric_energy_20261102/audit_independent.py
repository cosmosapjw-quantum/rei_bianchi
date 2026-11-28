#!/usr/bin/env python3
"""Second original-rate implementation from physical event channels (stdlib).
Operates only on original-source-generated spatial outputs, independent of
the native solver and its event population RHS implementation.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math
from pathlib import Path
EV=1.602176634e-12
CHI_H=13.598434599702
CHI_HEI=24.587389011
CHI_HEII=54.41776
LYA=0.75*CHI_HEII
P_EXC=0.96
F=0.1
RATE_KEYS=("HI_ION","HEI_ION","HEII_ION","HII_CASE_B","HEII_GROUND","HEII_CASE_B","HEIII_GROUND","HEIII_N2","HEIII_CASCADE")
POWER_KEYS=("Bdot_net_erg_s","OTS_chemical_erg_s","OTS_heat_erg_s","OTS_unresolved_erg_s","OTS_escaped_erg_s")
N=46080
REL=2e-12

def sha(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):d.update(b)
    return d.hexdigest()

def verify(a, b, label):
    if not(math.isfinite(a) and math.isfinite(b)):
        raise ArithmeticError("NONFINITE_ORIGINAL_EVENT_"+label)
    discrepancy=abs(a-b)/max(abs(a),abs(b),1e-160)
    if discrepancy>REL:
        raise ArithmeticError(f"INDEPENDENT_RECOMBINATION_ENERGY_MISMATCH_{label}:{a},{b},{discrepancy}")
    return discrepancy

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True,type=Path)
    ap.add_argument("--science",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    record=json.loads(args.science.read_text())
    if sha(args.data)!=record["derived_46080_csv_sha256"]:raise ValueError("SCIENCE_CSV_SHA_CHANGED")
    if record["source_original_array_sha256"]!="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01":
        raise ValueError("ACCEPTED_ORIGINAL_SOURCE_DRIFT")
    if record["official_tick161"] or record["canonical_delta"]!=0 or record["production"]!="HOLD":
        raise ValueError("FALSE_ORIGINAL_ADMISSION")
    sums={k:[] for k in POWER_KEYS}
    rates={k:[] for k in RATE_KEYS}
    max_diff=0.0
    max_name=None
    original_event_count=0
    with gzip.open(args.data,"rt",newline="") as f:
        rd=csv.DictReader(f)
        required={"cell","original_v","branch_y","branch_z","branch_y2a","branch_y2b",
                  "branch_A_H","branch_A_HeI"} | set(POWER_KEYS) | {"rate_"+k for k in RATE_KEYS}
        if not required.issubset(set(rd.fieldnames or [])):raise ValueError("MISSING_SOURCE_EVENT_COLUMNS")
        for idx,row in enumerate(rd):
            if idx>=N or int(row["cell"])!=idx:raise ValueError("NATIVE_CELL_ORDER_CHANGED")
            def v(key):return float(row[key])
            r={k:v("rate_"+k) for k in RATE_KEYS}
            for name,value in r.items():
                if not math.isfinite(value) or value<-1e-100:raise ValueError("NEGATIVE_EVENT_"+name)
                rates[name].append(value)
            y=v("branch_y");z=v("branch_z");p2a=v("branch_y2a");p2b=v("branch_y2b")
            ah=v("branch_A_H");ae=v("branch_A_HeI");V=v("original_v")
            if any(x<-1e-12 or x>1+1e-12 for x in (y,z,p2a,p2b,ah,ae,V)):
                raise ValueError("INVALID_NATIVE_OTS_BRANCH_DOMAIN")
            ph=1.0-p2a-p2b
            # Independent reconstruction from original nine 26-event rates.
            dHII=(r["HI_ION"]+r["HEII_GROUND"]*y+r["HEII_CASE_B"]*P_EXC+
                  r["HEIII_GROUND"]*ph+r["HEIII_N2"]+r["HEIII_CASCADE"]*ah-
                  r["HII_CASE_B"])
            dHeIII=(r["HEII_ION"]+r["HEIII_GROUND"]*p2a-r["HEIII_GROUND"]-
                    r["HEIII_N2"]-r["HEIII_CASCADE"])
            dHeII=(r["HEI_ION"]+r["HEII_GROUND"]*(1-y)+r["HEIII_GROUND"]*p2b+
                   r["HEIII_CASCADE"]*ae+r["HEIII_GROUND"]+r["HEIII_N2"]+
                   r["HEIII_CASCADE"]-r["HEII_GROUND"]-r["HEII_CASE_B"]-
                   r["HEII_ION"]-r["HEIII_GROUND"]*p2a)
            B=EV*(CHI_H*dHII+CHI_HEI*(dHeII+dHeIII)+CHI_HEII*dHeIII)
            chem=EV*(-CHI_H*r["HII_CASE_B"]+
              r["HEII_GROUND"]*(-CHI_HEI+y*CHI_H+(1-y)*CHI_HEI)+
              r["HEII_CASE_B"]*(-CHI_HEI+P_EXC*CHI_H)+
              r["HEIII_GROUND"]*(-CHI_HEII+ph*CHI_H+p2b*CHI_HEI+p2a*CHI_HEII)+
              r["HEIII_N2"]*(-CHI_HEII+CHI_H)+
              r["HEIII_CASCADE"]*(-CHI_HEII+ah*CHI_H+ae*CHI_HEI))
            qots=r["HEIII_CASCADE"]*(1-V)*F*(z*(LYA-CHI_H)+(1-z)*(LYA-CHI_HEI))*EV
            esc=r["HEIII_CASCADE"]*(1-V)*(1-F)*LYA*EV
            unres=-chem-qots-esc
            predicted=(B,chem,qots,unres,esc)
            for key,pred in zip(POWER_KEYS,predicted):
                orig=v(key)
                err=verify(pred,orig,key+"_"+str(idx))
                if err>max_diff:max_diff=err;max_name=key
                sums[key].append(orig)
            original_event_count+=1
    if original_event_count!=N:raise ValueError("NOT_ALL_NATIVE_46080_CELLS_EVALUATED")
    totals={k:math.fsum(values) for k,values in sums.items()}
    rate_totals={k:math.fsum(values) for k,values in rates.items()}
    expected=record["result"]["physical_energy_powers"]
    refmap={"Bdot_net_erg_s":"Bdot_net_erg_s",
      "OTS_chemical_erg_s":"OTS_chemical_rate_erg_s",
      "OTS_heat_erg_s":"OTS_resolved_heat_erg_s",
      "OTS_unresolved_erg_s":"OTS_unresolved_residual_erg_s",
      "OTS_escaped_erg_s":"OTS_escaped_erg_s"}
    for k,orig in refmap.items():verify(totals[k],float(expected[orig]),"GLOBAL_"+k)
    for k,orig in rate_totals.items():
        verify(orig,record["result"]["original_reaction_rate"]["original_9_event_fluxes_per_s"][k],"GLOBAL_RATE_"+k)
    data={"schema":"BASS_HE_NATIVE_OTS_26EVENT_INDEPENDENT_STOICHIOMETRY_AUDIT_V1",
          "source_csv_sha256":sha(args.data),"source_json_sha256":sha(args.science),
          "verified_source_cells":original_event_count,
          "independent_original_event_rate_columns":9,
          "independent_stoichiometric_energy_channels":5,
          "source_reconstruction":"STDLIB_DIFFERENT_EQUATION_IMPLEMENTATION_SAME_AUTHOR",
          "max_scaled_per_cell_reconstruction_error":max_diff,
          "worst_channel":max_name,
          "global_power_erg_s":totals,"global_event_rates_per_s":rate_totals,
          "native_original_OTS_photon_spectrum":"UNRESOLVED_NOT_PROMOTED",
          "canonical_delta":0,"production":"HOLD","independent_external_referee":"NOT_RUN",
          "result":"PASS_SCOPED_ALL_46080_REAL_ORIGINAL_EVENTS"}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":data["result"],"source_cells":N,
      "max_scaled_error":max_diff,"source_csv_sha256":data["source_csv_sha256"],
      "audit_sha256":sha(args.out)},sort_keys=True))
if __name__=="__main__":main()
