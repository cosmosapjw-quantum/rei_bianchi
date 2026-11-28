#!/usr/bin/env python3
"""WU R58: 46,080 original-source H/D charge-exchange photon-neutral thermal budget.

Reuse source-native REI #367 HHe thermal 26-event RHS and WU #197 historical
D trajectories. Reconstruct signed microscopic CX event flux at accepted
epochs and integrate its ENERGETIC contribution on (0,160) and (160,161).
No REI source owner mutation, no claim of actual historical D initial data.

Units: one original cell has physical H inventory NH; rate per D nucleus /s;
energy in eV converted to erg; powers erg/s per original cell; cMpc^-3
normalization inherited exactly from original source domain.
"""
from __future__ import annotations
import csv,gzip,hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
R57=Path("/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102")
R56=Path("/home/cosmosapjw/research_backups/WU088_HH/R56_REI_F05_ACCEPTED_HISTORY_D_20261102")
REI=Path("/home/cosmosapjw/archives/rei_f05_owner_accepted_trajectory_rhs_20261102/private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
REC=Path("/home/cosmosapjw/worktrees/rec-f05-accepted-trajectory-20261102/research/rec_f05_accepted_trajectory_20261102/results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz")
REI_SHA="5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913"
REC_SHA="6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c"
R57_FULL_SHA="d6c7068ef6b07319a8c7b4715a0c681941d6a2c3dbb068ccceb53e5b98b3100e"
ETA=2.5e-5
EV_ERG=1.602176634e-12
DELTA_SAVIN_EV=0.0037
CHI_H_REI_EV=13.598434599702
CHI_D_R54_EV=13.6017
CHI_D_SOURCE_CX_EV=CHI_H_REI_EV+DELTA_SAVIN_EV
DELTA_D_PHOTO_CORRECTION_EV=CHI_D_SOURCE_CX_EV-CHI_D_R54_EV
N=46080
EPOCHS=(0,64,128,160)
SCENARIOS=("H_MATCHED","ALL_NEUTRAL")

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def qstat(a):
    q=np.percentile(np.asarray(a),[0,5,50,95,100])
    return dict(zip(["min","p05","median","p95","max"],map(float,q)))

def source_reference():
    if sha(REI)!=REI_SHA or sha(REC)!=REC_SHA or sha(R57/"results/R57_ORIGINAL_NATIVE_RHS_HERMITE_DI_46080.csv.gz")!=R57_FULL_SHA:
        raise ValueError("IMMUTABLE_REI_REC_WU_SOURCE_SHA_MISMATCH")
    source_Udot=[];source_Bdot=[];source_NH=[];source_T=[]
    with gzip.open(REI,"rt") as f:
        for j,r in enumerate(csv.DictReader(f)):
            if int(r["node"])!=j%N or int(r["accepted_tick"])!=EPOCHS[j//N]:
                raise ValueError("SOURCE_REI_184320_ROW_ORDER_DRIFT")
            source_NH.append(float(r["N_H"]))
            source_Udot.append(float(r["native_thermal_rhs_erg_s"]))
            source_Bdot.append(float(r["Bdot_net_erg_s"]))
            source_T.append(float(r["T_K"]))
    if len(source_NH)!=4*N:raise ValueError("REI_SOURCE_ROW_COUNT")
    source=dict(
      NH=np.asarray(source_NH).reshape(4,N),
      Udot=np.asarray(source_Udot).reshape(4,N),
      Bdot=np.asarray(source_Bdot).reshape(4,N),
      T=np.asarray(source_T).reshape(4,N))
    totals={}
    with gzip.open(REC,"rt") as f:
        for j,r in enumerate(csv.DictReader(f)):
            t=int(r["tick"])
            if int(r["node"])!=j%N or t!=EPOCHS[j//N]:
                raise ValueError("REC_SOURCE_EPOCH_MISMATCH")
            if t not in (0,160):continue
            d=totals.setdefault(t,{"low":[],"high":[]})
            d["low"].append(float(r["U_lower_erg"]))
            d["high"].append(float(r["U_upper_erg"]))
    U0=math.fsum(0.5*(a+b) for a,b in zip(totals[0]["low"],totals[0]["high"]))
    U160=math.fsum(0.5*(a+b) for a,b in zip(totals[160]["low"],totals[160]["high"]))
    original_delta=U160-U0
    if not original_delta<0:raise ArithmeticError("ORIGINAL_REI_ACCEPTED_0TO160_DELTA_U_SIGN")
    return source,dict(original_REI_accepted_U_0_erg=U0,
                       original_REI_accepted_U_160_erg=U160,
                       original_REI_accepted_deltaU_0to160_erg=original_delta,
                       original_REI_original_Udot_at_ticks_erg_s=[
                            float(math.fsum(a)) for a in source["Udot"]])

def cx_state(r54,v,donors,snap,tick):
    y,C,R,I,P,D,B=snap
    T,x,ne=donors
    nH=v["nH"]; NH=v["NH"]
    kf,kr=r54.rates(T,v)
    x_eff=x-ETA*C
    electron_eff=ne+ETA*nH*(y-C)
    if not np.all((y>=0)&(y<=1)&(x_eff>=0)&(x_eff<=1)&(electron_eff>0)):
        raise ArithmeticError("CHEMICAL_SOURCE_CONE")
    forward=nH*kf*x_eff*(1-y)
    reverse=nH*kr*(1-x_eff)*y
    net=forward-reverse
    nuclei_rate=ETA*NH*net
    delta_erg=DELTA_SAVIN_EV*EV_ERG
    heat=-delta_erg*nuclei_rate
    bind=delta_erg*nuclei_rate
    Hion_rate=-nuclei_rate
    Dion_rate=+nuclei_rate
    erel=np.max(abs((Hion_rate+Dion_rate))/np.maximum(abs(nuclei_rate),1e-300))
    heattrace=np.max(abs(heat+bind)/np.maximum(abs(bind),1e-300))
    if erel>1e-14 or heattrace>1e-14:
        raise ArithmeticError("CHARGE_OR_CX_ENERGY_STOICHIOMETRY")
    # Fixed-original-H trace model: the corrected H+ donor uses ETA*C.
    # This negative HII source is supplied TO owner, not injected into source owner itself.
    return dict(y=y,C=C,forward=forward,reverse=reverse,net=net,
                count_flux=nuclei_rate,gas_power=heat,binding_power=bind,
                Hion_dot=Hion_rate,Dion_dot=Dion_rate,
                x_eff=x_eff,electron_eff=electron_eff,
                charge_residual=erel,energy_residual=heattrace)

def write_csv(out,fields):
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as z:
            with __import__("io").TextIOWrapper(z,encoding="ascii",newline="") as w:
                c=csv.writer(w,lineterminator="\n")
                c.writerow(fields)
                for i in range(N):
                    c.writerow([i if key=="node" else format(float(arr[i]),".17e") for key,arr in fields.items()])

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    original,ref=source_reference()
    # Lock actual original REI source data and original WU R57 source donor model.
    spec=importlib.util.spec_from_file_location("r58_source_original_r57",R57/"r57_native_rhs_history_di.py")
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    r56,r54,v,baseline,r56_sha=m.bind()
    point,source_evidence=m.source_derivatives(v)
    old_donor=r56.donors
    r56.donors=lambda q,st,mode="native_rhs_hermite":m.interp(q,point,baseline,mode)
    if np.max(abs(original["NH"][0]-v["NH"])/v["NH"])>3e-14:
        raise ValueError("ORIGINAL_REI_CELL_NH_SOURCE_DIFFERENT")
    if max(abs(original["T"][3]-np.exp(point["logT"][3])))>1e-9:
        raise ValueError("SOURCE_26EVENT_TEMP_NOT_EQUAL_R57")
    init={"H_MATCHED":point["x"][0].copy(),"ALL_NEUTRAL":np.zeros(N)}
    original_r57=json.loads((R57/"results/R57_RESULTS.json").read_text())
    historic={};percell={};source_instant={};groups={}
    for label in SCENARIOS:
        print("START_HISTORICAL_SOURCE",label,flush=True)
        history=r56.evolve(v,baseline,r54,init[label],substeps=4,mode="native_rhs_hermite")
        old=original_r57["results"][label+"_native_rhs_hermite"]["first_tick_gross_photons_total"]
        got=float(sum(ETA*((history[161][4]-history[160][4])@v["NH"])))
        if abs(got/old-1)>2e-13:
            raise ArithmeticError("R57_SOURCE_HISTORICAL_D_REPRODUCTION_MISMATCH")
        sm={};at={}
        for j,tick in enumerate(EPOCHS):
            at[tick]=cx_state(r54,v,m.interp(float(tick),point,baseline,"native_rhs_hermite"),history[tick],tick)
            cx=at[tick]
            Udot=original["Udot"][j]
            sourceU=float(math.fsum(Udot))
            signed=float(math.fsum(cx["gas_power"]))
            abs_cx=float(math.fsum(abs(cx["gas_power"])))
            absU=float(math.fsum(abs(Udot)))
            ratios=abs(cx["gas_power"])/np.maximum(abs(Udot),1e-300)
            sm[str(tick)]={
                "accepted_original_HHe_epoch":tick,
                "signed_CX_thermal_power_erg_s_per_cMpc3":signed,
                "absolute_CX_thermal_power_erg_s_per_cMpc3":abs_cx,
                "original_26event_HHe_thermal_power_erg_s_per_cMpc3":sourceU,
                "CX_absolute_over_original_global_abs_thermal_power":abs_cx/max(abs(sourceU),1e-300),
                "CX_signed_over_original_global_thermal_power":signed/sourceU,
                "CX_local_abs_heat_over_original_abs_thermal_Udot":qstat(ratios),
                "CX_local_abs_heat_over_original_abs_thermal_Udot_gt_one_pct_cells":int(np.count_nonzero(ratios>0.01)),
                "CX_rate_per_D_s":qstat(cx["net"]),
                "CX_gas_power_sign_counts":{
                    "positive":int(np.count_nonzero(cx["gas_power"]>0)),
                    "negative":int(np.count_nonzero(cx["gas_power"]<0)),
                    "zero":int(np.count_nonzero(cx["gas_power"]==0))}
                }
        firsttime=cx_state(r54,v,m.interp(161,point,baseline,"native_rhs_hermite"),history[161],161)
        c160=history[160][1];c161=history[161][1];c0=history[0][1]
        N_H=v["NH"]
        q160=-ETA*DELTA_SAVIN_EV*EV_ERG*c160
        q161=-ETA*DELTA_SAVIN_EV*EV_ERG*(c161-c160)
        q160_erg=float(math.fsum(N_H*q160))
        qfirst_erg=float(math.fsum(N_H*q161))
        original_DELTA=ref["original_REI_accepted_deltaU_0to160_erg"]
        heatfirst=q161/np.maximum(abs(v["dU"]),1e-300)
        photon_sum=(history[161][4]-history[160][4]).sum(axis=0)
        # Earlier R54 adopted a legacy chi_D from HI 13.598 eV + Savin 3.7meV.
        # Native 26-event REI source uses a more precise chi_H, so isotope
        # source-consistent model threshold shifts upward by 0.4346 meV.
        photon_excess_heat_correction=-ETA*DELTA_D_PHOTO_CORRECTION_EV*EV_ERG*photon_sum
        qphoto_correction=float(math.fsum(N_H*photon_excess_heat_correction))
        historic[label]={
            "first_tick_reproduced_parent_R57_gross_DI_photons":got,
            "original_HHe_accepted_deltaU_0to160_erg":original_DELTA,
            "CX_history_0to160_signed_gas_energy_erg_per_cMpc3":q160_erg,
            "CX_history_0to160_abs_over_original_abs_accepted_deltaU":abs(q160_erg)/abs(original_DELTA),
            "CX_native_160to161_signed_gas_energy_erg_per_cMpc3":qfirst_erg,
            "CX_native_160to161_signed_gas_energy_per_H_erg":qstat(q161),
            "CX_native_160to161_abs_over_abs_native_U_delta_cell":qstat(abs(heatfirst)),
            "CX_native_160to161_abs_over_abs_native_U_delta_cell_gt1pct":int(np.count_nonzero(abs(heatfirst)>.01)),
            "CX_native_160to161_positive_heat_cells":int(np.count_nonzero(q161>0)),
            "CX_native_160to161_negative_heat_cells":int(np.count_nonzero(q161<0)),
            "CX_native_160to161_cumulative_events_per_D":qstat(c161-c160),
            "CX_history_0to160_cumulative_events_per_D":qstat(c160),
            "source_consistent_DI_photo_threshold_correction_erg_per_cMpc3":qphoto_correction,
            "source_consistent_DI_photo_threshold_correction_over_source_thermal_deltaU_first_tick":
                abs(qphoto_correction)/max(abs(float(math.fsum(N_H*v["dU"]))),1e-300),
            "first_tick_photoevent_sum_per_D":qstat(photon_sum),
            "first_tick_photon_events_gross_per_cMpc3":got,
            "REI_26event_tick161_unaccepted":True,
            "instantaneous_original_epoch_CX":sm
            }
        percell[label]={
            "C0":c0,"C64":history[64][1],"C128":history[128][1],
            "C160":c160,"C161":c161,
            "y160":history[160][0],"y161":history[161][0],
            "Qgas_CX_0to160_erg_per_H":q160,
            "Qgas_CX_first_tick_erg_per_H":q161,
            "Qgas_DI_photo_threshold_consistency_shift_first_tick_erg_per_H":photon_excess_heat_correction}
        for tick in EPOCHS:percell[label][f"cx_rate_tick{tick}_per_D_s"]=at[tick]["net"]
        for tick in EPOCHS:percell[label][f"CX_gas_power_tick{tick}_erg_per_cell_s"]=at[tick]["gas_power"]
        groups[label]=at
        print("DONE_HISTORICAL_SOURCE",label,
              "net_history_CX_erg",q160_erg,"first_CX_erg",qfirst_erg,
              "first_photo_correction",qphoto_correction,flush=True)
    r56.donors=old_donor
    data={"node":np.arange(N),"original_H_nuclei":v["NH"],
      "native_proper_nH_cm3":v["nH"],
      "original_HII_tick160":point["x"][3],
      "original_T_tick160_K":np.exp(point["logT"][3]),
      "original_REI_26event_thermal_Udot_tick160_erg_per_s":original["Udot"][3],
      "original_REI_26event_binding_Bdot_tick160_erg_per_s":original["Bdot"][3]}
    for label in SCENARIOS:
        for k,a in percell[label].items():data[label+"_"+k]=a
    file=out/"R58_REI_F05_46080_HISTORY_CX_ENERGY.csv.gz"
    write_csv(file,data)
    witness=out/"R58_SOURCE_WITNESS_24.csv"
    ix=np.argsort(v["nH"])[np.linspace(0,N-1,24,dtype=int)]
    labels=("node","native_proper_nH_cm3","original_HII_tick160",
        "original_REI_26event_thermal_Udot_tick160_erg_per_s",
        "H_MATCHED_y160","ALL_NEUTRAL_y160",
        "H_MATCHED_C160","ALL_NEUTRAL_C160",
        "H_MATCHED_Qgas_CX_first_tick_erg_per_H",
        "ALL_NEUTRAL_Qgas_CX_first_tick_erg_per_H")
    with witness.open("w",newline="") as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(labels)
        for i in ix:w.writerow([int(i) if k=="node" else format(float(data[k][i]),".17e") for k in labels])
    out_result={
        "schema":"WU_R58_ORIGINAL_REI_F05_SOURCE_CONDITIONED_HISTORICAL_DEUTERIUM_CX_GAS_ENERGY",
        "science":"NATIVE_26EVENT_HHE_THERMAL_CROSS_OWNER_CX_SOURCE_WITH_HISTORICAL_D_MEMORY",
        "WU_parent_PR":197,"WU_parent_HEAD":"276da121638b2a024dad639a78dbb6fcbd6e01f1",
        "REI_research_head_latest_PR":369,"REI_original_26event_thermal_PR":367,
        "authority_source_SHA256":{
           "REI_original_26event_184320_row_RHS":REI_SHA,
           "REC_original_4epoch_184320_row_material":REC_SHA,
           "R57_46080_original_D_history":R57_FULL_SHA},
        "physical_contract":{
           "real_cells":N,"source_accepted_HHe_ticks":list(EPOCHS),
           "original_REI_current_official_tick":"160/131072",
           "original_REI_161":"NOT_ACCEPTED",
           "continuum_HHe_and_D_initial":"UNRESOLVED_SOURCE_CONDITIONAL",
           "eta_D_assumed":ETA,
           "Savin_forward_Dplus_endo_energy_eV":DELTA_SAVIN_EV,
           "REI_original_26event_chi_H_eV":CHI_H_REI_EV,
           "legacy_WU_R54_chi_D_eV":CHI_D_R54_EV,
           "source_Savin_offset_consistent_chi_D_eV":CHI_D_SOURCE_CX_EV,
           "legacy_D_photo_threshold_upshift_eV":DELTA_D_PHOTO_CORRECTION_EV,
           "photo_threshold_shift_only_at_fixed_events":True,
           "CX_dN_HII_plus_dN_DII_equals_0":True,
           "CX_dNe_equals_0":True,
           "CX_photon_count_equals_0":True,
           "CX_energy_binding_plus_gas_equals_0":True,
           "gas_heat_is_isolated_CX_only_not_net_HHeDI":True,
           "original_26event_HHe_photon_OTS_not_re_evolved":True},
        "original_source_reference":ref,"scenario_science":historic,
        "sources_overwritten":False,
        "validation":{"WU_R57_photon_reproduction":"CHECKED",
            "original_full_original26_source_SHA":"CHECKED",
            "CX_population_charge_energy_algebra":"CHECKED",
            "independent_disjoint_csv_audit":"PENDING"},
        "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88","FAST":"4/7","new_canonical":0},
        "gates":{"official_tick161":"HOLD","production":"HOLD","merge":False,"owner_full_coupled_HHeDI_photons_OTSThermal":"NOT_RUN"},
        "files":{"full_original_source_conditional_46080_csv":file.name,
            "full_original_source_conditional_SHA256":sha(file),
            "24cell_witness_csv":witness.name,
            "24cell_witness_SHA256":sha(witness)}}
    (out/"R58_RESULTS.json").write_text(json.dumps(out_result,indent=2,sort_keys=True)+"\n")
    print("R58_RESULT "+json.dumps({label:{
        "Q_CX_0_160_erg":sc["CX_history_0to160_signed_gas_energy_erg_per_cMpc3"],
        "CX_over_abs_rei_0_160":sc["CX_history_0to160_abs_over_original_abs_accepted_deltaU"],
        "CX_t160_power":sc["instantaneous_original_epoch_CX"]["160"]["signed_CX_thermal_power_erg_s_per_cMpc3"],
        "CX_t160_over_owner_power":sc["instantaneous_original_epoch_CX"]["160"]["CX_absolute_over_original_global_abs_thermal_power"],
        "CX_first":sc["CX_native_160to161_signed_gas_energy_erg_per_cMpc3"],
        "first_DI_threshold_shift_erg":sc["source_consistent_DI_photo_threshold_correction_erg_per_cMpc3"]}
       for label,sc in historic.items()},sort_keys=True),flush=True)
    print("R58_FULL_CSV_SHA256",sha(file),flush=True)
    return out_result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"results")
    a=p.parse_args()
    run(a.out)
