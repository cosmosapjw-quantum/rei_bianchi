"""Versioned cell-parallel execution of the frozen v3/v4 physical map.

Only independent prepare/absorb cell evaluations move to ordered actors. Source
arithmetic, implicit gas solve, native RHS/reduction order, counters and final
attenuated-measure ownership are unchanged. No controller change is made here.
"""
from pathlib import Path
import math
import sys
import time
import numpy as np

HERE=Path(__file__).resolve().parent
Q1B=HERE.parent
for path in (Q1B/'c10',Q1B/'c11/integration',Q1B/'c11/integration/production'):
    sys.path.insert(0,str(path))
from native_step_v3 import (gas_energy_eV,implicit_gas_solve,split_thermal_work,
                            EV_ERG,COUNTER_NAMES)
from native_step_v4_diagnostics import _capture_kernel


def positive_native_step(state,t1,source,pool,native,*,source_api):
    started=time.monotonic()
    before=pool.metrics
    t0=float(state['t_s']);h=float(t1)-t0;p=source.provider;g=p.geometry(t1)
    events=source_api.provider_event_times(source,t0,t1)
    integrated=source_api.integrate_source(source,t0,t1,event_times=events)
    incident=source_api.advance_source(state['N'],state['U_eV'],integrated)
    source_s=time.monotonic()-started
    nangle,nenergy=incident['N'].shape
    _,mu,R=p.ray(np.ones(nangle),source.mu,t1)
    if not np.array_equal(R,integrated['R1']):raise ValueError('ENTRY_ENDPOINT_RAY_IDENTITY')
    lambdas=g['H']+g['s']*(3*mu*mu-1)
    requests=[];supports=[]
    for a in range(nangle):
        for j in range(nenergy):
            lo=float(source.edges[j]);hi=min(float(source.edges[j+1]),50000./R[a])
            if hi<lo:
                if incident['N'][a,j]!=0 or incident['U_eV'][a,j]!=0:raise ValueError('ENTRY_DORMANT_NONZERO')
                hi=lo
            supports.append([lo,hi])
            requests.append(dict(N=float(incident['N'][a,j]),U=float(incident['U_eV'][a,j]),
                R=float(R[a]),a=lo,b=hi,orders=(64,128),rtol=1e-7,
                support_cap_ev=(50000. if hi==50000./R[a] and hi<=source.edges[j+1] else None)))
    preparation_started=time.monotonic()
    prep_diagnostics=pool.prepare(requests)
    preparation_s=time.monotonic()-preparation_started
    native_rhs_s=0.;native_evaluations=0
    def evaluate(gas):
        nonlocal native_rhs_s,native_evaluations
        lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
        results=pool.absorb(lower,h)
        cells=np.zeros((len(requests),13))
        cells[:,0]=np.repeat(mu,nenergy);cells[:,1]=np.repeat(R,nenergy)
        cells[:,2]=np.repeat(lambdas,nenergy)
        for i,value in enumerate(results):
            cells[i,3:5]=[value['N'],value['U']]
            cells[i,7:10]=value['K0'];cells[i,10:13]=value['KE']
        rhs_started=time.monotonic()
        out=native.rhs(t1,g,gas,cells)
        native_rhs_s+=time.monotonic()-rhs_started
        native_evaluations+=1
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
    result=dict(t_s=float(t1),gas=gas,N=N,U_eV=U,R=np.repeat(R[:,None],nenergy,axis=1),
        support=np.array(supports).reshape(nangle,nenergy,2),counters=counters,nH_ref=nh,nHe_ref=he,
        diagnostics=dict(source=integrated['diagnostics'],source_pairing=incident['diagnostics'],
            newton=solver,work=workdiag,local_energy_residual_eV=energy,local_number_residual=number,
            native_absorbed_counter_disagreement=abs_error,native_local_number_residual=float(out[12]),
            native_local_energy_residual=float(out[13]),
            gas_temperature_K=float(out[11]),gamma=out[8:11].tolist(),increments=increments,
            source_events_s=list(events),prepared_cells=len(requests),
            native_coordinate_certificates=[dict(cell_index=i,certificate=diag['native_coordinate_certificate'])
                for i,diag in enumerate(prep_diagnostics) if 'native_coordinate_certificate' in diag],
            incident_order_pair_max_error=max((diag.get('order_pair_max_error',0.) for diag in prep_diagnostics),default=0.),
            claim='BOUNDED_FIRST_ORDER_SPLIT_STEP_ONLY'))
    # The payload is exactly the final converged gas residual's returned measure;
    # no endpoint reconstruction, extra RHS or opacity re-evaluation is performed.
    result['diagnostics']['output24_kernel']=_capture_kernel(result,g,cells,
        np.array([value['photoheat_direct'] for value in absorbed]),out[8:11],
        owner='ACTUAL_CONVERGED_NATIVE_V3_ATTENUATED_MEASURE',native_evaluations=native_evaluations)
    after=pool.metrics
    result['hpc_metrics']=dict(schema='rei.hpc.ordered_cell_map_metrics.v1',
        workers=pool.workers,opacity_binding=after['opacity_binding'],
        sigma_calls=after['native_calls']-before['native_calls'],
        sigma_energy_evaluations=after['energy_evaluations']-before['energy_evaluations'],
        native_rhs_calls=native_evaluations,source_s=source_s,prepare_wall_s=preparation_s,
        absorb_wall_s=after['timings']['absorb_wall_s']-before['timings']['absorb_wall_s'],
        native_rhs_s=native_rhs_s,map_wall_s=time.monotonic()-started,
        execution_only=True,physical_arithmetic_changed=False,controller_changed=False,
        ordered_cell_assembly=True,scientific_admission=False)
    return result
