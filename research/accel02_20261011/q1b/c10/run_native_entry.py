#!/usr/bin/env python3
"""Create-only bounded C2 actual entry runs; no old calculation replay."""
from pathlib import Path
import argparse,hashlib,json,math,sys,time,traceback
from datetime import datetime,timezone
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE.parent.parent/'n1'))
from provider import HistoryProvider
from grid_cells import load_grid
from source_cells import CellSource
from opacity_native import NativeOpacity
from native_step import NativeCell,initial_state,positive_native_step,gas_energy_eV,COUNTER_NAMES,gas_temperature


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def convert(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,dict):return {k:convert(a) for k,a in v.items()}
    if isinstance(v,(list,tuple)):return [convert(a) for a in v]
    return v

def fields(state,provider):
    g=provider.geometry(state['t_s']);x,y,z,w=state['gas']
    gamma=state['diagnostics']['gamma']
    return dict(xHII=x,xHeII=y,xHeIII=z,T_K=gas_temperature(state['gas'],g),
        ne_cm3=g['nH']*x+g['nHe']*(y+2*z),photon_cm3=math.fsum(state['N'].ravel())/g['a_rel']**3,
        GammaHI_s=gamma[0],GammaHeI_s=gamma[1],GammaHeII_s=gamma[2])

def ledger(state,ini):
    nh,he=state['nH_ref'],state['nHe_ref']
    e0=math.fsum(ini['U_eV'].ravel())+gas_energy_eV(ini['gas'],nh,he)
    en=math.fsum(state['U_eV'].ravel())+gas_energy_eV(state['gas'],nh,he)
    c=state['counters']
    er=math.fsum([en,-e0,c['Wrad_eV'],c['Wthermal_eV'],c['Eescape_eV'],-c['Esource_eV'],-c['ECMB_eV']])
    nr=math.fsum([math.fsum(state['N'].ravel()),-math.fsum(ini['N'].ravel()),c['Nabs'],-c['Nsource']])
    return dict(energy_initial_scaled=abs(er)/e0,number_nH_initial_scaled=abs(nr)/nh,
        energy_residual_eV=er,number_residual=nr,initial_energy_eV=e0,initial_nH_cm3=nh,
        pass_local_ledgers=abs(er)/e0<=1e-9 and abs(nr)/nh<=1e-9)

def main():
    a=argparse.ArgumentParser();a.add_argument('--final',type=float,required=True);a.add_argument('--steps',type=int,default=1)
    a.add_argument('--label',required=True);args=a.parse_args()
    stem=HERE/'evidence'/('NATIVE_ENTRY_'+args.label)
    if stem.with_suffix('.json').exists():raise FileExistsError('NATIVE evidence create-only')
    start=time.monotonic();p=HistoryProvider(r=0.);grid=load_grid(HERE.parent/'GRID_C2.json');src=CellSource(p,grid)
    saved=np.load(HERE.parent/'evidence/SOURCE_C2.npz');state=initial_state(src,saved_initial=saved);ini=state
    result=dict(schema='rei.q1b.native_entry_bounded.v1',label=args.label,created_utc=datetime.now(timezone.utc).isoformat(),
        final_s=args.final,steps=args.steps,physical_scope='FLRW r0 conditional initial gas; bounded source-entry only',
        native_calls=0,opacity_calls=0,old_RUN002_EVENT003_Q0_replays=0,
        identities={x:sha(HERE/x) for x in ('native_step.py','run_native_entry.py','source_entry.py','positive_absorption.py')},
        accepted_boundaries=[],status='RUNNING',scientific_admission=False)
    birth=int(np.where(src.edges==50000.)[0][0]);states=[state]
    try:
        with NativeOpacity() as opacity,NativeCell() as native:
            try:
                for i,t in enumerate(np.linspace(0,args.final,args.steps+1)[1:],1):
                    state=positive_native_step(state,float(t),src,opacity,native);states.append(state)
                    born={key:float(state[key][0,birth]) for key in ('N','U_eV','R')}
                    born.update(support=state['support'][0,birth].tolist(),
                        mean_q=float(state['U_eV'][0,birth]/state['R'][0,birth]/state['N'][0,birth]))
                    row=dict(index=i,t_s=float(t),gas=state['gas'].tolist(),birth=born,fields=fields(state,p),
                        ledger=ledger(state,ini),diagnostics=state['diagnostics'])
                    result['accepted_boundaries'].append(row)
                    print(json.dumps(convert(dict(boundary=i,t_s=t,gas=state['gas'],ledger=row['ledger'],elapsed_s=time.monotonic()-start))),flush=True)
                    boundary=stem.with_name(stem.name+f'_BOUNDARY_{i:03d}.npz')
                    with boundary.open('xb') as f:np.savez_compressed(f,gas=state['gas'],N=state['N'],U_eV=state['U_eV'],R=state['R'],support=state['support'],
                        counters=np.array([state['counters'][x] for x in COUNTER_NAMES]),t_s=t)
                    if not row['ledger']['pass_local_ledgers']:raise ArithmeticError('ENTRY_LOCAL_GLOBAL_SCALE_LEDGER_REJECTED')
                result['status']='PASS_BOUNDED_MAP_ONLY'
            finally:
                result['native_calls']=native.calls;result['opacity_calls']=opacity.native_calls
                result['sigma_energy_evaluations']=opacity.energy_evaluations
    except Exception as exc:
        result['status']='REJECTED_BOUNDED_ATTEMPT'
        result['failure']=dict(type=type(exc).__name__,message=str(exc),notes=getattr(exc,'__notes__',[]),
            diagnostics=getattr(exc,'diagnostics',None),traceback=traceback.format_exc())
        print(result['failure']['traceback'],flush=True)
    result['elapsed_s']=time.monotonic()-start
    stem.with_suffix('.json').write_text(json.dumps(convert(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','native_calls','opacity_calls','elapsed_s')}),flush=True)
    return 0 if result['status']=='PASS_BOUNDED_MAP_ONLY' else 1

if __name__=='__main__':raise SystemExit(main())
