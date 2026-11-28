#!/usr/bin/env python3
"""R56 adversarial readback: independent standard-library 46k-cell summation,
native accepted-state SHA and a disjoint SciPy single-cell fixed-photon IVP.
No imports from the R56 generator. This is a same-author, not distinct referee.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,math,struct,sys
from pathlib import Path
from bisect import bisect_right
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
PARENT=Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101")
SCENARIOS=("ALL_NEUTRAL","H_MATCHED","CX_EQ","ALL_IONIZED")
SOURCE_STATES={
64:("/home/cosmosapjw/archives/rei_f05_owner_original64_rust_20261101/private/FIRST64_CURRENT_RUNTIME_NONAUTHORITATIVE.state","aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"),
128:("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000128_NONAUTHORITATIVE.state","bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"),
160:("/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000160_NONAUTHORITATIVE.state","74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")}
ETA=2.5e-5
N=46080
RATES=PARENT/"source_inputs/SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv"

def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def node_donors(indices):
    """Independent native f64 state read. Only selected witness nodes for DOP853."""
    init=np.load(PARENT/"source_inputs/initial_material_state_z6.npz",allow_pickle=False)
    H=init["N_HI"]+init["N_HII"]
    v=init["W_node"]*(3.085677581491367e24)**3/(1+5.95)**3
    points={}
    for i in indices:
        ne0=init["N_HII"][i]+init["N_HeII"][i]+2*init["N_HeIII"][i]
        points[i]={0:{"x":float(init["N_HII"][i]/H[i]),"ne":float(ne0/v[i]),
                       "T":float(init["T_K"][i]),"nH":float(H[i]/v[i])}}
    for tick,(path,sha) in SOURCE_STATES.items():
        if digest(path)!=sha:raise AssertionError("IMMUTABLE_REI_STATE_SHA_"+str(tick))
        z=Path(path).read_bytes()
        if z[:8]!=b"REIADP1\0":raise AssertionError("STATE_MAGIC")
        n=struct.unpack_from("<Q",z,8)[0]
        head=json.loads(z[16:16+n])
        assert head["population_shape"]==[N,5]
        a=np.frombuffer(z[16+n:],dtype="<f8")
        assert a.size==N*12
        plo=a[:N*5].reshape(N,5); phi=a[N*5:N*10].reshape(N,5)
        logs_lo=a[N*10:N*11];logs_hi=a[N*11:N*12]
        for i in indices:
            p=.5*(plo[i]+phi[i])
            ne=p[1]+p[3]+2*p[4]
            points[i][tick]={"x":float(p[1]/H[i]),"ne":float(ne/v[i]),
                              "T":float(math.exp(.5*(logs_lo[i]+logs_hi[i]))),
                              "nH":float(H[i]/v[i])}
    return points

def k_rates(T,table):
    ln=math.log(T)
    xs,kf,kr=table
    j=max(0,min(bisect_right(xs,ln)-1,len(xs)-2))
    u=min(1.,max(0.,(ln-xs[j])/(xs[j+1]-xs[j])))
    return math.exp(kf[j]*(1-u)+kf[j+1]*u),math.exp(kr[j]*(1-u)+kr[j+1]*u)

def audit(out,history_samples=12):
    out=Path(out)
    data=json.loads((out/"R56_RESULTS.json").read_text())
    file=out/data["files"]["full_csv_name"]
    if digest(file)!=data["files"]["full_csv_sha256"]:raise AssertionError("FULL_PHYSICAL_DATA_SHA_CHANGED")
    if digest(out/data["files"]["witness_name"])!=data["files"]["witness_sha256"]:
        raise AssertionError("WITNESS_SHA_CHANGED")
    for tick,(path,h) in SOURCE_STATES.items():
        if digest(path)!=h:raise AssertionError("SOURCE_STATE_SHA_"+str(tick))
    with RATES.open(newline="") as f:rs=list(csv.DictReader(f))
    assert len(rs)==47
    table=([math.log(float(r["T_K"])) for r in rs],
           [math.log(float(r["k_forward_cm3_s"])) for r in rs],
           [math.log(float(r["k_reverse_cm3_s"])) for r in rs])
    photons={s:[] for s in SCENARIOS}
    residual_max={s:0. for s in SCENARIOS}
    y_violations={s:0 for s in SCENARIOS}
    n=0;selected={};max_CX_stationary=0.; source_matches=0
    with gzip.open(file,"rt",newline="") as f:
        for row in csv.DictReader(f):
            i=int(row["node"])
            if i!=n:raise AssertionError("R56_CELL_ORDER")
            n+=1
            nh=float(row["original_H_nuclei"])
            x0=float(row["accepted_HII_x_tick0"])
            x160=float(row["accepted_HII_x_tick160"])
            if not(0<x0<1 and 0<x160<1 and nh>0):raise AssertionError("SOURCE_CELL")
            kf,kr=k_rates(float(row["source_T_tick0_K"]),table)
            cx=kf*x0/(kf*x0+kr*(1-x0))
            max_CX_stationary=max(max_CX_stationary,abs(cx-float(row["initial_y_CX_equilibrium"])))
            for scenario in SCENARIOS:
                y=[float(row[f"{scenario}_DII_y_tick{tick}"]) for tick in (64,128,160,161)]
                if any((z<0 or z>1) for z in y):y_violations[scenario]+=1
                photon=float(row[f"{scenario}_first_tick_DI_photoevents_per_D"])
                if photon<0:raise AssertionError("NEGATIVE_PHOTO_EVENTS")
                photons[scenario].append(ETA*nh*photon)
                heat=float(row[f"{scenario}_first_tick_gross_heat_erg_per_H"])
                ratio=float(row[f"{scenario}_first_tick_heat_over_abs_native_F05_dU"])
                if heat<0 or ratio<0:raise AssertionError("NEGATIVE_GROSS_HEAT")
            if i%4096==0:selected[i]=dict(row)
    if n!=N:raise AssertionError("R56_ROWS_NOT_46080")
    if max_CX_stationary>1.e-12:raise AssertionError("CX_SOURCE_RATE_RECONSTRUCTION")
    actual={}
    for scenario in SCENARIOS:
        sumph=math.fsum(photons[scenario])
        supplied=data["scenario_tick160_161"][scenario]["first_tick_gross_photons_total"]
        residual_max[scenario]=abs(sumph-supplied)/max(sumph,1.)
        if residual_max[scenario]>3.e-12:raise AssertionError("FIRST_TICK_PHOTONS_RECOUNT_"+scenario)
        if y_violations[scenario]:raise AssertionError("ION_FRACTIONS_INVALID_"+scenario)
        actual[scenario]=sumph
        # G3 has no original photons; exactly 3 populated group contributions.
        rec=data["scenario_tick160_161"][scenario]
        if len(rec["first_tick_gross_group_photons"])!=3:raise AssertionError("G3_SHOULD_BE_ZERO")
        if abs(sum(rec["first_tick_gross_group_photons"])-supplied)>1e-11*supplied:raise AssertionError("GROUP_SUM")
        if rec["max_photon_conservation_residual_rel"]>5e-11:raise AssertionError("PHOTON_NUMBER")
        if rec["max_full_population_ledger"]>1e-11:raise AssertionError("5FLUX")
    # No false inference of unknown historical D: only documented initial family
    if data["physical_scope"]["true_historical_D_initial"]!="UNKNOWN_NOT_IN_REI_ORIGINAL_26EVENT":
        raise AssertionError("PRETENDED_D_HISTORICAL_INITIAL")
    if data["gates"]["official_tick161"]!="HOLD" or data["DAG"]["new_canonical_nodes"]!=0:
        raise AssertionError("PREMATURE_OWNER_ACCEPTANCE")

    # Alternative independent single-cell DOP853 with fixed original photons
    # estimates sensitivity to source interpolation/feedback without claiming a
    # source-owner continuous solution.
    points=node_donors(list(selected))
    forcing=PARENT/"source_inputs/canonical_time_resolved_forcing_nodes.csv"
    with forcing.open() as f:
        forcing_rows=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
    tt=np.array([float(r["time_s"]) for r in forcing_rows])
    gamma=PchipInterpolator(tt,[float(r["Gamma_HI_s-1"]) for r in forcing_rows],extrapolate=False)
    dt=float(data["physical_scope"]["proper_tick_duration_seconds"])
    differences={"ALL_NEUTRAL":[],"H_MATCHED":[]}
    for i,p in points.items():
        data_row=selected[i]
        times=(0,64,128,160)
        def donor(t):
            q=t/dt
            j=max(0,min(bisect_right(times,q)-1,2))
            f=max(0.,min(1.,(q-times[j])/(times[j+1]-times[j])))
            a=p[times[j]];b=p[times[j+1]]
            return (a["T"]*math.exp(math.log(b["T"]/a["T"])*f),
                    a["x"]*(1-f)+b["x"]*f,
                    a["ne"]*(1-f)+b["ne"]*f,a["nH"])
        def rhs(t,z):
            y,C=z
            T,x,ne,nH=donor(t)
            kf,kr=k_rates(T,table)
            ef=ne+ETA*nH*(y-C);xf=x-ETA*C
            cx=nH*(kf*xf*(1-y)-kr*(1-xf)*y)
            a=2.753e-14*(315614/T)**1.5/(1+((315614/T)/2.740)**.407)**2.242
            beta=5.835e-11*math.sqrt(T)*math.exp(-157804./T)
            dy=cx+float(gamma(t))*(1-y)+beta*ef*(1-y)-a*ef*y
            return [dy,cx]
        for scenario in differences:
            y0=0. if scenario=="ALL_NEUTRAL" else p[0]["x"]
            sol=solve_ivp(rhs,(0.,160*dt),[y0,0.],method="DOP853",rtol=2e-10,atol=2e-12)
            if not sol.success:raise AssertionError("INDEPENDENT_ODE_SOLVER_FAIL")
            differences[scenario].append(abs(float(sol.y[0,-1])-float(data_row[f"{scenario}_DII_y_tick160"])))
    checks={k:{"max_abs":max(v),"median_abs":float(np.median(v)),"source_cells":len(v)} for k,v in differences.items()}
    # Approximate fixed-photon diagnostic only, empirically report deviations,
    # do not treat this as an exact independent solve of coupled group photons.
    aud={"schema":"WU_R56_ADVERSARIAL_SOURCE_RECOUNT_AND_DISJOINT_IVP_V1",
      "native_source_original_46080_cells_read":n,
      "original_12_input_source_sha":data["source_sha256"]["R54_source_files"],
      "independent_savin_cx_at_tick0_max_abs":max_CX_stationary,
      "independent_first_tick_photon_recount_max_rel":residual_max,
      "independent_first_tick_photon_count":actual,
      "DII_positivity_violations":y_violations,
      "native_original_state_hashes_match":True,
      "separate_DOP853_fixed_original_photons_not_coupled":checks,
      "same_author_not_distinct_referee":True,
      "original_full_26_event_D_not_run":True,
      "original_tick161":"HOLD",
      "science_verdict":"SOURCE_CONDITIONAL_RECOUNT_PASS_NATIVE_SOURCE_OWNER_NOT_ADMITTED"}
    path=out/"R56_ADVERSARIAL_AUDIT.json"
    path.write_text(json.dumps(aud,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in aud.items() if k not in ("original_12_input_source_sha",)},sort_keys=True))
    return aud

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=HERE/"results")
    args=ap.parse_args();audit(args.out)
