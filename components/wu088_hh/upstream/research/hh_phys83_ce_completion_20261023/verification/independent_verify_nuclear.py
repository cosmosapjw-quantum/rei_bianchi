#!/usr/bin/env python3
"""Bounded independent scalar verification of the detached nuclear ledger.

Only supplied synthetic normal-frame event energies/relative weights are used.
No parent PHYS81 event, nuclear cross section/rate, stopping law, or ODE is run.
The scalar reference uses Decimal at precision80, independently of production.
"""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

from independent_verify import Recorder, safe, sha, utc

UNIT=Path(__file__).resolve().parents[1]
SOURCE=UNIT/"source"
FIELDS=("Kin_MeV","Kc_MeV","Egamma_MeV","Q_MeV")
ENERGY_FIELDS=("delta_rest_MeV","delta_thermal_MeV","delta_fast_MeV","delta_photon_MeV")


def D(value):
    return Decimal.from_float(float(value))


def exact_input_sum(values):
    with localcontext() as context:
        context.prec=80
        return float(sum(map(D,values),Decimal(0)))


def build_cases(rec,nuc):
    cases=[]
    frame="normal_orthonormal:independent_synthetic_cell"

    def add(name,callback):
        cases.append((name,"nuclear",callback))

    def event_and_residual():
        for sign in (-1,0,1):
            event=nuc.EventEnergy(.25,.125,2.125+sign*1e-12,2.0,frame)
            expected=exact_input_sum((event.Egamma_MeV,event.Kc_MeV,-event.Kin_MeV,-event.Q_MeV))
            rec.absolute("event_signed_residual",event.energy_residual_MeV,expected,2e-15)
            if sign:
                rec.check("small_residual_not_replaced_by_zero",sign*event.energy_residual_MeV>0)
            for mode in ("FAST_FIRST","PROMPT_THERMAL"):
                ledger=nuc.capture_ledger(event,mode)
                rec.absolute("capture_preserves_signed_residual",ledger.energy_residual_MeV,expected,2e-15)
                rec.check("frame_preserved",ledger.frame==frame)
                rec.check("photon_is_supplied",ledger.delta_photon_MeV==event.Egamma_MeV)
                rec.check("rest_is_negative_Q",ledger.delta_rest_MeV==-event.Q_MeV)
                rec.check("literal_particle_counts",type(ledger.delta_N_thermal) is int and type(ledger.delta_N_fast) is int)
                if mode=="FAST_FIRST":
                    rec.check("fast_capture_particle_ownership",(ledger.delta_N_thermal,ledger.delta_N_fast)==(-2,1))
                    rec.check("fast_capture_energy_ownership",ledger.delta_thermal_MeV==-event.Kin_MeV
                              and ledger.delta_fast_MeV==event.Kc_MeV)
                else:
                    rec.check("prompt_capture_particle_ownership",(ledger.delta_N_thermal,ledger.delta_N_fast)==(-1,0))
                    rec.absolute("prompt_capture_energy_ownership",ledger.delta_thermal_MeV,event.Kc_MeV-event.Kin_MeV,0)
        rec.counters["valid_supplied_synthetic_event_records"]+=3
    add("nuclear_supplied_events_signed_residual",event_and_residual)

    def weighted_means():
        records=(nuc.EventEnergy(.25,.125,2.125,2.0,frame),nuc.EventEnergy(.75,.25,2.5,2.0,frame))
        averages=[]
        for weights in ((2.0,5.0),(1e308,1e308),(0.0,5.0),(5e-324,5e-324)):
            average=nuc.weighted_event_mean(records,weights)
            averages.append(average)
            with localcontext() as context:
                context.prec=80
                norm=sum(map(D,weights),Decimal(0))
                for field in FIELDS:
                    expected=sum((D(weight)*D(getattr(event,field)) for weight,event in zip(weights,records)),Decimal(0))/norm
                    rec.relative("same_measure_energy_average",getattr(average,field),float(expected),2e-14)
            rec.absolute("weighted_energy_residual",average.energy_residual_MeV,0.0,2e-14)
            rec.check("weighted_frame_preserved",average.frame==frame)
        mean=averages[0]
        rec.check("unweighted_mean_mutant_discriminated",abs(mean.Kin_MeV-.5)>.1)
        rec.check("zero_weight_mean_none",nuc.weighted_event_mean(records,(0.0,0.0)) is None)
        rec.check("empty_mean_none",nuc.weighted_event_mean((),()) is None)
        tiny=5e-324
        subnormal=nuc.EventEnergy(0.0,0.0,tiny,tiny,frame)
        average=nuc.weighted_event_mean((subnormal,subnormal),(1.0,1.0))
        rec.check("subnormal_positive_constant_preserved",average.Egamma_MeV==tiny and average.Q_MeV==tiny)
        rec.counters["relative_weighted_event_means"]+=4
        rec.counters["subnormal_mean_cases"]+=1
        rec.counters["valid_supplied_synthetic_event_records"]+=3
    add("nuclear_weighted_mean_and_zero_measure",weighted_means)

    def transfer_composition():
        event=nuc.EventEnergy(.25,.125,2.125,2.0,frame)
        first=nuc.capture_ledger(event,"FAST_FIRST")
        prompt=nuc.capture_ledger(event,"PROMPT_THERMAL")
        for remaining in (0.0,.03125,.125):
            stop=nuc.stopping_transfer(event.Kc_MeV-remaining,frame=frame)
            match=nuc.assimilation_transfer(remaining,frame=frame)
            rec.check("stopping_does_not_assimilate",(stop.delta_N_thermal,stop.delta_N_fast)==(0,0))
            rec.check("assimilation_transfers_one_particle",(match.delta_N_thermal,match.delta_N_fast)==(1,-1))
            for field in ENERGY_FIELDS:
                total=exact_input_sum(getattr(ledger,field) for ledger in (first,stop,match))
                rec.absolute("exclusive_transfer_energy_composition",total,getattr(prompt,field),0.0)
            rec.check("exclusive_transfer_particle_composition",
                      (first.delta_N_thermal+stop.delta_N_thermal+match.delta_N_thermal,
                       first.delta_N_fast+stop.delta_N_fast+match.delta_N_fast)==(-1,0))
            rec.absolute("stopping_energy_residual",stop.energy_residual_MeV,0.0,0.0)
            rec.absolute("assimilation_energy_residual",match.energy_residual_MeV,0.0,0.0)
            rec.check("photon_not_deposited_by_stopping_or_matching",stop.delta_photon_MeV==match.delta_photon_MeV==0)
        rec.counters["exclusive_transfer_compositions"]+=3
        rec.counters["valid_supplied_synthetic_event_records"]+=1
    add("nuclear_stopping_assimilation_exclusive_composition",transfer_composition)

    def eos_and_selected_mean():
        # The reference obtains dT from du=(3/2)kB(n dT + T dn) and
        # du/dt = Q -(u+p)Theta, dn/dt = S - n Theta, independently.
        for temperature,density,power,number,theta in (
            (300.0,2.0,0.0,0.0,0.0),(1e6,1e3,2e-8,-.75,2e-8),
            (1e4,1e-6,-1e-15,1e-9,-2e-10),(1e8,1e10,0.0,-1e6,0.0)):
            actual=nuc.thermal_temperature_source(temperature,density,power,number,theta)
            with localcontext() as context:
                context.prec=80
                T,n,Q,S,H=map(D,(temperature,density,power,number,theta))
                kb=Decimal("1.380649e-16")
                q_erg=Q*Decimal("1.602176634e-6")
                u=Decimal("1.5")*n*kb*T
                pressure=n*kb*T
                du=q_erg-(u+pressure)*H
                dn=S-n*H
                expected=(du-Decimal("1.5")*kb*T*dn)/(Decimal("1.5")*n*kb)
            rec.relative("thermal_EOS_independent_energy_differential",actual,float(expected),1e-13)
        for temperature,alpha in ((300.0,0.0),(1e6,.5),(1e8,2.0),(1e9,-1.5+2**-40)):
            value=nuc.nr_selected_kinetic_mean(temperature,alpha,temperature_independent_sigma=True)
            with localcontext() as context:
                context.prec=80
                kT=Decimal("1.380649e-16")/Decimal("1.602176634e-6")*D(temperature)
                # COM Maxwell energy plus derivative-selected relative energy.
                expected=Decimal("1.5")*kT+(D(alpha)+Decimal("1.5"))*kT
            rec.relative("selected_pair_COM_plus_relative_energy",value,float(expected),1e-13)
        # Removing a thermal particle changes T even with Q=Theta=0.
        actual=nuc.thermal_temperature_source(100.0,10.0,0.0,-2.0,0.0)
        rec.absolute("number_source_not_missing_from_EOS",actual,20.0,0.0)
        rec.counters["synthetic_EOS_cases"]+=5
        rec.counters["conditional_NR_mean_cases"]+=4
    add("nuclear_thermal_EOS_and_selected_pair_mean",eos_and_selected_mean)

    def guards():
        event=nuc.EventEnergy(.25,.125,2.125,2.0,frame)
        for values in ((-.25,.125,2.125,2.0),(.25,-.125,2.125,2.0),(.25,.125,0.0,2.0),
                       (.25,.125,2.125,0.0),(.25,.125,2.126,2.0),
                       (float("nan"),.125,2.125,2.0),(True,.125,2.125,2.0),
                       ([.25],.125,2.125,2.0),(.25,.125,float("inf"),2.0)):
            rec.reject("event_domain_and_closure_guard",lambda values=values:nuc.EventEnergy(*values,frame))
        for bad_frame in (None,1,"lab","center_of_mass","normal_orthonormal:","normal_orthonormal: "):
            rec.reject("explicit_normal_frame_guard",lambda bad_frame=bad_frame:nuc.EventEnergy(.25,.125,2.125,2,bad_frame))
        other=nuc.EventEnergy(.25,.125,2.125,2,"normal_orthonormal:other_cell")
        for weights in ((1,-1),(1,float("nan")),(1,float("inf")),(1,True),(1,"1")):
            rec.reject("weight_domain_guard",lambda weights=weights:nuc.weighted_event_mean((event,event),weights))
        rec.reject("zero_weight_other_frame_rejected",lambda:nuc.weighted_event_mean((event,other),(1,0)))
        rec.reject("weight_length_guard",lambda:nuc.weighted_event_mean((event,),(1,1)))
        rec.reject("zero_weight_invalid_record_rejected",lambda:nuc.weighted_event_mean((event,object()),(1,0)))
        for value in (None,object()):
            rec.reject("nonzero_rate_mean_required",lambda value=value:nuc.capture_ledger(value))
        rec.reject("exclusive_capture_mode_guard",lambda:nuc.capture_ledger(event,"BOTH"))
        for transfer in (nuc.stopping_transfer,nuc.assimilation_transfer):
            for value in (-1,True,float("nan"),float("inf"),[1]):
                rec.reject("transfer_domain_guard",lambda transfer=transfer,value=value:transfer(value,frame=frame))
        for args in ((0,1,0,0),(-1,1,0,0),(1,0,0,0),(1,-1,0,0),
                     (1,1,float("inf"),0),(1,1,0,float("nan")),(True,1,0,0)):
            rec.reject("EOS_domain_guard",lambda args=args:nuc.thermal_temperature_source(*args))
        for flag in (False,None,1,"true"):
            rec.reject("sigma_derivative_attestation_guard",lambda flag=flag:nuc.nr_selected_kinetic_mean(
                1e6,.5,temperature_independent_sigma=flag))
        for alpha in (-1.5,-2,float("nan"),float("inf"),True):
            rec.reject("selected_relative_energy_domain_guard",lambda alpha=alpha:nuc.nr_selected_kinetic_mean(
                1e6,alpha,temperature_independent_sigma=True))
        for temperature in (0.0,float("nan")):
            rec.reject("selected_pair_temperature_guard",lambda temperature=temperature:nuc.nr_selected_kinetic_mean(
                temperature,.5,temperature_independent_sigma=True))
        rec.reject("event_immutability",lambda:setattr(event,"Q_MeV",7),(FrozenInstanceError,AttributeError))
        ledger=nuc.capture_ledger(event)
        rec.reject("ledger_immutability",lambda:setattr(ledger,"delta_N_fast",7),(FrozenInstanceError,AttributeError))
        rec.reject("literal_integer_ledger_counts",lambda:nuc.Ledger("STOPPING",True,0,0,0,0,0,frame))
        rec.counters["nuclear_rates_or_stopping_law_callbacks"]=0
        rec.counters["parent_PHYS81_event_callbacks"]=0
        rec.counters["valid_supplied_synthetic_event_records"]+=2
    add("nuclear_scalar_frame_weight_EOS_guards",guards)
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--case",action="append",default=[])
    parser.add_argument("--lease-receipt",type=Path)
    args=parser.parse_args()
    output=args.output.resolve()
    if UNIT/"verification" not in output.parents:
        raise ValueError("Verification outputs must remain under this unit/verification")
    output.mkdir(parents=True,exist_ok=False)
    variables=("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS")
    thread_env={key:os.environ.get(key) for key in variables}
    if any(value!="1" for value in thread_env.values()):
        raise RuntimeError("Explicit single-thread environment required")
    files=[SOURCE/"nuclear_ownership.py",Path(__file__),Path(__file__).with_name("independent_verify.py")]
    start={"schema":"PHYS83_DETACHED_NUCLEAR_INDEPENDENT_VERIFICATION_V1","utc":utc(),
           "input_sha256":{str(path.relative_to(UNIT)):sha(path) for path in files},
           "python":platform.python_version(),"workers":1,"thread_environment":thread_env,
           "lease_receipt":str(args.lease_receipt) if args.lease_receipt else None,
           "lease_receipt_sha256":sha(args.lease_receipt) if args.lease_receipt and args.lease_receipt.exists() else None,
           "lease_receipt_status":"PRESENT_AT_START" if args.lease_receipt and args.lease_receipt.exists()
               else "WRAPPER_WRITES_AFTER_CHILD_EXIT" if args.lease_receipt else "LINKED_BY_CALLER",
           "new_physical_nuclear_events":0,"new_nuclear_rates":0,"new_stopping_laws":0,
           "new_ODE":0,"completed_scientific_identity_reruns":0}
    (output/"START.json").write_text(json.dumps(start,indent=2)+"\n",encoding="utf-8")
    sys.path.insert(0,str(SOURCE))
    import nuclear_ownership as nuc
    rec=Recorder(output)
    cases=build_cases(rec,nuc)
    known={name for name,_,_ in cases}
    if set(args.case)-known:
        raise ValueError("Unknown case IDs")
    selected=[row for row in cases if not args.case or row[0] in args.case]
    begin=time.monotonic()
    success=True
    for name,group,callback in selected:
        if not rec.run(name,group,callback):
            success=False
            break
    outcome={**start,"finished_utc":utc(),"status":"PASS_SCOPED" if success else "FAIL_PRESERVED",
             "checks":rec.checks,"cases":rec.results,"selected_cases":[row[0] for row in selected],
             "unfinished_cases":[row[0] for row in selected if row[0] not in {r["case"] for r in rec.results}],
             "maximum_errors":rec.metrics,"counters":dict(rec.counters),
             "elapsed_seconds":time.monotonic()-begin,
             "reference":"Decimal precision80; independent signed field sums, weighted averages, and EOS energy differential",
             "limits":["Synthetic supplied scalar energies only; not on-shell/frame construction",
                       "No empirical rates, physical finite-T quadrature, stopping activation, or nuclear ODE",
                       "Aggregate two-to-one particle pool counts; isotope stoichiometry remains provider-owned",
                       "Finite sampled verification; no continuum certificate; production NOT_ISSUED"]}
    (output/"RESULT.json").write_text(json.dumps(safe(outcome),indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    rec.stream.close()
    print(json.dumps({"status":outcome["status"],"checks":rec.checks,"cases":len(rec.results),
                      "output":str(output),"counters":dict(rec.counters)}),flush=True)
    return 0 if success else 1


if __name__=="__main__":
    raise SystemExit(main())
