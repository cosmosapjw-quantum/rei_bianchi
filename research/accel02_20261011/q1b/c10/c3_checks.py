"""New C3 only: reuse saved Q0 and C2/direct opacity; no old run replay."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys
import time
import numpy as np

HERE=Path(__file__).resolve().parent
Q1B=HERE.parent
N1=Q1B.parent/'n1'
sys.path[:0]=[str(Q1B),str(N1)]
from grid_cells import load_grid
from source_cells import CellSource, EV_ERG, _metric
from reconstruction import reconstruct
from opacity_native import NativeOpacity
from opacity_ic_check import metric
from provider import HistoryProvider

FIELDS=['Gamma_s-1','energy_eV_s-1_per_absorber','heat_erg_s-1_per_absorber']
SOURCE_REFERENCE=Q1B.parent/'recovery/Q0_SOURCE_ATTRIBUTION.json'
OPACITY_REFERENCE=Q1B/'evidence/OPACITY_IC_CHECK.json'


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    with Path(path).open('x') as handle:
        json.dump(value,handle,indent=2,allow_nan=False)
        handle.write('\n')


def identity(provider):
    return {'provider':provider.identity,'saved_Q0_sha256':digest(SOURCE_REFERENCE),
        'saved_C09B_opacity_sha256':digest(OPACITY_REFERENCE),
        **{name:digest(Q1B/name) for name in ['GRID_C2.json','source_cells.py',
            'grid_cells.py','reconstruction.py','opacity_native.py']},
        **{name:digest(HERE/name) for name in ['GRID_C3.json','c3_grid.py','c3_checks.py','test_c3.py']}}


def source_check():
    output=HERE/'evidence/C3_SOURCE_IC_CHECK.json'
    npz_path=HERE/'evidence/C3_SOURCE.npz'
    if output.exists() or npz_path.exists(): raise FileExistsError('C3_SOURCE_CREATE_ONLY')
    start=time.monotonic()
    provider=HistoryProvider(r=0.)
    saved=json.loads(SOURCE_REFERENCE.read_text())
    if saved['source_implementation_sha256']['hm12_data.py']!=provider.identity['hm12_data.py']:
        raise ValueError('C3_SOURCE_SAVED_PROVIDER_IDENTITY')
    grid=load_grid(HERE/'GRID_C3.json')
    if grid['provider_identity']!=provider.identity:
        raise ValueError('C3_GRID_PHYSICAL_PROVIDER_IDENTITY')
    source=CellSource(provider,grid)
    rows=saved['exact_source_history']
    if len(rows)!=129 or rows[0]['time_s']!=0.:
        raise ValueError('C3_SAVED_REFERENCE_EPOCHS')
    uvb_ref=saved['runs']['EVENT_COUPLED002']['initial_UVB_moment_comparison']
    bands=saved['bands_eV']
    approx={field:[] for field in rows[0] if field.endswith(('_ref','_proper'))}
    initial_values,initial_metrics={},{}
    for name,band in bands.items():
        ini=source.initial(band)
        for quantity,val in [('number',float(ini['N'].sum())),('energy',float(ini['U_eV'].sum())*EV_ERG)]:
            field=name+'_'+quantity
            initial_values[field]=val
            initial_metrics[field]=_metric([val],[uvb_ref[field]['exact_declared_interpolation']],slice(None))
    full_N,full_U=[],[]
    max_z_error=max_Ra_error=0.
    for index,row in enumerate(rows):
        g=provider.geometry(row['time_s'])
        max_z_error=max(max_z_error,abs(g['z']-row['z']))
        for name,band in bands.items():
            result=source.source(row['time_s'],band)
            max_Ra_error=max(max_Ra_error,float(np.max(np.abs(result['R']*g['a_rel']-1))))
            if name=='full':
                full_N.append(result['N']);full_U.append(result['U_eV'])
            for quantity,value in [('number',float(result['N'].sum())),('energy',float(result['U_eV'].sum())*EV_ERG)]:
                approx[name+'_'+quantity+'_ref'].append(value)
                approx[name+'_'+quantity+'_proper'].append(value/g['a_rel']**3)
        if index%32==0:
            print(json.dumps({'stage':'C3_SOURCE','completed_epoch':index+1,'elapsed_s':time.monotonic()-start}),flush=True)
    metrics={name:{field:_metric(values,[row[field] for row in rows],subset) for field,values in approx.items()}
        for name,subset in [('shared129',slice(None)),('shared65',slice(None,None,2))]}
    initial=source.initial()
    with npz_path.open('xb') as handle:
        np.savez_compressed(handle,times_s=[row['time_s'] for row in rows],redshifts=[row['z'] for row in rows],
            source_N=full_N,source_U_eV=full_U,initial_N=initial['N'],initial_U_eV=initial['U_eV'],
            q_edges_eV=source.edges,initial_mu=source.mu,angular_weights=source.weights)
    passed=bool(max_z_error==0. and max_Ra_error<=1e-14 and all(m['pass'] for s in metrics.values() for m in s.values())
        and all(m['pass'] for m in initial_metrics.values()))
    report={'schema':'rei.q1b.c3.source_ic.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'member':'C3','status':'PASS_LOCAL_SOURCE_IC' if passed else 'FAIL_LOCAL_SOURCE_IC','pass':passed,
        'input_identity':identity(provider),'energy_cells':348,'total_cells':696,'target':1e-12,
        'source_metrics':metrics,'initial_values':initial_values,'initial_metrics':initial_metrics,'source_sums':approx,
        'max_geometry_z_minus_saved':max_z_error,'max_R_a_minus_one':max_Ra_error,
        'max_source_scaled_difference':max(v['normalized_error'] for s in metrics.values() for v in s.values()),
        'max_IC_scaled_difference':max(v['normalized_error'] for v in initial_metrics.values()),
        'raw_arrays':{'path':str(npz_path.relative_to(Q1B)),'sha256':digest(npz_path)},
        'old_RUN002_EVENT003_Q0_C1_C2_replays':0,'physical_ODE_calls':0,'native_calls':0,
        'saved_reference_reintegration':False,
        'reference_independence':'Saved Q0 values reused; new C3 cell sums share pinned HM12 interpolation and analytic exponential weights with reference. Existing manufactured integral tests are reused, not rerun. Not independent physical data.',
        'claim_ceiling':'Source/IC partition sums on saved 129/65 epoch sets only; no evolving spectrum, opacity or ODE admission.',
        'elapsed_s':time.monotonic()-start}
    write_json(output,report)
    print(json.dumps({k:report[k] for k in ['status','max_source_scaled_difference','max_IC_scaled_difference','elapsed_s']}),flush=True)
    return 0 if passed else 1


def opacity_check():
    output=HERE/'evidence/C3_OPACITY_IC_CHECK.json'
    if output.exists(): raise FileExistsError('C3_OPACITY_CREATE_ONLY')
    start=time.monotonic()
    provider=HistoryProvider(r=0.)
    saved=json.loads(OPACITY_REFERENCE.read_text())
    current=identity(provider)
    if current['provider']!=saved['input_identity']['provider']:
        raise ValueError('C3_OPACITY_PROVIDER_IDENTITY')
    for name in ['GRID_C2.json','source_cells.py','reconstruction.py','opacity_native.py']:
        if current[name]!=saved['input_identity'][name]:
            raise ValueError('C3_SAVED_OPACITY_COMPONENT_IDENTITY:'+name)
    if saved['members']['C2']['aggregate'] is None or not all(v['pass'] for v in saved['direct_UVB_reference']['order_metrics'].values()):
        raise ValueError('C3_SAVED_OPACITY_REFERENCE_INCOMPLETE')
    source_evidence=json.loads((HERE/'evidence/C3_SOURCE_IC_CHECK.json').read_text())
    if not source_evidence['pass'] or source_evidence['input_identity']['GRID_C3.json']!=current['GRID_C3.json']:
        raise ValueError('C3_SOURCE_IC_NOT_ACCEPTED_OR_GRID_CHANGED')
    raw_path=HERE/'evidence/C3_SOURCE.npz'
    if digest(raw_path)!=source_evidence['raw_arrays']['sha256']:
        raise ValueError('C3_INITIAL_ARRAYS_IDENTITY')
    grid=load_grid(HERE/'GRID_C3.json')
    edges=np.asarray(grid['q_edges_eV'])
    with np.load(raw_path,allow_pickle=False) as data:
        N0=data['initial_N'].copy();U0=data['initial_U_eV'].copy()
        if not np.array_equal(data['q_edges_eV'],edges): raise ValueError('C3_IC_EDGES')
    report={'schema':'rei.q1b.c3.actual_opacity_ic.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'input_identity':current,'scope':'IC z15.9, R=V=1 only; C3 new member against saved C2/direct64; no ODE',
        'orders':{'new_C3':[64,128],'saved_direct_UVB':64},
        'targets':{'local_quadrature':1e-7,'IC_closure_headroom':1e-4},
        'physical_ODE_calls':0,'native_RHS_calls':0,'old_RUN002_EVENT003_Q0_C1_C2_replays':0,
        'reference_reintegration':False,'first_failures':[]}
    cells=[];failures=[];K0total=np.zeros(3);KEtotal=np.zeros(3);heattotal=np.zeros(3)
    with NativeOpacity() as native:
        if native.binary_sha256!=saved['input_identity']['native_binary_sha256']:
            raise ValueError('C3_SAVED_OPACITY_NATIVE_IDENTITY')
        report['input_identity']['native_binary_sha256']=native.binary_sha256
        for angle in range(2):
            for j,(a,right) in enumerate(zip(edges[:-1],edges[1:])):
                N,U=float(N0[angle,j]),float(U0[angle,j])
                row={'angle':angle,'cell':j,'a':float(a),'q_right':float(right),'N':N,'U_eV':U}
                try:
                    if time.monotonic()-start>120: raise TimeoutError('C3_DECLARED_OPACITY_120_SECOND_WALL_BUDGET')
                    b=min(float(right),50000.)
                    if b<=a:
                        if N!=0 or U!=0: raise ValueError('C3_NONZERO_DORMANT_IC')
                        row.update(status='DORMANT_EMPTY',native_calls=0)
                    else:
                        cell=reconstruct(N,U,1.,a,b)
                        out=native.moments(cell,orders=(64,128),rtol=1e-7)
                        K0total+=out['K0'];KEtotal+=out['KE'];heattotal+=out['heat_eV']
                        row.update(status='LOCAL_ACTUAL_OPACITY_CHECKED',p=cell.p,reconstruction_status=cell.status,
                            K0=out['K0'],KE=out['KE'],heat_eV=out['heat_eV'],jacobian_status=out['jacobian_status'],
                            max_quadrature_error=max(v.get('order_pair_response_scaled_error',0.) for v in out['species_diagnostics']),
                            native_calls=out['actual_native_calls'])
                except Exception as exc:
                    row.update(status='EXPLICIT_LOCAL_FAILURE',exception=type(exc).__name__,message=str(exc))
                    failures.append({'angle':angle,'cell':j,'exception':type(exc).__name__,'message':str(exc)})
                    if not report['first_failures']:report['first_failures'].append(dict(row))
                cells.append(row)
            print(json.dumps({'stage':'C3_OPACITY','angle_completed':angle,'cells_completed':len(cells),'failures':len(failures),'elapsed_s':time.monotonic()-start}),flush=True)
        report['actual_native_SIGMA_calls']=native.native_calls
        report['actual_native_energy_evaluations']=native.energy_evaluations
    aggregate=dict(zip(FIELDS,[K0total.tolist(),KEtotal.tolist(),(heattotal*EV_ERG).tolist()]))
    report.update(cells=cells,failed_cells=failures,all_cells_complete=not failures,
        accepted_cell_partial_sums=aggregate,aggregate=aggregate if not failures else None,
        saved_reference={'direct64':saved['direct_UVB_reference']['members']['64'],'C2':saved['members']['C2']['aggregate'],
            'direct_order_metrics':saved['direct_UVB_reference']['order_metrics'],
            'C2_vs_direct_UVB_metrics':saved['comparisons']['C2_vs_direct_UVB'],
            'independence':saved['direct_UVB_reference']['independence']})
    report['comparisons']={
        'C3_vs_saved_direct_UVB':{field:metric(aggregate[field],saved['direct_UVB_reference']['members']['64'][field],1e-4) for field in FIELDS},
        'saved_C2_vs_C3':{field:metric(saved['members']['C2']['aggregate'][field],aggregate[field],1e-4) for field in FIELDS}
        } if not failures else {'status':'NOT_EVALUATED_INCOMPLETE_CELLS'}
    passed=not failures and all(v['pass'] for comp in report['comparisons'].values() for v in comp.values())
    report['pass']=passed
    report['status']='PASS_C2_C3_IC_LOCAL_HEADROOM_ONLY' if passed else 'FAIL_OR_INCOMPLETE_C2_C3_IC_LOCAL_HEADROOM'
    report['claim_ceiling']='IC-only closure comparison, not a continuum certificate or temporal/evolving spectral/global ledger/Bianchi/source-entry/coupled-solver admission'
    report['elapsed_s']=time.monotonic()-start
    write_json(output,report)
    print(json.dumps({'status':report['status'],'cells':len(cells),'failures':len(failures),'native_calls':report['actual_native_SIGMA_calls'],'elapsed_s':report['elapsed_s']}),flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['source','opacity'])
    args=parser.parse_args()
    raise SystemExit(source_check() if args.stage=='source' else opacity_check())
