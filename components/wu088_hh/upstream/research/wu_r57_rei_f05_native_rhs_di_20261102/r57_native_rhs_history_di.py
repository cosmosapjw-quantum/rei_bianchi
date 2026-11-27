#!/usr/bin/env python3
"""WU R57: native accepted HII/electron/temperature RHS anchored H/He donor for D histories.

Direct original 26-event per-cell derivatives at 0/64/128/160 via byte-locked
REI367 source plus original REC195 states. C1 cubic Hermite is an interpolation
of native endpoints and source instantaneous derivatives, NOT an accepted
continuous original REI trajectory or rigorous enclosed solution.
"""
from __future__ import annotations
import csv,gzip,json,hashlib,importlib.util,sys,math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
R56ROOT=Path("/home/cosmosapjw/research_backups/WU088_HH/R56_REI_F05_ACCEPTED_HISTORY_D_20261102")
OLD_REI=Path("/home/cosmosapjw/archives/rei_f05_owner_accepted_trajectory_rhs_20261102/private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
NEW_REI=ROOT/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
LOCKED_OLD="5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913"
LOCKED_NEW="d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e"
PARENT_R56_CODE_SHA=None # dynamically recorded, exact SHA in output
TICK_NODES=(0.,64.,128.,160.,161.)
N=46080

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def bind():
    if sha(OLD_REI)!=LOCKED_OLD or sha(NEW_REI)!=LOCKED_NEW:
        raise ValueError("NATIVE_REI367_SHA_SOURCE_DRIFT")
    source_file=R56ROOT/"r56_original_history_di.py"
    spec=importlib.util.spec_from_file_location("r57_locked_original_wu_r56",source_file)
    if not(spec and spec.loader):raise RuntimeError("R56_MODULE_NOT_FOUND")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    r54,v,baseline,_=mod.load_source()
    if any(len(baseline[k])!=5 for k in ("x","ne","T")):raise ValueError("R56_SNAPSHOT_COUNT")
    return mod,r54,v,baseline,sha(source_file)

def source_derivatives(v):
    """Compare ALL original 184,320 RHS source fields bytewise with unchanged REI #367."""
    states={key:[] for key in ["N_HII_point","N_HeII_point","N_HeIII_point","N_e","T_K","dN_HII_dt_per_s","dN_HeII_dt_per_s","dN_HeIII_dt_per_s","dN_e_dt_per_s","dlogT_dt_per_s","N_H","N_He","Udot_thermochemical_erg_s"]}
    count=0
    max_electron_res=0.;max_thermo_res=0.;mismatch=0
    with gzip.open(OLD_REI,"rt") as original,gzip.open(NEW_REI,"rt") as ff:
        ref=csv.DictReader(original);new=csv.DictReader(ff)
        if new.fieldnames[:20]!=ref.fieldnames:raise ValueError("UPSTREAM_20COL_FIELDS_CHANGED")
        for a,b in zip(ref,new,strict=True):
            i=int(b["node"]);tick=int(b["accepted_tick"])
            if i!=count%N or tick!=(0,64,128,160)[count//N]:
                raise ValueError("REI367_ROW_ORDER_CHANGED")
            if any(a[k]!=b[k] for k in ref.fieldnames):
                mismatch+=1
            for key in states:states[key].append(float(b[key]))
            e_dot=float(b["dN_e_dt_per_s"])
            byspecies=float(b["dN_HII_dt_per_s"])+float(b["dN_HeII_dt_per_s"])+2*float(b["dN_HeIII_dt_per_s"])
            max_electron_res=max(max_electron_res,abs(e_dot-byspecies)/max(abs(e_dot),abs(byspecies),1.e-250))
            N_tot=float(b["N_H"])+float(b["N_He"])+float(b["N_e"])
            U=(1.5*1.380649e-16)*N_tot*float(b["T_K"])
            calc=float(b["Udot_thermochemical_erg_s"])/U-e_dot/N_tot
            direct=float(b["dlogT_dt_per_s"])
            max_thermo_res=max(max_thermo_res,abs(calc-direct)/max(abs(calc),abs(direct),1.e-120))
            count+=1
    if count!=4*N or mismatch or max_electron_res>5.e-13 or max_thermo_res>5.e-12:
        raise ArithmeticError("NATIVE_ORIGINAL_26EVENT_RHS_SOURCE_PARITY")
    z={key:np.asarray(x).reshape(4,N) for key,x in states.items()}
    if np.max(abs(z["N_H"]-v["NH"])/np.maximum(v["NH"],1.e-290))>5.e-14:
        raise ValueError("ORIGINAL_NATIVE_H_NUCLEI_CHANGED")
    st={}
    st["x"]=z["N_HII_point"]/z["N_H"]
    st["ne"]=z["N_e"]/v["V"]
    st["logT"]=np.log(z["T_K"])
    dt=v["dt"]
    st["dx"]=z["dN_HII_dt_per_s"]/z["N_H"]*dt
    st["dne"]=z["dN_e_dt_per_s"]/v["V"]*dt
    st["dlogT"]=z["dlogT_dt_per_s"]*dt
    # Source-manifold coordinates: H is logit, He is 3-state softmax
    # with HeI computed by exact nucleus conservation.
    heI=z["N_He"]-z["N_HeII_point"]-z["N_HeIII_point"]
    if not np.all(heI>0):raise ArithmeticError("ORIGINAL_HEI_POSITIVE_SOURCE_REQUIRED")
    x=st["x"]
    st["hlogit"]=np.log(x/(1-x))
    st["dhlogit"]=st["dx"]/(x*(1-x))
    st["he_tot"]=z["N_He"]
    st["NH"]=z["N_H"]
    st["V"]=v["V"]
    st["he_logII"]=np.log(z["N_HeII_point"]/heI)
    st["he_logIII"]=np.log(z["N_HeIII_point"]/heI)
    dheI=-(z["dN_HeII_dt_per_s"]+z["dN_HeIII_dt_per_s"])
    st["dhe_logII"]=dt*(z["dN_HeII_dt_per_s"]/z["N_HeII_point"]-dheI/heI)
    st["dhe_logIII"]=dt*(z["dN_HeIII_dt_per_s"]/z["N_HeIII_point"]-dheI/heI)
    return st,dict(rows=count,mismatch=mismatch,max_relative_electron_identity=max_electron_res,max_relative_logT_energy_identity=max_thermo_res)

def interp(q,st,baseline,mode):
    tick=float(q)
    seg=int(np.searchsorted([64,128,160,161],tick,side="right"))
    seg=min(seg,3)
    a=TICK_NODES[seg];b=TICK_NODES[seg+1]
    u=min(1.,max(0.,(tick-a)/(b-a)))
    if seg==3: # never regard original tick161 preview as a source-accepted RHS
        x=st["x"][3]*(1-u)+baseline["x"][4]*u
        e=st["ne"][3]*(1-u)+baseline["ne"][4]*u
        ln=st["logT"][3]*(1-u)+np.log(baseline["T"][4])*u
        return np.exp(ln),x,e
    if mode=="owner_point_linear":
        x=(1-u)*st["x"][seg]+u*st["x"][seg+1]
        e=(1-u)*st["ne"][seg]+u*st["ne"][seg+1]
        ln=(1-u)*st["logT"][seg]+u*st["logT"][seg+1]
    elif mode=="native_rhs_hermite":
        h=(b-a)
        h00=2*u**3-3*u**2+1
        h10=u**3-2*u**2+u
        h01=-2*u**3+3*u**2
        h11=u**3-u**2
        def H(y,dy):
            return h00*y[seg]+h10*h*dy[seg]+h01*y[seg+1]+h11*h*dy[seg+1]
        # Logit / 3-species softmax guarantee source H and He positivity,
        # nuclear conservation and HHe electron charge at EVERY interpolated t.
        # They also preserve original source first derivatives at each endpoint.
        logistic=H(st["hlogit"],st["dhlogit"])
        x=np.exp(-np.logaddexp(0.,-logistic))
        eta2=H(st["he_logII"],st["dhe_logII"])
        eta3=H(st["he_logIII"],st["dhe_logIII"])
        anchor=np.maximum(0.,np.maximum(eta2,eta3))
        e0=np.exp(-anchor)
        e2=np.exp(eta2-anchor)
        e3=np.exp(eta3-anchor)
        denom=e0+e2+e3
        heII=st["he_tot"][seg]*(e2/denom)
        heIII=st["he_tot"][seg]*(e3/denom)
        e=(x*st["NH"][seg]+heII+2*heIII)/st["V"]
        ln=H(st["logT"],st["dlogT"])
    else:raise ValueError("NONPHYSICAL_R57_DONOR_MODE")
    if np.any((x<0)|(x>1)) or np.any(e<=0) or np.any(~np.isfinite(ln)):
        raise ArithmeticError("HERMITE_OWNER_SOURCE_DONOR_LEAVES_PHYSICAL_CONE")
    return np.exp(ln),x,e

def qstat(a):
    vals=np.percentile(a,[0,5,50,95,100])
    return dict(zip(("min","p05","median","p95","max"),map(float,vals)))

def validate_donor(st,baseline):
    tests={}
    for tick in (0,64,128,160):
        idx=(0,64,128,160).index(tick)
        p=interp(tick,st,baseline,"native_rhs_hermite")
        tests[str(tick)]=dict(max_x_abs=float(np.max(abs(p[1]-st["x"][idx]))),
                              max_ne_rel=float(np.max(abs(p[2]-st["ne"][idx])/st["ne"][idx])),
                              max_T_rel=float(np.max(abs(p[0]-np.exp(st["logT"][idx]))/np.exp(st["logT"][idx]))))
    # original 26-event RHS slope identity checked through finite differences at
    # each knot side; no derivative assumption at tick160→161 preview.
    mids={};maxdev=0.
    for tick in (0,64,128):
        t=float(tick)
        eps=1e-4
        f0=interp(t,st,baseline,"native_rhs_hermite")
        f1=interp(t+eps,st,baseline,"native_rhs_hermite")
        j=(0,64,128).index(tick)
        errx=float(np.max(abs((f1[1]-f0[1])/eps-st["dx"][j])))
        erre=float(np.max(abs((f1[2]-f0[2])/eps-st["dne"][j])/np.maximum(np.maximum(abs(st["dne"][j]),st["ne"][j]),1.e-100)))
        errln=float(np.max(abs((np.log(f1[0])-np.log(f0[0]))/eps-st["dlogT"][j])))
        mids[str(tick)]=dict(dx_tick_abs=errx,dne_relscale=erre,dlogT_tick_abs=errln)
    for q in np.linspace(0,160,33):
        a=interp(q,st,baseline,"native_rhs_hermite")
        b=interp(q,st,baseline,"owner_point_linear")
        maxdev=max(maxdev,float(np.max(abs(a[1]-b[1]))))
    return dict(endpoints=tests,source_slope_checks=mids,
      Hermite_vs_ownerpoint_linear_max_abs_x_over_33_knots=maxdev,
      source_point_minus_R56_midpoint_tick160_x=qstat(st["x"][3]-baseline["x"][3]),
      source_point_minus_R56_midpoint_tick160_T_K=qstat(np.exp(st["logT"][3])-baseline["T"][3]),
      source_point_minus_R56_midpoint_tick160_ne_cm3=qstat(st["ne"][3]-baseline["ne"][3]))

def run(out):
    r56,r54,v,baseline,r56_sha=bind()
    point,verify=source_derivatives(v)
    diagnostics=validate_donor(point,baseline)
    # Original RHS slopes measured at four accepted endpoints; Hermite is a
    # source-tangent interpolation, not native exact 26-event dense output.
    original_donors=r56.donors
    def bridge(q,st,mode="native_rhs_hermite"):
        return interp(q,point,baseline,mode)
    r56.donors=bridge
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    previous=json.loads((R56ROOT/"results/R56_RESULTS.json").read_text())
    native_emitted=previous["validation"]["first_tick_native_source_emission_count"]
    init={"ALL_NEUTRAL":np.zeros(N),"H_MATCHED":point["x"][0].copy()}
    gathered={};states={};records={}
    for label,mode in (("H_MATCHED","native_rhs_hermite"),
                       ("H_MATCHED","owner_point_linear"),
                       ("ALL_NEUTRAL","native_rhs_hermite"),
                       ("ALL_NEUTRAL","owner_point_linear")):
        name=label+"_"+mode
        print("R57_RUN",name,flush=True)
        sn=r56.evolve(v,baseline,r54,init[label],substeps=4,mode=mode)
        hist,summ,arr=r56.per_tick_records(v,r54,init[label],sn,name,native_emitted)
        gathered[name]=summ;states[name]=sn;records[name]=arr
        print("R57_DONE",name,"first_tick_photons",summ["first_tick_gross_photons_total"],"y160_median",summ["tick160_Dplus_initial"]["median"],flush=True)
    # Use full-source original output R56 at 46080 cells as separate historical
    # comparison, explicitly not exact same accepted-point interpolation.
    old=R56ROOT/"results/R56_ORIGINAL_REI_HISTORICAL_D_46080.csv.gz"
    base_rows={}
    with gzip.open(old,"rt") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=N:raise ValueError("R56_ORIGINAL_SOURCE_FULL_CSV_MISSING")
    full={
       "node":np.arange(N),"original_H_nuclei":v["NH"],"source_nH_proper_cm3":v["nH"],
       "native_HII_tick0":point["x"][0],"native_HII_tick160":point["x"][3],
       "R56_HII_midpoint_tick160":baseline["x"][3],
       "native_dHII_dTick_tick160":point["dx"][3],
       "native_dNe_dTick_tick160":point["dne"][3],
       "native_dlogT_dTick_tick160":point["dlogT"][3],
    }
    for name,sn in states.items():
        full[name+"_DII_tick160"]=sn[160][0]
        full[name+"_DII_tick161"]=sn[161][0]
        full[name+"_DI_gross_photo_per_D_160to161"]=(sn[161][4]-sn[160][4]).sum(axis=0)
        full[name+"_DI_gross_photoheat_erg_per_H_160to161"]=records[name]["heat"]
    base_y=np.array([float(r["H_MATCHED_DII_y_tick160"]) for r in rows])
    full["R56_H_MATCHED_DII_tick160"]=base_y
    out_file=out/"R57_ORIGINAL_NATIVE_RHS_HERMITE_DI_46080.csv.gz"
    r56.write_gz(out_file,full)
    h=states["H_MATCHED_native_rhs_hermite"];l=states["H_MATCHED_owner_point_linear"]
    n=states["ALL_NEUTRAL_native_rhs_hermite"];nl=states["ALL_NEUTRAL_owner_point_linear"]
    delta=dict(H_MATCHED_y160_Hermite_minus_pointlinear=qstat(h[160][0]-l[160][0]),
      H_MATCHED_y160_Hermite_minus_R56=qstat(h[160][0]-base_y),
      ALL_NEUTRAL_y160_Hermite_minus_pointlinear=qstat(n[160][0]-nl[160][0]))
    output=dict(schema="WU_R57_ORIGINAL_REI_F05_NATIVE_RHS_C1_HERMITE_DI_HISTORY_V1",
      scientific_scope="SOURCE_AUTHENTIC_NATIVE_26EVENT_ENDPOINT_TANGENT_C1_INTERPOLATION_NOT_OWNED_CONTINUOUS_TRAJECTORY",
      immutable_parent_WU_PR196="2d52baa98bd97b513a2cdad2f2c1fe1b5e9917b0",
      source_original_REI367="b9cd64afee16dc4c0e74aa39b00c831df626c777",
      source_original_REI367_20field_private_sha256=LOCKED_OLD,
      new_source_original_derivative_27field_sha256=LOCKED_NEW,
      source_R56_code_SHA256=r56_sha,
      native_four_epoch_exact_20field_parity=verify,
      accepted_source_derivative_consistency=diagnostics,
      accepted_original_material_ticks=[0,64,128,160],
      historical_initial_D="NOT_SOURCE_AUTHENTIC",
      continuous_original_26event_owner_trajectory="NOT_RECONSTRUCTED",
      original_26event_derivative_source=True,
      real_original_source_cells=N,
      source_interpolants=["NATIVE_RHS_HERMITE","OWNER_POINT_LINEAR"],
      y160_differences=delta,
      results=gathered,
      prior_R56_scenarios={s:previous["scenario_tick160_161"][s] for s in ("ALL_NEUTRAL","H_MATCHED")},
      numerical={"R56_original_source_nuclear_units":"photons_per_cMpc3","gross_not_net_heat":True},
      original_rei_tick161="HOLD",
      science_decision="EXPLORATORY_SOURCE_TANGENT_SENSITIVITY_ONLY",
      DAG={"WU":"34/49","REI_CENTRAL":"28/88","REI_WORKING":"33/88","FAST":"4/7","canonical_delta":0},
      files={"physical_full":out_file.name,"sha256":sha(out_file)})
    (out/"R57_RESULTS.json").write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"R57_SCIENCE":"REAL_46080_SOURCE_RHS_D_MEMORY","H_MATCHED_HERMITE_PHOTONS":gathered["H_MATCHED_native_rhs_hermite"]["first_tick_gross_photons_total"],"H_MATCHED_POINT_LINEAR_PHOTONS":gathered["H_MATCHED_owner_point_linear"]["first_tick_gross_photons_total"],"NEUTRAL_HERMITE_PHOTONS":gathered["ALL_NEUTRAL_native_rhs_hermite"]["first_tick_gross_photons_total"],"SOURCE_PARITY":verify,"FULL_CSV_SHA256":sha(out_file)},sort_keys=True))
    r56.donors=original_donors
    return output

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"results")
    args=parser.parse_args()
    run(args.out)
