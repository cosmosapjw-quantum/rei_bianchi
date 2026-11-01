#!/usr/bin/env python3
"""Independent source-conditional F05 owner auditing.

No imports of producer program, original map, original workbook, or generated
V2 decoder. Reopens 46,080 original source rows, REC trajectory, BASS 26-event
event/energy donor, and produced 46k aligned source physical rows.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

N=46080
DT=4871848749.16828
REC_SHA="6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c"
BASS_SHA="f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c"
EXPECTED_WITNESS_SHA="965f59f2bbf6dc889155bf3a4454167e69d30bea17fa7dda64ca4f2c3529805d"
SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def req(c,key):
    if not c:raise AssertionError("OWNER_F05_INDEPENDENT_"+key)
def ok_close(a,b,scale=0.0):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=64*2.220446049250313e-16*max(abs(a),abs(b),scale,1e-300)

def read_original_rec(path):
    values={128:[],160:[]}
    with gzip.open(path,"rt",newline="") as f:
        rd=csv.DictReader(f)
        counts={0:0,64:0,128:0,160:0}
        for pos,row in enumerate(rd):
            group=(0,64,128,160)[pos//N] if pos//N<4 else -1
            i=pos%N
            req(int(row["node"])==i and int(row["tick"])==group,"REC_SOURCE_CLOCK_ROW")
            counts[group]+=1
            if group in values:values[group].append(row)
    req(all(x==N for x in counts.values()),"REC_COMPLETE_FOUR_EPOCHS")
    return values

def run(args):
    req(digest(args.rec)==REC_SHA and digest(args.bass)==BASS_SHA,"UPSTREAM_SHA")
    req(digest(args.witness)==EXPECTED_WITNESS_SHA,"WITNESS_SHA")
    science=json.loads(args.science.read_text())
    req(science["original_source_tar_sha256"]==SOURCE_TAR,"REI_26EVENT_ARCHIVE")
    req(science["project_owner_original_F05_accepted"]=="160/131072" and
        science["v2_canonical_accepted"] is False,"OFFICIAL_PROVENANCE")
    req(science["source_v2_endpoint_rows"]==N and science["source_Bdot_full_cell_rows"]==N,"SOURCE_ROW_SCOPE")
    req(digest(args.full)==science["full_source_real_physics_csv_sha256"],"PRIVATE_REAL_DATA_SHA")
    rec=read_original_rec(args.rec)
    with args.witness.open(newline="") as f:
        witness={int(x["cell"]):x for x in csv.DictReader(f)}
    req(len(witness)==24,"PUBLIC_24_PHYSICAL_WITNESSES")
    source_abs=[];source_rate=[];candidate_sec=[];accepted_sec=[]
    original_extensive_parent_magnitudes=[]
    source_photo=[];source_coll=[];source_ots=[]
    discordant=[]
    max_source_identity=0.0;max_ots_identity=0.0;max_source_row_error=0.0
    species_change_ne=[]
    with gzip.open(args.full,"rt",newline="") as f,gzip.open(args.bass,"rt",newline="") as fb:
        rows=csv.DictReader(f);up=csv.DictReader(fb)
        for i,(row,donor) in enumerate(zip(rows,up,strict=True)):
            req(i<N and int(row["cell"])==i and int(donor["cell"])==i,"SOURCE_ALIGNED_ROWS")
            r128=rec[128][i];r160=rec[160][i]
            B128mid=(float(r128["B_lower_erg"])+float(r128["B_upper_erg"]))*0.5
            B160rec=(float(r160["B_lower_erg"])+float(r160["B_upper_erg"]))*0.5
            B128=float(row["B128_mid_erg"])
            B160=float(row["B160_mid_erg"])
            B161=float(row["B161V2_mid_erg"])
            original_extensive_parent_magnitudes.append(abs(B128)+abs(B160)+abs(B161))
            scale0=max(abs(B128mid),abs(B160rec),abs(B160),abs(B161))
            req(ok_close(B128,B128mid,scale0),"ORIGINAL_ACCEPTED128")
            req(ok_close(B160,B160rec,scale0),"ORIGINAL_ACCEPTED160")
            r128sec=(B160-B128)/(32*DT)
            r161sec=(B161-B160)/DT
            req(ok_close(float(row["B128_160_secant_erg_s"]),r128sec,scale0/DT),"ACCEPTED_SECANT")
            req(ok_close(float(row["B160_161V2_secant_erg_s"]),r161sec,scale0/DT),"V2_SECANT")
            dot=float(donor["Bdot_net_erg_s"])
            ph=float(donor["photo_binding_erg_s"])
            co=float(donor["collisional_binding_erg_s"])
            ot=float(donor["OTS_chemical_erg_s"])
            h=float(donor["OTS_heat_erg_s"])
            u=float(donor["OTS_unresolved_erg_s"])
            e=float(donor["OTS_escaped_erg_s"])
            err=abs(dot-math.fsum((ph,co,ot)))
            denom=max(abs(ph)+abs(co)+abs(ot),1e-300)
            max_source_identity=max(max_source_identity,err/denom)
            req(err/denom<3e-12,"ORIGINAL_STOICHIOMETRY")
            otserr=abs(math.fsum((ot,h,u,e)))
            otsden=max(abs(ot)+abs(h)+abs(u)+abs(e),1e-300)
            max_ots_identity=max(max_ots_identity,otserr/otsden)
            req(otserr/otsden<3e-12,"SOURCE_OTS_BALANCE")
            for key,expected in (("Bdot_160_erg_s",dot),
                                 ("Bdot_photo_160_erg_s",ph),
                                 ("Bdot_collisional_160_erg_s",co),
                                 ("Bdot_OTSchemical_160_erg_s",ot),
                                 ("OTS_heat_160_erg_s",h),
                                 ("OTS_unresolved_160_erg_s",u),
                                 ("OTS_escaped_160_erg_s",e)):
                obs=float(row[key])
                req(ok_close(obs,expected,abs(expected)),"UPSTREAM_SOURCE_VALUE_"+key)
                max_source_row_error=max(max_source_row_error,
                             abs(obs-expected)/max(abs(obs),abs(expected),1e-300))
            for key in ("NH","NHe"):
                src=float(r160["N_H" if key=="NH" else "N_He"])
                req(ok_close(float(row[key]),src),"NUCLEUS_SOURCE_"+key)
            ne160=float(row["Ne160_mid"]);ne161=float(row["Ne161V2_mid"])
            req(ne160>0 and ne161>0,"FREE_ELECTRON_CONE")
            species_change_ne.append(ne161-ne160)
            for key in ("U160_mid_erg","U161V2_mid_erg"):
                req(float(row[key])>0,"THERMAL_POSITIVE")
            source_rate.append(dot);source_photo.append(ph);source_coll.append(co);source_ots.append(ot)
            accepted_sec.append(r128sec);candidate_sec.append(r161sec)
            source_abs.append(abs(dot))
            if math.copysign(1.0,r161sec)!=math.copysign(1.0,dot):
                discordant.append({"cell":i,"source_Bdot":dot,"v2_secant":r161sec,
                                   "source_Bdot_fraction_of_abs_sum":abs(dot)})
            if i in witness:
                w=witness[i]
                for key in ("B128_mid_erg","B160_mid_erg","B161V2_mid_erg",
                            "Bdot_160_erg_s","B160_161V2_secant_erg_s"):
                    req(ok_close(float(w[key]),float(row[key])),"WITNESS_"+key)
    req(len(source_rate)==N,"FULL_INPUT_ROW_COUNT")
    sumv=lambda a:float(math.fsum(a))
    global_rates={
        "source_net_Bdot":sumv(source_rate),
        "photo_Bdot":sumv(source_photo),
        "collisional_Bdot":sumv(source_coll),
        "ots_Bdot":sumv(source_ots),
        "accepted_128_160_mid_secant":sumv(accepted_sec),
        "candidate_160_161_mid_secant":sumv(candidate_sec),
        "candidate_delta_Ne":sumv(species_change_ne)}
    s=science["global_physics"]
    for k,source_key in (("source_net_Bdot","Bdot_net_160_erg_s"),
                         ("photo_Bdot","Bdot_photo_160_erg_s"),
                         ("collisional_Bdot","Bdot_collisional_160_erg_s"),
                         ("ots_Bdot","Bdot_OTS_chemical_160_erg_s"),
                         ("accepted_128_160_mid_secant","accepted_128_160_mid_secant_erg_s"),
                         ("candidate_160_161_mid_secant","candidate_160_161_mid_secant_erg_s"),
                         ("candidate_delta_Ne","delta_Ne_160_161_v2_mid")):
        if k in ("accepted_128_160_mid_secant","candidate_160_161_mid_secant"):
            # Global finite secants subtract ~1e56 erg extensive parents
            # to obtain ~1e39 erg/s. Compare only at original parent
            # binary64 summation scale, not delta-relative accuracy.
            dt=32*DT if k=="accepted_128_160_mid_secant" else DT
            budget=64*2.220446049250313e-16*sumv(original_extensive_parent_magnitudes)/dt
            req(abs(global_rates[k]-s[source_key])<=budget,"GLOBAL_CANCELLED_"+k)
        else:
            req(ok_close(global_rates[k],s[source_key]),"GLOBAL_"+k)
    req(len(discordant)==science["new_46k_cell_sign_diagnostic"]["different_sign"],"SIGN_CLASS_COUNT")
    abs_sum=sumv(source_abs);discord_abs=sumv([r["source_Bdot_fraction_of_abs_sum"] for r in discordant])
    result={
        "schema":"REI_OWNER_F05_V2_OTS_CAUSAL_INDEPENDENT_AUDIT_V1",
        "source_cell_rows_checked":N,"rec_original_rows_checked":4*N,
        "witness_public_rows_checked":len(witness),
        "source_original_bin_sha256":digest(args.full),
        "upstream_REC195_original_sha256":REC_SHA,"upstream_BASS_HE150_original_sha256":BASS_SHA,
        "max_relative_26event_stoich_residual":max_source_identity,
        "max_relative_OTS_energy_identity_residual":max_ots_identity,
        "max_source_value_relative_error":max_source_row_error,
        "global_quantities_independently_summed":global_rates,
        "candidate_vs_instant_source_relative_difference":
            global_rates["candidate_160_161_mid_secant"]/global_rates["source_net_Bdot"]-1.0,
        "discordant_sign_cells":len(discordant),
        "discordant_source_Bdot_absolute_weight_fraction":discord_abs/abs_sum,
        "discordant_cells_first_20":[x["cell"] for x in discordant[:20]],
        "original_rei_official_tick":"160/131072","v2_official":False,
        "source_scope":"FROZEN_T160_26EVENT_OTS_VS_ORIGINAL_ACCEPTED_AND_V2_CANDIDATE_MIDPOINT",
        "independent_of":"ORIGINAL_26EVENT_WORKER_AND_PRODUCER_PYTHON_IMPLEMENTATION",
        "central_DAG":"28/88","production":"HOLD",
        "candidate_chemistry_source_vs_secant_global_distinction":True
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"audit_status":"PASS","source_rows":N,
         "max_stoichiometric_residual":max_source_identity,
         "max_OTS_identity_residual":max_ots_identity,
         "candidate_secant":global_rates["candidate_160_161_mid_secant"],
         "source_net_dot":global_rates["source_net_Bdot"],
         "discordant_cells":len(discordant),
         "discordant_abs_weight_fraction":discord_abs/abs_sum,
         "independent_receipt_sha256":digest(args.out)},indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for key in ("full","rec","bass","science","witness","out"):
        parser.add_argument("--"+key,required=True,type=Path)
    run(parser.parse_args())
