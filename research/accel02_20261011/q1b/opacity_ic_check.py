"""Bounded new IC-only actual opacity/closure diagnostic; no history ODE."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,time
import numpy as np
from numpy.polynomial.legendre import leggauss
from reconstruction import reconstruct
from opacity_native import NativeOpacity,C_CM_S,EV_ERG,CHEMICAL_CHI_EV,THRESHOLDS_EV,HERE,N1
from source_cells import CellSource
from grid_cells import load_grid
sys.path.insert(0,str(N1))
from provider import HistoryProvider


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reference_uvb(provider,native,order):
    table=provider.tables['uvb']
    cuts=np.unique(np.r_[10.,50000.,THRESHOLDS_EV,
                        table.energies_eV[(table.energies_eV>10)&(table.energies_eV<50000)]])
    x,w=leggauss(order)
    loglo=np.log(cuts[:-1]); widths=np.log(cuts[1:]/cuts[:-1])
    energy=np.exp((loglo[:,None]+widths[:,None]*(x+1)/2).ravel())
    weights=np.broadcast_to(widths[:,None]*w/2,(len(widths),order)).ravel()
    density=table.photon_number_log(energy,provider.z_initial)
    sigma=np.vstack([native.sigma(energy[i:i+2048]) for i in range(0,len(energy),2048)])
    measure=weights*density
    rates=C_CM_S*sigma*measure[:,None]
    K0=np.sum(rates,axis=0)
    KE=np.sum(rates*energy[:,None],axis=0)
    heat=np.sum(rates*(energy[:,None]-CHEMICAL_CHI_EV),axis=0)
    return {'Gamma_s-1':K0.tolist(),'energy_eV_s-1_per_absorber':KE.tolist(),
            'heat_erg_s-1_per_absorber':(heat*EV_ERG).tolist(),
            'number_cm-3':float(np.sum(measure)),
            'energy_eV_cm-3':float(np.sum(energy*measure)),
            'order':order,'native_segments':len(widths),'nodes':len(energy)}


def metric(a,b,target):
    a,b=np.asarray(a,float),np.asarray(b,float)
    diff=abs(a-b)
    errors=[]
    for d,ref in zip(diff,b):
        errors.append(float(d/abs(ref)) if ref else (0. if d==0 else None))
    return {'per_species_relative_error':errors,'target':target,
            'pass':all(x is not None and x<=target for x in errors),
            'zero_reference_requires_exact_zero':True}


def main():
    output=HERE/'evidence/OPACITY_IC_CHECK.json'
    if output.exists():raise FileExistsError('Create-only IC evidence')
    started=time.monotonic()
    provider=HistoryProvider(r=0.)
    report={'schema':'rei.q1b.actual_opacity_ic.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Initial z=15.9 only; pinned UVB Cauchy measure, R=V=1, no emissivity history/ODE',
        'orders':{'closure':[64,128],'direct_UVB':[32,64]},
        'targets':{'local_quadrature':1e-7,'direct_order_comparison':1e-8,'IC_closure_headroom':1e-4},
        'input_identity':{'provider':provider.identity,**{name:digest(HERE/name) for name in
            ['reconstruction.py','opacity_native.py','opacity_ic_check.py','opacity_test.py','source_cells.py','GRID_C1.json','GRID_C2.json']}},
        'physical_ODE_calls':0,'native_RHS_calls':0,'old_RUN002_EVENT003_Q0_replays':0,
        'source_reference_reintegration':False,'members':{},'first_failures':[]}
    fields=['Gamma_s-1','energy_eV_s-1_per_absorber','heat_erg_s-1_per_absorber']
    with NativeOpacity() as native:
        report['input_identity']['native_binary_sha256']=native.binary_sha256
        for label in ['C1','C2']:
            grid=load_grid(HERE/('GRID_'+label+'.json'))
            source=CellSource(provider,grid)
            initial=source.initial()
            cells=[]; K0total=np.zeros(3); KEtotal=np.zeros(3); heattotal=np.zeros(3)
            failures=[]
            for angle in range(len(source.mu)):
                for j,(a,right) in enumerate(zip(source.edges[:-1],source.edges[1:])):
                    if time.monotonic()-started>120:raise TimeoutError('DECLARED_IC_120_SECOND_WALL_BUDGET')
                    N,U=float(initial['N'][angle,j]),float(initial['U_eV'][angle,j])
                    row={'angle':angle,'cell':j,'a':float(a),'q_right':float(right),'N':N,'U_eV':U}
                    try:
                        b=min(float(right),50000.)
                        if b<=a:
                            if N!=0 or U!=0:raise ValueError('NONZERO_DORMANT_IC')
                            row.update(status='DORMANT_EMPTY',native_calls=0)
                        else:
                            cell=reconstruct(N,U,1.,a,b)
                            out=native.moments(cell,orders=(64,128),rtol=1e-7)
                            K0total+=out['K0'];KEtotal+=out['KE'];heattotal+=out['heat_eV']
                            row.update(status='LOCAL_ACTUAL_OPACITY_CHECKED',p=cell.p,
                                reconstruction_status=cell.status,K0=out['K0'],KE=out['KE'],
                                heat_eV=out['heat_eV'],jacobian_status=out['jacobian_status'],
                                max_quadrature_error=max((v.get('order_pair_response_scaled_error',0.) for v in out['species_diagnostics'])),
                                native_calls=out['actual_native_calls'])
                    except Exception as exc:
                        row.update(status='EXPLICIT_LOCAL_FAILURE',exception=type(exc).__name__,message=str(exc))
                        failures.append({'angle':angle,'cell':j,'exception':type(exc).__name__,'message':str(exc)})
                        if not report['first_failures']:report['first_failures'].append({'member':label,**row})
                    cells.append(row)
            report['members'][label]={'cells':cells,'failed_cells':failures,
                'status':'COMPLETE_IC_LOCAL_MOMENTS' if not failures else 'INCOMPLETE_EXPLICIT_CELL_FAILURES',
                'accepted_cell_partial_sums':dict(zip(fields,[K0total.tolist(),KEtotal.tolist(),(heattotal*EV_ERG).tolist()])),
                'aggregate':dict(zip(fields,[K0total.tolist(),KEtotal.tolist(),(heattotal*EV_ERG).tolist()])) if not failures else None}
            print(json.dumps({'member':label,'cells':len(cells),'failures':len(failures),'elapsed_s':time.monotonic()-started}),flush=True)
        # New opacity-weighted initial measure reference, not old source campaign.
        references={str(order):reference_uvb(provider,native,order) for order in [32,64]}
        report['direct_UVB_reference']={'members':references,
            'independence':'Direct unchanged UVB interpolation times actual native sigma; independent of power-law reconstruction and CellSource moment closure. Shares physical provider, native sigma and Gauss quadrature family. Order agreement is numerical evidence, not a rigorous continuum bound.',
            'order_metrics':{field:metric(references['32'][field],references['64'][field],1e-8) for field in fields}}
        report['comparisons']={}
        for label in ['C1','C2']:
            aggregate=report['members'][label]['aggregate']
            report['comparisons'][label+'_vs_direct_UVB']={field:metric(aggregate[field],references['64'][field],1e-4) for field in fields} if aggregate else {'status':'NOT_EVALUATED_INCOMPLETE_CELLS'}
        a,b=report['members']['C1']['aggregate'],report['members']['C2']['aggregate']
        report['comparisons']['C1_vs_C2']={field:metric(a[field],b[field],1e-4) for field in fields} if a and b else {'status':'NOT_EVALUATED_INCOMPLETE_CELLS'}
        report['actual_native_SIGMA_calls']=native.native_calls
        report['actual_native_energy_evaluations']=native.energy_evaluations
    all_complete=all(m['aggregate'] is not None for m in report['members'].values())
    reference_pass=all(v['pass'] for v in report['direct_UVB_reference']['order_metrics'].values())
    headroom_pass=all_complete and reference_pass and all(v['pass'] for comp in report['comparisons'].values() for v in comp.values())
    report['status']='PASS_IC_LOCAL_HEADROOM_ONLY' if headroom_pass else 'FAIL_OR_INCOMPLETE_IC_LOCAL_HEADROOM_NO_ODE'
    report['all_cells_complete']=all_complete
    report['elapsed_s']=time.monotonic()-started
    report['claim_ceiling']='IC-only closure/integration diagnostic; no temporal, evolving spectral, global ledger, Bianchi, source-entry, or coupled-solver admission'
    with output.open('x') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':report['status'],'elapsed_s':report['elapsed_s'],'native_calls':report['actual_native_SIGMA_calls'],'output':str(output)}),flush=True)
    return 0 if headroom_pass else 1


if __name__=='__main__':raise SystemExit(main())
