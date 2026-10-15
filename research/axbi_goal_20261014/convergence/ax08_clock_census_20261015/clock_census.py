#!/usr/bin/env python3
"""AX08 completed ZERO / HALF_PLUS: conserved H/He census and exact clock split.

Read-only original science files (hash-pinned). Whole 312238 physical endpoints
per case; all 6 abundance species per endpoint validated. No solver started.
Numerical interpolation is a CONDITIONAL diagnostic, not AX11 error admission.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import NamedTuple
import numpy as np

HERE=Path(__file__).resolve().parent
UPSTREAM=HERE.parent/"ax08_half_plus_20261015"
COLS=("time_s","a","zbar","x_HI","x_HII","x_HeI","x_HeII","x_HeIII",
      "nH_proper_cm3","ne_proper_cm3","temperature_K","J2_photon_u_eV_per_H")
SPECIES=("H_I","H_II","He_I","He_II","He_III","electron")
CASES=("ZERO","SHEAR_HALF_PLUS")
N=312238
M=1001

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()

def bindings(owner:Path):
    m=json.loads((UPSTREAM/"paired_manifest.json").read_text())
    if m["comparison_kind"]!="PAIRED" or m["source_relation"]["status"]!="ACCEPTED_SCOPED":
        raise ValueError("UNREVIEWED_OR_UNMATCHED_ORIGINAL_SOURCE")
    out={}
    for key,field in zip(CASES,("reference","candidate")):
        spec=m[field]
        if spec["id"]!=key:raise ValueError("INCORRECT_SOURCE_CASE_ID")
        bound={}
        for typ in ("history","abundances","source_identity","terminal"):
            p=owner/spec[typ]["path"]
            if not p.is_file() or digest(p)!=spec[typ]["sha256"]:
                raise ValueError(f"SOURCE_BYTE_IDENTITY:{key}:{typ}")
            bound[typ]={"path":p,"sha256":spec[typ]["sha256"]}
        if "COMPLETE_REPRESENTED_INTERVAL" not in bound["terminal"]["path"].read_text():
            raise ValueError("INCOMPLETE_SCIENCE_SCENARIO")
        out[key]=bound
    return out

def history(path:Path,mode="numpy"):
    with path.open(newline="") as f:
        header=next(csv.reader(f))
    if len(header)!=25 or any(s not in header for s in COLS):
        raise ValueError("AX08_HISTORY_HEADER_CHANGED")
    ix=[header.index(s) for s in COLS]
    t0=time.perf_counter()
    if mode=="numpy":
        arr=np.loadtxt(path,delimiter=",",skiprows=1,usecols=ix,dtype=np.float64)
    elif mode=="csv":
        rows=[]
        with path.open(newline="") as f:
            reader=csv.reader(f);next(reader)
            for r in reader:rows.append([float(r[j]) for j in ix])
        arr=np.asarray(rows,dtype=np.float64)
    else:raise ValueError("UNKNOWN_LOADING_BACKEND")
    duration=time.perf_counter()-t0
    if arr.shape!=(N,len(COLS)) or not np.all(np.isfinite(arr)):
        raise ValueError("BAD_FINITE_WHOLE_SOURCE")
    if np.any(np.diff(arr[:,0])<=0) or np.any(np.diff(arr[:,1])<=0):
        raise ValueError("NON_MONOTONE_PROPER_TIME_OR_SCALE")
    if arr[0,0]!=0 or abs(arr[-1,1]-.2)>1e-15:
        raise ValueError("INITIAL_OR_FINAL_SOURCE_CLOCK")
    if np.any(arr[:,3:8]<-1e-12) or np.any(arr[:,3:8]>1+1e-12):
        raise ValueError("NEGATIVE_ION_OR_GREATER_THAN_ONE")
    return arr,duration

def census(path:Path,H:np.ndarray,case:str):
    """Stream all 6*N provenance rows without materializing the 350MiB CSV."""
    with path.open(newline="") as f:header=next(csv.reader(f))
    fields=("run_id","time_s","species_id","nproper","element_fraction",
            "Ybaryon","electron_xe","charge","A","Tgas_K")
    if not all(q in header for q in fields):raise ValueError("ABUNDANCES_SCHEMA_CHANGED")
    ix={s:header.index(s) for s in fields}
    t0=time.perf_counter()
    nr=0
    maxerr={k:0. for k in ("species_number","history_fraction","electron_charge",
                          "electron_xe","electron_history","electron_history_row","H_number","He_number","Ybaryon_sum",
                          "gas_temperature")}
    # Group by each 6-row full, specified species sequence; no interspecies mixing.
    totals=[]
    rows_per_case=0
    from itertools import islice
    with path.open(newline="") as f:
        rd=csv.reader(f);next(rd)
        for i in range(N):
            chunk=list(islice(rd,6))
            if len(chunk)!=6:raise ValueError(f"TRUNCATED_6_SPECIES_GROUP_AT_{i}")
            for k,row in enumerate(chunk):
                if row[ix["run_id"]]!=case or row[ix["species_id"]]!=SPECIES[k]:
                    raise ValueError(f"SPECIES_ORDER_OR_CASE_CHANGED_{i}_{k}")
                if float(row[ix["time_s"]])!=H[i,0]:
                    raise ValueError(f"ABUNDANCE_HISTORY_CLOCK_DISAGREES_{i}")
                if int(row[ix["A"]])!=(1 if k<2 else 4 if k<5 else 0):
                    raise ValueError(f"NUCLEUS_BARYON_NUMBER_BINDING_CHANGED_{i}_{k}")
            value=np.array([float(v[ix["nproper"]]) for v in chunk])
            fractions=np.array([float(v[ix["element_fraction"]]) if v[ix["element_fraction"]] else np.nan for v in chunk])
            yb=np.array([float(v[ix["Ybaryon"]]) for v in chunk])
            if not np.all(np.isfinite(value)) or np.any(value<0):
                raise ValueError("NONFINITE_NEGATIVE_NUCLEUS_OR_ELECTRON")
            nH=value[0]+value[1]
            nHe=sum(value[2:5])
            ne=value[1]+value[3]+2*value[4]
            if nH<=0 or nHe<=0:raise ValueError("ZERO_H_OR_HE_NUCLEI")
            # Scale normalized residuals by the local H number density.
            candidates=dict(
              species_number=abs(value[0]/nH-fractions[0])+abs(value[1]/nH-fractions[1])
                     +sum(abs(value[2+k]/nHe-fractions[2+k]) for k in range(3)),
              history_fraction=max(abs(fractions[0]-H[i,3]),abs(fractions[1]-H[i,4]),
                   abs(fractions[2]-H[i,5]),abs(fractions[3]-H[i,6]),
                   abs(fractions[4]-H[i,7])),
              electron_charge=abs(ne-value[5])/H[i,8],
              electron_xe=abs(value[5]/H[i,8]-float(chunk[5][ix["electron_xe"]])),
              electron_history=abs(ne-H[i,9])/H[i,8],
              electron_history_row=abs(value[5]-H[i,9])/H[i,8],
              H_number=abs(nH-H[i,8])/H[i,8],
              He_number=abs(nHe/H[i,8]-(totals[0][0] if totals else nHe/H[i,8])),
              Ybaryon_sum=abs(yb[0]+yb[1]+4*sum(yb[2:5])-1),
              gas_temperature=max(abs(float(row[ix["Tgas_K"]])-H[i,10]) for row in chunk))
            if not np.all(np.isfinite(list(candidates.values()))):
                raise ValueError("NONFINITE_CHARGE_FRACTION_RESIDUAL")
            for k,v in candidates.items():maxerr[k]=max(maxerr[k],float(v))
            if i==0 or i==N-1:
                totals.append((nHe/nH,float(value[5]/nH),float(yb[0]+yb[1]+4*yb[2:5].sum())))
            rows_per_case+=len(chunk)
        if next(rd,None) is not None:raise ValueError("EXTRA_ABUNDANCE_ROWS")
    if rows_per_case!=6*N:raise ValueError("INCOMPLETE_ION_CENSUS")
    # Numerical readback tolerance, not source-solver error certification.
    if max(maxerr.values())>5e-9:
        raise ValueError(f"ABUNDANCE_OR_CHARGE_LEDGER_MISMATCH:{maxerr}")
    return dict(rows=rows_per_case,clock_rows=N,neutrals_ions=SPECIES,
        max_abs_residuals=maxerr,initial_nHe_per_nH=totals[0][0],
        final_nHe_per_nH=totals[-1][0],
        final_xe_per_H=totals[-1][1],
        duration_s=time.perf_counter()-t0,
        full_all_rows_checked=True)

def single(case:str,pathmap:dict,mode="numpy",with_census=True):
    H,load_s=history(Path(pathmap["history"]["path"]),mode)
    result=dict(case=case,samples=len(H),read_history_s=load_s,
                hII_initial=H[0,4],hII_final=H[-1,4],
                temp_initial=H[0,10],temp_final=H[-1,10],
                duration_proper_s=H[-1,0])
    if with_census:
        result["census"]=census(Path(pathmap["abundances"]["path"]),H,case)
    return H,result

def compare(Z,S,nodes=4097):
    i_t,i_a,i_z=0,1,2
    # Match in ln(a), NEVER equate the proper time coordinates a priori.
    amin=max(Z[0,i_a],S[0,i_a]);amax=min(Z[-1,i_a],S[-1,i_a])
    if not (amin<amax):raise ValueError("NO_COMMON_SCALE_INTERVAL")
    a=np.exp(np.linspace(math.log(amin),math.log(amax),nodes))
    a[0]=amin;a[-1]=amax
    t0=np.interp(a,Z[:,i_a],Z[:,i_t])
    ts=np.interp(a,S[:,i_a],S[:,i_t])
    names=["x_HII","x_HeII","x_HeIII","temperature_K",
           "ne_proper_cm3","J2_photon_u_eV_per_H"]
    cols=[4,6,7,10,9,11]
    good=(ts>=Z[0,0])&(ts<=Z[-1,0])
    # No extrapolation on different terminal proper clocks.
    if good.sum()<nodes//2:raise ValueError("INSUFFICIENT_MATCHED_PROPER_TIME")
    output={}
    plot={}
    for name,j in zip(names,cols):
        zero_a=np.interp(a,Z[:,i_a],Z[:,j])
        shear_a=np.interp(a,S[:,i_a],S[:,j])
        zero_t=np.interp(ts[good],Z[:,i_t],Z[:,j])
        fixed_a=(shear_a-zero_a)[good]
        clock=(zero_a[good]-zero_t)
        fixed_t=(shear_a[good]-zero_t)
        # Exact numerical algebra identity at the chosen common sampling.
        defect=float(np.max(np.abs(fixed_t-fixed_a-clock)))
        maxamp=max(float(np.max(np.abs(fixed_t))),1e-300)
        output[name]=dict(max_abs_delta_fixed_scale=float(np.max(np.abs(fixed_a))),
            max_abs_delta_fixed_proper_time=float(np.max(np.abs(fixed_t))),
            max_abs_clock_contribution=float(np.max(np.abs(clock))),
            exact_discrete_decomposition_error=defect,
            normalized_identity_residual=defect/maxamp,
            end_delta_fixed_scale=float(fixed_a[-1]),
            end_delta_fixed_time=float(fixed_t[-1]),
            end_clock_contribution=float(clock[-1]),
            numerical_source_error="UNKNOWN_NOT_AX11_CERTIFIED")
        if defect>max(5e-12*maxamp,5e-14):
            raise ValueError("CLOCK_DECOMPOSITION_FAILED:"+name)
        plot[name]=(fixed_t,fixed_a,clock)
    stats=dict(schema="rei.axbi.clock_census.v1",
       scope="SHEAR_HALF_PLUS and ZERO completed actual 312238-row histories",
       comparison="full completed histories, 4097 common log(a) samples",
       nodes=nodes,matched_time_nodes=int(good.sum()),excluded_due_to_terminal_clock=int((~good).sum()),
       max_proper_time_offset_s=float(np.max(np.abs(t0[good]-ts[good]))),
       candidate_terminal_proper_s=float(S[-1,i_t]),
       reference_terminal_proper_s=float(Z[-1,i_t]),
       observables=output,scientific_admission="EXPLORATORY_CLOCK_DECOMPOSITION_NOT_AX11_ERROR_CERTIFICATE")
    return stats,a[good],plot,good,Z,S

def save(stats,a,plot,Z,S,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False)
    fig,axes=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
    for ax,(name,(time,scale,clock)) in zip(axes.flat,plot.items()):
        ax.plot(1/a-1,time,label="fixed proper time",lw=1.4)
        ax.plot(1/a-1,scale,label="fixed mean scale",lw=1.2,ls="--")
        ax.plot(1/a-1,clock,label="background clock drift",lw=1.1,ls=":")
        ax.invert_xaxis();ax.set_title(name);ax.set_xlabel("Mean redshift");ax.legend(fontsize=7)
        ax.grid(alpha=.25)
    fig.suptitle("AX08 ZERO vs +0.005, exact discrete matched-clock decomposition; errors unknown")
    fig.savefig(out/"ax08_matched_clock_decomposition.png",dpi=160);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for row,(label,hist) in enumerate((("ZERO",Z),("SHEAR_HALF_PLUS",S))):
        times=hist[:,0]/(365.25*86400*1e6)
        # Preserve chronological ordering also on nonmonotone temperature axis.
        step=max(1,len(hist)//4500)
        idx=np.r_[np.arange(0,len(hist),step),len(hist)-1]
        for j,names in enumerate(((3,4),(5,6,7))):
            for k in names:
                axes[row,0].plot(times[idx],hist[idx,k],lw=1.15,
                    label=COLS[k])
                axes[row,1].plot(hist[idx,10],hist[idx,k],lw=1.15,label=COLS[k])
            break  # Time/temperature panels show all ionic fractions with legend.
        for k in (5,6,7):
            axes[row,0].plot(times[idx],hist[idx,k],lw=1.0,label=COLS[k])
            axes[row,1].plot(hist[idx,10],hist[idx,k],lw=1.0,label=COLS[k])
        axes[row,0].set_ylabel(label+" elemental fraction")
        axes[row,0].set_xlabel("Elapsed proper time [Myr]")
        axes[row,1].set_xlabel("Gas temperature [K]; joined in time order")
        axes[row,0].legend(fontsize=7,ncol=2)
        axes[row,1].legend(fontsize=7,ncol=2)
        for ax in axes[row]:ax.grid(alpha=.25)
    fig.suptitle("Original completed AXBI ionization histories (model-scoped; no AX11 errors)")
    fig.savefig(out/"ax08_abundances_two_completed_cases.png",dpi=160);plt.close(fig)
    (out/"CLOCK_CENSUS_RESULT.json").write_text(json.dumps(stats,indent=2)+"\n")

def main(owner,out,workers):
    orig=bindings(owner)
    start=time.perf_counter()
    if workers==2:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=2) as pool:
            fut={name:pool.submit(single,name,orig[name],"numpy",True) for name in CASES}
            cases={name:f.result() for name,f in fut.items()}
    elif workers==1:
        cases={name:single(name,orig[name],"numpy",True) for name in CASES}
    else:raise ValueError("WORKERS_MUST_BE_ONE_OR_TWO")
    stats,a,plot,mask,Z,S=compare(cases["ZERO"][0],cases["SHEAR_HALF_PLUS"][0])
    stats["timing_s"]=time.perf_counter()-start
    stats["workload"]={case:cases[case][1] for case in CASES}
    stats["source_sha256"]={case:{k:d["sha256"] for k,d in orig[case].items()} for case in CASES}
    stats["workers"]=workers
    stats["streaming_abundance_rows_total"]=12*N
    save(stats,a,plot,Z,S,out)
    print(json.dumps({k:stats[k] for k in
       ("scope","nodes","matched_time_nodes","max_proper_time_offset_s",
        "timing_s","workload","workers")},indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--workers",type=int,choices=(1,2),default=2)
    ar=ap.parse_args()
    main(ar.owner_root,ar.output,ar.workers)
