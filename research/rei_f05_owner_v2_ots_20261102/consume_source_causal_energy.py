#!/usr/bin/env python3
"""REI original F05 owner: real 46k source, stoichiometry and candidate-state bridge.

Original REC195 [128,160], BASS_HE150 accepted-t160 26-event OTS chemistry
and original V2 candidate161 all source-locked. Source-private physical 46k
rows never committed. V2 is a shadow, NEVER official accepted F05 history.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np

N=46080
TICKS=(0,64,128,160)
SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_STATE160="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
SOURCE_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
REC_CSV_SHA="6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c"
REC_JSON_SHA="f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429"
BASS_CSV_SHA="f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c"
BASS_JSON_SHA="202c422e7c23da3ea93b82e35429efe387b66225107e94248e28c6263facc5e2"
V2_ORIGINAL_OLD_SHA="eb13b86f86dfdd37ba17a7007640263b7210397be31ead24a05c5d2dbf62f90b"
EV=1.602176634e-12
KB=1.380649e-16
CHI_H=13.598434599702
CHI_HE1=24.587389011
CHI_HE2=54.417760
DT=4871848749.16828
DT_128_160=32*DT
RADIUS=64.0*np.finfo(np.float64).eps

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def require(c,key):
    if not c:raise ValueError("REI_OWNER_F05_V2_CAUSAL_"+key)

def pair_mid(a,b):return 0.5*a+0.5*b

def original_physics(pop,logT,nh,nhe):
    require(pop.shape==(N,5) and logT.shape==(N,),"NATIVE_46K_5")
    require(np.all(pop>0) and np.isfinite(pop).all(),"POSITIVE")
    # Each bound is a corner of a *set enclosure*, not a separate
    # nucleus-conserving physical state. Conservation belongs to the
    # two-sided parent/candidate interval check below, not each corner.
    ne=pop[:,1]+pop[:,3]+2*pop[:,4]
    B=EV*(CHI_H*pop[:,1]+CHI_HE1*(pop[:,3]+pop[:,4])+CHI_HE2*pop[:,4])
    U=1.5*KB*(nh+nhe+ne)*np.exp(logT)
    require(np.isfinite(ne).all() and np.isfinite(B).all() and np.isfinite(U).all(),"FINITE_PHYS")
    require(np.all(ne>0) and np.all(B>0) and np.all(U>0),"POSITIVE_PHYS")
    return ne,B,U

def read_rec(path):
    nh=np.empty(N);nhe=np.empty(N)
    fields=("B_lower_erg","B_upper_erg","Ne_lower","Ne_upper","U_lower_erg","U_upper_erg",
            "T_lower_K","T_upper_K","source_volume_cm3")
    by={t:{k:np.empty(N,dtype=np.float64) for k in fields} for t in (128,160)}
    counts={t:0 for t in TICKS}
    with gzip.open(path,"rt",newline="") as f:
        rd=csv.DictReader(f)
        require(set(fields).issubset(rd.fieldnames or ()),"REC_SCHEMA")
        for pos,row in enumerate(rd):
            tick=TICKS[pos//N] if pos//N<len(TICKS) else -1
            cell=pos%N
            require(int(row["tick"])==tick and int(row["node"])==cell,"REC_CLOCK_OR_ORDER")
            counts[tick]+=1
            if tick not in by:continue
            h=float(row["N_H"]);he=float(row["N_He"])
            require(h>0 and he>0,"REC_NUCLEI")
            if tick==128:nh[cell]=h;nhe[cell]=he
            else:
                require(h==nh[cell] and he==nhe[cell],"SOURCE_NUCLEI_CHANGED")
            for k in fields:
                x=float(row[k]);require(math.isfinite(x),"REC_FINITE")
                by[tick][k][cell]=x
    require(all(x==N for x in counts.values()),"REC_EPOCH_COUNTS")
    for tick in by:
        for lo,hi in [("B_lower_erg","B_upper_erg"),("Ne_lower","Ne_upper"),
                      ("U_lower_erg","U_upper_erg"),("T_lower_K","T_upper_K")]:
            require(np.all(by[tick][lo]>0) and np.all(by[tick][lo]<=by[tick][hi]),"REC_INTERVAL")
    return nh,nhe,by

def read_bass(path):
    names=("Bdot_net_erg_s","photo_binding_erg_s","collisional_binding_erg_s",
           "OTS_chemical_erg_s","OTS_heat_erg_s","OTS_unresolved_erg_s",
           "OTS_escaped_erg_s","primary_photoheat_erg_s")
    data={n:np.empty(N,dtype=np.float64) for n in names}
    count=0;max_resid=0.0;max_ots_resid=0.0
    with gzip.open(path,"rt",newline="") as f:
        rd=csv.DictReader(f)
        require(set(names).issubset(rd.fieldnames or ()),"BASS_SCHEMA")
        for row in rd:
            i=count
            require(i<N and int(row["cell"])==i,"BASS_NODE_ORDER")
            for name in names:
                x=float(row[name]);require(math.isfinite(x),"BASS_FINITE")
                data[name][i]=x
            p=data["photo_binding_erg_s"][i]
            c=data["collisional_binding_erg_s"][i]
            r=data["OTS_chemical_erg_s"][i]
            dot=data["Bdot_net_erg_s"][i]
            q=data["OTS_heat_erg_s"][i]
            u=data["OTS_unresolved_erg_s"][i]
            e=data["OTS_escaped_erg_s"][i]
            den=max(abs(p)+abs(c)+abs(r),1e-300)
            resid=abs(dot-(p+c+r))/den
            max_resid=max(max_resid,resid)
            require(resid<3e-12,"BASS_26EVENT_CHEM_STOICHIOMETRY")
            den2=max(abs(r)+abs(q)+abs(u)+abs(e),1e-300)
            resid2=abs(r+q+u+e)/den2
            max_ots_resid=max(max_ots_resid,resid2)
            require(resid2<3e-12,"BASS_OTS_ENERGY_BALANCE")
            count+=1
    require(count==N,"BASS_CELL_COUNT")
    return data,max_resid,max_ots_resid

def save_gzip_csv(path,header,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as binary:
        with gzip.GzipFile(filename="",mode="wb",fileobj=binary,compresslevel=6,mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as text:
                writer=csv.writer(text,lineterminator="\n")
                writer.writerow(header)
                for row in rows:writer.writerow(row)

def main(args):
    require(sha(args.rec_csv)==REC_CSV_SHA and sha(args.rec_json)==REC_JSON_SHA,"REC_SOURCE_SHA")
    require(sha(args.bass_csv)==BASS_CSV_SHA and sha(args.bass_json)==BASS_JSON_SHA,"BASS_SOURCE_SHA")
    require(sha(args.old_v2_npz)==V2_ORIGINAL_OLD_SHA,"ARCHIVED_V2_SHA")
    recmeta=json.loads(args.rec_json.read_text())
    bassmeta=json.loads(args.bass_json.read_text())
    receipt=json.loads(args.v2_receipt.read_text())
    require(sha(args.v2_npz)==receipt["candidate_state_sha256"],"V2_RECEIPT_SHA")
    require(recmeta["original_tar_sha256"]==SOURCE_TAR and
            recmeta["original_final160_array_sha256"]==SOURCE_STATE160 and
            recmeta["original_kernel_sha256"]==SOURCE_KERNEL,"REC_SOURCE_AUTHORITY")
    require(bassmeta["source_original_tar_sha256"]==SOURCE_TAR and
            bassmeta["source_original_array_sha256"]==SOURCE_STATE160 and
            bassmeta["kernel_sha256"]==SOURCE_KERNEL,"BASS_SOURCE_AUTHORITY")
    require(receipt["source_sha256"]==SOURCE_TAR and
            receipt["state_array_sha256"]==SOURCE_STATE160 and
            receipt["kernel_sha256"]==SOURCE_KERNEL,"V2_SOURCE_AUTHORITY")
    require(receipt["original_accepted_tick"]=="160/131072" and
            receipt["shadow_v2_candidate_tick"]=="161/131072_NOT_OFFICIAL" and
            receipt["official_tick161_accepted"] is False,"V2_NOT_OFFICIAL_SCOPE")
    require(receipt.get("original_14_ledger_pass") is True and
            not receipt.get("original_table_event",{}).get("any_event",True),"V2_SOURCE_LEDGER")
    require(max(receipt["new_original_common_parent_local_upper"].values())<2e-4 and
            max(receipt["original_public_widths"].values())<2e-3 and
            receipt["old_independent_endpoint_local_upper"]["log_T"]>2e-4,"ORIGINAL_V1_V2_GATES")
    nh,nhe,rec=read_rec(args.rec_csv)
    src,mres,ores=read_bass(args.bass_csv)
    with np.load(args.v2_npz,allow_pickle=False) as new,np.load(args.old_v2_npz,allow_pickle=False) as old:
        keys=set(("population_lower","population_upper","log_temperature_lower",
                  "log_temperature_upper","source_parent_population_lower",
                  "source_parent_population_upper","source_parent_logT_lower","source_parent_logT_upper"))
        require(set(new.files)==set(old.files)==keys,"V2_POPULATION_SCHEMA")
        arrays={k:np.array(new[k],copy=True) for k in keys}
        olds={k:np.array(old[k],copy=True) for k in keys}
    for k in keys:
        require(np.isfinite(arrays[k]).all(),"V2_FINITE_"+k)
    for k in ("source_parent_population_lower","source_parent_population_upper",
              "source_parent_logT_lower","source_parent_logT_upper"):
        require(np.array_equal(arrays[k],olds[k]),"V2_SHARED_OLD_PARENT")
    poplo=arrays["population_lower"];pophi=arrays["population_upper"]
    ltlo=arrays["log_temperature_lower"];lthi=arrays["log_temperature_upper"]
    require(np.all(poplo<=pophi) and np.all(ltlo<=lthi),"V2_POP_INTERVAL")
    disjoint=0;max_rel=0.0;max_temperature_rel=0.0
    for k in ("population","log_temperature"):
        keylo=k+"_lower";keyhi=k+"_upper"
        al,ah=olds[keylo],olds[keyhi];bl,bh=arrays[keylo],arrays[keyhi]
        disjoint+=int(np.count_nonzero((al>bh)|(bl>ah)))
        midold=pair_mid(al,ah);midnew=pair_mid(bl,bh)
        rel=np.abs(midold-midnew)/np.maximum(np.maximum(np.abs(midold),np.abs(midnew)),np.finfo(float).tiny)
        if k=="population":max_rel=float(np.max(rel))
        else:max_temperature_rel=float(np.max(rel))
    require(disjoint==0,"V2_OLD_NEW_DISJOINT")
    p0l,p0h=arrays["source_parent_population_lower"],arrays["source_parent_population_upper"]
    z0l,z0h=arrays["source_parent_logT_lower"],arrays["source_parent_logT_upper"]
    n0l,b0l,u0l=original_physics(p0l,z0l,nh,nhe)
    n0h,b0h,u0h=original_physics(p0h,z0h,nh,nhe)
    n1l,b1l,u1l=original_physics(poplo,ltlo,nh,nhe)
    n1h,b1h,u1h=original_physics(pophi,lthi,nh,nhe)
    for pl,ph,name in ((p0l,p0h,"PARENT"),(poplo,pophi,"V2_CANDIDATE")):
        h_l=pl[:,0]+pl[:,1];h_h=ph[:,0]+ph[:,1]
        he_l=pl[:,2]+pl[:,3]+pl[:,4];he_h=ph[:,2]+ph[:,3]+ph[:,4]
        require(np.all(h_l<=nh*(1+3e-12)) and np.all(h_h>=nh*(1-3e-12)),"H_INTERVAL_"+name)
        require(np.all(he_l<=nhe*(1+3e-12)) and np.all(he_h>=nhe*(1-3e-12)),"HE_INTERVAL_"+name)
    for name,l,h in (("B",b0l,b0h),("Ne",n0l,n0h),("U",u0l,u0h)):
        low=rec[160][{"B":"B_lower_erg","Ne":"Ne_lower","U":"U_lower_erg"}[name]]
        high=rec[160][{"B":"B_upper_erg","Ne":"Ne_upper","U":"U_upper_erg"}[name]]
        # Interval intersection rather than demanding endpoint equality;
        # two valid outward enclosures can have different widths.
        gap=np.maximum(l-high,low-h)
        allowed=64*np.finfo(float).eps*np.maximum(np.maximum(np.abs(l),np.abs(h)),np.finfo(float).tiny)
        require(np.all(gap<=allowed),"ORIGINAL_PARENT_REC_INTERVAL_"+name)
    D_128_160=np.array([pair_mid(rec[160]["B_lower_erg"],rec[160]["B_upper_erg"])-
                        pair_mid(rec[128]["B_lower_erg"],rec[128]["B_upper_erg"])])[0]/DT_128_160
    D_160_161=(pair_mid(b1l,b1h)-pair_mid(b0l,b0h))/DT
    net=src["Bdot_net_erg_s"]
    mids={
       "B128":pair_mid(rec[128]["B_lower_erg"],rec[128]["B_upper_erg"]),
       "B160":pair_mid(b0l,b0h),
       "B161":pair_mid(b1l,b1h),
       "U160":pair_mid(u0l,u0h),
       "U161":pair_mid(u1l,u1h),
       "Ne160":pair_mid(n0l,n0h),
       "Ne161":pair_mid(n1l,n1h)
    }
    global_sum=lambda v:float(math.fsum(float(x) for x in v))
    totals={
        "Bdot_photo_160_erg_s":global_sum(src["photo_binding_erg_s"]),
        "Bdot_collisional_160_erg_s":global_sum(src["collisional_binding_erg_s"]),
        "Bdot_OTS_chemical_160_erg_s":global_sum(src["OTS_chemical_erg_s"]),
        "Bdot_net_160_erg_s":global_sum(net),
        "OTS_heat_160_erg_s":global_sum(src["OTS_heat_erg_s"]),
        "OTS_unresolved_160_erg_s":global_sum(src["OTS_unresolved_erg_s"]),
        "OTS_escaped_160_erg_s":global_sum(src["OTS_escaped_erg_s"]),
        "primary_photoheat_160_erg_s":global_sum(src["primary_photoheat_erg_s"]),
        "delta_B_128_160_mid_erg":global_sum(D_128_160)*DT_128_160,
        "delta_B_160_161_v2_mid_erg":global_sum(D_160_161)*DT,
        "delta_U_160_161_v2_mid_erg":global_sum(mids["U161"]-mids["U160"]),
        "delta_Ne_160_161_v2_mid":global_sum(mids["Ne161"]-mids["Ne160"])
    }
    totals["source_Bdot_t160_one_tick_predict_delta_erg"]=totals["Bdot_net_160_erg_s"]*DT
    totals["accepted_128_160_mid_secant_erg_s"]=global_sum(D_128_160)
    totals["candidate_160_161_mid_secant_erg_s"]=global_sum(D_160_161)
    totals["candidate_minus_source_one_tick_erg"]=totals["delta_B_160_161_v2_mid_erg"]-totals["source_Bdot_t160_one_tick_predict_delta_erg"]
    totals["candidate_vs_source_rate_relative"]=(
        totals["candidate_160_161_mid_secant_erg_s"]/totals["Bdot_net_160_erg_s"]-1)
    expected=bassmeta["result"]["physical_energy_powers"]["Bdot_net_erg_s"]
    require(abs(totals["Bdot_net_160_erg_s"]-expected)<3e-12*abs(expected),"BASS_T160_GLOBAL_SUM")
    origrec=recmeta["interval_physics"][2]["source_delta_B_secant_erg_s"]
    require(origrec[0]<=totals["accepted_128_160_mid_secant_erg_s"]<=origrec[1],"REC_ACCEPTED_SECANT_INTERVAL")
    strict_source=bassmeta["result"]["source_interval_energy_bounds"]["Bdot_net_erg_s"]
    require(strict_source[0]<=totals["Bdot_net_160_erg_s"]<=strict_source[1],"SOURCE_GROSS_IN_BOUNDS")
    # Compare independent acceptance and source without imposing equality
    accepted_source_overlap=(origrec[0]<=strict_source[1] and strict_source[0]<=origrec[1])
    require(accepted_source_overlap,"ORIGINAL_ACCEPTED_AND_T160_SOURCE_DISJOINT")
    sign_candidate=np.sign(D_160_161);sign_source=np.sign(net)
    same_sign=int(np.count_nonzero(sign_candidate==sign_source))
    rows=[]
    interesting=tuple(sorted(set((0,1,2,3,7,10,50,100,500,1000,5000,10000,
                        12527,18000,20000,24000,28000,32000,36000,40000,42000,
                        44000,45000,46079))))
    witnesses=[]
    for i in range(N):
        row=(i,nh[i],nhe[i],mids["B128"][i],mids["B160"][i],mids["B161"][i],
             D_128_160[i],D_160_161[i],net[i],
             src["photo_binding_erg_s"][i],src["collisional_binding_erg_s"][i],
             src["OTS_chemical_erg_s"][i],src["OTS_heat_erg_s"][i],
             src["OTS_unresolved_erg_s"][i],src["OTS_escaped_erg_s"][i],
             src["primary_photoheat_erg_s"][i],mids["Ne160"][i],
             mids["Ne161"][i],mids["U160"][i],mids["U161"][i])
        rows.append(row)
        if i in interesting:witnesses.append(row)
    header=("cell","NH","NHe","B128_mid_erg","B160_mid_erg","B161V2_mid_erg",
            "B128_160_secant_erg_s","B160_161V2_secant_erg_s","Bdot_160_erg_s",
            "Bdot_photo_160_erg_s","Bdot_collisional_160_erg_s","Bdot_OTSchemical_160_erg_s",
            "OTS_heat_160_erg_s","OTS_unresolved_160_erg_s",
            "OTS_escaped_160_erg_s","primary_photoheat_160_erg_s",
            "Ne160_mid","Ne161V2_mid","U160_mid_erg","U161V2_mid_erg")
    private=args.private_dir;public=args.public_dir
    private.mkdir(parents=True,exist_ok=True);public.mkdir(parents=True,exist_ok=True)
    full=private/"ORIGINAL_REI_T160_161_V2_OTS_SOURCE_ALIGNED_46080.csv.gz"
    sample=public/"ORIGINAL_SOURCE_OTS_24_PHYSICAL_WITNESSES.csv"
    save_gzip_csv(full,header,rows)
    with sample.open("w",newline="") as f:
        wr=csv.writer(f,lineterminator="\n");wr.writerow(header);wr.writerows(witnesses)
    summary={
       "schema":"REI_OWNER_F05_26EVENT_T160_TO161_OTS_SOURCE_CAUSAL_CONSUMPTION_V1",
       "owner_parent_pr":365,"project_owner_original_F05_accepted":"160/131072",
       "v2_canonical_accepted":False,"production":"HOLD",
       "original_source_tar_sha256":SOURCE_TAR,"original_source_160_sha256":SOURCE_STATE160,
       "original_source_kernel_sha256":SOURCE_KERNEL,
       "rec195_HEAD":"0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235",
       "rec195_csv_sha256":REC_CSV_SHA,"rec195_science_json_sha256":REC_JSON_SHA,
       "bass_he150_HEAD":"f2d26ef196b50e69c1793cc4c29e96a248fe6c0b",
       "bass_he150_csv_sha256":BASS_CSV_SHA,"bass_he150_science_json_sha256":BASS_JSON_SHA,
       "candidate_pinned_npz_sha256":sha(args.v2_npz),
       "candidate_v2_receipt_sha256":sha(args.v2_receipt),
       "old_v2_npz_sha256":V2_ORIGINAL_OLD_SHA,
       "candidate_vs_old_disjoint_physical_source_intervals":disjoint,
       "candidate_vs_old_max_population_relative":max_rel,
       "candidate_vs_old_max_logT_relative":max_temperature_rel,
       "candidate_full_half_half_14_original_ledgers_pass":True,
       "original_v1_logT_upper":receipt["old_independent_endpoint_local_upper"]["log_T"],
       "original_v2_logT_upper":receipt["new_original_common_parent_local_upper"]["log_T"],
       "original_fixed_error_gate":2e-4,"original_fixed_width_gate":2e-3,
       "accepted_source_material_rows":184320,"source_Bdot_full_cell_rows":N,
       "source_v2_endpoint_rows":N,"real_aligned_new_source_rows":N,
       "physical_independent_realizations":1,
       "proper_dt_one_tick_s":DT,
       "direct_26event_chemical_stoichiometric_max_scaled_residual":mres,
       "direct_26event_OTS_energy_balance_max_scaled_residual":ores,
       "original_128_160_source_secant_bound_erg_s":origrec,
       "original_t160_Bdot_source_bound_erg_s":strict_source,
       "accepted_secant_and_instant_source_interval_overlap":accepted_source_overlap,
       "global_physics":totals,
       "new_46k_cell_sign_diagnostic":{"same_sign_v2_deltaB_vs_instant_source":same_sign,
         "different_sign":N-same_sign,"candidate_net_binding_decrease":int(np.count_nonzero(D_160_161<0)),
         "source_net_binding_decrease":int(np.count_nonzero(net<0))},
       "full_source_real_physics_csv_sha256":sha(full),
       "full_source_real_physics_csv_size_bytes":full.stat().st_size,
       "source_free_witness_csv_sha256":sha(sample),
       "source_free_witness_rows":len(witnesses),
       "valid_scope":"SOURCE_CONDITIONAL_F05_T160_STOICHIOMETRIC_INSTANT_VS_ACCEPTED_AND_UNACCEPTED_V2_SECANT",
       "not_equivalent_to":["official_f05_v2_worker_acceptance","continuous_ode_global_error_bound",
             "independent_astronomical_history","observed_CMB","net_gas_heating"],
       "central_DAG":"28/88","working_DAG":"33/88","physical_fast_DAG":"4/7",
       "canonical_delta":0,"native_subagent":"NOT_RUN"}
    dest=public/"PHYSICS_RESULT.json"
    dest.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"source_status":"PHYSICAL_SOURCE_CONSUMPTION_PASS",
         "cell_rows":N,"v2_semantic_disjoint":disjoint,
         "net_Bdot":totals["Bdot_net_160_erg_s"],
         "accepted_secant":totals["accepted_128_160_mid_secant_erg_s"],
         "v2_candidate_secant":totals["candidate_160_161_mid_secant_erg_s"],
         "candidate_vs_dot_relative":totals["candidate_vs_source_rate_relative"],
         "dB_candidate":totals["delta_B_160_161_v2_mid_erg"],
         "dU_candidate":totals["delta_U_160_161_v2_mid_erg"],
         "dNe_candidate":totals["delta_Ne_160_161_v2_mid"],
         "sign_same":same_sign,
         "source_csv_sha":sha(full),"science_sha":sha(dest)},indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for n in ("rec-csv","rec-json","bass-csv","bass-json","v2-npz",
              "v2-receipt","old-v2-npz","private-dir","public-dir"):
        ap.add_argument("--"+n,required=True,type=Path)
    main(ap.parse_args())
