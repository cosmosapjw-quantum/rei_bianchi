#!/usr/bin/env python3
"""Step-doubling controller for a positive, photon-conserving C10 sink pilot.

Finite sampled tolerances are algorithmic choices, not cosmological error bounds.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic as d

FIELDS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_per_H","photon_U_eV_per_H")
DEFAULT_TOL=np.array([3e-7,3e-7,3e-7,.02,3e-7,1e-5])


def propagate_adaptive(pack:d.Packets,initial:d.Gas,interval_s=1e12,
                       initial_step_s=1e11,tolerance=DEFAULT_TOL,
                       max_steps=3000):
    if interval_s<=0 or initial_step_s<=0 or np.any(np.asarray(tolerance)<=0):
        raise ValueError("positive time interval, step, tolerances required")
    tolerance=np.asarray(tolerance,dtype=float)
    start_n=pack.n+initial.ne
    start_E=pack.u+initial.thermal_eV_cm3+initial.binding_eV_cm3
    currentpack=pack.clone()
    gas=initial
    t=0.
    dt=min(float(initial_step_s),float(interval_s))
    accepted=0
    rejected=0
    max_energy_res=0.
    max_number_res=0.
    max_est_ratio=0.
    history=[d.observables(0.,gas,currentpack)]
    while t<interval_s:
        if accepted+rejected>=max_steps:
            raise d.StepFailure("bounded adaptive history exhausted")
        dt=min(dt,interval_s-t)
        if dt<1e-14*interval_s:
            raise d.StepFailure("adaptive timestep underflow")
        try:
            gwhole,pwhole,_=d.midpoint_step(gas,currentpack,dt)
            ghalf,phalf,_=d.midpoint_step(gas,currentpack,dt*.5)
            gtwo,ptwo,_=d.midpoint_step(ghalf,phalf,dt*.5)
            # Richardson difference: second-order method, local O(dt^3).
            whole=d.observables(t+dt,gwhole,pwhole)
            two=d.observables(t+dt,gtwo,ptwo)
            local=np.array([abs(two[k]-whole[k])/3. for k in FIELDS])
            ratio=float(np.max(local/tolerance))
        except d.StepFailure:
            ratio=float("inf")
        if ratio<=1.:
            gas,currentpack=gtwo,ptwo
            t=interval_s if math.isclose(t+dt,interval_s,rel_tol=1e-14) else t+dt
            accepted+=1
            max_est_ratio=max(max_est_ratio,ratio)
            row=d.observables(t,gas,currentpack)
            history.append(row)
            max_energy_res=max(max_energy_res,abs(currentpack.u+
                             gas.thermal_eV_cm3+gas.binding_eV_cm3-start_E))
            max_number_res=max(max_number_res,abs(currentpack.n+gas.ne-start_n))
        else:
            rejected+=1
        if not math.isfinite(ratio) or ratio==0.:
            factor=.25 if ratio>1 else 1.8
        else:
            factor=min(1.8,max(.25,.86*ratio**(-1./3.)))
        dt*=factor
    return {"accepted":accepted,"rejected":rejected,
            "max_local_estimator_over_tolerance":max_est_ratio,
            "max_photon_electron_relative_residual":max_number_res/max(start_n,1e-30),
            "max_total_energy_relative_residual":max_energy_res/max(start_E,1e-30),
            "final":history[-1],"history":history,"photon_bytes":pack.bytes}


def test_case(source:str,nmu=12,ne=16,photons_per_H=1.):
    m=d.c9.Scenario(d.ROOT)
    from benchmark import HardSource
    spectral=d.c9.Spectrum() if source=="bb50k" else HardSource()
    ages=np.geomspace(m.ar,.2,d.c9.AGE_COUNT)
    cohorts=d.c9.build_packets(m,spectral,ages,0.,n_mu=nmu,n_energy=ne)
    original=d.c9.source_age_weights(m,ages,0.)
    train,hold=d.c9.gas_states(m)
    tensor=d.c9.evaluate_packets(cohorts,np.vstack((train,hold)))
    fit=d.c9.design(tensor,original,5,len(train))
    gas=d.Gas.initial(m)
    compact=d.to_packets(cohorts,d.weights_from_design(fit,len(ages)),gas,photons_per_H)
    dense=d.to_packets(cohorts,original,gas,photons_per_H)
    result={}
    for label,pack in (("dense36",dense),("compressed",compact)):
        t0=perf_counter()
        adaptive=propagate_adaptive(pack,gas)
        adaptive_s=perf_counter()-t0
        t0=perf_counter()
        reference=d.propagate(pack,gas,nsteps=256,interval=1e12)
        ref_s=perf_counter()-t0
        delta={k:abs(adaptive["final"][k]-reference["final"][k]) for k in FIELDS}
        result[label]={"adaptive":adaptive,"reference_256":reference["final"],
                       "ref_delta":delta,"adaptive_time_s":adaptive_s,
                       "reference_time_s":ref_s}
    return {"source":source,"compression_age_count":fit["retained"],
            "cases":result}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spectrum",choices=("bb50k","hard"),default="bb50k")
    args=p.parse_args()
    r=test_case(args.spectrum)
    path=HERE/("ADAPTIVE_"+args.spectrum.upper()+".json")
    path.write_text(json.dumps(r,indent=2)+"\n")
    for kind,data in r["cases"].items():
        a=data["adaptive"]
        print(args.spectrum,kind,"accepted/rejected",a["accepted"],a["rejected"],
              "wall_speed",data["reference_time_s"]/data["adaptive_time_s"],
              "max_energy",a["max_total_energy_relative_residual"],
              "vs_fixed256",data["ref_delta"])


if __name__=="__main__":
    main()
