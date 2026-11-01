#!/usr/bin/env python3
"""Independent stdlib-only original REI 4-epoch 26-event physics audit.
Reads original supplier *published* source fields, no native chemistry solver import.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

N=46080
INPUT_SHA="5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913"
HE_SHA="f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c"
REC_SHA="f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429"
SOURCE_SHA="759b3b265bfbe540bcca28fe8fa51c06177256c825c3d10bb3541d44c703d351"
CHANNELS=("Bdot_net_erg_s","photo_binding_erg_s","collisional_binding_erg_s",
 "OTS_chemical_erg_s","OTS_resolved_heat_erg_s","OTS_unresolved_erg_s",
 "OTS_escaped_erg_s","primary_photoheat_erg_s","Udot_thermochemical_erg_s",
 "native_thermal_rhs_erg_s","dN_e_dt_per_s")
HE_MATCH=(("Bdot_net_erg_s","Bdot_net_erg_s"),
 ("photo_binding_erg_s","photo_binding_erg_s"),
 ("collisional_binding_erg_s","collisional_binding_erg_s"),
 ("OTS_chemical_erg_s","OTS_chemical_erg_s"),
 ("OTS_resolved_heat_erg_s","OTS_heat_erg_s"),
 ("OTS_unresolved_erg_s","OTS_unresolved_erg_s"),
 ("OTS_escaped_erg_s","OTS_escaped_erg_s"),
 ("primary_photoheat_erg_s","primary_photoheat_erg_s"))
def fail(ok,what):
    if not ok:raise ValueError("REI_OWNER_SOURCE_ADVERSARIAL_"+what)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def check_sha(p,ref):
    fail(sha(p)==ref,"SOURCE_SHA_"+Path(p).name)
def accurate(a,b,rtol=2e-12,scale_floor=1e-300):
    v=max(abs(a),abs(b),scale_floor)
    return abs(a-b)/v<=rtol
def audit(args):
    for name,sig in ((args.raw,INPUT_SHA),(args.science,SOURCE_SHA),
                     (args.he_csv,HE_SHA),(args.rec_json,REC_SHA)):
        check_sha(name,sig)
    source=json.loads(Path(args.science).read_text())
    rec=json.loads(Path(args.rec_json).read_text())
    fail(source["source_46080_cell_rows"]==4*N and source["new_official_tick161"] is False,"SCOPE")
    fail(len(source["original_epoch_results"])==4 and len(source["original_accepted_interval_comparisons"])==3,"EPOCH_COUNT")
    fail(rec["original_accepted_tick"]=="160/131072" and rec["cells_per_epoch"]==N,"REC_ACCEPTED_SOURCE")
    sums={tick:{k:[] for k in CHANNELS} for tick in (0,64,128,160)}
    rate_mismatches=0
    t160_mismatches=0
    max_t160_rel=0.0
    maximum_scaled_cell_stoich=0.0
    maximum_scaled_cell_ots=0.0
    max_local_therm=0.0
    exact_ticks=(0,64,128,160)
    original_clock={int(r["tick"]):float(r["proper_time_s"]) for r in source["original_epoch_results"]}
    with gzip.open(args.raw,"rt",newline="") as native, gzip.open(args.he_csv,"rt",newline="") as he:
        rows=csv.DictReader(native)
        target=csv.DictReader(he)
        for tick in exact_ticks:
            for i in range(N):
                try:r=next(rows)
                except StopIteration as e:raise ValueError("TRUNCATED_ORIGINAL_RHS") from e
                fail(int(r["accepted_tick"])==tick and int(r["node"])==i,"ORIGINAL_CELL_ORDER")
                fail(accurate(float(r["proper_time_s"]),original_clock[tick],1e-15),"ORIGINAL_PROPER_CLOCK")
                x={k:float(r[k]) for k in CHANNELS}
                h=float(r["N_H"]); hec=float(r["N_He"]); ele=float(r["N_e"]); temp=float(r["T_K"])
                fail(h>0 and hec>0 and ele>0 and temp>0 and all(math.isfinite(z) for z in (h,hec,ele,temp,*x.values())),"ORIGINAL_PHYSICAL_STATE")
                for k in CHANNELS:sums[tick][k].append(x[k])
                b=x["Bdot_net_erg_s"]; photo=x["photo_binding_erg_s"]; col=x["collisional_binding_erg_s"]; ots=x["OTS_chemical_erg_s"]
                pheat=x["OTS_resolved_heat_erg_s"]; unres=x["OTS_unresolved_erg_s"]; escape=x["OTS_escaped_erg_s"]
                scale=max(abs(b),abs(photo),abs(col),abs(ots),1e-280)
                scale2=max(abs(ots),abs(pheat),abs(unres),abs(escape),1e-280)
                stoich=abs(b-photo-col-ots)/scale
                ots_err=abs(ots+pheat+unres+escape)/scale2
                maximum_scaled_cell_stoich=max(maximum_scaled_cell_stoich,stoich)
                maximum_scaled_cell_ots=max(maximum_scaled_cell_ots,ots_err)
                fail(stoich<3e-12 and ots_err<3e-12,"ORIGINAL_ENERGY_STOICHIOMETRY")
                th=abs(x["Udot_thermochemical_erg_s"]-x["native_thermal_rhs_erg_s"])/max(abs(x["Udot_thermochemical_erg_s"]),abs(x["native_thermal_rhs_erg_s"]),1e-280)
                max_local_therm=max(max_local_therm,th)
                fail(th<3e-12,"THERMAL_SOURCE_IDENTITY")
                if tick==160:
                    try:q=next(target)
                    except StopIteration as e:raise ValueError("TRUNCATED_BASS_HE150") from e
                    fail(int(q["cell"])==i,"BASS_HE150_ORIGINAL_NODE")
                    for k,correspondent in HE_MATCH:
                        a=float(r[k]); bb=float(q[correspondent])
                        rel=abs(a-bb)/max(abs(a),abs(bb),1e-280)
                        max_t160_rel=max(max_t160_rel,rel)
                        if rel>2e-12:t160_mismatches+=1
                    fail(accurate(temp,float(q["temperature_K"]),2e-12),"BASS_HE150_TEMPERATURE")
        fail(next(rows,None) is None,"EXTRA_ORIGINAL_ROWS")
        fail(next(target,None) is None,"EXTRA_BASS_HE150_ROWS")
    fail(t160_mismatches==0,"BASS_HE150_CELLWISE_SOURCE_PARITY")
    aggr={}
    for tick in exact_ticks:
        mapped=next(r["source_powers"] for r in source["original_epoch_results"] if r["tick"]==tick)
        aggr[str(tick)]={}
        for key,vals in sums[tick].items():
            tot=math.fsum(vals)
            mapped_key="dNe_dt_per_s" if key=="dN_e_dt_per_s" else key
            fail(accurate(tot,mapped[mapped_key],2e-12),"SCIENTIFIC_AGGREGATE_"+key+"_"+str(tick))
            aggr[str(tick)][key]=tot
    cases=[]
    for j,interval in enumerate(source["original_accepted_interval_comparisons"]):
        a,b=interval["original_interval_ticks"]
        orig=rec["interval_physics"][j]
        fail(orig["interval_ticks"]==[a,b] and a in exact_ticks and b in exact_ticks,"REC_ORIGINAL_INTERVAL")
        checks={}
        for letter,channel in (("B","Bdot_net_erg_s"),("U","Udot_thermochemical_erg_s")):
            v=interval[letter]
            a0=aggr[str(a)][channel];b0=aggr[str(b)][channel]
            midpoint=(a0+b0)*0.5
            lo,hi=orig[f"source_delta_{letter}_secant_erg_s"]
            fail(all(accurate(z,t,2e-12) for z,t in zip(v["accepted_material_source_secant_erg_s"],[lo,hi])),"DONOR_SECANT_VALUE")
            fail(accurate(midpoint,v["trapezoid_endpoint_derivative_erg_s"],2e-12),"TRAPEZOID_RECONSTRUCTION")
            checks[letter]={"original_secant_erg_s":[lo,hi],"original_rate_left":a0,"original_rate_right":b0,
                "trapezoid":midpoint,"trapezoid_in_original_secant":lo<=midpoint<=hi,
                "trapezoid_minus_source_secant_interval":[midpoint-hi,midpoint-lo]}
        cases.append({"interval_ticks":[a,b],"science":checks})
    fail(not cases[0]["science"]["B"]["trapezoid_in_original_secant"],"OLD_INTERVAL_NEGATIVE_WITNESS_MUST_BE_PRESERVED")
    claim={
      "schema":"REI_F05_4_ACCEPTED_EPOCH_SOURCE_RHS_INDEPENDENT_CELLS_AUDIT_V1",
      "status":"PASS_SCOPED_SOURCE_CONDITIONAL",
      "source_rows_directly_read":4*N,"tick160_cellwise_original_OTS_donor_rows_compared":N,
      "tick160_donor_source_power_channels_checked":len(HE_MATCH),
      "tick160_donor_cellwise_mismatches":t160_mismatches,
      "tick160_max_relative_source_difference":max_t160_rel,
      "max_cell_chemical_stoichiometry_scaled_residual":maximum_scaled_cell_stoich,
      "max_cell_OTS_photon_energy_scaled_residual":maximum_scaled_cell_ots,
      "max_cell_original_thermal_RHS_difference_scaled":max_local_therm,
      "actually_original_time_segment_cases":cases,
      "negative_witness":"First [0,64] chemical B endpoint trapezoid is OUTSIDE accepted material secant. This is NOT a corrected history, validated LTE or an ODE impossibility.",
      "original_native_state_admission":"HISTORICAL_T160_ONLY; T161_NOT_ACCEPTED",
      "support":"same_author_independent_published_source_native_cellwise_arithmetic_not_distinct_author",
      "dag":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","delta":0},
      "production":"HOLD"}
    Path(args.output).write_text(json.dumps(claim,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"audit":"PASS","cells":4*N,"donor_cellwise_mismatches":t160_mismatches,"max_rel_donor":max_t160_rel,
        "first64_trapezoid_failure_preserved":True,"dag":"28/88"}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for s in ("raw","science","he_csv","rec_json","output"):p.add_argument("--"+s.replace("_","-"),dest=s,required=True)
    audit(p.parse_args())
