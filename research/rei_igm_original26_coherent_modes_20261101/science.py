#!/usr/bin/env python3
"""Source-authentic correlated physical perturbation curves and original 26-event local maps.

All points remain in immutable tick160 parent intervals, with H/He nuclear inventories
unchanged. These 1D coherent curves DO NOT cover the complete uncertainty set X.
No global validation or canonical promotion is claimed.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parents[1]/"research/rei_igm_original26_commonparent_20261101/science.py"
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
MODES=("H_ION","HEI_HEII","HEII_HEIII","LOG_T")
CENTRAL="28/88"
WORKING="33/88"
FAST="4/7"
GATE=2e-4

def import_parent():
    spec=importlib.util.spec_from_file_location("rei_prev_original26_science",PARENT)
    if spec is None or spec.loader is None:raise ImportError(PARENT)
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)
    return m

def modes(p,lo,hi,x,xlo,xhi):
    """Nuclei-conserving affine physical lines inside the original componentwise box.

    a in [-1,1] is a *single shared parameter* changing the state across all nodes.
    Along any one line, all states p+a*delta are admissible box representatives.
    """
    result={}
    for name,i,j in (("H_ION",0,1),("HEI_HEII",2,3),("HEII_HEIII",3,4)):
        slack=np.minimum.reduce([p[:,i]-lo[:,i],hi[:,i]-p[:,i],
                                 p[:,j]-lo[:,j],hi[:,j]-p[:,j]])
        amp=0.20*np.maximum(slack,0.)
        v=np.zeros_like(p)
        v[:,i]=-amp
        v[:,j]=amp
        result[name]=(v,np.zeros_like(x),amp)
    at=0.20*np.maximum(np.minimum(x-xlo,xhi-x),0.)
    result["LOG_T"]=(np.zeros_like(p),at,at)
    return result

def validate_point(p,x,p0,x0,lo,hi,xlo,xhi,nh,nhe):
    if not (np.isfinite(p).all() and np.isfinite(x).all()):raise ValueError("nonfinite state")
    tol=3e-12
    if np.any(p<lo-tol)|np.any(p>hi+tol)|np.any(x<xlo-tol)|np.any(x>xhi+tol):
        raise ValueError("selected source state lies outside original admissible parent")
    if not np.all(p>0):raise ValueError("nonpositive atomic population")
    if np.max(abs(p[:,:2].sum(axis=1)-nh))>tol*max(1.,float(max(nh))):
        raise ValueError("H nuclei changed")
    if np.max(abs(p[:,2:5].sum(axis=1)-nhe))>tol*max(1.,float(max(nhe))):
        raise ValueError("He nuclei changed")
    return True

def interval_mid(q):
    return 0.5*(np.asarray(q.lo)+np.asarray(q.hi))

def event_response(src,mod,model,p,x,nh,t0):
    e=mod.event_box(model,mod._I(p),mod._I(np.exp(x)),t0)
    f=interval_mid(e.flux)
    dn=src.stoich_flux(f)
    if np.max(abs(dn[:,:2].sum(axis=1)))>1e-11*max(float(np.max(abs(dn))),1e-300):
        raise ValueError("original H source nuclear ledger mismatch")
    if np.max(abs(dn[:,2:5].sum(axis=1)))>1e-11*max(float(np.max(abs(dn))),1e-300):
        raise ValueError("original He source nuclear ledger mismatch")
    energy=e.resolved_heat+e.unresolved_energy+e.escaped_energy+e.chemical_energy
    if not (np.all(e.photon_identity.lo<=0)&np.all(e.photon_identity.hi>=0)&
            np.all(energy.lo<=0)&np.all(energy.hi>=0)):
        raise ValueError("source photon or energy interval failed inclusion")
    electrons=p[:,1]+p[:,3]+2*p[:,4]
    T=np.exp(x)
    kb=1.380649e-16
    ev_erg=1.602176634e-12
    utherm=1.5*kb*T*(p[:,:5].sum(axis=1)+electrons)/nh
    uion=ev_erg*(mod.rim.CHI_H_EV*p[:,1]+mod.rim.CHI_HEI_EV*p[:,3]
           +(mod.rim.CHI_HEI_EV+mod.rim.CHI_HEII_EV)*p[:,4])/nh
    return dict(electron_per_H=electrons/nh,
        electron_rate_per_H_s=(dn[:,1]+dn[:,3]+2*dn[:,4])/nh,
        photoheat_erg_per_H_s=interval_mid(e.photo_heat)/nh,
        temperature_K=T,
        thermal_energy_erg_per_H=utherm,
        ionization_binding_energy_erg_per_H=uion)

def original_map(mod,model,base,p,x,nh,nhe,t0,t1):
    m=(t0+t1)/2
    P,X=mod._I(p),mod._I(x)
    out={}
    full=mod.run_step(model,base,parent_pop=P,parent_logt=X,
                      t0=t0,t1=t1,total_h=nh,total_he=nhe)
    out["full"]=full.classification
    if not full.certified:return None,out
    first=mod.run_step(model,base,parent_pop=P,parent_logt=X,
                       t0=t0,t1=m,total_h=nh,total_he=nhe)
    out["first_half"]=first.classification
    if not first.certified:return None,out
    second=mod.run_step(model,base,parent_pop=first.population,
                       parent_logt=first.log_temperature,t0=m,t1=t1,
                       total_h=nh,total_he=nhe)
    out["second_half"]=second.classification
    if not second.certified:return None,out
    quantities={}
    for key,i,s in (("x_HII",1,nh),("x_HeII",3,nhe),("x_HeIII",4,nhe)):
        f0,f1=full.population.lo[:,i]/s,full.population.hi[:,i]/s
        h0,h1=second.population.lo[:,i]/s,second.population.hi[:,i]/s
        quantities[key]=(f0,f1,h0,h1)
    quantities["log_T"]=(np.asarray(full.log_temperature.lo),
                         np.asarray(full.log_temperature.hi),
                         np.asarray(second.log_temperature.lo),
                         np.asarray(second.log_temperature.hi))
    result={}
    for key,(f0,f1,h0,h1) in quantities.items():
        lo=f0-h1;hi=f1-h0
        if np.any(lo>hi):raise ValueError("original map difference interval inverted")
        result[key]={"center":0.5*(lo+hi),
                     "lower":lo,"upper":hi,
                     "point_interval_upper":np.maximum(abs(lo),abs(hi))}
    return result,out

def write_gzip(path,headers,records):
    with open(path,"wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as g:
            with io.TextIOWrapper(g,newline="",encoding="utf-8") as t:
                w=csv.writer(t);w.writerow(headers)
                for rec in records:w.writerow(rec)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(lane,out):
    if lane not in LANES:raise ValueError("unknown original lane")
    parent=import_parent()
    parent.LANE=lane
    src,mod,model,base,p0,x0,nh,nhe,t0,t1=parent.init_source()
    st=src.archived_tick160(parent.ORIGINAL_ARCHIVE)[lane]
    if st["array_sha"]!=parent.ARRAY_SHA:raise ValueError("original state SHA mismatched")
    source_modes=modes(p0,st["lo"],st["hi"],x0,st["tl"],st["th"])
    validate_point(p0,x0,p0,x0,st["lo"],st["hi"],st["tl"],st["th"],nh,nhe)
    trace={"schema":"REI_IGM_ORIGINAL26_COHERENT_PHYSICAL_MODE_TICK160_V1",
       "lane":lane,"original_parent_PR":327,"original_source_array_sha256":parent.ARRAY_SHA,
       "original_archive_sha256":src.ARCHIVE_SHA,"original_tick":[160,161],
       "original_local_error_gate":GATE,"source_owned_model":"original_26event_MPRK22_SDIRK2",
       "scientific_scope":"four 1D correlated physical paths within X, not all-X enclosure",
       "uncertain_source_parameters_correlated_all_X":False,
       "source_model_realizations_not_replaced":True,
       "canonical_delta":0,"central_reported":CENTRAL,"working_reported":WORKING,
       "physical_fast_reported":FAST,"production":"HOLD","results":{}}
    out.mkdir(parents=True,exist_ok=True)
    path=out/"MODE_RESULTS.json"
    def save():path.write_text(json.dumps(trace,indent=2,sort_keys=True,default=str)+"\n")
    save()
    physical=[]
    mode_conditions=[("CENTER",0,np.zeros_like(p0),np.zeros_like(x0),np.zeros_like(x0))]
    for name,(v,w,amp) in source_modes.items():
        for sign in (-1,1):
            p=p0+sign*v;x=x0+sign*w
            validate_point(p,x,p0,x0,st["lo"],st["hi"],st["tl"],st["th"],nh,nhe)
            mode_conditions.append((name,sign,v,w,amp))
    baseline=event_response(src,mod,model,p0,x0,nh,t0)
    all_model_runs={}
    for mode,sign,v,w,amp in mode_conditions:
        p=p0+sign*v;x=x0+sign*w
        e=baseline if mode=="CENTER" else event_response(src,mod,model,p,x,nh,t0)
        key=mode+("_PLUS" if sign==1 else "_MINUS" if sign==-1 else "")
        physical.append((key,sign,amp,e))
        fields=[e["electron_per_H"],e["electron_rate_per_H_s"],
                e["photoheat_erg_per_H_s"],e["temperature_K"],
                e["thermal_energy_erg_per_H"],e["ionization_binding_energy_erg_per_H"]]
        if any(np.size(a)!=46080 or not np.isfinite(a).all() for a in fields):
            raise ValueError("nonfinite original physical response")
        rec={"source_rows":46080,"temperature_amp_max_log" :float(np.max(w)),
             "amplitude_max":float(np.max(amp)),
             "nonzero_amplitude_nodes":int(np.count_nonzero(amp)),
             "source_electron_rate_mean":float(np.mean(e["electron_rate_per_H_s"])),
             "source_photon_energy_preserved":True,
             "source_nuclear_inventory_preserved":True,
             "map_status":"NOT_RUN"}
        trace["results"][key]=rec;save()
        try:
            mapped,status=original_map(mod,model,base,p,x,nh,nhe,t0,t1)
            rec["map_status"]="CERTIFIED_POINT" if mapped is not None else "MAP_LOCAL_CERTIFICATE_FAILED"
            rec["map_stage_classifications"]=status
            if mapped is not None:
                rec["point_map_max_output_upper"]={k:float(np.max(t["point_interval_upper"])) for k,t in mapped.items()}
                rec["point_map_logT_defect_median_center"]=float(np.median(mapped["log_T"]["center"]))
                all_model_runs[key]=mapped
        except Exception as err:
            rec["map_status"]="ERROR"
            rec["error"]=str(err)
        save()
        print("REAL_ORIGINAL_PHYSICAL_MODE",json.dumps({"lane":lane,"key":key,
            "status":rec["map_status"],
            "max_logT_point_upper":rec.get("point_map_max_output_upper",{}).get("log_T")}),flush=True)
    records=[]
    for key,sign,amp,e in physical:
        for i in range(46080):
            records.append((i,key,sign,format(float(amp[i]),".17g"),
               format(float(e["electron_per_H"][i]),".17g"),
               format(float(e["electron_rate_per_H_s"][i]),".17g"),
               format(float(e["photoheat_erg_per_H_s"][i]),".17g"),
               format(float(e["temperature_K"][i]),".17g"),
               format(float(e["thermal_energy_erg_per_H"][i]),".17g"),
               format(float(e["ionization_binding_energy_erg_per_H"][i]),".17g")))
    csvpath=out/"ORIGINAL_SOURCE_PHYSICAL_MODES_414720.csv.gz"
    trace["source_csv_sha256"]=write_gzip(csvpath,["node","mode","sign",
       "absolute_amplitude","electron_per_H","electron_rate_per_H_s",
       "photoheat_erg_per_H_s","temperature_K",
       "thermal_energy_erg_per_H","ionization_binding_energy_erg_per_H"],records)
    trace["source_physical_rows"]=len(records)
    trace["point_map_cases"]=len(mode_conditions)
    trace["point_map_certified_cases"]=len(all_model_runs)
    if all_model_runs:
        maprows=[]
        for key,val in all_model_runs.items():
            for i in range(46080):
                for q in ("log_T","x_HII","x_HeII","x_HeIII"):
                    a=val[q]
                    maprows.append((i,key,q,format(float(a["center"][i]),".17g"),
                        format(float(a["lower"][i]),".17g"),
                        format(float(a["upper"][i]),".17g")))
        mfile=out/"ORIGINAL_POINT_DIFF_MAPS.csv.gz"
        trace["point_map_csv_sha256"]=write_gzip(mfile,["node","mode","quantity",
            "difference_center","difference_lower","difference_upper"],maprows)
        trace["point_map_data_rows"]=len(maprows)
    trace["all_X_joint_difference_certificate"]="NOT_CONSTRUCTED"
    trace["source_evaluation_scope"]="SOURCE_CONDITIONAL_1D_MODE_CURVES"
    trace["original_whole_interval_accepted"]=False
    save()
    print("REAL_MODE_FINAL",json.dumps({"lane":lane,"rows":len(records),
       "point_cases":len(mode_conditions),"certified_cases":len(all_model_runs),
       "central":CENTRAL,"canonical_delta":0}),flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--lane",required=True,choices=LANES)
    a.add_argument("--out",type=Path,required=True)
    opt=a.parse_args()
    run(opt.lane,opt.out.resolve())

if __name__=="__main__":main()
