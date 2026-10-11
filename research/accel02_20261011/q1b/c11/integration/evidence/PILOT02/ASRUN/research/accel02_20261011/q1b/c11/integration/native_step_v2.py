"""C11 versioned source dependency injection; frozen absorption/gas semantics.

The C10 split-map body is retained verbatim except the three source operations
are resolved on an explicit caller-selected module. This is numerical source
precision plumbing, not a new physical provider or high-order map. C10 files
and globals are never patched. Required keyword avoids fallback to old source.
"""
from pathlib import Path
import math
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
C10=HERE.parents[1]/'c10'
sys.path.insert(0,str(C10))
from native_step import (NativeCell, initial_state, gas_temperature,
    gas_admissible, gas_energy_eV, implicit_gas_solve, split_thermal_work,
    EV_ERG, CHI, COUNTER_NAMES)
from positive_absorption import prepare_incident, absorb


def positive_native_step(state,t1,source,opacity,native,*,source_api):
    t0=float(state['t_s']);h=float(t1)-t0;p=source.provider;g=p.geometry(t1)
    events=source_api.provider_event_times(source,t0,t1)
    integrated=source_api.integrate_source(source,t0,t1,event_times=events)
    incident=source_api.advance_source(state['N'],state['U_eV'],integrated)
    nangle,nenergy=incident['N'].shape
    _,mu,R=p.ray(np.ones(nangle),source.mu,t1)
    if not np.array_equal(R,integrated['R1']):raise ValueError('ENTRY_ENDPOINT_RAY_IDENTITY')
    lambdas=g['H']+g['s']*(3*mu*mu-1)
    prep=[];supports=[]
    for a in range(nangle):
        for j in range(nenergy):
            lo=float(source.edges[j]);hi=min(float(source.edges[j+1]),50000./R[a])
            if hi<lo:
                if incident['N'][a,j]!=0 or incident['U_eV'][a,j]!=0:raise ValueError('ENTRY_DORMANT_NONZERO')
                hi=lo  # support metadata only; not a state projection
            supports.append([lo,hi])
            try:
                prep.append(prepare_incident(float(incident['N'][a,j]),float(incident['U_eV'][a,j]),
                    float(R[a]),lo,hi,opacity,orders=(64,128),rtol=1e-7))
            except Exception as exc:
                exc.add_note(f'angle={a},energy_cell={j},q_left={lo},q_right={hi},t0={t0},t1={t1}')
                raise
    def evaluate(gas):
        lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
        results=[absorb(cell,lower,h) for cell in prep]
        cells=np.zeros((len(prep),13))
        cells[:,0]=np.repeat(mu,nenergy);cells[:,1]=np.repeat(R,nenergy)
        cells[:,2]=np.repeat(lambdas,nenergy)
        for i,result in enumerate(results):
            cells[i,3:5]=[result['N'],result['U']]
            cells[i,7:10]=result['K0'];cells[i,10:13]=result['KE']
        out=native.rhs(t1,g,gas,cells)
        return out[:4],(out,results,cells)
    gas,(out,absorbed,cells),solver=implicit_gas_solve(state['gas'],h,g,evaluate)
    N=cells[:,3].reshape(nangle,nenergy);U=cells[:,4].reshape(nangle,nenergy)
    thermal,workdiag=split_thermal_work(out,gas,g,cells[:,2],cells[:,4])
    increments=dict(Nsource=math.fsum(integrated['dN'].ravel()),
        Nabs=math.fsum(float(v) for a in absorbed for v in a['number_absorbed_species']),
        Esource_eV=math.fsum(integrated['injected_energy_eV'].ravel()),
        Eescape_eV=h*out[4]/EV_ERG,Wrad_eV=math.fsum(incident['radiation_work_eV'].ravel()),
        Wthermal_eV=h*thermal,ECMB_eV=h*out[14]/EV_ERG)
    counters={key:state['counters'][key]+increments[key] for key in COUNTER_NAMES}
    nh,he=state['nH_ref'],state['nHe_ref']
    e0=math.fsum(state['U_eV'].ravel())+gas_energy_eV(state['gas'],nh,he)
    e1=math.fsum(U.ravel())+gas_energy_eV(gas,nh,he)
    energy=math.fsum([e1,-e0,increments['Wrad_eV'],increments['Wthermal_eV'],
        increments['Eescape_eV'],-increments['Esource_eV'],-increments['ECMB_eV']])
    number=math.fsum([math.fsum(N.ravel()),-math.fsum(state['N'].ravel()),increments['Nabs'],-increments['Nsource']])
    nabs_owner=h*out[7]
    abs_scale=max(abs(nabs_owner),abs(increments['Nabs']))
    abs_error=abs(nabs_owner-increments['Nabs'])/abs_scale if abs_scale else 0.
    if abs_error>1e-12:raise ArithmeticError('ENTRY_NATIVE_ABSORPTION_COUNTER_MISMATCH')
    return dict(t_s=float(t1),gas=gas,N=N,U_eV=U,R=np.repeat(R[:,None],nenergy,axis=1),
        support=np.array(supports).reshape(nangle,nenergy,2),counters=counters,nH_ref=nh,nHe_ref=he,
        diagnostics=dict(source=integrated['diagnostics'],source_pairing=incident['diagnostics'],
            newton=solver,work=workdiag,local_energy_residual_eV=energy,local_number_residual=number,
            native_absorbed_counter_disagreement=abs_error,native_local_number_residual=float(out[12]),
            native_local_energy_residual=float(out[13]),
            gas_temperature_K=float(out[11]),gamma=out[8:11].tolist(),increments=increments,
            source_events_s=list(events),prepared_cells=len(prep),claim='BOUNDED_FIRST_ORDER_SPLIT_STEP_ONLY'))
