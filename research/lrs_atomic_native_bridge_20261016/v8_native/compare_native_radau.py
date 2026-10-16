#!/usr/bin/env python3
"""Compare frozen-owner Rust RR/DR-only output with independent V8 continuous RHS."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
V8 = HERE.parent / "v8"
sys.path.insert(0, str(V8))
import rrdr_sourcefree_v8 as ref

CASES = {
    "D1_X1e-5_T15000": (1e-5, 1., 15000.),
    "D100_X002_T15000": (.002, 100., 15000.),
    "D1000_X002_T15000": (.002, 1000., 15000.),
    "D10000_X0003_T15000": (.0003, 10000., 15000.),
    "D1000_X002_T22000": (.002, 1000., 22000.),
    "D1e6_X0001_T15000": (.0001, 1e6, 15000.),
}
NS = (8, 16, 32, 64, 128)
CHANNELS = ref.CHANNELS

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reference(span: float, density: float, t0: float, sensitive: bool):
    s0=ref.stock_vector((.075,.12,.03))
    e0=ref.nuclei_and_electrons(s0)[2]
    y0=np.zeros(17)
    y0[:3]=(.075,.12,.03)
    y0[3]=1.5*ref.KB*t0*(1+ref.Y_HE+e0)
    return solve_ivp(lambda x,y:ref.rhs_independent(x,y,density),(0.,span),y0,
                     method="Radau",rtol=2e-13 if sensitive else 2e-12,
                     atol=np.array([8e-16]*3+[1e-29]*14) if sensitive else np.array([8e-15]*3+[1e-28]*14),
                     max_step=span/(128 if sensitive else 64),dense_output=True)

def getrow(path:Path):
    with path.open(newline="") as f:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]

def observ(y):
    p,he2,he3,w=y[:4]
    s=ref.stock_vector((p,he2,he3))
    return {
        "temperature_K":ref.temperature_from_stocks(w,s),
        "electron_per_H":ref.nuclei_and_electrons(s)[2],
        "stocks_per_H":s.tolist(),
        "events_per_H":y[4:8].tolist(),
        "cooling_erg_per_H":y[8:12].tolist(),
        "binding_escape_erg_per_H":y[12:16].tolist(),
        "work_erg_per_H":float(y[16]),
    }

def native_observ(r):
    return {
        "temperature_K":r["Tend_K"],"electron_per_H":r["e_per_H"],
        "stocks_per_H":[r[k] for k in ("HI","HII","HeI","HeII","HeIII")],
        "events_per_H":[r[f"cum_events_{x}"] for x in CHANNELS],
        "cooling_erg_per_H":[r[f"cum_cooling_{x}"] for x in CHANNELS],
        "binding_escape_erg_per_H":[r[f"cum_binding_{x}"] for x in CHANNELS],
        "work_erg_per_H":r["cum_work"],
    }

def error(a,b):
    out={}
    for k in a:
        aa=np.asarray(a[k]);bb=np.asarray(b[k]);vv=np.abs(aa-bb)
        out[k]=vv.tolist() if vv.ndim else float(vv)
    return out

def slope(vals):
    return [math.log(vals[i]/vals[i+1],2) if vals[i]>0 and vals[i+1]>0 else None for i in range(len(vals)-1)]

def run(raw:Path):
    rows=[];summary={}; all_geom=0.; max_eledger=0.; max_energy_rel=0.; max_nuclear=0.
    for name,(span,density,t0) in CASES.items():
        base=reference(span,density,t0,False); tight=reference(span,density,t0,True)
        if not base.success or not tight.success: raise RuntimeError(f"Radau failure {name}: {base.message} {tight.message}")
        ob=observ(base.y[:,-1]); ot=observ(tight.y[:,-1]); sens=error(ob,ot)
        case=[]
        for n in NS:
            f=raw/f"{name}_N{n}.csv"; rr=getrow(f)
            if len(rr)!=n: raise RuntimeError(f"wrong row count {f}")
            final=rr[-1]; no=native_observ(final);err=error(no,ob)
            perstep=[]
            for i,r in enumerate(rr):
                xmid=(i+.5)*span/n
                a=ref.native.A0*math.exp(xmid)
                nh,nhe=ref.native.density(a)
                H=ref.native.hubble(a)
                for key,expect in (("a",a),("H_s",H),("nh_cm3",density*nh),("nhe_cm3",density*nhe),("dtmid_s",span/n/H)):
                    all_geom=max(all_geom,abs(r[key]-expect)/max(abs(expect),1e-300))
                max_eledger=max(max_eledger,abs(r["cum_events_RR_HII"]+r["cum_events_RR_HeII"]+r["cum_events_RR_HeIII"]+r["cum_events_DR_HeII"]-(.075+ref.Y_HE*(.12+2*.03)-r["e_per_H"])))
                max_nuclear=max(max_nuclear,abs(r["HI"]+r["HII"]-1.),abs(r["HeI"]+r["HeII"]+r["HeIII"]-ref.Y_HE))
                max_energy_rel=max(max_energy_rel,abs(r["energy_residual_erg_per_H"])/(1.5*ref.KB*t0*(1+ref.Y_HE+.075+ref.Y_HE*(.12+2*.03))+ref.binding_energy(ref.stock_vector((.075,.12,.03)))))
                if density==1e6:
                    re=observ(base.sol(r["X"]))
                    perstep.append({"step":i+1,"X":r["X"],"T_error_K":abs(r["Tend_K"]-re["temperature_K"]),"electron_error_per_H":abs(r["e_per_H"]-re["electron_per_H"]),"exposure_HeII_sum":r["exposure_HeII_sum"],"exposure_max":max(r[f"exposure_{x}"] for x in CHANNELS)})
            entry={"case":name,"steps":n,"x_end":span,"density_factor":density,"T0_K":t0,
                   "native_final":no,"radau_final":ob,"absolute_error":err,
                   "max_midpoint_residual_K":max(r["root_residual_K"] for r in rr),
                   "max_rr_exposure":max(max(r[f"exposure_{x}"] for x in CHANNELS) for r in rr),
                   "max_HeII_combined_exposure":max(r["exposure_HeII_sum"] for r in rr),
                   "max_energy_residual_erg_per_H":max(abs(r["energy_residual_erg_per_H"]) for r in rr),
                   "max_HeII_combined_exposure_by_phase":{
                       phase:max(r[f"exposure_{phase}_HeII_sum"] for r in rr)
                       for phase in ("begin","mid","end")},
                   "csv_sha256":sha(f)}
            if perstep: entry["stiff_step_errors"]=perstep
            case.append(entry); rows.append(entry)
        terr=[r["absolute_error"]["temperature_K"] for r in case]
        eerr=[r["absolute_error"]["electron_per_H"] for r in case]
        cs={}
        for j,c in enumerate(CHANNELS):
            vals=[r["absolute_error"]["cooling_erg_per_H"][j] for r in case]
            cs[c]={"errors_erg_per_H":vals,"orders":slope(vals)}
        summary[name]={"reference_sensitivity":sens,"temperature_errors_K":terr,"temperature_orders":slope(terr),
                       "electron_errors_per_H":eerr,"electron_orders":slope(eerr),
                       "cooling":cs,"radau_nfev":base.nfev,"radau_sensitive_nfev":tight.nfev}
    return {"native_runs":len(rows),"geometry_max_relative_error":all_geom,
            "electron_ledger_max_abs_per_H":max_eledger,"nuclear_ledger_max_abs_per_H":max_nuclear,
            "energy_ledger_max_relative":max_energy_rel,"case_summary":summary,"runs":rows,
            "reference_source_sha256":sha(V8/"rrdr_sourcefree_v8.py")}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("raw",type=Path);ap.add_argument("output",type=Path);args=ap.parse_args()
    ans=run(args.raw);args.output.write_text(json.dumps(ans,indent=2,sort_keys=True)+"\n")
    for k,v in ans["case_summary"].items(): print(k,"Terror",v["temperature_errors_K"],"Torder",v["temperature_orders"])
    print("runs",ans["native_runs"],"geom",ans["geometry_max_relative_error"],"e ledger",ans["electron_ledger_max_abs_per_H"],"energy",ans["energy_ledger_max_relative"])
