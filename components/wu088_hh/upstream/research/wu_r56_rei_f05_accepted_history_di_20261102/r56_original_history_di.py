#!/usr/bin/env python3
"""WU R56 source-conditional D histories using four exactly source-accepted REI F05 H/He snapshots.
This is a WU science consumer. It does not reconstruct the original continuous
26-event HHe trajectory nor make any assumption that D initial state was accepted.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, json, math, struct, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101")
REC=Path("/home/cosmosapjw/worktrees/rec-f05-accepted-trajectory-20261102/research/rec_f05_accepted_trajectory_20261102")
REC_CSV=REC/"results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz"
REC_CSV_SHA="6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c"
SRC_STATES={
64:("/home/cosmosapjw/archives/rei_f05_owner_original64_rust_20261101/private/FIRST64_CURRENT_RUNTIME_NONAUTHORITATIVE.state","aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"),
128:("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000128_NONAUTHORITATIVE.state","bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"),
160:("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000160_NONAUTHORITATIVE.state","74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")}
N=46080
ETA=2.5e-5
CHI_D=13.6017
TICKS=161
CHECK_TICKS=(0,64,128,160,161)
SOURCE_NODES=17
PARENT_EXPECTED_SHA="ded9c2542d05d4734370d10819d544986c89c06ef57064ea7e376f3580770885"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def native_state(p,expected):
    raw=Path(p).read_bytes()
    if sha(p)!=expected:raise ValueError("EXACT_ACCEPTED_STATE_SHA_MISMATCH")
    if raw[:8]!=b"REIADP1\0":raise ValueError("ORIGINAL_STATE_MAGIC")
    (n,)=struct.unpack_from("<Q",raw,8)
    head=json.loads(raw[16:16+n])
    if head["schema"]!=1 or head["population_shape"]!=[N,5] or head["log_temperature_shape"]!=[N]:
        raise ValueError("ORIGINAL_STATE_DTYPE_OR_SHAPE_MISMATCH")
    z=np.frombuffer(raw[16+n:],dtype="<f8")
    if z.size!=12*N:raise ValueError("ORIGINAL_STATE_BODY_SIZE")
    lo=z[:5*N].reshape(N,5)
    hi=z[5*N:10*N].reshape(N,5)
    loglo=z[10*N:11*N]
    loghi=z[11*N:12*N]
    if np.any(lo<=0) or np.any(lo>hi) or np.any(loglo>loghi):
        raise ValueError("ORIGINAL_STATE_ENCLOSURE_INVALID")
    return .5*(lo+hi),np.exp(.5*(loglo+loghi)),float(np.max((hi[:,1]-lo[:,1]))),float(np.max(loghi-loglo))

def load_source():
    if sha(PARENT/"r54_group_photon_perturbation.py")!=PARENT_EXPECTED_SHA:raise ValueError("R54_CODE_SOURCE_CHANGED")
    if sha(REC_CSV)!=REC_CSV_SHA:raise ValueError("REC195_SOURCE_CSV_CHANGED")
    sys.path.insert(0,str(PARENT))
    import r54_group_photon_perturbation as r54
    v=r54.load()
    if len(v["NH"])!=N or len(v["times"])!=SOURCE_NODES:raise ValueError("SOURCE_NATIVE_INPUT_SHAPE")
    ini=np.load(PARENT/"source_inputs/initial_material_state_z6.npz",allow_pickle=False)
    H=ini["N_HI"]+ini["N_HII"]
    if not np.array_equal(H,v["NH"]):raise ValueError("ORIGINAL_H_INVENTORY_CHANGED")
    xlist=[ini["N_HII"]/H]
    tlist=[np.asarray(ini["T_K"],float)]
    nelist=[(ini["N_HII"]+ini["N_HeII"]+2*ini["N_HeIII"])/v["V"]]
    widths={}
    for tick,(p,expected) in SRC_STATES.items():
        pop,T,wh,wlog=native_state(p,expected)
        if max(abs((pop[:,0]+pop[:,1])-H)/np.maximum(H,1.e-299))>1.e-5:
            raise ValueError("ORIGINAL_H_SOURCE_INTERVAL_CENTER_NOT_INVENTORY_CONE")
        xlist.append(pop[:,1]/H)
        tlist.append(T)
        nelist.append((pop[:,1]+pop[:,3]+2*pop[:,4])/v["V"])
        widths[str(tick)]={"max_HII_raw_interval_width_count":wh,"max_log_T_interval_width":wlog}
    # Cross-authority REC195 184320-row readback for all epochs, including volume/nuclei.
    rec_epochs={0:[],64:[],128:[],160:[]}
    with gzip.open(REC_CSV,"rt") as f:
        for j,row in enumerate(csv.DictReader(f)):
            tick=int(row["tick"]);i=int(row["node"])
            if tick not in rec_epochs or i!=j%N:raise ValueError("REC195_ROW_ORDER")
            if len(rec_epochs[tick])!=i:raise ValueError("REC195_EPOCH_ORDER")
            if abs(float(row["N_H"])/H[i]-1)>3e-15 or abs(float(row["source_volume_cm3"])/v["V"][i]-1)>3e-15:
                raise ValueError("REC195_SOURCE_PHYSICAL_IDENTITY")
            if i%4096==0:
                Te=.5*(float(row["T_lower_K"])+float(row["T_upper_K"]))
                ne=.5*(float(row["Ne_lower"])+float(row["Ne_upper"]))/v["V"][i]
                if abs(Te/tlist[[0,64,128,160].index(tick)][i]-1)>3e-7 or abs(ne/nelist[[0,64,128,160].index(tick)][i]-1)>3e-14:
                    raise ValueError("REC195_STATE_THERMODYNAMIC_REPLAY_MISMATCH")
            rec_epochs[tick].append(i)
    if any(len(vv)!=N for vv in rec_epochs.values()):raise ValueError("REC195_ROWS_NOT_184320")
    # Source-locked, unaccepted tick161 preview only as post-160 donor
    if max(abs(xlist[-1]-v["x0"]))>5e-15 or max(abs(tlist[-1]-v["T0"]))>1e-9:
        raise ValueError("R54_PREVIEW_T160_DIFFERS_FROM_REC195_ACCEPTED")
    xlist.append(v["x1"]);tlist.append(v["T1"]);nelist.append(v["ne1"])
    arr=dict(x=np.stack(xlist),T=np.stack(tlist),ne=np.stack(nelist))
    if not all(np.all((x>0)&(x<1)) for x in (arr["x"],)) or not(np.all(arr["T"]>0) and np.all(arr["ne"]>0)):
        raise ValueError("REC_ACCEPTED_SOURCE_CONE")
    return r54,v,arr,widths

def donors(q,st,mode="linear"):
    seg=min(int(np.searchsorted([64,128,160,161],q,side="right")),3)
    start=(0.,64.,128.,160.)[seg]
    end=(64.,128.,160.,161.)[seg]
    frac=max(0.,min(1.,(q-start)/(end-start)))
    if mode=="left_hold" and q<160:frac=0.
    if mode not in ("linear","left_hold"):raise ValueError("UNKNOWN_DONOR_INTERPOLATION")
    x=st["x"][seg]*(1-frac)+st["x"][seg+1]*frac
    ne=st["ne"][seg]*(1-frac)+st["ne"][seg+1]*frac
    T=st["T"][seg]*np.exp(np.log(st["T"][seg+1]/st["T"][seg])*frac)
    return T,x,ne

def source_at(q,v):
    t=q*v["dt"]
    ng=np.asarray(v["source_N"](t),float)
    ag=np.asarray(v["source_A"](t),float)
    source_gamma=float(v["source_gam"](t))
    if np.any(ng[:3]<=0) or not(ng[3]==0 and ag[3]==0):
        raise ValueError("NATIVE_PHOTON_G3_ZERO_SOURCE")
    w=ng*v["sigma"];w/=np.sum(w)
    lam=np.zeros(3);lam[:]=np.maximum(ag[:3],0.)/ng[:3]
    return ng,lam,source_gamma,w[:3]

def rhs(q,z,v,st,r54,mode):
    y,C,R,I,P,D,B=z
    T,x,ne=donors(q,st,mode)
    ng,lam,source_gamma,w=source_at(q,v)
    depleted=D/ng[:3]
    if np.any(depleted< -5e-15) or np.any(depleted>1):
        raise ValueError("PHOTON_SOURCE_DEPLETION_CONE")
    gamma_g=source_gamma*w*(1-depleted)
    eff_x=x-ETA*C
    eff_e=ne+ETA*v["nH"]*(y-C)
    if np.any(eff_x<0) or np.any(eff_x>1) or np.any(eff_e<=0):
        raise ValueError("SOURCE_CHARGE_COMPENSATION_CONE")
    kf,kr=r54.rates(T,v)
    cx=v["nH"]*(kf*eff_x*(1-y)-kr*(1-eff_x)*y)
    rr=r54.alpha_B(T)*eff_e*y
    eii=r54.beta_H(T)*eff_e*(1-y)
    photo=gamma_g[:,None]*(1-y)[None,:]
    group=ETA*(photo@v["NH"])
    dD=group-lam*D
    dB=lam*D
    # q is tick time, derivative in proper seconds * native dt
    return tuple(v["dt"]*x for x in (cx+photo.sum(axis=0)+eii-rr,
                                     cx,rr,eii,photo,dD,dB))

def add(z,k,h):
    return tuple(a+h*b for a,b in zip(z,k))

def one_step(q,z,h,v,st,r54,mode):
    k1=rhs(q,z,v,st,r54,mode)
    k2=rhs(q+h/2,add(z,k1,h/2),v,st,r54,mode)
    k3=rhs(q+h/2,add(z,k2,h/2),v,st,r54,mode)
    k4=rhs(q+h,add(z,k3,h),v,st,r54,mode)
    return tuple(a+(h/6)*(b+2*c+2*d+e) for a,b,c,d,e in zip(z,k1,k2,k3,k4))

def evolve(v,st,r54,initial,substeps=4,mode="linear"):
    z=(initial.copy(),np.zeros(N),np.zeros(N),np.zeros(N),
       np.zeros((3,N)),np.zeros(3),np.zeros(3))
    snapshots={0:tuple(a.copy() for a in z)}
    h=1./substeps
    for tick in range(TICKS):
        for j in range(substeps):
            z=one_step(tick+j*h,z,h,v,st,r54,mode)
        if tick+1 in CHECK_TICKS:
            snapshots[tick+1]=tuple(a.copy() for a in z)
            # D photo number and its depleted native field plus displaced original HHe absorption.
            y,C,R,I,P,D,B=z
            if not np.all(np.isfinite(y)) or np.any(y<-5e-12) or np.any(y>1+5e-12):
                raise ArithmeticError("HISTORY_Y_OUTSIDE_POSITIVITY_CONE")
            gross=ETA*(P@v["NH"])
            err=np.max(abs(gross-D-B)/np.maximum(gross,1e-30))
            if err>1e-11 or not(np.all(D>=0) and np.all(B>=0)):
                raise ArithmeticError("HISTORY_PHOTON_BALANCE_BROKEN")
            if np.max(abs(y-initial-C-P.sum(axis=0)-I+R))>8e-12:
                raise ArithmeticError("HISTORY_5FLUX_STOICHIOMETRY_BROKEN")
    return snapshots

def summ(a):
    a=np.asarray(a)
    return {k:float(z) for k,z in zip(["min","p05","median","p95","max"],np.percentile(a,[0,5,50,95,100]))}

def per_tick_records(v,r54,state0,snapshots,label,emitted160):
    results=[]
    for tick in CHECK_TICKS:
        y,C,R,I,P,D,B=snapshots[tick]
        photons=ETA*(P@v["NH"])
        assert abs(photons[0]-D[0]-B[0])<2e-11*max(photons[0],1.)
        rec=dict(scenario=label,tick=tick,
          fraction_y=summ(y),count_D_plus=float(np.dot(v["NH"],y)*ETA),
          gross_group_photons_per_cMpc3=[float(x) for x in photons],
          group_deficit_per_cMpc3=[float(x) for x in D],
          displaced_HHe_absorption_per_cMpc3=[float(x) for x in B],
          photoevents_per_D=summ(P.sum(axis=0)),
          source_chemical_CX_integrated_per_D=summ(C),
          original_group_G3_exact_zero=True)
        if tick==160:
            results.append(rec)
        elif tick in (0,64,128,161):
            results.append(rec)
    # Fresh first-tick 160→161 from historical D state and retained photon/CX history,
    # rather than incorrectly zeroing cumulative CX or photon field at tick160.
    a=snapshots[160];b=snapshots[161]
    dphoto=b[4]-a[4]
    if np.min(dphoto)<-1e-12:raise ArithmeticError("TICK160_161_GROSS_PHOTO_NEGATIVE")
    inc=ETA*(dphoto@v["NH"])
    E=np.asarray(v["meanE"][:3])
    photoheat=ETA*r54.EV_ERG*(E@dphoto-CHI_D*dphoto.sum(axis=0))
    latent=ETA*r54.EV_ERG*CHI_D*dphoto.sum(axis=0)
    thermal_ratio=photoheat/np.abs(v["dU"])
    photon_energy=photoheat+latent
    if np.max(abs(photon_energy-ETA*r54.EV_ERG*(E@dphoto)))>2e-27:
        raise ArithmeticError("TICK161_PHOTO_ENERGY_LEDGER")
    out=dict(label=label,original_tick_range=[160,161],
      first_tick_gross_group_photons=[float(x) for x in inc],
      first_tick_gross_photons_total=float(sum(inc)),
      first_tick_photoevents_over_native_emission=float(sum(inc)/emitted160),
      first_tick_photoelectron_heat_over_abs_native_deltaU=summ(thermal_ratio),
      first_tick_gross_heat_gt1pct_deltaU_cells=int(np.count_nonzero(thermal_ratio>.01)),
      tick160_Dplus_initial=summ(a[0]),
      tick161_Dplus_final=summ(b[0]),
      final_max_native_group_photon_depletion=float(max(b[5][i]/v["source_N"](161*v["dt"])[i] for i in range(3))),
      max_photon_conservation_residual_rel=float(np.max(abs(inc-(b[5]-a[5])-(b[6]-a[6]))/np.maximum(inc,1e-20))),
      max_full_population_ledger=float(np.max(abs(b[0]-state0-b[1]-b[4].sum(axis=0)-b[3]+b[2]))),
      max_electron_compensation_ledger=float(np.max(abs(ETA*(b[0]-state0-b[1])-ETA*(b[4].sum(axis=0)+b[3]-b[2])))))
    return results,out,dict(photo_increment=dphoto,heat=photoheat,latent=latent,ratio=thermal_ratio)

def write_gz(out,fields):
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("wb") as file:
        with gzip.GzipFile(fileobj=file,filename="",mode="wb",mtime=0,compresslevel=6) as g:
            with io.TextIOWrapper(g,encoding="ascii",newline="") as f:
                wr=csv.writer(f,lineterminator="\n")
                wr.writerow(fields)
                data=list(fields.values())
                for i in range(N):wr.writerow([i if key=="node" else format(float(arr[i]),".17e") for key,arr in fields.items()])

def run(out):
    r54,v,st,widths=load_source()
    kf,kr=r54.rates(st["T"][0],v)
    cx=kf*st["x"][0]/(kf*st["x"][0]+kr*(1-st["x"][0]))
    initial={"ALL_NEUTRAL":np.zeros(N),"H_MATCHED":st["x"][0],"CX_EQ":cx,"ALL_IONIZED":np.ones(N)}
    # Full native first [160,161] emission count reused from R54, NOT first 0-160 emission.
    r54_summary=json.loads((PARENT/"results/R54_RESULTS.json").read_text())
    emitted160=float(r54_summary["numeric"]["original_emitted_photons_native_source"])
    snapshots={};scientific={};epoch_rows=[];tick_outputs={}
    for label,y0 in initial.items():
        print("RUN",label,flush=True)
        sn=evolve(v,st,r54,y0,substeps=4,mode="linear")
        snapshots[label]=sn
        records,tick,per=per_tick_records(v,r54,y0,sn,label,emitted160)
        scientific[label]=tick
        epoch_rows.extend(records)
        tick_outputs[label]=per
        print("DONE",label,"first_tick_photons",tick["first_tick_gross_photons_total"],"y160_median",tick["tick160_Dplus_initial"]["median"],flush=True)
    # A second donor approximation on the same accepted snapshot data diagnoses
    # missing continuous-time owner trajectory; not a rigorous error bound.
    print("RUN", "H_MATCHED_LEFT_HOLD",flush=True)
    left=evolve(v,st,r54,initial["H_MATCHED"],substeps=4,mode="left_hold")
    left_rows,left_science,left_results=per_tick_records(v,r54,initial["H_MATCHED"],left,"H_MATCHED_LEFT_HOLD",emitted160)
    epoch_rows.extend(left_rows)
    # 2 versus 4 substeps for one scenario, physical solver accuracy indicator only.
    print("RUN","H_MATCHED_RK2",flush=True)
    coarse=evolve(v,st,r54,initial["H_MATCHED"],substeps=2,mode="linear")
    error=float(np.max(abs(coarse[160][0]-snapshots["H_MATCHED"][160][0])))
    if error>1e-6:raise ArithmeticError("RK2_RK4_HISTORICAL_D_INITIAL_SENSITIVITY")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    full=out/"R56_ORIGINAL_REI_HISTORICAL_D_46080.csv.gz"
    cols={"node":np.arange(N),"original_H_nuclei":v["NH"],"nH_proper_cm3":v["nH"],
      "accepted_HII_x_tick0":st["x"][0],"accepted_HII_x_tick64":st["x"][1],
      "accepted_HII_x_tick128":st["x"][2],"accepted_HII_x_tick160":st["x"][3],
      "source_T_tick0_K":st["T"][0],"source_T_tick160_K":st["T"][3],
      "initial_y_CX_equilibrium":cx}
    for label,sn in snapshots.items():
        for tick in (64,128,160,161):
            cols[f"{label}_DII_y_tick{tick}"]=sn[tick][0]
        p=snapshots[label][161][4]-snapshots[label][160][4]
        cols[f"{label}_first_tick_DI_photoevents_per_D"]=p.sum(axis=0)
        cols[f"{label}_first_tick_gross_heat_erg_per_H"]=tick_outputs[label]["heat"]
        cols[f"{label}_first_tick_heat_over_abs_native_F05_dU"]=tick_outputs[label]["ratio"]
    cols["H_MATCHED_LEFT_HOLD_DII_y_tick160"]=left[160][0]
    cols["H_MATCHED_LEFT_HOLD_first_tick_DI_photoevents_per_D"]=(left[161][4]-left[160][4]).sum(axis=0)
    write_gz(full,cols)
    small=out/"R56_REAL_SOURCE_WITNESS_24.csv"
    ix=np.unique(np.argsort(v["nH"])[np.linspace(0,N-1,24,dtype=int)])
    names=["node","nH_proper_cm3","accepted_HII_x_tick0","accepted_HII_x_tick160",
      "H_MATCHED_DII_y_tick160","ALL_NEUTRAL_DII_y_tick160",
      "ALL_IONIZED_DII_y_tick160","H_MATCHED_DII_y_tick161",
      "H_MATCHED_first_tick_DI_photoevents_per_D"]
    with small.open("w",newline="") as f:
        wr=csv.writer(f,lineterminator="\n");wr.writerow(names)
        for i in ix:wr.writerow([int(cols[k][i]) if k=="node" else format(float(cols[k][i]),".17e") for k in names])
    # Four exact accepted time snapshots; 161 is unaccepted preview donor.
    assert all(x in CHECK_TICKS for x in (0,64,128,160,161))
    b0=snapshots["ALL_NEUTRAL"];bi=snapshots["ALL_IONIZED"];bh=snapshots["H_MATCHED"]
    violations=int(np.count_nonzero((bh[160][0]<b0[160][0]-1e-10)|(bh[160][0]>bi[160][0]+1e-10)))
    if violations:raise ArithmeticError("REAL_HISTORICAL_SCENARIO_NOT_BRACKETED")
    summary={
      "schema":"WU_R56_ORIGINAL_REI_F05_ACCEPTED_HISTORY_DEUTERIUM_SOURCE_CONDITIONAL_V1",
      "status":"ORIGINAL_REI_ACCEPTED_HHE_FOUR_SNAPSHOTS_WITH_CONDITIONAL_DI_HISTORY_NOT_NATIVE_26EVENT_D",
      "WU_parent_PR":195,"WU_parent_HEAD":"20a68553c15e89a2178e5f2ad0caaff5c889aba0",
      "REI_owner_PR":365,"REI_owner_head":"fab9429140038974a98f3ad3212036b0227e600e",
      "REC_original_history_PR":195,"REC_head":"0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235",
      "source_sha256":{
        "REC195_replayed_184320_cells":REC_CSV_SHA,
        "R54_code":PARENT_EXPECTED_SHA,
        "R54_source_files":r54_summary["source_SHA256"],
        "REI_states":{str(k):v[1] for k,v in SRC_STATES.items()}},
      "physical_scope":{
        "source_accepted_ticks":[0,64,128,160],"source_first_preview_tick161":"NOT_ACCEPTED",
        "source_original_HHe_cells":N,"source_radius":"ORIGINAL_FIRST_F05_131072_TICKS",
        "proper_tick_duration_seconds":v["dt"],"source_hypothetical_eta_D":ETA,
        "source_HII_ne_T":"CERTIFIED_INTERVAL_MIDPOINTS_AT_4_ACCEPTED_TICKS",
        "between_epochs":"SOURCE_CONDITIONAL_LINEAR_X_NE_LOG_LINEAR_T",
        "second_donor":"LEFT_HOLD_DONOR_SENSITIVITY_NOT_BOUND",
        "original_HHe_photon_history":"ORIGINAL_SOURCE_FIRST_17_PCHIP_N_G_A_G_GAMMA",
        "DI_photo_opacity":"SAVIN_2002_HI_CLONED_MODEL_APPROXIMATION",
        "true_historical_D_initial":"UNKNOWN_NOT_IN_REI_ORIGINAL_26EVENT",
        "D_initial_scenarios":["ALL_NEUTRAL","H_MATCHED","CX_EQ","ALL_IONIZED"],
        "frozen_original_HHe_group_opacity":True,
        "true_gas_net_heat":"NOT_COMPUTED",
        "full_original_HHeDI_OTSPHOTON_EINSTEIN":"NOT_RUN"},
      "source_accepted_interval_halfwidths":widths,
      "scenario_tick160_161":scientific,
      "scenario_LEFT_HOLD_tick160_161":left_science,
      "epochs":epoch_rows,
      "validation":{
        "H_MATCHED_RK2_vs_RK4_DII_tick160_max_abs":error,
        "H_MATCHED_initial_extreme_enclosure_cell_violations":violations,
        "first_tick_native_source_emission_count":emitted160,
        "source_snapshot_total":4,
        "original_source_cell_epoch_records":N*4,
        "FULL_REI_OWNER_V2_NOT_RUN":True,
        "same_author_independent_audit":"PENDING",
        "native_subagent":"NOT_RUN","distinct_author":"NOT_RUN"},
      "files":{"full_csv_name":full.name,"full_csv_sha256":sha(full),
        "witness_name":small.name,"witness_sha256":sha(small)},
      "DAG":{"WU":"34/49","REI_CENTRAL":"28/88","REI_WORKING":"33/88","FAST":"4/7","new_canonical_nodes":0},
      "gates":{"official_tick161":"HOLD","production":"HOLD","main_merge":False,"auto_next_node":False}}
    (out/"R56_RESULTS.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"SUMMARY":"R56_COMPLETED_SOURCE_CONDITIONAL","R56_full_physical_sha256":summary["files"]["full_csv_sha256"],"one_tick_source_photons":emitted160,"scenarios":{key:{"DII_tick160_median":val["tick160_Dplus_initial"]["median"],"DI_photons_tick160_161":val["first_tick_gross_photons_total"],"photo_fraction_emitted":val["first_tick_photoevents_over_native_emission"]} for key,val in scientific.items()},"rk_diff":error},sort_keys=True))
    return summary

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=HERE/"results")
    args=ap.parse_args()
    run(args.out)
