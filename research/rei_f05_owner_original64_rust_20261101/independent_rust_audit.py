#!/usr/bin/env python3
"""Independent stdlib hostile 46,080-row physical conservation audit, source-private read."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
H=13.598434599702; HEI=24.587389011; HEII=54.417760
EV=1.602176634e-12; KB=1.380649e-16
def digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def nearly(a,b,rtol=5e-13):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=rtol*max(abs(a),abs(b),1e-290)
def run(source,rust,rust_json,source_summary,out):
    summ=json.loads(Path(source_summary).read_text())
    rustsum=json.loads(Path(rust_json).read_text())
    assert summ["byte_equal_to_historical"] is True
    assert summ["recomputed_14_ledgers_include_zero"] is True
    assert summ["table_event_count"]==0
    assert len(summ["recomputed_14_ledger_keys"])==14
    assert summ["source_map_full_half_half_certified"]==[True,True,True]
    assert all(float(q)<2e-4 for q in summ["recomputed_local_bounds"].values())
    assert all(float(q)<2e-3 for q in summ["recomputed_widths"].values())
    assert rustsum["source_rows"]==46080
    assert rustsum["electron_interval_misses"]==0 and rustsum["thermal_interval_misses"]==0
    assert rustsum["production"]=="HOLD" and rustsum["canonical_DAG"]=="28/88"
    totals={key:[] for key in ("ne0","ne1","b0","b1","u0","u1")}
    count={"negative":0,"positive":0,"ambiguous":0}
    max_errors={k:0.0 for k in totals}
    with Path(source).open(newline="") as fs,Path(rust).open(newline="") as fr:
        inp=csv.DictReader(fs);res=csv.DictReader(fr)
        for i,(a,z) in enumerate(zip(inp,res,strict=True)):
            assert int(a["node"])==int(z["node"])==i
            h=float(a["N_H"]);he=float(a["N_He"])
            hi0=float(a["N_HII_0"]);hei0=float(a["N_HeII_0"]);heiii0=float(a["N_HeIII_0"])
            t0=float(a["T0_K"])
            hlo,hhi=(float(a["N_HII64_"+k]) for k in ("lo","hi"))
            helo,hehi=(float(a["N_HeII64_"+k]) for k in ("lo","hi"))
            he3lo,he3hi=(float(a["N_HeIII64_"+k]) for k in ("lo","hi"))
            tl,th=(float(a["T64_"+k+"_K"]) for k in ("lo","hi"))
            assert 0<h and 0<he and tl<=th and t0>0
            assert 0<=hi0<=h and 0<=hlo<=hhi<=h
            assert 0<=helo<=hehi<=he and 0<=he3lo<=he3hi<=he
            assert hehi+he3hi<=he*(1+5e-12)
            vH=(hlo+hhi)/2;vHe=(helo+hehi)/2;vHe3=(he3lo+he3hi)/2
            t=(tl+th)/2
            ne0=hi0+hei0+2*heiii0
            ne1=vH+vHe+2*vHe3
            b0=EV*(H*hi0+HEI*hei0+(HEI+HEII)*heiii0)
            b1=EV*(H*vH+HEI*vHe+(HEI+HEII)*vHe3)
            u0=1.5*KB*(h+he+ne0)*t0
            u1=1.5*KB*(h+he+ne1)*t
            expected={"ne0":ne0,"ne1":ne1,"b0":b0,"b1":b1,"u0":u0,"u1":u1}
            fields={"ne0":"Ne0","ne1":"Ne64_mid","b0":"B0_erg","b1":"B64_mid_erg",
                    "u0":"U0_erg","u1":"U64_mid_erg"}
            for key,value in expected.items():
                observed=float(z[fields[key]])
                if not nearly(value,observed):raise AssertionError(f"RUST_PHYSICAL_{key}_CELL_{i}: {value} vs {observed}")
                err=abs(value-observed)/max(abs(value),abs(observed),1e-290)
                max_errors[key]=max(max_errors[key],err)
                totals[key].append(value)
            # Parent subtraction is cancellation-sensitive. Compare to the
            # *unsubtracted* source magnitude with a priori 64 binary64 ulps,
            # not relative to a near-zero increment. This is representation
            # verification, never a relaxation of the original physical gate.
            for k,x,p0,p1 in (("DeltaNe_mid",ne1-ne0,ne0,ne1),
                              ("DeltaB_mid_erg",b1-b0,b0,b1),
                              ("DeltaU_mid_erg",u1-u0,u0,u1)):
                if abs(float(z[k])-x) > 64*2.220446049250313e-16*(abs(p0)+abs(p1)):
                    raise AssertionError(f"RUST_INCREMENT_{k}_CELL_{i}")
            nel=hlo+helo+2*he3lo;neu=hhi+hehi+2*he3hi
            assert nel<=ne1<=neu or nearly(ne1,nel) or nearly(ne1,neu)
            ul=1.5*KB*(h+he+nel)*tl
            uu=1.5*KB*(h+he+neu)*th
            assert ul<=u1<=uu or nearly(u1,ul) or nearly(u1,uu)
            if neu<ne0:count["negative"]+=1
            elif nel>ne0:count["positive"]+=1
            else:count["ambiguous"]+=1
    assert len(totals["ne0"])==46080
    glob={k:math.fsum(v) for k,v in totals.items()}
    glob.update(dne=glob["ne1"]-glob["ne0"],db=glob["b1"]-glob["b0"],du=glob["u1"]-glob["u0"])
    checks={"ne0":"source_ne0","ne1":"source_ne64_mid",
            "b0":"source_B0_erg","b1":"source_B64_mid_erg",
            "u0":"source_U0_erg","u1":"source_U64_mid_erg",
            "dne":"delta_ne_mid","db":"delta_B_mid_erg","du":"delta_U_mid_erg"}
    global_discrepancy={}
    for key,name in checks.items():
        val=glob[key];other=float(rustsum[name])
        if key in ("dne","db","du"):
            parent0,parent1={"dne":("ne0","ne1"),"db":("b0","b1"),
                             "du":("u0","u1")}[key]
            scale=abs(glob[parent0])+abs(glob[parent1])
            if abs(val-other)>64*2.220446049250313e-16*scale:
                raise AssertionError(f"RUST_GLOBAL_CANCELLED_{key}_MISMATCH {val} {other}")
            global_discrepancy[key]=abs(val-other)/scale
        else:
            if not nearly(val,other,2e-13):
                raise AssertionError(f"RUST_GLOBAL_{key}_MISMATCH {val} {other}")
            global_discrepancy[key]=abs(val-other)/max(abs(val),abs(other),1e-290)
    assert count["negative"]==rustsum["definitely_decreasing_electron_cells"]
    assert count["positive"]==rustsum["definitely_increasing_electron_cells"]
    assert count["ambiguous"]==rustsum["sign_ambiguous_cells"]
    phys=summ["physics"]
    for key,lower,upper in (("ne1",*phys["endpoint_electrons"]),("b1",*phys["endpoint_ionization_storage_erg"]),
                            ("u1",*phys["endpoint_gas_thermal_erg"])):
        assert lower<=glob[key]<=upper or nearly(glob[key],lower) or nearly(glob[key],upper)
    record={"schema":"REI_F05_ORIGINAL64_RUST_INDEPENDENT_46080_V1",
        "source_rows":46080,"checks_per_row":14,"source_sha256":digest(source),
        "rust_rows_sha256":digest(rust),"rust_summary_sha256":digest(rust_json),
        "original64_source_summary_sha256":digest(source_summary),
        "rust_vs_oracle_max_cell_rel_error":max_errors,
        "rust_vs_oracle_global_rel_error":global_discrepancy,
        "independently_summed":glob,"electron_cell_sign":count,
        "exact_original_state_byte_parity":summ["byte_equal_to_historical"],
        "claim_scope":"SOURCE_CONDITIONAL_ORIGINAL64_RUST_EOS_NOT_PRODUCTION_WORKER_ADMISSION",
        "central_DAG":"28/88","production":"HOLD","blind_referee":"SAME_AUTHOR_DIFFERENT_IMPLEMENTATION"}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"audit_status":"PASS","46k_cells":46080,"max_cell_relative":max(max_errors.values()),
        "max_global_relative":max(global_discrepancy.values()),
        "deltas":{"Ne":glob["dne"],"B_erg":glob["db"],"U_erg":glob["du"]},
        "sign_classes":count,"audit_sha256":digest(out)},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ("source","rust","rust-json","source-summary","out"):p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    run(a.source,a.rust,a.rust_json,a.source_summary,a.out)
