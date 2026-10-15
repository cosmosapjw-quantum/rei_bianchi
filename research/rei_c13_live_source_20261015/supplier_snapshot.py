#!/usr/bin/env python3
"""Actual owner bass_cr true-child source-conditioned adaptive spectral bound
on NEW dynamic C13 photon radiation after a native-source proper-time history.

Read-only inherited original bass_cr supplier. C13 photons are all transported
to one exact receiver clock *before* forming a genuine moment oracle per
single original emission direction; angular sectors are never pooled.
"""
from __future__ import annotations
import json,math,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/"research/rei_crossrepo_integration_20261015/suppliers/cr"))
import short_interval as s
from adaptive_q import PositivePacketOracle,AdaptiveQGrid

def run_real_source_bound(q=0.,nsteps=8,max_cells=8):
    model=s.Scenario(s.ROOT)
    src=s.NativeStellarSource.load(model,HERE/"NATIVE_SOURCE_8X8.csv")
    if q not in (0.,-.01,.01):raise ValueError("locked signed source")
    bg=s.Background(s.Family(q))
    g=s.initial_gas(model,s.START)
    state=s.SourceState(s.START,g,s.PhotonCloud.empty())
    provider=s.CaseARates()
    dx=s.stable_dx(s.START,s.STOP)/nsteps
    for i in range(nsteps):
        a=s.STOP if i==nsteps-1 else s.START*math.exp((i+1)*dx)
        state,receipt=s.one_interval(state,a,bg,model,src,provider)
    # Fixed single emission-angle label j=5. Three source spectral groups remain
    # separate indexed photons, but every packet is at the SAME receiver clock.
    j=5
    offset=np.arange(len(state.photons.E))%len(src.energy)
    take=np.where(offset%src.nang==j)[0]
    sky=s.PhotonCloud(state.photons.E[take],state.photons.mu[take],state.photons.NperH[take])
    lo=float(np.nextafter(sky.E.min(),0.))
    hi=float(np.nextafter(sky.E.max(),math.inf))
    oracle=PositivePacketOracle(sky.E,sky.NperH,src.source_id,
             f"C13_single_native_ray_idx{j}_q{q:+.3f}_multi_age_true_packets",
             float(state.elapsed_s))
    # Exactly one present proper gas/dt, no injection or born-cohort mixing
    # after the oracle snapshot.
    dt=1e12
    grid=AdaptiveQGrid(oracle,[lo,hi],1.,state.gas.neutral,dt,
                       [1e-9]*3+[1e-7]*3,nodes_per_branch=2)
    before=grid.summary()
    after=grid.run(max_cells)
    p=sky.to_native_chemistry(state.gas.nH)
    A,heat,energy,remain,absorbed=s.c10.reactions_vector(
        p.count,p.E,p.sigma,p.sigma_heat,state.gas.neutral,dt)
    sigma=p.sigma
    neutral=state.gas.neutral
    lam=s.C_CGS*dt*(sigma@neutral)
    frac=np.ones_like(lam)
    np.divide(-np.expm1(-lam),lam,out=frac,where=lam>0)
    # Use exact physical species heat separate, not one total only.
    w=p.count*frac
    per_sp=(s.C_CGS*dt)*(w@p.sigma_heat)*neutral/state.gas.nH
    vals=np.concatenate((A/state.gas.nH,per_sp))
    for k,(v,(low,high)) in enumerate(zip(vals,after["event"]+after["heat"])):
        if not low-1e-12<=v<=high+1e-12:
            raise AssertionError(f"C13_BASSCR_POSITIVE_SOURCE_PACKET_ESCAPE {k}: {v} not [{low},{high}]")
    if not all(y<=x+1e-14 for x,y in zip(before["widths"],after["widths"])):
        raise AssertionError("BASSCR_ADAPTIVE_OUTER_NOT_NESTED")
    return {"schema":"rei.c13.actual_source_age_true_child_bass_cr_bound.v1",
            "q":q,"native_source_sha256":src.source_sha256,
            "one_ray_source_index":j,"proper_clock_s":state.elapsed_s,
            "n_genuine_source_derived_packets":len(sky.E),
            "n_energy_groups":src.segments*3,
            "total_photon_perH_single_ray":sky.number,
            "total_energy_eV_perH_single_ray":sky.energy,
            "actual_species_photoevents_and_photoheat_perH":vals.tolist(),
            "initial_outer_widths":before["widths"],
            "final_outer_widths":after["widths"],
            "ratios":[x/y if y>0 else None for x,y in zip(before["widths"],after["widths"])],
            "precision_gate":after["precision_gate"],
            "preserves_exact_binary64_input_moments":after["exact_dyadic_partition"],
            "science_status":"conditional_one_proper_clock_positivity_bounds; not dynamic global accuracy"}
if __name__=="__main__":
    out=run_real_source_bound()
    (HERE/"BASSCR_C13_SOURCE_BOUND.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ("q","n_genuine_source_derived_packets",
       "precision_gate","ratios")},indent=2))
