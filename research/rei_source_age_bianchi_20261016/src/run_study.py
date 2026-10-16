"""Bounded, deterministic positive source-age Bianchi reference study (no native execution)."""
import json
from pathlib import Path
from dataclasses import asdict,replace
from math import log2
import numpy as np
from age_transport import (Model,CHI,integrate_ray,reference_ray,integrate_source,
   integrate_spectral_source,source_free_sharp_pi_bounds, source_free_pressure,
   photon_events,age_event_boundaries,adaptive_birth_age_source,integrate_angular_event_source)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'

def slim(x):
    return x if isinstance(x,(int,float,str,bool)) else asdict(x)

def main():
    OUT.mkdir(exist_ok=True)
    m=Model()
    report={"schema":"rei.source_age.bianchi.reference.v1",
            "assumptions":{"geometry":"prescribed signed LRS Bianchi I, H/H_ref=1",
                          "species":"Verner 1996 HI HeI HeII; prescribed n_i proportional a^-3; no gas evolution",
                          "source":"positive manufactured emission per dln a and birth physical photon energy",
                          "units":"photons/H, eV/H, x=ln(a/a_ref)"},
            "reference_model":asdict(m),"sharp_pressure":[],"signed_convergence":[],
            "source_age_refinement":[],"spectral_refinement":[],"multicrossing":{},
            "adaptive_age":[],"angular_refinement":[],"independent_age_reference":{}}
    for v in [-.04,0.,.04]:
        case=replace(m,signed_v0=v)
        lo,hi=source_free_sharp_pi_bounds(case)
        report["sharp_pressure"].append({"v":v,"lower":lo,"upper":hi,
            "transverse":source_free_pressure(case,0.),"polar":source_free_pressure(case,1.)})
        ref=reference_ray(case,.07,.61,n_time=96)
        rows=[]
        for n in [8,16,32,64,128,256]:
            sol=integrate_ray(case,.07,.61,n_time=n)
            err=max(abs(sol.survivor-ref.survivor),
                    abs(sol.heat_ev-ref.heat_ev)/case.e_birth_ev,
                    abs(sol.work_ev-ref.work_ev)/case.e_birth_ev)
            rows.append({"n_time":n,"max_error_normalized":err,
                         "photon_residual":sol.photon_residual,"energy_residual_ev":sol.energy_residual})
        report["signed_convergence"].append({"v":v,"reference":slim(ref),
            "data":rows,"tail_orders":[log2(rows[i-1]["max_error_normalized"]/rows[i]["max_error_normalized"])
                                          for i in range(1,len(rows))]})
    # Compare bounded, source-age continuous irradiation with actual terminal threshold cuts.
    base=replace(m,signed_v0=.04)
    for n in [4,8,16,32,64]:
        for mode in [False,True]:
            z=integrate_source(base,n,8,n_time=64,age_split=mode)
            report["source_age_refinement"].append({"n_age_target":n,"age_split":mode,
                "effective_age_nodes":z.ray_calls//8,"HeII_absorbed":z.absorbed[2],
                "emitted":z.emitted_photons,"survivors":z.survivors,"work_ev":z.work_ev,
                "pi_ev":z.final_pi_ev,"photon_residual":z.photon_residual,
                "energy_residual_ev":z.energy_residual,"ray_calls":z.ray_calls,
                "event_count":z.event_count,"panels":z.age_panels})
    for n in [8,16,32]:
        r=integrate_spectral_source(base,n_energy=n,n_age=6,n_mu=8,n_time=32,
                                    split_birth_thresholds=True)
        report["spectral_refinement"].append({"requested_n_energy":n,
            "emitted_ev":r.emitted_ev,"photon_survivors":r.survivors,
            "species_absorbed":list(r.absorbed),"heat_ev":r.heat_ev,
            "physical_work_ev":r.work_ev,"photon_residual":r.photon_residual,
            "energy_residual_ev":r.energy_residual,"ray_calls":r.ray_calls})
    extreme=replace(m,signed_v0=0.,b_osc_amp=.22,b_osc_freq=18.)
    rr=integrate_ray(extreme,0.,1.,n_time=160,scan=768)
    ref=reference_ray(extreme,0.,1.,n_time=64,scan=768)
    report["multicrossing"]={"scope":"manufactured large shear, not near-FLRW physical prediction",
        "signed_s_over_H_max_abs":extreme.b_osc_amp*extreme.b_osc_freq,
        "event_roots_x":photon_events(extreme,0.,1.,scan=768)[1:-1],
        "integrated":slim(rr),"DOP853":slim(ref),
        "number_difference":rr.survivor-ref.survivor,
        "heat_difference_ev":rr.heat_ev-ref.heat_ev,
        "work_difference_ev":rr.work_ev-ref.work_ev}
    # Adaptive GL4/GL8 source-age quadrature: local embedded estimator is not
    # a rigorous bound. Quantify against an independent continuous DOP853 RHS.
    parent=replace(m,signed_v0=.04)
    reference=integrate_source(parent,64,8,48,age_split=True,independent=True)
    report["independent_age_reference"]={"solver":"DOP853, independent differential photon/heat/work RHS",
        "age_integration":"GL source-age panels split at terminal spectral threshold",
        "rays":reference.ray_calls,"HeII_absorbed":reference.absorbed[2],
        "heat_ev":reference.heat_ev,"pi_ev":reference.final_pi_ev,
        "photon_residual":reference.photon_residual,"energy_residual":reference.energy_residual}
    for n_time in [32,64,128]:
        ar=adaptive_birth_age_source(parent,8,n_time,rtol=1e-5,atol=1e-7)
        r=ar.result
        report["adaptive_age"].append({"n_time":n_time,"ray_calls":r.ray_calls,
            "accepted_panels":ar.accepted_panels,"HeII_absorbed":r.absorbed[2],
            "heat_ev":r.heat_ev,"pi_ev":r.final_pi_ev,
            "relative_HeII_difference_from_DOP853":abs(r.absorbed[2]-reference.absorbed[2])/reference.absorbed[2],
            "relative_heat_difference_from_DOP853":abs(r.heat_ev-reference.heat_ev)/reference.heat_ev,
            "photon_residual":r.photon_residual,"energy_residual":r.energy_residual,
            "embedded_max_absolute_estimator":ar.estimated_max_absolute_error,
            "estimator_is_rigorous":False})
    # Fixed-age angular refinement, no claim of full convergence from one axis.
    for v in [-.04,.04]:
        case=replace(m,signed_v0=v)
        baseline=integrate_angular_event_source(case,24,64,64)
        for nmu in [4,8,16,32]:
            for aligned in (False,True):
                r=integrate_angular_event_source(case,24,nmu,64) if aligned else \
                   integrate_source(case,24,nmu,64)
                report["angular_refinement"].append({"v":v,"n_mu_target":nmu,
                    "terminal_event_split":aligned,"ray_calls":r.ray_calls,
                    "HeII_absorbed":r.absorbed[2],"pi_ev":r.final_pi_ev,
                    "abs_HeII_error_against_mu64_split":abs(r.absorbed[2]-baseline.absorbed[2]),
                    "abs_Pi_error_against_mu64_split":abs(r.final_pi_ev-baseline.final_pi_ev),
                    "photon_residual":r.photon_residual,"energy_residual":r.energy_residual})
    (OUT/'SOURCE_AGE_NUMERICS.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('SIGNED TAIL ORDERS',[(x['v'],x['tail_orders'][-2:]) for x in report['signed_convergence']])
    print('SOURCE AGE',[(x['n_age_target'],x['age_split'],x['effective_age_nodes'],x['HeII_absorbed'])
                        for x in report['source_age_refinement']])
    print('SPECTRAL',[(x['requested_n_energy'],x['species_absorbed']) for x in report['spectral_refinement']])
    print('MULTICROSS',report['multicrossing']['event_roots_x'],report['multicrossing']['number_difference'])
    print('OUTPUT',OUT/'SOURCE_AGE_NUMERICS.json')

if __name__=='__main__':main()
